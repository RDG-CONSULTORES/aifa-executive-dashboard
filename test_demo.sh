#!/bin/bash

echo "🚀 Iniciando demo AIFA CORREGIDO..."
echo "📋 Características del demo:"
echo "   ✅ GitHub button y Deploy button ocultos"
echo "   ✅ Menú hamburger oculto"
echo "   ✅ Footer 'Made with Streamlit' oculto"
echo "   ✅ 8 tabs completamente funcionales SIN emojis"
echo "   ✅ Tema Aerospace Español profesional"
echo "   ✅ Todos los diagramas y KPIs funcionando"
echo ""
echo "🆕 CORRECCIONES APLICADAS:"
echo "   ✅ Error 'responsive' property corregido"
echo "   ✅ Emojis removidos del menú (como solicitado)"
echo "   ✅ Error 'No such file or directory' RESUELTO"
echo "   ✅ Sistema inteligente de búsqueda de archivos CSV"
echo "   ✅ Gráficas responsivas - NO se salen a la derecha"
echo "   ✅ Tabs con scroll horizontal para pantallas pequeñas"
echo "   ✅ Indicadores visuales para tab activo"
echo "   ✅ Diseño responsive para móviles y tablets"
echo ""
echo "📱 RESPONSIVE DESIGN:"
echo "   ✅ Desktop: Tabs completos visibles"
echo "   ✅ Tablet: Scroll horizontal con barra azul"
echo "   ✅ Móvil: Tabs compactos con scroll"
echo ""
echo "🌐 La aplicación se abrirá en: http://localhost:8504"
echo "⏹️  Para detener: Ctrl+C"
echo "💡 Prueba cambiar el tamaño del navegador para ver el responsive design"
echo ""

# Cambiar al directorio del proyecto
cd /Users/robertodavila/aifa_rutas_demo

# Ejecutar Streamlit en puerto específico
streamlit run streamlit_app_demo_final.py --server.port=8504