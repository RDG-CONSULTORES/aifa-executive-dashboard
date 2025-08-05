#!/bin/bash

echo "🛑 Deteniendo servidor AIFA..."

# Cambiar al directorio del proyecto
cd /Users/robertodavila/aifa_rutas_demo

# Leer el PID si existe
if [ -f "streamlit.pid" ]; then
    PID=$(cat streamlit.pid)
    if ps -p $PID > /dev/null; then
        echo "🔄 Deteniendo proceso PID: $PID"
        kill $PID
        sleep 2
        if ps -p $PID > /dev/null; then
            echo "⚠️  Forzando cierre..."
            kill -9 $PID
        fi
    fi
    rm streamlit.pid
fi

# Matar cualquier proceso restante
pkill -f "streamlit run app.py" 2>/dev/null || true

echo "✅ Servidor detenido"