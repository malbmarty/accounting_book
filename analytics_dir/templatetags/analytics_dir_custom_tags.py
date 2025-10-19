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

@register.simple_tag
def equalize_columns(*columns):
    """
    Делает все списки одинаковой длины, добавляя None в конец недостающих.
    Пример:
        {% equalize_columns list1 list2 list3 as cols %}
        {% for col in cols.0 %}
            ...
        {% endfor %}
    """
    # вычисляем максимальную длину
    max_len = max(len(col) for col in columns if col is not None)

    # дополняем каждый список до одинаковой длины
    equalized = []
    for col in columns:
        if col is None:
            col = []
        col = list(col) + [None] * (max_len - len(col))
        equalized.append(col)

    return equalized