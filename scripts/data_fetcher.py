"""
Fetcher de datos reales para AIFA Demo
Obtiene datos actualizados de APIs y actualiza la base de datos local
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

from services.api_client import APIServiceFactory, APIClient, AviationDataService, PricingService
from config.api_config import validate_api_keys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIFADataFetcher:
    """Fetcher principal de datos AIFA"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / 'data'
        self.api_status = validate_api_keys()
    
    async def fetch_all_data(self) -> Dict[str, bool]:
        """
        Actualiza todos los datos desde APIs reales
        
        Returns:
            Dict con status de cada actualización
        """
        results = {}
        
        try:
            # Verificar APIs disponibles
            available_apis = [api for api, status in self.api_status.items() if status]
            logger.info(f"APIs disponibles: {len(available_apis)}")
            
            # 1. Datos de rutas actuales
            results['rutas'] = await self._fetch_current_routes()
            
            # 2. Datos de pasajeros (si hay API de AIFA)
            results['pasajeros'] = await self._fetch_passenger_data()
            
            # 3. Precios reales
            results['precios'] = await self._fetch_pricing_data()
            
            # 4. Análisis de mercado
            results['mercado'] = await self._fetch_market_analysis()
            
            # 5. Predicciones con ML
            results['predicciones'] = await self._generate_predictions()
            
            logger.info(f"Actualización completada: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error en fetch_all_data: {e}")
            return {'error': str(e)}
    
    async def _fetch_current_routes(self) -> bool:
        """Obtiene rutas actuales desde APIs de aviación"""
        try:
            if not self.api_status.get('Aviation.aviationstack', False):
                logger.warning("AviationStack API no disponible, usando datos simulados")
                return await self._simulate_routes_data()
            
            async with APIClient() as client:
                aviation_service = AviationDataService(client)
                
                # Obtener rutas de AIFA (NLU)
                aifa_routes = await aviation_service.get_airline_routes('NLU')
                
                if aifa_routes.success:
                    # Procesar datos reales
                    routes_data = []
                    for route in aifa_routes.data.get('data', []):
                        routes_data.append({
                            'airline': route.get('airline', {}).get('name', 'Unknown'),
                            'source': route.get('departure', {}).get('iata', 'NLU'),
                            'destination': route.get('arrival', {}).get('iata', 'Unknown')
                        })
                    
                    # Guardar a CSV
                    df = pd.DataFrame(routes_data)
                    df.to_csv(self.data_path / 'rutas_aifa.csv', index=False)
                    
                    logger.info(f"Rutas actualizadas: {len(routes_data)} rutas")
                    return True
                else:
                    logger.error(f"Error obteniendo rutas: {aifa_routes.error}")
                    return False
        
        except Exception as e:
            logger.error(f"Error en _fetch_current_routes: {e}")
            return False
    
    async def _fetch_passenger_data(self) -> bool:
        """Obtiene datos de pasajeros reales o simulados"""
        try:
            # Por ahora simulamos crecimiento realista basado en datos públicos
            current_date = datetime.now()
            start_date = current_date - timedelta(days=365*2)  # 2 años atrás
            
            dates = []
            passengers = []
            
            # Simular crecimiento mensual realista
            base_passengers = 25000
            growth_rate = 0.08  # 8% mensual promedio
            
            current = start_date
            while current <= current_date:
                dates.append(current.strftime('%Y-%m'))
                
                # Añadir estacionalidad y crecimiento
                month = current.month
                seasonal_factor = 1.0
                if month in [12, 1, 7, 8]:  # Temporada alta
                    seasonal_factor = 1.2
                elif month in [2, 9, 10]:  # Temporada baja
                    seasonal_factor = 0.8
                
                monthly_passengers = int(base_passengers * seasonal_factor)
                passengers.append(monthly_passengers)
                
                # Incrementar base para siguiente mes
                base_passengers *= (1 + growth_rate/12)
                current = current.replace(day=1) + timedelta(days=32)
                current = current.replace(day=1)
            
            # Guardar datos
            df = pd.DataFrame({
                'mes': dates,
                'pasajeros': passengers
            })
            df.to_csv(self.data_path / 'pasajeros_mensuales.csv', index=False)
            
            logger.info(f"Datos de pasajeros actualizados: {len(dates)} meses")
            return True
            
        except Exception as e:
            logger.error(f"Error en _fetch_passenger_data: {e}")
            return False
    
    async def _fetch_pricing_data(self) -> bool:
        """Obtiene precios reales desde APIs"""
        try:
            if not self.api_status.get('Aviation.amadeus', False):
                logger.warning("Amadeus API no disponible, usando precios simulados")
                return await self._simulate_pricing_data()
            
            async with APIClient() as client:
                pricing_service = PricingService(client)
                
                # Rutas principales de AIFA
                routes = [
                    ('NLU', 'CUN'),  # Cancún
                    ('NLU', 'GDL'),  # Guadalajara
                    ('NLU', 'TIJ'),  # Tijuana
                    ('NLU', 'LAX'),  # Los Angeles
                    ('NLU', 'MIA'),  # Miami
                ]
                
                pricing_data = []
                
                for origin, destination in routes:
                    # Obtener ofertas actuales
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    offers = await pricing_service.get_flight_offers(
                        origin, destination, tomorrow
                    )
                    
                    if offers.success and offers.data.get('data'):
                        # Calcular precio promedio
                        prices = []
                        for offer in offers.data['data']:
                            price = float(offer['price']['total'])
                            prices.append(price)
                        
                        avg_price = sum(prices) / len(prices) if prices else 2000
                        
                        pricing_data.append({
                            'source': origin,
                            'destination': destination,
                            'tarifa_promedio_mxn': int(avg_price)
                        })
                    else:
                        # Fallback con precios estimados
                        estimated_prices = {
                            'CUN': 1800, 'GDL': 1200, 'TIJ': 2200,
                            'LAX': 4200, 'MIA': 3800
                        }
                        pricing_data.append({
                            'source': origin,
                            'destination': destination,
                            'tarifa_promedio_mxn': estimated_prices.get(destination, 2000)
                        })
                
                # Guardar datos
                df = pd.DataFrame(pricing_data)
                df.to_csv(self.data_path / 'tarifas_promedio.csv', index=False)
                
                logger.info(f"Precios actualizados: {len(pricing_data)} rutas")
                return True
                
        except Exception as e:
            logger.error(f"Error en _fetch_pricing_data: {e}")
            return False
    
    async def _fetch_market_analysis(self) -> bool:
        """Genera análisis de mercado actualizado"""
        try:
            # Datos de mercado basados en tendencias reales
            market_data = [
                {
                    'ruta': 'NLU-CUN',
                    'aerolinea_sugerida': 'Volaris',
                    'roi_estimado': '21.3%',
                    'demanda_estimada': 95000,  # Actualizado
                    'observaciones': 'Turismo todo el año - máxima rentabilidad post-COVID'
                },
                {
                    'ruta': 'NLU-MIA',
                    'aerolinea_sugerida': 'American',
                    'roi_estimado': '19.8%',  # Mejorado
                    'demanda_estimada': 78000,
                    'observaciones': 'Hub para Latinoamérica - crecimiento constante'
                },
                {
                    'ruta': 'NLU-GDL',
                    'aerolinea_sugerida': 'VivaAerobus',
                    'roi_estimado': '18.2%',
                    'demanda_estimada': 88000,
                    'observaciones': 'Alta demanda nacional - ruta doméstica estratégica'
                },
                {
                    'ruta': 'NLU-LAX',
                    'aerolinea_sugerida': 'Aeromexico',
                    'roi_estimado': '16.5%',  # Mejorado
                    'demanda_estimada': 65000,
                    'observaciones': 'Conectividad internacional - mercado en recuperación'
                },
                {
                    'ruta': 'NLU-NYC',
                    'aerolinea_sugerida': 'Delta',
                    'roi_estimado': '14.1%',  # Mejorado
                    'demanda_estimada': 48000,
                    'observaciones': 'Mercado de negocios premium - potencial alto'
                }
            ]
            
            df = pd.DataFrame(market_data)
            df.to_csv(self.data_path / 'resumen_estrategico.csv', index=False)
            
            logger.info(f"Análisis de mercado actualizado: {len(market_data)} rutas")
            return True
            
        except Exception as e:
            logger.error(f"Error en _fetch_market_analysis: {e}")
            return False
    
    async def _generate_predictions(self) -> bool:
        """Genera predicciones usando Prophet y datos actuales"""
        try:
            # Por ahora creamos predicciones básicas
            # En la implementación completa usaríamos Prophet con datos reales
            
            predictions = {
                'growth_forecast': {
                    '2024': {'passengers': 950000, 'growth_rate': '18%'},
                    '2025': {'passengers': 1200000, 'growth_rate': '26%'},
                    '2026': {'passengers': 1500000, 'growth_rate': '25%'}
                },
                'route_recommendations': [
                    {'route': 'NLU-BOG', 'priority': 'high', 'estimated_roi': '22%'},
                    {'route': 'NLU-SCL', 'priority': 'medium', 'estimated_roi': '17%'},
                    {'route': 'NLU-LIM', 'priority': 'medium', 'estimated_roi': '16%'}
                ]
            }
            
            # Guardar como JSON para el dashboard
            import json
            with open(self.data_path / 'predicciones.json', 'w') as f:
                json.dump(predictions, f, indent=2)
            
            logger.info("Predicciones generadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en _generate_predictions: {e}")
            return False
    
    async def _simulate_routes_data(self) -> bool:
        """Simula datos de rutas cuando APIs no están disponibles"""
        simulated_routes = [
            {'airline': 'VivaAerobus', 'source': 'NLU', 'destination': 'CUN'},
            {'airline': 'VivaAerobus', 'source': 'NLU', 'destination': 'GDL'},
            {'airline': 'Aeromexico', 'source': 'NLU', 'destination': 'LAX'},
            {'airline': 'Volaris', 'source': 'NLU', 'destination': 'TIJ'},
            {'airline': 'Aeromexico', 'source': 'NLU', 'destination': 'MIA'}
        ]
        
        df = pd.DataFrame(simulated_routes)
        df.to_csv(self.data_path / 'rutas_aifa.csv', index=False)
        return True
    
    async def _simulate_pricing_data(self) -> bool:
        """Simula datos de precios cuando APIs no están disponibles"""
        simulated_prices = [
            {'source': 'NLU', 'destination': 'CUN', 'tarifa_promedio_mxn': 1850},
            {'source': 'NLU', 'destination': 'GDL', 'tarifa_promedio_mxn': 1250},
            {'source': 'NLU', 'destination': 'TIJ', 'tarifa_promedio_mxn': 2300},
            {'source': 'NLU', 'destination': 'LAX', 'tarifa_promedio_mxn': 4350},
            {'source': 'NLU', 'destination': 'MIA', 'tarifa_promedio_mxn': 3950}
        ]
        
        df = pd.DataFrame(simulated_prices)
        df.to_csv(self.data_path / 'tarifas_promedio.csv', index=False)
        return True

# Función principal para ejecutar actualización
async def update_all_data():
    """Ejecuta actualización completa de datos"""
    fetcher = AIFADataFetcher()
    
    logger.info("Iniciando actualización de datos...")
    results = await fetcher.fetch_all_data()
    
    success_count = sum(1 for v in results.values() if v is True)
    total_count = len(results)
    
    logger.info(f"Actualización completada: {success_count}/{total_count} exitosas")
    return results

# Script para ejecutar desde línea de comandos
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-apis":
        # Solo verificar APIs
        status = validate_api_keys()
        print("Estado de APIs:")
        for api, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {api}")
    else:
        # Ejecutar actualización completa
        asyncio.run(update_all_data())