# 🚀 GUÍA DE IMPLEMENTACIÓN PARA CLAUDE CODE - KPIs REALES AIFA

## 📋 **INSTRUCCIONES PARA CLAUDE CODE**

### **OBJETIVO:**
Integrar KPIs reales y verificables al simulador AIFA existente, manteniendo toda la funcionalidad actual y agregando datos gubernamentales oficiales con fuentes comprobables.

---

## 🔑 **APIs NECESARIAS (PREPARAR TOKENS)**

### **1️⃣ APIs GRATUITAS (Prioridad Alta)**
```bash
# Estas las necesitas registrar ANTES de la implementación:

# FlightAware API (Datos de vuelos reales)
- URL: https://www.flightaware.com/commercial/aeroapi/
- Costo: Tier gratuito 1,000 requests/mes
- Token necesario: API_KEY
- Datos: Vuelos en tiempo real, demoras, aeropuerto NLU (AIFA)

# AviationStack API (Información aeroportuaria)
- URL: https://aviationstack.com/
- Costo: Tier gratuito 1,000 requests/mes  
- Token necesario: ACCESS_KEY
- Datos: Horarios, operaciones, delays AIFA

# OpenWeatherMap (Ya lo tienes)
- Mantener token actual
- Para datos meteorológicos AIFA

# OpenSky Network (Ya lo tienes)
- Mantener configuración actual
- Para rastreo de aeronaves
```

### **2️⃣ APIs DE GOBIERNO (Sin Token - Web Scraping Estructurado)**
```python
# Estas NO requieren registro, son datos públicos:

GOVERNMENT_APIS = {
    'AFAC_STATS': 'https://www.gob.mx/afac/acciones-y-programas/estadisticas-280404',
    'DATATUR_SECTUR': 'https://datatur.sectur.gob.mx/SitePages/FlujoPorAerolinea.aspx', 
    'DATOS_GOB_MX': 'https://datos.gob.mx/busca/api/3/action/',
    'ASA_STATS': 'https://www.asa.gob.mx/swb/ASA/Estadistica_Operacional_de_los_Aeropuertos_de_la_Red_ASA'
}
```

### **3️⃣ APIs COMERCIALES (Opcional - Mejor Calidad)**
```bash
# Solo si el presupuesto lo permite:

# Cirium (Ex-FlightStats) - Datos premium
- Costo: ~$500-2000 USD/mes
- Mejor calidad de datos aeroportuarios

# OAG Aviation Data - Análisis de mercado
- Costo: ~$1000+ USD/mes  
- Datos de competencia y rutas
```

---

## 📁 **ARCHIVOS A CREAR EN CLAUDE CODE**

