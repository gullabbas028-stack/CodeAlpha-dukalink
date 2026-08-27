from django import template
from django.conf import settings

register = template.Library()


@register.filter
def pkr(value):
    """Format a number as 'Rs. 4,999' (no decimals when it's a whole number)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    if value == int(value):
        formatted = f"{int(value):,}"
    else:
        formatted = f"{value:,.2f}"
    return f"{settings.CURRENCY_SYMBOL}{formatted}"


@register.filter
def star_range(rating):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    full = int(rating)
    return range(full)


@register.filter
def empty_star_range(rating):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    return range(5 - int(rating))
