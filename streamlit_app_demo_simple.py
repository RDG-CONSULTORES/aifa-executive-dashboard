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
    page_title="AIFA - Centro de Operaciones",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Ocultar elementos de Streamlit
st.markdown("""
<style>
/* Ocultar botón Deploy */
.stDeployButton {
    display: none;
}

/* Ocultar menú hamburger */
#MainMenu {
    visibility: hidden;
}

/* Ocultar footer "Made with Streamlit" */
footer {
    visibility: hidden;
}

/* Ocultar header */
header {
    visibility: hidden;
}

/* Ocultar botón GitHub si aparece */
.viewerBadge_container__1QSob {
    display: none;
}

/* Ajustar margen superior */
.main .block-container {
    padding-top: 1rem;
}

/* Tema Aerospace Español */
.main-header {
    background: #003566;
    color: white;
    padding: 25px;
    margin: -55px -50px 30px;
    border-bottom: 3px solid #0496FF;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.metric-box {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s;
    margin-bottom: 16px;
}

.metric-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    color: #003566;
    margin: 10px 0;
}

.metric-label {
    color: #333333;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.7;
}

.metric-delta-positive {
    color: #06A77D;
    font-size: 14px;
    font-weight: 500;
}

.metric-delta-negative {
    color: #D00000;
    font-size: 14px;
    font-weight: 500;
}

.stButton > button {
    background-color: #0496FF;
    color: white;
    border: none;
    padding: 10px 24px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: all 0.3s;
}

.stButton > button:hover {
    background-color: #003566;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# Colores del tema Aerospace
COLORS = {
    "primary": "#003566",
    "secondary": "#006BA6", 
    "accent": "#0496FF",
    "success": "#06A77D",
    "warning": "#F1A208",
    "danger": "#D00000",
    "neutral": "#E5E5E5",
    "text": "#333333"
}

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

# Header principal
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-weight: 400;">CENTRO DE OPERACIONES AIFA</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Aeropuerto Internacional Felipe Ángeles</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 28px; font-weight: 300;">{datetime.now().strftime('%H:%M')}</div>
            <div style="font-size: 14px; opacity: 0.8;">Hora de Ciudad de México</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Configuración
st.sidebar.markdown("### ⚙️ CONFIGURACIÓN")

# Selección de destino
destinos_disponibles = ['CUN', 'GDL', 'TIJ', 'LAX', 'MIA', 'NYC', 'CDG', 'MAD', 'LHR']
destino = st.sidebar.selectbox(
    "DESTINO:",
    destinos_disponibles,
    index=0
)

# Selección de aerolínea
aerolineas = ['VivaAerobus', 'Aeromexico', 'Volaris', 'Interjet', 'Magnicharters']
aerolinea = st.sidebar.selectbox(
    "AEROLÍNEA:",
    aerolineas,
    index=0
)

# Frecuencia de vuelos
frecuencia_semanal = st.sidebar.slider(
    "VUELOS POR SEMANA:",
    min_value=1,
    max_value=14,
    value=7
)

# Tabs principales
tabs = st.tabs([
    "OPERACIONES", 
    "DATOS HISTÓRICOS", 
    "PLANEACIÓN ESTRATÉGICA", 
    "RESUMEN EJECUTIVO",
    "ANÁLISIS DE SLOTS", 
    "INFRAESTRUCTURA", 
    "MAPEO GEOGRÁFICO", 
    "KPIs EN TIEMPO REAL"
])

# TAB 1: OPERACIONES
with tabs[0]:
    st.header("OPERACIONES DE VUELO")
    
    # Botón para ejecutar simulación
    if st.sidebar.button("EJECUTAR SIMULACIÓN"):
        with st.spinner('PROCESANDO SIMULACIÓN...'):
            # Crear instancia del simulador
            simulador = SimuladorRutaAIFA()
            
            # Ejecutar simulación
            resultado = simulador.simular_ruta_completa(
                origen='NLU',
                destino=destino,
                aerolinea=aerolinea,
                vuelos_semanales=frecuencia_semanal
            )
        
        # Mostrar resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">ROI ANUAL</div>
                <div class="metric-value">{resultado['financieros']['roi_porcentaje']:.1f}%</div>
                <div class="metric-delta-{'positive' if resultado['financieros']['roi_porcentaje'] > 15 else 'negative'}">
                    {'▲' if resultado['financieros']['roi_porcentaje'] > 15 else '▼'} {resultado['financieros']['roi_porcentaje'] - 15:.1f}% vs objetivo
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">INGRESOS ANUALES</div>
                <div class="metric-value">${resultado['financieros']['ingresos_totales_mxn']/1000000:.1f}M</div>
                <div class="metric-delta-positive">MXN</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">COSTOS OPERATIVOS</div>
                <div class="metric-value">${resultado['financieros']['costos_totales_usd'] * 20/1000000:.1f}M</div>
                <div class="metric-delta-negative">MXN</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">GANANCIA NETA</div>
                <div class="metric-value">${resultado['financieros']['ganancia_neta_usd'] * 20/1000000:.1f}M</div>
                <div class="metric-delta-positive">MXN</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráfico de ROI por mes
        st.subheader("PROYECCIÓN MENSUAL DE ROI")
        
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Simular variación estacional
        roi_mensual = []
        factores_estacionales = [0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.15, 1.0, 0.9, 0.85, 1.3]
        
        for factor in factores_estacionales:
            roi_mes = resultado['financieros']['roi_porcentaje'] * factor
            roi_mensual.append(roi_mes)
        
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Scatter(
            x=meses,
            y=roi_mensual,
            mode='lines+markers',
            name='ROI Mensual',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=8)
        ))
        
        fig_roi.add_hline(y=15, line_dash="dash", line_color=COLORS['warning'], 
                         annotation_text="ROI Objetivo (15%)")
        
        fig_roi.update_layout(
            title="Proyección de ROI por Mes",
            xaxis_title="Mes",
            yaxis_title="ROI (%)",
            height=400,
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color=COLORS['text'])
        )
        
        st.plotly_chart(fig_roi, use_container_width=True)
    else:
        st.info("Configure los parámetros en el sidebar y presione EJECUTAR SIMULACIÓN")

# TAB 2: DATOS HISTÓRICOS  
with tabs[1]:
    st.header("ANÁLISIS DE DATOS HISTÓRICOS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("EVOLUCIÓN DE PASAJEROS")
        
        fig_pasajeros = px.line(
            pasajeros_df,
            x='mes',
            y='pasajeros',
            color='airline',
            title='Pasajeros Mensuales por Aerolínea',
            color_discrete_sequence=[COLORS['primary'], COLORS['accent'], COLORS['secondary']]
        )
        
        fig_pasajeros.update_layout(
            height=400,
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color=COLORS['text'])
        )
        
        st.plotly_chart(fig_pasajeros, use_container_width=True)
    
    with col2:
        st.subheader("TARIFAS PROMEDIO POR DESTINO")
        
        fig_tarifas = px.bar(
            tarifas_df,
            x='destination',
            y='tarifa_promedio_mxn',
            title='Precio Promedio por Destino',
            color_discrete_sequence=[COLORS['primary']]
        )
        
        fig_tarifas.update_layout(
            height=400,
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color=COLORS['text'])
        )
        
        st.plotly_chart(fig_tarifas, use_container_width=True)

# TAB 3: PLANEACIÓN ESTRATÉGICA
with tabs[2]:
    st.header("PLANEACIÓN ESTRATÉGICA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**FORTALEZAS**")
        st.write("- Ubicación estratégica en zona metropolitana")
        st.write("- Infraestructura moderna y capacidad de crecimiento")
        st.write("- Apoyo gubernamental y tarifas competitivas")
        st.write("- Menor saturación vs. otros aeropuertos")
        
        st.info("**OPORTUNIDADES**")
        st.write("- Crecimiento del mercado de aviación mexicano")
        st.write("- Demanda insatisfecha en rutas internacionales")
        st.write("- Potencial para aerolíneas de bajo costo")
        st.write("- Conectividad con destinos turísticos")
    
    with col2:
        st.warning("**DEBILIDADES**")
        st.write("- Reconocimiento de marca limitado")
        st.write("- Conectividad terrestre en desarrollo")
        st.write("- Competencia con aeropuertos establecidos")
        st.write("- Base de pasajeros en construcción")
        
        st.error("**AMENAZAS**")
        st.write("- Volatilidad económica y del combustible")
        st.write("- Regulaciones cambiantes en aviación")
        st.write("- Competencia agresiva de otros aeropuertos")
        st.write("- Eventos externos (pandemias, conflictos)")

# TAB 4: RESUMEN EJECUTIVO
with tabs[3]:
    st.header("RESUMEN EJECUTIVO")
    
    # KPIs principales
    st.subheader("MÉTRICAS CLAVE AIFA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">PASAJEROS TOTALES 2023</div>
            <div class="metric-value">678K</div>
            <div class="metric-delta-positive">▲ +35% vs 2022</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">RUTAS ACTIVAS</div>
            <div class="metric-value">{len(rutas_df)}</div>
            <div class="metric-delta-positive">▲ +2 nuevas rutas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">AEROLÍNEAS OPERANDO</div>
            <div class="metric-value">{rutas_df['airline'].nunique()}</div>
            <div class="metric-delta-positive">▲ +1 aerolínea</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">TARIFA PROMEDIO</div>
            <div class="metric-value">${tarifas_df['tarifa_promedio_mxn'].mean():,.0f}</div>
            <div class="metric-delta-positive">MXN</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 5: ANÁLISIS DE SLOTS
with tabs[4]:
    st.header("ANÁLISIS DE SLOTS AEROPORTUARIOS")
    
    # Obtener métricas en tiempo real
    metricas_slots = obtener_metricas_slots()
    visualizaciones = generar_visualizaciones_slots()
    
    # Métricas principales en tiempo real
    st.subheader("MÉTRICAS EN TIEMPO REAL")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">HORA ACTUAL</div>
            <div class="metric-value">{metricas_slots['tiempo_real']['hora']}</div>
            <div class="metric-delta-positive">{metricas_slots['tiempo_real']['slots_disponibles_ahora']} slots libres</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">OCUPACIÓN ACTUAL</div>
            <div class="metric-value">{metricas_slots['tiempo_real']['ocupacion_actual']:.1f}%</div>
            <div class="metric-delta-{'positive' if metricas_slots['tiempo_real']['ocupacion_actual'] < 80 else 'negative'}">
                {'Normal' if metricas_slots['tiempo_real']['ocupacion_actual'] < 80 else 'Alta'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">PRÓXIMO SLOT LIBRE</div>
            <div class="metric-value">{metricas_slots['tiempo_real']['proximo_slot_libre']}</div>
            <div class="metric-delta-positive">Disponible</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">INGRESOS POTENCIALES</div>
            <div class="metric-value">{metricas_slots['proyecciones']['ingresos_potenciales'].split(' ')[0]}</div>
            <div class="metric-delta-positive">MXN/mes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("MAPA DE CALOR SEMANAL")
        st.plotly_chart(visualizaciones['mapa_calor'], use_container_width=True)
    
    with col2:
        st.subheader("VISUALIZACIÓN 3D")
        st.plotly_chart(visualizaciones['vista_3d'], use_container_width=True)

# TAB 6: INFRAESTRUCTURA
with tabs[5]:
    st.header("INFRAESTRUCTURA AEROPORTUARIA")
    
    try:
        diagram = AIFAAirportDiagram()
        fig_diagram = diagram.crear_diagrama_completo()
        st.plotly_chart(fig_diagram, use_container_width=True)
        
        # Información adicional
        st.subheader("ESPECIFICACIONES TÉCNICAS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pistas", "2", help="Pista principal: 4,500m | Pista secundaria: 3,500m")
        
        with col2:
            st.metric("Gates", "48", help="Capacidad actual de puertas de embarque")
        
        with col3:
            st.metric("Capacidad/Hora", "55 operaciones", help="Capacidad máxima operativa por hora")
            
    except Exception as e:
        st.warning("Diagrama del aeropuerto no disponible temporalmente")

# TAB 7: MAPEO GEOGRÁFICO
with tabs[6]:
    st.header("MAPEO GEOGRÁFICO")
    
    try:
        geo_map = AIFAGeoMap()
        fig_map = geo_map.crear_mapa_completo(rutas_df)
        st.plotly_chart(fig_map, use_container_width=True)
        
    except Exception as e:
        st.warning("Mapa geográfico no disponible temporalmente")

# TAB 8: KPIs EN TIEMPO REAL
with tabs[7]:
    st.header("KPIs EN TIEMPO REAL")
    
    try:
        # Intentar conectar con APIs reales
        with st.spinner('OBTENIENDO DATOS EN TIEMPO REAL...'):
            kpi_calculator = AIFAKPICalculator()
            dashboard_data = kpi_calculator.generar_dashboard_completo()
            
            scorecard = dashboard_data['scorecard_general']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">SCORE GENERAL</div>
                    <div class="metric-value">{scorecard['score_general']}/100</div>
                    <div class="metric-delta-positive">{scorecard['clasificacion']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">ESTRATÉGICO</div>
                    <div class="metric-value">{scorecard['score_estrategico']}/100</div>
                    <div class="metric-delta-positive">Tendencia: {scorecard['tendencia']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">OPERACIONAL</div>
                    <div class="metric-value">{scorecard['score_operacional']}/100</div>
                    <div class="metric-delta-positive">Eficiencia gates: 48.6%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">ECONÓMICO</div>
                    <div class="metric-value">{scorecard['score_economico']}/100</div>
                    <div class="metric-delta-positive">Derrama: $44.4B MXN/año</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Mostrar gráficas adicionales si están disponibles
            if 'graficas' in dashboard_data:
                for titulo, grafica in dashboard_data['graficas'].items():
                    st.subheader(titulo.upper())
                    st.plotly_chart(grafica, use_container_width=True)
                    
    except Exception as e:
        st.warning("Conectando con fuentes de datos en tiempo real...")
        st.info("Los KPIs en tiempo real requieren conexión a APIs externas")

# Footer
st.markdown("---")
st.markdown("**AIFA - Aeropuerto Internacional Felipe Ángeles** | Centro de Operaciones y Análisis")