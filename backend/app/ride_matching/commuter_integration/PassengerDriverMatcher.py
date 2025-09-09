import requests
import json
from supabase import create_client, Client
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import random
import time
from dotenv import load_dotenv
import os
from datetime import datetime

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
    
    
    def spatial_prefilter(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float], 
        prefilter_distance_meters: int = 10000,
        time_window_hours: int = 2,
        passenger_departure_time: Optional[str] = None
    ) -> Dict:
        """
        Run spatial pre-filtering to find relevant drivers from database
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            prefilter_distance_meters: Pre-filter distance in meters (default 10km)
            time_window_hours: Time window for departure matching in hours (default 2.0)
            passenger_departure_time: ISO datetime string for departure time (optional)
            
        Returns:
            Dictionary with spatial matches and statistics
        """
        
        try:
            print(f"🔍 Running spatial pre-filter...")
            print(f"   Passenger trip: {passenger_pickup} → {passenger_destination}")
            print(f"   Search radius: {prefilter_distance_meters/1000}km")
            if passenger_departure_time:
                print(f"   Departure time: {passenger_departure_time} (±{time_window_hours}h)")
            
            # Call PostgreSQL spatial pre-filter function (modified version)
            result = self.supabase.rpc(
                'find_nearby_drivers_for_passenger_modified',
                {
                    'passenger_pickup_point': [passenger_pickup[0], passenger_pickup[1]],
                    'passenger_destination_point': [passenger_destination[0], passenger_destination[1]],
                    'prefilter_distance_meters': prefilter_distance_meters,
                    'time_window_hours': time_window_hours,
                    'passenger_departure_time': passenger_departure_time
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
        prefilter_distance_meters: int = 10000,
        direction_tolerance: float = 0.05,
        time_window_hours: float = 2,
        passenger_departure_time: Optional[str] = None
    ) -> Dict:
        """
        Two-step analysis: spatial pre-filter + individual corridor analysis
        Uses each driver's individual max detour preference and queries database directly
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            prefilter_distance_meters: Pre-filter distance in meters (default 10km)
            direction_tolerance: Direction tolerance for corridor analysis
            time_window_hours: Time window for departure matching in hours (default 2.0)
            passenger_departure_time: ISO datetime string for departure time (optional)
            
        Returns:
            Dictionary with complete analysis results
        """
        
        print(f"🔍 Two-Step Analysis:")
        print(f"   Step 1: Spatial pre-filter ({prefilter_distance_meters/1000}km)")
        
        start_time = time.time()
        
        # Step 1: Spatial pre-filtering (now queries database directly)
        prefilter_result = self.spatial_prefilter(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            prefilter_distance_meters=prefilter_distance_meters,
            time_window_hours=time_window_hours,
            passenger_departure_time=passenger_departure_time
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
            detour_key = f'{detour_km}km'
            if detour_key in detour_stats:
                detour_stats[detour_key] += 1
            
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
                'total_drivers': prefilter_stats['total_drivers_checked'],
                'spatially_filtered': len(filtered_drivers),
                'final_viable': len(viable_drivers),
                'spatial_conversion': round(len(filtered_drivers) / prefilter_stats['total_drivers_checked'] * 100, 1) if prefilter_stats['total_drivers_checked'] > 0 else 0,
                'corridor_conversion': round(len(viable_drivers) / len(filtered_drivers) * 100, 1) if filtered_drivers else 0,
                'overall_conversion': round(len(viable_drivers) / prefilter_stats['total_drivers_checked'] * 100, 1) if prefilter_stats['total_drivers_checked'] > 0 else 0
            }
        }

    # Convenience method for easy usage
    def find_matches_for_passenger(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        departure_time: Optional[datetime] = None,
        search_radius_km: float = 10.0,
        time_window_hours: float = 2
    ) -> Dict:
        """
        Simplified interface for finding driver matches
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup location
            passenger_destination: (longitude, latitude) of destination
            departure_time: Preferred departure time (optional)
            search_radius_km: Search radius in kilometers (default 10km)
            time_window_hours: Time flexibility in hours (default ±2 hours)
            
        Returns:
            Dictionary with analysis results and viable driver matches
        """
        
        # Convert departure time to ISO string if provided
        departure_time_str = None
        if departure_time:
            departure_time_str = departure_time.isoformat()
        
        return self.two_step_analysis(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            prefilter_distance_meters=int(search_radius_km * 1000),
            time_window_hours=time_window_hours,
            passenger_departure_time=departure_time_str
        )
    


    def analyze_multiple_drivers_for_passenger_batch(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        filtered_drivers: List[Dict],
        direction_tolerance: float = 0.05
    ) -> Dict:
        """
        Batch analyze multiple drivers for a passenger trip in a single database call
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            filtered_drivers: List of driver matches from spatial pre-filter
            direction_tolerance: Direction tolerance for analysis
            
        Returns:
            Dictionary with batch analysis results
        """
        
        try:
            print(f"🔍 Batch corridor analysis for {len(filtered_drivers)} drivers...")
            
            # Prepare driver data for batch processing
            driver_data = []
            for i, driver_match in enumerate(filtered_drivers):
                driver_info = driver_match['driver_info']
                driver_data.append({
                    'route_geojson': driver_match['route_geojson'],
                    'max_detour_meters': driver_info['max_detour_meters'],
                    'driver_id': driver_match['driver_id'],
                    'driver_info': driver_info
                })
            
            # Single batch database call
            result = self.supabase.rpc(
                'analyze_passenger_against_multiple_drivers',
                {
                    'passenger_pickup_point': [passenger_pickup[0], passenger_pickup[1]],
                    'passenger_destination_point': [passenger_destination[0], passenger_destination[1]],
                    'driver_data': driver_data,
                    'direction_tolerance': direction_tolerance
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                batch_results = result.data[0]['driver_results']
                
                # Parse results and combine with original spatial data
                viable_drivers = []
                detour_stats = {'1km': 0, '2km': 0, '3km': 0, '5km': 0}
                
                for driver_result in batch_results['driver_results']:
                    driver_index = driver_result['driver_index']
                    original_driver = filtered_drivers[driver_index]
                    corridor_analysis = driver_result['corridor_analysis']
                    
                    # Track detour preference distribution
                    detour_km = driver_result['driver_info']['max_detour_km']
                    detour_key = f'{detour_km}km'
                    if detour_key in detour_stats:
                        detour_stats[detour_key] += 1
                    
                    # Combine spatial and corridor results
                    complete_result = {
                        **original_driver,
                        'corridor_analysis': corridor_analysis,
                        'match_eligible': corridor_analysis.get('match_eligible', False),
                        'processing_success': driver_result.get('processing_success', True)
                    }
                    
                    if corridor_analysis.get('match_eligible', False):
                        viable_drivers.append(complete_result)
                
                return {
                    'viable_drivers': viable_drivers,
                    'detour_distribution': detour_stats,
                    'batch_summary': batch_results['analysis_summary'],
                    'all_driver_results': batch_results['driver_results']
                }
            else:
                return {'viable_drivers': [], 'error': 'No batch analysis results'}
                
        except Exception as e:
            return {'viable_drivers': [], 'error': str(e)}


    def two_step_analysis_optimized(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        prefilter_distance_meters: int = 10000,
        direction_tolerance: float = 0.05,
        time_window_hours: float = 2,
        passenger_departure_time: Optional[str] = None
    ) -> Dict:
        """
        Optimized two-step analysis with batch corridor processing
        
        Args:
            passenger_pickup: (longitude, latitude) of pickup
            passenger_destination: (longitude, latitude) of destination
            prefilter_distance_meters: Pre-filter distance in meters (default 10km)
            direction_tolerance: Direction tolerance for corridor analysis
            time_window_hours: Time window for departure matching in hours (default 2.0)
            passenger_departure_time: ISO datetime string for departure time (optional)
            
        Returns:
            Dictionary with complete analysis results
        """
        
        print(f"🔍 Optimized Two-Step Analysis:")
        print(f"   Step 1: Spatial pre-filter ({prefilter_distance_meters/1000}km)")
        
        start_time = time.time()
        
        # Step 1: Spatial pre-filtering
        prefilter_result = self.spatial_prefilter(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            prefilter_distance_meters=prefilter_distance_meters,
            time_window_hours=time_window_hours,
            passenger_departure_time=passenger_departure_time
        )
        
        if not prefilter_result:
            return None
        
        prefilter_time = time.time() - start_time
        filtered_drivers = prefilter_result['spatial_matches']
        prefilter_stats = prefilter_result['prefilter_stats']
        
        print(f"   Step 2: Batch corridor analysis ({len(filtered_drivers)} drivers)")
        
        # Step 2: Batch corridor analysis
        corridor_start = time.time()
        
        batch_result = self.analyze_multiple_drivers_for_passenger_batch(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            filtered_drivers=filtered_drivers,
            direction_tolerance=direction_tolerance
        )
        
        corridor_time = time.time() - corridor_start
        total_time = time.time() - start_time
        
        viable_drivers = batch_result.get('viable_drivers', [])
        detour_stats = batch_result.get('detour_distribution', {})
        batch_summary = batch_result.get('batch_summary', {})
        
        # Sort viable drivers by distance and detour preference
        viable_drivers.sort(key=lambda d: (
            d['min_distance_meters'],  # Closer is better
            -d['driver_info']['max_detour_km']  # More flexible drivers are better
        ))
        
        print(f"✅ Optimized analysis complete in {total_time:.2f}s!")
        print(f"   ⏱️  Pre-filter: {prefilter_time:.2f}s")
        print(f"   ⏱️  Batch corridor analysis: {corridor_time:.2f}s")
        print(f"   🎯 Final viable drivers: {len(viable_drivers)}/{len(filtered_drivers)}")
        print(f"   🚗 Detour preferences: {detour_stats}")
        print(f"   📊 Batch success rate: {batch_summary.get('success_rate', 0)}%")
        
        return {
            'prefilter_stats': prefilter_stats,
            'spatial_matches': filtered_drivers,
            'viable_drivers': viable_drivers,
            'detour_distribution': detour_stats,
            'batch_summary': batch_summary,
            'timing': {
                'prefilter_time': prefilter_time,
                'corridor_time': corridor_time,
                'total_time': total_time,
                'performance_improvement': f"1 DB call vs {len(filtered_drivers)} calls"
            },
            'analysis_stats': {
                'total_drivers': prefilter_stats['total_drivers_checked'],
                'spatially_filtered': len(filtered_drivers),
                'final_viable': len(viable_drivers),
                'spatial_conversion': round(len(filtered_drivers) / prefilter_stats['total_drivers_checked'] * 100, 1) if prefilter_stats['total_drivers_checked'] > 0 else 0,
                'corridor_conversion': round(len(viable_drivers) / len(filtered_drivers) * 100, 1) if filtered_drivers else 0,
                'overall_conversion': round(len(viable_drivers) / prefilter_stats['total_drivers_checked'] * 100, 1) if prefilter_stats['total_drivers_checked'] > 0 else 0
            }
        }

    def insert_ride_matches(
    self,
    rider_id: int,
    viable_drivers: List[Dict],
    price: Optional[float] = None
) -> Dict:
        """
        Insert ride matches into Ride_Match table
        
        Args:
            rider_id: ID of the passenger/rider
            viable_drivers: List of viable driver matches from analysis
            price: Optional price for the ride
            
        Returns:
            Dictionary with insertion results
        """
    
        try:
            match_records = []
            
            # Prepare match records for insertion
            for driver in viable_drivers:
                driver_db_id = driver['driver_info']['database_id']
                
                match_record = {
                    'driver_id': driver_db_id,
                    'rider_id': rider_id,
                    'price': price,
                    'driver_accept': False,  # Default values from table schema
                    'rider_accept': False
                }
                match_records.append(match_record)
            
            # Batch insert all matches
            result = self.supabase.table('Ride_Match').insert(match_records).execute()
            
            if result.data:
                print(f"✅ Inserted {len(result.data)} ride matches")
                return {
                    'success': True,
                    'matches_created': len(result.data),
                    'match_ids': [match['id'] for match in result.data]
                }
            else:
                print("❌ No matches were inserted")
                return {'success': False, 'error': 'No data returned from insert'}
                
        except Exception as e:
            print(f"❌ Failed to insert ride matches: {e}")
            return {'success': False, 'error': str(e)}
    
    def find_and_create_matches(
    self,
    rider_id: int,
    passenger_pickup: Tuple[float, float],
    passenger_destination: Tuple[float, float],
    departure_time: Optional[datetime] = None,
    search_radius_km: float = 10.0,
    time_window_hours: float = 2,
    price: Optional[float] = None,
    use_optimized: bool = True
) -> Dict:
        """
        Complete workflow: find matches and insert into database
        
        Args:
            rider_id: ID of the passenger/rider
            passenger_pickup: (longitude, latitude) of pickup location
            passenger_destination: (longitude, latitude) of destination
            departure_time: Preferred departure time (optional)
            search_radius_km: Search radius in kilometers
            time_window_hours: Time flexibility in hours
            price: Price for the ride (optional)
            use_optimized: Whether to use the optimized batch analysis
            
        Returns:
            Dictionary with complete results including database insertions
        """
    
        print(f"🔍 Finding and creating matches for rider {rider_id}")
        
        # Step 1: Find viable driver matches
        if use_optimized and hasattr(self, 'two_step_analysis_optimized'):
            analysis_results = self.two_step_analysis_optimized(
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                prefilter_distance_meters=int(search_radius_km * 1000),
                time_window_hours=time_window_hours,
                passenger_departure_time=departure_time.isoformat() if departure_time else None
            )
        else:
            analysis_results = self.two_step_analysis(
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                prefilter_distance_meters=int(search_radius_km * 1000),
                time_window_hours=time_window_hours,
                passenger_departure_time=departure_time.isoformat() if departure_time else None
            )
        
        if not analysis_results:
            return {'success': False, 'error': 'No analysis results'}
        
        viable_drivers = analysis_results.get('viable_drivers', [])
        
        if not viable_drivers:
            print(f"❌ No viable drivers found for rider {rider_id}")
            return {
                'success': True,
                'analysis_results': analysis_results,
                'matches_created': 0,
                'message': 'No viable drivers found'
            }
        
        # Step 2: Insert matches into database
        print(f"📝 Creating {len(viable_drivers)} match records...")
        
        insertion_result = self.insert_ride_matches_safe(
            rider_id=rider_id,
            viable_drivers=viable_drivers,
            price=price
        )

        # insertion_result = self.insert_ride_matches(
        #     rider_id=rider_id,
        #     viable_drivers=viable_drivers,
        #     price=price
        # )
        
        # Step 3: Return complete results
        return {
            'success': insertion_result['success'],
            'analysis_results': analysis_results,
            'matches_created': insertion_result.get('matches_created', 0),
            'match_ids': insertion_result.get('match_ids', []),
            'error': insertion_result.get('error'),
            'viable_drivers': viable_drivers
        }

    def check_existing_matches(
    self,
    rider_id: int,
    driver_ids: List[int]
) -> List[int]:
        """
        Check for existing matches to avoid duplicates
        
        Args:
            rider_id: ID of the rider
            driver_ids: List of driver IDs to check
            
        Returns:
            List of driver IDs that don't already have matches with this rider
        """
    
        try:
            # Query existing matches
            result = self.supabase.table('Ride_Match').select('driver_id').eq(
                'rider_id', rider_id
            ).in_('driver_id', driver_ids).execute()
            
            existing_driver_ids = {match['driver_id'] for match in result.data}
            new_driver_ids = [did for did in driver_ids if did not in existing_driver_ids]
            
            if existing_driver_ids:
                print(f"ℹ️ Skipping {len(existing_driver_ids)} existing matches")
            
            return new_driver_ids
            
        except Exception as e:
            print(f"❌ Error checking existing matches: {e}")
            return driver_ids  # Return all if check fails

    def insert_ride_matches_safe(
        self,
        rider_id: int,
        viable_drivers: List[Dict],
        price: Optional[float] = None,
        avoid_duplicates: bool = True
    ) -> Dict:
        """
        Safely insert ride matches with duplicate checking
        
        Args:
            rider_id: ID of the passenger/rider
            viable_drivers: List of viable driver matches
            price: Optional price for the ride
            avoid_duplicates: Whether to check for existing matches
            
        Returns:
            Dictionary with insertion results
        """
        
        try:
            # Extract driver IDs
            driver_ids = [driver['driver_info']['database_id'] for driver in viable_drivers]
            
            # Check for duplicates if requested
            if avoid_duplicates:
                new_driver_ids = self.check_existing_matches(rider_id, driver_ids)
                if not new_driver_ids:
                    return {
                        'success': True,
                        'matches_created': 0,
                        'message': 'All matches already exist'
                    }
                
                # Filter viable_drivers to only include new matches
                new_drivers = [
                    driver for driver in viable_drivers 
                    if driver['driver_info']['database_id'] in new_driver_ids
                ]
            else:
                new_drivers = viable_drivers
            
            # Insert new matches
            return self.insert_ride_matches(rider_id, new_drivers, price)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}