#!/bin/bash

echo "🚀 ACTUALIZANDO VERSIÓN DE PRODUCCIÓN AIFA..."
echo ""
echo "📋 MEJORAS APLICADAS:"
echo "   ✅ GitHub button y Deploy button OCULTOS"
echo "   ✅ Menú hamburger y footer OCULTOS" 
echo "   ✅ Tabs SIN emojis (profesional)"
echo "   ✅ Gráficas responsivas - NO overflow"
echo "   ✅ Sistema inteligente de carga de archivos CSV"
echo "   ✅ Tabs con scroll horizontal"
echo "   ✅ Diseño responsive completo"
echo "   ✅ Tema Aerospace Español profesional"
echo "   ✅ 8 tabs completamente funcionales"
echo ""
echo "⏹️  Deteniendo versión anterior..."

# Detener procesos de Streamlit existentes
pkill -f "streamlit run streamlit_app.py"
sleep 2

echo "🔄 Iniciando versión actualizada..."
echo "🌐 La aplicación estará disponible en: http://localhost:8501"
echo "⏹️  Para detener: Ctrl+C"
echo ""

# Cambiar al directorio del proyecto
cd /Users/robertodavila/aifa_rutas_demo

# Ejecutar Streamlit en producción
streamlit run streamlit_app.py