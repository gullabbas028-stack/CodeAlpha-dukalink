from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    icon = models.CharField(
        max_length=10,
        blank=True,
        help_text="A single emoji shown on the category card, e.g. 📱",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_list") + f"?category={self.slug}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Uploaded image takes priority; image_url is a fallback (used by seed data
    # so the catalog looks populated before any admin uploads real photos).
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(blank=True)

    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)
    features = models.TextField(
        blank=True, help_text="One feature per line — shown as a bullet list on the product page."
    )

    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base_slug}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return ""

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def stock_label(self):
        if self.stock <= 0:
            return "Out of stock"
        if self.stock <= 5:
            return f"Only {self.stock} left"
        return "In stock"

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name="wishlist_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="wishlisted_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("demo_card", "Demo Card Payment (test only)"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        User, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True
    )

    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        import random

        while True:
            candidate = f"DL-{random.randint(10000, 99999)}"
            if not Order.objects.filter(order_number=candidate).exists():
                return candidate

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot, survives product deletion
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # unit price at purchase time

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
