# myapp/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split the string by the given delimiter (arg)."""
    return value.split(arg) if value else []
