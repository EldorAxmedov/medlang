from django import template

register = template.Library()

@register.filter(name='split_matching')
def split_matching(value):
    """
    Splits 'Term :: Definition' into ['Term', 'Definition']
    """
    if not value or ' :: ' not in value:
        return [value, '']
    return value.split(' :: ', 1)
