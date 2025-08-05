"""
OpenWeatherMap API Integration para AIFA Demo
Obtiene condiciones meteorológicas para aeropuertos y rutas
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class WeatherAPI:
    """Cliente para OpenWeatherMap API"""
    
    def __init__(self, api_key: str = "ca19e602f4dca39dc3b80331f9a6b65a"):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        
        # Coordenadas de aeropuertos principales mexicanos
        self.airports = {
            'NLU': {'name': 'AIFA - Felipe Ángeles', 'lat': 19.7411, 'lon': -99.0183},
            'MEX': {'name': 'CDMX - Benito Juárez', 'lat': 19.4363, 'lon': -99.0721},
            'CUN': {'name': 'Cancún', 'lat': 21.0364, 'lon': -86.8771},
            'GDL': {'name': 'Guadalajara', 'lat': 20.5218, 'lon': -103.311},
            'TIJ': {'name': 'Tijuana', 'lat': 32.5411, 'lon': -116.970},
            'LAX': {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
            'MIA': {'name': 'Miami', 'lat': 25.7617, 'lon': -80.1918},
            'MAD': {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038},
            'LHR': {'name': 'Londres Heathrow', 'lat': 51.4700, 'lon': -0.4543}
        }
    
    def get_current_weather(self, airport_code: str) -> Optional[Dict]:
        """
        Obtiene clima actual para un aeropuerto
        
        Args:
            airport_code: Código IATA del aeropuerto
            
        Returns:
            Dict con datos meteorológicos
        """
        if airport_code not in self.airports:
            return None
            
        airport = self.airports[airport_code]
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': airport['lat'],
                'lon': airport['lon'],
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos
            processed_data = {
                'airport_code': airport_code,
                'airport_name': airport['name'],
                'timestamp': datetime.utcnow().isoformat(),
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
                'conditions': self._analyze_flight_conditions(data)
            }
            
            return processed_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo clima para {airport_code}: {e}")
            return None
    
    def get_forecast(self, airport_code: str, days: int = 5) -> Optional[Dict]:
        """
        Obtiene pronóstico meteorológico
        
        Args:
            airport_code: Código IATA del aeropuerto
            days: Días de pronóstico (máximo 5)
            
        Returns:
            Dict con pronóstico
        """
        if airport_code not in self.airports:
            return None
            
        airport = self.airports[airport_code]
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': airport['lat'],
                'lon': airport['lon'],
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar pronóstico
            forecast_data = {
                'airport_code': airport_code,
                'airport_name': airport['name'],
                'timestamp': datetime.utcnow().isoformat(),
                'forecast': []
            }
            
            for item in data['list'][:days * 8]:  # 8 predicciones por día (cada 3 horas)
                forecast_item = {
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'weather': {
                        'main': item['weather'][0]['main'],
                        'description': item['weather'][0]['description']
                    },
                    'wind_speed': item['wind']['speed'],
                    'clouds': item.get('clouds', {}).get('all', 0),
                    'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0),
                    'flight_conditions': self._analyze_flight_conditions(item)
                }
                forecast_data['forecast'].append(forecast_item)
            
            return forecast_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo pronóstico para {airport_code}: {e}")
            return None
    
    def get_route_weather(self, origin: str, destination: str) -> Dict:
        """
        Obtiene clima para una ruta completa
        
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
            'timestamp': datetime.utcnow().isoformat(),
            'origin': origin_weather,
            'destination': dest_weather,
            'route_analysis': self._analyze_route_conditions(origin_weather, dest_weather)
        }
    
    def _analyze_flight_conditions(self, weather_data: Dict) -> Dict:
        """
        Analiza condiciones de vuelo basado en datos meteorológicos
        
        Args:
            weather_data: Datos meteorológicos raw
            
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
        
        # Status general
        if conditions['weather_status'] == 'severe' or conditions['visibility_status'] == 'poor':
            conditions['overall_status'] = 'poor'
        elif conditions['weather_status'] == 'adverse' or conditions['wind_status'] == 'strong':
            conditions['overall_status'] = 'caution'
        
        return conditions
    
    def _analyze_route_conditions(self, origin_weather: Dict, dest_weather: Dict) -> Dict:
        """
        Analiza condiciones de ruta completa
        
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
            'recommendations': recommendations
        }
    
    def get_multiple_airports_weather(self, airport_codes: List[str]) -> Dict:
        """
        Obtiene clima para múltiples aeropuertos
        
        Args:
            airport_codes: Lista de códigos IATA
            
        Returns:
            Dict con clima de todos los aeropuertos
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'airports': {},
            'summary': {
                'total_airports': len(airport_codes),
                'successful_requests': 0,
                'failed_requests': 0
            }
        }
        
        for code in airport_codes:
            weather = self.get_current_weather(code)
            if weather:
                results['airports'][code] = weather
                results['summary']['successful_requests'] += 1
            else:
                results['summary']['failed_requests'] += 1
            
            # Rate limiting - pausa breve entre requests
            time.sleep(0.1)
        
        return results

def test_weather_api():
    """Función de prueba para la API meteorológica"""
    print("🌤️  Probando OpenWeatherMap API...")
    
    weather_api = WeatherAPI()
    
    # Probar aeropuertos mexicanos principales
    test_airports = ['NLU', 'MEX', 'CUN', 'GDL']
    
    print("\n📍 Clima actual en aeropuertos mexicanos:")
    for airport in test_airports:
        weather = weather_api.get_current_weather(airport)
        if weather:
            curr = weather['current']
            cond = weather['conditions']
            print(f"{airport} ({weather['airport_name']}):")
            print(f"  🌡️  {curr['temperature']}°C - {curr['weather']['description']}")
            print(f"  💨 Viento: {curr['wind']['speed']} m/s")
            print(f"  ✈️  Estado vuelo: {cond['overall_status']} - {cond['flight_impact']} impacto")
        else:
            print(f"{airport}: ❌ Error obteniendo datos")
        print()
    
    # Probar ruta específica
    print("🛫 Analizando ruta AIFA -> Cancún:")
    route_weather = weather_api.get_route_weather('NLU', 'CUN')
    if route_weather and route_weather['origin'] and route_weather['destination']:
        analysis = route_weather['route_analysis']
        print(f"  Estado general: {analysis['overall_status']}")
        print(f"  Impacto en vuelo: {analysis['flight_impact']}")
        print("  Recomendaciones:")
        for rec in analysis['recommendations']:
            print(f"    • {rec}")

if __name__ == "__main__":
    test_weather_api()