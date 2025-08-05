#!/usr/bin/env python3
"""
Prueba completa de AviationStack API con endpoints reales
Usando API key activa: 59f5d7300a3c8236dc29e095fa6ab923
"""

import sys
import os
sys.path.append('scripts')

from real_data_connector import AviationStackConnector
import json
from datetime import datetime

def test_aviationstack_complete():
    """
    Prueba completa de todos los endpoints de AviationStack
    """
    
    print("🧪 PRUEBA COMPLETA AVIATIONSTACK API")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: 59f5d7300a3c8236dc29e095fa6ab923")
    print("")
    
    # Inicializar conector
    connector = AviationStackConnector()
    
    # Test 1: Conexión básica
    print("1️⃣ PROBANDO CONEXIÓN BÁSICA")
    print("-" * 40)
    connection = connector.test_connection()
    print(f"Status: {connection.get('status', 'ERROR')}")
    if connection.get('api_activa'):
        print(f"✅ API Activa: {connection['requests_disponibles']}")
        print(f"📊 Total aeropuertos: {connection.get('total_aeropuertos', 'N/A')}")
    else:
        print(f"❌ Error: {connection.get('error_msg', 'Desconocido')}")
        return False
    
    print("")
    
    # Test 2: Información del aeropuerto AIFA
    print("2️⃣ INFORMACIÓN AEROPUERTO AIFA (NLU)")
    print("-" * 40)
    airport_info = connector.get_airport_info("NLU")
    
    if 'error' not in airport_info:
        print(f"✅ Aeropuerto: {airport_info['nombre']}")
        print(f"📍 IATA: {airport_info['iata']} | ICAO: {airport_info['icao']}")
        print(f"🌍 Coordenadas: {airport_info['latitud']}, {airport_info['longitud']}")
        print(f"🏙️ Ciudad: {airport_info['ciudad']} | País: {airport_info['pais']}")
        print(f"⏰ Zona horaria: {airport_info['zona_horaria']}")
    else:
        print(f"⚠️ Error obteniendo info aeropuerto: {airport_info['error']}")
    
    print("")
    
    # Test 3: Vuelos de salida AIFA
    print("3️⃣ VUELOS SALIDA DESDE AIFA")
    print("-" * 40)
    departures = connector.get_real_flights("NLU", "departure", 10)
    
    if departures.get('success'):
        flights = departures.get('flights', [])
        print(f"✅ Encontrados {len(flights)} vuelos de salida")
        
        for i, flight in enumerate(flights[:3]):
            flight_num = flight.get('flight', {}).get('iata', 'N/A')
            airline = flight.get('airline', {}).get('name', 'N/A')
            destination = flight.get('arrival', {}).get('airport', 'N/A')
            status = flight.get('flight_status', 'N/A')
            
            print(f"   {i+1}. {flight_num} ({airline}) → {destination} [{status}]")
            
    else:
        print(f"⚠️ No se encontraron vuelos de salida")
        print(f"   Código: {departures.get('error_code', 'N/A')}")
    
    print("")
    
    # Test 4: Vuelos de llegada AIFA  
    print("4️⃣ VUELOS LLEGADA A AIFA")
    print("-" * 40)
    arrivals = connector.get_real_flights("NLU", "arrival", 10)
    
    if arrivals.get('success'):
        flights = arrivals.get('flights', [])
        print(f"✅ Encontrados {len(flights)} vuelos de llegada")
        
        for i, flight in enumerate(flights[:3]):
            flight_num = flight.get('flight', {}).get('iata', 'N/A')
            airline = flight.get('airline', {}).get('name', 'N/A')
            origin = flight.get('departure', {}).get('airport', 'N/A')
            status = flight.get('flight_status', 'N/A')
            
            print(f"   {i+1}. {flight_num} ({airline}) ← {origin} [{status}]")
            
    else:
        print(f"⚠️ No se encontraron vuelos de llegada")
        print(f"   Código: {arrivals.get('error_code', 'N/A')}")
    
    print("")
    
    # Test 5: Resumen completo de vuelos
    print("5️⃣ RESUMEN OPERACIONES AIFA")
    print("-" * 40)
    summary = connector.get_flights_summary("NLU")
    
    if summary.get('precision') == 'REAL':
        print(f"✅ Datos REALES obtenidos de AviationStack")
        print(f"📊 Total operaciones: {summary['total_operaciones_dia']}")
        print(f"🛫 Salidas: {summary['salidas_reales']}")  
        print(f"🛬 Llegadas: {summary['llegadas_reales']}")
        print(f"🎯 Destinos principales: {', '.join(summary['principales_destinos'])}")
        print(f"✈️ Aerolíneas activas: {', '.join(summary['aerolineas_activas'])}")
    else:
        print(f"⚠️ Usando datos simulados")
        print(f"📊 Operaciones estimadas: {summary.get('total_operaciones_estimadas_dia', 'N/A')}")
        print(f"📝 Nota: {summary.get('nota', 'N/A')}")
    
    print("")
    
    # Test 6: Estadísticas completas del aeropuerto
    print("6️⃣ ESTADÍSTICAS COMPLETAS AIFA")  
    print("-" * 40)
    stats = connector.get_airport_statistics("NLU")
    
    if 'error' not in stats:
        print(f"✅ Estadísticas generadas exitosamente")
        activity = stats.get('actividad_reciente', {})
        print(f"📈 Actividad reciente:")
        print(f"   Salidas encontradas: {activity.get('salidas_encontradas', 0)}")
        print(f"   Llegadas encontradas: {activity.get('llegadas_encontradas', 0)}")
        print(f"   Success rate: {activity.get('success_rate', 'N/A')}")
    else:
        print(f"⚠️ Error en estadísticas: {stats.get('error', 'N/A')}")
    
    print("")
    print("="*60)
    print("✅ PRUEBA AVIATIONSTACK COMPLETADA")
    
    # Resumen final
    total_tests = 6
    passed_tests = 0
    
    if connection.get('api_activa'): passed_tests += 1
    if 'error' not in airport_info: passed_tests += 1  
    if departures.get('success'): passed_tests += 1
    if arrivals.get('success'): passed_tests += 1
    if summary.get('precision') == 'REAL': passed_tests += 1
    if 'error' not in stats: passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"📊 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 50:
        print("🎉 API AVIATIONSTACK FUNCIONAL PARA PRODUCCIÓN")
        return True
    else:
        print("⚠️ API CON LIMITACIONES - USAR FALLBACKS")
        return False

if __name__ == "__main__":
    test_aviationstack_complete()