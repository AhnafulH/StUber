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
    
    def get_route_geometry(
        self,
        ride_id: int
    ) -> Optional[Dict]:
        """Get the route geometry that is stored in the DB"""
        result = self.supabase.table('Ride_Offer').select('route_geometry').eq('id', ride_id).execute()
        if result.data:
            return result.data[0]['route_geometry']
        else:
            print(f"No coordinates found for ride {ride_id}")
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
        


    def find_matching_passengers_from_db(
        self,
        route_geometry: Dict,
        buffer_distance_meters: int = 2000,
        direction_tolerance: float = 0.05
    ) -> Dict:
        """
        Find matching passengers from Ride_Offer table using direction-aware corridor analysis
        
        Args:
            route_geometry: GeoJSON route geometry from Mapbox
            buffer_distance_meters: Corridor buffer distance in meters
            direction_tolerance: Minimum progress difference for direction alignment
            
        Returns:
            Dictionary with passenger details and match analysis
        """
        
        try:
            print("Querying passengers from database...")
            
            # Query all ride offers from database
            result = self.supabase.table('Ride_Request').select('*').execute()
            
            if not result.data:
                print("No passengers found in database")
                return None
                
            passengers = result.data
            print(f"Found {len(passengers)} passengers in database")
            
            # Extract coordinates and labels for analysis
            pickup_points = []
            destination_points = []
            point_labels = []
            
            for passenger in passengers:
                # Assuming your table has these columns - adjust column names as needed
                pickup_lng = passenger['starting_longitude']  # or whatever your column is named
                pickup_lat = passenger['starting_latitude']
                dropoff_lng = passenger['destination_longitude'] 
                dropoff_lat = passenger['destination_latitude']
                
                pickup_points.append((pickup_lng, pickup_lat))
                destination_points.append((dropoff_lng, dropoff_lat))
                
                # Create descriptive label
                passenger_id = passenger.get('id', 'Unknown')
                point_labels.append(f"Passenger {passenger_id}")
            
            print(f"Analyzing {len(pickup_points)} passenger trips...")
            
            # Call your existing corridor analysis method
            analysis_result = self.analyze_corridor_with_direction(
                route_geometry=route_geometry,
                pickup_points=pickup_points,
                destination_points=destination_points,
                point_labels=point_labels,
                buffer_distance_meters=buffer_distance_meters,
                direction_tolerance=direction_tolerance
            )
            
            if not analysis_result:
                print("Corridor analysis failed")
                return None
                
            # Enhance results with passenger details
            enhanced_results = self._merge_passenger_details(
                analysis_result, 
                passengers
            )
            
            return enhanced_results
            
        except Exception as e:
            print(f"Database integration error: {e}")
            return None

    def _merge_passenger_details(self, analysis_result: Dict, passengers: List[Dict]) -> Dict:
        """
        Merge spatial analysis results with passenger database records
        
        Args:
            analysis_result: Result from analyze_corridor_with_direction
            passengers: Original passenger records from database
            
        Returns:
            Enhanced results with passenger details
        """
        
        point_analysis = analysis_result['point_analysis']
        
        # Add passenger details to each point analysis
        for i, point in enumerate(point_analysis):
            if i < len(passengers):
                passenger = passengers[i]
                point['passenger_details'] = {
                    'id': passenger.get('id'),
                    'user_id': passenger.get('user_id'),
                    'pickup_address': passenger.get('pickup_address'),
                    'dropoff_address': passenger.get('dropoff_address'),
                    'request_time': passenger.get('created_at'),
                    'phone': passenger.get('phone_number'),
                    'notes': passenger.get('notes')
                    # Add any other fields from your table
                }
        
        # Separate eligible matches with full passenger info
        eligible_matches = []
        for i, point in enumerate(point_analysis):
            if point['match_eligible']:
                eligible_matches.append({
                    'passenger_id': passengers[i].get('id'),
                    'match_analysis': point,
                    'passenger_info': point.get('passenger_details', {}),
                    'pickup_coords': point['pickup_coords'],
                    'dropoff_coords': point['destination_coords']
                })
        
        # Add summary of eligible matches
        analysis_result['eligible_passengers'] = eligible_matches
        analysis_result['eligible_count'] = len(eligible_matches)
        
        print(f"Found {len(eligible_matches)} eligible passenger matches!")
        
        return analysis_result
        