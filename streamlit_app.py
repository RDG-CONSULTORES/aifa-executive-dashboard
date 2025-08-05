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
    page_title="AIFA - Simulador de Rutas",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para scroll horizontal de tabs
st.markdown("""
<style>
    /* Permitir scroll horizontal en tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        overflow-x: auto;
        scrollbar-width: thin;
        padding-bottom: 5px;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 4px;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Hacer tabs más compactos */
    .stTabs [data-baseweb="tab"] {
        min-width: auto;
        padding: 8px 12px;
        font-size: 14px;
        white-space: nowrap;
    }
    
    /* Ajustar el título para mejor visualización */
    .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🛬 AIFA - Simulador de Atracción de Aerolíneas")
st.markdown("### Análisis de viabilidad y ROI para nuevas rutas aéreas")

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

# Sidebar - Configuración de simulación
st.sidebar.header("⚙️ Configuración de Simulación")

# Selección de destino
destinos_disponibles = ['CUN', 'GDL', 'TIJ', 'LAX', 'MIA', 'NYC', 'CDG', 'MAD', 'LHR']
destino = st.sidebar.selectbox(
    "Destino:",
    destinos_disponibles,
    index=0
)

# Selección de aerolínea
aerolineas = ['VivaAerobus', 'Aeromexico', 'Volaris', 'Interjet', 'Magnicharters']
aerolinea = st.sidebar.selectbox(
    "Aerolínea:",
    aerolineas,
    index=0
)

# Parámetros de la ruta
st.sidebar.subheader("📊 Parámetros de la Ruta")

capacidad_avion = st.sidebar.slider(
    "Capacidad del avión:",
    min_value=100,
    max_value=400,
    value=180,
    step=20
)

frecuencia_semanal = st.sidebar.slider(
    "Frecuencias por semana:",
    min_value=1,
    max_value=14,
    value=4,
    step=1
)

factor_ocupacion = st.sidebar.slider(
    "Factor de ocupación esperado (%):",
    min_value=50,
    max_value=95,
    value=75,
    step=5
) / 100

precio_promedio = st.sidebar.number_input(
    "Precio promedio por boleto (MXN):",
    min_value=800,
    max_value=15000,
    value=2500,
    step=100
)

# Botón de simulación
simular = st.sidebar.button("🚀 Ejecutar Simulación", type="primary")

# Layout principal con tabs originales (8 tabs)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Simulación", 
    "📈 Datos Históricos", 
    "🎯 Recomendaciones", 
    "📋 Resumen Ejecutivo",
    "🎰 Análisis de Slots",
    "🏢 Diagrama Aeropuerto", 
    "🗺️ Mapa Georeferenciado",
    "📊 KPIs Reales"
])

with tab1:
    if simular:
        # Crear simulador con la ruta correcta
        data_path = os.path.join(os.path.dirname(__file__), 'data') + '/'
        simulador = SimuladorRutaAIFA(data_path=data_path)
        
        # Ejecutar simulación
        with st.spinner('Ejecutando simulación...'):
            resultado = simulador.simular_ruta_completa(
                origen='NLU',
                destino=destino,
                aerolinea=aerolinea,
                vuelos_semanales=frecuencia_semanal
            )
        
        # Mostrar resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "ROI Anual",
                f"{resultado['financieros']['roi_porcentaje']:.1f}%",
                delta=f"{resultado['financieros']['roi_porcentaje'] - 15:.1f}% vs objetivo"
            )
        
        with col2:
            st.metric(
                "Ingresos Anuales",
                f"${resultado['financieros']['ingresos_totales_mxn']:,.0f} MXN"
            )
        
        with col3:
            st.metric(
                "Costos Anuales",
                f"${resultado['financieros']['costos_totales_usd'] * 20:,.0f} MXN"
            )
        
        with col4:
            st.metric(
                "Ganancia Neta",
                f"${resultado['financieros']['ganancia_neta_usd'] * 20:,.0f} MXN"
            )
        
        # Gráfico de ROI por mes
        st.subheader("📈 Proyección Mensual de ROI")
        
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
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig_roi.add_hline(y=15, line_dash="dash", line_color="red", 
                         annotation_text="ROI Objetivo (15%)")
        
        fig_roi.update_layout(
            title="Proyección de ROI por Mes",
            xaxis_title="Mes",
            yaxis_title="ROI (%)",
            height=400
        )
        
        st.plotly_chart(fig_roi, use_container_width=True)
        
        # Desglose de costos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Desglose de Costos Anuales")
            
            costos_totales_mxn = resultado['financieros']['costos_totales_usd'] * 20
            costos_detalle = {
                'Combustible': costos_totales_mxn * 0.35,
                'Tripulación': costos_totales_mxn * 0.25,
                'Mantenimiento': costos_totales_mxn * 0.20,
                'Tasas Aeroportuarias': costos_totales_mxn * 0.15,
                'Otros': costos_totales_mxn * 0.05
            }
            
            fig_costos = px.pie(
                values=list(costos_detalle.values()),
                names=list(costos_detalle.keys()),
                title="Distribución de Costos"
            )
            st.plotly_chart(fig_costos, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Análisis de Viabilidad")
            
            score = resultado['analisis']['viabilidad_score'] * 10  # Convertir de 1-10 a 1-100
            
            if score >= 80:
                st.success(f"✅ Ruta VIABLE (Score: {score}/100)")
                st.write("La ruta presenta excelentes perspectivas de rentabilidad.")
            elif score >= 60:
                st.warning(f"⚠️ Ruta MODERADA (Score: {score}/100)")
                st.write("La ruta requiere análisis adicional antes de implementación.")
            else:
                st.error(f"❌ Ruta NO VIABLE (Score: {score}/100)")
                st.write("La ruta presenta alto riesgo de pérdidas.")
            
            # Factores del score
            st.write("**Factores considerados:**")
            st.write(f"- ROI: {resultado['financieros']['roi_porcentaje']:.1f}%")
            st.write(f"- Factor ocupación: {resultado['operacionales']['factor_ocupacion_promedio']*100:.0f}%")
            st.write(f"- Frecuencia: {frecuencia_semanal} vuelos/semana")
            st.write(f"- Pasajeros totales: {resultado['operacionales']['pasajeros_totales']:,}")

with tab2:
    st.header("📊 Análisis de Datos Históricos")
    
    # Gráfico de crecimiento de pasajeros
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Crecimiento de Pasajeros AIFA")
        
        pasajeros_df['mes'] = pd.to_datetime(pasajeros_df['mes'])
        
        fig_pasajeros = px.line(
            pasajeros_df,
            x='mes',
            y='pasajeros',
            title='Evolución Mensual de Pasajeros',
            markers=True
        )
        
        fig_pasajeros.update_traces(line_color='#2E8B57', line_width=3)
        fig_pasajeros.update_layout(height=400)
        
        st.plotly_chart(fig_pasajeros, use_container_width=True)
    
    with col2:
        st.subheader("💵 Tarifas Promedio por Destino")
        
        fig_tarifas = px.bar(
            tarifas_df,
            x='destination',
            y='tarifa_promedio_mxn',
            title='Precio Promedio por Destino',
            color='tarifa_promedio_mxn',
            color_continuous_scale='viridis'
        )
        
        fig_tarifas.update_layout(height=400)
        st.plotly_chart(fig_tarifas, use_container_width=True)
    
    # Tabla de rutas actuales
    st.subheader("🛫 Rutas Actuales AIFA")
    st.dataframe(rutas_df, use_container_width=True)

with tab3:
    st.header("🎯 Recomendaciones Estratégicas")
    
    st.subheader("🏆 Top Rutas Recomendadas")
    
    # Mostrar resumen estratégico
    if not resumen_df.empty:
        for idx, row in resumen_df.iterrows():
            with st.expander(f"✈️ {row['ruta']} - ROI: {row['roi_estimado']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Aerolínea sugerida:** {row['aerolinea_sugerida']}")
                    st.write(f"**Demanda estimada:** {row['demanda_estimada']:,} pasajeros/año")
                    st.write(f"**ROI estimado:** {row['roi_estimado']}")
                
                with col2:
                    st.write(f"**Observaciones:**")
                    st.write(row['observaciones'])
    
    # Recomendaciones generales
    st.subheader("💡 Recomendaciones Generales")
    
    recomendaciones = [
        "🎯 **Enfoque en rutas domésticas**: Mayor demanda y menores costos operativos",
        "🌟 **Alianzas estratégicas**: Negociar con aerolíneas de bajo costo para mayor volumen",
        "📊 **Monitoreo continuo**: Implementar KPIs para evaluar performance de rutas",
        "🚀 **Marketing dirigido**: Campañas específicas para destinos turísticos",
        "💰 **Optimización de precios**: Estrategias dinámicas según temporada",
        "🛡️ **Gestión de riesgos**: Diversificar portfolio de rutas para minimizar riesgos"
    ]
    
    for rec in recomendaciones:
        st.markdown(rec)

with tab4:
    st.header("📋 Resumen Ejecutivo")
    
    # KPIs principales
    st.subheader("📊 Métricas Clave AIFA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Pasajeros Totales 2023",
            "678K",
            delta="35% vs 2022"
        )
    
    with col2:
        st.metric(
            "Rutas Activas",
            len(rutas_df),
            delta="+2 nuevas rutas"
        )
    
    with col3:
        st.metric(
            "Aerolíneas Operando",
            rutas_df['airline'].nunique(),
            delta="+1 aerolínea"
        )
    
    with col4:
        st.metric(
            "Tarifa Promedio",
            f"${tarifas_df['tarifa_promedio_mxn'].mean():,.0f} MXN"
        )
    
    # Análisis FODA simplificado
    st.subheader("⚖️ Análisis Estratégico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**🟢 Fortalezas**")
        st.write("- Ubicación estratégica en zona metropolitana")
        st.write("- Infraestructura moderna y capacidad de crecimiento")
        st.write("- Apoyo gubernamental y tarifas competitivas")
        st.write("- Menor saturación vs. otros aeropuertos")
        
        st.info("**🔵 Oportunidades**")
        st.write("- Crecimiento del mercado de aviación mexicano")
        st.write("- Demanda insatisfecha en rutas internacionales")
        st.write("- Potencial para aerolíneas de bajo costo")
        st.write("- Conectividad con destinos turísticos")
    
    with col2:
        st.warning("**🟡 Debilidades**")
        st.write("- Reconocimiento de marca limitado")
        st.write("- Conectividad terrestre en desarrollo")
        st.write("- Competencia con aeropuertos establecidos")
        st.write("- Base de pasajeros en construcción")
        
        st.error("**🔴 Amenazas**")
        st.write("- Volatilidade económica y del combustible")
        st.write("- Regulaciones cambiantes en aviación")
        st.write("- Competencia agresiva de otros aeropuertos")
        st.write("- Eventos externos (pandemias, conflictos)")

with tab5:
    st.header("🎰 Análisis de Slots Aeroportuarios AIFA")
    
    # Obtener métricas en tiempo real
    metricas_slots = obtener_metricas_slots()
    visualizaciones = generar_visualizaciones_slots()
    
    # Métricas principales en tiempo real
    st.subheader("⏰ Métricas en Tiempo Real")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🕐 Hora Actual",
            metricas_slots['tiempo_real']['hora'],
            delta=f"{metricas_slots['tiempo_real']['slots_disponibles_ahora']} slots libres"
        )
    
    with col2:
        st.metric(
            "📊 Ocupación Actual",
            f"{metricas_slots['tiempo_real']['ocupacion_actual']:.1f}%",
            delta="Normal" if metricas_slots['tiempo_real']['ocupacion_actual'] < 80 else "Alta"
        )
    
    with col3:
        st.metric(
            "🎯 Próximo Slot Libre",
            metricas_slots['tiempo_real']['proximo_slot_libre']
        )
    
    with col4:
        st.metric(
            "💰 Ingresos Potenciales",
            metricas_slots['proyecciones']['ingresos_potenciales']
        )
    
    # Mapa de calor de disponibilidad
    st.subheader("🗓️ Mapa de Calor - Disponibilidad Semanal")
    st.plotly_chart(visualizaciones['mapa_calor'], use_container_width=True)
    
    # Vista 3D de utilización
    st.subheader("🎲 Vista 3D - Utilización de Slots")
    st.plotly_chart(visualizaciones['vista_3d'], use_container_width=True)
    
    # Ventanas óptimas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Mejores Ventanas para Nuevos Slots")
        
        for ventana in visualizaciones['ventanas_optimas']:
            with st.expander(f"⏰ {ventana['hora']:02d}:00 - Score: {ventana['score_oportunidad']:.1f}/100"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write(f"**Slots disponibles:** {ventana['slots_disponibles']}")
                    st.write(f"**Tipo:** {'Hora Pico' if ventana['es_hora_pico'] else 'Hora Valle'}")
                
                with col_b:
                    st.write(f"**Recomendación:**")
                    st.write(ventana['recomendacion'])
    
    with col2:
        st.subheader("📊 Resumen del Día")
        
        st.info(f"""
        **Total Slots:** {metricas_slots['resumen_dia']['total_slots_dia']}
        **Ocupados:** {metricas_slots['resumen_dia']['slots_ocupados']}
        **Disponibles:** {metricas_slots['resumen_dia']['slots_disponibles']}
        **Ocupación Promedio:** {metricas_slots['resumen_dia']['ocupacion_promedio']:.1f}%
        """)
        
        st.success(f"""
        **🎯 Oportunidades**
        
        **Hora Pico:** {metricas_slots['oportunidades']['slots_hora_pico_disponibles']} slots
        **Hora Valle:** {metricas_slots['oportunidades']['slots_hora_valle_disponibles']} slots
        **Potencial Mes:** {metricas_slots['proyecciones']['slots_potenciales_mes']} slots
        """)
    
    # Análisis de conectividad
    st.subheader("🌐 Análisis de Conectividad")
    
    # Crear gráfico de conectividad
    conectividad_data = {
        'Horario': ['05:00-09:00', '09:00-13:00', '13:00-17:00', '17:00-21:00', '21:00-23:00'],
        'Conexiones_Nacionales': [15, 22, 18, 25, 10],
        'Conexiones_Internacionales': [5, 12, 15, 20, 8],
        'Slots_Disponibles': [12, 8, 15, 6, 18]
    }
    
    df_conectividad = pd.DataFrame(conectividad_data)
    
    fig_conectividad = go.Figure()
    
    fig_conectividad.add_trace(go.Bar(
        name='Conexiones Nacionales',
        x=df_conectividad['Horario'],
        y=df_conectividad['Conexiones_Nacionales'],
        marker_color='lightblue'
    ))
    
    fig_conectividad.add_trace(go.Bar(
        name='Conexiones Internacionales',
        x=df_conectividad['Horario'],
        y=df_conectividad['Conexiones_Internacionales'],
        marker_color='darkblue'
    ))
    
    fig_conectividad.add_trace(go.Scatter(
        name='Slots Disponibles',
        x=df_conectividad['Horario'],
        y=df_conectividad['Slots_Disponibles'],
        mode='lines+markers',
        line=dict(color='red', width=3),
        yaxis='y2'
    ))
    
    fig_conectividad.update_layout(
        title='Conectividad y Disponibilidad por Horario',
        xaxis_title='Franja Horaria',
        yaxis_title='Número de Conexiones',
        yaxis2=dict(
            title='Slots Disponibles',
            overlaying='y',
            side='right'
        ),
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig_conectividad, use_container_width=True)

with tab6:
    st.header("🏢 Diagrama del Aeropuerto AIFA")
    
    # Crear instancia del diagrama
    airport_diagram = AIFAAirportDiagram()
    
    # Generar el diagrama completo
    with st.spinner('Generando diagrama del aeropuerto...'):
        fig_diagram = airport_diagram.create_airport_diagram()
    
    st.plotly_chart(fig_diagram, use_container_width=True)
    
    # Información detallada del aeropuerto
    st.subheader("ℹ️ Información del Aeropuerto")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🚪 Terminales y Puertas**
        - Terminal A: Puertas A1-A12 (Vuelos Nacionales)
        - Terminal B: Puertas B1-B10 (Vuelos Internacionales)
        - Terminal C: Puertas C1-C13 (Vuelos Regionales)
        """)
    
    with col2:
        st.success("""
        **🛫 Pistas de Aterrizaje**
        - Pista 04/22: 4,000m x 45m (Principal)
        - Pista 18/36: 3,500m x 45m (Secundaria)
        - Capacidad: 60 operaciones/hora
        """)
    
    with col3:
        st.warning("""
        **📊 Estado Actual**
        - Ocupación Promedio: 65%
        - Puertas Disponibles: 12/35
        - Próximo Slot Libre: 14:30
        - Operaciones Activas: 23
        """)
    
    # Métricas en tiempo real del aeropuerto
    st.subheader("⚡ Métricas en Tiempo Real")
    
    metrics_data = airport_diagram.get_realtime_metrics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "✈️ Vuelos Activos",
            metrics_data['active_flights'],
            delta=f"+{metrics_data['active_flights'] - 18} vs promedio"
        )
    
    with col2:
        st.metric(
            "🚪 Puertas Ocupadas",
            f"{metrics_data['occupied_gates']}/35",
            delta=f"{metrics_data['gate_occupancy']:.1f}% ocupación"
        )
    
    with col3:
        st.metric(
            "🛬 Aterrizajes Hoy",
            metrics_data['landings_today'],
            delta="+3 vs ayer"
        )
    
    with col4:
        st.metric(
            "🛫 Despegues Hoy",
            metrics_data['takeoffs_today'],
            delta="+2 vs ayer"
        )
    
    with col5:
        st.metric(
            "⏱️ Retraso Promedio",
            f"{metrics_data['avg_delay']} min",
            delta="-5 min vs ayer" if metrics_data['avg_delay'] < 15 else "+2 min vs ayer"
        )
    
    # Tabla de vuelos próximos
    st.subheader("📋 Próximos Vuelos")
    
    upcoming_flights = airport_diagram.get_upcoming_flights()
    df_flights = pd.DataFrame(upcoming_flights)
    
    st.dataframe(
        df_flights,
        use_container_width=True,
        column_config={
            "hora": st.column_config.TimeColumn("🕐 Hora"),
            "vuelo": st.column_config.TextColumn("✈️ Vuelo"),
            "aerolinea": st.column_config.TextColumn("🏢 Aerolínea"),
            "destino": st.column_config.TextColumn("🎯 Destino"),
            "puerta": st.column_config.TextColumn("🚪 Puerta"),
            "estado": st.column_config.TextColumn("📊 Estado"),
            "tipo": st.column_config.TextColumn("🔄 Tipo")
        }
    )
    
    # Recomendaciones operacionales
    st.subheader("💡 Recomendaciones Operacionales")
    
    recommendations = [
        "🎯 **Optimización de Slots**: Las puertas B7-B10 tienen menor utilización, ideales para vuelos de mayor duración",
        "⚡ **Horas Valle**: Aprovechar 10:00-12:00 y 15:00-17:00 para nuevas rutas con mayor flexibilidad",
        "🚀 **Crecimiento**: Terminal C tiene capacidad para 5 puertas adicionales con demanda proyectada",
        "📊 **Monitoreo**: Implementar sensores IoT en puertas A8-A12 para optimizar tiempos de rotación",
        "🌐 **Conectividad**: Mejorar señalización digital en Terminal B para reducir tiempos de conexión"
    ]
    
    for rec in recommendations:
        st.markdown(rec)

