# 🚀 Guía de Deploy AIFA Demo

## 🆓 **OPCIÓN RECOMENDADA: Streamlit Community Cloud**

### **✅ Ventajas:**
- **100% GRATIS** para siempre
- Deploy automático desde GitHub
- SSL incluido
- URL: `https://aifa-rutas-demo.streamlit.app`
- Mantenimiento automático

### **📋 PASOS PARA DEPLOY:**

#### **1. Crear Repositorio GitHub**
```bash
# En tu Mac
cd /Users/robertodavila/aifa_rutas_demo

# Inicializar git (si no está ya)
git init

# Agregar archivos
git add .
git commit -m "AIFA Demo - Simulador completo con slots y métricas"

# Subir a GitHub (crear repo primero en github.com)
git remote add origin https://github.com/TU_USUARIO/aifa-rutas-demo.git
git push -u origin main
```

#### **2. Deploy en Streamlit Cloud**
1. **Ir a:** https://share.streamlit.io/
2. **Sign in** con GitHub
3. **New app** → Conectar tu repositorio
4. **Configurar:**
   - Repository: `TU_USUARIO/aifa-rutas-demo`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
5. **Deploy!**

#### **3. ¡Listo!**
Tu app estará en: `https://aifa-rutas-demo.streamlit.app`

---

## 💰 **ALTERNATIVAS PAGAS:**

### **🚂 Railway - $5/mes**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### **🌊 Digital Ocean - $5/mes**
```bash
# Crear app.yaml
# Deploy desde GitHub
```

### **🟣 Heroku - $7/mes**
```bash
# Crear Procfile
echo "web: streamlit run streamlit_app.py --server.port=$PORT" > Procfile

# Deploy
heroku create aifa-demo
git push heroku main
```

---

## 📦 **ARCHIVOS PREPARADOS PARA DEPLOY:**

✅ `streamlit_app.py` - Entry point para Streamlit Cloud  
✅ `requirements.txt` - Dependencias actualizadas  
✅ `.streamlit/config.toml` - Configuración optimizada  
✅ `.gitignore` - Archivos a ignorar  
✅ `README.md` - Documentación completa  

## 🔧 **CONFIGURACIÓN STREAMLIT CLOUD:**

**Archivo principal:** `streamlit_app.py`  
**Puerto:** 8501 (automático)  
**Python:** 3.9+ (automático)  
**Región:** US East (default)  

## 🌐 **URLs RESULTANTES:**

### **Streamlit Cloud (GRATIS):**
- `https://aifa-rutas-demo.streamlit.app`
- `https://aifa-demo-robertodavila.streamlit.app`

### **Railway ($5/mes):**
- `https://aifa-demo.railway.app`

### **Heroku ($7/mes):**
- `https://aifa-demo.herokuapp.com`

---

## 🚀 **DEPLOY INMEDIATO:**

### **Para Deploy HOY MISMO:**

1. **Crear cuenta GitHub** (si no tienes)
2. **Subir código** (5 min)
3. **Conectar a Streamlit Cloud** (2 min)
4. **¡Demo online!** (https://tu-app.streamlit.app)

### **Comando Rápido GitHub:**
```bash
# Todo en uno
cd /Users/robertodavila/aifa_rutas_demo
git init
git add .
git commit -m "🛬 AIFA Demo - Simulador profesional"
# Crear repo en github.com primero, luego:
git remote add origin https://github.com/TU_USUARIO/aifa-rutas-demo.git
git push -u origin main
```

**🎯 En 10 minutos puedes tener tu demo live para mostrar a cualquier aerolínea o inversionista.**

## 📊 **MÉTRICAS ESPERADAS:**

- **Carga inicial:** ~10-15 segundos
- **Interacciones:** <2 segundos
- **Uptime:** 99.9% (Streamlit Cloud)
- **Concurrent users:** 100+ sin problema

## 🔐 **DOMINIO PERSONALIZADO (OPCIONAL):**

Para tener `https://aifa-demo.com`:
1. Comprar dominio ($10-15/año)
2. Configurar DNS → Streamlit Cloud
3. SSL automático incluido

**🎉 Tu demo estará disponible 24/7 desde cualquier dispositivo en el mundo**