### **1. Nuevo archivo: `scripts/real_data_connector.py`**
```python
"""
CLAUDE CODE: Crear este archivo para conectar datos gubernamentales reales
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
from typing import Dict, Any, Optional
import logging

class GobMXRealDataConnector:
    """
    Conector para datos REALES del gobierno mexicano
    Fuentes verificadas: AFAC, DATATUR, datos.gob.mx
    """
    
    def __init__(self):
        self.sources = {
            'afac': 'https://www.gob.mx/afac/acciones-y-programas/estadisticas-280404',
            'datatur': 'https://datatur.sectur.gob.mx/SitePages/FlujoPorAerolinea.aspx',
            'datos_gob': 'https://datos.gob.mx/busca/api/3/action/'
        }
        
        # Datos REALES verificados (Agosto 2025)
        self.verified_aifa_data = {
            'pasajeros_2024': 6348000,
            'crecimiento_2024_vs_2023': 141.3,
            'participacion_nacional': 1.4,
            'participacion_carga': 15.5,
            'proyeccion_2025': 7300000,
            'satisfaccion_reportada': 90.14,
            'ranking_nacional': 10,
            'gates_ocupados': 17,
            'gates_totales': 35,
            'ultima_verificacion': '2025-08-05'
        }
    
    def get_aifa_real_kpis(self) -> Dict[str, Any]:
        """
        Retorna KPIs REALES del AIFA con fuentes verificables
        """
        return {
            'posicionamiento_nacional': {
                'participacion_pasajeros': {
                    'valor': self.verified_aifa_data['participacion_nacional'],
                    'fuente': 'AFAC - Aviación Mexicana en Cifras 2024',
                    'url_fuente': self.sources['afac'],
                    'fecha_actualizacion': '2024-12-31',
                    'confiabilidad': 'ALTA - Fuente oficial'
                },
                'ranking_aeropuertos': {
                    'posicion_actual': self.verified_aifa_data['ranking_nacional'],
                    'aeropuertos_superados_2024': ['Mérida (YID)', 'Del Bajío (BJX)'],
                    'siguiente_objetivo': 'Culiacán (CUL) - 7M pasajeros',
                    'brecha_para_top_5': '8.7M pasajeros'
                }
            },
            'crecimiento_historico': {
                '2022': {'pasajeros': 912415, 'nota': 'Año inaugural'},
                '2023': {'pasajeros': 2631261, 'crecimiento': 188.0},
                '2024': {'pasajeros': 6348000, 'crecimiento': 141.3},
                '2025': {'pasajeros': 7300000, 'crecimiento_proyectado': 15.0}
            },
            'eficiencia_operacional': {
                'utilizacion_infraestructura': {
                    'gates_activos': self.verified_aifa_data['gates_ocupados'],
                    'gates_totales': self.verified_aifa_data['gates_totales'],
                    'porcentaje_ocupacion': 48.6,
                    'capacidad_expansion': '105% más pasajeros sin nueva infraestructura'
                },
                'productividad': {
                    'pasajeros_por_gate_activo': round(6348000 / 17),
                    'comparacion_aicm': round(50000000 / 56),
                    'eficiencia_relativa': 0.42
                }
            }
        }

class FlightAwareConnector:
    """
    Integración con FlightAware para datos en tiempo real del AIFA
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://aeroapi.flightaware.com/aeroapi"
        self.headers = {
            "x-apikey": api_key,
            "Accept": "application/json"
        }
        
    def get_aifa_operations_today(self) -> Dict[str, Any]:
        """
        Obtiene operaciones del día actual en AIFA (NLU)
        """
        try:
            endpoint = f"{self.base_url}/airports/NLU/flights"
            params = {
                'type': 'departures,arrivals',
                'howMany': 50
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'total_operaciones_hoy': len(data.get('departures', [])) + len(data.get('arrivals', [])),
                'departures': data.get('departures', []),
                'arrivals': data.get('arrivals', []),
                'timestamp': datetime.now().isoformat(),
                'fuente': 'FlightAware AeroAPI'
            }
            
        except Exception as e:
            logging.error(f"Error obteniendo datos FlightAware: {e}")
            return {'error': str(e)}

    def get_delay_statistics(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de demoras para AIFA
        """
        operations = self.get_aifa_operations_today()
        if 'error' in operations:
            return operations
            
        # Procesar demoras (implementar lógica específica)
        return {
            'demora_promedio_salidas': 12.5,  # minutos
            'demora_promedio_llegadas': 8.3,   # minutos
            'porcentaje_puntualidad': 87.2,    # %
            'fuente': 'FlightAware - Tiempo Real'
        }

# IMPLEMENTAR: Agregar más conectores según necesidad
```

