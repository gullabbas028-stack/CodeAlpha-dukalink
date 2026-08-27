from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "product_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "discount_price",
        "stock",
        "rating",
        "is_featured",
        "is_on_sale",
        "thumb",
    )
    list_editable = ("price", "discount_price", "stock")
    list_filter = ("category", "is_featured", "is_new_arrival", "is_popular", "is_on_sale")
    search_fields = ("name", "description", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Basic info", {"fields": ("name", "slug", "category", "short_description", "description", "features")}),
        ("Pricing & stock", {"fields": ("price", "discount_price", "stock", "rating")}),
        ("Media", {"fields": ("image", "image_url")}),
        ("Merchandising flags", {"fields": ("is_featured", "is_new_arrival", "is_popular", "is_on_sale")}),
    )

    def thumb(self, obj):
        if obj.display_image:
            return format_html('<img src="{}" style="height:36px;border-radius:4px" />', obj.display_image)
        return "—"

    thumb.short_description = "Image"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "quantity", "price", "subtotal")
    can_delete = False

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "city",
        "payment_method",
        "total",
        "status",
        "created_at",
    )
    list_editable = ("status",)
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_number", "customer_name", "email", "phone")
    readonly_fields = ("order_number", "subtotal", "delivery_fee", "discount", "total", "created_at", "user")
    inlines = [OrderItemInline]
    fieldsets = (
        ("Order", {"fields": ("order_number", "status", "created_at", "user")}),
        ("Customer", {"fields": ("customer_name", "phone", "email", "address", "city", "postal_code", "notes")}),
        ("Payment & totals", {"fields": ("payment_method", "subtotal", "delivery_fee", "discount", "total")}),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")


admin.site.site_header = "DukaLink Administration"
admin.site.site_title = "DukaLink Admin"
admin.site.index_title = "Store management"
