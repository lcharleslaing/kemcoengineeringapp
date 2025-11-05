from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary
    Usage: {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def format_duration(duration):
    """
    Format timedelta duration for display
    """
    if not duration:
        return ""
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
