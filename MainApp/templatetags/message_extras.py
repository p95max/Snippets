from django import template

register = template.Library()

@register.filter
def message_mapping(origin_class):
    mapping = {
        'error': 'danger',
        'debug': 'light',
    }
    return mapping.get(origin_class, origin_class)