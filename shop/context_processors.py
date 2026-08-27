from django.conf import settings

from .cart import Cart
from .models import Category, Wishlist


def site_settings(request):
    return {"CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL}


def cart_and_wishlist(request):
    cart = Cart(request)
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return {
        "cart": cart,
        "cart_item_count": len(cart),
        "wishlist_count": wishlist_count,
    }


def site_categories(request):
    return {"nav_categories": Category.objects.all()}
