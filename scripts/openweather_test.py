"""
Script de prueba exhaustiva para tokens de OpenWeatherMap
Prueba múltiples endpoints y configuraciones
"""

import requests
import json
from datetime import datetime
import time

class OpenWeatherTest:
    """Tester exhaustivo para tokens de OpenWeatherMap"""
    
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.tokens_to_test = [
            "6a6e94ae482a1c310fe583b6a35eb72b",  # Token más reciente
            "ca19e602f4dca39dc3b80331f9a6b65a"   # Token anterior
        ]
        
        # Coordenadas de prueba (AIFA)
        self.test_coordinates = {
            'lat': 19.7411,
            'lon': -99.0183,
            'name': 'AIFA Felipe Ángeles'
        }
    
    def test_token(self, token: str) -> dict:
        """
        Prueba exhaustiva de un token específico
        
        Args:
            token: API key de OpenWeatherMap
            
        Returns:
            Dict con resultados de todas las pruebas
        """
        results = {
            'token': token,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        print(f"\n🧪 Probando token: {token}")
        print("=" * 50)
        
        # Prueba 1: Current Weather API (básica)
        results['tests']['current_weather'] = self._test_current_weather(token)
        
        # Prueba 2: Con diferentes parámetros
        results['tests']['with_units'] = self._test_with_units(token)
        
        # Prueba 3: Con idioma español
        results['tests']['with_language'] = self._test_with_language(token)
        
        # Prueba 4: Diferentes coordenadas
        results['tests']['different_location'] = self._test_different_location(token)
        
        # Prueba 5: Por nombre de ciudad
        results['tests']['city_name'] = self._test_city_name(token)
        
        return results
    
    def _test_current_weather(self, token: str) -> dict:
        """Prueba básica de current weather"""
        print("🌤️  Prueba 1: Current Weather API básica")
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': self.test_coordinates['lat'],
            'lon': self.test_coordinates['lon'],
            'appid': token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'url': response.url,
                'response_time': response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                data = response.json()
                result['data_preview'] = {
                    'location': data.get('name', 'Unknown'),
                    'temperature': data.get('main', {}).get('temp', 'N/A'),
                    'weather': data.get('weather', [{}])[0].get('main', 'N/A')
                }
                print(f"  ✅ Éxito - {data.get('name')} - {data.get('main', {}).get('temp')}K")
            else:
                result['error'] = response.text
                print(f"  ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            result = {
                'success': False,
                'error': str(e),
                'status_code': None
            }
            print(f"  ❌ Excepción: {e}")
        
        return result
    
    def _test_with_units(self, token: str) -> dict:
        """Prueba con unidades métricas"""
        print("📏 Prueba 2: Con unidades métricas")
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': self.test_coordinates['lat'],
            'lon': self.test_coordinates['lon'],
            'appid': token,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                temp_c = data.get('main', {}).get('temp', 'N/A')
                print(f"  ✅ Éxito - Temperatura: {temp_c}°C")
                result['temperature_celsius'] = temp_c
            else:
                result['error'] = response.text
                print(f"  ❌ Error {response.status_code}")
                
        except Exception as e:
            result = {'success': False, 'error': str(e)}
            print(f"  ❌ Excepción: {e}")
        
        return result
    
    def _test_with_language(self, token: str) -> dict:
        """Prueba con idioma español"""
        print("🇪🇸 Prueba 3: Con idioma español")
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': self.test_coordinates['lat'],
            'lon': self.test_coordinates['lon'],
            'appid': token,
            'units': 'metric',
            'lang': 'es'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                desc = data.get('weather', [{}])[0].get('description', 'N/A')
                print(f"  ✅ Éxito - Descripción: {desc}")
                result['description_spanish'] = desc
            else:
                result['error'] = response.text
                print(f"  ❌ Error {response.status_code}")
                
        except Exception as e:
            result = {'success': False, 'error': str(e)}
            print(f"  ❌ Excepción: {e}")
        
        return result
    
    def _test_different_location(self, token: str) -> dict:
        """Prueba con diferentes coordenadas (Cancún)"""
        print("🏝️  Prueba 4: Coordenadas diferentes (Cancún)")
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': 21.0364,  # Cancún
            'lon': -86.8771,
            'appid': token,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                location = data.get('name', 'Unknown')
                temp = data.get('main', {}).get('temp', 'N/A')
                print(f"  ✅ Éxito - {location}: {temp}°C")
                result['location'] = location
                result['temperature'] = temp
            else:
                result['error'] = response.text
                print(f"  ❌ Error {response.status_code}")
                
        except Exception as e:
            result = {'success': False, 'error': str(e)}
            print(f"  ❌ Excepción: {e}")
        
        return result
    
    def _test_city_name(self, token: str) -> dict:
        """Prueba con nombre de ciudad"""
        print("🏙️  Prueba 5: Por nombre de ciudad (Ciudad de México)")
        
        url = f"{self.base_url}/weather"
        params = {
            'q': 'Mexico City,MX',
            'appid': token,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                location = data.get('name', 'Unknown')
                temp = data.get('main', {}).get('temp', 'N/A')
                print(f"  ✅ Éxito - {location}: {temp}°C")
                result['location'] = location
                result['temperature'] = temp
            else:
                result['error'] = response.text
                print(f"  ❌ Error {response.status_code}")
                
        except Exception as e:
            result = {'success': False, 'error': str(e)}
            print(f"  ❌ Excepción: {e}")
        
        return result
    
    def run_all_tests(self) -> dict:
        """Ejecuta todas las pruebas para todos los tokens"""
        print("🌤️  PRUEBAS EXHAUSTIVAS OpenWeatherMap API")
        print("=" * 60)
        print(f"🕒 Iniciando pruebas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'tokens_tested': len(self.tokens_to_test),
            'results': []
        }
        
        for i, token in enumerate(self.tokens_to_test, 1):
            print(f"\n📋 TOKEN {i}/{len(self.tokens_to_test)}")
            results = self.test_token(token)
            all_results['results'].append(results)
            
            # Pausa entre tokens para evitar rate limiting
            if i < len(self.tokens_to_test):
                print("\n⏳ Pausa de 2 segundos...")
                time.sleep(2)
        
        # Resumen final
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, results: dict):
        """Imprime resumen de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        for i, token_result in enumerate(results['results'], 1):
            token = token_result['token']
            tests = token_result['tests']
            
            successful_tests = sum(1 for test in tests.values() if test.get('success', False))
            total_tests = len(tests)
            
            print(f"\n🔑 Token {i}: {token}")
            print(f"   ✅ Pruebas exitosas: {successful_tests}/{total_tests}")
            
            if successful_tests > 0:
                print(f"   🎉 ESTE TOKEN FUNCIONA!")
            else:
                print(f"   ❌ Token no funcional")
        
        # Recomendación
        working_tokens = []
        for token_result in results['results']:
            tests = token_result['tests']
            if any(test.get('success', False) for test in tests.values()):
                working_tokens.append(token_result['token'])
        
        if working_tokens:
            print(f"\n💡 RECOMENDACIÓN: Usar token {working_tokens[0]}")
        else:
            print(f"\n🚨 NINGÚN TOKEN FUNCIONA - Revisa activación en OpenWeatherMap")

def main():
    """Función principal de pruebas"""
    tester = OpenWeatherTest()
    results = tester.run_all_tests()
    
    # Guardar resultados
    output_file = 'data/openweather_test_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}")

if __name__ == "__main__":
    main()