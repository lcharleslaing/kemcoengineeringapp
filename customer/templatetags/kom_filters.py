from django import template

register = template.Library()

@register.filter
def has_value(value):
    """Check if a value is meaningful (not None, empty string, 'MISSING', or '-')"""
    if value is None:
        return False
    if isinstance(value, str):
        value = value.strip()
        if not value or value.upper() == 'MISSING' or value == '-':
            return False
    if isinstance(value, (int, float)):
        return True  # Numbers are always meaningful
    if isinstance(value, bool):
        return True  # Booleans are always meaningful
    return bool(value)

@register.filter
def display_if(value, default="-"):
    """Display value if it has meaning, otherwise return default"""
    if has_value(value):
        return value
    return default

