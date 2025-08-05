#!/usr/bin/env python3
"""
OpenSky Network OAuth2 Implementation
Implementación correcta usando OAuth2 Client Credentials Flow
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenSkyOAuth:
    def __init__(self):
        self.client_id = os.getenv('OPENSKY_CLIENT_ID')
        self.client_secret = os.getenv('OPENSKY_CLIENT_SECRET')
        self.auth_url = 'https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token'
        self.api_base = 'https://opensky-network.org/api'
        self.data_path = Path(__file__).parent.parent / 'data'
        
        # Token cache
        self.access_token = None
        self.token_expires_at = None
        
        logger.info(f"🔐 OpenSky OAuth2 Inicializado")
        logger.info(f"Client ID: {self.client_id}")
        logger.info(f"Client Secret: {'*' * len(self.client_secret) if self.client_secret else 'None'}")
    
    async def get_access_token(self, session):
        """Obtener token OAuth2 usando Client Credentials Flow"""
        try:
            # Verificar si tenemos token válido
            if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
                logger.info("🎯 Usando token válido existente")
                return self.access_token
            
            logger.info("🔄 Obteniendo nuevo token OAuth2...")
            
            # Datos para la petición de token
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with session.post(self.auth_url, data=token_data, headers=headers) as response:
                if response.status == 200:
                    token_response = await response.json()
                    
                    self.access_token = token_response.get('access_token')
                    expires_in = token_response.get('expires_in', 1800)  # 30 minutos por defecto
                    
                    # Renovar token 5 minutos antes de que expire
                    self.token_expires_at = time.time() + expires_in - 300
                    
                    logger.info(f"✅ Token OAuth2 obtenido - Expira en {expires_in} segundos")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Error obteniendo token: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error en OAuth2: {e}")
            return None
    
    async def make_authenticated_request(self, session, endpoint, params=None):
        """Hacer petición autenticada con token OAuth2"""
        try:
            # Obtener token válido
            token = await self.get_access_token(session)
            if not token:
                logger.error("❌ No se pudo obtener token de acceso")
                return None
            
            # Headers con token Bearer
            headers = {
                'Authorization': f'Bearer {token}',
                'User-Agent': 'AIFA-Route-Simulator/1.0'
            }
            
            url = f"{self.api_base}{endpoint}"
            logger.info(f"🌐 Request a: {url}")
            
            async with session.get(url, params=params, headers=headers) as response:
                logger.info(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logger.warning("🔄 Token expirado, renovando...")
                    # Forzar renovación de token
                    self.access_token = None
                    self.token_expires_at = None
                    
                    # Reintentar con nuevo token
                    token = await self.get_access_token(session)
                    if token:
                        headers['Authorization'] = f'Bearer {token}'
                        async with session.get(url, params=params, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                            else:
                                error_text = await retry_response.text()
                                logger.error(f"❌ Error en reintento: {retry_response.status} - {error_text}")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Error API: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error en request autenticado: {e}")
            return None
    
    async def get_aifa_arrivals(self, session, hours_back=24):
        """Obtener llegadas a AIFA usando OAuth2"""
        try:
            end_time = int(datetime.now().timestamp())
            begin_time = end_time - (hours_back * 3600)
            
            params = {
                'airport': 'MMSM',  # Código ICAO de AIFA
                'begin': begin_time,
                'end': end_time
            }
            
            logger.info(f"🛬 Buscando llegadas AIFA últimas {hours_back} horas...")
            data = await self.make_authenticated_request(session, '/flights/arrival', params)
            
            if data:
                logger.info(f"✅ Llegadas AIFA: {len(data)} vuelos")
                
                # Guardar datos de llegadas
                with open(self.data_path / 'aifa_arrivals_oauth.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
                
                return data
            else:
                logger.warning("⚠️ No se obtuvieron datos de llegadas")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo llegadas AIFA: {e}")
            return []
    
    async def get_aifa_departures(self, session, hours_back=24):
        """Obtener salidas de AIFA usando OAuth2"""
        try:
            end_time = int(datetime.now().timestamp())
            begin_time = end_time - (hours_back * 3600)
            
            params = {
                'airport': 'MMSM',  # Código ICAO de AIFA
                'begin': begin_time,
                'end': end_time
            }
            
            logger.info(f"🛫 Buscando salidas AIFA últimas {hours_back} horas...")
            data = await self.make_authenticated_request(session, '/flights/departure', params)
            
            if data:
                logger.info(f"✅ Salidas AIFA: {len(data)} vuelos")
                
                # Guardar datos de salidas
                with open(self.data_path / 'aifa_departures_oauth.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
                
                return data
            else:
                logger.warning("⚠️ No se obtuvieron datos de salidas")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo salidas AIFA: {e}")
            return []
    
    async def get_enhanced_states(self, session):
        """Obtener estados de aeronaves con datos mejorados (autenticado)"""
        try:
            # Coordenadas ampliadas México Central
            params = {
                'lamin': 18.5,
                'lomin': -100.5,
                'lamax': 20.5,
                'lomax': -97.5
            }
            
            logger.info("✈️ Obteniendo estados mejorados con OAuth2...")
            data = await self.make_authenticated_request(session, '/states/all', params)
            
            if data and data.get('states'):
                logger.info(f"✅ Estados mejorados: {len(data['states'])} aeronaves")
                
                # Procesar y guardar
                enhanced_flights = []
                for state in data['states']:
                    if state[1]:  # Si tiene callsign
                        flight_info = {
                            'icao24': state[0],
                            'callsign': state[1].strip(),
                            'origin_country': state[2],
                            'time_position': state[3],
                            'last_contact': state[4],
                            'longitude': state[5],
                            'latitude': state[6],
                            'baro_altitude': state[7],
                            'on_ground': state[8],
                            'velocity': state[9],
                            'true_track': state[10],
                            'vertical_rate': state[11],
                            'sensors': state[12],
                            'geo_altitude': state[13],
                            'squawk': state[14],
                            'spi': state[15],
                            'position_source': state[16],
                            'timestamp': datetime.fromtimestamp(data['time'])
                        }
                        enhanced_flights.append(flight_info)
                
                # Guardar datos mejorados
                with open(self.data_path / 'enhanced_states_oauth.json', 'w') as f:
                    json.dump(enhanced_flights, f, indent=2, default=str, ensure_ascii=False)
                
                return enhanced_flights
            else:
                logger.warning("⚠️ No se obtuvieron estados mejorados")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estados mejorados: {e}")
            return []
    
    async def generate_comprehensive_report(self, arrivals, departures, enhanced_states):
        """Generar reporte comprensivo con todos los datos OAuth2"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'data_source': 'OpenSky Network OAuth2',
                'aifa_operations': {
                    'arrivals_24h': len(arrivals),
                    'departures_24h': len(departures),
                    'total_operations': len(arrivals) + len(departures)
                },
                'enhanced_coverage': {
                    'total_aircraft': len(enhanced_states),
                    'area': 'México Central con datos OAuth2 mejorados'
                },
                'operational_analysis': {},
                'route_analysis': {},
                'airline_analysis': {}
            }
            
            # Análisis de operaciones AIFA
            all_aifa_flights = arrivals + departures
            if all_aifa_flights:
                airlines = {}
                routes = {}
                
                for flight in all_aifa_flights:
                    # Análisis de aerolíneas
                    if flight.get('callsign'):
                        airline_code = flight['callsign'][:3]
                        airlines[airline_code] = airlines.get(airline_code, 0) + 1
                    
                    # Análisis de rutas
                    if flight.get('estDepartureAirport') and flight.get('estArrivalAirport'):
                        route = f"{flight['estDepartureAirport']}-{flight['estArrivalAirport']}"
                        routes[route] = routes.get(route, 0) + 1
                
                report['airline_analysis'] = dict(sorted(airlines.items(), key=lambda x: x[1], reverse=True))
                report['route_analysis'] = dict(sorted(routes.items(), key=lambda x: x[1], reverse=True))
            
            # Análisis operacional
            if len(arrivals) > 0 or len(departures) > 0:
                total_ops = len(arrivals) + len(departures)
                report['operational_analysis'] = {
                    'operations_per_hour': round(total_ops / 24, 1),
                    'arrival_departure_ratio': round(len(arrivals) / max(len(departures), 1), 2),
                    'peak_activity_estimate': round(total_ops * 0.1, 0),
                    'operational_status': 'Active' if total_ops > 0 else 'Limited'
                }
            
            # Guardar reporte
            with open(self.data_path / 'opensky_oauth_report.json', 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Reporte OAuth2 generado - {report['aifa_operations']['total_operations']} operaciones AIFA")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return {}

async def main():
    """Ejecutar prueba completa OAuth2"""
    logger.info("🚀 INICIANDO PRUEBA OAUTH2 OPENSKY")
    
    oauth = OpenSkyOAuth()
    
    if not oauth.client_id or not oauth.client_secret:
        logger.error("❌ Credenciales faltantes")
        return
    
    async with aiohttp.ClientSession() as session:
        # Probar obtención de token
        token = await oauth.get_access_token(session)
        if not token:
            logger.error("❌ No se pudo obtener token OAuth2")
            return
        
        logger.info("✅ Token OAuth2 obtenido exitosamente")
        
        # Obtener datos de AIFA
        arrivals = await oauth.get_aifa_arrivals(session, hours_back=24)
        departures = await oauth.get_aifa_departures(session, hours_back=24)
        enhanced_states = await oauth.get_enhanced_states(session)
        
        # Generar reporte
        report = await oauth.generate_comprehensive_report(arrivals, departures, enhanced_states)
        
        # Resumen final
        logger.info("=" * 50)
        logger.info("📋 RESUMEN OAUTH2")
        logger.info("=" * 50)
        logger.info(f"✅ Llegadas AIFA: {len(arrivals)}")
        logger.info(f"✅ Salidas AIFA: {len(departures)}")
        logger.info(f"✅ Estados mejorados: {len(enhanced_states)}")
        logger.info(f"✅ Total operaciones AIFA: {len(arrivals) + len(departures)}")
        
        if len(arrivals) + len(departures) > 0:
            logger.info("🎉 OAUTH2 FUNCIONANDO - Datos históricos de AIFA obtenidos!")
        else:
            logger.info("ℹ️ Sin operaciones recientes en AIFA - Sistema funcionando correctamente")

if __name__ == "__main__":
    asyncio.run(main())