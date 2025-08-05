# 🆓 APIs GRATUITAS para AIFA Demo

## 🎯 APIs 100% GRATUITAS (Sin límite de tiempo)

### 1. **OpenSky Network** ✈️
- **URL**: https://opensky-network.org/api
- **Datos**: Vuelos en tiempo real, posiciones de aviones
- **Límite**: 1000 requests/día (gratis)
- **Sin registro**: ¡Usar directamente!
```python
# Ejemplo: Vuelos sobre México
https://opensky-network.org/api/states/all?lamin=14.5&lomin=-117&lamax=32.7&lomax=-86
```

### 2. **AeroDataBox (RapidAPI)** 🛫
- **URL**: https://rapidapi.com/aedbx-aedbx/api/aerodatabox
- **Datos**: Aeropuertos, vuelos, estadísticas
- **Límite**: 500 requests/mes GRATIS
- **Registro**: RapidAPI (gratis)
```python
# Info de AIFA (NLU)
https://aerodatabox.p.rapidapi.com/airports/icao/MMSM
```

### 3. **Exchange Rates API** 💱
- **URL**: https://exchangerate-api.com/
- **Datos**: Tipos de cambio USD/MXN
- **Límite**: 1500 requests/mes GRATIS
- **Para**: Convertir precios internacionales

### 4. **World Bank API** 📊
- **URL**: https://api.worldbank.org/
- **Datos**: Indicadores económicos México
- **Límite**: ILIMITADO
- **Sin registro**: Totalmente abierto
```python
# PIB México
https://api.worldbank.org/v2/country/MEX/indicator/NY.GDP.MKTP.CD?format=json
```

### 5. **INEGI API México** 🇲🇽
- **URL**: https://www.inegi.org.mx/servicios/api_indicadores.html
- **Datos**: Estadísticas oficiales México
- **Límite**: ILIMITADO
- **Registro**: Token gratis

---

## 💎 APIs CON TIER GRATUITO GENEROSO

### 6. **AviationStack** ✈️
- **Free Tier**: 100 requests/mes
- **Datos**: Rutas, aerolíneas, vuelos
- **Suficiente para**: Demo básico
```python
# Rutas desde AIFA
http://api.aviationstack.com/v1/routes?dep_iata=NLU&access_key=TU_KEY
```

### 7. **OpenWeatherMap** 🌤️
- **Free Tier**: 1000 requests/día
- **Datos**: Clima en aeropuertos
- **Útil para**: Factor clima en operaciones
```python
# Clima CDMX
https://api.openweathermap.org/data/2.5/weather?q=Mexico+City&appid=TU_KEY
```

### 8. **Mapbox** 🗺️
- **Free Tier**: 50,000 requests/mes
- **Datos**: Mapas, rutas terrestres
- **Para**: Conectividad AIFA-CDMX

### 9. **NewsAPI** 📰
- **Free Tier**: 100 requests/día
- **Datos**: Noticias AIFA, aviación México
- **Para**: Sentiment analysis
```python
# Noticias AIFA
https://newsapi.org/v2/everything?q=AIFA+aeropuerto&apiKey=TU_KEY
```

### 10. **Abstract API** 🔍
- **Free Tier**: 1000 requests/mes
- **Datos**: Geolocalización, timezone
- **Para**: Análisis de conexiones

---

## 🚀 APIs ESPECÍFICAS AVIACIÓN MÉXICO

### 11. **FlightRadar24** (No oficial)
- **Método**: Web scraping permitido
- **Datos**: Vuelos en tiempo real
- **Límite**: Uso responsable
```python
# Requiere headers de navegador
headers = {'User-Agent': 'Mozilla/5.0...'}
```

### 12. **Datos Abiertos México** 🇲🇽
- **URL**: https://datos.gob.mx/
- **Datasets**: 
  - Estadísticas aeroportuarias SCT
  - Pasajeros por aeropuerto
  - Operaciones aéreas
- **Límite**: ILIMITADO
- **Formato**: CSV, JSON, API