with tab7:
    st.header("🗺️ Mapa Georeferenciado AIFA")
    st.markdown("### Vista satelital del aeropuerto con ubicación real y ocupación de gates")
    
    # Crear instancia del mapa georeferenciado
    geo_map = AIFAGeoMap()
    
    # Controles de visualización
    col1, col2, col3 = st.columns(3)
    
    with col1:
        map_style = st.selectbox(
            "🎨 Estilo de Mapa:",
            ["satellite", "open-street-map", "satellite-streets"],
            index=0,
            help="Selecciona el estilo de visualización del mapa"
        )
    
    with col2:
        show_gates = st.checkbox(
            "🚪 Mostrar Gates",
            value=True,
            help="Mostrar ubicación y estado de las puertas de embarque"
        )
    
    with col3:
        show_runways = st.checkbox(
            "🛫 Mostrar Pistas",
            value=True,
            help="Mostrar pistas de aterrizaje y despegue"
        )
    
    # Generar mapa principal
    with st.spinner('Generando mapa satelital georeferenciado...'):
        satellite_map = geo_map.create_satellite_map()
    
    st.plotly_chart(satellite_map, use_container_width=True)
    
    # Información georeferenciada
    st.subheader("📍 Información Georeferenciada")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **🌍 Coordenadas Centrales**
        - **Latitud:** 19.7425°N
        - **Longitud:** 99.0157°W
        - **Elevación:** 2,226 msnm
        - **Zona Horaria:** UTC-6 (CST)
        """)
    
    with col2:
        st.success(f"""
        **🛫 Pistas Georeferenciadas**
        - **RW04/22:** 4,000m (Principal)
        - **Orientación:** 043°/223° magnético
        - **Elevación:** 2,226 msnm
        - **Superficie:** Concreto reforzado
        """)
    
    with col3:
        occupancy_stats = geo_map.get_gate_occupancy_stats()
        st.warning(f"""
        **📊 Estado de Gates**
        - **Total Gates:** {occupancy_stats['total_gates']}
        - **Ocupados:** {occupancy_stats['occupied_gates']} ({occupancy_stats['occupancy_rate']:.1f}%)
        - **Disponibles:** {occupancy_stats['available_gates']}
        - **Actualizado:** {occupancy_stats['timestamp']}
        """)
    
    # Vista 3D del aeropuerto
    st.subheader("🏗️ Vista 3D del Complejo Aeroportuario")
    
    with st.spinner('Generando vista 3D...'):
        map_3d = geo_map.create_3d_airport_view()
    
    st.plotly_chart(map_3d, use_container_width=True)
    
    # Mapa de calor de ocupación
    st.subheader("🔥 Mapa de Calor - Ocupación de Gates")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.spinner('Generando mapa de calor...'):
            heatmap = geo_map.create_occupancy_heatmap()
        
        st.plotly_chart(heatmap, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Análisis de Ocupación")
        
        # Análisis detallado por terminal
        terminal_analysis = geo_map.get_terminal_analysis()
        
        for terminal, data in terminal_analysis.items():
            with st.expander(f"🏢 {terminal}"):
                st.write(f"**Gates Totales:** {data['total_gates']}")
                st.write(f"**Ocupados:** {data['occupied_gates']}")
                st.write(f"**Ocupación:** {data['occupancy_rate']:.1f}%")
                st.write(f"**Tipo:** {data['flight_type']}")
                
                # Indicador visual de ocupación
                if data['occupancy_rate'] > 80:
                    st.error("🔴 Alta ocupación")
                elif data['occupancy_rate'] > 60:
                    st.warning("🟡 Ocupación moderada")
                else:
                    st.success("🟢 Baja ocupación")
    
    # Información adicional del mapa
    st.subheader("ℹ️ Detalles del Mapa Georeferenciado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🛰️ Datos del Mapa Satelital:**
        - **Fuente:** Mapbox Satellite
        - **Resolución:** Alta definición
        - **Coordenadas:** Sistema WGS84
        - **Proyección:** Web Mercator
        - **Precisión:** ±3 metros
        
        **🏗️ Infraestructura Mapeada:**
        - ✅ Terminal de pasajeros
        - ✅ Pistas de aterrizaje
        - ✅ Calles de rodaje (taxiways)
        - ✅ Plataformas de estacionamiento
        - ✅ Torres de control
        - ✅ Áreas de servicio
        """)
    
    with col2:
        st.markdown("""
        **🎯 Estado en Tiempo Real:**
        - **Datos:** Simulación basada en patrones reales
        - **Actualización:** Cada 30 segundos
        - **Gates:** Ocupación dinámica
        - **Colores:** Rojo=Ocupado, Verde=Disponible
        
        **📊 Métricas Visuales:**
        - 🔴 **Gate Ocupado:** Vuelo activo o en preparación
        - 🟢 **Gate Disponible:** Listo para nueva asignación
        - 🔵 **Pista Principal:** RW04/22 (4,000m)
        - 🟡 **Edificios Terminales:** A, B, C
        - ⚫ **Infraestructura de Apoyo:** Torres, hangares
        """)
    
    # Controles avanzados
    st.subheader("⚙️ Controles Avanzados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Actualizar Datos", type="secondary"):
            st.rerun()
    
    with col2:
        if st.button("📸 Captura Aérea", type="secondary"):
            st.info("Vista satelital actualizada desde coordenadas 19.7425°N, 99.0157°W")
    
    with col3:
        zoom_level = st.slider("🔍 Nivel de Zoom", 10, 18, 15)
    
    with col4:
        if st.button("🎯 Centrar en AIFA", type="secondary"):
            st.success("Mapa centrado en las coordenadas principales del AIFA")

