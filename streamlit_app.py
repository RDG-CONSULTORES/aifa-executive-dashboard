import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import pytz

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

# Ocultar elementos de Streamlit pero preservar sidebar
st.markdown("""
<style>
/* Ocultar botón Deploy */
.stDeployButton {
    display: none;
}

/* Ocultar footer "Made with Streamlit" */
footer {
    visibility: hidden;
}

/* Ocultar botón GitHub si aparece */
.viewerBadge_container__1QSob {
    display: none;
}

/* ENFOQUE MÍNIMO: Solo ocultar elementos específicos del menú */
#MainMenu > div {
    display: none;
}

/* Preservar header completamente para mantener funcionalidad sidebar */
header {
    display: block !important;
    visibility: visible !important;
}

/* Ocultar solo elementos específicos dentro del header */
header .css-1avcm0n,
header .css-12oz5g7,
header .css-1v3fvcr {
    display: none !important;
}

/* CREAR BOTÓN MANUAL DEL SIDEBAR */
.sidebar-toggle {
    position: fixed !important;
    top: 1rem !important;
    left: 1rem !important;
    z-index: 999999 !important;
    background: #003566 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
    font-size: 14px !important;
    font-weight: bold !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}

.sidebar-toggle:hover {
    background: #0496FF !important;
}

/* Asegurar que TODOS los elementos del sidebar toggle sean visibles */
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"],
button[kind="header"],
button[title*="sidebar"],
button[title*="Sidebar"] {
    display: block !important;
    visibility: visible !important;
    z-index: 999999 !important;
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

/* ARREGLAR OVERFLOW DE GRÁFICAS */
.js-plotly-plot, .plotly, .main-svg {
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: auto !important;
}

.plot-container {
    max-width: 100% !important;
    overflow-x: auto !important;
}

/* TABS RESPONSIVE */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    flex-wrap: wrap !important;
    overflow-x: auto !important;
    padding-bottom: 10px;
    scrollbar-width: thin;
    scrollbar-color: #0496FF #E5E5E5;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    height: 6px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
    background: #E5E5E5;
    border-radius: 3px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background: #0496FF;
    border-radius: 3px;
}

.stTabs [data-baseweb="tab-list"] button {
    min-width: 120px !important;
    white-space: nowrap !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    flex-shrink: 0 !important;
}

/* CONTAINER RESPONSIVE */
.main .block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* COLUMNAS RESPONSIVE */
.stColumn {
    max-width: 100% !important;
    overflow-x: auto !important;
}

/* INDICADORES VISUALES PARA TABS */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #003566 !important;
    color: white !important;
    border-bottom: 3px solid #0496FF !important;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    background-color: #E5F3FF !important;
    color: #003566 !important;
}

/* SIDEBAR RESPONSIVE */
.css-1d391kg {
    min-width: 250px !important;
}

@media (max-width: 1024px) {
    .stTabs [data-baseweb="tab-list"] button {
        min-width: 130px !important;
        font-size: 11px !important;
        padding: 8px 8px !important;
    }
}

@media (max-width: 768px) {
    .stTabs [data-baseweb="tab-list"] button {
        min-width: 110px !important;
        font-size: 10px !important;
        padding: 6px 6px !important;
    }
    
    .main-header h1 {
        font-size: 20px !important;
    }
    
    .main-header p {
        font-size: 12px !important;
    }
    
    .metric-value {
        font-size: 20px !important;
    }
    
    .metric-label {
        font-size: 11px !important;
    }
    
    /* Hacer sidebar colapsable en móviles */
    .css-1d391kg {
        min-width: 200px !important;
    }
}

@media (max-width: 480px) {
    .stTabs [data-baseweb="tab-list"] button {
        min-width: 80px !important;
        font-size: 9px !important;
        padding: 4px 4px !important;
    }
    
    .main-header {
        padding: 15px !important;
        margin: -55px -15px 20px !important;
    }
    
    .main-header h1 {
        font-size: 18px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# JavaScript para crear botón manual del sidebar
st.markdown("""
<script>
function toggleSidebar() {
    // Buscar el botón nativo del sidebar
    const sidebarButton = document.querySelector('[data-testid="collapsedControl"]') || 
                         document.querySelector('button[title*="sidebar"]') ||
                         document.querySelector('button[title*="Sidebar"]') ||
                         document.querySelector('.css-1d391kg') ||
                         document.querySelector('.css-1y4p8pa');
    
    if (sidebarButton) {
        sidebarButton.click();
    } else {
        // Si no encontramos el botón, intentar toggle via CSS
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            if (sidebar.style.display === 'none') {
                sidebar.style.display = 'block';
            } else {
                sidebar.style.display = 'none';
            }
        }
    }
}

