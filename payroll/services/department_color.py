# utils/department_colors.py
import hashlib

def get_department_colors(department_name):
    if not department_name:
        return {'bg': 'rgba(128, 128, 128, 0.2)', 'text': '#808080'}
    
    # Нормализуем название
    name = department_name.lower().strip()
    
    # Создаем хеш
    hash_obj = hashlib.md5(name.encode('utf-8'))
    hex_dig = hash_obj.hexdigest()
    
    # Генерируем hue из хеша (0-359)
    hue = int(hex_dig[:2], 16) % 360
    
    # Фиксированные значения для лучшей читаемости
    bg_color = f"hsla({hue}, 70%, 85%, 0.4)"
    text_color = f"hsl({hue}, 70%, 25%)"
    
    return {'bg': bg_color, 'text': text_color}

def get_all_departments_colors(departments):
    return {dept.name: get_department_colors(dept.name) for dept in departments}