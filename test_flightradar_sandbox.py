#!/usr/bin/env python3
"""
Prueba específica para FlightRadar24 Sandbox
Enfoque directo en endpoints conocidos
"""

import requests
import json
from datetime import datetime
import time

def test_flightradar_sandbox_direct():
    """Prueba directa de FlightRadar24 Sandbox con endpoints comunes"""
    
    print("🧪 PRUEBA DIRECTA FLIGHTRADAR24 SANDBOX")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Sandbox Token: 01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb")
    print(f"🏗️ Ambiente: SANDBOX (sin consumo de créditos)")
    print()
    
    # Token de sandbox
    api_key = "01987b9a-a8d6-71b3-abbd-53bdf5474e33|R5WQ8qJALNFEjdqqKi8fYcy8J3V1jxAZNJNQXEXob45572fb"
    
    # Endpoints comunes de FlightRadar24 basados en documentación típica
    test_configs = [
        {
            'name': 'Live Flight Data',
            'url': 'https://api.flightradar24.com/live/flights',
            'method': 'GET',
            'headers': {'X-API-Key': api_key},
            'params': {'bounds': '20,-98,19,-99'}  # Área AIFA
        },
        {
            'name': 'Airport Data',
            'url': 'https://api.flightradar24.com/airports/MEX',
            'method': 'GET', 
            'headers': {'Authorization': f'Bearer {api_key}'},
            'params': {}
        },
        {
            'name': 'Flight Search',
            'url': 'https://api.flightradar24.com/search',
            'method': 'GET',
            'headers': {'X-API-Key': api_key},
            'params': {'query': 'AIFA', 'type': 'airport'}
        },
        {
            'name': 'Zone Feed (Mexico)',
            'url': 'https://data-live.flightradar24.com/zones/fcgi/feed.js',
            'method': 'GET',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'params': {'bounds': '20,-98,19,-99', 'faa': '1', 'satellite': '1', 'mlat': '1', 'flarm': '1'}
        },
        {
            'name': 'Airport Traffic JSON',
            'url': 'https://www.flightradar24.com/_json/airports/traffic/MEX',
            'method': 'GET',
            'headers': {'X-API-Key': api_key},
            'params': {}
        },
        {
            'name': 'Basic API Test',
            'url': 'https://api.flightradar24.com',
            'method': 'GET',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'params': {}
        }
    ]
    
    successful_tests = []
    failed_tests = []
    
    print("🔍 PROBANDO ENDPOINTS CONOCIDOS DE FLIGHTRADAR24...")
    print("-" * 60)
    
    for i, config in enumerate(test_configs, 1):
        try:
            print(f"{i}️⃣ {config['name']}")
            print(f"   🌐 URL: {config['url']}")
            print(f"   🔑 Auth: {list(config['headers'].keys())[0]}")
            
            start_time = time.time()
            response = requests.get(
                config['url'],
                headers=config['headers'],
                params=config['params'],
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000
            
            print(f"   📊 Status: {response.status_code}")
            print(f"   ⚡ Tiempo: {response_time:.0f}ms")
            print(f"   📦 Tamaño: {len(response.content)} bytes")
            print(f"   📄 Tipo: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                print(f"   ✅ ÉXITO")
                
                # Intentar parsear JSON
                try:
                    if 'json' in response.headers.get('content-type', ''):
                        data = response.json()
                        print(f"   📋 Datos: JSON con {len(str(data))} caracteres")
                        
                        # Mostrar muestra de datos
                        if isinstance(data, dict):
                            keys = list(data.keys())[:5]
                            print(f"   🔑 Keys: {keys}")
                        elif isinstance(data, list):
                            print(f"   📝 Lista con {len(data)} elementos")
                    else:
                        print(f"   📝 Contenido: {response.text[:100]}...")
                        
                except json.JSONDecodeError:
                    print(f"   📝 Texto: {response.text[:100]}...")
                
                successful_tests.append({
                    'name': config['name'],
                    'url': config['url'],
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', 'N/A')
                })
                
            elif response.status_code == 401:
                print(f"   🔑 ERROR: API Key inválida o no autorizada")
                failed_tests.append({'name': config['name'], 'error': 'Unauthorized'})
            elif response.status_code == 403:
                print(f"   🚫 ERROR: Acceso denegado")
                failed_tests.append({'name': config['name'], 'error': 'Forbidden'})
            elif response.status_code == 404:
                print(f"   🔍 ERROR: Endpoint no encontrado")
                failed_tests.append({'name': config['name'], 'error': 'Not Found'})
            elif response.status_code == 429:
                print(f"   ⏰ ERROR: Rate limit excedido")
                failed_tests.append({'name': config['name'], 'error': 'Rate Limited'})
            else:
                print(f"   ❌ ERROR: {response.status_code} - {response.text[:100]}")
                failed_tests.append({'name': config['name'], 'error': f'HTTP {response.status_code}'})
            
            print()
            time.sleep(0.5)  # Pausa entre requests
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT")
            failed_tests.append({'name': config['name'], 'error': 'Timeout'})
            print()
        except requests.exceptions.ConnectionError:
            print(f"   🔌 ERROR DE CONEXIÓN")
            failed_tests.append({'name': config['name'], 'error': 'Connection Error'})
            print()    
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {str(e)}")
            failed_tests.append({'name': config['name'], 'error': str(e)})
            print()
    
    # Resumen final
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Exitosas: {len(successful_tests)}")
    print(f"❌ Fallidas: {len(failed_tests)}")
    print(f"📈 Tasa de éxito: {len(successful_tests)/(len(successful_tests)+len(failed_tests))*100:.1f}%")
    print()
    
    if successful_tests:
        print("🎉 ENDPOINTS FUNCIONANDO:")
        for test in successful_tests:
            print(f"   ✅ {test['name']} - {test['status_code']} ({test['response_time_ms']:.0f}ms)")
        print()
        
        # Seleccionar el mejor endpoint para usar
        best_endpoint = min(successful_tests, key=lambda x: x['response_time_ms'])
        print(f"🏆 MEJOR ENDPOINT: {best_endpoint['name']}")
        print(f"   🌐 URL: {best_endpoint['url']}")
        print(f"   ⚡ Tiempo: {best_endpoint['response_time_ms']:.0f}ms")
        print(f"   📦 Tamaño: {best_endpoint['content_length']} bytes")
        
    if failed_tests:
        print("❌ ENDPOINTS NO FUNCIONANDO:")
        for test in failed_tests:
            print(f"   ❌ {test['name']} - {test['error']}")
    
    print()
    print("=" * 60)
    
    if successful_tests:
        print("🎯 RESULTADO: FlightRadar24 SANDBOX ACCESIBLE")
        print(f"🚀 Próximo paso: Integrar endpoint {best_endpoint['name']} al sistema AIFA")
        return True
    else:
        print("⚠️ RESULTADO: Sin acceso a FlightRadar24 Sandbox")
        print("💡 Sugerencia: Verificar documentación o contactar soporte")
        return False

if __name__ == "__main__":
    test_flightradar_sandbox_direct()