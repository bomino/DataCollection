

# collection/templatetags/collection_filters.py
from django import template

register = template.Library()

@register.filter
def filter_by_status(queryset, status):
    """Filter uploads by their status."""
    return [item for item in queryset if item.status == status]


@register.filter
def split_errors(value):
    """Split error message into list by newlines"""
    if isinstance(value, str):
        return value.split('\n')
    return value

@register.filter
def startswith(value, arg):
    """Check if string starts with argument"""
    return value.startswith(arg)

@register.filter
def is_list(value):
    """Check if the value is a list or tuple"""
    return isinstance(value, (list, tuple))