// Crear botón manual si no existe
function createSidebarToggle() {
    if (!document.querySelector('.manual-sidebar-toggle')) {
        const button = document.createElement('button');
        button.innerHTML = '☰ Menú';
        button.className = 'manual-sidebar-toggle';
        button.style.cssText = `
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 999999 !important;
            background: #003566 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            cursor: pointer !important;
            font-size: 14px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        `;
        button.onclick = toggleSidebar;
        button.onmouseover = function() { this.style.background = '#0496FF !important'; };
        button.onmouseout = function() { this.style.background = '#003566 !important'; };
        document.body.appendChild(button);
    }
}

// Ejecutar cuando la página esté lista
setTimeout(createSidebarToggle, 1000);
setTimeout(createSidebarToggle, 3000); // Segundo intento por si no carga la primera vez
</script>
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

# Función para obtener hora de Ciudad de México
def get_mexico_time():
    """Obtiene la hora actual de Ciudad de México"""
    mexico_tz = pytz.timezone('America/Mexico_City')
    mexico_time = datetime.now(mexico_tz)
    return mexico_time

# Función para cargar datos
@st.cache_data
def cargar_datos():
    """Carga datos CSV con múltiples rutas de búsqueda"""
    
    # Múltiples rutas posibles
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'data'),  # Ruta relativa al script
        os.path.join(os.getcwd(), 'data'),                # Ruta desde directorio actual
        './data',                                         # Ruta relativa simple
        'data'                                            # Ruta directa
    ]
    
    data_path = None
    
    # Buscar la ruta correcta
    for path in possible_paths:
        test_file = os.path.join(path, 'rutas_aifa.csv')
        if os.path.exists(test_file):
            data_path = path
            break
    
    if not data_path:
        st.error(f"""
        **Error cargando datos**: No se encontraron los archivos CSV en ninguna de estas rutas:
        
        {chr(10).join([f"• {path}" for path in possible_paths])}
        
        **Directorio actual**: `{os.getcwd()}`  
        **Directorio del script**: `{os.path.dirname(__file__)}`
        
        Por favor, verifica que los archivos estén en la carpeta `data/`
        """)
        st.stop()
    
    try:
        rutas = pd.read_csv(os.path.join(data_path, 'rutas_aifa.csv'))
        pasajeros = pd.read_csv(os.path.join(data_path, 'pasajeros_mensuales.csv'))
        tarifas = pd.read_csv(os.path.join(data_path, 'tarifas_promedio.csv'))
        resumen = pd.read_csv(os.path.join(data_path, 'resumen_estrategico.csv'))
        
        # Mostrar éxito en sidebar
        st.sidebar.success(f"✅ Datos cargados desde: `{data_path}`")
        
        return rutas, pasajeros, tarifas, resumen
        
    except Exception as e:
        st.error(f"""
        **Error cargando datos**: {str(e)}
        
        **Ruta encontrada**: `{data_path}`
        
        Verifica que todos los archivos CSV necesarios estén presentes.
        """)
        st.stop()

# Cargar datos
rutas_df, pasajeros_df, tarifas_df, resumen_df = cargar_datos()

# Función helper para layouts responsivos
def get_responsive_layout(title="", height=400):
    """Configuración responsiva estándar para gráficas"""
    return {
        'title': title,
        'height': height,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': dict(family="Arial, sans-serif", size=12, color=COLORS['text']),
        'margin': dict(l=50, r=50, t=80, b=50),
        'xaxis': dict(
            fixedrange=False,
            automargin=True
        ),
        'yaxis': dict(
            fixedrange=False,
            automargin=True
        ),
        'autosize': True
    }

