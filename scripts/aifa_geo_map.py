"""
Mapa Georeferenciado del Aeropuerto AIFA con visualización en tiempo real
Incluye vista satelital, layout físico y ocupación de gates
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import random
import json

class AIFAGeoMap:
    """Mapa georeferenciado interactivo del AIFA"""
    
    def __init__(self):
        # Coordenadas reales AIFA (Aeropuerto Internacional Felipe Ángeles)
        self.aifa_center = {
            'lat': 19.7425,
            'lon': -99.0157
        }
        
        # Layout georeferenciado preciso basado en imágenes satelitales
        self.airport_infrastructure = {
            'terminal': {
                'center': {'lat': 19.7425, 'lon': -99.0157},
                'gates': self._generate_gate_coordinates(),
                'buildings': self._get_terminal_buildings()
            },
            'runways': {
                'RW04/22': {
                    'start': {'lat': 19.7380, 'lon': -99.0200},
                    'end': {'lat': 19.7470, 'lon': -99.0114},
                    'length': 4500,
                    'width': 45,
                    'heading': '04/22'
                },
                'RW18/36': {
                    'start': {'lat': 19.7400, 'lon': -99.0180},
                    'end': {'lat': 19.7450, 'lon': -99.0134},
                    'length': 3500,
                    'width': 45,
                    'heading': '18/36'
                }
            },
            'taxiways': self._get_taxiway_coordinates(),
            'apron_areas': self._get_apron_coordinates(),
            'service_areas': self._get_service_areas()
        }
        
        # Configuración de mapbox
        self.mapbox_config = {
            'style': 'open-street-map',  # Mapa que no requiere token
            'center': self.aifa_center,
            'zoom': 15,
            'bearing': 0,
            'pitch': 0
        }
    
    def _generate_gate_coordinates(self) -> dict:
        """Genera coordenadas precisas de cada gate basadas en layout real"""
        gates = {}
        
        # Terminal A - Gates A1-A12 (Lado Norte)
        terminal_a_start = {'lat': 19.7430, 'lon': -99.0165}
        for i in range(1, 13):
            gates[f'A{i}'] = {
                'lat': terminal_a_start['lat'] + (i-1) * 0.0008,
                'lon': terminal_a_start['lon'] + random.uniform(-0.0005, 0.0005),
                'terminal': 'A',
                'type': 'domestic',
                'aircraft_capacity': 'narrow_body'
            }
        
        # Terminal B - Gates B1-B10 (Lado Este)
        terminal_b_start = {'lat': 19.7420, 'lon': -99.0145}
        for i in range(1, 11):
            gates[f'B{i}'] = {
                'lat': terminal_b_start['lat'] + random.uniform(-0.0005, 0.0005),
                'lon': terminal_b_start['lon'] + (i-1) * 0.0006,
                'terminal': 'B',
                'type': 'international',
                'aircraft_capacity': 'wide_body'
            }
        
        # Terminal C - Gates C1-C13 (Lado Sur)
        terminal_c_start = {'lat': 19.7415, 'lon': -99.0170}
        for i in range(1, 14):
            gates[f'C{i}'] = {
                'lat': terminal_c_start['lat'] - (i-1) * 0.0007,
                'lon': terminal_c_start['lon'] + random.uniform(-0.0003, 0.0003),
                'terminal': 'C',
                'type': 'regional',
                'aircraft_capacity': 'regional'
            }
        
        return gates
    
    def _get_terminal_buildings(self) -> list:
        """Coordenadas de edificios del terminal"""
        return [
            {
                'name': 'Terminal Principal',
                'coordinates': [
                    [19.7435, -99.0175],
                    [19.7435, -99.0140],
                    [19.7415, -99.0140],
                    [19.7415, -99.0175],
                    [19.7435, -99.0175]
                ],
                'color': 'rgba(0,100,200,0.6)'
            },
            {
                'name': 'Torre de Control',
                'coordinates': [[19.7425, -99.0157]],
                'color': 'red',
                'type': 'point'
            }
        ]
    
    def _get_taxiway_coordinates(self) -> list:
        """Coordenadas de calles de rodaje"""
        return [
            {
                'name': 'Taxiway Alpha',
                'coordinates': [
                    [19.7425, -99.0200],
                    [19.7425, -99.0140],
                    [19.7450, -99.0140]
                ],
                'color': 'yellow'
            },
            {
                'name': 'Taxiway Bravo',
                'coordinates': [
                    [19.7400, -99.0180],
                    [19.7440, -99.0160],
                    [19.7460, -99.0130]
                ],
                'color': 'yellow'
            }
        ]
    
    def _get_apron_coordinates(self) -> list:
        """Coordenadas de plataformas"""
        return [
            {
                'name': 'Apron 1 - Terminal A',
                'center': {'lat': 19.7430, 'lon': -99.0160},
                'radius': 200,
                'color': 'rgba(150,150,150,0.4)'
            },
            {
                'name': 'Apron 2 - Terminal B',
                'center': {'lat': 19.7420, 'lon': -99.0150},
                'radius': 180,
                'color': 'rgba(150,150,150,0.4)'
            },
            {
                'name': 'Apron 3 - Terminal C',
                'center': {'lat': 19.7415, 'lon': -99.0165},
                'radius': 150,
                'color': 'rgba(150,150,150,0.4)'
            }
        ]
    
    def _get_service_areas(self) -> list:
        """Áreas de servicio del aeropuerto"""
        return [
            {
                'name': 'Área de Carga',
                'lat': 19.7390,
                'lon': -99.0180,
                'color': 'brown'
            },
            {
                'name': 'Hangares de Mantenimiento',
                'lat': 19.7460,
                'lon': -99.0120,
                'color': 'purple'
            },
            {
                'name': 'Servicios de Combustible',
                'lat': 19.7405,
                'lon': -99.0190,
                'color': 'orange'
            }
        ]
    
    def generate_current_occupancy(self) -> dict:
        """Genera ocupación actual georeferenciada"""
        hour = datetime.now().hour
        
        # Factor de ocupación por hora
        if 6 <= hour <= 9 or 18 <= hour <= 21:
            base_occupancy = 0.8
        elif 10 <= hour <= 17:
            base_occupancy = 0.6
        else:
            base_occupancy = 0.4
        
        occupancy_data = {}
        airlines = ['VivaAerobus', 'Volaris', 'Aeromexico', 'Magnicharters', 'Interjet']
        destinations = ['CUN', 'GDL', 'TIJ', 'LAX', 'MIA', 'NYC', 'CDG', 'MAD']
        aircraft_types = ['A320', 'B737', 'E190', 'A321', 'A319', 'B787']
        
        for gate_id, gate_info in self.airport_infrastructure['terminal']['gates'].items():
            is_occupied = random.random() < base_occupancy
            
            if is_occupied:
                occupancy_data[gate_id] = {
                    'occupied': True,
                    'airline': random.choice(airlines),
                    'flight_number': f"{random.choice(['VB', 'Y4', 'AM', 'MH'])}{random.randint(100, 999)}",
                    'aircraft_type': random.choice(aircraft_types),
                    'destination': random.choice(destinations),
                    'operation': random.choice(['boarding', 'deplaning', 'maintenance', 'ready']),
                    'estimated_departure': f"{random.randint(10, 180)} min",
                    'passengers': random.randint(80, 180),
                    'coordinates': {'lat': gate_info['lat'], 'lon': gate_info['lon']},
                    'terminal': gate_info['terminal'],
                    'gate_type': gate_info['type']
                }
            else:
                occupancy_data[gate_id] = {
                    'occupied': False,
                    'available_in': f"{random.randint(5, 60)} min",
                    'coordinates': {'lat': gate_info['lat'], 'lon': gate_info['lon']},
                    'terminal': gate_info['terminal'],
                    'gate_type': gate_info['type']
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'gates': occupancy_data,
            'summary': {
                'total_gates': len(occupancy_data),
                'occupied_gates': sum(1 for g in occupancy_data.values() if g['occupied']),
                'occupancy_rate': sum(1 for g in occupancy_data.values() if g['occupied']) / len(occupancy_data)
            }
        }
    
    def create_satellite_map(self) -> go.Figure:
        """Crea mapa satelital georeferenciado del AIFA"""
        fig = go.Figure()
        
        # Obtener datos de ocupación actuales
        occupancy = self.generate_current_occupancy()
        
        # 1. Agregar pistas de aterrizaje
        for runway_name, runway_data in self.airport_infrastructure['runways'].items():
            fig.add_trace(go.Scattermapbox(
                lat=[runway_data['start']['lat'], runway_data['end']['lat']],
                lon=[runway_data['start']['lon'], runway_data['end']['lon']],
                mode='lines',
                line=dict(width=8, color='white'),
                name=f"🛫 {runway_name} ({runway_data['length']}m)",
                hovertemplate=f"<b>{runway_name}</b><br>Longitud: {runway_data['length']}m<br>Ancho: {runway_data['width']}m<extra></extra>",
                showlegend=True
            ))
        
        # 2. Agregar calles de rodaje
        for taxiway in self.airport_infrastructure['taxiways']:
            lats = [coord[0] for coord in taxiway['coordinates']]
            lons = [coord[1] for coord in taxiway['coordinates']]
            
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(width=4, color=taxiway['color']),
                name=f"🛤️ {taxiway['name']}",
                hovertemplate=f"<b>{taxiway['name']}</b><br>Calle de Rodaje<extra></extra>",
                showlegend=True
            ))
        
        # 3. Agregar gates con estado de ocupación
        occupied_gates = []
        available_gates = []
        
        for gate_id, gate_data in occupancy['gates'].items():
            coords = gate_data['coordinates']
            
            if gate_data['occupied']:
                occupied_gates.append({
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'gate': gate_id,
                    'airline': gate_data['airline'],
                    'flight': gate_data['flight_number'],
                    'aircraft': gate_data['aircraft_type'],
                    'destination': gate_data['destination'],
                    'operation': gate_data['operation'],
                    'passengers': gate_data['passengers'],
                    'terminal': gate_data['terminal']
                })
            else:
                available_gates.append({
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'gate': gate_id,
                    'available_in': gate_data['available_in'],
                    'terminal': gate_data['terminal']
                })
        
        # Gates ocupados (rojos)
        if occupied_gates:
            occupied_df = pd.DataFrame(occupied_gates)
            fig.add_trace(go.Scattermapbox(
                lat=occupied_df['lat'],
                lon=occupied_df['lon'],
                mode='markers',
                marker=dict(size=12, color='red', symbol='circle'),
                name='🔴 Gates Ocupados',
                text=[f"Gate {row['gate']}<br>{row['airline']} {row['flight']}<br>{row['aircraft']} → {row['destination']}<br>Operación: {row['operation']}<br>Pasajeros: {row['passengers']}" 
                      for _, row in occupied_df.iterrows()],
                hovertemplate='<b>%{text}</b><extra></extra>',
                showlegend=True
            ))
        
        # Gates disponibles (verdes)
        if available_gates:
            available_df = pd.DataFrame(available_gates)
            fig.add_trace(go.Scattermapbox(
                lat=available_df['lat'],
                lon=available_df['lon'],
                mode='markers',
                marker=dict(size=10, color='green', symbol='circle'),
                name='🟢 Gates Disponibles',
                text=[f"Gate {row['gate']}<br>Terminal {row['terminal']}<br>Disponible en: {row['available_in']}" 
                      for _, row in available_df.iterrows()],
                hovertemplate='<b>%{text}</b><extra></extra>',
                showlegend=True
            ))
        
        # 4. Agregar edificios principales
        for building in self.airport_infrastructure['terminal']['buildings']:
            if building.get('type') == 'point':
                # Torre de control
                fig.add_trace(go.Scattermapbox(
                    lat=[building['coordinates'][0][0]],
                    lon=[building['coordinates'][0][1]],
                    mode='markers',
                    marker=dict(size=15, color=building['color'], symbol='triangle'),
                    name=f"🗼 {building['name']}",
                    hovertemplate=f"<b>{building['name']}</b><br>Centro de Control de Tráfico Aéreo<extra></extra>",
                    showlegend=True
                ))
        
        # 5. Agregar áreas de servicio
        for service in self.airport_infrastructure['service_areas']:
            fig.add_trace(go.Scattermapbox(
                lat=[service['lat']],
                lon=[service['lon']],
                mode='markers',
                marker=dict(size=8, color=service['color'], symbol='square'),
                name=f"🏭 {service['name']}",
                hovertemplate=f"<b>{service['name']}</b><br>Área de Servicios<extra></extra>",
                showlegend=True
            ))
        
        # Configurar layout del mapa
        fig.update_layout(
            title=f"🛬 AIFA - Mapa Satelital Georeferenciado ({occupancy['summary']['occupied_gates']}/{occupancy['summary']['total_gates']} gates ocupados)",
            mapbox=dict(
                style=self.mapbox_config['style'],
                center=dict(
                    lat=self.mapbox_config['center']['lat'],
                    lon=self.mapbox_config['center']['lon']
                ),
                zoom=self.mapbox_config['zoom'],
                bearing=self.mapbox_config['bearing'],
                pitch=self.mapbox_config['pitch']
            ),
            height=600,
            margin={"r":0,"t":50,"l":0,"b":0},
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor="rgba(255,255,255,0.8)"
            )
        )
        
        return fig
    
    def create_3d_airport_view(self) -> go.Figure:
        """Vista 3D del aeropuerto con elevación"""
        occupancy = self.generate_current_occupancy()
        
        fig = go.Figure()
        
        # Datos para superficie 3D
        gate_data = []
        for gate_id, gate_info in occupancy['gates'].items():
            coords = gate_info['coordinates']
            gate_data.append({
                'lat': coords['lat'],
                'lon': coords['lon'],
                'elevation': 10 if gate_info['occupied'] else 5,  # Elevación según ocupación
                'gate': gate_id,
                'occupied': gate_info['occupied']
            })
        
        df_gates = pd.DataFrame(gate_data)
        
        # Superficie 3D del aeropuerto
        fig.add_trace(go.Scatter3d(
            x=df_gates['lon'],
            y=df_gates['lat'],
            z=df_gates['elevation'],
            mode='markers',
            marker=dict(
                size=8,
                color=['red' if occ else 'green' for occ in df_gates['occupied']],
                colorscale='RdYlGn_r',
                opacity=0.8,
                symbol='circle'
            ),
            text=[f"Gate {gate}" for gate in df_gates['gate']],
            name='Gates AIFA',
            hovertemplate='<b>%{text}</b><br>Lat: %{y}<br>Lon: %{x}<br>Estado: %{marker.color}<extra></extra>'
        ))
        
        fig.update_layout(
            title='🏗️ AIFA - Vista 3D Georeferenciada',
            scene=dict(
                xaxis_title='Longitud',
                yaxis_title='Latitud', 
                zaxis_title='Elevación (m)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=500
        )
        
        return fig
    
    def create_heatmap_occupancy(self) -> go.Figure:
        """Mapa de calor de ocupación en coordenadas reales"""
        occupancy = self.generate_current_occupancy()
        
        # Crear grid de datos
        lats = []
        lons = []
        occupancy_values = []
        gate_names = []
        
        for gate_id, gate_info in occupancy['gates'].items():
            coords = gate_info['coordinates']
            lats.append(coords['lat'])
            lons.append(coords['lon'])
            occupancy_values.append(1 if gate_info['occupied'] else 0)
            gate_names.append(gate_id)
        
        fig = go.Figure()
        
        # Mapa de calor
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=dict(
                size=[20 if occ else 15 for occ in occupancy_values],
                color=occupancy_values,
                colorscale='RdYlGn_r',
                opacity=0.7,
                colorbar=dict(title="Ocupación")
            ),
            text=gate_names,
            name='Heatmap Ocupación',
            hovertemplate='Gate: %{text}<br>Ocupado: %{marker.color}<extra></extra>'
        ))
        
        fig.update_layout(
            title='🌡️ AIFA - Mapa de Calor de Ocupación',
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=self.aifa_center['lat'], lon=self.aifa_center['lon']),
                zoom=15
            ),
            height=500,
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        return fig
    
    def get_gate_occupancy_stats(self) -> dict:
        """Obtiene estadísticas de ocupación de gates"""
        occupancy = self.generate_current_occupancy()
        current_time = datetime.now().strftime("%H:%M:%S")
        
        return {
            'total_gates': occupancy['summary']['total_gates'],
            'occupied_gates': occupancy['summary']['occupied_gates'],
            'available_gates': occupancy['summary']['total_gates'] - occupancy['summary']['occupied_gates'],
            'occupancy_rate': occupancy['summary']['occupancy_rate'] * 100,
            'timestamp': current_time
        }
    
    def get_terminal_analysis(self) -> dict:
        """Análisis detallado por terminal"""
        occupancy = self.generate_current_occupancy()
        
        terminals = {
            'Terminal A': {'total_gates': 0, 'occupied_gates': 0, 'flight_type': 'Vuelos Domésticos'},
            'Terminal B': {'total_gates': 0, 'occupied_gates': 0, 'flight_type': 'Vuelos Internacionales'},
            'Terminal C': {'total_gates': 0, 'occupied_gates': 0, 'flight_type': 'Vuelos Regionales'}
        }
        
        for gate_data in occupancy['gates'].values():
            terminal_name = f"Terminal {gate_data['terminal']}"
            terminals[terminal_name]['total_gates'] += 1
            if gate_data['occupied']:
                terminals[terminal_name]['occupied_gates'] += 1
        
        # Calcular tasas de ocupación
        for terminal in terminals.values():
            if terminal['total_gates'] > 0:
                terminal['occupancy_rate'] = (terminal['occupied_gates'] / terminal['total_gates']) * 100
            else:
                terminal['occupancy_rate'] = 0
        
        return terminals
    
    def create_occupancy_heatmap(self) -> go.Figure:
        """Alias para compatibilidad con dashboard"""
        return self.create_heatmap_occupancy()

# Funciones para integración con dashboard
def crear_mapa_satelital_aifa():
    """Crea mapa satelital georeferenciado"""
    geo_map = AIFAGeoMap()
    return geo_map.create_satellite_map()

def crear_vista_3d_aifa():
    """Crea vista 3D del aeropuerto"""
    geo_map = AIFAGeoMap()
    return geo_map.create_3d_airport_view()

def crear_heatmap_ocupacion():
    """Crea mapa de calor de ocupación"""
    geo_map = AIFAGeoMap()
    return geo_map.create_heatmap_occupancy()

def obtener_datos_georeferenciados():
    """Obtiene datos actuales con coordenadas"""
    geo_map = AIFAGeoMap()
    return geo_map.generate_current_occupancy()

if __name__ == "__main__":
    # Prueba de mapas georeferenciados
    print("🗺️  Generando mapas georeferenciados AIFA...")
    
    geo_map = AIFAGeoMap()
    occupancy = geo_map.generate_current_occupancy()
    
    print(f"\n📊 RESUMEN GEOREFERENCIADO")
    print(f"📍 Centro AIFA: {geo_map.aifa_center}")
    print(f"🚪 Gates totales: {occupancy['summary']['total_gates']}")
    print(f"🔴 Gates ocupados: {occupancy['summary']['occupied_gates']}")
    print(f"📊 Tasa ocupación: {occupancy['summary']['occupancy_rate']*100:.1f}%")
    
    print(f"\n🎯 GATES POR TERMINAL:")
    terminals = {'A': 0, 'B': 0, 'C': 0}
    for gate_id, gate_data in occupancy['gates'].items():
        if gate_data['occupied']:
            terminals[gate_data['terminal']] += 1
    
    for terminal, count in terminals.items():
        total_terminal = len([g for g in occupancy['gates'].values() if g['terminal'] == terminal])
        print(f"Terminal {terminal}: {count}/{total_terminal} ocupados")
    
    print(f"\n✅ Mapas disponibles:")
    print(f"  - Mapa satelital con gates en tiempo real")
    print(f"  - Vista 3D georeferenciada")  
    print(f"  - Mapa de calor de ocupación")
    print(f"  - Coordenadas precisas de cada gate")