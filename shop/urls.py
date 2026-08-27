from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),

    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<str:order_number>/", views.order_success, name="order_success"),

    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/", views.wishlist_toggle, name="wishlist_toggle"),

    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.DukaLinkLoginView.as_view(), name="login"),
    path("accounts/logout/", views.DukaLinkLogoutView.as_view(), name="logout"),
    path("accounts/profile/", views.profile, name="profile"),
]
