from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Возвращает значение словаря по ключу или None, если ключа нет"""
    return d.get(key)