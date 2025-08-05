"""
Métricas en Tiempo Real para AIFA
Simula y calcula métricas operativas en tiempo real
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import json
import aiohttp

class AIFARealtimeMetrics:
    """Generador de métricas en tiempo real para AIFA"""
    
    def __init__(self):
        self.base_metrics = {
            'operaciones_hora': 15,
            'pasajeros_hora': 1200,
            'factor_puntualidad': 0.92,
            'tiempo_taxi_promedio': 12,  # minutos
            'gates_totales': 35,
            'posiciones_remotas': 15
        }
        
        # APIs gratuitas para datos reales
        self.free_apis = {
            'weather': 'https://api.openweathermap.org/data/2.5/weather?q=Mexico+City&appid=demo',
            'flights': 'https://opensky-network.org/api/states/all?lamin=19.3&lomin=-99.3&lamax=19.6&lomax=-98.9'
        }
    
    def obtener_metricas_tiempo_real(self) -> Dict:
        """Obtiene todas las métricas en tiempo real"""
        ahora = datetime.now()
        hora_actual = ahora.hour
        
        # Factor de variación por hora
        factor_hora = self._calcular_factor_hora(hora_actual)
        
        metricas = {
            'timestamp': ahora.strftime('%Y-%m-%d %H:%M:%S'),
            'operaciones': self._calcular_operaciones(factor_hora),
            'pasajeros': self._calcular_flujo_pasajeros(factor_hora),
            'puntualidad': self._calcular_puntualidad(hora_actual),
            'seguridad': self._metricas_seguridad(),
            'servicios': self._metricas_servicios(),
            'clima': self._obtener_clima(),
            'alertas': self._generar_alertas(hora_actual)
        }
        
        return metricas
    
    def _calcular_factor_hora(self, hora: int) -> float:
        """Calcula factor de actividad según hora del día"""
        # Horas pico: 6-9 AM y 6-9 PM
        if 6 <= hora <= 9 or 18 <= hora <= 21:
            return random.uniform(1.3, 1.5)
        # Horas valle: 10 AM - 5 PM
        elif 10 <= hora <= 17:
            return random.uniform(0.7, 0.9)
        # Madrugada/noche
        else:
            return random.uniform(0.3, 0.5)
    
    def _calcular_operaciones(self, factor: float) -> Dict:
        """Calcula métricas de operaciones aéreas"""
        base = self.base_metrics['operaciones_hora']
        actual = int(base * factor * random.uniform(0.9, 1.1))
        
        return {
            'despegues_ultima_hora': actual // 2,
            'aterrizajes_ultima_hora': actual - (actual // 2),
            'total_ultima_hora': actual,
            'promedio_dia': base * 18,  # 18 horas operativas
            'ocupacion_pistas': f"{(actual / 30) * 100:.1f}%",  # 30 ops/hora máx
            'tiempo_separacion': f"{60 / actual:.1f} min",
            'vuelos_en_aproximacion': random.randint(2, 8),
            'vuelos_en_tierra': random.randint(5, 15)
        }
    
    def _calcular_flujo_pasajeros(self, factor: float) -> Dict:
        """Calcula métricas de flujo de pasajeros"""
        base = self.base_metrics['pasajeros_hora']
        actual = int(base * factor * random.uniform(0.85, 1.15))
        
        return {
            'pasajeros_ultima_hora': actual,
            'salidas': int(actual * 0.52),
            'llegadas': int(actual * 0.48),
            'en_terminal': random.randint(2000, 4000),
            'tiempo_check_in': f"{random.randint(15, 35)} min",
            'tiempo_seguridad': f"{random.randint(10, 25)} min",
            'tiempo_migracion': f"{random.randint(20, 45)} min",
            'ocupacion_salas': f"{random.uniform(60, 85):.0f}%"
        }
    
    def _calcular_puntualidad(self, hora: int) -> Dict:
        """Calcula métricas de puntualidad"""
        # Puntualidad baja en horas pico
        if 6 <= hora <= 9 or 18 <= hora <= 21:
            puntualidad = random.uniform(0.82, 0.88)
        else:
            puntualidad = random.uniform(0.88, 0.96)
        
        return {
            'indice_puntualidad': f"{puntualidad * 100:.1f}%",
            'vuelos_a_tiempo': int(puntualidad * 100),
            'retrasos_15_min': random.randint(5, 15),
            'retrasos_30_min': random.randint(2, 8),
            'retrasos_60_min': random.randint(0, 3),
            'cancelaciones': random.randint(0, 2),
            'tiempo_rotacion_promedio': f"{random.randint(35, 55)} min"
        }
    
    def _metricas_seguridad(self) -> Dict:
        """Métricas de seguridad aeroportuaria"""
        return {
            'incidentes_24h': 0,
            'nivel_alerta': 'Verde',
            'puntos_inspeccion_activos': random.randint(8, 12),
            'tiempo_respuesta_emergencia': '3 min',
            'personal_seguridad': random.randint(150, 200),
            'camaras_operativas': '98%',
            'sistemas_criticos': 'Operativo'
        }
    
    def _metricas_servicios(self) -> Dict:
        """Métricas de servicios aeroportuarios"""
        return {
            'gates_disponibles': random.randint(8, 15),
            'gates_ocupados': random.randint(20, 27),
            'buses_operando': random.randint(12, 18),
            'carruseles_activos': random.randint(4, 6),
            'tiempo_entrega_equipaje': f"{random.randint(18, 35)} min",
            'restaurantes_abiertos': f"{random.randint(15, 22)}/25",
            'tiendas_abiertas': f"{random.randint(18, 28)}/30",
            'wifi_usuarios': random.randint(800, 2500),
            'estacionamiento_ocupacion': f"{random.uniform(65, 88):.0f}%"
        }
    
    def _obtener_clima(self) -> Dict:
        """Obtiene condiciones climáticas (simuladas)"""
        condiciones = ['Despejado', 'Parcialmente nublado', 'Nublado', 'Lluvia ligera']
        
        return {
            'condicion': random.choice(condiciones),
            'temperatura': f"{random.randint(15, 28)}°C",
            'viento': f"{random.randint(5, 25)} km/h",
            'visibilidad': f"{random.randint(8, 10)} km",
            'presion': f"{random.randint(1010, 1025)} hPa",
            'humedad': f"{random.randint(40, 80)}%",
            'techo_nubes': f"{random.randint(2000, 5000)} ft",
            'afecta_operaciones': random.choice([False, False, False, True])
        }
    
    def _generar_alertas(self, hora: int) -> List[Dict]:
        """Genera alertas operativas"""
        alertas = []
        
        # Probabilidad de alertas según hora
        if random.random() < 0.3:
            tipos_alerta = [
                {'tipo': 'info', 'mensaje': 'Mantenimiento programado Pista 2 - 23:00-05:00'},
                {'tipo': 'warning', 'mensaje': 'Congestión moderada en sala de llegadas internacionales'},
                {'tipo': 'info', 'mensaje': 'Nuevo servicio: WiFi premium en salas VIP'},
                {'tipo': 'warning', 'mensaje': 'Retraso en carrusel 3 - 10 min adicionales'},
                {'tipo': 'success', 'mensaje': 'Record de puntualidad: 95% en últimas 24h'}
            ]
            
            num_alertas = random.randint(1, 3)
            alertas = random.sample(tipos_alerta, num_alertas)
        
        return alertas
    
    def generar_dashboard_data(self) -> Dict:
        """Genera datos completos para dashboard en tiempo real"""
        metricas = self.obtener_metricas_tiempo_real()
        
        # Agregar métricas adicionales para visualización
        metricas['kpis_principales'] = {
            'eficiencia_operativa': f"{random.uniform(85, 95):.1f}%",
            'satisfaccion_pasajeros': f"{random.uniform(4.0, 4.5):.1f}/5",
            'utilizacion_capacidad': f"{random.uniform(70, 85):.1f}%",
            'ingresos_dia': f"${random.uniform(8.5, 12.5):.1f}M MXN"
        }
        
        # Tendencias (últimas 6 horas)
        metricas['tendencias'] = self._generar_tendencias()
        
        return metricas
    
    def _generar_tendencias(self) -> Dict:
        """Genera datos de tendencia para gráficos"""
        horas = []
        operaciones = []
        pasajeros = []
        puntualidad = []
        
        ahora = datetime.now()
        
        for i in range(6, 0, -1):
            hora = ahora - timedelta(hours=i)
            horas.append(hora.strftime('%H:00'))
            
            factor = self._calcular_factor_hora(hora.hour)
            operaciones.append(int(self.base_metrics['operaciones_hora'] * factor * random.uniform(0.9, 1.1)))
            pasajeros.append(int(self.base_metrics['pasajeros_hora'] * factor * random.uniform(0.85, 1.15)))
            
            if 6 <= hora.hour <= 9 or 18 <= hora.hour <= 21:
                puntualidad.append(random.uniform(82, 88))
            else:
                puntualidad.append(random.uniform(88, 96))
        
        return {
            'horas': horas,
            'operaciones': operaciones,
            'pasajeros': pasajeros,
            'puntualidad': puntualidad
        }

# API endpoints simulados para integración futura
async def obtener_vuelos_opensky():
    """Obtiene vuelos reales de OpenSky Network (cuando se implemente)"""
    # Por ahora retorna datos simulados
    return {
        'vuelos_detectados': random.randint(10, 25),
        'sobre_aifa': random.randint(2, 8),
        'en_aproximacion': random.randint(1, 5)
    }

def generar_metricas_dashboard():
    """Función principal para el dashboard"""
    generator = AIFARealtimeMetrics()
    return generator.generar_dashboard_data()

if __name__ == "__main__":
    # Prueba del generador
    generator = AIFARealtimeMetrics()
    metricas = generator.generar_dashboard_data()
    
    print("🎯 MÉTRICAS EN TIEMPO REAL AIFA")
    print("=" * 50)
    print(f"⏰ {metricas['timestamp']}")
    print(f"✈️ Operaciones/hora: {metricas['operaciones']['total_ultima_hora']}")
    print(f"👥 Pasajeros/hora: {metricas['pasajeros']['pasajeros_ultima_hora']}")
    print(f"📊 Puntualidad: {metricas['puntualidad']['indice_puntualidad']}")
    print(f"🌤️ Clima: {metricas['clima']['condicion']} - {metricas['clima']['temperatura']}")
    
    if metricas['alertas']:
        print("\n⚠️ ALERTAS ACTIVAS:")
        for alerta in metricas['alertas']:
            print(f"  - [{alerta['tipo'].upper()}] {alerta['mensaje']}")