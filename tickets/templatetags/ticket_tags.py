from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """Recherche une valeur dans un dictionnaire ou une liste de tuples"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, key)
    elif isinstance(dictionary, (list, tuple)):
        for item_key, item_value in dictionary:
            if item_key == key:
                return item_value
    return key
