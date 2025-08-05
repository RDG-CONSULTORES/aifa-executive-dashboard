"""
Diagrama interactivo del Aeropuerto AIFA con slots en tiempo real
Muestra layout físico, gates, pistas y ocupación actual
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import random

class AIFAAirportDiagram:
    """Generador de diagrama interactivo AIFA"""
    
    def __init__(self):
        # Coordenadas reales AIFA
        self.aifa_coords = {
            'lat': 19.7425,
            'lon': -99.0157
        }
        
        # Layout físico AIFA (simplificado)
        self.airport_layout = {
            'terminal': {
                'gates': {
                    'A': list(range(1, 13)),  # A1-A12
                    'B': list(range(1, 11)),  # B1-B10
                    'C': list(range(1, 14))   # C1-C13
                },
                'total_gates': 35
            },
            'runways': {
                'RW04/22': {
                    'length': 4500,
                    'width': 45,
                    'coordinates': [(19.7380, -99.0200), (19.7470, -99.0114)]
                },
                'RW18/36': {
                    'length': 3500, 
                    'width': 45,
                    'coordinates': [(19.7400, -99.0180), (19.7450, -99.0134)]
                }
            },
            'positions_remote': 15,
            'cargo_area': 8,
            'maintenance': 5
        }
    
    def generate_current_usage(self) -> dict:
        """Genera uso actual de facilities"""
        hora_actual = datetime.now().hour
        
        # Factor de ocupación según hora
        if 6 <= hora_actual <= 9 or 18 <= hora_actual <= 21:
            factor_ocupacion = random.uniform(0.7, 0.9)
        else:
            factor_ocupacion = random.uniform(0.3, 0.6)
        
        # Generar ocupación gates
        total_gates = self.airport_layout['terminal']['total_gates']
        gates_ocupados = int(total_gates * factor_ocupacion)
        
        gate_status = {}
        aerolineas = ['VivaAerobus', 'Volaris', 'Aeromexico', 'Magnicharters', 'Interjet']
        
        # Gates por sección
        for seccion, gates in self.airport_layout['terminal']['gates'].items():
            gate_status[seccion] = {}
            for gate_num in gates:
                gate_id = f"{seccion}{gate_num}"
                
                if random.random() < factor_ocupacion:
                    gate_status[seccion][gate_num] = {
                        'ocupado': True,
                        'aerolinea': random.choice(aerolineas),
                        'tipo_aeronave': random.choice(['A320', 'B737', 'E190', 'A321']),
                        'destino': random.choice(['CUN', 'GDL', 'TIJ', 'LAX', 'MIA']),
                        'tiempo_ocupacion': f"{random.randint(30, 180)} min",
                        'tipo_operacion': random.choice(['boarding', 'deplaning', 'maintenance', 'ready'])
                    }
                else:
                    gate_status[seccion][gate_num] = {
                        'ocupado': False,
                        'disponible_en': f"{random.randint(5, 60)} min"
                    }
        
        return {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'factor_ocupacion': factor_ocupacion,
            'gates_ocupados': gates_ocupados,
            'gates_disponibles': total_gates - gates_ocupados,
            'gate_status': gate_status,
            'runway_status': self._generate_runway_status(),
            'remote_positions': self._generate_remote_positions()
        }
    
    def _generate_runway_status(self) -> dict:
        """Estado actual de pistas"""
        return {
            'RW04/22': {
                'status': 'operativa',
                'operaciones_ultima_hora': random.randint(12, 18),
                'proximo_slot': f"{random.randint(5, 15)} min",
                'viento': f"{random.randint(5, 20)} km/h",
                'condicion': random.choice(['excelente', 'buena', 'regular'])
            },
            'RW18/36': {
                'status': 'operativa',
                'operaciones_ultima_hora': random.randint(8, 14),
                'proximo_slot': f"{random.randint(3, 12)} min",
                'viento': f"{random.randint(5, 20)} km/h",
                'condicion': random.choice(['excelente', 'buena'])
            }
        }
    
    def _generate_remote_positions(self) -> dict:
        """Estado posiciones remotas"""
        total_remote = self.airport_layout['positions_remote']
        ocupadas = random.randint(3, 10)
        
        return {
            'total': total_remote,
            'ocupadas': ocupadas,
            'disponibles': total_remote - ocupadas,
            'factor_ocupacion': ocupadas / total_remote
        }
    
    def create_airport_diagram(self) -> go.Figure:
        """Crea diagrama principal del aeropuerto"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Vista General AIFA',
                'Ocupación Gates por Sección', 
                'Status Pistas en Tiempo Real',
                'Distribución Operaciones'
            ],
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "indicator"}, {"type": "pie"}]
            ]
        )
        
        usage = self.generate_current_usage()
        
        # 1. Vista general del aeropuerto
        self._add_airport_overview(fig, usage, row=1, col=1)
        
        # 2. Ocupación por sección
        self._add_gate_occupancy(fig, usage, row=1, col=2)
        
        # 3. Status pistas
        self._add_runway_status(fig, usage, row=2, col=1)
        
        # 4. Distribución operaciones
        self._add_operations_distribution(fig, usage, row=2, col=2)
        
        fig.update_layout(
            title=f"🛬 AIFA - Layout en Tiempo Real ({usage['timestamp']})",
            height=800,
            showlegend=True
        )
        
        return fig
    
    def _add_airport_overview(self, fig, usage, row, col):
        """Agrega vista general del aeropuerto"""
        # Terminal principal
        fig.add_trace(
            go.Scatter(
                x=[0, 5, 5, 0, 0],
                y=[0, 0, 3, 3, 0],
                mode='lines',
                fill='toself',
                fillcolor='lightblue',
                line=dict(color='blue', width=2),
                name='Terminal',
                hovertemplate='Terminal Principal<br>Gates: 35<br>Ocupación: %{customdata}%<extra></extra>',
                customdata=[usage['factor_ocupacion'] * 100]
            ),
            row=row, col=col
        )
        
        # Pistas
        fig.add_trace(
            go.Scatter(
                x=[-2, 3],
                y=[1, 1],
                mode='lines',
                line=dict(color='gray', width=8),
                name='RW04/22 (4500m)',
                hovertemplate='Pista 04/22<br>4500m x 45m<br>Status: Operativa<extra></extra>'
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Scatter(
                x=[-1, 2],
                y=[2, 2],
                mode='lines',
                line=dict(color='darkgray', width=6),
                name='RW18/36 (3500m)',
                hovertemplate='Pista 18/36<br>3500m x 45m<br>Status: Operativa<extra></extra>'
            ),
            row=row, col=col
        )
        
        # Gates ocupados (puntos rojos) y libres (puntos verdes)
        gates_x = []
        gates_y = []
        gates_color = []
        gates_text = []
        
        y_pos = 0.5
        for seccion, gates in usage['gate_status'].items():
            x_start = 0.5 if seccion == 'A' else (2 if seccion == 'B' else 3.5)
            
            for i, (gate_num, status) in enumerate(gates.items()):
                gates_x.append(x_start + (i % 6) * 0.3)
                gates_y.append(y_pos + (i // 6) * 0.2)
                
                if status['ocupado']:
                    gates_color.append('red')
                    gates_text.append(f"{seccion}{gate_num}<br>{status['aerolinea']}<br>{status['destino']}")
                else:
                    gates_color.append('green')
                    gates_text.append(f"{seccion}{gate_num}<br>Disponible<br>{status['disponible_en']}")
            
            y_pos += 1
        
        fig.add_trace(
            go.Scatter(
                x=gates_x,
                y=gates_y,
                mode='markers',
                marker=dict(color=gates_color, size=8),
                name='Gates',
                text=gates_text,
                hovertemplate='%{text}<extra></extra>'
            ),
            row=row, col=col
        )
    
    def _add_gate_occupancy(self, fig, usage, row, col):
        """Gráfico de ocupación por sección"""
        secciones = []
        ocupados = []
        totales = []
        
        for seccion, gates in usage['gate_status'].items():
            secciones.append(f"Sección {seccion}")
            seccion_ocupados = sum(1 for g in gates.values() if g['ocupado'])
            ocupados.append(seccion_ocupados)
            totales.append(len(gates))
        
        fig.add_trace(
            go.Bar(
                name='Disponibles',
                x=secciones,
                y=[t - o for t, o in zip(totales, ocupados)],
                marker_color='lightgreen'
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Bar(
                name='Ocupados',
                x=secciones,
                y=ocupados,
                marker_color='lightcoral'
            ),
            row=row, col=col
        )
    
    def _add_runway_status(self, fig, usage, row, col):
        """Indicador de status pistas"""
        runway_ops = sum(r['operaciones_ultima_hora'] for r in usage['runway_status'].values())
        
        fig.add_trace(
            go.Indicator(
                mode = "gauge+number+delta",
                value = runway_ops,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Operaciones/Hora"},
                delta = {'reference': 25},
                gauge = {
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 35], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 40
                    }
                }
            ),
            row=row, col=col
        )
    
    def _add_operations_distribution(self, fig, usage, row, col):
        """Distribución de operaciones"""
        labels = ['Gates Ocupados', 'Gates Disponibles', 'Posiciones Remotas']
        values = [
            usage['gates_ocupados'],
            usage['gates_disponibles'],
            usage['remote_positions']['ocupadas']
        ]
        
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=.3
            ),
            row=row, col=col
        )
    
    def create_live_slots_map(self) -> go.Figure:
        """Mapa de slots en tiempo real"""
        usage = self.generate_current_usage()
        
        # Crear mapa base
        fig = go.Figure()
        
        # Agregar pistas como líneas
        for runway_name, runway_data in self.airport_layout['runways'].items():
            coords = runway_data['coordinates']
            fig.add_trace(
                go.Scattermapbox(
                    lat=[coords[0][0], coords[1][0]],
                    lon=[coords[0][1], coords[1][1]],
                    mode='lines',
                    line=dict(width=8, color='gray'),
                    name=f"{runway_name} ({runway_data['length']}m)",
                    hovertemplate=f"{runway_name}<br>Longitud: {runway_data['length']}m<br>Operaciones/hora: {usage['runway_status'][runway_name]['operaciones_ultima_hora']}<extra></extra>"
                )
            )
        
        # Agregar terminal
        fig.add_trace(
            go.Scattermapbox(
                lat=[self.aifa_coords['lat']],
                lon=[self.aifa_coords['lon']],
                mode='markers',
                marker=dict(
                    size=20,
                    color='blue',
                    symbol='building'
                ),
                name='Terminal',
                text=f"Ocupación: {usage['factor_ocupacion']*100:.1f}%",
                hovertemplate="Terminal AIFA<br>Gates: 35<br>Ocupación: %{text}<extra></extra>"
            )
        )
        
        # Configurar mapa
        fig.update_layout(
            title="🗺️ AIFA - Vista Aérea con Slots en Tiempo Real",
            mapbox=dict(
                style="satellite-streets",
                center=dict(lat=self.aifa_coords['lat'], lon=self.aifa_coords['lon']),
                zoom=14
            ),
            height=500,
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        return fig
    
    def generate_slots_timeline(self) -> go.Figure:
        """Timeline de slots próximas 2 horas"""
        fig = go.Figure()
        
        # Generar slots próximas 2 horas
        base_time = datetime.now()
        slots_data = []
        
        for i in range(48):  # Cada 2.5 min por 2 horas
            slot_time = base_time.timestamp() + (i * 150)  # 2.5 min intervals
            slot_datetime = datetime.fromtimestamp(slot_time)
            
            # Probabilidad de ocupación
            prob_ocupado = 0.7 if 6 <= slot_datetime.hour <= 9 or 18 <= slot_datetime.hour <= 21 else 0.4
            
            if random.random() < prob_ocupado:
                slots_data.append({
                    'time': slot_datetime,
                    'runway': random.choice(['RW04/22', 'RW18/36']),
                    'airline': random.choice(['VivaAerobus', 'Volaris', 'Aeromexico']),
                    'flight': f"VB{random.randint(100,999)}",
                    'operation': random.choice(['Departure', 'Arrival']),
                    'status': 'Scheduled'
                })
        
        # Crear timeline
        for runway in ['RW04/22', 'RW18/36']:
            runway_slots = [s for s in slots_data if s['runway'] == runway]
            
            if runway_slots:
                fig.add_trace(
                    go.Scatter(
                        x=[s['time'] for s in runway_slots],
                        y=[runway] * len(runway_slots),
                        mode='markers',
                        marker=dict(
                            size=12,
                            color=['blue' if s['operation'] == 'Departure' else 'green' for s in runway_slots]
                        ),
                        name=runway,
                        text=[f"{s['flight']}<br>{s['airline']}<br>{s['operation']}" for s in runway_slots],
                        hovertemplate='%{text}<br>%{x}<extra></extra>'
                    )
                )
        
        fig.update_layout(
            title="⏰ Timeline Slots - Próximas 2 Horas",
            xaxis_title="Tiempo",
            yaxis_title="Pista",
            height=300,
            xaxis=dict(type='date')
        )
        
        return fig
    
    def get_realtime_metrics(self) -> dict:
        """Obtiene métricas en tiempo real para el dashboard"""
        usage = self.generate_current_usage()
        
        return {
            'timestamp': usage['timestamp'],
            'active_flights': usage['gates_ocupados'] + random.randint(0, 5),
            'occupied_gates': usage['gates_ocupados'],
            'total_gates': self.airport_layout['terminal']['total_gates'],
            'gate_occupancy': (usage['gates_ocupados'] / self.airport_layout['terminal']['total_gates']) * 100,
            'landings_today': random.randint(45, 75),
            'takeoffs_today': random.randint(42, 78),
            'avg_delay': random.randint(8, 25),
            'runway_operations': sum(r['operaciones_ultima_hora'] for r in usage['runway_status'].values()),
            'remote_positions_used': usage['remote_positions']['ocupadas']
        }
    
    def get_upcoming_flights(self) -> list:
        """Genera lista de próximos vuelos para el dashboard"""
        upcoming = []
        base_time = datetime.now()
        
        airlines = ['VivaAerobus', 'Volaris', 'Aeromexico', 'Magnicharters', 'Interjet']
        destinations = ['CUN', 'GDL', 'TIJ', 'LAX', 'MIA', 'NYC', 'CDG', 'MAD']
        aircraft_types = ['A320', 'B737', 'E190', 'A321', 'A319']
        gates = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        
        for i in range(12):  # Próximos 12 vuelos
            flight_time = base_time + pd.Timedelta(minutes=random.randint(15, 180))
            
            flight_data = {
                'hora': flight_time.strftime('%H:%M'),
                'vuelo': f"{random.choice(['VB', 'Y4', 'AM', 'MH'])}{random.randint(100, 999)}",
                'aerolinea': random.choice(airlines),
                'destino': random.choice(destinations),
                'puerta': random.choice(gates),
                'estado': random.choice(['A Tiempo', 'Retrasado', 'Abordando', 'Confirmado']),
                'tipo': random.choice(['Salida', 'Llegada']),
                'aeronave': random.choice(aircraft_types)
            }
            
            upcoming.append(flight_data)
        
        # Ordenar por hora
        upcoming.sort(key=lambda x: x['hora'])
        return upcoming

# Funciones para integrar en el dashboard
def generar_diagrama_aeropuerto():
    """Genera diagrama principal del aeropuerto"""
    diagram = AIFAAirportDiagram()
    return diagram.create_airport_diagram()

def generar_mapa_slots_live():
    """Genera mapa de slots en tiempo real"""
    diagram = AIFAAirportDiagram()
    return diagram.create_live_slots_map()

def generar_timeline_slots():
    """Genera timeline de slots"""
    diagram = AIFAAirportDiagram()
    return diagram.generate_slots_timeline()

def obtener_metricas_aeropuerto():
    """Obtiene métricas actuales del aeropuerto"""
    diagram = AIFAAirportDiagram()
    return diagram.generate_current_usage()

if __name__ == "__main__":
    # Prueba del diagrama
    diagram = AIFAAirportDiagram()
    usage = diagram.generate_current_usage()
    
    print("🛬 MÉTRICAS AEROPUERTO AIFA")
    print("-" * 40)
    print(f"⏰ Hora: {usage['timestamp']}")
    print(f"🚪 Gates ocupados: {usage['gates_ocupados']}/{35}")
    print(f"📊 Factor ocupación: {usage['factor_ocupacion']*100:.1f}%")
    print(f"🛫 Operaciones RW04/22: {usage['runway_status']['RW04/22']['operaciones_ultima_hora']}/hora")
    print(f"🛬 Operaciones RW18/36: {usage['runway_status']['RW18/36']['operaciones_ultima_hora']}/hora")
    
    # Probar nuevas funciones
    print(f"\n📊 MÉTRICAS ADICIONALES")
    print("-" * 40)
    metrics = diagram.get_realtime_metrics()
    print(f"✈️ Vuelos activos: {metrics['active_flights']}")
    print(f"🚪 Ocupación gates: {metrics['gate_occupancy']:.1f}%")
    print(f"🛬 Aterrizajes hoy: {metrics['landings_today']}")
    print(f"🛫 Despegues hoy: {metrics['takeoffs_today']}")
    print(f"⏱️ Retraso promedio: {metrics['avg_delay']} min")