with tab8:
    st.header("📊 KPIs Reales del AIFA")
    st.markdown("### Datos verificados de fuentes oficiales del gobierno mexicano")
    st.caption("🔍 Fuentes: AFAC, DATATUR SECTUR, ASA, datos.gob.mx")
    
    # Inicializar conectores de datos reales
    with st.spinner('Cargando datos gubernamentales verificados...'):
        try:
            # Conector de datos gubernamentales
            gov_connector = GobMXRealDataConnector()
            
            # Conector AviationStack (opcional, con fallback)
            aviationstack_key = st.secrets.get("AVIATIONSTACK_KEY", "59f5d7300a3c8236dc29e095fa6ab923")
            aviation_connector = AviationStackConnector(aviationstack_key) if aviationstack_key else None
            
            # Conector FlightAware (opcional, con fallback)
            flightaware_key = st.secrets.get("FLIGHTAWARE_API_KEY", "gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc")
            flightaware_connector = FlightAwareConnector(flightaware_key) if flightaware_key else None
            
            # Weather Manager (OpenWeatherMap)
            openweather_key = st.secrets.get("OPENWEATHER_API_KEY", "6a6e94ae482a1c310fe583b6a35eb72b")
            weather_manager = WeatherManager(openweather_key) if openweather_key else None
            
            # FlightRadar24 Connector
            flightradar_key = st.secrets.get("FLIGHTRADAR24_SANDBOX_KEY", "01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb")
            flightradar_connector = FlightRadar24ZoneConnector(flightradar_key) if flightradar_key else None
            
            # Calculadora de KPIs
            kpi_calc = AIFAKPICalculator(gov_connector, aviation_connector, flightaware_connector, weather_manager, flightradar_connector)
            
            # Generar dashboard ejecutivo completo
            dashboard_data = kpi_calc.generate_executive_dashboard()
            
            # ✅ SECCIÓN 1: SCORECARD GENERAL
            st.subheader("🎯 Scorecard General de Desempeño")
            
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
                    delta="Eficiencia de gates: 48.6%"
                )
            
            with col4:
                st.metric(
                    "💰 Económico",
                    f"{scorecard['score_economico']}/100",
                    delta="Derrama: $44.4B MXN/año"
                )
            
            # ✅ SECCIÓN 2: KPIs ESTRATÉGICOS VERIFICADOS
            st.subheader("🚀 KPIs Estratégicos (Datos Oficiales)")
            
            strategic_kpis = dashboard_data['kpis_estrategicos']
            
            # KPI 1: Participación Nacional
            kpi1 = strategic_kpis['kpi_1_participacion_nacional']
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.metric(
                    kpi1['nombre'],
                    f"{kpi1['valor_actual']}%",
                    delta=kpi1['tendencia']
                )
                st.caption(f"✅ Fuente: {kpi1['fuente']}")
                st.caption(f"🎯 Objetivo 2025: {kpi1['objetivo_2025']}% | Brecha: {kpi1['brecha_objetivo']}%")
                
                # Progreso hacia objetivo
                progress_participacion = (kpi1['valor_actual'] / kpi1['objetivo_2025']) * 100
                st.progress(min(progress_participacion / 100, 1.0))
                st.caption(f"Progreso hacia objetivo: {progress_participacion:.1f}%")
            
            with col2:
                estado_color = {
                    'EXCELENTE': '🟢',
                    'BUENO': '🟡', 
                    'REGULAR': '🟠',
                    'REQUIERE_ATENCION': '🔴'
                }
                st.info(f"""
                **{estado_color.get(kpi1['estado'], '⚪')} Estado: {kpi1['estado']}**
                
                **Confiabilidad:** {kpi1['confiabilidad']}
                **Impacto:** {kpi1['impacto_negocio']}
                **Fórmula:** {kpi1['formula']}
                """)
            
            # KPI 2: Crecimiento Anual
            st.markdown("---")
            kpi2 = strategic_kpis['kpi_2_crecimiento_anual']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "📈 Crecimiento 2024",
                    f"{kpi2['valor_2024']}%",
                    delta=f"vs 2023: {kpi2['valor_2023']}%"
                )
            
            with col2:
                st.metric(
                    "🎯 Proyección 2025",
                    f"{kpi2['proyeccion_2025']}%",
                    delta=f"vs Industria: {kpi2['promedio_industria']}%"
                )
            
            with col3:
                st.metric(
                    "🏆 Ventaja Competitiva",
                    kpi2['ventaja_competitiva'],
                    delta=kpi2['estado']
                )
            
            # Gráfico de crecimiento histórico
            st.subheader("📊 Evolución Histórica de Crecimiento")
            
            crecimiento_data = {
                'Año': ['2022', '2023', '2024', '2025*'],
                'Pasajeros': [912415, 2631261, 6348000, 7300000],
                'Crecimiento': [0, 188.0, 141.3, 15.0]
            }
            
            fig_crecimiento = go.Figure()
            
            # Barras de pasajeros
            fig_crecimiento.add_trace(go.Bar(
                name='Pasajeros (Millones)',
                x=crecimiento_data['Año'],
                y=[p/1000000 for p in crecimiento_data['Pasajeros']],
                marker_color=['lightblue', 'blue', 'darkblue', 'navy'],
                yaxis='y1'
            ))
            
            # Línea de crecimiento
            fig_crecimiento.add_trace(go.Scatter(
                name='Crecimiento %',
                x=crecimiento_data['Año'][1:],  # Excluir 2022
                y=crecimiento_data['Crecimiento'][1:],
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=10),
                yaxis='y2'
            ))
            
            fig_crecimiento.update_layout(
                title='Evolución de Pasajeros y Crecimiento AIFA',
                xaxis_title='Año',
                yaxis=dict(title='Pasajeros (Millones)', side='left'),
                yaxis2=dict(title='Crecimiento (%)', side='right', overlaying='y'),
                height=400
            )
            
            st.plotly_chart(fig_crecimiento, use_container_width=True)
            
            # Mostrar más KPIs según disponibilidad
            if 'kpis_operacionales' in dashboard_data:
                st.subheader("⚙️ KPIs Operacionales")
                operational_kpis = dashboard_data['kpis_operacionales']
                
                # Mostrar algunos KPIs operacionales clave
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'kpi_4_utilizacion_infraestructura' in operational_kpis:
                        kpi4 = operational_kpis['kpi_4_utilizacion_infraestructura']
                        st.metric(
                            "🚪 Utilización Gates",
                            f"{kpi4['porcentaje_utilizacion']}%",
                            delta=f"{kpi4['gates_activos']}/{kpi4['gates_totales']} activos"
                        )
                
                with col2:
                    if 'kpi_6_operaciones_tiempo_real' in operational_kpis:
                        kpi6 = operational_kpis['kpi_6_operaciones_tiempo_real']
                        if kpi6.get('estado') == 'DATOS_REALES_ACTIVOS':
                            st.metric(
                                "✈️ Operaciones Hoy",
                                kpi6.get('operaciones_dia', 'N/A'),
                                delta="Tiempo real"
                            )
                
                with col3:
                    if 'kpi_8_condiciones_meteorologicas' in operational_kpis:
                        kpi8 = operational_kpis['kpi_8_condiciones_meteorologicas']
                        if kpi8.get('estado') == 'DATOS_REALES_ACTIVOS':
                            st.metric(
                                "🌤️ Temperatura AIFA",
                                f"{kpi8.get('temperatura_actual', 'N/A')}°C",
                                delta="OpenWeatherMap"
                            )
            
        except Exception as e:
            st.error(f"⚠️ Error cargando KPIs reales: {str(e)}")
            st.info("""
            **💡 Información sobre los KPIs Reales:**
            
            Este módulo integra datos verificados del gobierno mexicano para proporcionar 
            KPIs estratégicos, operacionales y económicos del AIFA basados en fuentes oficiales:
            
            - **AFAC**: Estadísticas oficiales de aviación civil
            - **DATATUR**: Sistema nacional de información turística  
            - **ASA**: Aeropuertos y servicios auxiliares
            - **datos.gob.mx**: Portal de datos abiertos del gobierno
            
            **Datos clave verificados:**
            - 6.348M pasajeros en 2024 (crecimiento 141.3%)
            - Participación nacional: 1.4%
            - Ranking: #10 aeropuerto nacional
            - Utilización de gates: 17/35 (48.6%)
            """)

# Footer
st.markdown("---")
st.markdown("### 🔧 Herramientas Utilizadas")
st.markdown("**Simulación:** Algoritmos de ROI y análisis de viabilidad | **Visualización:** Plotly & Streamlit | **Datos:** CSV históricos y proyecciones | **Slots:** Análisis en tiempo real | **Diagrama:** Layout interactivo del aeropuerto | **Mapa Georeferenciado:** Vista satelital con coordenadas reales (19.7425°N, 99.0157°W) | **KPIs Reales:** Datos gubernamentales (AFAC, DATATUR, ASA) + AviationStack (40 operaciones/día) + FlightAware (puntualidad 95%) + OpenWeatherMap OneCall 3.0 (condiciones meteorológicas en tiempo real)")