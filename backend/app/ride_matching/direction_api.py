import requests
import json
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import transform
from pyproj import Transformer
from typing import Dict, List, Tuple, Optional

class RouteCorridorVisualizer:
    def __init__(self, access_token: str):
        """
        Initialize Mapbox Directions API client with corridor visualization
        
        Args:
            access_token: Your Mapbox API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.mapbox.com/directions/v5"
    
    def get_directions(
        self,
        coordinates: List[Tuple[float, float]],
        profile: str = "mapbox/driving-traffic"
    ) -> Dict:
        """
        Get directions between waypoints
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Routing profile 
            
        Returns:
            JSON response from Mapbox API
        """
        
        # Format coordinates as semicolon-separated string
        coords_str = ";".join([f"{lng},{lat}" for lng, lat in coordinates])
        
        # Build URL
        url = f"{self.base_url}/{profile}/{coords_str}"
        
        # Parameters
        params = {
            "access_token": self.access_token,
            "geometries": "geojson",
            "overview": "full"
        }
        
        # Make request
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
    
    def extract_coordinates(self, route_geometry) -> List[Tuple[float, float]]:
        """
        Extract coordinates from route geometry
        
        Args:
            route_geometry: GeoJSON geometry dict
            
        Returns:
            List of (latitude, longitude) tuples
        """
        
        if isinstance(route_geometry, dict) and route_geometry.get("type") == "LineString":
            coordinates = route_geometry["coordinates"]
            # Convert from [lng, lat] to (lat, lng) for easier handling
            return [(coord[1], coord[0]) for coord in coordinates]
        else:
            print(f"Unexpected geometry type: {type(route_geometry)}")
            return []
    
    def create_buffer_corridor(
        self, 
        coordinates: List[Tuple[float, float]], 
        buffer_distance_meters: float = 2000
    ) -> List[Tuple[float, float]]:
        """
        Create a buffer corridor around the route
        
        Args:
            coordinates: List of (lat, lng) tuples
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            List of (lat, lng) tuples forming the buffer polygon
        """
        
        if len(coordinates) < 2:
            return []
        
        try:
            # Convert to lng, lat for Shapely (Shapely expects x, y format)
            shapely_coords = [(lng, lat) for lat, lng in coordinates]
            
            # Create LineString
            line = LineString(shapely_coords)
            
            # Create transformer for meters-based projection (approximate)
            # Using Web Mercator for simplicity
            transformer_to_meters = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            transformer_to_degrees = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
            
            # Transform to meters
            line_meters = transform(transformer_to_meters.transform, line)
            
            # Create buffer in meters
            buffer_meters = line_meters.buffer(buffer_distance_meters)
            
            # Transform back to lat/lng
            buffer_degrees = transform(transformer_to_degrees.transform, buffer_meters)
            
            # Extract exterior coordinates
            if hasattr(buffer_degrees, 'exterior'):
                buffer_coords = list(buffer_degrees.exterior.coords)
                # Convert back to (lat, lng) format
                return [(lat, lng) for lng, lat in buffer_coords]
            else:
                print("Buffer creation failed - no exterior boundary")
                return []
                
        except Exception as e:
            print(f"Error creating buffer: {e}")
            # Fallback: simple circular buffer around each point
            return self.simple_buffer(coordinates, buffer_distance_meters)
    
    def simple_buffer(
        self, 
        coordinates: List[Tuple[float, float]], 
        buffer_distance_meters: float
    ) -> List[Tuple[float, float]]:
        """
        Simple fallback buffer using circles around route points
        
        Args:
            coordinates: List of (lat, lng) tuples
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            List of (lat, lng) tuples approximating buffer
        """
        
        # Approximate degrees per meter (rough conversion)
        meters_per_degree = 111000  # Approximate
        buffer_degrees = buffer_distance_meters / meters_per_degree
        
        buffer_points = []
        
        for i, (lat, lng) in enumerate(coordinates[::max(1, len(coordinates)//20)]):
            # Create points around each coordinate
            for angle in range(0, 360, 30):  # Every 30 degrees
                angle_rad = np.radians(angle)
                offset_lat = lat + buffer_degrees * np.sin(angle_rad)
                offset_lng = lng + buffer_degrees * np.cos(angle_rad)
                buffer_points.append((offset_lat, offset_lng))
        
        return buffer_points
    
    def plot_route_with_corridor(
        self, 
        response: Dict, 
        buffer_distance_meters: float = 2000,
        title: str = "Route with Buffer Corridor"
    ) -> None:
        """
        Plot the route with buffer corridor using Plotly
        
        Args:
            response: Response from Mapbox Directions API
            buffer_distance_meters: Buffer distance in meters
            title: Title for the plot
        """
        
        if not response or response.get("code") != "Ok":
            print("❌ No valid route to plot")
            return
            
        routes = response.get("routes", [])
        if not routes:
            print("❌ No routes in response")
            return
        
        # Use the first route
        route = routes[0]
        geometry = route["geometry"]
        
        print(f"📊 Plotting route with {buffer_distance_meters}m corridor...")
        print(f"   Distance: {route['distance']:.1f} meters ({route['distance']/1000:.1f}km)")
        print(f"   Duration: {route['duration']:.1f} seconds ({route['duration']/60:.1f}min)")
        
        # Extract coordinates
        coordinates = self.extract_coordinates(geometry)
        
        if not coordinates:
            print("❌ Couldn't extract coordinates from geometry")
            return
        
        print(f"   Found {len(coordinates)} coordinate points")
        
        # Create buffer corridor
        print(f"   Creating {buffer_distance_meters}m buffer corridor...")
        buffer_coords = self.create_buffer_corridor(coordinates, buffer_distance_meters)
        
        if not buffer_coords:
            print("❌ Couldn't create buffer corridor")
            return
        
        print(f"   Created buffer with {len(buffer_coords)} boundary points")
        
        # Create the map
        fig = go.Figure()
        
        # Add buffer corridor (fill)
        if buffer_coords:
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=[coord[1] for coord in buffer_coords] + [buffer_coords[0][1]],  # Close the polygon
                lat=[coord[0] for coord in buffer_coords] + [buffer_coords[0][0]],
                fill="toself",
                fillcolor="rgba(255, 0, 0, 0.1)",  # Light red fill
                line=dict(width=1, color='rgba(255, 0, 0, 0.3)'),
                name=f"Buffer Corridor ({buffer_distance_meters}m)",
                hovertemplate=f"Buffer Zone ({buffer_distance_meters}m)<br>Lat: %{{lat}}<br>Lon: %{{lon}}<extra></extra>"
            ))
        
        # Add route line (on top of buffer)
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[coord[1] for coord in coordinates],
            lat=[coord[0] for coord in coordinates],
            line=dict(width=4, color='blue'),
            name="Route",
            hovertemplate="Route<br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
        ))
        
        # Add start point
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[coordinates[0][1]],
            lat=[coordinates[0][0]],
            marker=dict(size=15, color='green', symbol="circle"),
            name="Start",
            hovertemplate="Start Point<br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
        ))
        
        # Add end point
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[coordinates[-1][1]],
            lat=[coordinates[-1][0]],
            marker=dict(size=15, color='red', symbol="circle"),
            name="End",
            hovertemplate="End Point<br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
        ))
        
        # Calculate center and zoom
        center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
        center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            title=f"{title}<br>Distance: {route['distance']/1000:.2f}km, Duration: {route['duration']/60:.1f}min, Buffer: {buffer_distance_meters}m",
            height=700,
            showlegend=True
        )
        
        # Show the plot
        fig.show()
        
        return coordinates, buffer_coords


def main():
    # Your Mapbox token
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    # Initialize visualizer
    viz = RouteCorridorVisualizer(MAPBOX_TOKEN)
    
    print("🗺️  Route Corridor Visualization")
    print("=" * 50)
    
    # Example coordinates - change these to test your area
    coordinates = [
        # (-122.42, 37.78),  # San Francisco  
        # (-122.27, 37.80)   # Oakland
        (-113.525540, 53.519250),
        (-113.606566, 53.430753)
    ]
    
    print(f"📍 Getting route from {coordinates[0]} to {coordinates[1]}")
    
    # Get route
    response = viz.get_directions(coordinates=coordinates)
    
    if response:
        # Test different buffer sizes
        buffer_sizes = [1000, 2000, 3000]  # 1km, 2km, 3km
        
        for buffer_size in buffer_sizes:
            print(f"\n🛣️  Creating {buffer_size}m corridor...")
            route_coords, buffer_coords = viz.plot_route_with_corridor(
                response, 
                buffer_distance_meters=buffer_size,
                title=f"Route with {buffer_size}m Buffer Corridor"
            )
    else:
        print("❌ Failed to get route")


if __name__ == "__main__":
    main()