from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def dict_get(d, key):
    """Возвращает значение словаря по ключу или None, если ключа нет"""
    return d.get(key)

@register.filter
def json_serialize(value):
    """Сериализует данные в JSON"""
    return mark_safe(json.dumps(value))