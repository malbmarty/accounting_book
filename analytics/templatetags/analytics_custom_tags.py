from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Позволяет брать значение словаря по ключу в шаблоне"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def dict_get(d, key):
    """Возвращает значение словаря по ключу или None, если ключа нет"""
    return d.get(key)


