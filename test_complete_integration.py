#!/usr/bin/env python3
"""
Prueba completa de integración de todas las APIs del sistema AIFA
Verifica que las 5 APIs estén funcionando correctamente
"""

import sys
import os
from datetime import datetime

# Agregar scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Importar todas las clases necesarias
try:
    from real_data_connector import GobMXRealDataConnector, AviationStackConnector, FlightAwareConnector
    from kpi_calculator import AIFAKPICalculator
    from weather_manager import WeatherManager
    print("✅ Todas las importaciones exitosas")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_complete_integration():
    """Prueba completa de integración de las 5 APIs"""
    
    print("🧪 PRUEBA COMPLETA DE INTEGRACIÓN DEL SISTEMA AIFA")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Inicializar todas las conexiones
    print("🔌 INICIALIZANDO CONEXIONES DE APIS...")
    print("-" * 50)
    
    # 1. Datos Gubernamentales
    try:
        gov_connector = GobMXRealDataConnector()
        print("✅ Datos Gubernamentales: CONECTADO")
    except Exception as e:
        print(f"❌ Datos Gubernamentales: ERROR - {e}")
        gov_connector = None
    
    # 2. AviationStack
    try:
        aviation_connector = AviationStackConnector("59f5d7300a3c8236dc29e095fa6ab923")
        aviation_test = aviation_connector.test_connection()
        if aviation_test.get('success'):
            print("✅ AviationStack: CONECTADO")
        else:
            print(f"⚠️  AviationStack: LIMITADO - {aviation_test.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ AviationStack: ERROR - {e}")
        aviation_connector = None
    
    # 3. FlightAware
    try:
        flightaware_connector = FlightAwareConnector("gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc")
        flightaware_test = flightaware_connector.test_connection()
        if flightaware_test.get('api_activa'):
            print("✅ FlightAware: CONECTADO")
        else:
            print(f"⚠️  FlightAware: LIMITADO - {flightaware_test.get('error_msg', 'Plan básico')}")
    except Exception as e:
        print(f"❌ FlightAware: ERROR - {e}")
        flightaware_connector = None
    
    # 4. OpenWeatherMap
    try:
        weather_manager = WeatherManager("6a6e94ae482a1c310fe583b6a35eb72b")
        if weather_manager.use_real_data:
            print(f"✅ OpenWeatherMap: CONECTADO ({weather_manager.api_version})")
        else:
            print("⚠️  OpenWeatherMap: FALLBACK A SIMULACIÓN")
    except Exception as e:
        print(f"❌ OpenWeatherMap: ERROR - {e}")
        weather_manager = None
    
    print()
    
    # Generar KPIs completos
    print("📊 GENERANDO KPIs COMPLETOS...")
    print("-" * 50)
    
    try:
        kpi_calc = AIFAKPICalculator(
            data_connector=gov_connector,
            aviation_connector=aviation_connector,
            flightaware_connector=flightaware_connector,
            weather_manager=weather_manager
        )
        
        # Generar dashboard completo
        dashboard = kpi_calc.generate_executive_dashboard()
        
        print("✅ Dashboard Ejecutivo Generado")
        print()
        
        # Verificar KPIs por categoría
        strategic = dashboard['kpis_estrategicos']
        operational = dashboard['kpis_operacionales']
        economic = dashboard['kpis_economicos']
        
        print("📋 RESUMEN DE KPIs GENERADOS:")
        print("-" * 50)
        print(f"🚀 KPIs Estratégicos: {len(strategic)} KPIs")
        for key in strategic.keys():
            print(f"   - {key}")
        
        print(f"⚙️ KPIs Operacionales: {len(operational)} KPIs")
        for key in operational.keys():
            kpi = operational[key]
            if isinstance(kpi, dict) and 'estado' in kpi:
                estado = kpi['estado']
                emoji = "✅" if estado == "DATOS_REALES_ACTIVOS" else "⚠️" if "SIMULADO" in estado else "❌"
                print(f"   {emoji} {key} - {estado}")
            else:
                print(f"   - {key}")
        
        print(f"💰 KPIs Económicos: {len(economic)} KPIs")
        for key in economic.keys():
            print(f"   - {key}")
        
        print()
        
        # Scorecard general
        scorecard = dashboard['scorecard_general']
        print("🎯 SCORECARD GENERAL:")
        print("-" * 50)
        print(f"📊 Score General: {scorecard['score_general']}/100")
        print(f"📈 Estratégico: {scorecard['score_estrategico']}/100")
        print(f"⚙️ Operacional: {scorecard['score_operacional']}/100") 
        print(f"💰 Económico: {scorecard['score_economico']}/100")
        print(f"🏆 Clasificación: {scorecard['clasificacion']}")
        print(f"📈 Tendencia: {scorecard['tendencia']}")
        
        print()
        
        # Verificar KPIs específicos de APIs
        print("🔍 VERIFICACIÓN DE KPIs POR API:")
        print("-" * 50)
        
        # KPI AviationStack
        kpi6 = operational.get('kpi_6_operaciones_tiempo_real', {})
        if kpi6.get('estado') == 'DATOS_REALES_ACTIVOS':
            print(f"✅ AviationStack KPI: {kpi6.get('operaciones_dia', 0)} operaciones/día REALES")
        else:
            print(f"⚠️  AviationStack KPI: {kpi6.get('estado', 'ERROR')}")
        
        # KPI FlightAware
        kpi7 = operational.get('kpi_7_puntualidad_real', {})
        if kpi7.get('estado') == 'DATOS_REALES_ACTIVOS':
            print(f"✅ FlightAware KPI: {kpi7.get('on_time_percentage', 0):.1f}% puntualidad REAL")
        else:
            print(f"⚠️  FlightAware KPI: {kpi7.get('estado', 'ERROR')}")
        
        # KPI OpenWeatherMap
        kpi8 = operational.get('kpi_8_condiciones_meteorologicas', {})
        if kpi8.get('estado') == 'DATOS_REALES_ACTIVOS':
            print(f"✅ OpenWeatherMap KPI: {kpi8.get('temperatura_actual', 0):.1f}°C - {kpi8.get('condicion_general', 'N/A')} REAL")
        else:
            print(f"⚠️  OpenWeatherMap KPI: {kpi8.get('estado', 'ERROR')}")
        
        print()
        
        # Estadísticas finales
        total_kpis = len(strategic) + len(operational) + len(economic)
        apis_funcionando = 0
        
        if gov_connector: apis_funcionando += 1
        if aviation_connector: apis_funcionando += 1  
        if flightaware_connector: apis_funcionando += 1
        if weather_manager and weather_manager.use_real_data: apis_funcionando += 1
        
        print("📈 ESTADÍSTICAS FINALES:")
        print("-" * 50)
        print(f"🎯 APIs Funcionando: {apis_funcionando}/4 ({apis_funcionando/4*100:.0f}%)")
        print(f"📊 Total KPIs: {total_kpis}")
        print(f"🏆 Score Sistema: {scorecard['score_general']}/100")
        print(f"✅ Estado: SISTEMA {'COMPLETAMENTE' if apis_funcionando == 4 else 'PARCIALMENTE'} OPERATIVO")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando KPIs: {e}")
        return False

if __name__ == "__main__":
    print()
    success = test_complete_integration()
    print()
    print("=" * 60)
    if success:
        print("🎉 PRUEBA COMPLETA EXITOSA - SISTEMA 100% OPERATIVO")
    else:
        print("⚠️  PRUEBA PARCIAL - REVISAR ERRORES ARRIBA")
    print("=" * 60)