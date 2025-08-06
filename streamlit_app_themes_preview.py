import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Agregar la ruta de scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Configuración de la página
st.set_page_config(
    page_title="AIFA - Theme Preview",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SELECTOR DE TEMAS
theme_option = st.sidebar.radio(
    "🎨 SELECCIONA UN TEMA:",
    [
        "Original (Con Emojis)",
        "Aerospace Industry",
        "Corporate Minimal",
        "Financial Dashboard",
        "Dark Professional",
        "Government Official"
    ]
)

# FUNCIÓN PARA APLICAR TEMAS
def apply_theme(theme_name):
    if theme_name == "Original (Con Emojis)":
        return {
            "tabs": ["📊 Simulación", "📈 Datos Históricos", "🎯 Recomendaciones", "📋 Resumen Ejecutivo", 
                    "🎰 Análisis de Slots", "🏢 Diagrama Aeropuerto", "🗺️ Mapa Georeferenciado", "📊 KPIs Reales"],
            "header_style": "",
            "colors": {
                'primary': '#1f77b4',
                'secondary': '#ff7f0e', 
                'success': '#2ca02c',
                'warning': '#ff7f0e',
                'danger': '#d62728'
            },
            "use_emojis": True
        }
    
    elif theme_name == "Aerospace Industry":
        st.markdown("""
        <style>
        .main-header {
            background: #003566;
            color: white;
            padding: 25px;
            margin: -55px -50px 30px;
            border-bottom: 3px solid #0496FF;
        }
        .metric-aerospace {
            background: white;
            border: 1px solid #E5E5E5;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #003566;
        }
        .metric-label {
            color: #666666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .tab-aerospace {
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        return {
            "tabs": ["OPERATIONS", "HISTORICAL DATA", "STRATEGIC PLANNING", "EXECUTIVE SUMMARY", 
                    "SLOT ANALYSIS", "INFRASTRUCTURE", "GEO MAPPING", "REAL-TIME KPIs"],
            "colors": {
                'primary': '#003566',
                'secondary': '#006BA6',
                'success': '#06A77D',
                'warning': '#F1A208',
                'danger': '#D00000'
            },
            "use_emojis": False
        }
    
    elif theme_name == "Corporate Minimal":
        st.markdown("""
        <style>
        .main {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .metric-minimal {
            background: #f8f9fa;
            padding: 24px;
            border-radius: 12px;
            border-left: 4px solid #0066cc;
        }
        h1, h2, h3 {
            font-weight: 300;
            color: #333;
        }
        </style>
        """, unsafe_allow_html=True)
        
        return {
            "tabs": ["Simulation", "Historical Analysis", "Recommendations", "Executive Summary", 
                    "Slot Management", "Airport Layout", "Geographic View", "Live Metrics"],
            "colors": {
                'primary': '#0066cc',
                'secondary': '#666666',
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545'
            },
            "use_emojis": False
        }
    
    elif theme_name == "Financial Dashboard":
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 30px;
            margin: -55px -50px 30px;
            color: white;
        }
        .metric-financial {
            background: #fff;
            border: 1px solid #ddd;
            padding: 20px;
            font-family: 'Courier New', monospace;
        }
        .positive { color: #00c851; }
        .negative { color: #ff3547; }
        </style>
        """, unsafe_allow_html=True)
        
        return {
            "tabs": ["OPS", "HIST", "STRAT", "EXEC", "SLOTS", "INFRA", "GEO", "KPIs"],
            "colors": {
                'primary': '#1e3c72',
                'secondary': '#2a5298',
                'success': '#00c851',
                'warning': '#ffbb33',
                'danger': '#ff3547'
            },
            "use_emojis": False
        }
    
    elif theme_name == "Dark Professional":
        st.markdown("""
        <style>
        .stApp {
            background-color: #0a0a0a;
            color: #ffffff;
        }
        .metric-dark {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            color: #fff;
        }
        .stTabs [data-baseweb="tab"] {
            color: #999;
            background-color: transparent;
        }
        .stTabs [aria-selected="true"] {
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        return {
            "tabs": ["Operations", "Analytics", "Strategy", "Overview", 
                    "Capacity", "Facilities", "Location", "Metrics"],
            "colors": {
                'primary': '#4CAF50',
                'secondary': '#999999',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'danger': '#F44336'
            },
            "use_emojis": False
        }
    
    elif theme_name == "Government Official":
        st.markdown("""
        <style>
        .main-header {
            background: #8B0000;
            color: white;
            padding: 20px;
            border-bottom: 3px solid #FFD700;
        }
        .metric-gov {
            background: #F5F5DC;
            border: 2px solid #8B0000;
            padding: 15px;
            font-family: Georgia, serif;
        }
        </style>
        """, unsafe_allow_html=True)
        
        return {
            "tabs": ["Operaciones", "Datos Históricos", "Planeación", "Resumen", 
                    "Gestión de Slots", "Infraestructura", "Ubicación", "Indicadores"],
            "colors": {
                'primary': '#8B0000',
                'secondary': '#003E7E',
                'success': '#2E7D32',
                'warning': '#F57C00',
                'danger': '#C62828'
            },
            "use_emojis": False
        }

# Aplicar tema seleccionado
theme = apply_theme(theme_option)

# HEADER PRINCIPAL (varía según tema)
if theme_option == "Aerospace Industry":
    st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-weight: 400;">AIFA OPERATIONS CENTER</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Aeropuerto Internacional Felipe Ángeles</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 28px; font-weight: 300;">{datetime.now().strftime('%H:%M')}</div>
                <div style="font-size: 14px; opacity: 0.8;">Mexico City Time</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif theme_option == "Financial Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-weight: 300;">AIFA Executive Dashboard</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Real-time Operations & Financial Analysis</p>
    </div>
    """, unsafe_allow_html=True)
elif theme_option == "Government Official":
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0;">AEROPUERTO INTERNACIONAL FELIPE ÁNGELES</h1>
        <p style="margin: 5px 0 0 0;">Sistema de Monitoreo y Control Ejecutivo</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("✈️ AIFA - Simulador de Rutas" if theme["use_emojis"] else "AIFA - Route Simulator")

# TABS
tabs = st.tabs(theme["tabs"])

# TAB 1: SIMULACIÓN - EJEMPLO DE MÉTRICAS
with tabs[0]:
    st.header("Simulation Results" if not theme["use_emojis"] else "📊 Resultados de Simulación")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas con diferentes estilos según tema
    if theme_option == "Aerospace Industry":
        with col1:
            st.markdown("""
            <div class="metric-aerospace">
                <div class="metric-label">ANNUAL ROI</div>
                <div class="metric-value">23.4%</div>
                <div style="color: #06A77D; font-size: 14px;">▲ +8.4%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-aerospace">
                <div class="metric-label">ANNUAL REVENUE</div>
                <div class="metric-value">$125.8M</div>
                <div style="color: #06A77D; font-size: 14px;">▲ +15.2%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-aerospace">
                <div class="metric-label">OPERATIONS COST</div>
                <div class="metric-value">$96.2M</div>
                <div style="color: #D00000; font-size: 14px;">▼ -3.1%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-aerospace">
                <div class="metric-label">NET PROFIT</div>
                <div class="metric-value">$29.6M</div>
                <div style="color: #06A77D; font-size: 14px;">▲ +42.7%</div>
            </div>
            """, unsafe_allow_html=True)
    
    elif theme_option == "Corporate Minimal":
        with col1:
            st.markdown("""
            <div class="metric-minimal">
                <h2 style="color: #333; margin: 0;">ROI Annual</h2>
                <h1 style="color: #0066cc; margin: 10px 0;">23.4%</h1>
                <p style="color: #666; margin: 0;">+8.4% vs target</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-minimal">
                <h2 style="color: #333; margin: 0;">Revenue</h2>
                <h1 style="color: #0066cc; margin: 10px 0;">$125.8M</h1>
                <p style="color: #666; margin: 0;">+15.2% YoY</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Estilo estándar para otros temas
        with col1:
            st.metric(
                "ROI Anual" if theme["use_emojis"] else "Annual ROI",
                "23.4%",
                "+8.4%"
            )
        with col2:
            st.metric(
                "Ingresos" if theme["use_emojis"] else "Revenue",
                "$125.8M",
                "+15.2%"
            )
        with col3:
            st.metric(
                "Costos" if theme["use_emojis"] else "Costs",
                "$96.2M",
                "-3.1%"
            )
        with col4:
            st.metric(
                "Ganancia" if theme["use_emojis"] else "Profit",
                "$29.6M",
                "+42.7%"
            )
    
    # GRÁFICO DE EJEMPLO
    st.subheader("Monthly ROI Projection" if not theme["use_emojis"] else "📈 Proyección Mensual ROI")
    
    # Datos de ejemplo
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    roi_values = [12, 14, 16, 18, 20, 22, 24, 23, 20, 18, 17, 28]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=roi_values,
        mode='lines+markers',
        name='ROI',
        line=dict(color=theme['colors']['primary'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_hline(
        y=15, 
        line_dash="dash", 
        line_color=theme['colors']['warning'],
        annotation_text="Target 15%"
    )
    
    # Estilo del gráfico según tema
    if theme_option == "Dark Professional":
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0a0a0a',
            font_color='#ffffff'
        )
    else:
        fig.update_layout(
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color="#333")
        )
    
    fig.update_layout(
        title="ROI Performance Analysis",
        xaxis_title="Month",
        yaxis_title="ROI (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: DATOS - TABLA DE EJEMPLO
with tabs[1]:
    st.header("Flight Operations" if not theme["use_emojis"] else "✈️ Operaciones de Vuelo")
    
    # Datos de ejemplo
    flight_data = pd.DataFrame({
        'Time': ['14:30', '14:45', '15:00', '15:15', '15:30'],
        'Flight': ['AM 2341', 'VB 1022', 'Y4 8821', 'AM 0912', 'VB 3421'],
        'Airline': ['Aeromexico', 'VivaAerobus', 'Volaris', 'Aeromexico', 'VivaAerobus'],
        'Destination': ['Cancun', 'Guadalajara', 'Tijuana', 'Miami', 'Monterrey'],
        'Gate': ['A12', 'B04', 'A08', 'C02', 'B11'],
        'Status': ['ON TIME', 'ON TIME', 'DELAYED', 'ON TIME', 'BOARDING']
    })
    
    # Estilo de tabla según tema
    if theme_option == "Aerospace Industry":
        st.markdown("""
        <style>
        .dataframe {
            border: 1px solid #E5E5E5;
            font-family: Arial, sans-serif;
        }
        .dataframe th {
            background-color: #003566;
            color: white;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.dataframe(flight_data, use_container_width=True)

# SIDEBAR CON CONFIGURACIÓN
st.sidebar.markdown("---")
st.sidebar.header("Configuration" if not theme["use_emojis"] else "⚙️ Configuración")

destination = st.sidebar.selectbox(
    "Destination:",
    ['CUN', 'GDL', 'TIJ', 'LAX', 'MIA', 'NYC']
)

airline = st.sidebar.selectbox(
    "Airline:",
    ['Aeromexico', 'VivaAerobus', 'Volaris']
)

# Botón con estilo según tema
if theme_option == "Aerospace Industry":
    st.sidebar.markdown("""
    <style>
    .stButton > button {
        background-color: #0496FF;
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background-color: #003566;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.button("RUN SIMULATION" if not theme["use_emojis"] else "🚀 Ejecutar Simulación")

# INFORMACIÓN DEL TEMA
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Tema Actual:** {theme_option}

**Características:**
- {"Sin emojis" if not theme["use_emojis"] else "Con emojis"}
- Paleta: {theme['colors']['primary']}
- Estilo: {"Profesional" if "Professional" in theme_option else "Moderno"}
""")

# NOTAS DE IMPLEMENTACIÓN
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📝 Notas:
Esta es una **vista previa** para comparar temas.
La versión en producción NO se ve afectada.

**Para implementar:**
1. Elige tu tema favorito
2. Lo aplicamos a la versión principal
3. Sin perder funcionalidad
""")