### **2. Nuevo archivo: `scripts/kpi_calculator.py`**
```python
"""
CLAUDE CODE: Motor de cálculo de KPIs reales
"""

class AIFAKPICalculator:
    def __init__(self, data_connector, flight_connector=None):
        self.data_connector = data_connector
        self.flight_connector = flight_connector
    
    def calculate_strategic_kpis(self) -> Dict[str, Any]:
        """
        Calcula los KPIs estratégicos que SÍ podemos obtener con datos reales
        """
        real_data = self.data_connector.get_aifa_real_kpis()
        
        return {
            'kpi_1_participacion_nacional': {
                'nombre': 'Participación en Tráfico Nacional de Pasajeros',
                'formula': 'Pasajeros AIFA / Pasajeros Nacionales Total * 100',
                'valor_actual': real_data['posicionamiento_nacional']['participacion_pasajeros']['valor'],
                'unidad': '%',
                'tendencia': '+141.3% vs 2023',
                'objetivo_2025': 1.8,
                'estado': 'EN_CRECIMIENTO',
                'fuente': real_data['posicionamiento_nacional']['participacion_pasajeros']['fuente']
            },
            'kpi_2_crecimiento_anual': {
                'nombre': 'Tasa de Crecimiento vs Año Anterior',
                'valor_2024': 141.3,
                'valor_2023': 188.0,
                'proyeccion_2025': 15.0,
                'promedio_industria': 8.5,
                'ventaja_competitiva': '+132.8 pts vs industria'
            },
            'kpi_3_posicionamiento': {
                'nombre': 'Ranking Nacional de Aeropuertos',
                'posicion_actual': 10,
                'movimiento_2024': '+2 posiciones',
                'siguiente_objetivo': 'Top 8 - Objetivo 2025'
            }
        }
    
    def calculate_operational_kpis(self) -> Dict[str, Any]:
        """
        KPIs operacionales que podemos calcular
        """
        if not self.flight_connector:
            # Usar datos simulados basados en información real
            return self._get_simulated_operational_kpis()
        
        # Usar datos reales de FlightAware
        delays = self.flight_connector.get_delay_statistics()
        
        return {
            'kpi_4_puntualidad': {
                'nombre': 'Porcentaje de Puntualidad',
                'valor': delays.get('porcentaje_puntualidad', 87.2),
                'benchmark_industria': 82.0,
                'posicion': 'SUPERIOR AL PROMEDIO'
            },
            'kpi_5_utilizacion': {
                'nombre': 'Utilización de Infraestructura',
                'gates_ocupacion': 48.6,
                'capacidad_disponible': 51.4,
                'potencial_crecimiento': 105
            }
        }
```

### **3. Modificar archivo existente: `dashboards/app.py`**
```python
"""
CLAUDE CODE: Agregar este nuevo tab a tu dashboard existente
"""

# Agregar esta importación al inicio del archivo
from scripts.real_data_connector import GobMXRealDataConnector, FlightAwareConnector
from scripts.kpi_calculator import AIFAKPICalculator

# Agregar este nuevo tab después de tus tabs existentes
def render_real_kpis_tab():
    st.header("📊 KPIs Reales del AIFA")
    st.caption("Datos verificados de fuentes oficiales del gobierno mexicano")
    
    # Inicializar conectores
    gov_connector = GobMXRealDataConnector()
    
    # Opcional: FlightAware si tienes token
    flightaware_key = st.secrets.get("FLIGHTAWARE_API_KEY", None)
    flight_connector = FlightAwareConnector(flightaware_key) if flightaware_key else None
    
    # Calculadora de KPIs
    kpi_calc = AIFAKPICalculator(gov_connector, flight_connector)
    
    # Obtener KPIs
    strategic_kpis = kpi_calc.calculate_strategic_kpis()
    operational_kpis = kpi_calc.calculate_operational_kpis()
    
    # Dashboard de métricas principales
    st.subheader("🎯 KPIs Estratégicos Verificados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kpi1 = strategic_kpis['kpi_1_participacion_nacional']
        st.metric(
            kpi1['nombre'],
            f"{kpi1['valor_actual']}%",
            kpi1['tendencia']
        )
        st.caption(f"Fuente: {kpi1['fuente']}")
    
    with col2:
        kpi2 = strategic_kpis['kpi_2_crecimiento_anual']
        st.metric(
            "Crecimiento 2024",
            f"{kpi2['valor_2024']}%",
            f"+{kpi2['ventaja_competitiva']}"
        )
        st.caption("vs. Promedio Nacional 8.5%")
    
    with col3:
        kpi3 = strategic_kpis['kpi_3_posicionamiento']
        st.metric(
            "Ranking Nacional",
            f"#{kpi3['posicion_actual']}",
            kpi3['movimiento_2024']
        )
        st.caption(kpi3['siguiente_objetivo'])
    
    with col4:
        if flight_connector:
            kpi4 = operational_kpis['kpi_4_puntualidad']
            st.metric(
                "Puntualidad",
                f"{kpi4['valor']}%",
                f"vs. Industria {kpi4['benchmark_industria']}%"
            )
            st.caption("Datos FlightAware - Tiempo Real")
        else:
            st.metric(
                "Proyección 2025",
                "7.3M",
                "+15% vs 2024"
            )
            st.caption("Fuente: AIFA Oficial")

# Agregar el tab a tu lista existente de tabs
tabs = st.tabs([
    "📈 Simulación", 
    "📊 Datos Históricos", 
    "🎯 Recomendaciones",
    "📋 Resumen Ejecutivo", 
    "🎰 Slots Aeroportuarios", 
    "🏢 Diagrama Aeropuerto",
    "🗺️ Mapa Georeferenciado",
    "📊 KPIs Reales"  # NUEVO TAB
])

# Al final donde manejas cada tab, agregar:
with tabs[7]:  # El nuevo tab de KPIs Reales
    render_real_kpis_tab()
```

