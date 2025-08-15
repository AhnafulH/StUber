import requests
import json
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from supabase import create_client, Client
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import os
load_dotenv()

class RouteCorridorVisualizer:
    def __init__(self, access_token: str, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Mapbox Directions API client with corridor visualization
        
        Args:
            access_token: Your Mapbox API access token
            supabase_url: Your Supabase project URL (optional, for PostGIS)
            supabase_key: Your Supabase anon key (optional, for PostGIS)
        """
        self.access_token = access_token
        self.base_url = "https://api.mapbox.com/directions/v5"
        
        # Initialize Supabase client if credentials provided
        self.use_postgis = supabase_url and supabase_key
        if self.use_postgis:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            print("✅ PostGIS mode enabled (using Supabase)")
        else:
            print("⚠️  Shapely mode enabled (install 'supabase' for PostGIS)")
    
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
    
    def create_buffer_corridor_postgis(
        self, 
        route_geometry: Dict,
        buffer_distance_meters: float = 2000
    ) -> Tuple[List[Tuple[float, float]], Dict]:
        """
        Create a buffer corridor using PostGIS
        
        Args:
            route_geometry: GeoJSON geometry from Mapbox
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            Tuple of (buffer_coordinates, corridor_info)
        """
        
        if not self.use_postgis:
            print("❌ PostGIS not available - use Shapely fallback")
            return [], {}
        
        try:
            print(f"🔧 Creating {buffer_distance_meters}m corridor with PostGIS...")
            
            # Call the PostgreSQL function
            result = self.supabase.rpc(
                'create_route_corridor',
                {
                    'route_geojson': route_geometry,
                    'buffer_distance_meters': int(buffer_distance_meters)
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                corridor_data = result.data[0]
                corridor_info = corridor_data['corridor_info']
                
                print(f"✅ PostGIS corridor created!")
                print(f"   Buffer distance: {corridor_info['buffer_distance_km']:.1f} km")
                print(f"   Corridor area: {corridor_info['corridor_area_km2']:.2f} km²")
                
                # Parse the corridor GeoJSON
                corridor_geojson = json.loads(corridor_data['corridor_geojson'])
                
                if corridor_geojson['type'] == 'Polygon':
                    # Extract coordinates and convert to (lat, lng) format
                    coords = corridor_geojson['coordinates'][0]  # Exterior ring
                    buffer_coords = [(coord[1], coord[0]) for coord in coords]  # Convert lng,lat to lat,lng
                    
                    return buffer_coords, corridor_info
                else:
                    print(f"❌ Unexpected corridor geometry type: {corridor_geojson['type']}")
                    return [], {}
            else:
                print("❌ No data returned from PostGIS function")
                return [], {}
                
        except Exception as e:
            print(f"❌ PostGIS error: {e}")
            print("🔄 Falling back to Shapely method...")
            return self.create_buffer_corridor_shapely(route_geometry, buffer_distance_meters)
    
    def create_buffer_corridor_shapely(
        self, 
        route_geometry: Dict,
        buffer_distance_meters: float = 2000
    ) -> Tuple[List[Tuple[float, float]], Dict]:
        """
        Create a buffer corridor using Shapely (fallback method)
        
        Args:
            route_geometry: GeoJSON geometry from Mapbox
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            Tuple of (buffer_coordinates, corridor_info)
        """
        
        # Extract route coordinates
        coordinates = self.extract_coordinates(route_geometry)
        
        if len(coordinates) < 2:
            return [], {}
        
        try:
            # Import here to make it optional
            from shapely.geometry import LineString
            from shapely.ops import transform
            from pyproj import Transformer
            
            # Convert to lng, lat for Shapely (Shapely expects x, y format)
            shapely_coords = [(lng, lat) for lat, lng in coordinates]
            
            # Create LineString
            line = LineString(shapely_coords)
            
            # Create transformer for meters-based projection
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
                buffer_coordinates = [(lat, lng) for lng, lat in buffer_coords]
                
                # Create corridor info
                corridor_info = {
                    'buffer_distance_meters': buffer_distance_meters,
                    'buffer_distance_km': buffer_distance_meters / 1000.0,
                    'corridor_area_km2': buffer_degrees.area / 1000000.0,  # Approximate
                    'corridor_perimeter_km': buffer_degrees.length / 1000.0  # Approximate
                }
                
                return buffer_coordinates, corridor_info
            else:
                print("Buffer creation failed - no exterior boundary")
                return [], {}
                
        except ImportError:
            print("❌ Shapely/PyProj not installed. Install with: pip install shapely pyproj")
            return [], {}
        except Exception as e:
            print(f"Error creating Shapely buffer: {e}")
            return [], {}
    
    def create_buffer_corridor(
        self, 
        route_geometry: Dict,
        buffer_distance_meters: float = 2000
    ) -> Tuple[List[Tuple[float, float]], Dict]:
        """
        Create a buffer corridor using best available method
        
        Args:
            route_geometry: GeoJSON geometry from Mapbox (not coordinates!)
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            Tuple of (buffer_coordinates, corridor_info)
        """
        
        if self.use_postgis:
            return self.create_buffer_corridor_postgis(route_geometry, buffer_distance_meters)
        else:
            return self.create_buffer_corridor_shapely(route_geometry, buffer_distance_meters)
    
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
        
        # Extract route coordinates for visualization
        coordinates = self.extract_coordinates(geometry)
        
        if not coordinates:
            print("❌ Couldn't extract coordinates from geometry")
            return
        
        print(f"   Found {len(coordinates)} coordinate points")
        
        # Create buffer corridor - pass the geometry object, not coordinates!
        buffer_coords, corridor_info = self.create_buffer_corridor(geometry, buffer_distance_meters)
        
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
        
        # Create title with corridor info
        method = "PostGIS" if self.use_postgis else "Shapely"
        title_text = f"{title} ({method})<br>Distance: {route['distance']/1000:.2f}km, Duration: {route['duration']/60:.1f}min"
        
        if corridor_info:
            title_text += f", Buffer: {corridor_info.get('buffer_distance_km', buffer_distance_meters/1000):.1f}km"
            if 'corridor_area_km2' in corridor_info:
                title_text += f", Area: {corridor_info['corridor_area_km2']:.1f}km²"
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            title=title_text,
            height=700,
            showlegend=True
        )
        
        # Show the plot
        fig.show()
        
        return coordinates, buffer_coords


def main():
    # Configuration
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    # Supabase credentials (optional - if not provided, will use Shapely)
    SUPABASE_URL = os.environ.get("SUPABASE_URL") # Replace with your URL
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # Replace with your key
    
    # Initialize visualizer with PostGIS support
    viz = RouteCorridorVisualizer(
        access_token=MAPBOX_TOKEN,
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )
    
    print("🗺️  Route Corridor Visualization")
    print("=" * 50)
    
    # Your coordinates
    coordinates = [
        (-113.525540, 53.519250),  # Edmonton coordinates
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