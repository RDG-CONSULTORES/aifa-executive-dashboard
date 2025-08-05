#!/usr/bin/env python3
"""
Prueba de OpenWeatherMap API 3.0 OneCall
API Key: 6a6e94ae482a1c310fe583b6a35eb72b
Documentación: https://api.openweathermap.org/data/3.0/onecall
"""

import requests
import json
from datetime import datetime

def test_openweather_v3():
    """
    Prueba completa de OpenWeatherMap API 3.0 OneCall
    """
    
    print("🌤️ PRUEBA OPENWEATHERMAP API 3.0 ONECALL")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: 6a6e94ae482a1c310fe583b6a35eb72b")
    print("")
    
    # Coordenadas AIFA
    lat = 19.7425
    lon = -99.0157
    api_key = "6a6e94ae482a1c310fe583b6a35eb72b"
    
    # Test 1: OneCall API 3.0 completa
    print("1️⃣ PROBANDO ONECALL API 3.0 COMPLETA")
    print("-" * 50)
    
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
        'lang': 'es'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 3.0 OneCall FUNCIONANDO")
            
            # Datos actuales
            current = data.get('current', {})
            print(f"🌡️ Temperatura actual: {current.get('temp', 'N/A')}°C")
            print(f"🌡️ Sensación térmica: {current.get('feels_like', 'N/A')}°C")
            print(f"💨 Viento: {current.get('wind_speed', 'N/A')} m/s")
            print(f"💧 Humedad: {current.get('humidity', 'N/A')}%")
            print(f"☁️ Nubes: {current.get('clouds', 'N/A')}%")
            
            weather = current.get('weather', [{}])[0]
            print(f"🌤️ Condición: {weather.get('description', 'N/A')}")
            
            # Pronóstico por horas
            hourly = data.get('hourly', [])
            print(f"📊 Pronóstico por horas: {len(hourly)} horas disponibles")
            
            # Pronóstico diario
            daily = data.get('daily', [])
            print(f"📅 Pronóstico diario: {len(daily)} días disponibles")
            
            # Alertas
            alerts = data.get('alerts', [])
            if alerts:
                print(f"⚠️ Alertas meteorológicas: {len(alerts)}")
            else:
                print("✅ Sin alertas meteorológicas")
                
        elif response.status_code == 401:
            print("❌ Error 401: API Key inválida o no autorizada")
            print(f"Response: {response.text}")
        elif response.status_code == 402:
            print("❌ Error 402: Suscripción requerida para OneCall 3.0")
            print("💡 Intentando con API 2.5...")
            return test_openweather_v25(lat, lon, api_key)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    print("")
    
    # Test 2: Weather Overview con AI
    print("2️⃣ PROBANDO WEATHER OVERVIEW (AI)")
    print("-" * 50)
    
    overview_url = "https://api.openweathermap.org/data/3.0/onecall/overview"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(overview_url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            overview = data.get('weather_overview', 'N/A')
            print("✅ Weather Overview AI FUNCIONANDO")
            print(f"🤖 Resumen AI: {overview[:200]}...")
        else:
            print(f"⚠️ Weather Overview no disponible: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error en Weather Overview: {e}")
    
    print("")
    print("="*60)
    print("✅ PRUEBA OPENWEATHERMAP COMPLETADA")
    return True

def test_openweather_v25(lat, lon, api_key):
    """
    Fallback a OpenWeatherMap API 2.5 (gratuita)
    """
    print("🔄 INTENTANDO OPENWEATHERMAP API 2.5 (GRATUITA)")
    print("-" * 50)
    
    # Current Weather API 2.5
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
        'lang': 'es'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 2.5 FUNCIONANDO")
            
            # Datos básicos
            main = data.get('main', {})
            wind = data.get('wind', {})
            weather = data.get('weather', [{}])[0]
            
            print(f"🌡️ Temperatura: {main.get('temp', 'N/A')}°C")
            print(f"🌡️ Sensación térmica: {main.get('feels_like', 'N/A')}°C")
            print(f"💨 Viento: {wind.get('speed', 'N/A')} m/s")
            print(f"💧 Humedad: {main.get('humidity', 'N/A')}%")
            print(f"🌤️ Condición: {weather.get('description', 'N/A')}")
            
            return True
        else:
            print(f"❌ API 2.5 también falló: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en API 2.5: {e}")
        return False

if __name__ == "__main__":
    test_openweather_v3()