"""
Analizador de Slots Aeroportuarios AIFA
Calcula disponibilidad, optimización y visualización de slots
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple

class AIFASlotsAnalyzer:
    """Análisis y optimización de slots aeroportuarios"""
    
    def __init__(self):
        # Capacidad AIFA
        self.capacidad_pistas = {
            'pista_1': {
                'nombre': '04/22',
                'longitud': 4500,
                'operaciones_hora': 30,  # Máximo teórico
                'tipo_aeronaves': ['narrow', 'wide', 'cargo']
            },
            'pista_2': {
                'nombre': '18/36', 
                'longitud': 3500,
                'operaciones_hora': 25,
                'tipo_aeronaves': ['narrow', 'regional']
            }
        }
        
        # Horarios operativos
        self.horario_operacion = {
            'apertura': 5,  # 5:00 AM
            'cierre': 23,   # 11:00 PM
            'horas_pico': [(6, 9), (18, 21)],  # Mañana y tarde
            'horas_valle': [(10, 17), (21, 23)]
        }
        
        # Slots actuales simulados
        self.slots_ocupados = self._generar_slots_actuales()
    
    def _generar_slots_actuales(self) -> pd.DataFrame:
        """Genera distribución actual de slots"""
        slots_data = []
        
        # Simulamos slots ocupados actuales
        aerolineas = ['VivaAerobus', 'Volaris', 'Aeromexico', 'Magnicharters']
        
        for hora in range(5, 23):
            for minuto in [0, 15, 30, 45]:  # Slots cada 15 min
                # Probabilidad de ocupación según hora
                if 6 <= hora <= 9 or 18 <= hora <= 21:  # Horas pico
                    prob_ocupado = 0.7
                else:  # Horas valle
                    prob_ocupado = 0.3
                
                if np.random.random() < prob_ocupado:
                    slots_data.append({
                        'hora': hora,
                        'minuto': minuto,
                        'slot_time': f"{hora:02d}:{minuto:02d}",
                        'aerolinea': np.random.choice(aerolineas),
                        'tipo_operacion': np.random.choice(['salida', 'llegada']),
                        'tipo_vuelo': np.random.choice(['nacional', 'internacional']),
                        'ocupado': True
                    })
        
        return pd.DataFrame(slots_data)
    
    def calcular_disponibilidad_slots(self) -> Dict:
        """Calcula slots disponibles por hora"""
        disponibilidad = {}
        
        # Total de slots posibles por hora (4 slots x 2 pistas)
        slots_maximos_hora = 8
        
        for hora in range(5, 23):
            slots_hora = self.slots_ocupados[self.slots_ocupados['hora'] == hora]
            ocupados = len(slots_hora)
            disponibles = slots_maximos_hora - ocupados
            
            disponibilidad[hora] = {
                'total': slots_maximos_hora,
                'ocupados': ocupados,
                'disponibles': disponibles,
                'porcentaje_ocupacion': (ocupados / slots_maximos_hora) * 100,
                'es_hora_pico': any(inicio <= hora < fin for inicio, fin in self.horario_operacion['horas_pico'])
            }
        
        return disponibilidad
    
    def analizar_ventanas_optimas(self) -> List[Dict]:
        """Identifica las mejores ventanas para nuevos slots"""
        disponibilidad = self.calcular_disponibilidad_slots()
        ventanas_optimas = []
        
        for hora, datos in disponibilidad.items():
            if datos['disponibles'] > 0:
                # Calcular score de oportunidad
                score = self._calcular_score_slot(hora, datos)
                
                ventanas_optimas.append({
                    'hora': hora,
                    'slots_disponibles': datos['disponibles'],
                    'es_hora_pico': datos['es_hora_pico'],
                    'score_oportunidad': score,
                    'recomendacion': self._generar_recomendacion(hora, score)
                })
        
        # Ordenar por score
        return sorted(ventanas_optimas, key=lambda x: x['score_oportunidad'], reverse=True)
    
    def _calcular_score_slot(self, hora: int, datos: Dict) -> float:
        """Calcula score de oportunidad para un slot"""
        score = 0.0
        
        # Factor hora pico (más valioso)
        if datos['es_hora_pico']:
            score += 40
        
        # Factor disponibilidad
        score += datos['disponibles'] * 5
        
        # Factor conectividad (mejor en horas intermedias)
        if 10 <= hora <= 16:
            score += 20  # Bueno para conexiones
        
        # Factor competencia (menos saturación es mejor)
        score += (100 - datos['porcentaje_ocupacion']) * 0.3
        
        return min(score, 100)  # Máximo 100
    
    def _generar_recomendacion(self, hora: int, score: float) -> str:
        """Genera recomendación para el slot"""
        if score >= 80:
            return "🟢 EXCELENTE - Alta demanda, prioridad máxima"
        elif score >= 60:
            return "🟡 BUENO - Oportunidad sólida"
        elif score >= 40:
            return "🟠 REGULAR - Considerar para rutas específicas"
        else:
            return "🔴 BAJO - Solo si no hay otras opciones"
    
    def generar_mapa_calor_slots(self) -> go.Figure:
        """Genera mapa de calor de disponibilidad de slots"""
        # Preparar datos para el mapa de calor
        horas = list(range(5, 23))
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        # Simular datos semanales
        z_data = []
        for dia in range(7):
            fila = []
            for hora in horas:
                # Variación por día
                factor_dia = 1.0 if dia < 5 else 0.7  # Menos tráfico fin de semana
                disponibilidad = self.calcular_disponibilidad_slots()
                ocupacion = disponibilidad[hora]['porcentaje_ocupacion'] * factor_dia
                fila.append(ocupacion)
            z_data.append(fila)
        
        # Crear mapa de calor
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=[f"{h:02d}:00" for h in horas],
            y=dias,
            colorscale=[
                [0, 'green'],      # 0% ocupación - Verde (disponible)
                [0.5, 'yellow'],   # 50% ocupación - Amarillo
                [0.7, 'orange'],   # 70% ocupación - Naranja
                [1, 'red']         # 100% ocupación - Rojo (saturado)
            ],
            colorbar=dict(
                title="Ocupación %"
            ),
            hovertemplate='%{y}<br>%{x}<br>Ocupación: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Mapa de Calor - Disponibilidad de Slots AIFA',
            xaxis_title='Hora del día',
            yaxis_title='Día de la semana',
            height=400
        )
        
        return fig
    
    def calcular_metricas_tiempo_real(self) -> Dict:
        """Calcula métricas en tiempo real para el dashboard"""
        # Zona horaria de Ciudad de México
        zona_mx = pytz.timezone('America/Mexico_City')
        ahora = datetime.now(zona_mx)
        hora_actual = ahora.hour
        
        disponibilidad = self.calcular_disponibilidad_slots()
        ventanas = self.analizar_ventanas_optimas()
        
        # Métricas principales
        metricas = {
            'tiempo_real': {
                'hora': ahora.strftime('%H:%M'),
                'slots_disponibles_ahora': disponibilidad.get(hora_actual, {}).get('disponibles', 0),
                'ocupacion_actual': disponibilidad.get(hora_actual, {}).get('porcentaje_ocupacion', 0),
                'proximo_slot_libre': self._encontrar_proximo_slot_libre(hora_actual)
            },
            'resumen_dia': {
                'total_slots_dia': sum(d['total'] for d in disponibilidad.values()),
                'slots_ocupados': sum(d['ocupados'] for d in disponibilidad.values()),
                'slots_disponibles': sum(d['disponibles'] for d in disponibilidad.values()),
                'ocupacion_promedio': np.mean([d['porcentaje_ocupacion'] for d in disponibilidad.values()])
            },
            'oportunidades': {
                'mejor_ventana': ventanas[0] if ventanas else None,
                'slots_hora_pico_disponibles': sum(v['slots_disponibles'] for v in ventanas if v['es_hora_pico']),
                'slots_hora_valle_disponibles': sum(v['slots_disponibles'] for v in ventanas if not v['es_hora_pico'])
            },
            'proyecciones': {
                'capacidad_utilizada_hoy': f"{np.mean([d['porcentaje_ocupacion'] for d in disponibilidad.values()]):.1f}%",
                'slots_potenciales_mes': self._calcular_slots_potenciales_mes(),
                'ingresos_potenciales': self._calcular_ingresos_potenciales()
            }
        }
        
        return metricas
    
    def _encontrar_proximo_slot_libre(self, hora_actual: int) -> str:
        """Encuentra el próximo slot disponible"""
        disponibilidad = self.calcular_disponibilidad_slots()
        
        for h in range(hora_actual, 23):
            if disponibilidad[h]['disponibles'] > 0:
                return f"{h:02d}:00"
        
        return "Mañana 05:00"
    
    def _calcular_slots_potenciales_mes(self) -> int:
        """Calcula slots disponibles en el mes"""
        disponibilidad_dia = sum(d['disponibles'] for d in self.calcular_disponibilidad_slots().values())
        return disponibilidad_dia * 30
    
    def _calcular_ingresos_potenciales(self) -> str:
        """Estima ingresos por slots disponibles"""
        # Tarifa promedio por slot en AIFA (estimado)
        tarifa_slot_promedio = 25000  # MXN
        slots_mes = self._calcular_slots_potenciales_mes()
        ingresos = slots_mes * tarifa_slot_promedio
        
        return f"${ingresos:,.0f} MXN/mes"
    
    def generar_visualizacion_3d_slots(self) -> go.Figure:
        """Genera visualización 3D de utilización de slots"""
        # Datos para visualización 3D
        horas = []
        dias = []
        ocupacion = []
        
        for dia in range(7):
            for hora in range(5, 23):
                horas.append(hora)
                dias.append(dia)
                # Simular variación
                factor = 1.0 if dia < 5 else 0.7
                disp = self.calcular_disponibilidad_slots()
                ocupacion.append(disp[hora]['porcentaje_ocupacion'] * factor)
        
        # Crear gráfico 3D
        fig = go.Figure(data=[go.Scatter3d(
            x=horas,
            y=dias,
            z=ocupacion,
            mode='markers',
            marker=dict(
                size=8,
                color=ocupacion,
                colorscale='RdYlGn_r',
                colorbar=dict(title="Ocupación %"),
                showscale=True
            ),
            text=[f"Día {d+1}, {h}:00<br>Ocupación: {o:.1f}%" 
                  for h, d, o in zip(horas, dias, ocupacion)],
            hoverinfo='text'
        )])
        
        fig.update_layout(
            title='Utilización de Slots AIFA - Vista 3D',
            scene=dict(
                xaxis_title='Hora',
                yaxis_title='Día de la semana',
                zaxis_title='% Ocupación'
            ),
            height=600
        )
        
        return fig

# Funciones auxiliares para el dashboard
def obtener_metricas_slots():
    """Obtiene métricas de slots para el dashboard"""
    analyzer = AIFASlotsAnalyzer()
    return analyzer.calcular_metricas_tiempo_real()

def generar_visualizaciones_slots():
    """Genera todas las visualizaciones de slots"""
    analyzer = AIFASlotsAnalyzer()
    
    return {
        'mapa_calor': analyzer.generar_mapa_calor_slots(),
        'vista_3d': analyzer.generar_visualizacion_3d_slots(),
        'ventanas_optimas': analyzer.analizar_ventanas_optimas()[:5]  # Top 5
    }

if __name__ == "__main__":
    # Prueba del analizador
    analyzer = AIFASlotsAnalyzer()
    metricas = analyzer.calcular_metricas_tiempo_real()
    
    print("📊 MÉTRICAS DE SLOTS AIFA")
    print("-" * 50)
    print(f"⏰ Hora actual: {metricas['tiempo_real']['hora']}")
    print(f"🎰 Slots disponibles ahora: {metricas['tiempo_real']['slots_disponibles_ahora']}")
    print(f"📈 Ocupación actual: {metricas['tiempo_real']['ocupacion_actual']:.1f}%")
    print(f"💰 Ingresos potenciales: {metricas['proyecciones']['ingresos_potenciales']}")