### 13. **SENEAM México** ✈️
- **URL**: Publicaciones mensuales
- **Datos**: Tráfico aéreo oficial
- **Formato**: PDF (convertir a datos)
- **Gratis**: Información pública

---

## 📊 IMPLEMENTACIÓN RÁPIDA

### **Opción 1: Mix Gratuito**
```python
# Combinación 100% gratis
- OpenSky: Vuelos en tiempo real
- World Bank: Datos económicos
- INEGI: Estadísticas México
- Datos.gob.mx: Pasajeros históricos
```

### **Opción 2: Free Tier Óptimo**
```python
# ~1000 requests/mes gratis
- AeroDataBox: 500/mes
- AviationStack: 100/mes
- NewsAPI: 100/día
- OpenWeather: 1000/día
```

### **Opción 3: Web Scraping Legal**
```python
# Sitios públicos permitidos
- AIFA oficial: Rutas publicadas
- SCT: Estadísticas mensuales
- FlightRadar24: Con límites
- Aerolíneas: Horarios públicos
```

---

## 🔧 CONFIGURACIÓN INMEDIATA

### **Paso 1: APIs Sin Registro**
```bash
# OpenSky Network - Vuelos en tiempo real
curl "https://opensky-network.org/api/states/all?lamin=19&lomin=-99.5&lamax=20&lomax=-98.5"

# World Bank - Datos económicos
curl "https://api.worldbank.org/v2/country/MEX/indicator/NY.GDP.MKTP.CD?format=json&date=2020:2023"
```

### **Paso 2: Registro Rápido (5 min)**
1. **RapidAPI**: https://rapidapi.com/signup
2. **OpenWeather**: https://openweathermap.org/api
3. **NewsAPI**: https://newsapi.org/register

### **Paso 3: Actualizar Cliente**
```python
# En api_client.py agregar:
FREE_APIS = {
    'opensky': {
        'base_url': 'https://opensky-network.org/api',
        'auth': False
    },
    'worldbank': {
        'base_url': 'https://api.worldbank.org/v2',
        'auth': False
    }
}
```

---

## 💡 ESTRATEGIA RECOMENDADA

### **Para Demo Inmediato (0 costo):**
1. **OpenSky**: Vuelos en tiempo real ✅
2. **Datos.gob.mx**: Estadísticas AIFA ✅
3. **World Bank**: Contexto económico ✅
4. **Web scraping**: Rutas actuales ✅

### **Para Demo Mejorado ($0 con límites):**
1. **AeroDataBox**: 500 req/mes
2. **AviationStack**: 100 req/mes
3. **OpenWeather**: Clima aeropuertos
4. **NewsAPI**: Sentiment analysis

### **Datos que SÍ puedes obtener GRATIS:**
- ✅ Vuelos en tiempo real (OpenSky)
- ✅ Información aeropuertos (AeroDataBox)
- ✅ Estadísticas México (INEGI/Datos.gob)
- ✅ Clima aeropuertos (OpenWeather)
- ✅ Noticias AIFA (NewsAPI)
- ✅ Indicadores económicos (World Bank)
- ✅ Tipos de cambio (ExchangeRate)

### **Limitaciones del plan gratuito:**
- ❌ Precios de boletos en tiempo real
- ❌ Disponibilidad de asientos
- ❌ Datos privados de aerolíneas
- ⚠️ Límites de requests mensuales
- ⚠️ Sin SLA garantizado

---

## 🚀 SCRIPT DE INICIO RÁPIDO

```bash
# 1. Configurar APIs gratuitas
cd /Users/robertodavila/aifa_rutas_demo
echo "OPENSKY_API=https://opensky-network.org/api" >> .env
echo "RAPIDAPI_KEY=tu_key_gratis" >> .env

# 2. Instalar dependencias extra
pip install beautifulsoup4 selenium

# 3. Ejecutar fetcher con APIs gratis
python scripts/free_data_fetcher.py

# 4. ¡Listo! Dashboard con datos reales
./start_server.sh
```

**🎯 Con estas APIs gratuitas puedes tener un demo funcional con datos reales de aviación sin gastar un peso.**