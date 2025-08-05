# 🛬 AIFA - Sistema de Análisis Ejecutivo

Dashboard ejecutivo en tiempo real para el Aeropuerto Internacional Felipe Ángeles (AIFA) con datos de 5 fuentes oficiales.

## 🎯 Características

- **5 APIs integradas** con datos en tiempo real
- **13 KPIs** estratégicos, operacionales y económicos  
- **Score general 82/100** (ALTO DESEMPEÑO)
- **Dashboard interactivo** con 8 secciones

## 📊 Fuentes de Datos

1. **Gobierno de México** - KPIs oficiales AFAC/DATATUR
2. **AviationStack** - Operaciones tiempo real (40 vuelos/día)
3. **FlightAware** - Puntualidad real (95% vs 82% industria)
4. **OpenWeatherMap** - Meteorología OneCall 3.0
5. **FlightRadar24** - Rastreo de aeronaves área México

## 🚀 Características

### ✨ Simulador de Rutas
- Cálculo de ROI anual y mensual
- Análisis de costos operativos detallados
- Proyecciones de ingresos con factores estacionales
- Score de viabilidad automatizado

### 📊 Dashboard Interactivo
- **4 Pestañas Principales**:
  - 📈 **Simulación**: Configuración y resultados en tiempo real
  - 📊 **Datos Históricos**: Análisis de tendencias AIFA
  - 🎯 **Recomendaciones**: Rutas estratégicas sugeridas
  - 📋 **Resumen Ejecutivo**: KPIs y análisis FODA

### 🔧 Configuración Avanzada
- Capacidad de avión (100-400 asientos)
- Frecuencias semanales (1-14 vuelos)
- Factor de ocupación (50-95%)
- Precios promedio por ruta
- Selección de aerolíneas y destinos

## 📁 Estructura del Proyecto

```
aifa_rutas_demo/
├── data/                    # Datos CSV
│   ├── rutas_aifa.csv      # Rutas actuales
│   ├── pasajeros_mensuales.csv  # Histórico de pasajeros
│   ├── tarifas_promedio.csv     # Precios por destino
│   └── resumen_estrategico.csv  # Recomendaciones
├── scripts/                 # Lógica de negocio
│   └── simulador_ruta.py   # Simulador principal
├── dashboards/             # Interfaz web
│   └── app.py             # Dashboard Streamlit
├── requirements.txt        # Dependencias
└── README.md              # Documentación
```

## 🛠️ Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el dashboard
```bash
cd dashboards
streamlit run app.py
```

### 3. Acceder a la aplicación
Abrir: `http://localhost:8501`

## 📊 Uso del Simulador

### Configuración Básica
1. **Seleccionar destino**: CUN, GDL, TIJ, LAX, MIA, NYC, etc.
2. **Elegir aerolínea**: VivaAerobus, Aeromexico, Volaris, etc.
3. **Configurar parámetros**: Capacidad, frecuencia, ocupación, precio
4. **Ejecutar simulación**: Obtener resultados instantáneos

### Interpretación de Resultados
- **ROI > 15%**: ✅ Ruta viable
- **ROI 10-15%**: ⚠️ Analizar riesgos
- **ROI < 10%**: ❌ No recomendada

## 🎯 Casos de Uso

### Para Aerolíneas
- Evaluar nuevas rutas antes de invertir
- Optimizar frecuencias y precios
- Análisis de competencia y market share

### Para AIFA
- Atraer nuevas aerolíneas con datos sólidos
- Identificar oportunidades de crecimiento
- Estrategias de desarrollo comercial

### Para Inversionistas
- Análisis de rentabilidad del sector
- Due diligence para inversiones
- Proyecciones financieras basadas en datos

## 📈 Métricas Clave

### Cálculos Incluidos
- **Costos Operativos**: Combustible (35%), tripulación (25%), mantenimiento (20%), tasas (15%), otros (5%)
- **Factores Estacionales**: Variación mensual de demanda
- **Análisis de Sensibilidad**: Impacto de cambios en parámetros clave
- **Benchmarking**: Comparación con rutas similares

### KPIs del Dashboard
- ROI anual y mensual
- Ingresos y costos proyectados
- Score de viabilidad (0-100)
- Análisis comparativo por destino

## 🔮 Roadmap (Fases Siguientes)

### Fase 2: Inteligencia Avanzada
- 🤖 **Prophet Models**: Predicciones con ML
- 🌐 **APIs Externas**: Datos en tiempo real
- 📱 **Agent AI**: Consultas inteligentes

### Fase 3: Integración Empresarial
- 🔗 **APIs RESTful**: Integración con sistemas externos
- 👥 **Multi-usuario**: Roles y permisos
- 📊 **Reportes Avanzados**: Exportación automática

## 🤝 Contribuciones

Este es un proyecto demo diseñado para mostrar el potencial comercial de AIFA. Para contribuir:

1. Fork del repositorio
2. Crear feature branch
3. Commit de cambios
4. Pull request con descripción detallada

## 📄 Licencia

Proyecto demo - Uso educativo y comercial permitido.

---

**Desarrollado para demostrar el potencial de atracción de aerolíneas al Aeropuerto Internacional Felipe Ángeles (AIFA)**

✈️ *"Conectando México con el mundo a través de datos inteligentes"*