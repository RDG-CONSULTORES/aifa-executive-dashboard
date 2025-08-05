"""
Cliente unificado para todas las APIs de AIFA Demo
Maneja autenticación, rate limiting, caché y errores
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib

from config.api_config import get_api_config, CACHE_CONFIG

@dataclass
class APIResponse:
    """Respuesta estándar de API"""
    success: bool
    data: Any
    error: Optional[str] = None
    cached: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RateLimiter:
    """Control de rate limiting por API"""
    
    def __init__(self):
        self._requests = {}
        self._windows = {}
    
    async def wait_if_needed(self, api_name: str, limit: int = 100):
        """Espera si es necesario para respetar rate limits"""
        now = time.time()
        window_start = now - 60  # ventana de 1 minuto
        
        if api_name not in self._requests:
            self._requests[api_name] = []
        
        # Limpiar requests antiguos
        self._requests[api_name] = [
            req_time for req_time in self._requests[api_name] 
            if req_time > window_start
        ]
        
        # Verificar si necesitamos esperar
        if len(self._requests[api_name]) >= limit:
            wait_time = self._requests[api_name][0] - window_start
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Registrar nueva request
        self._requests[api_name].append(now)

class APICache:
    """Caché simple en memoria para responses"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Genera key única para caché"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Dict = None, ttl: int = 300) -> Optional[Any]:
        """Obtiene valor del caché si está vigente"""
        cache_key = self._get_cache_key(endpoint, params)
        
        if cache_key in self._cache:
            timestamp = self._timestamps.get(cache_key)
            if timestamp and (datetime.now() - timestamp).seconds < ttl:
                return self._cache[cache_key]
            else:
                # Expiró, limpiar
                del self._cache[cache_key]
                if cache_key in self._timestamps:
                    del self._timestamps[cache_key]
        
        return None
    
    def set(self, endpoint: str, data: Any, params: Dict = None):
        """Guarda valor en caché"""
        cache_key = self._get_cache_key(endpoint, params)
        self._cache[cache_key] = data
        self._timestamps[cache_key] = datetime.now()

class APIClient:
    """Cliente unificado para todas las APIs"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.cache = APICache()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def request(
        self, 
        api_name: str, 
        endpoint: str, 
        method: str = 'GET',
        params: Dict = None,
        headers: Dict = None,
        use_cache: bool = True
    ) -> APIResponse:
        """
        Realiza request a API específica
        
        Args:
            api_name: Nombre de la API (ej: 'aviationstack')
            endpoint: Endpoint específico
            method: Método HTTP
            params: Parámetros de query
            headers: Headers adicionales
            use_cache: Si usar caché
        
        Returns:
            APIResponse con resultado
        """
        try:
            # Obtener configuración de API
            config = get_api_config(api_name)
            if not config:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"API '{api_name}' no configurada"
                )
            
            # Verificar caché primero
            if use_cache and method == 'GET':
                cached_data = self.cache.get(
                    f"{api_name}:{endpoint}", 
                    params,
                    CACHE_CONFIG['cache_ttl'].get(api_name, 300)
                )
                if cached_data:
                    return APIResponse(
                        success=True,
                        data=cached_data,
                        cached=True
                    )
            
            # Rate limiting
            await self.rate_limiter.wait_if_needed(api_name, config.rate_limit)
            
            # Preparar request
            url = f"{config.base_url}{endpoint}"
            request_headers = headers or {}
            
            # Agregar autenticación
            if config.requires_auth and config.api_key:
                if api_name == 'aviationstack':
                    params = params or {}
                    params['access_key'] = config.api_key
                elif api_name in ['openai', 'claude']:
                    request_headers['Authorization'] = f"Bearer {config.api_key}"
                elif api_name == 'amadeus':
                    request_headers['Authorization'] = f"Bearer {config.api_key}"
            
            # Ejecutar request
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                headers=request_headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Guardar en caché
                    if use_cache and method == 'GET':
                        self.cache.set(f"{api_name}:{endpoint}", data, params)
                    
                    return APIResponse(
                        success=True,
                        data=data
                    )
                else:
                    error_text = await response.text()
                    return APIResponse(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_text}"
                    )
        
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                error=str(e)
            )

class AviationDataService:
    """Servicio específico para datos de aviación"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    async def get_airport_info(self, airport_code: str) -> APIResponse:
        """Obtiene información de aeropuerto"""
        return await self.client.request(
            api_name='aviationstack',
            endpoint='/airports',
            params={'search': airport_code}
        )
    
    async def get_airline_routes(self, airline_code: str) -> APIResponse:
        """Obtiene rutas de aerolínea"""
        return await self.client.request(
            api_name='aviationstack',
            endpoint='/routes',
            params={'airline_iata': airline_code}
        )
    
    async def get_flight_data(
        self, 
        departure: str, 
        arrival: str, 
        date: str = None
    ) -> APIResponse:
        """Obtiene datos de vuelos entre aeropuertos"""
        params = {
            'dep_iata': departure,
            'arr_iata': arrival
        }
        if date:
            params['flight_date'] = date
        
        return await self.client.request(
            api_name='aviationstack',
            endpoint='/flights',
            params=params
        )

