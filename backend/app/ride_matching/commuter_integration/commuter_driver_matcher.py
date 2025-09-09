import requests
import json
from supabase import create_client, Client
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import random
import time
from dotenv import load_dotenv
import os

load_dotenv()


class PassengerDriverMatcher:
    def __init__(self, supabase_url: str, supabase_key: str, mapbox_token: str):
        """
        Initialize passenger-driver spatial pre-filter matching system
        
        Two-Step Approach:
        1. Spatial pre-filter (10km) - "Are we in the same area?"
        2. Individual corridor analysis - "Does this fit the driver's detour preference?"
        
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
    
    
    def spatial_prefilter(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float], 
        driver_routes: List[Dict],
        prefilter_distance_meters: int = 10000
    ) -> Dict:
        """
        Run spatial pre-filtering to find relevant drivers
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            driver_routes: List of driver route dictionaries
            prefilter_distance_meters: Pre-filter distance in meters (default 10km)
            
        Returns:
            Dictionary with spatial matches and statistics
        """
        
        try:
            print(f"🔍 Running spatial pre-filter...")
            print(f"   Passenger trip: {passenger_pickup} → {passenger_destination}")
            print(f"   Checking {len(driver_routes)} drivers within {prefilter_distance_meters/1000}km")
            
            # Call PostgreSQL spatial pre-filter function
            result = self.supabase.rpc(
                'find_nearby_drivers_for_passenger_modified',
                {
                    'passenger_pickup_point': [passenger_pickup[0], passenger_pickup[1]],
                    'passenger_destination_point': [passenger_destination[0], passenger_destination[1]],
                    'driver_routes': driver_routes,
                    'prefilter_distance_meters': prefilter_distance_meters
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                filter_data = result.data[0]
                stats = filter_data['prefilter_stats']
                
                print(f"✅ Spatial pre-filter complete!")
                print(f"   📊 Results: {stats['filtered_drivers']}/{stats['total_drivers_checked']} drivers match")
                print(f"   🎯 Reduction: {stats['reduction_ratio']}% filtered out")
                print(f"   📍 Pickup matches: {stats['pickup_matches']}")
                print(f"   🏁 Destination matches: {stats['destination_matches']}")
                print(f"   🎯 Both intersect: {stats['both_intersects_count']}")
                
                return filter_data
            else:
                print("❌ No results from spatial pre-filter")
                return None
                
        except Exception as e:
            print(f"❌ Spatial pre-filter error: {e}")
            return None
    
    def analyze_single_driver_for_passenger(
        self,
        driver_route_geojson: Dict,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        driver_max_detour_meters: int,  # Driver's chosen max detour
        direction_tolerance: float = 0.05
    ) -> Dict:
        """
        Analyze if a single driver route works for a passenger trip
        
        Args:
            driver_route_geojson: Driver's route geometry
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            driver_max_detour_meters: Driver's maximum acceptable detour distance
            direction_tolerance: Direction tolerance for analysis
            
        Returns:
            Dictionary with corridor analysis results
        """
        
        try:
            # Call the original corridor analysis function with driver's detour preference
            result = self.supabase.rpc(
                'find_rides_in_corridor_with_direction',
                {
                    'route_geojson': driver_route_geojson,
                    'buffer_distance_meters': driver_max_detour_meters,  # Use driver's preference
                    'pickup_points': [[passenger_pickup[0], passenger_pickup[1]]],
                    'destination_points': [[passenger_destination[0], passenger_destination[1]]],
                    'point_labels': ['Passenger Trip'],
                    'direction_tolerance': direction_tolerance
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                analysis_data = result.data[0]
                point_analysis = analysis_data['point_analysis'][0]  # First (and only) trip
                direction_analysis = analysis_data['direction_analysis'][0]
                
                return {
                    'match_eligible': point_analysis.get('match_eligible', False),
                    'both_in_corridor': point_analysis.get('both_in_corridor', False),
                    'pickup_in_corridor': point_analysis.get('pickup_in_corridor', False),
                    'destination_in_corridor': point_analysis.get('destination_in_corridor', False),
                    'pickup_progress': direction_analysis.get('pickup_progress'),
                    'dropoff_progress': direction_analysis.get('dropoff_progress'),
                    'progress_difference': direction_analysis.get('progress_difference'),
                    'direction_aligned': direction_analysis.get('direction_aligned', False),
                    'driver_max_detour_km': driver_max_detour_meters / 1000.0,
                    'corridor_stats': analysis_data['stats']
                }
            else:
                return {'match_eligible': False, 'error': 'No analysis results'}
                
        except Exception as e:
            return {'match_eligible': False, 'error': str(e)}

    def two_step_analysis(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        driver_routes: List[Dict],
        prefilter_distance_meters: int = 10000,
        direction_tolerance: float = 0.05
    ) -> Dict:
        """
        Two-step analysis: spatial pre-filter + individual corridor analysis
        Uses each driver's individual max detour preference
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            driver_routes: List of driver route dictionaries (with max_detour_meters)
            prefilter_distance_meters: Pre-filter distance in meters (default 10km)
            direction_tolerance: Direction tolerance for corridor analysis
            
        Returns:
            Dictionary with complete analysis results
        """
        
        print(f"🔍 Two-Step Analysis:")
        print(f"   Step 1: Spatial pre-filter ({prefilter_distance_meters/1000}km)")
        
        start_time = time.time()
        
        # Step 1: Spatial pre-filtering
        prefilter_result = self.spatial_prefilter(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            driver_routes=driver_routes,
            prefilter_distance_meters=prefilter_distance_meters
        )
        
        if not prefilter_result:
            return None
        
        prefilter_time = time.time() - start_time
        filtered_drivers = prefilter_result['spatial_matches']
        prefilter_stats = prefilter_result['prefilter_stats']
        
        print(f"   Step 2: Corridor analysis using each driver's detour preference")
        
        # Step 2: Individual corridor analysis for each filtered driver
        corridor_start = time.time()
        viable_drivers = []
        detour_stats = {'1km': 0, '2km': 0, '3km': 0, '5km': 0}
        
        for i, driver_match in enumerate(filtered_drivers):
            # Get driver's individual detour preference
            driver_max_detour = driver_match['driver_info']['max_detour_meters']
            detour_km = driver_match['driver_info']['max_detour_km']
            
            corridor_result = self.analyze_single_driver_for_passenger(
                driver_route_geojson=driver_match['route_geojson'],
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                driver_max_detour_meters=driver_max_detour,  # Use driver's preference
                direction_tolerance=direction_tolerance
            )
            
            # Track detour preference distribution
            detour_stats[f'{detour_km}km'] += 1
            
            # Combine spatial and corridor results
            complete_result = {
                **driver_match,
                'corridor_analysis': corridor_result,
                'match_eligible': corridor_result.get('match_eligible', False)
            }
            
            if corridor_result.get('match_eligible', False):
                viable_drivers.append(complete_result)
        
        corridor_time = time.time() - corridor_start
        total_time = time.time() - start_time
        
        # Sort viable drivers by distance and detour preference
        viable_drivers.sort(key=lambda d: (
            d['min_distance_meters'],  # Closer is better
            -d['driver_info']['max_detour_km']  # More flexible drivers are better
        ))
        
        print(f"✅ Two-step analysis complete in {total_time:.2f}s!")
        print(f"   ⏱️  Pre-filter: {prefilter_time:.2f}s")
        print(f"   ⏱️  Corridor analysis: {corridor_time:.2f}s")
        print(f"   🎯 Final viable drivers: {len(viable_drivers)}/{len(filtered_drivers)}")
        print(f"   🚗 Detour preferences: {detour_stats}")
        
        return {
            'prefilter_stats': prefilter_stats,
            'spatial_matches': filtered_drivers,
            'viable_drivers': viable_drivers,
            'detour_distribution': detour_stats,
            'timing': {
                'prefilter_time': prefilter_time,
                'corridor_time': corridor_time,
                'total_time': total_time
            },
            'analysis_stats': {
                'total_drivers': len(driver_routes),
                'spatially_filtered': len(filtered_drivers),
                'final_viable': len(viable_drivers),
                'spatial_conversion': round(len(filtered_drivers) / len(driver_routes) * 100, 1),
                'corridor_conversion': round(len(viable_drivers) / len(filtered_drivers) * 100, 1) if filtered_drivers else 0,
                'overall_conversion': round(len(viable_drivers) / len(driver_routes) * 100, 1)
            }
        }
    
    