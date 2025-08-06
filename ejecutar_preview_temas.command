#!/bin/bash

# Script para ejecutar la demo completa AIFA con temas

echo "✈️ AIFA - Demo Completa con Temas"
echo "=================================="
echo ""

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Verificar si streamlit está instalado
if ! command -v streamlit &> /dev/null
then
    echo "⚠️  Streamlit no está instalado. Instalando..."
    pip3 install streamlit pandas matplotlib plotly pytz numpy
    echo ""
fi

# Menú de opciones
echo "Selecciona qué demo ejecutar:"
echo ""
echo "1) Demo Completa (Aerospace Español) - Recomendado"
echo "2) Preview de Temas (comparar opciones)"
echo "3) Versión en Producción (actual)"
echo ""
read -p "Opción (1-3): " opcion

case $opcion in
    1)
        archivo="streamlit_app_demo_completa.py"
        echo ""
        echo "🚀 Ejecutando Demo Completa con tema Aerospace Español..."
        ;;
    2)
        archivo="streamlit_app_themes_preview.py"
        echo ""
        echo "🎨 Ejecutando Preview de Temas..."
        ;;
    3)
        archivo="streamlit_app.py"
        echo ""
        echo "📊 Ejecutando Versión en Producción..."
        ;;
    *)
        echo "Opción inválida. Saliendo..."
        exit 1
        ;;
esac

echo ""
echo "✅ Abriendo en tu navegador..."
echo ""
echo "🌐 Si no se abre automáticamente, visita:"
echo "   http://localhost:8501"
echo ""
echo "📌 Para detener: Presiona Control+C"
echo ""

# Ejecutar Streamlit
streamlit run $archivo

# Mantener terminal abierta
read -p "Presiona Enter para cerrar..."