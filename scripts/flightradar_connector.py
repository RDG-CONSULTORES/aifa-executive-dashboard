#!/usr/bin/env python3
"""
FlightRadar24 API Connector
Integración con FlightRadar24 para datos de vuelos en tiempo real
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

class FlightRadar24Connector:
    """
    Conector para FlightRadar24 API
    Proporciona datos de vuelos en tiempo real, rastreo de aeronaves y estadísticas de aeropuertos
    """
    
    def __init__(self, api_key: str = "01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb", environment: str = "sandbox"):
        self.api_key = api_key
        self.environment = environment
        
        # URLs posibles para FlightRadar24 API (incluyendo sandbox)
        if environment == "sandbox":
            self.possible_base_urls = [
                "https://api.flightradar24.com/sandbox/v1",
                "https://sandbox-api.flightradar24.com/v1",
                "https://api-sandbox.flightradar24.com/v1",
                "https://api.flightradar24.com/test/v1",
                "https://api.flightradar24.com/common/v1",
                "https://api.flightradar24.com/v1"
            ]
        else:
            self.possible_base_urls = [
                "https://api.flightradar24.com/common/v1",
                "https://api.flightradar24.com/v1", 
                "https://data-live.flightradar24.com",
                "https://data-cloud.flightradar24.com/zones/fcgi/feed.js",
                "https://www.flightradar24.com/_json/airports/traffic/",
                "https://api.flightradar24.com"
            ]
        
        self.base_url = self.possible_base_urls[0]  # Empezar con el primero
        
        # Diferentes formas de autenticación
        self.auth_methods = [
            {'Authorization': f'Bearer {api_key}'},
            {'X-API-Key': api_key},
            {'api_key': api_key},
            {'token': api_key}
        ]
        
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AIFA-Simulator/1.0'
        }
        
        # Coordenadas AIFA
        self.aifa_coords = {
            'lat': 19.7425,
            'lon': -99.0157,
            'airport_code': 'NLU',
            'icao': 'MMSM'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def test_connection(self) -> Dict[str, Any]:
        """Prueba exhaustiva de conexión con múltiples endpoints y métodos de autenticación"""
        results = {
            'tests_performed': [],
            'successful_endpoints': [],
            'failed_endpoints': [],
            'best_working_config': None
        }
        
        # Endpoints de prueba comunes
        test_endpoints = [
            ('search', {'query': 'MEX', 'limit': 1}),
            ('flights', {}),
            ('airports', {}),
            ('zones/fcgi/feed.js', {'bounds': '19,20,-99,-98'}),
            ('', {})  # Root endpoint
        ]
        
        print("🔍 Probando múltiples configuraciones de FlightRadar24...")
        
        # Probar cada combinación de URL base y método de autenticación
        for base_url in self.possible_base_urls:
            for auth_method in self.auth_methods:
                for endpoint_name, params in test_endpoints:
                    try:
                        # Configurar headers para esta prueba
                        test_headers = self.headers.copy()
                        test_headers.update(auth_method)
                        
                        # Construir URL
                        if endpoint_name:
                            url = f"{base_url}/{endpoint_name}" if base_url.endswith('/') else f"{base_url}/{endpoint_name}"
                        else:
                            url = base_url
                        
                        print(f"   🧪 Probando: {base_url} + {list(auth_method.keys())[0]} + {endpoint_name}")
                        
                        response = requests.get(url, headers=test_headers, params=params, timeout=5)
                        
                        test_result = {
                            'base_url': base_url,
                            'auth_method': list(auth_method.keys())[0],
                            'endpoint': endpoint_name or 'root',
                            'status_code': response.status_code,
                            'success': response.status_code == 200,
                            'response_time_ms': response.elapsed.total_seconds() * 1000,
                            'content_length': len(response.content),
                            'content_type': response.headers.get('content-type', 'N/A')
                        }
                        
                        if response.status_code == 200:
                            try:
                                data = response.json() if 'json' in response.headers.get('content-type', '') else response.text[:200]
                                test_result['data_sample'] = data
                                results['successful_endpoints'].append(test_result)
                                
                                # Marcar como la mejor configuración si es la primera exitosa
                                if not results['best_working_config']:
                                    results['best_working_config'] = test_result
                                    self.base_url = base_url
                                    self.session.headers.update(auth_method)
                                    
                            except:
                                test_result['data_sample'] = response.text[:200]
                                results['successful_endpoints'].append(test_result)
                        else:
                            test_result['error'] = response.text[:200]
                            results['failed_endpoints'].append(test_result)
                        
                        results['tests_performed'].append(test_result)
                        
                        # Pausa entre requests para evitar rate limiting
                        time.sleep(0.2)
                        
                    except Exception as e:
                        test_result = {
                            'base_url': base_url,
                            'auth_method': list(auth_method.keys())[0],
                            'endpoint': endpoint_name or 'root',
                            'success': False,
                            'error': str(e)
                        }
                        results['failed_endpoints'].append(test_result)
                        results['tests_performed'].append(test_result)
        
        # Generar resumen final
        if results['successful_endpoints']:
            return {
                'success': True,
                'status': 'CONECTADO',
                'api_active': True,
                'working_endpoints': len(results['successful_endpoints']),
                'failed_endpoints': len(results['failed_endpoints']),
                'total_tests': len(results['tests_performed']),
                'best_config': results['best_working_config'],
                'all_results': results,
                'message': f'FlightRadar24 accesible con {len(results["successful_endpoints"])} endpoints'
            }
        else:
            return {
                'success': False,
                'status': 'NO_ACCESS',
                'api_active': False,
                'working_endpoints': 0,
                'failed_endpoints': len(results['failed_endpoints']),
                'total_tests': len(results['tests_performed']),
                'all_results': results,
                'error': 'Ningún endpoint de FlightRadar24 accesible con esta API key'
            }
    
    def get_airport_info(self, airport_code: str = "NLU") -> Dict[str, Any]:
        """Obtiene información detallada del aeropuerto"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'query': airport_code,
                'limit': 10
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Buscar el aeropuerto específico
                airport_info = None
                for item in data.get('results', []):
                    if item.get('type') == 'airport' and (
                        item.get('iata') == airport_code or 
                        item.get('icao') == airport_code or
                        airport_code.upper() in item.get('name', '').upper()
                    ):
                        airport_info = item
                        break
                
                if airport_info:
                    return {
                        'success': True,
                        'airport_found': True,
                        'name': airport_info.get('name', 'N/A'),
                        'iata': airport_info.get('iata', 'N/A'),
                        'icao': airport_info.get('icao', 'N/A'),
                        'country': airport_info.get('country', 'N/A'),
                        'city': airport_info.get('city', 'N/A'),
                        'latitude': airport_info.get('lat', 0),
                        'longitude': airport_info.get('lon', 0),
                        'timezone': airport_info.get('timezone', 'N/A'),
                        'elevation': airport_info.get('elevation', 0),
                        'website': airport_info.get('website', 'N/A'),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'flightradar24'
                    }
                else:
                    return {
                        'success': False,
                        'airport_found': False,
                        'error': f'Aeropuerto {airport_code} no encontrado',
                        'results_count': len(data.get('results', []))
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
    
    def get_flights_around_airport(self, airport_code: str = "NLU", radius_nm: int = 50) -> Dict[str, Any]:
        """Obtiene vuelos alrededor del aeropuerto"""
        try:
            # Usar coordenadas AIFA
            lat = self.aifa_coords['lat'] if airport_code == "NLU" else 19.7425
            lon = self.aifa_coords['lon'] if airport_code == "NLU" else -99.0157
            
            url = f"{self.base_url}/flights/search"
            params = {
                'bounds': f"{lat-1},{lon-1},{lat+1},{lon+1}",  # Área alrededor del aeropuerto
                'limit': 50
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                flights = data.get('data', [])
                
                # Procesar vuelos
                processed_flights = []
                aifa_departures = []
                aifa_arrivals = []
                
                for flight in flights:
                    try:
                        flight_info = {
                            'flight_id': flight.get('id', 'N/A'),
                            'callsign': flight.get('flight', 'N/A'),
                            'aircraft_type': flight.get('aircraft_model', 'N/A'),
                            'airline': flight.get('airline_name', 'N/A'),
                            'origin': flight.get('origin_airport_name', 'N/A'),
                            'destination': flight.get('destination_airport_name', 'N/A'),
                            'origin_iata': flight.get('origin_iata', 'N/A'),
                            'destination_iata': flight.get('destination_iata', 'N/A'),
                            'altitude': flight.get('altitude', 0),
                            'speed': flight.get('ground_speed', 0),
                            'latitude': flight.get('latitude', 0),
                            'longitude': flight.get('longitude', 0),
                            'heading': flight.get('heading', 0),
                            'status': flight.get('status', 'N/A')
                        }
                        
                        processed_flights.append(flight_info)
                        
                        # Clasificar vuelos AIFA
                        if 'NLU' in flight_info['origin_iata'] or 'MMSM' in flight_info.get('origin_icao', ''):
                            aifa_departures.append(flight_info)
                        elif 'NLU' in flight_info['destination_iata'] or 'MMSM' in flight_info.get('destination_icao', ''):
                            aifa_arrivals.append(flight_info)
                            
                    except Exception as e:
                        print(f"Error procesando vuelo: {e}")
                        continue
                
                return {
                    'success': True,
                    'total_flights_area': len(processed_flights),
                    'aifa_departures': len(aifa_departures),
                    'aifa_arrivals': len(aifa_arrivals),
                    'flights_data': processed_flights,
                    'aifa_departures_data': aifa_departures,
                    'aifa_arrivals_data': aifa_arrivals,
                    'search_area': f"±1° around {lat}, {lon}",
                    'timestamp': datetime.now().isoformat(),
                    'source': 'flightradar24'
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
    
    def get_airport_arrivals_departures(self, airport_code: str = "NLU") -> Dict[str, Any]:
        """Obtiene llegadas y salidas programadas del aeropuerto"""
        try:
            # Intentar múltiples endpoints para obtener datos del aeropuerto
            endpoints_to_try = [
                f"airports/{airport_code}/arrivals",
                f"airports/{airport_code}/departures", 
                f"airports/MMSM/arrivals",
                f"airports/MMSM/departures"
            ]
            
            all_results = {}
            
            for endpoint in endpoints_to_try:
                try:
                    url = f"{self.base_url}/{endpoint}"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        all_results[endpoint] = data
                    else:
                        all_results[endpoint] = {'error': f'HTTP {response.status_code}'}
                        
                except Exception as e:
                    all_results[endpoint] = {'error': str(e)}
                
                # Pequeña pausa entre requests
                time.sleep(0.5)
            
            return {
                'success': True,
                'airport_code': airport_code,
                'endpoints_tested': endpoints_to_try,
                'results': all_results,
                'timestamp': datetime.now().isoformat(),
                'note': 'Múltiples endpoints probados para obtener datos del aeropuerto'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_flight_details(self, flight_id: str) -> Dict[str, Any]:
        """Obtiene detalles específicos de un vuelo"""
        try:
            url = f"{self.base_url}/flights/{flight_id}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'flight_data': data,
                    'timestamp': datetime.now().isoformat()
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
    
    def get_comprehensive_aifa_data(self) -> Dict[str, Any]:
        """Obtiene un resumen completo de datos AIFA desde FlightRadar24"""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'airport_code': 'NLU/MMSM',
                'tests_performed': [],
                'data_collected': {}
            }
            
            # 1. Información del aeropuerto
            print("🔍 Obteniendo información del aeropuerto...")
            airport_info = self.get_airport_info("NLU")
            results['data_collected']['airport_info'] = airport_info
            results['tests_performed'].append('airport_info')
            
            # 2. Vuelos en el área
            print("✈️ Buscando vuelos en el área...")
            flights_area = self.get_flights_around_airport("NLU", 50)
            results['data_collected']['flights_area'] = flights_area
            results['tests_performed'].append('flights_area')
            
            # 3. Llegadas y salidas
            print("📋 Obteniendo llegadas y salidas...")
            arrivals_departures = self.get_airport_arrivals_departures("NLU")
            results['data_collected']['arrivals_departures'] = arrivals_departures
            results['tests_performed'].append('arrivals_departures')
            
            # Análisis de resultados
            results['analysis'] = {
                'airport_found': airport_info.get('airport_found', False),
                'flights_in_area': flights_area.get('total_flights_area', 0),
                'aifa_operations': {
                    'departures': flights_area.get('aifa_departures', 0),
                    'arrivals': flights_area.get('aifa_arrivals', 0)
                },
                'api_accessibility': {
                    'search_endpoint': airport_info.get('success', False),
                    'flights_endpoint': flights_area.get('success', False),
                    'airport_endpoints': arrivals_departures.get('success', False)
                }
            }
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def test_flightradar24_api():
    """Función de prueba completa para FlightRadar24 Sandbox"""
    print("🧪 PRUEBA COMPLETA FLIGHTRADAR24 SANDBOX API")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Sandbox Token: 01987b9a-a8d6-...b45572fb")
    print(f"🏗️ Ambiente: SANDBOX (sin consumo de créditos)")
    print()
    
    # Inicializar conector en modo sandbox
    fr24 = FlightRadar24Connector(environment="sandbox")
    
    # 1. Prueba de conexión
    print("1️⃣ PRUEBA DE CONEXIÓN")
    print("-" * 40)
    
    connection_test = fr24.test_connection()
    
    if connection_test['success']:
        print(f"✅ Estado: {connection_test['status']}")
        print(f"⚡ Tiempo de respuesta: {connection_test.get('response_time_ms', 0):.0f}ms")
        print(f"🎯 Endpoint probado: {connection_test.get('endpoint_tested', 'N/A')}")
    else:
        print(f"❌ Error: {connection_test['error']}")
        print(f"📊 Estado: {connection_test['status']}")
    
    print()
    
    # 2. Prueba completa si la conexión es exitosa
    if connection_test['success']:
        print("2️⃣ DATOS COMPLETOS AIFA")
        print("-" * 40)
        
        comprehensive_data = fr24.get_comprehensive_aifa_data()
        
        if comprehensive_data.get('success', True):  # Asumir éxito si no hay clave 'success'
            analysis = comprehensive_data.get('analysis', {})
            
            print(f"🏢 Aeropuerto encontrado: {'✅' if analysis.get('airport_found') else '❌'}")
            print(f"✈️ Vuelos en área: {analysis.get('flights_in_area', 0)}")
            print(f"🛫 Salidas AIFA: {analysis.get('aifa_operations', {}).get('departures', 0)}")
            print(f"🛬 Llegadas AIFA: {analysis.get('aifa_operations', {}).get('arrivals', 0)}")
            
            # Mostrar accesibilidad de endpoints
            api_access = analysis.get('api_accessibility', {})
            print(f"🔍 Endpoint Search: {'✅' if api_access.get('search_endpoint') else '❌'}")
            print(f"✈️ Endpoint Flights: {'✅' if api_access.get('flights_endpoint') else '❌'}")
            print(f"📋 Endpoint Airport: {'✅' if api_access.get('airport_endpoints') else '❌'}")
            
        else:
            print(f"❌ Error obteniendo datos: {comprehensive_data.get('error', 'Unknown')}")
    
    print()
    print("=" * 60)
    print("✅ PRUEBA FLIGHTRADAR24 COMPLETADA")
    
    return connection_test['success']

if __name__ == "__main__":
    test_flightradar24_api()