from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, RegisterForm
from .models import Category, Order, OrderItem, Product, Wishlist


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
def home(request):
    context = {
        "featured_products": Product.objects.filter(is_featured=True)[:8],
        "new_arrivals": Product.objects.filter(is_new_arrival=True)[:8],
        "popular_products": Product.objects.filter(is_popular=True)[:8],
        "sale_products": Product.objects.filter(is_on_sale=True)[:8],
        "categories": Category.objects.all(),
    }
    return render(request, "home.html", context)


# ---------------------------------------------------------------------------
# Product listing — search, filter, sort
# ---------------------------------------------------------------------------
def product_list(request):
    products = Product.objects.select_related("category").all()

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    category_slug = request.GET.get("category", "")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    availability = request.GET.get("availability", "")
    if availability == "in_stock":
        products = products.filter(stock__gt=0)
    elif availability == "out_of_stock":
        products = products.filter(stock=0)

    min_rating = request.GET.get("min_rating")
    if min_rating:
        products = products.filter(rating__gte=min_rating)

    sort = request.GET.get("sort", "newest")
    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
        "popular": "-rating",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)
        )

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_slug,
        "sort": sort,
        "availability": availability,
        "min_price": min_price or "",
        "max_price": max_price or "",
        "min_rating": min_rating or "",
        "wishlist_ids": wishlist_ids,
        "result_count": products.count(),
    }
    return render(request, "products.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    context = {
        "product": product,
        "related_products": related,
        "in_wishlist": in_wishlist,
    }
    return render(request, "product_detail.html", context)


# ---------------------------------------------------------------------------
# Cart — AJAX endpoints return JSON so the page never needs a hard refresh
# ---------------------------------------------------------------------------
def cart_view(request):
    cart = Cart(request)
    return render(request, "cart.html", {"cart": cart})


@require_POST
def cart_add(request):
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    quantity = int(request.POST.get("quantity", 1) or 1)
    cart = Cart(request)

    if not product.in_stock:
        return JsonResponse({"ok": False, "error": "This product is out of stock."}, status=400)

    cart.add(product, quantity=quantity)
    return JsonResponse(
        {
            "ok": True,
            "message": f"{product.name} added to cart successfully!",
            "cart_count": len(cart),
            "cart_subtotal": str(cart.subtotal),
        }
    )


@require_POST
def cart_update(request):
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    quantity = int(request.POST.get("quantity", 1) or 1)
    cart = Cart(request)
    cart.update(product, quantity)

    line_total = None
    for item in cart:
        if item["product"].id == product.id:
            line_total = item["line_total"]
            break

    return JsonResponse(
        {
            "ok": True,
            "cart_count": len(cart),
            "line_total": str(line_total) if line_total is not None else "0",
            "subtotal": str(cart.subtotal),
            "delivery_fee": str(cart.delivery_fee),
            "total": str(cart.total),
            "removed": line_total is None,
        }
    )


@require_POST
def cart_remove(request):
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    cart = Cart(request)
    cart.remove(product)
    return JsonResponse(
        {
            "ok": True,
            "cart_count": len(cart),
            "subtotal": str(cart.subtotal),
            "delivery_fee": str(cart.delivery_fee),
            "total": str(cart.total),
        }
    )


# ---------------------------------------------------------------------------
# Checkout & order processing
# ---------------------------------------------------------------------------
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty — add something before checking out.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Re-validate stock right before creating the order.
            for item in cart:
                if item["quantity"] > item["product"].stock:
                    messages.error(
                        request,
                        f"Sorry, only {item['product'].stock} of {item['product'].name} left in stock.",
                    )
                    return redirect("cart")

            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.subtotal = cart.subtotal
            order.delivery_fee = cart.delivery_fee
            order.discount = cart.discount
            order.total = cart.total
            order.status = "pending"
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    quantity=item["quantity"],
                    price=item["unit_price"],
                )
                item["product"].stock = max(0, item["product"].stock - item["quantity"])
                item["product"].save(update_fields=["stock"])

            cart.clear()
            return redirect("order_success", order_number=order.order_number)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {"customer_name": request.user.get_full_name() or request.user.username, "email": request.user.email}
        form = CheckoutForm(initial=initial)

    return render(request, "checkout.html", {"form": form, "cart": cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "order_success.html", {"order": order})


# ---------------------------------------------------------------------------
# Wishlist
# ---------------------------------------------------------------------------
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product")
    wishlist_ids = {item.product_id for item in items}
    return render(request, "wishlist.html", {"items": items, "wishlist_ids": wishlist_ids})


@login_required
@require_POST
def wishlist_toggle(request):
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    existing = Wishlist.objects.filter(user=request.user, product=product).first()
    if existing:
        existing.delete()
        added = False
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
    return JsonResponse(
        {
            "ok": True,
            "added": added,
            "wishlist_count": Wishlist.objects.filter(user=request.user).count(),
        }
    )


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to DukaLink, {user.username}!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


class DukaLinkLoginView(LoginView):
    template_name = "registration/login.html"


class DukaLinkLogoutView(LogoutView):
    next_page = reverse_lazy("home")


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "profile.html", {"orders": orders})
