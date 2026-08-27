from decimal import Decimal

from django.conf import settings

from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """
    A simple session-backed cart. Keyed by product id (as a string, since
    session data is JSON) -> quantity. Works for both guests and logged-in
    users — no separate DB cart model is needed for a project this size.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, product, quantity=1, replace=False):
        product_id = str(product.id)
        max_qty = max(product.stock, 0)
        if product_id in self.cart and not replace:
            new_qty = self.cart[product_id] + quantity
        else:
            new_qty = quantity
        self.cart[product_id] = max(1, min(new_qty, max_qty)) if max_qty > 0 else 0
        self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        max_qty = max(product.stock, 0)
        if quantity <= 0:
            self.remove(product)
            return
        self.cart[product_id] = min(quantity, max_qty)
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.cart = {}
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_by_id = {str(p.id): p for p in products}
        for product_id, quantity in self.cart.items():
            product = products_by_id.get(product_id)
            if not product:
                continue
            unit_price = product.current_price
            yield {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    @property
    def subtotal(self):
        return sum((item["line_total"] for item in self), Decimal("0"))

    @property
    def delivery_fee(self):
        if len(self) == 0:
            return Decimal("0")
        if self.subtotal >= Decimal(str(settings.FREE_DELIVERY_THRESHOLD)):
            return Decimal("0")
        return Decimal(str(settings.DELIVERY_FEE))

    @property
    def discount(self):
        # Placeholder for future coupon support — no discount logic yet.
        return Decimal("0")

    @property
    def total(self):
        return self.subtotal + self.delivery_fee - self.discount

    @property
    def remaining_for_free_delivery(self):
        threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
        remaining = threshold - self.subtotal
        return remaining if remaining > 0 else Decimal("0")