class PricingService:
    """Servicio para datos de precios"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    async def get_flight_offers(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str,
        adults: int = 1
    ) -> APIResponse:
        """Obtiene ofertas de vuelos"""
        return await self.client.request(
            api_name='amadeus',
            endpoint='/shopping/flight-offers',
            params={
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': adults
            }
        )
    
    async def get_price_analysis(
        self, 
        origin: str, 
        destination: str
    ) -> APIResponse:
        """Obtiene análisis de precios históricos"""
        return await self.client.request(
            api_name='amadeus',
            endpoint='/analytics/itinerary-price-metrics',
            params={
                'originIataCode': origin,
                'destinationIataCode': destination,
                'departureDate': datetime.now().strftime('%Y-%m-%d')
            }
        )

class AIService:
    """Servicio para análisis con IA"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    async def analyze_route_viability(
        self, 
        route_data: Dict,
        market_data: Dict
    ) -> APIResponse:
        """Análisis inteligente de viabilidad de ruta"""
        
        prompt = f"""
        Analiza la viabilidad comercial de esta ruta aérea:
        
        Ruta: {route_data.get('origin')} → {route_data.get('destination')}
        Datos del mercado: {json.dumps(market_data, indent=2)}
        
        Proporciona:
        1. Score de viabilidad (0-100)
        2. Factores clave de éxito
        3. Riesgos principales
        4. Recomendaciones específicas
        
        Responde en formato JSON.
        """
        
        return await self.client.request(
            api_name='openai',
            endpoint='/chat/completions',
            method='POST',
            headers={'Content-Type': 'application/json'},
            params={
                'model': 'gpt-4',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.3
            }
        )

# Factory para crear servicios
class APIServiceFactory:
    """Factory para crear servicios de API"""
    
    @staticmethod
    async def create_aviation_service() -> AviationDataService:
        client = APIClient()
        await client.__aenter__()
        return AviationDataService(client)
    
    @staticmethod
    async def create_pricing_service() -> PricingService:
        client = APIClient()
        await client.__aenter__()
        return PricingService(client)
    
    @staticmethod
    async def create_ai_service() -> AIService:
        client = APIClient()
        await client.__aenter__()
        return AIService(client)

# Ejemplo de uso
async def example_usage():
    """Ejemplo de cómo usar los servicios"""
    
    async with APIClient() as client:
        aviation_service = AviationDataService(client)
        
        # Obtener info de AIFA
        aifa_info = await aviation_service.get_airport_info('NLU')
        print(f"AIFA Info: {aifa_info.data if aifa_info.success else aifa_info.error}")
        
        # Obtener rutas de VivaAerobus
        viva_routes = await aviation_service.get_airline_routes('VB')
        print(f"VivaAerobus routes: {len(viva_routes.data) if viva_routes.success else 'Error'}")

if __name__ == "__main__":
    asyncio.run(example_usage())