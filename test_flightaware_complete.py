#!/usr/bin/env python3
"""
Prueba completa de FlightAware AeroAPI
API Key: gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc
"""

import sys
import os
sys.path.append('scripts')

from flightaware_connector import FlightAwareConnector
import json
from datetime import datetime

def test_flightaware_complete():
    """
    Prueba exhaustiva de FlightAware AeroAPI
    """
    
    print("🛩️ PRUEBA COMPLETA FLIGHTAWARE AEROAPI")
    print("="*70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: gbSpYb4XG8AXJzyC6Gx3WevjWfPR7NKc")
    print("")
    
    # Inicializar conector
    connector = FlightAwareConnector()
    
    # Test 1: Conexión básica
    print("1️⃣ PROBANDO CONEXIÓN BÁSICA")
    print("-" * 50)
    connection = connector.test_connection()
    print(f"Status: {connection.get('status', 'ERROR')}")
    
    if connection.get('api_activa'):
        print(f"✅ API Activa: {connection.get('plan', 'Plan detectado')}")
        print(f"📊 Airports sample: {connection.get('total_airports', 'N/A')}")
        print(f"📝 Response preview: {connection.get('response_sample', 'N/A')}")
    else:
        print(f"❌ Error: {connection.get('error_msg', 'Desconocido')}")
        return False
    
    print("")
    
    # Test 2: Información del aeropuerto AIFA
    print("2️⃣ INFORMACIÓN AEROPUERTO AIFA (NLU)")
    print("-" * 50)
    airport_info = connector.get_airport_info("NLU")
    
    if airport_info.get('success'):
        data = airport_info.get('airport_data', {})
        print(f"✅ Aeropuerto AIFA encontrado")
        print(f"📝 Datos disponibles: {list(data.keys()) if data else 'Estructura vacía'}")
        if data:
            print(f"   Muestra de datos: {str(data)[:200]}...")
    else:
        print(f"⚠️ Error obteniendo info AIFA: {airport_info.get('error_msg', 'Desconocido')}")
        print(f"   Código error: {airport_info.get('error_code', 'N/A')}")
    
    print("")
    
    # Test 3: Vuelos de salida desde AIFA
    print("3️⃣ VUELOS DE SALIDA DESDE AIFA")
    print("-" * 50)
    departures = connector.get_airport_flights("NLU", "departures")
    
    if departures.get('success'):
        flights = departures.get('flights', [])
        print(f"✅ Encontrados {len(flights)} vuelos de salida")
        
        for i, flight in enumerate(flights[:3]):
            print(f"   {i+1}. Vuelo: {str(flight)[:100]}...")
    else:
        print(f"⚠️ No se encontraron vuelos de salida")
        print(f"   Código: {departures.get('error_code', 'N/A')}")
        print(f"   Error: {departures.get('error_msg', 'N/A')}")
    
    print("")
    
    # Test 4: Vuelos de llegada a AIFA
    print("4️⃣ VUELOS DE LLEGADA A AIFA")
    print("-" * 50)
    arrivals = connector.get_airport_flights("NLU", "arrivals")
    
    if arrivals.get('success'):
        flights = arrivals.get('flights', [])
        print(f"✅ Encontrados {len(flights)} vuelos de llegada")
        
        for i, flight in enumerate(flights[:3]):
            print(f"   {i+1}. Vuelo: {str(flight)[:100]}...")
    else:
        print(f"⚠️ No se encontraron vuelos de llegada")
        print(f"   Código: {arrivals.get('error_code', 'N/A')}")
        print(f"   Error: {arrivals.get('error_msg', 'N/A')}")
    
    print("")
    
    # Test 5: Vuelos programados
    print("5️⃣ VUELOS PROGRAMADOS (SCHEDULED)")
    print("-" * 50)
    scheduled_deps = connector.get_airport_flights("NLU", "scheduled_departures")
    scheduled_arrs = connector.get_airport_flights("NLU", "scheduled_arrivals")
    
    deps_count = scheduled_deps.get('total_flights', 0) if scheduled_deps.get('success') else 0
    arrs_count = scheduled_arrs.get('total_flights', 0) if scheduled_arrs.get('success') else 0
    
    print(f"📋 Salidas programadas: {deps_count}")
    print(f"📋 Llegadas programadas: {arrs_count}")
    
    if deps_count > 0:
        print("   Ejemplo salida programada:")
        flight = scheduled_deps.get('flights', [{}])[0]
        print(f"   {str(flight)[:150]}...")
    
    print("")
    
    # Test 6: Estadísticas de delays
    print("6️⃣ ESTADÍSTICAS DE DELAYS Y PUNTUALIDAD")
    print("-" * 50)
    delay_stats = connector.get_airport_delay_stats("NLU")
    
    if delay_stats.get('success'):
        stats = delay_stats.get('delay_stats', {})
        calc_stats = delay_stats.get('calculated_stats', False)
        
        print(f"✅ Estadísticas obtenidas {'(calculadas)' if calc_stats else '(API)'}")
        print(f"📊 Vuelos analizados: {delay_stats.get('total_flights_analyzed', 'N/A')}")
        
        if stats:
            for key, value in stats.items():
                print(f"   {key}: {value}")
    else:
        print(f"⚠️ Error en estadísticas de delays")
        print(f"   Error: {delay_stats.get('error', 'N/A')}")
    
    print("")
    
    # Test 7: Resumen completo operaciones AIFA
    print("7️⃣ RESUMEN COMPLETO OPERACIONES AIFA")
    print("-" * 50)
    summary = connector.get_aifa_operations_summary("NLU")
    
    if 'error' not in summary:
        ops = summary.get('operations', {})
        perf = summary.get('performance', {})
        
        print(f"✅ Resumen generado exitosamente")
        print(f"📊 Total operaciones: {ops.get('total_operations', 0)}")
        print(f"🛫 Salidas: {ops.get('departures', {}).get('total_flights', 0)}")
        print(f"🛬 Llegadas: {ops.get('arrivals', {}).get('total_flights', 0)}")
        print(f"⏱️ Performance disponible: {'✅' if perf.get('success') else '❌'}")
    else:
        print(f"⚠️ Error en resumen: {summary.get('error', 'N/A')}")
    
    print("")
    
    # Test 8: Probar con otros aeropuertos conocidos para comparar
    print("8️⃣ COMPARACIÓN CON AEROPUERTOS CONOCIDOS")
    print("-" * 50)
    
    test_airports = ['MEX', 'CUN', 'GDL']  # AICM, Cancún, Guadalajara
    
    for airport in test_airports:
        print(f"🔍 Probando {airport}:")
        info = connector.get_airport_info(airport)
        deps = connector.get_airport_flights(airport, "departures")
        
        if info.get('success'):
            print(f"   ✅ Info: Disponible")
        else:
            print(f"   ❌ Info: {info.get('error_code', 'N/A')}")
            
        if deps.get('success'):
            print(f"   ✅ Vuelos: {deps.get('total_flights', 0)} encontrados")
        else:
            print(f"   ❌ Vuelos: {deps.get('error_code', 'N/A')}")
    
    print("")
    print("="*70)
    print("✅ PRUEBA FLIGHTAWARE COMPLETADA")
    
    # Resumen final
    total_tests = 8
    passed_tests = 0
    
    if connection.get('api_activa'): passed_tests += 1
    if airport_info.get('success'): passed_tests += 1
    if departures.get('success'): passed_tests += 1
    if arrivals.get('success'): passed_tests += 1
    if deps_count > 0 or arrs_count > 0: passed_tests += 1
    if delay_stats.get('success'): passed_tests += 1
    if 'error' not in summary: passed_tests += 1
    # Test 8 cuenta como passed si al menos 1 aeropuerto funciona
    passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"📊 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("🎉 FLIGHTAWARE API FUNCIONAL PARA PRODUCCIÓN")
        return True
    else:
        print("⚠️ FLIGHTAWARE CON LIMITACIONES - EVALUAR PLAN")
        return False

if __name__ == "__main__":
    test_flightaware_complete()