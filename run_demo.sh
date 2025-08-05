#!/bin/bash

echo "🛬 Iniciando AIFA Demo..."

# Activar entorno virtual
source venv/bin/activate

# Verificar que estamos en el directorio correcto
if [ ! -f "dashboards/app.py" ]; then
    echo "❌ Error: No se encuentra app.py"
    echo "Ejecuta este script desde: /Users/robertodavila/aifa_rutas_demo/"
    exit 1
fi

echo "✅ Entorno virtual activado"
echo "🚀 Iniciando Streamlit en http://localhost:8501"

# Cambiar al directorio de dashboards y ejecutar
cd dashboards
streamlit run app.py