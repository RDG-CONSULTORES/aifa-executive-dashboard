"""
Simulador de Datos Meteorológicos para AIFA Demo
Simula condiciones meteorológicas realistas mientras se obtiene token válido de OpenWeatherMap
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math

class WeatherSimulator:
    """Simulador de condiciones meteorológicas realistas"""
    
    def __init__(self):
        # Coordenadas de aeropuertos principales mexicanos
        self.airports = {
            'NLU': {'name': 'AIFA - Felipe Ángeles', 'lat': 19.7411, 'lon': -99.0183, 'elevation': 2200},
            'MEX': {'name': 'CDMX - Benito Juárez', 'lat': 19.4363, 'lon': -99.0721, 'elevation': 2230},
            'CUN': {'name': 'Cancún', 'lat': 21.0364, 'lon': -86.8771, 'elevation': 10},
            'GDL': {'name': 'Guadalajara', 'lat': 20.5218, 'lon': -103.311, 'elevation': 1566},
            'TIJ': {'name': 'Tijuana', 'lat': 32.5411, 'lon': -116.970, 'elevation': 160},
            'LAX': {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'elevation': 38},
            'MIA': {'name': 'Miami', 'lat': 25.7617, 'lon': -80.1918, 'elevation': 2},
            'MAD': {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038, 'elevation': 610},
            'LHR': {'name': 'Londres Heathrow', 'lat': 51.4700, 'lon': -0.4543, 'elevation': 25}
        }
        
        # Patrones climáticos por región/época
        self.weather_patterns = {
            'tropical': ['clear', 'partly_cloudy', 'thunderstorm', 'rain'],
            'temperate': ['clear', 'cloudy', 'overcast', 'rain', 'drizzle'],
            'desert': ['clear', 'sunny', 'dust', 'partly_cloudy'],
            'mountain': ['clear', 'cloudy', 'fog', 'snow', 'rain']
        }
        
        # Seed para consistencia en demos
        random.seed(42)
    
    def get_current_weather(self, airport_code: str) -> Optional[Dict]:
        """
        Simula clima actual para un aeropuerto
        
        Args:
            airport_code: Código IATA del aeropuerto
            
        Returns:
            Dict con datos meteorológicos simulados
        """
        if airport_code not in self.airports:
            return None
            
        airport = self.airports[airport_code]
        
        # Generar condiciones realistas basadas en ubicación y época
        weather_data = self._generate_realistic_weather(airport)
        
        processed_data = {
            'airport_code': airport_code,
            'airport_name': airport['name'],
            'timestamp': datetime.now().isoformat(),
            'coordinates': {
                'lat': airport['lat'],
                'lon': airport['lon']
            },
            'current': weather_data,
            'conditions': self._analyze_flight_conditions(weather_data),
            'data_source': 'simulated'  # Identificar datos simulados
        }
        
        return processed_data
    
    def _generate_realistic_weather(self, airport: Dict) -> Dict:
        """Genera condiciones meteorológicas realistas por ubicación"""
        
        # Factores por ubicación
        lat = airport['lat']
        elevation = airport['elevation']
        
        # Temperatura base por latitud y elevación
        base_temp = 30 - abs(lat) * 0.5 - elevation * 0.006
        temp_variation = random.uniform(-8, 8)
        temperature = round(base_temp + temp_variation, 1)
        
        # Humedad (mayor en trópicos y costas)
        if abs(lat) < 25:  # Trópicos
            humidity = random.randint(60, 95)
        else:  # Templado
            humidity = random.randint(40, 80)
        
        # Presión (ajustada por elevación)
        sea_level_pressure = random.uniform(1010, 1025)
        pressure = round(sea_level_pressure * (1 - 0.0065 * elevation / 288.15) ** 5.255, 1)
        
        # Viento (más fuerte en costas y montañas)
        if elevation > 1000 or abs(lat) > 30:
            wind_speed = random.uniform(2, 18)
        else:
            wind_speed = random.uniform(1, 12)
        
        # Visibilidad
        visibility = random.choice([10, 10, 10, 8, 6, 4])  # Mayoría buena visibilidad
        
        # Condiciones meteorológicas
        weather_conditions = self._select_weather_condition(airport)
        
        return {
            'temperature': temperature,
            'feels_like': round(temperature + random.uniform(-3, 3), 1),
            'humidity': humidity,
            'pressure': pressure,
            'visibility': visibility,
            'weather': weather_conditions,
            'wind': {
                'speed': round(wind_speed, 1),
                'direction': random.randint(0, 360),
                'gust': round(wind_speed * random.uniform(1.2, 1.8), 1) if wind_speed > 8 else 0
            },
            'clouds': random.randint(0, 100)
        }
    
    def _select_weather_condition(self, airport: Dict) -> Dict:
        """Selecciona condición meteorológica realista"""
        
        lat = airport['lat']
        elevation = airport['elevation']
        
        # Determinar región climática
        if abs(lat) < 25 and elevation < 500:
            region = 'tropical'
        elif elevation > 1500:
            region = 'mountain'
        elif abs(lat) > 35:
            region = 'temperate'
        else:
            region = 'temperate'
        
        # Condiciones más probables por región
        conditions = {
            'tropical': {
                'Clear': {'prob': 0.4, 'desc': 'cielo despejado'},
                'Clouds': {'prob': 0.3, 'desc': 'parcialmente nublado'},
                'Rain': {'prob': 0.2, 'desc': 'lluvia ligera'},
                'Thunderstorm': {'prob': 0.1, 'desc': 'tormenta eléctrica'}
            },
            'temperate': {
                'Clear': {'prob': 0.5, 'desc': 'cielo despejado'},
                'Clouds': {'prob': 0.35, 'desc': 'nublado'},
                'Rain': {'prob': 0.1, 'desc': 'lluvia'},
                'Drizzle': {'prob': 0.05, 'desc': 'llovizna'}
            },
            'mountain': {
                'Clear': {'prob': 0.4, 'desc': 'cielo despejado'},
                'Clouds': {'prob': 0.4, 'desc': 'nublado'},
                'Fog': {'prob': 0.15, 'desc': 'niebla'},
                'Rain': {'prob': 0.05, 'desc': 'lluvia'}
            }
        }
        
        # Seleccionar condición basada en probabilidades
        rand = random.random()
        cumulative = 0
        
        for condition, data in conditions[region].items():
            cumulative += data['prob']
            if rand <= cumulative:
                return {
                    'main': condition,
                    'description': data['desc'],
                    'icon': self._get_weather_icon(condition)
                }
        
        # Fallback
        return {'main': 'Clear', 'description': 'cielo despejado', 'icon': '01d'}
    
    def _get_weather_icon(self, condition: str) -> str:
        """Mapea condición a icono de OpenWeatherMap"""
        icon_map = {
            'Clear': '01d',
            'Clouds': '03d',
            'Rain': '10d',
            'Thunderstorm': '11d',
            'Drizzle': '09d',
            'Fog': '50d',
            'Snow': '13d'
        }
        return icon_map.get(condition, '01d')
    
    def _analyze_flight_conditions(self, weather_data: Dict) -> Dict:
        """
        Analiza condiciones de vuelo basado en datos meteorológicos
        
        Args:
            weather_data: Datos meteorológicos simulados
            
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
        visibility = weather_data['visibility']
        if visibility < 1:
            conditions['visibility_status'] = 'poor'
            conditions['recommendations'].append('Visibilidad reducida - procedimientos IFR requeridos')
        elif visibility < 3:
            conditions['visibility_status'] = 'limited'
            conditions['recommendations'].append('Visibilidad limitada - precaución extra')
        
        # Analizar viento
        wind_speed = weather_data['wind']['speed']
        wind_gust = weather_data['wind']['gust']
        
        if wind_speed > 15 or wind_gust > 20:
            conditions['wind_status'] = 'strong'
            conditions['recommendations'].append('Vientos fuertes - posibles retrasos')
        elif wind_speed > 10:
            conditions['wind_status'] = 'moderate'
        
        # Analizar condiciones generales
        weather_main = weather_data['weather']['main'].lower()
        
        if weather_main in ['thunderstorm']:
            conditions['weather_status'] = 'severe'
            conditions['flight_impact'] = 'high'
            conditions['recommendations'].append('Condiciones severas - vuelos pueden cancelarse')
        elif weather_main in ['rain', 'drizzle']:
            conditions['weather_status'] = 'adverse'
            conditions['flight_impact'] = 'moderate'
            conditions['recommendations'].append('Precipitación - posibles retrasos menores')
        elif weather_main in ['fog']:
            conditions['weather_status'] = 'reduced_visibility'
            conditions['flight_impact'] = 'moderate'
            conditions['recommendations'].append('Niebla - operaciones IFR')
        
        # Status general
        if conditions['weather_status'] == 'severe' or conditions['visibility_status'] == 'poor':
            conditions['overall_status'] = 'poor'
        elif conditions['weather_status'] == 'adverse' or conditions['wind_status'] == 'strong':
            conditions['overall_status'] = 'caution'
        
        return conditions
    
    def get_route_weather(self, origin: str, destination: str) -> Dict:
        """
        Simula clima para una ruta completa
        
        Args:
            origin: Código IATA aeropuerto origen
            destination: Código IATA aeropuerto destino
            
        Returns:
            Dict con clima de origen y destino simulados
        """
        origin_weather = self.get_current_weather(origin)
        dest_weather = self.get_current_weather(destination)
        
        return {
            'route': f"{origin}-{destination}",
            'timestamp': datetime.now().isoformat(),
            'origin': origin_weather,
            'destination': dest_weather,
            'route_analysis': self._analyze_route_conditions(origin_weather, dest_weather),
            'data_source': 'simulated'
        }
    
    def _analyze_route_conditions(self, origin_weather: Dict, dest_weather: Dict) -> Dict:
        """Analiza condiciones de ruta completa"""
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
        Simula clima para múltiples aeropuertos
        
        Args:
            airport_codes: Lista de códigos IATA
            
        Returns:
            Dict con clima simulado de todos los aeropuertos
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'airports': {},
            'summary': {
                'total_airports': len(airport_codes),
                'successful_requests': len(airport_codes),
                'failed_requests': 0
            },
            'data_source': 'simulated'
        }
        
        for code in airport_codes:
            weather = self.get_current_weather(code)
            if weather:
                results['airports'][code] = weather
        
        return results

