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
    
    def generate_realistic_drivers(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        num_drivers: int = 50,
        radius_km: float = 25.0
    ) -> List[Dict]:
        """
        Generate more realistic driver routes that have higher chance of matching
        
        Args:
            passenger_pickup: Passenger pickup coordinates 
            passenger_destination: Passenger destination coordinates
            num_drivers: Number of driver routes to generate
            radius_km: Radius within which to generate routes
            
        Returns:
            List of driver route dictionaries with realistic routes
        """
        
        print(f"🚗 Generating {num_drivers} realistic driver routes...")
        
        drivers = []
        successful_routes = 0
        
        # Convert radius to approximate degree offset
        degree_offset = radius_km / 111.0
        
        for i in range(num_drivers * 3):  # Try more to account for failures
            if successful_routes >= num_drivers:
                break
            
            # Generate routes with higher probability of alignment
            route_type = random.choice(['parallel', 'intersecting', 'random'])
            
            if route_type == 'parallel':
                # Generate routes roughly parallel to passenger trip
                direction_vector = (
                    passenger_destination[0] - passenger_pickup[0],
                    passenger_destination[1] - passenger_pickup[1]
                )
                
                # Start near passenger area with some randomness
                start_offset = random.uniform(-degree_offset/2, degree_offset/2)
                start_lon = passenger_pickup[0] + start_offset
                start_lat = passenger_pickup[1] + start_offset
                
                # End in similar direction as passenger
                end_lon = start_lon + direction_vector[0] * random.uniform(0.7, 1.3)
                end_lat = start_lat + direction_vector[1] * random.uniform(0.7, 1.3)
                
            elif route_type == 'intersecting':
                # Generate routes that intersect passenger route
                mid_lon = (passenger_pickup[0] + passenger_destination[0]) / 2
                mid_lat = (passenger_pickup[1] + passenger_destination[1]) / 2
                
                # Start and end around the midpoint of passenger trip
                start_lon = mid_lon + random.uniform(-degree_offset/3, degree_offset/3)
                start_lat = mid_lat + random.uniform(-degree_offset/3, degree_offset/3)
                end_lon = mid_lon + random.uniform(-degree_offset/3, degree_offset/3)
                end_lat = mid_lat + random.uniform(-degree_offset/3, degree_offset/3)
                
            else:
                # Random routes (some should still be far away)
                center_lon = (passenger_pickup[0] + passenger_destination[0]) / 2
                center_lat = (passenger_pickup[1] + passenger_destination[1]) / 2
                
                start_lon = center_lon + random.uniform(-degree_offset, degree_offset)
                start_lat = center_lat + random.uniform(-degree_offset, degree_offset)
                end_lon = center_lon + random.uniform(-degree_offset, degree_offset)
                end_lat = center_lat + random.uniform(-degree_offset, degree_offset)
            
            start_coords = (start_lon, start_lat)
            end_coords = (end_lon, end_lat)
            
            # Get route from Mapbox
            route_response = self.get_route(start_coords, end_coords)
            
            if route_response and route_response.get("code") == "Ok":
                route = route_response["routes"][0]
                
                driver_data = {
                    "id": f"driver_{successful_routes + 1:03d}",
                    "label": f"Driver {successful_routes + 1} ({route_type})",
                    "route_geojson": route["geometry"],
                    "driver_info": {
                        "start_coords": start_coords,
                        "end_coords": end_coords,
                        "distance_km": round(route["distance"] / 1000, 1),
                        "duration_min": round(route["duration"] / 60, 1),
                        "departure_time": f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}",
                        "available_seats": random.randint(1, 3),
                        "max_detour_km": random.choice([1, 2, 3, 5]),
                        "max_detour_meters": None,
                        "route_type": route_type
                    }
                }
                
                # Set detour in meters
                driver_data["driver_info"]["max_detour_meters"] = driver_data["driver_info"]["max_detour_km"] * 1000
                
                drivers.append(driver_data)
                successful_routes += 1
                
                if successful_routes % 10 == 0:
                    print(f"   Generated {successful_routes}/{num_drivers} routes...")
            
            # Add small delay to respect API limits
            time.sleep(0.1)
        
        # Show distribution of route types
        route_types = {}
        for driver in drivers:
            route_type = driver['driver_info']['route_type']
            route_types[route_type] = route_types.get(route_type, 0) + 1
        
        print(f"✅ Successfully generated {len(drivers)} realistic driver routes")
        print(f"   📊 Route types: {route_types}")
        return drivers

    def generate_sample_drivers(
        self,
        center_coords: Tuple[float, float] = (-113.5, 53.5),
        num_drivers: int = 50,
        radius_km: float = 25.0
    ) -> List[Dict]:
        """
        Generate sample driver routes for testing
        
        Args:
            center_coords: Center point for generating routes (longitude, latitude)
            num_drivers: Number of driver routes to generate
            radius_km: Radius within which to generate routes
            
        Returns:
            List of driver route dictionaries
        """
        
        print(f"🚗 Generating {num_drivers} sample driver routes...")
        
        drivers = []
        successful_routes = 0
        
        # Convert radius to approximate degree offset
        degree_offset = radius_km / 111.0  # Rough conversion
        
        for i in range(num_drivers * 2):  # Try more to account for failures
            if successful_routes >= num_drivers:
                break
                
            # Generate random start and end points around center
            start_lon = center_coords[0] + random.uniform(-degree_offset, degree_offset)
            start_lat = center_coords[1] + random.uniform(-degree_offset, degree_offset)
            end_lon = center_coords[0] + random.uniform(-degree_offset, degree_offset)  
            end_lat = center_coords[1] + random.uniform(-degree_offset, degree_offset)
            
            start_coords = (start_lon, start_lat)
            end_coords = (end_lon, end_lat)
            
            # Get route from Mapbox
            route_response = self.get_route(start_coords, end_coords)
            
            if route_response and route_response.get("code") == "Ok":
                route = route_response["routes"][0]
                
                driver_data = {
                    "id": f"driver_{successful_routes + 1:03d}",
                    "label": f"Driver {successful_routes + 1}",
                    "route_geojson": route["geometry"],
                    "driver_info": {
                        "start_coords": start_coords,
                        "end_coords": end_coords,
                        "distance_km": round(route["distance"] / 1000, 1),
                        "duration_min": round(route["duration"] / 60, 1),
                        "departure_time": f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}",
                        "available_seats": random.randint(1, 3),
                        "max_detour_km": random.choice([1, 2, 3, 5]),  # Driver's detour preference
                        "max_detour_meters": None  # Will be set below
                    }
                }
                
                # Set detour in meters
                driver_data["driver_info"]["max_detour_meters"] = driver_data["driver_info"]["max_detour_km"] * 1000
                
                drivers.append(driver_data)
                successful_routes += 1
                
                if successful_routes % 10 == 0:
                    print(f"   Generated {successful_routes}/{num_drivers} routes...")
            
            # Add small delay to respect API limits
            time.sleep(0.1)
        
        print(f"✅ Successfully generated {len(drivers)} driver routes")
        return drivers
    
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
                'find_nearby_drivers_for_passenger',
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
    
    def visualize_prefilter_results(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        analysis_data: Dict,
        title: str = "Passenger-Driver Spatial Pre-Filter Results"
    ) -> None:
        """
        Visualize spatial pre-filter results
        
        Args:
            passenger_pickup: Passenger pickup coordinates
            passenger_destination: Passenger destination coordinates
            analysis_data: Results from spatial_prefilter or two_step_analysis
            title: Plot title
        """
        
        if not analysis_data:
            print("❌ No analysis data to visualize")
            return
        
        spatial_matches = analysis_data['spatial_matches']
        prefilter_stats = analysis_data['prefilter_stats']
        
        print(f"📊 Creating visualization...")
        
        # Create map figure
        fig = go.Figure()
        
        # Add passenger trip
        fig.add_trace(go.Scattermap(
            lon=[passenger_pickup[0], passenger_destination[0]],
            lat=[passenger_pickup[1], passenger_destination[1]],
            mode="markers+lines",
            line=dict(width=4, color='red'),
            marker=dict(size=16, color='red'),
            name="🧑 Passenger Trip",
            hovertemplate="Passenger Trip<br>%{text}<extra></extra>",
            text=["Pickup", "Destination"],
            showlegend=True
        ))
        
        # Categorize drivers
        pickup_only = {'lons': [], 'lats': [], 'labels': [], 'routes': []}
        destination_only = {'lons': [], 'lats': [], 'labels': [], 'routes': []}
        both_intersect = {'lons': [], 'lats': [], 'labels': [], 'routes': []}
        
        for match in spatial_matches:
            route_coords = match['route_geojson']['coordinates']
            start_coords = route_coords[0]
            end_coords = route_coords[-1]
            
            driver_label = match['driver_label']
            driver_info = match['driver_info']
            
            hover_text = (f"{driver_label}<br>"
                         f"Distance: {driver_info['distance_km']}km<br>"
                         f"Duration: {driver_info['duration_min']}min<br>"
                         f"Seats: {driver_info['available_seats']}<br>"
                         f"Max detour: {driver_info['max_detour_km']}km<br>"
                         f"Departure: {driver_info['departure_time']}")
            
            if match['both_intersects']:
                both_intersect['lons'].extend([start_coords[0], end_coords[0]])
                both_intersect['lats'].extend([start_coords[1], end_coords[1]])
                both_intersect['labels'].extend([hover_text, hover_text])
                both_intersect['routes'].append(route_coords)
            elif match['pickup_intersects']:
                pickup_only['lons'].extend([start_coords[0], end_coords[0]])
                pickup_only['lats'].extend([start_coords[1], end_coords[1]])
                pickup_only['labels'].extend([hover_text, hover_text])
                pickup_only['routes'].append(route_coords)
            else:  # destination_intersects
                destination_only['lons'].extend([start_coords[0], end_coords[0]])
                destination_only['lats'].extend([start_coords[1], end_coords[1]])
                destination_only['labels'].extend([hover_text, hover_text])
                destination_only['routes'].append(route_coords)
        
        # Add driver routes and points
        colors = {
            'both': {'route': 'green', 'marker': 'darkgreen', 'name': '✅ Both Intersect'},
            'pickup': {'route': 'orange', 'marker': 'darkorange', 'name': '🔶 Pickup Only'}, 
            'destination': {'route': 'blue', 'marker': 'darkblue', 'name': '🔷 Destination Only'}
        }
        
        for category, data in [('both', both_intersect), ('pickup', pickup_only), ('destination', destination_only)]:
            if data['lons']:
                # Add route lines
                for route_coords in data['routes']:
                    route_lons = [coord[0] for coord in route_coords]
                    route_lats = [coord[1] for coord in route_coords]
                    
                    fig.add_trace(go.Scattermap(
                        lon=route_lons,
                        lat=route_lats,
                        mode="lines",
                        line=dict(width=2, color=colors[category]['route']),
                        hoverinfo='skip',
                        showlegend=False,
                        opacity=0.7
                    ))
                
                # Add start/end markers
                fig.add_trace(go.Scattermap(
                    lon=data['lons'],
                    lat=data['lats'],
                    mode="markers",
                    marker=dict(size=8, color=colors[category]['marker']),
                    name=colors[category]['name'],
                    hovertemplate="%{text}<extra></extra>",
                    text=data['labels'],
                    showlegend=True
                ))
        
        # Calculate center for map
        all_lons = [passenger_pickup[0], passenger_destination[0]]
        all_lats = [passenger_pickup[1], passenger_destination[1]]
        
        for match in spatial_matches:
            route_coords = match['route_geojson']['coordinates']
            all_lons.extend([coord[0] for coord in route_coords])
            all_lats.extend([coord[1] for coord in route_coords])
        
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        
        # Update layout
        fig.update_layout(
            map=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=9
            ),
            title=f"{title}<br>" +
                  f"Found: {prefilter_stats['filtered_drivers']}/{prefilter_stats['total_drivers_checked']} drivers " +
                  f"(🎯 {prefilter_stats['both_intersects_count']} both, " +
                  f"🔶 {prefilter_stats['pickup_matches'] - prefilter_stats['both_intersects_count']} pickup, " +
                  f"🔷 {prefilter_stats['destination_matches'] - prefilter_stats['both_intersects_count']} destination)",
            height=800,
            showlegend=True
        )
        
        fig.show()
    
    def test_prefilter_performance(
        self,
        passenger_pickup: Tuple[float, float],
        passenger_destination: Tuple[float, float],
        num_drivers: int = 100
    ) -> None:
        """
        Test and demonstrate pre-filter performance
        
        Args:
            passenger_pickup: Passenger pickup coordinates
            passenger_destination: Passenger destination coordinates  
            num_drivers: Number of sample drivers to generate
        """
        
        print(f"🧪 Testing Pre-Filter Performance")
        print("=" * 60)
        
        # Generate sample drivers
        sample_drivers = self.generate_sample_drivers(
            center_coords=passenger_pickup,
            num_drivers=num_drivers,
            radius_km=30.0
        )
        
        print(f"\n📊 Performance Test Results:")
        print("-" * 40)
        
        # Test different pre-filter distances  
        distances = [5000, 10000, 15000, 20000]  # 5km, 10km, 15km, 20km
        
        for distance in distances:
            print(f"\n🔍 Pre-filter distance: {distance/1000}km")
            
            start_time = time.time()
            result = self.spatial_prefilter(
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                driver_routes=sample_drivers,
                prefilter_distance_meters=distance
            )
            filter_time = time.time() - start_time
            
            if result:
                stats = result['prefilter_stats']
                print(f"   ⏱️  Filter time: {filter_time:.3f}s")
                print(f"   📉 Reduction: {stats['reduction_ratio']}%")
                print(f"   🎯 Matches: {stats['filtered_drivers']}/{stats['total_drivers_checked']}")
        
        # Run two-step analysis with realistic drivers 
        print(f"\n🔬 Two-Step Analysis with Realistic Drivers:")
        realistic_large = self.generate_realistic_drivers(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            num_drivers=num_drivers,
            radius_km=30.0
        )
        
        two_step_large = self.two_step_analysis(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            driver_routes=realistic_large,
            prefilter_distance_meters=10000
        )
        
        if two_step_large:
            print(f"\n🎯 Realistic Routes Performance Summary:")
            timing = two_step_large['timing']
            stats = two_step_large['analysis_stats']
            
            print(f"   ⏱️  Total time: {timing['total_time']:.2f}s")
            print(f"   📊 Pre-filter efficiency: {stats['spatial_conversion']}%")
            print(f"   🎯 Corridor efficiency: {stats['corridor_conversion']}%")
            print(f"   🏆 Overall efficiency: {stats['overall_conversion']}%")
            print(f"   🚗 Detour distribution: {two_step_large['detour_distribution']}")
            
            # Convert two-step result to format expected by visualization
            viz_data = {
                'spatial_matches': two_step_large['spatial_matches'],
                'prefilter_stats': two_step_large['prefilter_stats']
            }
            
            # Visualize results
            self.visualize_prefilter_results(
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                analysis_data=viz_data,
                title=f"Realistic Routes: {num_drivers} Drivers → Two-Step Analysis"
            )


