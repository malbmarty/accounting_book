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

@register.simple_tag
def zip_lists(list1, list2):
    return zip(list1, list2)

@register.filter
def get_project_name(projects, project_id):
    if project_id is None or project_id == '':
        return ''
    try:
        pid = int(project_id)
    except (ValueError, TypeError):
        return ''
    for p in projects:
        # если projects — queryset, p.id будет int
        if p.id == pid:
            return p.name
    return ''