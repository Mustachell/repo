from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def trim(value):
    return str(value).strip()

@register.filter
def matches_coordinates(value):
    # Patrón más estricto para coordenadas
    pattern = r'^\s*-?\d{1,2}\.\d{4,},-?\d{1,3}\.\d{4,}\s*$'
    
    try:
        value = str(value).strip()
        # Si no coincide con el patrón exacto, retornar False
        if not re.match(pattern, value):
            return False
        
        # Verificar que solo hay dos números separados por una coma
        parts = value.split(',')
        if len(parts) != 2:
            return False
            
        # Convertir a números y verificar rangos
        lat, lon = map(float, parts)
        
        # Verificar rangos válidos de coordenadas
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return False
            
        # Verificar que tienen suficientes decimales (al menos 4)
        if len(parts[0].split('.')[-1]) < 4 or len(parts[1].split('.')[-1]) < 4:
            return False
            
        return True
    except:
        return False 