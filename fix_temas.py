#!/usr/bin/env python3
"""
Script para arreglar los temas en streamlit_app_demo_completa.py
Reemplaza todas las clases CSS hardcoded con una función dinámica
"""

import re

def fix_themes():
    # Leer el archivo
    with open('streamlit_app_demo_completa.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar todas las instancias de metric-aerospace con una función dinámica
    # Patrón para encontrar divs con clase metric-aerospace
    pattern = r'<div class="metric-aerospace">'
    replacement = '<div class="{css_class}">'
    
    # Reemplazar
    content = content.replace(pattern, replacement)
    
    # Agregar la definición de css_class al inicio de cada sección que usa métricas
    sections_to_fix = [
        ('# Usar la función render_metric para todas las métricas', 
         '# Usar la función render_metric para todas las métricas\n    css_class = get_metric_class()'),
        ('# Métricas principales en tiempo real', 
         '# Métricas principales en tiempo real\n    css_class = get_metric_class()'),
        ('# Mostrar métricas del análisis', 
         '# Mostrar métricas del análisis\n    css_class = get_metric_class()')
    ]
    
    for old, new in sections_to_fix:
        content = content.replace(old, new)
    
    # Función get_metric_class debe estar disponible globalmente
    global_func = '''
def get_metric_class():
    """Determina la clase CSS correcta según el tema actual"""
    theme_name = st.session_state.get('theme_name', 'Aerospace Español')
    if "Aerospace" in theme_name:
        return "metric-aerospace"
    elif theme_name == "Corporativo Minimalista":
        return "metric-corporate"
    elif theme_name == "Gobierno Oficial":
        return "metric-gov"
    elif theme_name == "Modo Oscuro Profesional":
        return "metric-dark"
    else:
        return "metric-classic"

'''
    
    # Insertar la función después de las funciones CSS
    insertion_point = "# Función para cargar datos"
    content = content.replace(insertion_point, global_func + insertion_point)
    
    # Escribir el archivo corregido
    with open('streamlit_app_demo_completa.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Temas corregidos exitosamente!")
    print("Todos los temas ahora deberían funcionar correctamente.")

if __name__ == "__main__":
    fix_themes()