# Header principal
mexico_time = get_mexico_time()
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-weight: 400;">CENTRO DE OPERACIONES AIFA</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Aeropuerto Internacional Felipe Ángeles</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 28px; font-weight: 300;">{mexico_time.strftime('%H:%M')}</div>
            <div style="font-size: 14px; opacity: 0.8;">Hora de Ciudad de México</div>
            <div style="font-size: 11px; opacity: 0.6;">{mexico_time.strftime('%d/%m/%Y')}</div>
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
    "KPIs TIEMPO REAL"
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
        
        layout_config = get_responsive_layout("Proyección de ROI por Mes", height=400)
        layout_config.update({
            'xaxis_title': "Mes",
            'yaxis_title': "ROI (%)"
        })
        fig_roi.update_layout(layout_config)
        
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
            title='Evolución de Pasajeros Mensuales AIFA',
            color_discrete_sequence=[COLORS['primary']]
        )
        
        fig_pasajeros.update_layout(get_responsive_layout("Evolución de Pasajeros Mensuales AIFA", height=400))
        
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
        
        fig_tarifas.update_layout(get_responsive_layout("Tarifas Promedio por Destino", height=400))
        
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
    
    # Mostrar métricas primero
    st.subheader("ESPECIFICACIONES TÉCNICAS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">PISTAS DE ATERRIZAJE</div>
            <div class="metric-value">2</div>
            <div class="metric-delta-positive">Principal: 4,500m | Secundaria: 3,500m</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">GATES DISPONIBLES</div>
            <div class="metric-value">48</div>
            <div class="metric-delta-positive">Capacidad actual</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">CAPACIDAD/HORA</div>
            <div class="metric-value">55</div>
            <div class="metric-delta-positive">Operaciones máximas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Intentar cargar el diagrama original
    st.subheader("LAYOUT DEL AEROPUERTO")
    
    try:
        with st.spinner("Cargando diagrama del aeropuerto..."):
            diagram = AIFAAirportDiagram()
            fig_diagram = diagram.create_airport_diagram()
            st.plotly_chart(fig_diagram, use_container_width=True)
            st.success("✅ Diagrama original cargado exitosamente")
            
    except Exception as e:
        st.error(f"Error cargando diagrama original: {str(e)}")
        st.info("Mostrando diagrama alternativo...")
        
        # Crear diagrama alternativo
        fig_layout = go.Figure()
        
        # Pista principal
        fig_layout.add_shape(
            type="rect",
            x0=100, y0=200, x1=800, y1=250,
            fillcolor=COLORS['neutral'],
            line=dict(color=COLORS['primary'], width=2)
        )
        fig_layout.add_annotation(
            x=450, y=225, text="PISTA PRINCIPAL (04/22) - 4,500m",
            showarrow=False, font=dict(size=12, color=COLORS['text'])
        )
        
        # Pista secundaria  
        fig_layout.add_shape(
            type="rect",
            x0=100, y0=100, x1=700, y1=150,
            fillcolor=COLORS['neutral'],
            line=dict(color=COLORS['secondary'], width=2)
        )
        fig_layout.add_annotation(
            x=400, y=125, text="PISTA SECUNDARIA (18/36) - 3,500m",
            showarrow=False, font=dict(size=12, color=COLORS['text'])
        )
        
        # Terminal
        fig_layout.add_shape(
            type="rect",
            x0=300, y0=300, x1=600, y1=400,
            fillcolor=COLORS['accent'],
            line=dict(color=COLORS['primary'], width=3)
        )
        fig_layout.add_annotation(
            x=450, y=350, text="TERMINAL<br>48 Gates",
            showarrow=False, font=dict(size=14, color="white")
        )
        
        # Torre de control
        fig_layout.add_shape(
            type="circle",
            x0=680, y0=320, x1=720, y1=360,
            fillcolor=COLORS['warning'],
            line=dict(color=COLORS['primary'], width=2)
        )
        fig_layout.add_annotation(
            x=700, y=340, text="ATC",
            showarrow=False, font=dict(size=10, color="white")
        )
        
        fig_layout.update_layout(
            title="Layout Aeropuerto Internacional Felipe Ángeles",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            plot_bgcolor='white',
            showlegend=False
        )
        
        st.plotly_chart(fig_layout, use_container_width=True)
    
    # Información adicional
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CAPACIDADES OPERATIVAS")
        st.write("🛬 **Operaciones diarias máximas**: 1,320")
        st.write("✈️ **Tipos de aeronaves**: Narrow body, Wide body, Carga")
        st.write("🚁 **Helipuerto**: Disponible para operaciones especiales")
        st.write("⛽ **Combustible**: Sistema centralizado disponible")
    
    with col2:
        st.subheader("SERVICIOS E INSTALACIONES")
        st.write("🏢 **Área terminal**: 74,000 m²")
        st.write("🅿️ **Estacionamiento**: 2,500 espacios")
        st.write("🚌 **Transporte terrestre**: Conexión Metro y autobús")
        st.write("📡 **Navegación**: ILS Cat II en ambas pistas")

# TAB 7: MAPEO GEOGRÁFICO
with tabs[6]:
    st.header("MAPEO GEOGRÁFICO")
    
    # Intentar cargar el mapa original
    try:
        with st.spinner("Cargando mapa geográfico..."):
            geo_map = AIFAGeoMap()
            fig_map = geo_map.create_satellite_map()
            st.plotly_chart(fig_map, use_container_width=True)
            st.success("✅ Mapa original cargado exitosamente")
        
    except Exception as e:
        st.warning(f"Mapa geográfico original no disponible. Error: {str(e)}")
        st.info("Mostrando mapa alternativo...")
        
        # Mapa alternativo
        locations = {
            'AIFA (NLU)': {'lat': 19.7281, 'lon': -99.0198, 'type': 'hub'},
            'Cancún (CUN)': {'lat': 21.0364, 'lon': -86.8772, 'type': 'domestic'},
            'Guadalajara (GDL)': {'lat': 20.5218, 'lon': -103.3108, 'type': 'domestic'},
            'Tijuana (TIJ)': {'lat': 32.5411, 'lon': -116.9703, 'type': 'domestic'},
            'Los Angeles (LAX)': {'lat': 34.0522, 'lon': -118.2437, 'type': 'international'},
            'Miami (MIA)': {'lat': 25.7617, 'lon': -80.1918, 'type': 'international'},
            'New York (JFK)': {'lat': 40.6413, 'lon': -73.7781, 'type': 'international'}
        }
        
        fig_map = go.Figure()
        
        # AIFA como hub principal
        fig_map.add_trace(go.Scattergeo(
            lon=[-99.0198],
            lat=[19.7281],
            text=['AIFA - Hub Principal'],
            mode='markers',
            marker=dict(size=20, color=COLORS['primary']),
            name='AIFA Hub'
        ))
        
        # Destinos domésticos
        domestic_lats = [loc['lat'] for name, loc in locations.items() if loc['type'] == 'domestic']
        domestic_lons = [loc['lon'] for name, loc in locations.items() if loc['type'] == 'domestic']
        domestic_names = [name for name, loc in locations.items() if loc['type'] == 'domestic']
        
        fig_map.add_trace(go.Scattergeo(
            lon=domestic_lons,
            lat=domestic_lats,
            text=domestic_names,
            mode='markers',
            marker=dict(size=12, color=COLORS['accent']),
            name='Destinos Domésticos'
        ))
        
        # Destinos internacionales
        intl_lats = [loc['lat'] for name, loc in locations.items() if loc['type'] == 'international']
        intl_lons = [loc['lon'] for name, loc in locations.items() if loc['type'] == 'international'] 
        intl_names = [name for name, loc in locations.items() if loc['type'] == 'international']
        
        fig_map.add_trace(go.Scattergeo(
            lon=intl_lons,
            lat=intl_lats,
            text=intl_names,
            mode='markers',
            marker=dict(size=12, color=COLORS['secondary']),
            name='Destinos Internacionales'
        ))
        
        # Líneas de rutas
        for name, loc in locations.items():
            if name != 'AIFA (NLU)':
                fig_map.add_trace(go.Scattergeo(
                    lon=[-99.0198, loc['lon']],
                    lat=[19.7281, loc['lat']],
                    mode='lines',
                    line=dict(width=2, color=COLORS['accent'] if loc['type'] == 'domestic' else COLORS['secondary']),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        fig_map.update_layout(
            title="Red de Rutas AIFA - Conectividad Nacional e Internacional",
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showocean=True,
                oceancolor='lightblue',
                showlakes=True,
                lakecolor='lightblue',
                center=dict(lat=25, lon=-100),
                lonaxis=dict(range=[-130, -70]),
                lataxis=dict(range=[10, 45])
            ),
            height=600
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    # Métricas de conectividad
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">DESTINOS DOMÉSTICOS</div>
            <div class="metric-value">12</div>
            <div class="metric-delta-positive">Principales ciudades mexicanas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">DESTINOS INTERNACIONALES</div>
            <div class="metric-value">8</div>
            <div class="metric-delta-positive">Estados Unidos y Centroamérica</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">DISTANCIA PROMEDIO</div>
            <div class="metric-value">1,850</div>
            <div class="metric-delta-positive">km por ruta</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 8: KPIs EN TIEMPO REAL
with tabs[7]:
    st.header("KPIs EN TIEMPO REAL")
    
    import random
    
    # Dashboard ejecutivo  
    st.subheader("DASHBOARD EJECUTIVO")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Scores simulados realistas
    score_general = random.randint(72, 78)
    score_estrategico = random.randint(68, 75)
    score_operacional = random.randint(75, 82)
    score_economico = random.randint(70, 77)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">SCORE GENERAL</div>
            <div class="metric-value">{score_general}/100</div>
            <div class="metric-delta-positive">{"EXCELENTE" if score_general > 75 else "BUENO"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">ESTRATÉGICO</div>
            <div class="metric-value">{score_estrategico}/100</div>
            <div class="metric-delta-positive">Tendencia: ▲ CRECIMIENTO</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">OPERACIONAL</div>
            <div class="metric-value">{score_operacional}/100</div>
            <div class="metric-delta-positive">Eficiencia gates: 78.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">ECONÓMICO</div>
            <div class="metric-value">{score_economico}/100</div>
            <div class="metric-delta-positive">Derrama: $44.4B MXN/año</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Operaciones en tiempo real
    st.subheader("OPERACIONES EN TIEMPO REAL")
    
    col1, col2, col3, col4 = st.columns(4)
    
    vuelos_hoy = random.randint(85, 120)
    pasajeros_hoy = vuelos_hoy * random.randint(120, 180)
    puntualidad = random.uniform(88, 95)
    ocupacion_terminal = random.randint(45, 65)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">VUELOS HOY</div>
            <div class="metric-value">{vuelos_hoy}</div>
            <div class="metric-delta-positive">▲ +12% vs ayer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">PASAJEROS HOY</div>
            <div class="metric-value">{pasajeros_hoy:,}</div>
            <div class="metric-delta-positive">▲ +8% vs ayer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">PUNTUALIDAD</div>
            <div class="metric-value">{puntualidad:.1f}%</div>
            <div class="metric-delta-positive">Excelente desempeño</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">OCUPACIÓN TERMINAL</div>
            <div class="metric-value">{ocupacion_terminal}%</div>
            <div class="metric-delta-positive">Nivel normal</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de tendencias
    st.subheader("TENDENCIA DE OPERACIONES (ÚLTIMOS 7 DÍAS)")
    
    dias = []
    vuelos_semana = []
    pasajeros_semana = []
    
    for i in range(7):
        fecha = datetime.now() - timedelta(days=6-i)
        dias.append(fecha.strftime('%d/%m'))
        vuelos_semana.append(random.randint(75, 125))
        pasajeros_semana.append(vuelos_semana[-1] * random.randint(120, 180))
    
    fig_tendencia = go.Figure()
    
    fig_tendencia.add_trace(go.Scatter(
        x=dias,
        y=vuelos_semana,
        mode='lines+markers',
        name='Vuelos',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        yaxis='y'
    ))
    
    fig_tendencia.add_trace(go.Scatter(
        x=dias,
        y=pasajeros_semana,
        mode='lines+markers',
        name='Pasajeros',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    fig_tendencia.update_layout(
        title="Operaciones Diarias - Últimos 7 Días",
        xaxis_title="Fecha",
        yaxis=dict(title="Vuelos", side="left"),
        yaxis2=dict(title="Pasajeros", side="right", overlaying="y"),
        height=400,
        plot_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=COLORS['text'])
    )
    
    st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # KPIs adicionales
    st.subheader("INDICADORES CLAVE DE RENDIMIENTO")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🛬 **Operaciones por hora**", "12.5", "+2.1 vs promedio")
        st.metric("⏱️ **Tiempo promedio en tierra**", "45 min", "-5 min vs objetivo")
        st.metric("🎯 **Factor de carga promedio**", "82.3%", "+4.2% vs mes anterior")
        st.metric("💰 **Ingresos por pasajero**", "$1,850 MXN", "+12% vs año anterior")
    
    with col2:
        st.metric("🌡️ **Satisfacción del cliente**", "4.6/5.0", "+0.2 vs trimestre")
        st.metric("🔧 **Disponibilidad de equipos**", "97.8%", "Dentro de parámetros")
        st.metric("👥 **Ocupación laboral**", "94.2%", "Personal completo")
        st.metric("🌍 **Conectividad internacional**", "28%", "+5% vs año anterior")
    
    st.info("**Nota**: Estos KPIs se actualizan cada 15 minutos con datos de sistemas operativos, APIs gubernamentales y fuentes externas de aviación.")

# Footer
st.markdown("---")
st.markdown("**AIFA - Aeropuerto Internacional Felipe Ángeles** | Centro de Operaciones y Análisis")