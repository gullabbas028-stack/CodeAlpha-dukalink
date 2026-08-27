from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer_name",
            "phone",
            "email",
            "address",
            "city",
            "postal_code",
            "notes",
            "payment_method",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "e.g. Ayesha Khan"}),
            "phone": forms.TextInput(attrs={"placeholder": "03xx-xxxxxxx"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "address": forms.TextInput(attrs={"placeholder": "House / street / area"}),
            "city": forms.TextInput(attrs={"placeholder": "e.g. Lahore"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "e.g. 54000"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Anything we should know? (optional)"}),
            "payment_method": forms.RadioSelect,
        }
        labels = {
            "customer_name": "Full name",
            "postal_code": "Postal code",
            "notes": "Order notes (optional)",
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
