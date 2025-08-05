#!/usr/bin/env python3
"""
FlightRadar24 Zone Feed Connector
Integración específica con el endpoint que funciona: Zone Feed
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

class FlightRadar24ZoneConnector:
    """
    Conector específico para FlightRadar24 Zone Feed
    Usa el endpoint que confirmamos que funciona
    """
    
    def __init__(self, api_key: str = "01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb"):
        self.api_key = api_key
        self.base_url = "https://data-live.flightradar24.com/zones/fcgi/feed.js"
        
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'AIFA-Simulator/1.0'
        }
        
        # Coordenadas para diferentes áreas de México
        self.mexico_zones = {
            'aifa_area': {'bounds': '20.5,-98.5,19.0,-99.5', 'name': 'Área AIFA'},
            'cdmx_area': {'bounds': '20.0,-98.5,19.0,-99.5', 'name': 'Ciudad de México'},  
            'mexico_center': {'bounds': '25,-95,15,-105', 'name': 'México Central'},
            'mexico_full': {'bounds': '33,-86,14,-118', 'name': 'México Completo'}
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def test_connection(self) -> Dict[str, Any]:
        """Prueba la conexión con el endpoint que funciona"""
        try:
            params = {
                'bounds': self.mexico_zones['aifa_area']['bounds'],
                'faa': '1',
                'satellite': '1', 
                'mlat': '1',
                'flarm': '1'
            }
            
            start_time = time.time()
            response = self.session.get(self.base_url, params=params, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'success': True,
                        'status': 'CONECTADO',
                        'api_active': True,
                        'response_time_ms': response_time,
                        'endpoint': 'zone_feed',
                        'data_structure': {
                            'aircraft_count': len(data.get('aircraft', {})),
                            'full_count': data.get('full_count', 0),
                            'version': data.get('version', 'N/A'),
                            'keys': list(data.keys())
                        },
                        'zone_tested': self.mexico_zones['aifa_area']['name'],
                        'message': 'FlightRadar24 Zone Feed funcionando correctamente'
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'status': 'JSON_ERROR',
                        'error': 'Respuesta no es JSON válido',
                        'raw_response': response.text[:200]
                    }
            else:
                return {
                    'success': False,
                    'status': f'HTTP_{response.status_code}',
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'response_time_ms': response_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def get_flights_in_area(self, zone: str = 'aifa_area') -> Dict[str, Any]:
        """Obtiene vuelos en una zona específica"""
        try:
            if zone not in self.mexico_zones:
                return {
                    'success': False,
                    'error': f'Zona {zone} no definida. Disponibles: {list(self.mexico_zones.keys())}'
                }
            
            zone_config = self.mexico_zones[zone]
            params = {
                'bounds': zone_config['bounds'],
                'faa': '1',
                'satellite': '1',
                'mlat': '1', 
                'flarm': '1'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                aircraft_data = data.get('aircraft', {})
                
                # Procesar datos de aeronaves
                processed_flights = []
                aifa_related_flights = []
                
                # Manejar diferentes estructuras de datos
                if isinstance(aircraft_data, dict):
                    # Formato diccionario {flight_id: flight_info}
                    aircraft_items = aircraft_data.items()
                elif isinstance(aircraft_data, list):
                    # Formato lista de aeronaves
                    aircraft_items = enumerate(aircraft_data)
                else:
                    # Sin datos de aeronaves
                    aircraft_items = []
                
                for flight_id, flight_info in aircraft_items:
                    try:
                        # flight_info es típicamente una lista con datos de la aeronave
                        if isinstance(flight_info, list) and len(flight_info) >= 8:
                            flight_data = {
                                'flight_id': flight_id,
                                'callsign': flight_info[1] if len(flight_info) > 1 else 'N/A',
                                'latitude': flight_info[2] if len(flight_info) > 2 else 0,
                                'longitude': flight_info[3] if len(flight_info) > 3 else 0,
                                'heading': flight_info[4] if len(flight_info) > 4 else 0,
                                'altitude': flight_info[5] if len(flight_info) > 5 else 0,
                                'speed': flight_info[6] if len(flight_info) > 6 else 0,
                                'aircraft_type': flight_info[8] if len(flight_info) > 8 else 'N/A',
                                'origin': flight_info[11] if len(flight_info) > 11 else 'N/A',
                                'destination': flight_info[12] if len(flight_info) > 12 else 'N/A',
                                'airline': flight_info[13] if len(flight_info) > 13 else 'N/A'
                            }
                            
                            processed_flights.append(flight_data)
                            
                            # Detectar vuelos relacionados con AIFA
                            if self._is_aifa_related(flight_data):
                                aifa_related_flights.append(flight_data)
                                
                    except Exception as e:
                        print(f"Error procesando vuelo {flight_id}: {e}")
                        continue
                
                return {
                    'success': True,
                    'zone': zone_config['name'],
                    'bounds': zone_config['bounds'],
                    'total_aircraft': len(processed_flights),
                    'aifa_related': len(aifa_related_flights),
                    'full_count': data.get('full_count', 0),
                    'version': data.get('version', 'N/A'),
                    'flights': processed_flights,
                    'aifa_flights': aifa_related_flights,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'flightradar24_zone_feed',
                    'debug_info': {
                        'raw_data_keys': list(data.keys()),
                        'aircraft_data_type': type(aircraft_data).__name__,
                        'aircraft_data_length': len(aircraft_data) if hasattr(aircraft_data, '__len__') else 'N/A',
                        'aircraft_sample': str(aircraft_data)[:200] if aircraft_data else 'Empty'
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_aifa_related(self, flight_data: Dict) -> bool:
        """Determina si un vuelo está relacionado con AIFA"""
        aifa_indicators = ['NLU', 'MMSM', 'AIFA', 'FELIPE ANGELES', 'SANTA LUCIA']
        
        # Buscar en origen, destino, callsign
        search_fields = [
            flight_data.get('origin', ''),
            flight_data.get('destination', ''),
            flight_data.get('callsign', '')
        ]
        
        for field in search_fields:
            if field and any(indicator in str(field).upper() for indicator in aifa_indicators):
                return True
        
        # También verificar proximidad geográfica (coordenadas cerca de AIFA)
        lat = flight_data.get('latitude', 0)
        lon = flight_data.get('longitude', 0)
        
        if lat and lon:
            # AIFA está en 19.7425, -99.0157
            aifa_lat, aifa_lon = 19.7425, -99.0157
            
            # Si está dentro de ~20km de AIFA
            lat_diff = abs(lat - aifa_lat)
            lon_diff = abs(lon - aifa_lon)
            
            if lat_diff < 0.2 and lon_diff < 0.2:  # Aproximadamente 20km
                return True
        
        return False
    
    def get_aifa_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen específico de actividad AIFA"""
        try:
            # Obtener datos del área AIFA
            aifa_data = self.get_flights_in_area('aifa_area')
            
            if not aifa_data['success']:
                return aifa_data
            
            # Análisis específico para AIFA
            flights = aifa_data.get('flights', [])
            aifa_flights = aifa_data.get('aifa_flights', [])
            
            # Clasificar vuelos AIFA
            departures = []
            arrivals = []
            overflights = []
            
            for flight in aifa_flights:
                origin = str(flight.get('origin', '')).upper()
                destination = str(flight.get('destination', '')).upper()
                
                if 'NLU' in origin or 'MMSM' in origin:
                    departures.append(flight)
                elif 'NLU' in destination or 'MMSM' in destination:
                    arrivals.append(flight)
                else:
                    # Vuelo que pasa cerca de AIFA
                    overflights.append(flight)
            
            # Estadísticas de aerolíneas
            airlines = {}
            for flight in aifa_flights:
                airline = flight.get('airline', 'Unknown')
                if airline and airline != 'N/A':
                    airlines[airline] = airlines.get(airline, 0) + 1
            
            return {
                'success': True,
                'summary': {
                    'total_area_aircraft': len(flights),
                    'aifa_related_aircraft': len(aifa_flights),
                    'departures': len(departures),
                    'arrivals': len(arrivals),
                    'overflights': len(overflights)
                },
                'airlines_operating': airlines,
                'departure_flights': departures,
                'arrival_flights': arrivals,
                'overflight_aircraft': overflights,
                'data_freshness': aifa_data.get('timestamp'),
                'zone_coverage': aifa_data.get('zone'),
                'source': 'flightradar24_zone_feed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def test_flightradar_zone_connector():
    """Prueba el conector de zone feed"""
    print("🛩️ PRUEBA FLIGHTRADAR24 ZONE CONNECTOR")
    print("=" * 60) 
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Sandbox Token: 01987b9a-a8d6-...b45572fb")
    print(f"🌐 Endpoint: Zone Feed (confirmado funcionando)")
    print()
    
    # Inicializar conector
    fr24_zone = FlightRadar24ZoneConnector()
    
    # 1. Prueba de conexión
    print("1️⃣ PRUEBA DE CONEXIÓN")
    print("-" * 40)
    
    connection = fr24_zone.test_connection()
    
    if connection['success']:
        print(f"✅ Estado: {connection['status']}")
        print(f"⚡ Tiempo respuesta: {connection['response_time_ms']:.0f}ms")
        print(f"🛩️ Aeronaves detectadas: {connection['data_structure']['aircraft_count']}")
        print(f"📊 Conteo total: {connection['data_structure']['full_count']}")
        print(f"🔖 Versión API: {connection['data_structure']['version']}")
        print(f"🗂️ Estructura: {connection['data_structure']['keys']}")
    else:
        print(f"❌ Error: {connection['error']}")
        return False
    
    print()
    
    # 2. Obtener vuelos en área AIFA
    print("2️⃣ ANÁLISIS ÁREA AIFA")
    print("-" * 40)
    
    aifa_data = fr24_zone.get_flights_in_area('aifa_area')
    
    if aifa_data['success']:
        print(f"📍 Zona: {aifa_data['zone']}")
        print(f"🗺️ Coordenadas: {aifa_data['bounds']}")
        print(f"✈️ Total aeronaves: {aifa_data['total_aircraft']}")
        print(f"🎯 Relacionadas AIFA: {aifa_data['aifa_related']}")
        
        # Mostrar algunos vuelos si los hay
        if aifa_data['aifa_flights']:
            print(f"🛩️ Vuelos AIFA detectados:")
            for i, flight in enumerate(aifa_data['aifa_flights'][:3], 1):
                print(f"   {i}. {flight['callsign']} - {flight['origin']} → {flight['destination']}")
                print(f"      Alt: {flight['altitude']}ft, Vel: {flight['speed']}kt")
    else:
        print(f"❌ Error: {aifa_data['error']}")
        return False
    
    print()
    
    # 3. Resumen AIFA
    print("3️⃣ RESUMEN AIFA ESPECÍFICO")
    print("-" * 40)
    
    summary = fr24_zone.get_aifa_summary()
    
    if summary['success']:
        stats = summary['summary']
        print(f"📊 Aeronaves en área: {stats['total_area_aircraft']}")
        print(f"🎯 Relacionadas AIFA: {stats['aifa_related_aircraft']}")
        print(f"🛫 Salidas: {stats['departures']}")
        print(f"🛬 Llegadas: {stats['arrivals']}")
        print(f"🔄 Sobrevuelos: {stats['overflights']}")
        
        airlines = summary.get('airlines_operating', {})
        if airlines:
            print(f"✈️ Aerolíneas activas: {list(airlines.keys())}")
        
    else:
        print(f"❌ Error: {summary['error']}")
    
    print()
    print("=" * 60)
    print("✅ FLIGHTRADAR24 ZONE CONNECTOR FUNCIONANDO")
    print("🚀 Listo para integrar al sistema AIFA")
    
    return True

if __name__ == "__main__":
    test_flightradar_zone_connector()