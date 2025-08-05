#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Ingresos y ROI para Nuevas Rutas AIFA
Calcula potencial de ingresos, costos operativos y ROI para rutas propuestas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class SimuladorRutaAIFA:
    def __init__(self, data_path="../data/"):
        """Inicializa el simulador con datos base del AIFA"""
        self.data_path = data_path
        self.load_data()
        
        # Parámetros operativos base
        self.costos_base = {
            'combustible_por_km': 0.85,  # USD por km
            'tripulacion_por_vuelo': 2500,  # USD por vuelo
            'mantenimiento_por_hora': 450,  # USD por hora de vuelo
            'tasas_aeroportuarias': {
                'nacional': 850,  # MXN
                'internacional': 1200  # MXN
            },
            'marketing_inicial': 50000,  # USD para lanzamiento
            'overhead_mensual': 25000  # USD gastos generales
        }
        
        # Parámetros de demanda
        self.factores_demanda = {
            'estacionalidad': {
                'alta': 1.3,  # Dic-Mar, Jun-Ago
                'media': 1.0,  # Abr-May, Sep-Nov
                'baja': 0.7   # Resto del año
            },
            'factor_ocupacion_inicial': 0.65,
            'crecimiento_mensual': 0.03,
            'capacidad_promedio': 180  # asientos por vuelo
        }
    
    def load_data(self):
        """Carga los datos CSV existentes"""
        try:
            self.rutas_actuales = pd.read_csv(os.path.join(self.data_path, "rutas_aifa.csv"))
            self.tarifas = pd.read_csv(os.path.join(self.data_path, "tarifas_promedio.csv"))
            self.pasajeros_historicos = pd.read_csv(os.path.join(self.data_path, "pasajeros_mensuales.csv"))
            self.resumen_estrategico = pd.read_csv(os.path.join(self.data_path, "resumen_estrategico.csv"))
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Crea datos de ejemplo si no se pueden cargar los archivos"""
        self.rutas_actuales = pd.DataFrame({
            'airline': ['VivaAerobus', 'Aeromexico', 'Volaris'],
            'source': ['NLU', 'NLU', 'NLU'],
            'destination': ['CUN', 'GDL', 'TIJ']
        })
        
        self.tarifas = pd.DataFrame({
            'source': ['NLU', 'NLU', 'NLU', 'NLU'],
            'destination': ['CUN', 'GDL', 'TIJ', 'LAX'],
            'tarifa_promedio_mxn': [1800, 1200, 2200, 4200]
        })
    
    def calcular_distancia_estimada(self, origen, destino):
        """Estima distancia entre aeropuertos usando códigos IATA"""
        distancias_conocidas = {
            ('NLU', 'CUN'): 1650, ('NLU', 'GDL'): 460, ('NLU', 'TIJ'): 2350,
            ('NLU', 'LAX'): 2500, ('NLU', 'MIA'): 2100, ('NLU', 'NYC'): 3200,
            ('NLU', 'MAD'): 9200, ('NLU', 'CDG'): 9400, ('NLU', 'LHR'): 8900,
            ('NLU', 'DFW'): 1800, ('NLU', 'ORD'): 2800, ('NLU', 'ATL'): 2300
        }
        return distancias_conocidas.get((origen, destino), 1500)
    
    def determinar_tipo_ruta(self, destino):
        """Determina si la ruta es nacional o internacional"""
        codigos_nacionales = ['GDL', 'CUN', 'MTY', 'TIJ', 'PVR', 'CZM', 'SJD', 'MZT', 'OAX', 'VER']
        return 'nacional' if destino in codigos_nacionales else 'internacional'
    
    def simular_ruta_completa(self, origen, destino, aerolinea, vuelos_semanales, meses=12):
        """Simulación completa de una nueva ruta"""
        distancia = self.calcular_distancia_estimada(origen, destino)
        tipo_ruta = self.determinar_tipo_ruta(destino)
        
        # Costos por vuelo
        costo_combustible = distancia * self.costos_base['combustible_por_km']
        costo_tripulacion = self.costos_base['tripulacion_por_vuelo']
        costo_mantenimiento = (distancia / 800) * self.costos_base['mantenimiento_por_hora']
        costo_tasas = self.costos_base['tasas_aeroportuarias'][tipo_ruta]
        
        costo_por_vuelo = costo_combustible + costo_tripulacion + costo_mantenimiento + (costo_tasas / 20)
        
        # Costos totales
        vuelos_totales = vuelos_semanales * 52 * meses / 12
        costos_operativos = costo_por_vuelo * vuelos_totales
        costos_marketing = self.costos_base['marketing_inicial']
        costos_overhead = self.costos_base['overhead_mensual'] * meses
        costos_totales_usd = costos_operativos + costos_marketing + costos_overhead
        
        # Obtener tarifa promedio
        tarifa_row = self.tarifas[
            (self.tarifas['source'] == origen) & 
            (self.tarifas['destination'] == destino)
        ]
        
        if not tarifa_row.empty:
            tarifa_promedio = tarifa_row['tarifa_promedio_mxn'].iloc[0]
        else:
            if tipo_ruta == 'nacional':
                tarifa_promedio = max(800, distancia * 0.65)
            else:
                tarifa_promedio = max(2500, distancia * 0.45)
        
        # Cálculo de ingresos con estacionalidad
        capacidad = self.factores_demanda['capacidad_promedio']
        factor_ocupacion_inicial = self.factores_demanda['factor_ocupacion_inicial']
        crecimiento_mensual = self.factores_demanda['crecimiento_mensual']
        
        ingresos_mensuales = []
        pasajeros_mensuales = []
        
        for mes in range(meses):
            factor_crecimiento = (1 + crecimiento_mensual) ** mes
            
            # Estacionalidad por mes
            if mes in [11, 0, 1, 5, 6, 7]:  # Alta temporada
                factor_estacional = self.factores_demanda['estacionalidad']['alta']
            elif mes in [8, 9, 10]:  # Baja temporada
                factor_estacional = self.factores_demanda['estacionalidad']['baja']
            else:
                factor_estacional = self.factores_demanda['estacionalidad']['media']
            
            ocupacion_mes = min(0.95, factor_ocupacion_inicial * factor_crecimiento * factor_estacional)
            vuelos_mes = vuelos_semanales * 4.33
            pasajeros_mes = vuelos_mes * capacidad * ocupacion_mes
            ingresos_mes = pasajeros_mes * tarifa_promedio
            
            ingresos_mensuales.append(ingresos_mes)
            pasajeros_mensuales.append(pasajeros_mes)
        
        ingresos_totales_mxn = sum(ingresos_mensuales)
        ingresos_totales_usd = ingresos_totales_mxn / 20  # Tipo de cambio estimado
        
        # Cálculo del ROI y métricas
        ganancia_neta_usd = ingresos_totales_usd - costos_totales_usd
        roi_porcentaje = (ganancia_neta_usd / costos_totales_usd) * 100 if costos_totales_usd > 0 else 0
        
        # Punto de equilibrio
        ingresos_mensuales_promedio = ingresos_totales_usd / meses
        costos_mensuales_promedio = costos_totales_usd / meses
        
        if ingresos_mensuales_promedio > costos_mensuales_promedio:
            meses_equilibrio = costos_marketing / (ingresos_mensuales_promedio - costos_mensuales_promedio * 0.8)
        else:
            meses_equilibrio = float('inf')
        
        # Análisis de viabilidad
        viabilidad_score = 0
        if roi_porcentaje > 15: viabilidad_score += 3
        elif roi_porcentaje > 8: viabilidad_score += 2
        elif roi_porcentaje > 0: viabilidad_score += 1
        
        factor_ocupacion_promedio = sum(pasajeros_mensuales) / (vuelos_semanales * 4.33 * meses * capacidad)
        
        if factor_ocupacion_promedio > 0.7: viabilidad_score += 2
        elif factor_ocupacion_promedio > 0.6: viabilidad_score += 1
        
        if meses_equilibrio < 8: viabilidad_score += 2
        elif meses_equilibrio < 12: viabilidad_score += 1
        
        viabilidad = "Alta" if viabilidad_score >= 6 else "Media" if viabilidad_score >= 3 else "Baja"
        
        return {
            'ruta': f"{origen}-{destino}",
            'aerolinea': aerolinea,
            'parametros': {
                'vuelos_semanales': vuelos_semanales,
                'meses_simulacion': meses,
                'distancia_km': distancia,
                'tipo_ruta': tipo_ruta
            },
            'financieros': {
                'ingresos_totales_usd': round(ingresos_totales_usd, 2),
                'ingresos_totales_mxn': round(ingresos_totales_mxn, 2),
                'costos_totales_usd': round(costos_totales_usd, 2),
                'ganancia_neta_usd': round(ganancia_neta_usd, 2),
                'roi_porcentaje': round(roi_porcentaje, 2),
                'tarifa_promedio_mxn': round(tarifa_promedio, 2)
            },
            'operacionales': {
                'pasajeros_totales': int(sum(pasajeros_mensuales)),
                'pasajeros_promedio_mensual': int(sum(pasajeros_mensuales) / meses),
                'factor_ocupacion_promedio': round(factor_ocupacion_promedio, 3),
                'vuelos_totales': int(vuelos_totales),
                'costo_por_vuelo_usd': round(costo_por_vuelo, 2)
            },
            'analisis': {
                'viabilidad': viabilidad,
                'viabilidad_score': viabilidad_score,
                'meses_punto_equilibrio': round(meses_equilibrio, 1) if meses_equilibrio != float('inf') else 'No alcanza equilibrio',
                'recomendacion': self.generar_recomendacion(roi_porcentaje, viabilidad, meses_equilibrio)
            },
            'detalle_mensual': {
                'ingresos_mensuales_usd': [round(x/20, 2) for x in ingresos_mensuales],
                'pasajeros_mensuales': [int(x) for x in pasajeros_mensuales]
            }
        }
    
    def generar_recomendacion(self, roi, viabilidad, meses_equilibrio):
        """Genera recomendación basada en métricas calculadas"""
        if roi > 20 and meses_equilibrio < 6:
            return "🟢 Ruta altamente recomendada - Excelente potencial de rentabilidad"
        elif roi > 15 and meses_equilibrio < 10:
            return "🟢 Ruta recomendada - Buen potencial comercial"
        elif roi > 8 and meses_equilibrio < 15:
            return "🟡 Ruta viable - Considerar factores estratégicos adicionales"
        elif roi > 0:
            return "🟡 Ruta marginalmente viable - Requiere análisis detallado de mercado"
        else:
            return "🔴 Ruta no recomendada - ROI negativo en condiciones actuales"
    
    def comparar_rutas(self, rutas_propuestas):
        """Compara múltiples rutas propuestas"""
        resultados = []
        
        for ruta in rutas_propuestas:
            simulacion = self.simular_ruta_completa(
                ruta['origen'], ruta['destino'], ruta['aerolinea'], ruta['vuelos_semanales']
            )
            resultados.append(simulacion)
        
        # Ordenar por ROI
        resultados_ordenados = sorted(resultados, key=lambda x: x['financieros']['roi_porcentaje'], reverse=True)
        
        return resultados_ordenados

def simular_nueva_ruta(origen, destino, aerolinea, vuelos_semanales, data_path="../data/"):
    """Función conveniente para simular una sola ruta"""
    simulador = SimuladorRutaAIFA(data_path)
    return simulador.simular_ruta_completa(origen, destino, aerolinea, vuelos_semanales)

if __name__ == "__main__":
    # Ejemplo de uso
    simulador = SimuladorRutaAIFA()
    
    # Simular ruta NLU-LAX
    resultado = simulador.simular_ruta_completa('NLU', 'LAX', 'Aeromexico', 4)
    
    print("=== SIMULACIÓN RUTA AIFA-LAX ===")
    print(f"ROI: {resultado['financieros']['roi_porcentaje']:.1f}%")
    print(f"Ingresos Anuales: ${resultado['financieros']['ingresos_totales_usd']:,.0f} USD")
    print(f"Costos Totales: ${resultado['financieros']['costos_totales_usd']:,.0f} USD")
    print(f"Ganancia Neta: ${resultado['financieros']['ganancia_neta_usd']:,.0f} USD")
    print(f"Viabilidad: {resultado['analisis']['viabilidad']}")
    print(f"Recomendación: {resultado['analisis']['recomendacion']}")