# ===== EXAMPLE USAGE AND TESTING =====

def main():
    """
    Two-Step Passenger-Driver Matching System
    
    Flow:
    1. Passenger requests ride: "Downtown → Airport"
    2. Spatial pre-filter (10km): Find drivers in general area
    3. Corridor analysis: Check each driver's individual detour preference
    4. Result: List of drivers willing and able to help
    """
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    # Initialize passenger-driver matcher
    matcher = PassengerDriverMatcher(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    print("🧑‍🤝‍🧑 Two-Step Passenger-Driver Matching System")
    print("=" * 60)
    print("Step 1: Spatial pre-filter (10km) - 'Are we in the same area?'")
    print("Step 2: Corridor analysis - 'Does this fit driver's detour preference?'")
    print("=" * 60)
    
    # Passenger trip in Edmonton
    passenger_pickup = (-113.525540, 53.519250)     # Downtown Edmonton
    passenger_destination = (-113.606566, 53.430753) # Southwest Edmonton
    
    print(f"🧑 Passenger Trip:")
    print(f"   Pickup: {passenger_pickup}")
    print(f"   Destination: {passenger_destination}")
    
    # Test 1: Basic spatial pre-filtering
    print(f"\n🧪 Test 1: Basic Spatial Pre-Filtering")
    print("-" * 40)
    
    # Generate sample drivers
    sample_drivers = matcher.generate_sample_drivers(
        center_coords=passenger_pickup,
        num_drivers=75,
        radius_km=25.0
    )
    
    # Run spatial pre-filter
    prefilter_result = matcher.spatial_prefilter(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        driver_routes=sample_drivers,
        prefilter_distance_meters=10000  # 10km pre-filter
    )
    
    if prefilter_result:
        matcher.visualize_prefilter_results(
            passenger_pickup=passenger_pickup,
            passenger_destination=passenger_destination,
            analysis_data=prefilter_result,
            title="Test 1: Spatial Pre-Filter (10km)"
        )
    
    # Test 2: Two-Step Analysis with Realistic Routes
    print(f"\n🧪 Test 2: Two-Step Analysis with Realistic Routes")
    print("-" * 60)
    
    # Generate more realistic drivers
    realistic_drivers = matcher.generate_realistic_drivers(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        num_drivers=50,
        radius_km=25.0
    )
    
    two_step_realistic = matcher.two_step_analysis(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        driver_routes=realistic_drivers,
        prefilter_distance_meters=10000,  # 10km pre-filter
        direction_tolerance=0.05          # 5% direction tolerance
    )
    
    if two_step_realistic:
        viable_drivers = two_step_realistic['viable_drivers']
        analysis_stats = two_step_realistic['analysis_stats']
        timing = two_step_realistic['timing']
        
        print(f"\n📊 Realistic Routes Results:")
        print(f"   🔧 Spatial filter: {analysis_stats['spatially_filtered']}/{analysis_stats['total_drivers']} " +
              f"({analysis_stats['spatial_conversion']}%)")
        print(f"   🎯 Corridor filter: {analysis_stats['final_viable']}/{analysis_stats['spatially_filtered']} " +
              f"({analysis_stats['corridor_conversion']}%)")
        print(f"   🏆 Overall: {analysis_stats['final_viable']}/{analysis_stats['total_drivers']} " +
              f"({analysis_stats['overall_conversion']}%)")
        
        print(f"\n📋 Viable Drivers Found:")
        for i, driver in enumerate(viable_drivers[:5]):  # Show top 5
            driver_info = driver['driver_info']
            corridor = driver['corridor_analysis']
            
            print(f"   ✅ {driver['driver_label']}:")
            print(f"      📍 Distance to route: {driver['min_distance_meters']:.0f}m")
            print(f"      🚗 Route: {driver_info['distance_km']}km, {driver_info['duration_min']}min")
            print(f"      🕐 Departure: {driver_info['departure_time']}")
            print(f"      💺 Seats: {driver_info['available_seats']}")
            print(f"      🎯 Max detour: {driver_info['max_detour_km']}km (driver's choice)")
            print(f"      📈 Progress: {corridor.get('pickup_progress', 'N/A'):.3f} → {corridor.get('dropoff_progress', 'N/A'):.3f}")

    # Test 3: Two-Step Analysis (Original Random Routes)
    print(f"\n🧪 Test 3: Two-Step Analysis (Original Random Routes)")
    print("-" * 60)
    
    two_step_result = matcher.two_step_analysis(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        driver_routes=sample_drivers,
        prefilter_distance_meters=10000,  # 10km pre-filter
        direction_tolerance=0.05          # 5% direction tolerance
    )
    
    if two_step_result:
        viable_drivers = two_step_result['viable_drivers']
        analysis_stats = two_step_result['analysis_stats']
        timing = two_step_result['timing']
        
        print(f"\n📊 Random Routes Results:")
        print(f"   🔧 Spatial filter: {analysis_stats['spatially_filtered']}/{analysis_stats['total_drivers']} " +
              f"({analysis_stats['spatial_conversion']}%)")
        print(f"   🎯 Corridor filter: {analysis_stats['final_viable']}/{analysis_stats['spatially_filtered']} " +
              f"({analysis_stats['corridor_conversion']}%)")
        print(f"   🏆 Overall: {analysis_stats['final_viable']}/{analysis_stats['total_drivers']} " +
              f"({analysis_stats['overall_conversion']}%)")
        
        # Debug: Show why drivers are being rejected
        print(f"\n🔍 Debug: Why drivers are rejected:")
        filtered_drivers = two_step_result['spatial_matches']
        rejection_reasons = {'not_in_corridor': 0, 'wrong_direction': 0, 'other': 0}
        
        for driver in filtered_drivers[:10]:  # Check first 10
            driver_info = driver['driver_info']
            
            # Get detailed analysis for this driver
            corridor_result = matcher.analyze_single_driver_for_passenger(
                driver_route_geojson=driver['route_geojson'],
                passenger_pickup=passenger_pickup,
                passenger_destination=passenger_destination,
                driver_max_detour_meters=driver_info['max_detour_meters'],
                direction_tolerance=0.05
            )
            
            if not corridor_result.get('both_in_corridor', False):
                rejection_reasons['not_in_corridor'] += 1
                print(f"   ❌ {driver['driver_label']}: Not both in {driver_info['max_detour_km']}km corridor")
            elif not corridor_result.get('direction_aligned', False):
                rejection_reasons['wrong_direction'] += 1
                print(f"   ❌ {driver['driver_label']}: Wrong direction (detour: {driver_info['max_detour_km']}km)")
            else:
                rejection_reasons['other'] += 1
                print(f"   ❌ {driver['driver_label']}: Other reason")

    # Test 5: Lenient Parameters Test 
    print(f"\n🧪 Test 5: Lenient Parameters Test (Debugging)")
    print("-" * 50)
    
    # Test with more lenient parameters to see if we can get matches
    lenient_result = matcher.two_step_analysis(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        driver_routes=sample_drivers[:20],  # Just 20 drivers for faster testing
        prefilter_distance_meters=15000,    # 15km pre-filter (more lenient)
        direction_tolerance=0.15           # 15% direction tolerance (more lenient)
    )
    
    if lenient_result:
        print(f"\n📊 Lenient Parameters Results:")
        stats = lenient_result['analysis_stats']
        print(f"   🔧 Spatial filter: {stats['spatially_filtered']}/{stats['total_drivers']} ({stats['spatial_conversion']}%)")
        print(f"   🎯 Corridor filter: {stats['final_viable']}/{stats['spatially_filtered']} ({stats['corridor_conversion']}%)")
        print(f"   🏆 Overall: {stats['final_viable']}/{stats['total_drivers']} ({stats['overall_conversion']}%)")
        
        if stats['final_viable'] > 0:
            print(f"   ✅ Found matches with lenient parameters!")
        else:
            print(f"   ❌ Still no matches even with lenient parameters")

    # Test 6: Performance demonstration with larger dataset
    print(f"\n🧪 Test 6: Performance Demonstration")
    print("-" * 40)
    
    matcher.test_prefilter_performance(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        num_drivers=100
    )


if __name__ == "__main__":
    main()