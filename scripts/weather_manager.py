"""
Weather Manager - Sistema integrado de datos meteorológicos
Combina datos reales de OpenWeatherMap con simulación de respaldo
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from weather_simulator import WeatherSimulator

class WeatherManager:
    """
    Administrador inteligente de datos meteorológicos
    
    - Prioriza datos reales de OpenWeatherMap si el token es válido
    - Utiliza simulación realista como respaldo
    - Proporciona análisis de condiciones de vuelo
    """
    
    def __init__(self, openweather_token: str = "6a6e94ae482a1c310fe583b6a35eb72b"):
        self.openweather_token = openweather_token
        self.base_url_v25 = "https://api.openweathermap.org/data/2.5"
        self.base_url_v3 = "https://api.openweathermap.org/data/3.0"
        self.simulator = WeatherSimulator()
        self.use_real_data = False
        
        # Verificar si el token es válido
        self._validate_token()
    
    def _validate_token(self) -> bool:
        """Valida si el token de OpenWeatherMap es funcional"""
        try:
            # Probar primero OneCall 3.0
            test_url = f"{self.base_url_v3}/onecall"
            test_params = {
                'lat': 19.7425,  # AIFA coordenadas precisas
                'lon': -99.0157,
                'appid': self.openweather_token,
                'units': 'metric'
            }
            
            response = requests.get(test_url, params=test_params, timeout=5)
            
            if response.status_code == 200:
                self.use_real_data = True
                self.api_version = "3.0_onecall"
                print("✅ Token OpenWeatherMap 3.0 OneCall válido - usando datos reales avanzados")
                return True
            elif response.status_code == 402:
                # Intentar con API 2.5 como fallback
                test_url = f"{self.base_url_v25}/weather"
                test_params = {
                    'lat': 19.7425,
                    'lon': -99.0157,
                    'appid': self.openweather_token,
                    'units': 'metric'
                }
                
                response = requests.get(test_url, params=test_params, timeout=5)
                if response.status_code == 200:
                    self.use_real_data = True
                    self.api_version = "2.5_basic"
                    print("✅ Token OpenWeatherMap 2.5 válido - usando datos reales básicos")
                    return True
                else:
                    print(f"⚠️  Token OpenWeatherMap inválido (Status: {response.status_code}) - usando simulación")
                    return False
            else:
                print(f"⚠️  Token OpenWeatherMap inválido (Status: {response.status_code}) - usando simulación")
                return False
                
        except Exception as e:
            print(f"⚠️  Error validando token OpenWeatherMap: {e} - usando simulación")
            return False
    
    def get_current_weather(self, airport_code: str) -> Optional[Dict]:
        """
        Obtiene clima actual - datos reales o simulados
        
        Args:
            airport_code: Código IATA del aeropuerto
            
        Returns:
            Dict con datos meteorológicos
        """
        if self.use_real_data:
            return self._get_real_weather(airport_code)
        else:
            return self._get_simulated_weather(airport_code)
    
    def _get_real_weather(self, airport_code: str) -> Optional[Dict]:
        """Obtiene datos reales de OpenWeatherMap usando OneCall 3.0 o 2.5"""
        
        # Coordenadas de aeropuertos (actualizadas con precisión)
        airports = {
            'NLU': {'lat': 19.7425, 'lon': -99.0157, 'name': 'AIFA - Felipe Ángeles'},
            'MEX': {'lat': 19.4363, 'lon': -99.0721, 'name': 'CDMX - Benito Juárez'},
            'CUN': {'lat': 21.0364, 'lon': -86.8771, 'name': 'Cancún'},
            'GDL': {'lat': 20.5218, 'lon': -103.311, 'name': 'Guadalajara'},
            'TIJ': {'lat': 32.5411, 'lon': -116.970, 'name': 'Tijuana'},
            'LAX': {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles'},
            'MIA': {'lat': 25.7617, 'lon': -80.1918, 'name': 'Miami'},
            'MAD': {'lat': 40.4168, 'lon': -3.7038, 'name': 'Madrid'},
            'LHR': {'lat': 51.4700, 'lon': -0.4543, 'name': 'Londres Heathrow'}
        }
        
        if airport_code not in airports:
            return None
            
        airport = airports[airport_code]
        
        try:
            # Usar OneCall 3.0 si está disponible
            if hasattr(self, 'api_version') and self.api_version == "3.0_onecall":
                return self._get_onecall_data(airport_code, airport)
            else:
                return self._get_basic_weather_data(airport_code, airport)
                
        except Exception as e:
            print(f"Error obteniendo datos reales para {airport_code}: {e}")
            # Fallback a simulación
            return self._get_simulated_weather(airport_code)
    
    def _get_onecall_data(self, airport_code: str, airport: Dict) -> Dict:
        """Obtiene datos completos usando OneCall 3.0"""
        url = f"{self.base_url_v3}/onecall"
        params = {
            'lat': airport['lat'],
            'lon': airport['lon'],
            'appid': self.openweather_token,
            'units': 'metric',
            'lang': 'es'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current', {})
        
        # Procesar datos de OneCall 3.0 (más completos)
        processed_data = {
            'airport_code': airport_code,
            'airport_name': airport['name'],
            'timestamp': datetime.now().isoformat(),
            'api_version': '3.0_onecall',
            'coordinates': {
                'lat': airport['lat'],
                'lon': airport['lon']
            },
            'current': {
                'temperature': current.get('temp', 0),
                'feels_like': current.get('feels_like', 0),
                'humidity': current.get('humidity', 0),
                'pressure': current.get('pressure', 1013),
                'visibility': current.get('visibility', 10000) / 1000,  # km
                'uv_index': current.get('uvi', 0),
                'dew_point': current.get('dew_point', 0),
                'weather': {
                    'main': current.get('weather', [{}])[0].get('main', 'Clear'),
                    'description': current.get('weather', [{}])[0].get('description', 'cielo claro'),
                    'icon': current.get('weather', [{}])[0].get('icon', '01d')
                },
                'wind': {
                    'speed': current.get('wind_speed', 0),
                    'direction': current.get('wind_deg', 0),
                    'gust': current.get('wind_gust', 0)
                },
                'clouds': current.get('clouds', 0)
            },
            'forecast': {
                'hourly_available': len(data.get('hourly', [])),
                'daily_available': len(data.get('daily', [])),
                'alerts': len(data.get('alerts', []))
            },
            'conditions': self._analyze_flight_conditions(current, is_real=True),
            'data_source': 'openweathermap_onecall_3.0'
        }
        
        return processed_data
    
    def _get_basic_weather_data(self, airport_code: str, airport: Dict) -> Dict:
        """Obtiene datos básicos usando API 2.5"""
        url = f"{self.base_url_v25}/weather" 
        params = {
            'lat': airport['lat'],
            'lon': airport['lon'],
            'appid': self.openweather_token,
            'units': 'metric',
            'lang': 'es'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Procesar datos de API 2.5 (básicos)
        processed_data = {
            'airport_code': airport_code,
            'airport_name': airport['name'],
            'timestamp': datetime.now().isoformat(),
            'api_version': '2.5_basic',
            'coordinates': {
                'lat': airport['lat'],
                'lon': airport['lon']
            },
            'current': {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'visibility': data.get('visibility', 10000) / 1000,  # km
                'weather': {
                    'main': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                },
                'wind': {
                    'speed': data['wind']['speed'],
                    'direction': data['wind'].get('deg', 0),
                    'gust': data['wind'].get('gust', 0)
                },
                'clouds': data.get('clouds', {}).get('all', 0)
            },
            'conditions': self._analyze_flight_conditions(data, is_real=True),
            'data_source': 'openweathermap_basic_2.5'
        }
        
        return processed_data
    
    def _get_simulated_weather(self, airport_code: str) -> Optional[Dict]:
        """Obtiene datos simulados usando WeatherSimulator"""
        weather_data = self.simulator.get_current_weather(airport_code)
        if weather_data:
            weather_data['data_source'] = 'simulated_fallback' if self.use_real_data else 'simulated'
        return weather_data
    
    def _analyze_flight_conditions(self, weather_data: Dict, is_real: bool = False) -> Dict:
        """
        Analiza condiciones de vuelo
        
        Args:
            weather_data: Datos meteorológicos (real o simulado)
            is_real: Si son datos reales de OpenWeatherMap
            
        Returns:
            Análisis de condiciones de vuelo
        """
        conditions = {
            'visibility_status': 'good',
            'wind_status': 'normal',
            'weather_status': 'good',
            'overall_status': 'good',
            'flight_impact': 'minimal',
            'recommendations': []
        }
        
        # Para datos reales de OpenWeatherMap
        if is_real:
            # Analizar visibilidad
            visibility = weather_data.get('visibility', 10000) / 1000
            if visibility < 1:
                conditions['visibility_status'] = 'poor'
                conditions['recommendations'].append('Visibilidad reducida - procedimientos IFR requeridos')
            elif visibility < 3:
                conditions['visibility_status'] = 'limited'
                conditions['recommendations'].append('Visibilidad limitada - precaución extra')
            
            # Analizar viento
            wind_speed = weather_data.get('wind', {}).get('speed', 0)
            wind_gust = weather_data.get('wind', {}).get('gust', 0)
            
            if wind_speed > 15 or wind_gust > 20:
                conditions['wind_status'] = 'strong'
                conditions['recommendations'].append('Vientos fuertes - posibles retrasos')
            elif wind_speed > 10:
                conditions['wind_status'] = 'moderate'
            
            # Analizar condiciones generales
            weather_main = weather_data.get('weather', [{}])[0].get('main', '').lower()
            
            if weather_main in ['thunderstorm', 'tornado']:
                conditions['weather_status'] = 'severe'
                conditions['flight_impact'] = 'high'
                conditions['recommendations'].append('Condiciones severas - vuelos pueden cancelarse')
            elif weather_main in ['rain', 'snow', 'drizzle']:
                conditions['weather_status'] = 'adverse'
                conditions['flight_impact'] = 'moderate'
                conditions['recommendations'].append('Precipitación - posibles retrasos menores')
            elif weather_main in ['fog', 'mist', 'haze']:
                conditions['weather_status'] = 'reduced_visibility'
                conditions['flight_impact'] = 'moderate'
        else:
            # Usar análisis del simulador
            return self.simulator._analyze_flight_conditions(weather_data)
        
        # Status general
        if conditions['weather_status'] == 'severe' or conditions['visibility_status'] == 'poor':
            conditions['overall_status'] = 'poor'
        elif conditions['weather_status'] == 'adverse' or conditions['wind_status'] == 'strong':
            conditions['overall_status'] = 'caution'
        
        return conditions
    
    def get_route_weather(self, origin: str, destination: str) -> Dict:
        """
        Obtiene clima para una ruta completa (origen y destino)
        
        Args:
            origin: Código IATA aeropuerto origen
            destination: Código IATA aeropuerto destino
            
        Returns:
            Dict con clima de origen y destino
        """
        origin_weather = self.get_current_weather(origin)
        dest_weather = self.get_current_weather(destination)
        
        return {
            'route': f"{origin}-{destination}",
            'timestamp': datetime.now().isoformat(),
            'origin': origin_weather,
            'destination': dest_weather,
            'route_analysis': self._analyze_route_conditions(origin_weather, dest_weather),
            'data_source': 'mixed' if origin_weather and dest_weather else 'error'
        }
    
    def _analyze_route_conditions(self, origin_weather: Dict, dest_weather: Dict) -> Dict:
        """
        Analiza condiciones meteorológicas para ruta completa
        
        Args:
            origin_weather: Clima en origen
            dest_weather: Clima en destino
            
        Returns:
            Análisis de condiciones de ruta
        """
        if not origin_weather or not dest_weather:
            return {'status': 'no_data', 'recommendations': ['Datos meteorológicos no disponibles']}
        
        origin_conditions = origin_weather['conditions']
        dest_conditions = dest_weather['conditions']
        
        # Determinar peor condición
        statuses = [origin_conditions['overall_status'], dest_conditions['overall_status']]
        
        if 'poor' in statuses:
            overall_status = 'poor'
            impact = 'high'
        elif 'caution' in statuses:
            overall_status = 'caution'
            impact = 'moderate'
        else:
            overall_status = 'good'
            impact = 'minimal'
        
        recommendations = []
        recommendations.extend(origin_conditions.get('recommendations', []))
        recommendations.extend(dest_conditions.get('recommendations', []))
        
        if not recommendations:
            recommendations = ['Condiciones meteorológicas favorables para vuelo']
        
        return {
            'overall_status': overall_status,
            'flight_impact': impact,
            'origin_status': origin_conditions['overall_status'],
            'destination_status': dest_conditions['overall_status'],
            'recommendations': recommendations,
            'flight_advice': self._generate_flight_advice(overall_status, impact)
        }
    
    def _generate_flight_advice(self, status: str, impact: str) -> str:
        """Genera consejo específico para vuelos basado en condiciones"""
        
        advice_matrix = {
            ('good', 'minimal'): 'Condiciones excelentes para vuelo - operaciones normales',
            ('caution', 'moderate'): 'Condiciones aceptables - monitorear desarrollos meteorológicos',
            ('poor', 'high'): 'Condiciones adversas - considerar reprogramación o rutas alternativas'
        }
        
        return advice_matrix.get((status, impact), 'Evaluar condiciones caso por caso')
    
    def get_weather_dashboard_data(self, airport_codes: List[str]) -> Dict:
        """
        Obtiene datos meteorológicos organizados para dashboard
        
        Args:
            airport_codes: Lista de códigos IATA
            
        Returns:
            Dict con datos organizados para visualización
        """
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'data_source': 'openweathermap' if self.use_real_data else 'simulated',
            'airports': {},
            'summary': {
                'total_airports': len(airport_codes),
                'good_conditions': 0,
                'caution_conditions': 0,
                'poor_conditions': 0,
                'operational_impact': 'minimal'
            }
        }
        
        condition_counts = {'good': 0, 'caution': 0, 'poor': 0}
        
        for code in airport_codes:
            weather = self.get_current_weather(code)
            if weather:
                dashboard_data['airports'][code] = {
                    'name': weather['airport_name'],
                    'temperature': weather['current']['temperature'],
                    'conditions': weather['current']['weather']['description'],
                    'wind_speed': weather['current']['wind']['speed'],
                    'visibility': weather['current']['visibility'],
                    'flight_status': weather['conditions']['overall_status'],
                    'flight_impact': weather['conditions']['flight_impact'],
                    'recommendations': weather['conditions']['recommendations']
                }
                
                # Contar condiciones
                status = weather['conditions']['overall_status']
                if status in condition_counts:
                    condition_counts[status] += 1
        
        # Actualizar resumen
        dashboard_data['summary']['good_conditions'] = condition_counts['good']
        dashboard_data['summary']['caution_conditions'] = condition_counts['caution']
        dashboard_data['summary']['poor_conditions'] = condition_counts['poor']
        
        # Determinar impacto operacional general
        if condition_counts['poor'] > 0:
            dashboard_data['summary']['operational_impact'] = 'high'
        elif condition_counts['caution'] > 0:
            dashboard_data['summary']['operational_impact'] = 'moderate'
        else:
            dashboard_data['summary']['operational_impact'] = 'minimal'
        
        return dashboard_data

def test_weather_manager():
    """Función de prueba para WeatherManager"""
    print("🌤️  Probando Weather Manager (Sistema Integrado)...")
    
    weather_mgr = WeatherManager()
    
    # Mostrar modo de operación
    mode = "DATOS REALES" if weather_mgr.use_real_data else "SIMULACIÓN"
    print(f"🔧 Modo de operación: {mode}")
    print()
    
    # Probar aeropuertos mexicanos principales
    test_airports = ['NLU', 'MEX', 'CUN', 'GDL']
    
    print("📍 Clima en aeropuertos mexicanos:")
    for airport in test_airports:
        weather = weather_mgr.get_current_weather(airport)
        if weather:
            curr = weather['current']
            cond = weather['conditions']
            source = weather['data_source']
            
            print(f"{airport} ({weather['airport_name']}) [{source.upper()}]:")
            print(f"  🌡️  {curr['temperature']}°C - {curr['weather']['description']}")
            print(f"  💨 Viento: {curr['wind']['speed']} m/s")
            print(f"  👁️  Visibilidad: {curr['visibility']} km")
            print(f"  ✈️  Estado: {cond['overall_status']} - {cond['flight_impact']} impacto")
            if cond['recommendations']:
                print(f"  💡 {', '.join(cond['recommendations'])}")
        print()
    
    # Probar análisis de ruta
    print("🛫 Análisis de ruta AIFA -> Cancún:")
    route_analysis = weather_mgr.get_route_weather('NLU', 'CUN')
    if route_analysis['origin'] and route_analysis['destination']:
        analysis = route_analysis['route_analysis']
        print(f"  📊 Estado general: {analysis['overall_status']}")
        print(f"  🎯 Impacto: {analysis['flight_impact']}")
        print(f"  💬 Consejo: {analysis['flight_advice']}")
    
    # Generar datos para dashboard
    print("\n📊 Generando datos para dashboard...")
    dashboard_data = weather_mgr.get_weather_dashboard_data(['NLU', 'MEX', 'CUN', 'GDL', 'TIJ'])
    
    summary = dashboard_data['summary']
    print(f"  ✅ Buenos: {summary['good_conditions']}")
    print(f"  ⚠️  Precaución: {summary['caution_conditions']}")
    print(f"  ❌ Adversos: {summary['poor_conditions']}")
    print(f"  🎯 Impacto operacional: {summary['operational_impact']}")
    
    # Guardar datos
    print("\n💾 Guardando datos integrados...")
    with open('data/weather_integrated_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Datos guardados en: data/weather_integrated_data.json")

if __name__ == "__main__":
    test_weather_manager()