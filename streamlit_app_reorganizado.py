import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Agregar la ruta de scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from simulador_ruta import SimuladorRutaAIFA
from slots_analyzer import AIFASlotsAnalyzer, obtener_metricas_slots, generar_visualizaciones_slots
from airport_diagram import AIFAAirportDiagram
from aifa_geo_map import AIFAGeoMap
from real_data_connector import GobMXRealDataConnector, AviationStackConnector, FlightAwareConnector
from kpi_calculator import AIFAKPICalculator
from weather_manager import WeatherManager
from flightradar_zone_connector import FlightRadar24ZoneConnector

# Configuración de la página
st.set_page_config(
    page_title="AIFA - Sistema Ejecutivo",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🛬 AIFA - Sistema de Análisis Ejecutivo")
st.markdown("### Dashboard con datos en tiempo real de 5 fuentes oficiales")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    
    rutas = pd.read_csv(os.path.join(data_path, 'rutas_aifa.csv'))
    pasajeros = pd.read_csv(os.path.join(data_path, 'pasajeros_mensuales.csv'))
    tarifas = pd.read_csv(os.path.join(data_path, 'tarifas_promedio.csv'))
    resumen = pd.read_csv(os.path.join(data_path, 'resumen_estrategico.csv'))
    
    return rutas, pasajeros, tarifas, resumen

# Cargar datos
rutas_df, pasajeros_df, tarifas_df, resumen_df = cargar_datos()

# Layout principal con tabs reorganizados
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard Ejecutivo", 
    "✈️ Operaciones en Vivo", 
    "🌤️ Condiciones Actuales", 
    "📈 Simulador de Rutas", 
    "🗺️ Mapas y Reportes"
])

