#!/usr/bin/env python3
"""
Diagnóstico completo de credenciales OpenSky Network
Prueba múltiples métodos de autenticación y endpoints
"""

import asyncio
import aiohttp
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64

# Cargar variables de entorno
load_dotenv()

class OpenSkyDiagnostic:
    def __init__(self):
        self.client_id = os.getenv('OPENSKY_CLIENT_ID')
        self.client_secret = os.getenv('OPENSKY_CLIENT_SECRET')
        self.base_url = 'https://opensky-network.org/api'
        
        print(f"🔍 DIAGNÓSTICO OPENSKY NETWORK")
        print(f"Client ID: {self.client_id}")
        print(f"Client Secret: {'*' * len(self.client_secret) if self.client_secret else 'None'}")
        print("=" * 50)
    
    def test_1_credentials_format(self):
        """Prueba 1: Verificar formato de credenciales"""
        print("\n1️⃣ VERIFICANDO FORMATO DE CREDENCIALES")
        
        if not self.client_id or not self.client_secret:
            print("❌ Credenciales faltantes")
            return False
        
        print(f"✅ Client ID presente: {len(self.client_id)} caracteres")
        print(f"✅ Client Secret presente: {len(self.client_secret)} caracteres")
        
        # Verificar formato básico
        if '-' in self.client_id and 'api' in self.client_id.lower():
            print("✅ Formato Client ID parece correcto")
        else:
            print("⚠️ Formato Client ID inusual")
        
        return True
    
    def test_2_basic_auth_sync(self):
        """Prueba 2: Autenticación básica síncrona"""
        print("\n2️⃣ PROBANDO AUTENTICACIÓN BÁSICA (REQUESTS)")
        
        try:
            # Endpoint público primero (sin auth)
            url = f"{self.base_url}/states/all"
            print(f"URL: {url}")
            
            # Sin autenticación
            print("Probando sin autenticación...")
            response = requests.get(url, timeout=10)
            print(f"Sin auth - Status: {response.status_code}")
            
            # Con autenticación
            print("Probando con autenticación...")
            response = requests.get(
                url, 
                auth=(self.client_id, self.client_secret),
                timeout=10
            )
            print(f"Con auth - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Éxito! Vuelos detectados: {len(data.get('states', [])) if data.get('states') else 0}")
                return True
            elif response.status_code == 401:
                print("❌ Error 401: Credenciales inválidas o inactivas")
                
                # Probar con Authorization header manual
                print("Probando con header Authorization manual...")
                credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
                headers = {'Authorization': f'Basic {credentials}'}
                
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Header manual - Status: {response.status_code}")
                
                return False
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ Error en requests: {e}")
            return False
    
    async def test_3_async_auth(self):
        """Prueba 3: Autenticación asíncrona con aiohttp"""
        print("\n3️⃣ PROBANDO AUTENTICACIÓN ASÍNCRONA (AIOHTTP)")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/states/all"
                
                # Con BasicAuth de aiohttp
                auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
                
                print(f"Usando aiohttp.BasicAuth...")
                async with session.get(url, auth=auth) as response:
                    print(f"Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Éxito! Vuelos detectados: {len(data.get('states', [])) if data.get('states') else 0}")
                        return True
                    else:
                        text = await response.text()
                        print(f"❌ Error {response.status}: {text[:100]}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error en aiohttp: {e}")
            return False
    
    def test_4_specific_endpoints(self):
        """Prueba 4: Endpoints específicos que requieren autenticación"""
        print("\n4️⃣ PROBANDO ENDPOINTS ESPECÍFICOS")
        
        # Endpoints que definitivamente requieren autenticación
        endpoints_to_test = [
            ('/flights/arrival', {'airport': 'MMSM', 'begin': int((datetime.now() - timedelta(hours=24)).timestamp()), 'end': int(datetime.now().timestamp())}),
            ('/flights/departure', {'airport': 'MMSM', 'begin': int((datetime.now() - timedelta(hours=24)).timestamp()), 'end': int(datetime.now().timestamp())}),
            ('/flights/all', {'begin': int((datetime.now() - timedelta(hours=1)).timestamp()), 'end': int(datetime.now().timestamp())})
        ]
        
        for endpoint, params in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"\nProbando: {url}")
                print(f"Parámetros: {params}")
                
                response = requests.get(
                    url,
                    params=params,
                    auth=(self.client_id, self.client_secret),
                    timeout=15
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Éxito! Registros: {len(data) if isinstance(data, list) else 'N/A'}")
                        return True
                    except:
                        print(f"✅ Respuesta exitosa (no JSON)")
                        return True
                elif response.status_code == 401:
                    print("❌ 401: Credenciales inválidas")
                elif response.status_code == 403:
                    print("❌ 403: Acceso denegado")
                else:
                    print(f"❌ Error {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return False
    
    def test_5_rate_limits(self):
        """Prueba 5: Verificar límites de velocidad"""
        print("\n5️⃣ VERIFICANDO LÍMITES DE VELOCIDAD")
        
        try:
            # Hacer múltiples requests para ver límites
            url = f"{self.base_url}/states/all"
            
            for i in range(3):
                print(f"Request {i+1}/3...")
                response = requests.get(
                    url,
                    auth=(self.client_id, self.client_secret),
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                
                # Verificar headers de rate limiting
                rate_headers = {}
                for header in response.headers:
                    if 'rate' in header.lower() or 'limit' in header.lower():
                        rate_headers[header] = response.headers[header]
                
                if rate_headers:
                    print(f"Rate limit headers: {rate_headers}")
                
                if response.status_code == 429:
                    print("❌ Rate limit excedido")
                    return False
                elif response.status_code == 200:
                    print("✅ Request exitoso")
                
                # Pequeña pausa entre requests
                import time
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todos los tests de diagnóstico"""
        results = []
        
        # Test 1: Formato de credenciales
        results.append(self.test_1_credentials_format())
        
        # Test 2: Auth básica síncrona
        results.append(self.test_2_basic_auth_sync())
        
        # Test 3: Auth asíncrona
        results.append(await self.test_3_async_auth())
        
        # Test 4: Endpoints específicos
        results.append(self.test_4_specific_endpoints())
        
        # Test 5: Rate limits
        results.append(self.test_5_rate_limits())
        
        # Resumen final
        print("\n" + "="*50)
        print("📋 RESUMEN DE DIAGNÓSTICO")
        print("="*50)
        
        tests = [
            "Formato de credenciales",
            "Autenticación básica (requests)",
            "Autenticación asíncrona (aiohttp)",
            "Endpoints específicos",
            "Límites de velocidad"
        ]
        
        success_count = sum(results)
        
        for i, (test, result) in enumerate(zip(tests, results)):
            status = "✅" if result else "❌"
            print(f"{status} {test}")
        
        print(f"\n🎯 RESULTADO: {success_count}/{len(results)} tests exitosos")
        
        if success_count == 0:
            print("\n🔧 RECOMENDACIONES:")
            print("1. Verificar credenciales en https://opensky-network.org/my-opensky")
            print("2. Confirmar que la cuenta esté activa")
            print("3. Revisar si necesitas solicitar acceso a la API")
            print("4. Verificar que no haya restricciones geográficas")
        elif success_count < len(results):
            print(f"\n⚠️ ALGUNOS TESTS FALLARON - Es posible que haya restricciones específicas")
        else:
            print(f"\n🎉 TODAS LAS PRUEBAS EXITOSAS - OpenSky funciona correctamente!")
        
        return success_count > 0

async def main():
    diagnostic = OpenSkyDiagnostic()
    await diagnostic.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())