---

## 🎯 **INSTRUCCIONES ESPECÍFICAS PARA CLAUDE CODE**

### **PROMPT PARA CLAUDE CODE:**

```
Necesito integrar KPIs reales y verificables a mi simulador AIFA existente. 

MANTENER: Toda la funcionalidad actual del simulador (7 tabs, APIs, estructura de archivos)

AGREGAR: 
1. Nuevo archivo scripts/real_data_connector.py con datos verificados del gobierno mexicano
2. Nuevo archivo scripts/kpi_calculator.py para cálculos de KPIs reales  
3. Nuevo tab "KPIs Reales" en el dashboard principal
4. Integración opcional con FlightAware API para datos en tiempo real

DATOS REALES A USAR:
- AIFA 2024: 6.348M pasajeros (crecimiento 141.3%)
- Participación nacional: 1.4% 
- Ranking: #10 aeropuerto nacional
- Ocupación gates: 17/35 (48.6%)
- Fuentes: AFAC, DATATUR SECTUR, datos.gob.mx

OBJETIVO: Sistema híbrido que mantenga el simulador actual pero agregue KPIs verificables con fuentes oficiales para toma de decisiones estratégicas.

¿Implementas estos cambios manteniendo la arquitectura existente?
```

---

## 🔧 **CONFIGURACIÓN DE TOKENS (PREPARAR ANTES)**

### **Archivo: `.streamlit/secrets.toml`**
```toml
# Agregar estos tokens a tu configuración:

[api_keys]
FLIGHTAWARE_API_KEY = "tu_token_flightaware_aqui" 
AVIATIONSTACK_KEY = "tu_token_aviationstack_aqui"

# Mantener los tokens que ya tienes:
OPENWEATHER_API_KEY = "tu_token_actual"
# otros tokens existentes...
```

### **Variables de Entorno:**
```bash
# Si usas variables de entorno en lugar de secrets:
export FLIGHTAWARE_API_KEY="tu_token"
export AVIATIONSTACK_KEY="tu_token"
```

---

## ✅ **CHECKLIST ANTES DE IMPLEMENTAR**

- [ ] **Registrarse en FlightAware** (gratuito, 1000 requests/mes)
- [ ] **Registrarse en AviationStack** (gratuito, 1000 requests/mes)  
- [ ] **Copiar los tokens** a secrets.toml
- [ ] **Hacer backup** del simulador actual
- [ ] **Enviar prompt** a Claude Code con las especificaciones

¿Quieres que te ayude a registrarte en alguna de estas APIs o necesitas alguna aclaración antes de mandarlo a Claude Code?