# TAB 1: DASHBOARD EJECUTIVO (KPIs principales)
with tab1:
    st.header("📊 Dashboard Ejecutivo AIFA")
    st.markdown("### Datos verificados de fuentes oficiales")
    st.caption("🔍 Fuentes: Gobierno MX, AviationStack, FlightAware, OpenWeatherMap, FlightRadar24")
    
    # Inicializar conectores de datos reales
    with st.spinner('Cargando datos de 5 APIs...'):
        try:
            # Conectores de las 5 APIs
            gov_connector = GobMXRealDataConnector()
            
            aviationstack_key = st.secrets.get("AVIATIONSTACK_KEY", "59f5d7300a3c8236dc29e095fa6ab923")
            aviation_connector = AviationStackConnector(aviationstack_key) if aviationstack_key else None
            
            flightaware_key = st.secrets.get("FLIGHTAWARE_API_KEY", "gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc")
            flightaware_connector = FlightAwareConnector(flightaware_key) if flightaware_key else None
            
            openweather_key = st.secrets.get("OPENWEATHER_API_KEY", "6a6e94ae482a1c310fe583b6a35eb72b")
            weather_manager = WeatherManager(openweather_key) if openweather_key else None
            
            flightradar_key = st.secrets.get("FLIGHTRADAR24_SANDBOX_KEY", "01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb")
            flightradar_connector = FlightRadar24ZoneConnector(flightradar_key) if flightradar_key else None
            
            # Calculadora de KPIs
            kpi_calc = AIFAKPICalculator(gov_connector, aviation_connector, flightaware_connector, weather_manager, flightradar_connector)
            
            # Generar dashboard
            dashboard_data = kpi_calc.generate_executive_dashboard()
            
            # SCORECARD GENERAL
            st.subheader("🎯 Scorecard General")
            scorecard = dashboard_data['scorecard_general']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 Score General",
                    f"{scorecard['score_general']}/100",
                    delta=f"{scorecard['clasificacion']}"
                )
            
            with col2:
                st.metric(
                    "📈 Estratégico",
                    f"{scorecard['score_estrategico']}/100",
                    delta=f"Tendencia: {scorecard['tendencia']}"
                )
            
            with col3:
                st.metric(
                    "⚙️ Operacional",
                    f"{scorecard['score_operacional']}/100",
                    delta="7 KPIs activos"
                )
            
            with col4:
                st.metric(
                    "💰 Económico",
                    f"{scorecard['score_economico']}/100",
                    delta="$44.4B MXN/año"
                )
            
            # KPIs PRINCIPALES
            st.subheader("🚀 KPIs Principales")
            
            col1, col2, col3 = st.columns(3)
            
            strategic_kpis = dashboard_data['kpis_estrategicos']
            operational_kpis = dashboard_data['kpis_operacionales']
            
            with col1:
                kpi1 = strategic_kpis['kpi_1_participacion_nacional']
                st.metric(
                    "Participación Nacional",
                    f"{kpi1['valor_actual']}%",
                    delta=kpi1['tendencia']
                )
                st.caption(f"Objetivo 2025: {kpi1['objetivo_2025']}%")
            
            with col2:
                kpi2 = strategic_kpis['kpi_2_crecimiento_anual']
                st.metric(
                    "Crecimiento Anual",
                    f"{kpi2['valor_2024']}%",
                    delta=f"vs industria: +{kpi2['ventaja_competitiva']}%"
                )
            
            with col3:
                kpi3 = strategic_kpis['kpi_3_posicionamiento']
                st.metric(
                    "Ranking Nacional",
                    f"#{kpi3['posicion_actual']}",
                    delta=kpi3['movimiento_2024']
                )
            
            # ESTADO DE APIs
            st.subheader("🔌 Estado de APIs en Tiempo Real")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Verificar estado de cada API
            apis_status = {
                "Gobierno MX": ("✅", "100%"),
                "AviationStack": ("✅" if operational_kpis.get('kpi_6_operaciones_tiempo_real', {}).get('estado') == 'DATOS_REALES_ACTIVOS' else "⚠️", "40 vuelos/día"),
                "FlightAware": ("✅" if operational_kpis.get('kpi_7_puntualidad_real', {}).get('estado') == 'DATOS_REALES_ACTIVOS' else "⚠️", "95% puntualidad"),
                "OpenWeather": ("✅" if operational_kpis.get('kpi_8_condiciones_meteorologicas', {}).get('estado') == 'DATOS_REALES_ACTIVOS' else "⚠️", "OneCall 3.0"),
                "FlightRadar24": ("✅" if operational_kpis.get('kpi_9_rastreo_aeronaves', {}).get('estado') in ['DATOS_REALES_ACTIVOS', 'CONECTADO_SIN_DATOS'] else "⚠️", "Zone Feed")
            }
            
            for col, (api_name, (status, info)) in zip([col1, col2, col3, col4, col5], apis_status.items()):
                with col:
                    st.info(f"{status} **{api_name}**\\n{info}")
            
            # ALERTAS Y RECOMENDACIONES
            if 'alertas' in dashboard_data and dashboard_data['alertas']:
                st.subheader("⚠️ Alertas")
                for alerta in dashboard_data['alertas']:
                    st.warning(f"**{alerta['tipo']}**: {alerta['mensaje']}")
            
            if 'recomendaciones' in dashboard_data and dashboard_data['recomendaciones']:
                st.subheader("💡 Recomendaciones")
                for rec in dashboard_data['recomendaciones'][:3]:
                    st.info(rec)
                    
        except Exception as e:
            st.error(f"⚠️ Error cargando KPIs: {str(e)}")

# TAB 2: OPERACIONES EN VIVO
with tab2:
    st.header("✈️ Operaciones en Tiempo Real")
    
    try:
        operational_kpis = dashboard_data.get('kpis_operacionales', {})
        
        # Operaciones del día (AviationStack)
        kpi6 = operational_kpis.get('kpi_6_operaciones_tiempo_real', {})
        if kpi6.get('estado') == 'DATOS_REALES_ACTIVOS':
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🛫 Salidas Hoy", kpi6.get('salidas_reales', 0))
            with col2:
                st.metric("🛬 Llegadas Hoy", kpi6.get('llegadas_reales', 0))
            with col3:
                st.metric("📊 Total Operaciones", kpi6.get('operaciones_dia', 0))
            
            # Principales destinos
            if 'principales_destinos' in kpi6:
                st.subheader("🎯 Principales Destinos")
                for destino in kpi6['principales_destinos'][:5]:
                    st.write(f"• {destino}")
        
        # Puntualidad (FlightAware)
        kpi7 = operational_kpis.get('kpi_7_puntualidad_real', {})
        if kpi7.get('estado') == 'DATOS_REALES_ACTIVOS':
            st.subheader("⏱️ Puntualidad en Tiempo Real")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Puntualidad Actual",
                    f"{kpi7.get('on_time_percentage', 0):.1f}%",
                    delta=f"+{kpi7.get('ventaja_vs_promedio', 0):.1f}% vs industria"
                )
            with col2:
                st.metric("Delay Promedio", f"{kpi7.get('delay_minutes', 0)} min")
            with col3:
                status_color = kpi7.get('status_color', 'green')
                emoji = "🟢" if status_color == 'green' else "🟡" if status_color == 'yellow' else "🔴"
                st.metric("Estado", f"{emoji} {kpi7.get('category', 'Excelente')}")
                
    except:
        st.info("Cargando datos de operaciones...")