def test_weather_simulator():
    """Función de prueba para el simulador meteorológico"""
    print("🌤️  Probando Simulador Meteorológico...")
    print("📝 NOTA: Datos simulados - para pruebas mientras obtienes token válido de OpenWeatherMap\n")
    
    weather_sim = WeatherSimulator()
    
    # Probar aeropuertos mexicanos principales
    test_airports = ['NLU', 'MEX', 'CUN', 'GDL']
    
    print("📍 Clima actual simulado en aeropuertos mexicanos:")
    for airport in test_airports:
        weather = weather_sim.get_current_weather(airport)
        if weather:
            curr = weather['current']
            cond = weather['conditions']
            print(f"{airport} ({weather['airport_name']}):")
            print(f"  🌡️  {curr['temperature']}°C - {curr['weather']['description']}")
            print(f"  💨 Viento: {curr['wind']['speed']} m/s")
            print(f"  👁️  Visibilidad: {curr['visibility']} km")
            print(f"  ✈️  Estado vuelo: {cond['overall_status']} - {cond['flight_impact']} impacto")
            if cond['recommendations']:
                print(f"  💡 Recomendaciones: {', '.join(cond['recommendations'])}")
        print()
    
    # Probar ruta específica
    print("🛫 Analizando ruta AIFA -> Cancún:")
    route_weather = weather_sim.get_route_weather('NLU', 'CUN')
    if route_weather and route_weather['origin'] and route_weather['destination']:
        analysis = route_weather['route_analysis']
        print(f"  📊 Estado general: {analysis['overall_status']}")
        print(f"  🎯 Impacto en vuelo: {analysis['flight_impact']}")
        print("  💡 Recomendaciones:")
        for rec in analysis['recommendations']:
            print(f"    • {rec}")
    
    # Guardar datos de ejemplo
    print("\n💾 Guardando datos meteorológicos simulados...")
    weather_data = weather_sim.get_multiple_airports_weather(['NLU', 'MEX', 'CUN', 'GDL', 'TIJ'])
    
    with open('data/weather_simulation_data.json', 'w', encoding='utf-8') as f:
        json.dump(weather_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Datos guardados en: data/weather_simulation_data.json")
    print("\n🔗 Para usar datos reales, obtén un token válido de OpenWeatherMap en:")
    print("   https://openweathermap.org/api")

if __name__ == "__main__":
    test_weather_simulator()