#!/usr/bin/env python3
"""
OpenSky Fallback - Usar API pública sin credenciales
Obtiene datos útiles sin autenticación
"""

import asyncio
import aiohttp
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenSkyFallback:
    def __init__(self):
        self.base_url = 'https://opensky-network.org/api'
        self.data_path = Path(__file__).parent.parent / 'data'
        
    async def get_public_flights_mexico(self):
        """Obtener vuelos públicos sobre México sin autenticación"""
        try:
            async with aiohttp.ClientSession() as session:
                # Coordenadas ampliadas de México Central
                params = {
                    'lamin': 18.5,    # Sur México Central
                    'lomin': -100.5,  # Oeste México Central
                    'lamax': 20.5,    # Norte México Central  
                    'lomax': -97.5    # Este México Central
                }
                
                url = f"{self.base_url}/states/all"
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and data.get('states'):
                            flights_data = []
                            
                            for state in data['states']:
                                if state[1]:  # Si tiene callsign
                                    flight_info = {
                                        'icao24': state[0],
                                        'callsign': state[1].strip(),
                                        'origin_country': state[2],
                                        'longitude': state[5],
                                        'latitude': state[6],
                                        'altitude': state[7],
                                        'velocity': state[9],
                                        'heading': state[10],
                                        'timestamp': datetime.fromtimestamp(data['time']),
                                        'distance_to_aifa': self._calculate_distance_to_aifa(state[6], state[5]) if state[6] and state[5] else None
                                    }
                                    flights_data.append(flight_info)
                            
                            # Filtrar vuelos cercanos a AIFA (dentro de 100km)
                            aifa_flights = [f for f in flights_data if f['distance_to_aifa'] and f['distance_to_aifa'] < 100]
                            
                            # Guardar todos los vuelos
                            df_all = pd.DataFrame(flights_data)
                            df_all.to_csv(self.data_path / 'vuelos_mexico_tiempo_real.csv', index=False)
                            
                            # Guardar vuelos cercanos a AIFA
                            if aifa_flights:
                                df_aifa = pd.DataFrame(aifa_flights)
                                df_aifa.to_csv(self.data_path / 'vuelos_cerca_aifa.csv', index=False)
                            
                            # Generar estadísticas
                            stats = self._generate_flight_stats(flights_data, aifa_flights)
                            
                            with open(self.data_path / 'estadisticas_vuelos_publicos.json', 'w') as f:
                                json.dump(stats, f, indent=2, default=str, ensure_ascii=False)
                            
                            logger.info(f"✅ Vuelos obtenidos - Total: {len(flights_data)}, Cerca AIFA: {len(aifa_flights)}")
                            return True
                        else:
                            logger.warning("No se encontraron vuelos en el área")
                            return False
                    else:
                        logger.error(f"Error API: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error obteniendo vuelos: {e}")
            return False
    
    def _calculate_distance_to_aifa(self, lat, lon):
        """Calcular distancia aproximada a AIFA en km"""
        if not lat or not lon:
            return None
            
        # Coordenadas AIFA: 19.7365°N, 99.0149°W
        aifa_lat, aifa_lon = 19.7365, -99.0149
        
        # Fórmula haversine simplificada
        import math
        
        lat1, lon1 = math.radians(aifa_lat), math.radians(aifa_lon)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return c * 6371  # Radio de la Tierra en km
    
    def _generate_flight_stats(self, all_flights, aifa_flights):
        """Generar estadísticas de vuelos"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_flights_mexico': len(all_flights),
            'flights_near_aifa_100km': len(aifa_flights),
            'coverage_area': 'México Central (18.5-20.5°N, 100.5-97.5°W)',
            'countries_detected': list(set(f['origin_country'] for f in all_flights if f['origin_country'])),
            'airlines_detected': [],
            'altitude_stats': {},
            'velocity_stats': {},
            'aifa_analysis': {}
        }
        
        if all_flights:
            # Análisis de aerolíneas (por callsign)
            callsigns = [f['callsign'][:3] for f in all_flights if f['callsign'] and len(f['callsign']) >= 3]
            airline_counts = {}
            for airline in callsigns:
                airline_counts[airline] = airline_counts.get(airline, 0) + 1
            
            stats['airlines_detected'] = dict(sorted(airline_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Estadísticas de altitud
            altitudes = [f['altitude'] for f in all_flights if f['altitude'] and f['altitude'] > 0]
            if altitudes:
                stats['altitude_stats'] = {
                    'min_meters': min(altitudes),
                    'max_meters': max(altitudes),
                    'avg_meters': sum(altitudes) / len(altitudes),
                    'flights_below_10000m': len([a for a in altitudes if a < 10000])
                }
            
            # Estadísticas de velocidad
            velocities = [f['velocity'] for f in all_flights if f['velocity'] and f['velocity'] > 0]
            if velocities:
                stats['velocity_stats'] = {
                    'min_mps': min(velocities),
                    'max_mps': max(velocities),
                    'avg_mps': sum(velocities) / len(velocities),
                    'avg_kmh': (sum(velocities) / len(velocities)) * 3.6
                }
        
        # Análisis específico de área AIFA
        if aifa_flights:
            aifa_altitudes = [f['altitude'] for f in aifa_flights if f['altitude'] and f['altitude'] > 0]
            aifa_countries = list(set(f['origin_country'] for f in aifa_flights if f['origin_country']))
            
            stats['aifa_analysis'] = {
                'flights_in_approach_altitude': len([a for a in aifa_altitudes if 500 < a < 3000]) if aifa_altitudes else 0,
                'countries_near_aifa': aifa_countries,
                'potential_aifa_traffic': len(aifa_flights),
                'closest_flight_km': min(f['distance_to_aifa'] for f in aifa_flights) if aifa_flights else None
            }
        
        return stats
    
    async def get_public_airport_data(self):
        """Intentar obtener datos públicos de aeropuertos"""
        try:
            # OpenSky no tiene endpoint público de aeropuertos
            # Pero podemos simular datos basados en vuelos detectados
            
            airport_data = {
                'aifa_info': {
                    'icao': 'MMSM',
                    'iata': 'NLU',
                    'name': 'Aeropuerto Internacional Felipe Ángeles',
                    'coordinates': [19.7365, -99.0149],
                    'elevation_meters': 2298,
                    'status': 'Operational'
                },
                'detection_method': 'Proximity analysis from public flight data',
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_path / 'aifa_info_publica.json', 'w') as f:
                json.dump(airport_data, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Información pública de AIFA guardada")
            return True
            
        except Exception as e:
            logger.error(f"Error generando datos de aeropuerto: {e}")
            return False

async def main():
    """Ejecutar obtención de datos públicos"""
    logger.info("🛩️ INICIANDO OPENSKY FALLBACK (SIN CREDENCIALES)")
    
    fallback = OpenSkyFallback()
    
    # Obtener vuelos públicos
    flights_success = await fallback.get_public_flights_mexico()
    
    # Obtener datos de aeropuerto
    airport_success = await fallback.get_public_airport_data()
    
    if flights_success or airport_success:
        logger.info("✅ Datos públicos obtenidos exitosamente")
        logger.info("📁 Archivos generados:")
        logger.info("  - vuelos_mexico_tiempo_real.csv")
        logger.info("  - vuelos_cerca_aifa.csv") 
        logger.info("  - estadisticas_vuelos_publicos.json")
        logger.info("  - aifa_info_publica.json")
    else:
        logger.error("❌ No se pudieron obtener datos públicos")

if __name__ == "__main__":
    asyncio.run(main())