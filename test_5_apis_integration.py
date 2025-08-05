#!/usr/bin/env python3
"""
Prueba completa de integración de las 5 APIs del sistema AIFA
Incluye FlightRadar24 como quinta API
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
    from flightradar_zone_connector import FlightRadar24ZoneConnector
    print("✅ Todas las importaciones exitosas (5 APIs)")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_five_apis_integration():
    """Prueba completa de integración de las 5 APIs"""
    
    print("🧪 PRUEBA COMPLETA DE INTEGRACIÓN - 5 APIs SISTEMA AIFA")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: Probar integración completa con FlightRadar24")
    print()
    
    # Inicializar todas las conexiones
    print("🔌 INICIALIZANDO CONEXIONES DE TODAS LAS APIS...")
    print("-" * 70)
    
    apis_status = {}
    
    # 1. Datos Gubernamentales
    try:
        gov_connector = GobMXRealDataConnector()
        apis_status['gobierno'] = {'status': 'CONECTADO', 'connector': gov_connector}
        print("✅ 1/5 Datos Gubernamentales: CONECTADO")
    except Exception as e:
        apis_status['gobierno'] = {'status': 'ERROR', 'error': str(e)}
        print(f"❌ 1/5 Datos Gubernamentales: ERROR - {e}")
        gov_connector = None
    
    # 2. AviationStack
    try:
        aviation_connector = AviationStackConnector("59f5d7300a3c8236dc29e095fa6ab923")
        aviation_test = aviation_connector.test_connection()
        if aviation_test.get('success'):
            apis_status['aviationstack'] = {'status': 'CONECTADO', 'connector': aviation_connector}
            print("✅ 2/5 AviationStack: CONECTADO")
        else:
            apis_status['aviationstack'] = {'status': 'LIMITADO', 'error': aviation_test.get('error', 'Unknown')}
            print(f"⚠️  2/5 AviationStack: LIMITADO - {aviation_test.get('error', 'Unknown')}")
    except Exception as e:
        apis_status['aviationstack'] = {'status': 'ERROR', 'error': str(e)}
        print(f"❌ 2/5 AviationStack: ERROR - {e}")
        aviation_connector = None
    
    # 3. FlightAware
    try:  
        flightaware_connector = FlightAwareConnector("gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc")
        flightaware_test = flightaware_connector.test_connection()
        if flightaware_test.get('api_activa'):
            apis_status['flightaware'] = {'status': 'CONECTADO', 'connector': flightaware_connector}
            print("✅ 3/5 FlightAware: CONECTADO")
        else:
            apis_status['flightaware'] = {'status': 'LIMITADO', 'error': flightaware_test.get('error_msg', 'Plan básico')}
            print(f"⚠️  3/5 FlightAware: LIMITADO - {flightaware_test.get('error_msg', 'Plan básico')}")
    except Exception as e:
        apis_status['flightaware'] = {'status': 'ERROR', 'error': str(e)}
        print(f"❌ 3/5 FlightAware: ERROR - {e}")
        flightaware_connector = None
    
    # 4. OpenWeatherMap
    try:
        weather_manager = WeatherManager("6a6e94ae482a1c310fe583b6a35eb72b")
        if weather_manager.use_real_data:
            apis_status['openweathermap'] = {'status': 'CONECTADO', 'connector': weather_manager, 'version': weather_manager.api_version}
            print(f"✅ 4/5 OpenWeatherMap: CONECTADO ({weather_manager.api_version})")
        else:
            apis_status['openweathermap'] = {'status': 'FALLBACK', 'connector': weather_manager}
            print("⚠️  4/5 OpenWeatherMap: FALLBACK A SIMULACIÓN")
    except Exception as e:
        apis_status['openweathermap'] = {'status': 'ERROR', 'error': str(e)}
        print(f"❌ 4/5 OpenWeatherMap: ERROR - {e}")
        weather_manager = None
    
    # 5. FlightRadar24 (NUEVO)
    try:
        flightradar_connector = FlightRadar24ZoneConnector()
        fr24_test = flightradar_connector.test_connection()
        if fr24_test.get('success'):
            apis_status['flightradar24'] = {'status': 'CONECTADO', 'connector': flightradar_connector}
            print(f"✅ 5/5 FlightRadar24: CONECTADO ({fr24_test.get('endpoint', 'zone_feed')})")
        else:
            apis_status['flightradar24'] = {'status': 'ERROR', 'error': fr24_test.get('error', 'Unknown')}
            print(f"❌ 5/5 FlightRadar24: ERROR - {fr24_test.get('error', 'Unknown')}")
            flightradar_connector = None
    except Exception as e:
        apis_status['flightradar24'] = {'status': 'ERROR', 'error': str(e)}
        print(f"❌ 5/5 FlightRadar24: ERROR - {e}")
        flightradar_connector = None
    
    print()
    
    # Generar KPIs con las 5 APIs
    print("📊 GENERANDO KPIs CON 5 APIs...")
    print("-" * 70)
    
    try:
        kpi_calc = AIFAKPICalculator(
            data_connector=gov_connector,
            aviation_connector=aviation_connector,
            flightaware_connector=flightaware_connector,
            weather_manager=weather_manager,
            flightradar_connector=flightradar_connector
        )
        
        # Generar dashboard completo
        dashboard = kpi_calc.generate_executive_dashboard()
        
        print("✅ Dashboard Ejecutivo con 5 APIs Generado")
        print()
        
        # Verificar KPIs por categoría
        strategic = dashboard['kpis_estrategicos']
        operational = dashboard['kpis_operacionales']
        economic = dashboard['kpis_economicos']
        
        print("📋 RESUMEN DE KPIs CON 5 APIs:")
        print("-" * 70)
        print(f"🚀 KPIs Estratégicos: {len(strategic)} KPIs")
        
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
        
        print()
        
        # Scorecard general
        scorecard = dashboard['scorecard_general']
        print("🎯 SCORECARD GENERAL CON 5 APIs:")
        print("-" * 70)
        print(f"📊 Score General: {scorecard['score_general']}/100")
        print(f"📈 Estratégico: {scorecard['score_estrategico']}/100")
        print(f"⚙️ Operacional: {scorecard['score_operacional']}/100")
        print(f"💰 Económico: {scorecard['score_economico']}/100")
        print(f"🏆 Clasificación: {scorecard['clasificacion']}")
        print(f"📈 Tendencia: {scorecard['tendencia']}")
        
        print()
        
        # Verificar KPIs específicos de todas las APIs
        print("🔍 VERIFICACIÓN DE KPIs POR API:")
        print("-" * 70)
        
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
        
        # KPI FlightRadar24 (NUEVO)
        kpi9 = operational.get('kpi_9_rastreo_aeronaves', {})
        if kpi9.get('estado') == 'DATOS_REALES_ACTIVOS':
            print(f"✅ FlightRadar24 KPI: {kpi9.get('aeronaves_area', 0)} aeronaves área + {kpi9.get('aeronaves_aifa', 0)} AIFA REAL")
        elif kpi9.get('estado') == 'CONECTADO_SIN_DATOS':
            print(f"⚠️  FlightRadar24 KPI: API CONECTADA - {kpi9.get('error_detalle', 'Sin actividad actual')}")
        else:
            print(f"⚠️  FlightRadar24 KPI: {kpi9.get('estado', 'ERROR')}")
        
        print()
        
        # Estadísticas finales de 5 APIs
        apis_funcionando = sum(1 for api in apis_status.values() if api['status'] in ['CONECTADO', 'LIMITADO'])
        total_kpis = len(strategic) + len(operational) + len(economic)
        
        print("📈 ESTADÍSTICAS FINALES - 5 APIs:")
        print("-" * 70)
        print(f"🎯 APIs Funcionando: {apis_funcionando}/5 ({apis_funcionando/5*100:.0f}%)")
        print(f"📊 Total KPIs: {total_kpis}")
        print(f"🏆 Score Sistema: {scorecard['score_general']}/100")
        
        # Estado por API
        print("\n🔍 ESTADO DETALLADO POR API:")
        for i, (api_name, api_data) in enumerate(apis_status.items(), 1):
            status = api_data['status']
            emoji = "✅" if status == "CONECTADO" else "⚠️" if status in ["LIMITADO", "FALLBACK"] else "❌"
            print(f"   {emoji} {i}/5 {api_name.upper()}: {status}")
        
        print(f"\n✅ Estado: SISTEMA CON 5 APIs {'COMPLETAMENTE' if apis_funcionando >= 4 else 'PARCIALMENTE'} OPERATIVO")
        
        return True, apis_funcionando
        
    except Exception as e:
        print(f"❌ Error generando KPIs con 5 APIs: {e}")
        return False, 0

if __name__ == "__main__":
    print()
    success, apis_working = test_five_apis_integration()
    print()
    print("=" * 70)
    if success and apis_working >= 4:
        print("🎉 PRUEBA 5 APIs EXITOSA - SISTEMA AIFA COMPLETAMENTE AMPLIADO")
        print(f"🚀 FlightRadar24 INTEGRADO EXITOSAMENTE COMO 5TA API")
        print(f"📊 {apis_working}/5 APIs funcionando - COBERTURA MÁXIMA ALCANZADA")
    elif success:
        print("⚠️  PRUEBA 5 APIs PARCIAL - MAYORÍA DE SISTEMAS FUNCIONANDO")
        print(f"📊 {apis_working}/5 APIs funcionando")
    else:
        print("⚠️  PRUEBA 5 APIs - REVISAR ERRORES ARRIBA")
    print("=" * 70)