from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Safely get a value from a dictionary."""
    return dictionary.get(key, [])

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])