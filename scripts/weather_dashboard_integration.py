"""
Integración de datos meteorológicos en el dashboard de Streamlit
Añade nueva pestaña con análisis meteorológico en tiempo real
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Importar el WeatherManager
sys.path.append(os.path.dirname(__file__))
from weather_manager import WeatherManager

def render_weather_tab():
    """Renderiza la pestaña de análisis meteorológico"""
    
    st.header("🌤️ Análisis Meteorológico en Tiempo Real")
    
    # Inicializar WeatherManager
    weather_mgr = WeatherManager()
    
    # Mostrar modo de operación
    mode_color = "🟢" if weather_mgr.use_real_data else "🟡"
    mode_text = "DATOS REALES" if weather_mgr.use_real_data else "SIMULACIÓN"
    st.info(f"{mode_color} **Modo de operación**: {mode_text}")
    
    # Aeropuertos principales para análisis
    airports_analysis = ['NLU', 'MEX', 'CUN', 'GDL', 'TIJ']
    
    # Obtener datos meteorológicos
    weather_dashboard = weather_mgr.get_weather_dashboard_data(airports_analysis)
    
    # Métricas generales
    st.subheader("📊 Resumen Meteorológico")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌤️ Condiciones Buenas",
            weather_dashboard['summary']['good_conditions'],
            delta=f"{weather_dashboard['summary']['total_airports']} aeropuertos"
        )
    
    with col2:
        st.metric(
            "⚠️ Condiciones Precaución",
            weather_dashboard['summary']['caution_conditions'],
            delta="Monitorear"
        )
    
    with col3:
        st.metric(
            "❌ Condiciones Adversas",
            weather_dashboard['summary']['poor_conditions'],
            delta="Crítico" if weather_dashboard['summary']['poor_conditions'] > 0 else "OK"
        )
    
    with col4:
        st.metric(
            "🎯 Impacto Operacional",
            weather_dashboard['summary']['operational_impact'].title(),
            delta="General"
        )
    
    # Vista detallada por aeropuerto
    st.subheader("✈️ Condiciones por Aeropuerto")
    
    # Crear datos para visualización
    airport_weather_data = []
    for code, data in weather_dashboard['airports'].items():
        airport_weather_data.append({
            'Aeropuerto': f"{code} - {data['name']}",
            'Temperatura': f"{data['temperature']}°C",
            'Condiciones': data['conditions'],
            'Viento': f"{data['wind_speed']} m/s",
            'Visibilidad': f"{data['visibility']} km",
            'Estado Vuelo': data['flight_status'],
            'Impacto': data['flight_impact']
        })
    
    df_weather = pd.DataFrame(airport_weather_data)
    
    # Función para colorear filas basado en estado de vuelo
    def color_flight_status(val):
        if val == 'good':
            return 'background-color: #d4edda'
        elif val == 'caution':
            return 'background-color: #fff3cd'
        elif val == 'poor':
            return 'background-color: #f8d7da'
        return ''
    
    # Mostrar tabla con colores
    styled_df = df_weather.style.applymap(color_flight_status, subset=['Estado Vuelo'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Análisis de ruta específica
    st.subheader("🛫 Análisis de Ruta Específica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        origin_airport = st.selectbox(
            "Aeropuerto Origen:",
            airports_analysis,
            index=0,
            format_func=lambda x: f"{x} - {weather_dashboard['airports'][x]['name']}" if x in weather_dashboard['airports'] else x
        )
    
    with col2:
        destination_airports = [code for code in airports_analysis if code != origin_airport]
        dest_airport = st.selectbox(
            "Aeropuerto Destino:",
            destination_airports,
            index=0,
            format_func=lambda x: f"{x} - {weather_dashboard['airports'][x]['name']}" if x in weather_dashboard['airports'] else x
        )
    
    if st.button("🔍 Analizar Ruta", type="primary"):
        # Obtener análisis de ruta
        route_analysis = weather_mgr.get_route_weather(origin_airport, dest_airport)
        
        if route_analysis['origin'] and route_analysis['destination']:
            st.success("✅ Análisis de ruta completado")
            
            # Mostrar análisis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🛫 Origen: {origin_airport}")
                origin_data = route_analysis['origin']
                st.write(f"**🌡️ Temperatura**: {origin_data['current']['temperature']}°C")
                st.write(f"**🌤️ Condiciones**: {origin_data['current']['weather']['description']}")
                st.write(f"**💨 Viento**: {origin_data['current']['wind']['speed']} m/s")
                st.write(f"**👁️ Visibilidad**: {origin_data['current']['visibility']} km")
                
                status_color = "🟢" if origin_data['conditions']['overall_status'] == 'good' else "🟡" if origin_data['conditions']['overall_status'] == 'caution' else "🔴"
                st.write(f"**{status_color} Estado**: {origin_data['conditions']['overall_status']}")
            
            with col2:
                st.subheader(f"🛬 Destino: {dest_airport}")
                dest_data = route_analysis['destination']
                st.write(f"**🌡️ Temperatura**: {dest_data['current']['temperature']}°C")
                st.write(f"**🌤️ Condiciones**: {dest_data['current']['weather']['description']}")
                st.write(f"**💨 Viento**: {dest_data['current']['wind']['speed']} m/s")
                st.write(f"**👁️ Visibilidad**: {dest_data['current']['visibility']} km")
                
                status_color = "🟢" if dest_data['conditions']['overall_status'] == 'good' else "🟡" if dest_data['conditions']['overall_status'] == 'caution' else "🔴"
                st.write(f"**{status_color} Estado**: {dest_data['conditions']['overall_status']}")
            
            # Análisis general de la ruta
            analysis = route_analysis['route_analysis']
            
            if analysis['overall_status'] == 'good':
                st.success(f"✅ **Ruta Viable** - {analysis['flight_advice']}")
            elif analysis['overall_status'] == 'caution':
                st.warning(f"⚠️ **Ruta con Precaución** - {analysis['flight_advice']}")
            else:
                st.error(f"❌ **Ruta Adversa** - {analysis['flight_advice']}")
            
            # Recomendaciones
            if analysis['recommendations']:
                st.subheader("💡 Recomendaciones")
                for rec in analysis['recommendations']:
                    st.write(f"• {rec}")
        else:
            st.error("❌ Error obteniendo datos de la ruta")
    
    # Gráfico de temperaturas por aeropuerto
    st.subheader("🌡️ Comparativa de Temperaturas")
    
    temp_data = []
    for code, data in weather_dashboard['airports'].items():
        temp_data.append({
            'Aeropuerto': code,
            'Nombre_Completo': data['name'],
            'Temperatura': data['temperature'],
            'Estado': data['flight_status']
        })
    
    df_temp = pd.DataFrame(temp_data)
    
    # Crear gráfico de barras con colores por estado
    color_map = {
        'good': '#28a745',
        'caution': '#ffc107', 
        'poor': '#dc3545'
    }
    
    df_temp['Color'] = df_temp['Estado'].map(color_map)
    
    fig_temp = go.Figure()
    
    for status in ['good', 'caution', 'poor']:
        df_filtered = df_temp[df_temp['Estado'] == status]
        if not df_filtered.empty:
            fig_temp.add_trace(go.Bar(
                name=status.title(),
                x=df_filtered['Aeropuerto'],
                y=df_filtered['Temperatura'],
                marker_color=color_map[status],
                text=df_filtered['Temperatura'],
                textposition='auto',
            ))
    
    fig_temp.update_layout(
        title='Temperatura por Aeropuerto (Coloreado por Estado de Vuelo)',
        xaxis_title='Aeropuerto',
        yaxis_title='Temperatura (°C)',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # Radar chart de condiciones meteorológicas
    st.subheader("🎯 Radar de Condiciones - AIFA vs Competencia")
    
    # Datos para radar chart (normalizar valores)
    aifa_data = weather_dashboard['airports'].get('NLU', {})
    mex_data = weather_dashboard['airports'].get('MEX', {})
    
    if aifa_data and mex_data:
        categories = ['Temperatura', 'Viento', 'Visibilidad', 'Condiciones Generales']
        
        # Normalizar datos (0-100 scale)
        aifa_values = [
            max(0, min(100, (aifa_data['temperature'] + 10) * 2)),  # Temperatura
            max(0, min(100, 100 - aifa_data['wind_speed'] * 5)),    # Viento (invertido)
            max(0, min(100, aifa_data['visibility'] * 10)),         # Visibilidad
            85 if aifa_data['flight_status'] == 'good' else 60 if aifa_data['flight_status'] == 'caution' else 30  # Estado general
        ]
        
        mex_values = [
            max(0, min(100, (mex_data['temperature'] + 10) * 2)),
            max(0, min(100, 100 - mex_data['wind_speed'] * 5)),
            max(0, min(100, mex_data['visibility'] * 10)),
            85 if mex_data['flight_status'] == 'good' else 60 if mex_data['flight_status'] == 'caution' else 30
        ]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=aifa_values,
            theta=categories,
            fill='toself',
            name='AIFA (NLU)',
            line_color='blue'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=mex_values,
            theta=categories,
            fill='toself',
            name='AICM (MEX)',
            line_color='red'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Comparativa de Condiciones Meteorológicas",
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Información adicional
    st.subheader("ℹ️ Información del Sistema Meteorológico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🔧 Sistema Implementado**
        - WeatherManager inteligente
        - Auto-fallback a simulación
        - Análisis de condiciones de vuelo
        - Evaluación de rutas completas
        - Datos organizados para dashboard
        """)
    
    with col2:
        data_source = weather_dashboard.get('data_source', 'unknown')
        if data_source == 'openweathermap':
            st.success("""
            **🌐 Fuente de Datos: OpenWeatherMap**
            - Datos meteorológicos reales
            - Actualización cada 10 minutos
            - Cobertura global
            - Alta precisión
            """)
        else:
            st.warning("""
            **🎲 Fuente de Datos: Simulación**
            - Datos simulados realistas
            - Basados en ubicación geográfica
            - Patrones climáticos típicos
            - Para pruebas y desarrollo
            """)

def create_weather_enhanced_app():
    """Crea una versión mejorada del dashboard con meteorología integrada"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="AIFA - Simulador Avanzado",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal
    st.title("🛬 AIFA - Simulador Avanzado de Rutas")
    st.markdown("### Análisis integral con meteorología en tiempo real")
    
    # Tabs principales (incluyendo nueva pestaña meteorológica)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Simulación", 
        "📊 Datos Históricos", 
        "🎯 Recomendaciones", 
        "📋 Resumen Ejecutivo", 
        "🎰 Slots Aeroportuarios", 
        "🏢 Diagrama Aeropuerto",
        "🌤️ Meteorología"
    ])
    
    # Las primeras 6 pestañas mantienen el código original
    # La séptima pestaña es la nueva funcionalidad meteorológica
    with tab7:
        render_weather_tab()

if __name__ == "__main__":
    create_weather_enhanced_app()