"""
Configuración de APIs para AIFA Demo
Contiene todos los endpoints, keys y configuraciones necesarias
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class APIConfig:
    """Configuración base para APIs"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests por minuto
    requires_auth: bool = True

# APIs de Aviación
AVIATION_APIS = {
    'aviationstack': APIConfig(
        name='AviationStack',
        base_url='http://api.aviationstack.com/v1',
        api_key=os.getenv('AVIATIONSTACK_API_KEY'),
        rate_limit=1000
    ),
    
    'flightaware': APIConfig(
        name='FlightAware',
        base_url='https://aeroapi.flightaware.com/aeroapi',
        api_key=os.getenv('FLIGHTAWARE_API_KEY'),
        rate_limit=100
    ),
    
    'amadeus': APIConfig(
        name='Amadeus',
        base_url='https://api.amadeus.com/v1',
        api_key=os.getenv('AMADEUS_API_KEY'),
        rate_limit=10
    )
}

# APIs de Datos Económicos y Meteorológicos
ECONOMIC_APIS = {
    'google_trends': APIConfig(
        name='Google Trends',
        base_url='https://trends.googleapis.com/trends/api',
        requires_auth=False,
        rate_limit=100
    ),
    
    'world_bank': APIConfig(
        name='World Bank',
        base_url='https://api.worldbank.org/v2',
        requires_auth=False,
        rate_limit=120
    ),
    
    'fred': APIConfig(
        name='FRED Economic Data',
        base_url='https://api.stlouisfed.org/fred',
        api_key=os.getenv('FRED_API_KEY'),
        rate_limit=120
    ),
    
    'openweather': APIConfig(
        name='OpenWeatherMap',
        base_url='https://api.openweathermap.org/data/2.5',
        api_key='6a6e94ae482a1c310fe583b6a35eb72b',
        rate_limit=1000
    )
}

# APIs de IA
AI_APIS = {
    'openai': APIConfig(
        name='OpenAI',
        base_url='https://api.openai.com/v1',
        api_key=os.getenv('OPENAI_API_KEY'),
        rate_limit=60
    ),
    
    'claude': APIConfig(
        name='Claude (Anthropic)',
        base_url='https://api.anthropic.com/v1',
        api_key=os.getenv('CLAUDE_API_KEY'),
        rate_limit=50
    )
}

# Configuración de AIFA (datos oficiales)
AIFA_CONFIG = {
    'official_website': 'https://www.aifa.com.mx',
    'statistics_endpoint': '/estadisticas',
    'routes_endpoint': '/rutas',
    'schedule_endpoint': '/horarios'
}

# Endpoints específicos por funcionalidad
ENDPOINTS = {
    'flight_data': {
        'current_flights': '/flights',
        'historical_routes': '/routes',
        'airport_stats': '/airports/{airport_code}/stats',
        'airline_performance': '/airlines/{airline_code}/performance'
    },
    
    'pricing': {
        'flight_offers': '/shopping/flight-offers',
        'price_analysis': '/analytics/itinerary-price-metrics',
        'market_insights': '/travel/analytics/air-traffic'
    },
    
    'predictions': {
        'demand_forecast': '/forecast/demand',
        'price_prediction': '/forecast/pricing',
        'route_viability': '/analytics/route-viability'
    }
}

# Configuración de caché y límites
CACHE_CONFIG = {
    'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
    'cache_ttl': {
        'flight_data': 300,      # 5 minutos
        'pricing': 1800,         # 30 minutos
        'economic_data': 3600,   # 1 hora
        'predictions': 86400     # 24 horas
    }
}

# Configuración de autenticación
AUTH_CONFIG = {
    'jwt_secret': os.getenv('JWT_SECRET'),
    'token_expiry': 3600,  # 1 hora
    'refresh_token_expiry': 86400 * 7  # 7 días
}

def get_api_config(api_name: str, category: str = None) -> Optional[APIConfig]:
    """
    Obtiene configuración de API específica
    
    Args:
        api_name: Nombre de la API
        category: Categoría (aviation, economic, ai)
    
    Returns:
        APIConfig object o None si no existe
    """
    all_apis = {**AVIATION_APIS, **ECONOMIC_APIS, **AI_APIS}
    return all_apis.get(api_name)

def validate_api_keys() -> Dict[str, bool]:
    """
    Valida que las API keys estén configuradas
    
    Returns:
        Dict con status de cada API
    """
    status = {}
    
    for category_name, apis in [
        ('Aviation', AVIATION_APIS),
        ('Economic', ECONOMIC_APIS),
        ('AI', AI_APIS)
    ]:
        for api_name, config in apis.items():
            if config.requires_auth:
                status[f"{category_name}.{api_name}"] = config.api_key is not None
            else:
                status[f"{category_name}.{api_name}"] = True
    
    return status