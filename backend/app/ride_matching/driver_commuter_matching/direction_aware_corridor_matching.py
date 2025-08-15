import requests
import json
from supabase import create_client, Client
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from shapely.geometry import shape, Point
from dotenv import load_dotenv
import os

load_dotenv()


class DirectionAwareCorridorMatching:
    def __init__(self, supabase_url: str, supabase_key: str, mapbox_token: str):
        """
        Initialize direction-aware corridor matching system
        PostGIS for accurate geometry + direction detection, Shapely for visualization
        
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
    
    def analyze_corridor_with_direction(
        self,
        route_geometry: Dict,
        pickup_points: List[Tuple[float, float]],
        destination_points: List[Tuple[float, float]],
        point_labels: List[str] = None,
        buffer_distance_meters: int = 2000,
        direction_tolerance: float = 0.05
    ) -> Dict:
        """
        Analyze corridor with direction awareness using PostGIS
        
        Args:
            route_geometry: GeoJSON route geometry from Mapbox
            pickup_points: List of (longitude, latitude) pickup coordinates
            destination_points: List of (longitude, latitude) destination coordinates
            point_labels: Optional labels for each pickup/destination pair
            buffer_distance_meters: Corridor buffer distance in meters
            direction_tolerance: Minimum progress difference for direction alignment (0.05 = 5%)
            
        Returns:
            Dictionary with corridor geometry, point analysis, and direction analysis
        """
        
        try:
            print(f"🔍 Analyzing {len(pickup_points)} pickup/destination pairs...")
            print(f"   Buffer distance: {buffer_distance_meters}m")
            print(f"   Direction tolerance: {direction_tolerance*100:.1f}%")
            
            # Convert coordinates to the format PostGIS expects
            pickup_points_json = [[coord[0], coord[1]] for coord in pickup_points]
            dest_points_json = [[coord[0], coord[1]] for coord in destination_points]
            labels_json = point_labels or [f"Trip {i+1}" for i in range(len(pickup_points))]
            
            # Call the enhanced PostgreSQL function
            result = self.supabase.rpc(
                'find_rides_in_corridor_with_direction',
                {
                    'route_geojson': route_geometry,
                    'buffer_distance_meters': buffer_distance_meters,
                    'pickup_points': pickup_points_json,
                    'destination_points': dest_points_json,
                    'point_labels': labels_json,
                    'direction_tolerance': direction_tolerance
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                analysis_data = result.data[0]
                stats = analysis_data['stats']
                
                print(f"✅ Direction-aware analysis complete!")
                print(f"   Points both in corridor: {stats['points_both_in_corridor']}/{stats['total_points']}")
                print(f"   Direction-aligned points: {stats['direction_aligned_points']}/{stats['points_both_in_corridor']}")
                print(f"   🎯 Final eligible matches: {stats['final_matches']}/{stats['total_points']}")
                print(f"   Corridor area: {stats['corridor_area_km2']:.2f} km²")
                
                return analysis_data
            else:
                print("❌ No results from direction-aware analysis")
                return None
                
        except Exception as e:
            print(f"❌ Direction-aware analysis error: {e}")
            return None
    
    def visualize_direction_aware_analysis(
        self,
        route_geometry: Dict,
        analysis_data: Dict,
        title: str = "Direction-Aware Corridor Analysis"
    ) -> None:
        """
        Visualize the corridor with direction-aware point analysis
        
        Args:
            route_geometry: Original route geometry from Mapbox
            analysis_data: Result from analyze_corridor_with_direction
            title: Plot title
        """
        
        if not analysis_data:
            print("❌ No analysis data to visualize")
            return
        
        # Parse data
        corridor_geojson = json.loads(analysis_data['corridor_geojson'])
        point_analysis = analysis_data['point_analysis']
        direction_analysis = analysis_data['direction_analysis']
        stats = analysis_data['stats']
        
        # Extract route coordinates
        route_coords = route_geometry["coordinates"]
        
        # Extract corridor boundary coordinates from PostGIS-created geometry
        corridor_coords = None
        
        if corridor_geojson['type'] == 'Polygon':
            corridor_coords = corridor_geojson['coordinates'][0]  # Exterior ring
        elif corridor_geojson['type'] == 'MultiPolygon':
            corridor_coords = corridor_geojson['coordinates'][0][0]  # First polygon, exterior ring
        else:
            print(f"❌ Unsupported corridor geometry type: {corridor_geojson['type']}")
            return
        
        print(f"📊 Creating direction-aware visualization...")
        
        # Create map figure
        fig = go.Figure()
        
        # Add PostGIS-created corridor polygon
        corridor_lons = [coord[0] for coord in corridor_coords]
        corridor_lats = [coord[1] for coord in corridor_coords]
        
        fig.add_trace(go.Scattermapbox(
            lon=corridor_lons,
            lat=corridor_lats,
            fill="toself",
            fillcolor="rgba(0, 123, 255, 0.15)",  # Light blue fill
            line=dict(width=2, color='rgba(0, 123, 255, 0.6)'),
            name=f"Corridor ({stats['buffer_distance_km']:.1f}km)",
            hovertemplate=f"Corridor<br>Area: {stats['corridor_area_km2']:.1f}km²<extra></extra>",
            showlegend=True
        ))
        
        # Add route line with direction arrow
        route_lons = [coord[0] for coord in route_coords]
        route_lats = [coord[1] for coord in route_coords]
        
        fig.add_trace(go.Scattermapbox(
            lon=route_lons,
            lat=route_lats,
            mode="lines",
            line=dict(width=6, color='darkblue'),
            name="Driver Route →",
            hovertemplate="Driver Route<extra></extra>",
            showlegend=True
        ))
        
        # Add start/end points with direction indicators
        fig.add_trace(go.Scattermapbox(
            lon=[route_coords[0][0]],
            lat=[route_coords[0][1]],
            mode="markers+text",
            marker=dict(size=18, color='green'),
            text=["START"],
            textposition="bottom center",
            name="Start",
            hovertemplate="Route Start<extra></extra>",
            showlegend=True
        ))
        
        fig.add_trace(go.Scattermapbox(
            lon=[route_coords[-1][0]],
            lat=[route_coords[-1][1]],
            mode="markers+text",
            marker=dict(size=18, color='red'),
            text=["END"],
            textposition="bottom center",
            name="End",
            hovertemplate="Route End<extra></extra>",
            showlegend=True
        ))
        
        # Categorize points for visualization
        eligible_matches = {'pickup_lons': [], 'pickup_lats': [], 'dest_lons': [], 'dest_lats': [], 'texts': [], 'labels': []}
        wrong_direction = {'pickup_lons': [], 'pickup_lats': [], 'dest_lons': [], 'dest_lats': [], 'texts': [], 'labels': []}
        not_in_corridor = {'pickup_lons': [], 'pickup_lats': [], 'dest_lons': [], 'dest_lats': [], 'texts': [], 'labels': []}
        
        for i, point in enumerate(point_analysis):
            pickup_coords = point['pickup_coords']
            dest_coords = point['destination_coords']
            label = point['label']
            direction_info = direction_analysis[i]
            
            pickup_text = f"🔶 PICKUP: {label}"
            dest_text = f"🔷 DROPOFF: {label}"
            
            if point['match_eligible']:
                # ✅ Eligible match: both in corridor AND correct direction
                eligible_matches['pickup_lons'].append(pickup_coords[0])
                eligible_matches['pickup_lats'].append(pickup_coords[1])
                eligible_matches['dest_lons'].append(dest_coords[0])
                eligible_matches['dest_lats'].append(dest_coords[1])
                eligible_matches['texts'].extend([
                    f"{pickup_text}<br>✅ ELIGIBLE MATCH<br>Progress: {direction_info.get('pickup_progress', 'N/A')}",
                    f"{dest_text}<br>✅ ELIGIBLE MATCH<br>Progress: {direction_info.get('dropoff_progress', 'N/A')}"
                ])
                eligible_matches['labels'].append(label)
                
            elif point['both_in_corridor'] and not direction_info.get('direction_aligned', False):
                # ❌ Wrong direction: both in corridor but going opposite way
                wrong_direction['pickup_lons'].append(pickup_coords[0])
                wrong_direction['pickup_lats'].append(pickup_coords[1])
                wrong_direction['dest_lons'].append(dest_coords[0])
                wrong_direction['dest_lats'].append(dest_coords[1])
                wrong_direction['texts'].extend([
                    f"{pickup_text}<br>❌ WRONG DIRECTION<br>Progress: {direction_info.get('pickup_progress', 'N/A')}",
                    f"{dest_text}<br>❌ WRONG DIRECTION<br>Progress: {direction_info.get('dropoff_progress', 'N/A')}"
                ])
                wrong_direction['labels'].append(label)
                
            else:
                # ⚫ Not in corridor: at least one point outside corridor
                not_in_corridor['pickup_lons'].append(pickup_coords[0])
                not_in_corridor['pickup_lats'].append(pickup_coords[1])
                not_in_corridor['dest_lons'].append(dest_coords[0])
                not_in_corridor['dest_lats'].append(dest_coords[1])
                not_in_corridor['texts'].extend([
                    f"{pickup_text}<br>⚫ NOT IN CORRIDOR",
                    f"{dest_text}<br>⚫ NOT IN CORRIDOR"
                ])
                not_in_corridor['labels'].append(label)
        
        # Add eligible matches (green)
        if eligible_matches['pickup_lons']:
            fig.add_trace(go.Scattermapbox(
                lon=eligible_matches['pickup_lons'],
                lat=eligible_matches['pickup_lats'],
                mode="markers",
                marker=dict(size=14, color='green', symbol="circle"),
                name="✅ Eligible Pickups",
                hovertemplate="%{text}<extra></extra>",
                text=eligible_matches['texts'][::2],  # Every other text (pickups only)
                showlegend=True
            ))
            
            fig.add_trace(go.Scattermapbox(
                lon=eligible_matches['dest_lons'],
                lat=eligible_matches['dest_lats'],
                mode="markers",
                marker=dict(size=14, color='darkgreen', symbol="square"),
                name="✅ Eligible Dropoffs",
                hovertemplate="%{text}<extra></extra>",
                text=eligible_matches['texts'][1::2],  # Every other text (dropoffs only)
                showlegend=True
            ))
        
        # Add wrong direction points (orange)
        if wrong_direction['pickup_lons']:
            fig.add_trace(go.Scattermapbox(
                lon=wrong_direction['pickup_lons'],
                lat=wrong_direction['pickup_lats'],
                mode="markers",
                marker=dict(size=12, color='orange', symbol="circle"),
                name="❌ Wrong Direction Pickups",
                hovertemplate="%{text}<extra></extra>",
                text=wrong_direction['texts'][::2],
                showlegend=True
            ))
            
            fig.add_trace(go.Scattermapbox(
                lon=wrong_direction['dest_lons'],
                lat=wrong_direction['dest_lats'],
                mode="markers",
                marker=dict(size=12, color='darkorange', symbol="square"),
                name="❌ Wrong Direction Dropoffs",
                hovertemplate="%{text}<extra></extra>",
                text=wrong_direction['texts'][1::2],
                showlegend=True
            ))
        
        # Add not in corridor points (gray)
        if not_in_corridor['pickup_lons']:
            fig.add_trace(go.Scattermapbox(
                lon=not_in_corridor['pickup_lons'],
                lat=not_in_corridor['pickup_lats'],
                mode="markers",
                marker=dict(size=10, color='gray', symbol="circle"),
                name="⚫ Outside Corridor Pickups",
                hovertemplate="%{text}<extra></extra>",
                text=not_in_corridor['texts'][::2],
                showlegend=True
            ))
            
            fig.add_trace(go.Scattermapbox(
                lon=not_in_corridor['dest_lons'],
                lat=not_in_corridor['dest_lats'],
                mode="markers",
                marker=dict(size=10, color='lightgray', symbol="square"),
                name="⚫ Outside Corridor Dropoffs",
                hovertemplate="%{text}<extra></extra>",
                text=not_in_corridor['texts'][1::2],
                showlegend=True
            ))
        
        # Calculate center
        center_lat = sum(route_lats) / len(route_lats)
        center_lon = sum(route_lons) / len(route_lons)
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            title=f"{title}<br>" +
                  f"🎯 Eligible: {stats['final_matches']}, " +
                  f"❌ Wrong Direction: {stats['points_both_in_corridor'] - stats['direction_aligned_points']}, " +
                  f"⚫ Outside: {stats['total_points'] - stats['points_both_in_corridor']}",
            height=800,
            showlegend=True
        )
        
        fig.show()
        
        # Print detailed analysis
        print(f"\n📋 Detailed Direction Analysis:")
        for i, point in enumerate(point_analysis):
            direction_info = direction_analysis[i]
            status = "✅ ELIGIBLE" if point['match_eligible'] else (
                "❌ WRONG DIRECTION" if point['both_in_corridor'] else "⚫ NOT IN CORRIDOR"
            )
            
            print(f"   {point['label']}: {status}")
            if direction_info.get('pickup_progress') is not None:
                print(f"      Progress: {direction_info['pickup_progress']:.3f} → {direction_info['dropoff_progress']:.3f} " +
                      f"(diff: {direction_info['progress_difference']:.3f})")


# # Example usage
# if __name__ == "__main__":
#     # Basic initialization example
#     SUPABASE_URL = os.environ.get("SUPABASE_URL")
#     SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
#     MAPBOX_TOKEN = "your-mapbox-token"
    
#     matcher = DirectionAwareCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
#     print("✅ DirectionAwareCorridorMatching initialized successfully!")
#     print("📝 For full testing examples, run test_direction_aware_corridor_matching.py")