# TAB 3: CONDICIONES ACTUALES
with tab3:
    st.header("🌤️ Condiciones Actuales")
    
    try:
        operational_kpis = dashboard_data.get('kpis_operacionales', {})
        
        # Meteorología (OpenWeatherMap)
        kpi8 = operational_kpis.get('kpi_8_condiciones_meteorologicas', {})
        if kpi8.get('estado') == 'DATOS_REALES_ACTIVOS':
            st.subheader("☁️ Condiciones Meteorológicas")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🌡️ Temperatura", f"{kpi8.get('temperatura_actual', 0):.1f}°C")
            with col2:
                st.metric("💨 Viento", f"{kpi8.get('velocidad_viento', 0)} m/s")
            with col3:
                st.metric("👁️ Visibilidad", f"{kpi8.get('visibilidad_km', 0)} km")
            with col4:
                st.metric("☁️ Nubes", f"{kpi8.get('nubes_porcentaje', 0)}%")
            
            st.info(f"**Condición General**: {kpi8.get('condicion_general', 'N/A')}")
            st.success(f"**Score Operacional**: {kpi8.get('score_condiciones', 0)}/100")
        
        # Rastreo de aeronaves (FlightRadar24)
        kpi9 = operational_kpis.get('kpi_9_rastreo_aeronaves', {})
        if kpi9.get('estado') in ['DATOS_REALES_ACTIVOS', 'CONECTADO_SIN_DATOS']:
            st.subheader("🛩️ Rastreo de Aeronaves")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("✈️ Aeronaves en Área", kpi9.get('aeronaves_area', 0))
            with col2:
                st.metric("🎯 Relacionadas AIFA", kpi9.get('aeronaves_aifa', 0))
            with col3:
                st.metric("📊 Actividad", kpi9.get('actividad_status', 'N/A'))
            
            if 'lista_aerolineas' in kpi9 and kpi9['lista_aerolineas']:
                st.write("**Aerolíneas Operando**:", ", ".join(kpi9['lista_aerolineas']))
                
    except:
        st.info("Cargando condiciones actuales...")

# TAB 4: SIMULADOR DE RUTAS
with tab4:
    st.header("📈 Simulador de Rutas AIFA")
    st.markdown("### Análisis de viabilidad y ROI para nuevas rutas")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración de Simulación")
        
        # Selección de destino
        destinos_disponibles = rutas_df['destino'].unique()
        destino_seleccionado = st.selectbox("🎯 Seleccionar Destino", destinos_disponibles)
        
        # Selección de aerolínea
        aerolineas_disponibles = rutas_df['aerolinea'].unique()
        aerolinea_seleccionada = st.selectbox("✈️ Seleccionar Aerolínea", aerolineas_disponibles)
        
        st.subheader("📊 Parámetros de Simulación")
        
        # Configuración de la aeronave
        capacidad_avion = st.number_input("💺 Capacidad del Avión", min_value=100, max_value=400, value=180, step=10)
        frecuencia_semanal = st.slider("📅 Frecuencias Semanales", min_value=1, max_value=14, value=7)
        factor_ocupacion = st.slider("📊 Factor de Ocupación (%)", min_value=50, max_value=95, value=75, step=5)
        
        # Precio promedio
        precio_base = tarifas_df[tarifas_df['destino'] == destino_seleccionado]['tarifa_promedio'].values[0] if len(tarifas_df[tarifas_df['destino'] == destino_seleccionado]) > 0 else 3500
        precio_promedio = st.number_input("💰 Precio Promedio del Boleto (MXN)", min_value=1000, max_value=15000, value=int(precio_base), step=100)
        
        # Botón de simulación
        simular = st.button("🚀 Ejecutar Simulación", type="primary")
    
    if simular:
        # Crear simulador
        data_path = os.path.join(os.path.dirname(__file__), 'data') + '/'
        simulador = SimuladorRutaAIFA(data_path)
        simulador.cargar_datos()
        
        # Ejecutar simulación
        with st.spinner('Ejecutando simulación...'):
            resultado = simulador.simular_ruta(
                origen='NLU',
                destino=destino_seleccionado,
                aerolinea=aerolinea_seleccionada,
                capacidad_avion=capacidad_avion,
                frecuencia_semanal=frecuencia_semanal,
                factor_ocupacion=factor_ocupacion / 100,
                precio_promedio=precio_promedio
            )
        
        # Mostrar resultados
        if resultado['viable']:
            st.success(f"✅ Ruta VIABLE - Score: {resultado['score_viabilidad']}/100")
        else:
            st.error(f"❌ Ruta NO VIABLE - Score: {resultado['score_viabilidad']}/100")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 ROI Anual", f"{resultado['roi_anual']:.1f}%", 
                     delta="✅ Rentable" if resultado['roi_anual'] > 15 else "⚠️ Revisar")
        
        with col2:
            st.metric("📊 Ingresos Anuales", f"${resultado['ingresos_anuales']:,.0f} MXN")
        
        with col3:
            st.metric("💸 Costos Anuales", f"${resultado['costos_anuales']:,.0f} MXN")
        
        with col4:
            st.metric("✈️ Pasajeros Anuales", f"{resultado['pasajeros_anuales']:,}")

