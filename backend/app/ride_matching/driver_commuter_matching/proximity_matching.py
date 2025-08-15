import requests
import json
from supabase import create_client, Client
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from shapely.geometry import shape, Point
from shapely import wkt
from dotenv import load_dotenv
import os
load_dotenv()

class HybridCorridorMatching:
    def __init__(self, supabase_url: str, supabase_key: str, mapbox_token: str):
        """
        Initialize hybrid corridor matching system
        PostGIS for accurate geometry, Shapely for visualization
        
        Args:
            supabase_url: Your Supabase project URL
            supabase_key: Your Supabase anon key
            mapbox_token: Your Mapbox access token
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.mapbox_token = mapbox_token
        self.mapbox_base_url = "https://api.mapbox.com/directions/v5"
    
    def get_route(
        self, 
        start_coords: Tuple[float, float], 
        end_coords: Tuple[float, float]
    ) -> Dict:
        """Get route from Mapbox Directions API"""
        
        coords_str = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
        url = f"{self.mapbox_base_url}/mapbox/driving-traffic/{coords_str}"
        
        params = {
            "access_token": self.mapbox_token,
            "geometries": "geojson",
            "overview": "full"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Mapbox error: {e}")
            return None
    
    def create_corridor_with_postgis(
        self,
        route_geometry: Dict,
        buffer_distance_meters: int
    ) -> Tuple[Dict, Dict]:
        """
        Create buffer corridor using PostGIS (accurate geometry)
        
        Args:
            route_geometry: GeoJSON route geometry from Mapbox
            buffer_distance_meters: Buffer distance in meters
            
        Returns:
            Tuple of (corridor_geojson_dict, corridor_info)
        """
        
        try:
            print(f"🔧 Creating {buffer_distance_meters}m corridor with PostGIS...")
            
            # Call PostgreSQL function for accurate geometry
            result = self.supabase.rpc(
                'create_route_corridor',
                {
                    'route_geojson': route_geometry,
                    'buffer_distance_meters': buffer_distance_meters
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                corridor_data = result.data[0]
                corridor_info = corridor_data['corridor_info']
                
                # Parse the GeoJSON string into a dict
                corridor_geojson = json.loads(corridor_data['corridor_geojson'])
                
                print(f"✅ PostGIS corridor created!")
                print(f"   Buffer: {corridor_info['buffer_distance_km']:.1f}km")
                print(f"   Area: {corridor_info['corridor_area_km2']:.2f}km²")
                
                return corridor_geojson, corridor_info
            else:
                print("❌ No data returned from PostGIS")
                return None, {}
                
        except Exception as e:
            print(f"❌ PostGIS error: {e}")
            return None, {}
    
    def check_points_in_corridor(
        self,
        corridor_geojson: Dict,
        pickup_points: List[Tuple[float, float]],
        destination_points: List[Tuple[float, float]]
    ) -> Dict:
        """
        Check which points fall within the PostGIS-created corridor
        Uses Shapely just for parsing and point-in-polygon checks
        
        Args:
            corridor_geojson: GeoJSON polygon from PostGIS
            pickup_points: List of (longitude, latitude) pickup coordinates
            destination_points: List of (longitude, latitude) destination coordinates
            
        Returns:
            Dictionary with point analysis results
        """
        
        try:
            # Convert PostGIS GeoJSON to Shapely polygon (just for parsing)
            corridor_polygon = shape(corridor_geojson)
            print(f"📊 Checking points against PostGIS corridor...")
            
            pickup_results = []
            destination_results = []
            
            # Check pickup points
            for i, (lng, lat) in enumerate(pickup_points):
                point = Point(lng, lat)
                # Use the accurate PostGIS-created geometry for contains check
                in_corridor = corridor_polygon.contains(point) or corridor_polygon.touches(point)
                
                pickup_results.append({
                    'index': i,
                    'coords': [lng, lat],
                    'in_corridor': in_corridor
                })
            
            # Check destination points
            for i, (lng, lat) in enumerate(destination_points):
                point = Point(lng, lat)
                in_corridor = corridor_polygon.contains(point) or corridor_polygon.touches(point)
                
                destination_results.append({
                    'index': i,
                    'coords': [lng, lat],
                    'in_corridor': in_corridor
                })
            
            # Calculate stats
            pickup_in_count = sum(1 for r in pickup_results if r['in_corridor'])
            dest_in_count = sum(1 for r in destination_results if r['in_corridor'])
            
            return {
                'pickup_results': pickup_results,
                'destination_results': destination_results,
                'stats': {
                    'total_pickup_points': len(pickup_points),
                    'pickup_points_in_corridor': pickup_in_count,
                    'total_destination_points': len(destination_points),
                    'destination_points_in_corridor': dest_in_count
                }
            }
            
        except Exception as e:
            print(f"❌ Point analysis error: {e}")
            return {
                'pickup_results': [],
                'destination_results': [],
                'stats': {
                    'total_pickup_points': len(pickup_points),
                    'pickup_points_in_corridor': 0,
                    'total_destination_points': len(destination_points),
                    'destination_points_in_corridor': 0
                }
            }
    
    def visualize_corridor_analysis(
        self,
        route_geometry: Dict,
        corridor_geojson: Dict,
        analysis_results: Dict,
        corridor_info: Dict,
        pickup_labels: List[str] = None,
        destination_labels: List[str] = None,
        title: str = "Hybrid PostGIS + Shapely Analysis"
    ) -> None:
        """
        Visualize the corridor with pickup/destination points using Plotly
        
        Args:
            route_geometry: Original route geometry from Mapbox
            corridor_geojson: Corridor geometry from PostGIS
            analysis_results: Results from check_points_in_corridor
            corridor_info: Corridor statistics from PostGIS
            pickup_labels: Optional labels for pickup points
            destination_labels: Optional labels for destination points
            title: Plot title
        """
        
        # Extract route coordinates
        route_coords = route_geometry["coordinates"]
        
        # Extract corridor boundary coordinates from PostGIS-created geometry
        corridor_coords = None
        
        if corridor_geojson['type'] == 'Polygon':
            corridor_coords = corridor_geojson['coordinates'][0]  # Exterior ring
            print(f"ℹ️  PostGIS returned Polygon with {len(corridor_coords)} boundary points")
        elif corridor_geojson['type'] == 'MultiPolygon':
            # PostGIS sometimes returns MultiPolygon, use the first polygon
            corridor_coords = corridor_geojson['coordinates'][0][0]  # First polygon, exterior ring
            print(f"ℹ️  PostGIS returned MultiPolygon, using first polygon with {len(corridor_coords)} boundary points")
        else:
            print(f"❌ Unsupported corridor geometry type: {corridor_geojson['type']}")
            print(f"   Geometry: {corridor_geojson}")
            return
        
        if not corridor_coords or len(corridor_coords) < 3:
            print(f"❌ Invalid corridor coordinates: {len(corridor_coords) if corridor_coords else 0} points")
            return
        
        # Create map figure
        fig = go.Figure()
        
        # Add PostGIS-created corridor polygon (connected buffer zone)
        corridor_lons = [coord[0] for coord in corridor_coords]
        corridor_lats = [coord[1] for coord in corridor_coords]
        
        # Method 1: Let Plotly auto-close with fill="toself" (recommended)
        # fig.add_trace(go.Scattermap(
        #     lon=corridor_lons,
        #     lat=corridor_lats,
        #     fill="toself",  # Automatically closes and fills the polygon
        #     fillcolor="rgba(0, 123, 255, 0.15)",  # Light blue fill
        #     line=dict(width=2, color='rgba(0, 123, 255, 0.6)'),
        #     name=f"PostGIS Corridor ({corridor_info['buffer_distance_km']:.1f}km)",
        #     hovertemplate=f"PostGIS Corridor<br>Area: {corridor_info['corridor_area_km2']:.1f}km²<extra></extra>",
        #     showlegend=True
        # ))
        
        # Alternative Method 2: Manually close polygon (like your example)
        # Uncomment these lines if you prefer explicit closing:
        #
        fig.add_trace(go.Scattermap(
            mode="lines",
            lon=corridor_lons + [corridor_lons[0]],  # Close the polygon manually
            lat=corridor_lats + [corridor_lats[0]],
            fill="toself",
            fillcolor="rgba(255, 0, 0, 0.1)",  # Light red fill
            line=dict(width=2, color='rgba(255, 0, 0, 0.4)'),
            name=f"Manual Closed Corridor ({corridor_info['buffer_distance_km']:.1f}km)",
            hovertemplate=f"Buffer Zone ({corridor_info['buffer_distance_km']:.1f}km)<br>Lat: %{{lat}}<br>Lon: %{{lon}}<extra></extra>",
            showlegend=True
        ))
        
        # Add route line
        route_lons = [coord[0] for coord in route_coords]
        route_lats = [coord[1] for coord in route_coords]
        
        fig.add_trace(go.Scattermap(
            lon=route_lons,
            lat=route_lats,
            mode="lines",
            line=dict(width=5, color='darkblue'),
            name="Route",
            hovertemplate="Route<extra></extra>",
            showlegend=True
        ))
        
        # Add start/end points
        fig.add_trace(go.Scattermap(
            lon=[route_coords[0][0]],
            lat=[route_coords[0][1]],
            mode="markers",
            marker=dict(size=10, color='green'),
            name="Start",
            hovertemplate="Start<extra></extra>",
            showlegend=True
        ))
        
        fig.add_trace(go.Scattermap(
            lon=[route_coords[-1][0]],
            lat=[route_coords[-1][1]],
            mode="markers",
            marker=dict(size=10, color='red'),
            name="End",
            hovertemplate="End<extra></extra>",
            showlegend=True
        ))
        
        # Add pickup points (analyzed with PostGIS accuracy)
        pickup_results = analysis_results['pickup_results']
        
        pickup_in_lons, pickup_in_lats, pickup_in_texts = [], [], []
        pickup_out_lons, pickup_out_lats, pickup_out_texts = [], [], []
        
        for result in pickup_results:
            coords = result['coords']
            index = result['index']
            label = pickup_labels[index] if pickup_labels and index < len(pickup_labels) else f"Pickup {index+1}"
            
            if result['in_corridor']:
                pickup_in_lons.append(coords[0])
                pickup_in_lats.append(coords[1])
                pickup_in_texts.append(f"{label}<br>✅ pickup IN PostGIS CORRIDOR")
            else:
                pickup_out_lons.append(coords[0])
                pickup_out_lats.append(coords[1])
                pickup_out_texts.append(f"{label}<br>❌ pickup Outside PostGIS corridor")
        
        # Pickup points IN corridor
        if pickup_in_lons:
            fig.add_trace(go.Scattermap(
                lon=pickup_in_lons,
                lat=pickup_in_lats,
                mode="markers",
                marker=dict(size=14, color='lightcoral', symbol="circle"),
                name="✅ Pickups IN PostGIS Corridor",
                hovertemplate="%{text}<extra></extra>",
                text=pickup_in_texts,
                showlegend=True
            ))
        
        # Pickup points OUTSIDE corridor
        if pickup_out_lons:
            fig.add_trace(go.Scattermap(
                lon=pickup_out_lons,
                lat=pickup_out_lats,
                mode="markers",
                marker=dict(size=14, color='lightcoral', symbol="circle"),
                name="❌ Pickups Outside",
                hovertemplate="%{text}<extra></extra>",
                text=pickup_out_texts,
                showlegend=True
            ))
        
        # Add destination points (analyzed with PostGIS accuracy)
        destination_results = analysis_results['destination_results']
        
        dest_in_lons, dest_in_lats, dest_in_texts = [], [], []
        dest_out_lons, dest_out_lats, dest_out_texts = [], [], []
        
        for result in destination_results:
            coords = result['coords']
            index = result['index']
            label = destination_labels[index] if destination_labels and index < len(destination_labels) else f"Destination {index+1}"
            
            if result['in_corridor']:
                dest_in_lons.append(coords[0])
                dest_in_lats.append(coords[1])
                dest_in_texts.append(f"{label}<br>✅ destination IN PostGIS CORRIDOR")
            else:
                dest_out_lons.append(coords[0])
                dest_out_lats.append(coords[1])
                dest_out_texts.append(f"{label}<br>❌ destination Outside PostGIS corridor")
        
        # Destination points IN corridor
        if dest_in_lons:
            fig.add_trace(go.Scattermap(
                lon=dest_in_lons,
                lat=dest_in_lats,
                mode="markers",
                marker=dict(size=14, color='blue', symbol="square"),
                name="✅ Destinations IN PostGIS Corridor",
                hovertemplate="%{text}<extra></extra>",
                text=dest_in_texts,
                showlegend=True
            ))
        
        # Destination points OUTSIDE corridor
        if dest_out_lons:
            fig.add_trace(go.Scattermap(
                lon=dest_out_lons,
                lat=dest_out_lats,
                mode="markers",
                marker=dict(size=14, color='blue', symbol="square"),
                name="❌ Destinations Outside",
                hovertemplate="%{text}<extra></extra>",
                text=dest_out_texts,
                showlegend=True
            ))
        
        # Calculate center
        center_lat = sum(route_lats) / len(route_lats)
        center_lon = sum(route_lons) / len(route_lons)
        
        # Update layout
        stats = analysis_results['stats']
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            title=f"{title}<br>" +
                  f"PostGIS Accuracy: Pickups {stats['pickup_points_in_corridor']}/{stats['total_pickup_points']}, " +
                  f"Destinations {stats['destination_points_in_corridor']}/{stats['total_destination_points']} in corridor",
            height=700,
            showlegend=True
        )
        
        fig.show()
    
    def analyze_multiple_buffers_hybrid(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        pickup_points: List[Tuple[float, float]],
        destination_points: List[Tuple[float, float]],
        buffer_sizes: List[int] = [1000, 2000, 3000],
        pickup_labels: List[str] = None,
        destination_labels: List[str] = None
    ) -> None:
        """
        Analyze multiple buffer sizes using PostGIS + Shapely hybrid approach
        
        Args:
            start_coords: (longitude, latitude) start coordinates
            end_coords: (longitude, latitude) end coordinates
            pickup_points: List of (longitude, latitude) pickup coordinates
            destination_points: List of (longitude, latitude) destination coordinates
            buffer_sizes: List of buffer distances in meters
            pickup_labels: Optional labels for pickup points
            destination_labels: Optional labels for destination points
        """
        
        print("🔥 Hybrid PostGIS + Shapely Analysis")
        print("=" * 60)
        print("🎯 PostGIS: Accurate geometry calculations")
        print("📊 Shapely: Parsing and visualization")
        
        # Get route from Mapbox
        print(f"\n📍 Getting route...")
        route_response = self.get_route(start_coords, end_coords)
        
        if not route_response or route_response.get("code") != "Ok":
            print("❌ Failed to get route")
            return
        
        route = route_response["routes"][0]
        route_geometry = route["geometry"]
        
        print(f"✅ Route: {route['distance']/1000:.1f}km, {route['duration']/60:.1f}min")
        print(f"📊 Analyzing {len(pickup_points)} pickup and {len(destination_points)} destination points")
        
        # Analyze each buffer size
        for buffer_size in buffer_sizes:
            print(f"\n🛣️  Analyzing {buffer_size}m buffer (PostGIS + Shapely)...")
            
            # Create accurate corridor with PostGIS
            corridor_geojson, corridor_info = self.create_corridor_with_postgis(
                route_geometry, buffer_size
            )
            
            if corridor_geojson is None:
                print(f"❌ Failed to create {buffer_size}m buffer with PostGIS")
                continue
            
            # Use Shapely to check points against PostGIS-created geometry
            analysis_results = self.check_points_in_corridor(
                corridor_geojson, pickup_points, destination_points
            )
            
            stats = analysis_results['stats']
            print(f"   Pickup points in PostGIS corridor: {stats['pickup_points_in_corridor']}/{stats['total_pickup_points']}")
            print(f"   Destination points in PostGIS corridor: {stats['destination_points_in_corridor']}/{stats['total_destination_points']}")
            
            # Visualize with Plotly
            self.visualize_corridor_analysis(
                route_geometry=route_geometry,
                corridor_geojson=corridor_geojson,
                analysis_results=analysis_results,
                corridor_info=corridor_info,
                pickup_labels=pickup_labels,
                destination_labels=destination_labels,
                title=f"Hybrid Analysis - {buffer_size}m PostGIS Buffer"
            )


# ===== EXAMPLE USAGE =====

def main():
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL") # Replace with your URL
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # Replace with your key
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    # Initialize hybrid system
    matcher = HybridCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    # Driver route: Edmonton coordinates (fixed syntax)
    start_coords = (-113.525540, 53.519250)  # Edmonton start
    end_coords = (-113.606566, 53.430753)    # Edmonton end
    
    # Sample pickup points around Edmonton area (longitude, latitude)
    pickup_points = [
        (-113.525540, 53.519250),  # Start point (should be IN for all buffers)
        (-113.4938, 53.5461),     # Downtown Edmonton
        (-113.5170, 53.5186),     # Whyte Avenue
        (-113.5064, 53.5693),     # NAIT
        (-113.4762, 53.5717),     # Kingsway Mall
        (-113.5700, 53.4800),     # Point along the route
        (-113.3000, 53.6000),     # Far northeast (should be OUT)
        (-113.7000, 53.3500),     # Far southwest (should be OUT)
        (-113.5517, 53.43565),
    ]
    
    # Sample destination points
    destination_points = [
        (-113.606566, 53.430753),  # End point (should be IN for all buffers)
        (-113.5160, 53.4685),      # Southgate Centre
        (-113.3947, 53.4556),      # Millwoods
        (-113.4174, 53.5521),      # Capilano Mall
        (-113.4904, 53.5966),      # Northgate Centre
        (-113.5900, 53.4500),      # Point near the route
        (-113.2000, 53.6500),      # Far northeast (should be OUT)
        (-113.8000, 53.3000),      # Far southwest (should be OUT)
    ]
    
    # Labels for the points
    pickup_labels = [
        "Start Point",
        "Downtown Edmonton", 
        "Whyte Avenue",
        "NAIT",
        "Kingsway Mall",
        "Near Route Point",
        "Far Northeast",
        "Far Southwest"
    ]
    
    destination_labels = [
        "End Point",
        "Southgate Centre",
        "Millwoods", 
        "Capilano Mall",
        "Northgate Centre",
        "Near Route Point",
        "Far Northeast",
        "Far Southwest"
    ]
    
    # Analyze multiple buffer sizes with hybrid approach
    matcher.analyze_multiple_buffers_hybrid(
        start_coords=start_coords,
        end_coords=end_coords,
        pickup_points=pickup_points,
        destination_points=destination_points,
        buffer_sizes=[1000, 2000, 3000],  # 1km, 2km, 3km
        pickup_labels=pickup_labels,
        destination_labels=destination_labels
    )


if __name__ == "__main__":
    main()