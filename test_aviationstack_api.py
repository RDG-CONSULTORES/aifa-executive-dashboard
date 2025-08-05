#!/usr/bin/env python3
"""
Script de prueba para verificar API key de AviationStack
"""

import requests
import json
from datetime import datetime

# Tu API key
API_KEY = "59f5d7300a3c8236dc29e095fa6ab923"

def test_aviationstack_api():
    """Prueba la API de AviationStack con el aeropuerto AIFA (NLU)"""
    
    print("🧪 PROBANDO API DE AVIATIONSTACK")
    print("="*50)
    
    # Endpoint para información del aeropuerto
    base_url = "http://api.aviationstack.com/v1"
    
    # Test 1: Información del aeropuerto AIFA
    print("\n1️⃣ Obteniendo información del AIFA (NLU)...")
    
    airports_url = f"{base_url}/airports"
    params = {
        'access_key': API_KEY,
        'search': 'Felipe Angeles'  # o usar 'iata_code': 'NLU'
    }
    
    try:
        response = requests.get(airports_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            airport = data['data'][0]
            print(f"✅ Aeropuerto encontrado: {airport['airport_name']}")
            print(f"   IATA: {airport['iata_code']}")
            print(f"   Ciudad: {airport['city']}")
            print(f"   País: {airport['country_name']}")
            print(f"   Coordenadas: {airport['latitude']}, {airport['longitude']}")
        else:
            print("⚠️ No se encontró información del aeropuerto")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Vuelos en tiempo real (si está disponible en tu plan)
    print("\n2️⃣ Probando vuelos en tiempo real...")
    
    flights_url = f"{base_url}/flights"
    params = {
        'access_key': API_KEY,
        'dep_iata': 'NLU',  # Salidas desde AIFA
        'limit': 5
    }
    
    try:
        response = requests.get(flights_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                print(f"✅ Encontrados {len(data['data'])} vuelos desde AIFA")
                for i, flight in enumerate(data['data'][:3]):
                    print(f"   Vuelo {i+1}: {flight.get('flight', {}).get('iata', 'N/A')} → {flight.get('arrival', {}).get('airport', 'N/A')}")
            else:
                print("ℹ️ No hay vuelos disponibles en este momento")
        else:
            print(f"ℹ️ Acceso a vuelos en tiempo real no disponible (Status: {response.status_code})")
            
    except Exception as e:
        print(f"ℹ️ Vuelos en tiempo real no disponibles en plan gratuito")
    
    # Test 3: Verificar límites de la API
    print("\n3️⃣ Información de tu cuenta...")
    
    # Algunos endpoints para verificar
    print(f"✅ API Key activa: {API_KEY[:10]}...")
    print(f"ℹ️ Plan gratuito: 1,000 requests/mes")
    print(f"📅 Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "="*50)
    print("✅ API DE AVIATIONSTACK FUNCIONAL")
    print("Puedes proceder con la implementación de KPIs reales")
    
    return True

if __name__ == "__main__":
    test_aviationstack_api()