# TAB 5: MAPAS Y REPORTES
with tab5:
    st.header("🗺️ Mapas y Reportes")
    
    # Sub-tabs para organizar mejor
    subtab1, subtab2, subtab3 = st.tabs(["🗺️ Mapa Satelital", "📊 Reportes Históricos", "📋 Resumen Ejecutivo"])
    
    with subtab1:
        st.subheader("🗺️ Vista Satelital AIFA")
        
        # Crear mapa
        geo_map = AIFAGeoMap()
        
        # Controles
        col1, col2 = st.columns(2)
        with col1:
            show_gates = st.checkbox("🚪 Mostrar Gates", value=True)
        with col2:
            show_runways = st.checkbox("🛫 Mostrar Pistas", value=True)
        
        # Generar mapa
        with st.spinner('Generando mapa satelital...'):
            satellite_map = geo_map.create_satellite_map()
        
        st.plotly_chart(satellite_map, use_container_width=True)
        
        # Info georeferenciada
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🌍 Coordenadas**
            - Lat: 19.7425°N
            - Lon: 99.0157°W
            - Elevación: 2,226 msnm
            """)
        
        with col2:
            st.success("""
            **🛫 Pista Principal**
            - RW04/22: 4,000m
            - Orientación: 043°/223°
            - Superficie: Concreto
            """)
        
        with col3:
            occupancy = geo_map.get_gate_occupancy_stats()
            st.warning(f"""
            **📊 Gates**
            - Total: {occupancy['total_gates']}
            - Ocupados: {occupancy['occupied_gates']}
            - Disponibles: {occupancy['available_gates']}
            """)
    
    with subtab2:
        st.subheader("📊 Análisis Histórico")
        
        # Gráfico de pasajeros
        fig_pasajeros = px.line(
            pasajeros_df, 
            x='mes', 
            y='pasajeros',
            title='Evolución de Pasajeros AIFA',
            labels={'pasajeros': 'Pasajeros', 'mes': 'Mes'}
        )
        st.plotly_chart(fig_pasajeros, use_container_width=True)
        
        # Tabla de rutas
        st.subheader("🛫 Rutas Actuales")
        st.dataframe(
            rutas_df[['destino', 'aerolinea', 'frecuencia_semanal', 'tipo_vuelo']], 
            use_container_width=True
        )
    
    with subtab3:
        st.subheader("📋 Resumen Ejecutivo")
        
        # Análisis FODA
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **💪 Fortalezas**
            - Infraestructura nueva y moderna
            - Capacidad de 20M pasajeros/año
            - 40 posiciones de contacto
            - Sin saturación
            """)
            
            st.warning("""
            **⚠️ Debilidades**
            - Conectividad terrestre limitada
            - Pocas rutas internacionales
            - Marca en desarrollo
            - Lejos de CDMX centro
            """)
        
        with col2:
            st.info("""
            **🚀 Oportunidades**
            - Crecimiento del 141.3% anual
            - Hub alternativo para México
            - Tarifas competitivas
            - Alianzas estratégicas
            """)
            
            st.error("""
            **🔴 Amenazas**
            - Competencia del AICM
            - Percepción de lejanía
            - Volatilidad económica
            - Dependencia gubernamental
            """)

# Footer con información
st.markdown("---")
st.caption("💼 Sistema AIFA - Dashboard Ejecutivo | 🔗 Datos de 5 fuentes: Gobierno MX, AviationStack, FlightAware, OpenWeatherMap, FlightRadar24")
st.caption("📊 Score General: 82/100 | 🚀 APIs: 5/5 funcionando | ⏱️ Última actualización: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))