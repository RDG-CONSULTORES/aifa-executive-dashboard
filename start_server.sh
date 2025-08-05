#!/bin/bash

echo "🛬 AIFA Demo - Servidor en Background"

# Cambiar al directorio del proyecto
cd /Users/robertodavila/aifa_rutas_demo

# Activar entorno virtual
source venv/bin/activate

# Matar cualquier proceso existente en el puerto 8501
echo "🔄 Limpiando puertos..."
pkill -f "streamlit run app.py" 2>/dev/null || true
sleep 2

# Cambiar al directorio de dashboards
cd dashboards

# Ejecutar en background con nohup
echo "🚀 Iniciando servidor en background..."
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../streamlit.log 2>&1 &

# Obtener el PID del proceso
STREAMLIT_PID=$!
echo $STREAMLIT_PID > ../streamlit.pid

echo "✅ Servidor iniciado con PID: $STREAMLIT_PID"
echo "📊 Dashboard disponible en:"
echo "   - Local: http://localhost:8501"
echo "   - Red:   http://0.0.0.0:8501"
echo ""
echo "📝 Ver logs: tail -f streamlit.log"
echo "🛑 Para detener: ./stop_server.sh"
echo ""

# Esperar un momento y verificar que el servidor esté corriendo
sleep 3
if ps -p $STREAMLIT_PID > /dev/null; then
    echo "🎉 ¡Servidor ejecutándose correctamente!"
else
    echo "❌ Error al iniciar el servidor. Ver logs:"
    cat ../streamlit.log
fi