#!/usr/bin/env python3
"""
Test script for find_nearby_drivers_for_passenger_modified SQL function
Tests the spatial pre-filtering functionality with real database data
"""
import os
import json
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class SQLFunctionTester:
    def __init__(self):
        """Initialize the SQL function tester"""
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        
        # Initialize Supabase client
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        
        print("SQL Function Tester initialized successfully")
    
    def test_sql_function(
        self, 
        passenger_pickup, 
        passenger_destination,
        prefilter_distance_meters=10000,
        time_window_hours=2,
        passenger_departure_time=None,
        test_name="Test"
    ):
        """Test the find_nearby_drivers_for_passenger_modified function"""
        
        print(f"\n{'='*60}")
        print(f"Running {test_name}")
        print(f"{'='*60}")
        print(f"Passenger pickup: {passenger_pickup}")
        print(f"Passenger destination: {passenger_destination}")
        print(f"Prefilter distance: {prefilter_distance_meters/1000}km")
        
        if passenger_departure_time:
            print(f"Departure time: {passenger_departure_time}")
            print(f"Time window: ±{time_window_hours} hours")
        
        try:
            # Call the SQL function
            result = self.supabase.rpc('find_nearby_drivers_for_passenger_modified', {
                'passenger_pickup_point': passenger_pickup,
                'passenger_destination_point': passenger_destination,
                'prefilter_distance_meters': prefilter_distance_meters,
                'time_window_hours': time_window_hours,
                'passenger_departure_time': passenger_departure_time
            }).execute()
            
            if result.data and len(result.data) > 0:
                self.display_results(result.data[0])
                return result.data[0]
            else:
                print("No results returned from SQL function")
                return None
                
        except Exception as e:
            print(f"Error calling SQL function: {e}")
            return None
    
    def display_results(self, results):
        """Display the results in a formatted way"""
        
        spatial_matches = results.get('spatial_matches', [])
        prefilter_stats = results.get('prefilter_stats', {})
        
        print(f"\n📊 SPATIAL PRE-FILTER RESULTS")
        print(f"{'='*40}")
        
        # Display statistics
        print(f"Total drivers checked: {prefilter_stats.get('total_drivers_checked', 0)}")
        print(f"Prefilter distance: {prefilter_stats.get('prefilter_distance_km', 0)}km")
        print(f"Pickup matches: {prefilter_stats.get('pickup_matches', 0)}")
        print(f"Destination matches: {prefilter_stats.get('destination_matches', 0)}")
        print(f"Both intersects: {prefilter_stats.get('both_intersects_count', 0)}")
        print(f"Either intersects: {prefilter_stats.get('either_intersects_count', 0)}")
        print(f"Reduction ratio: {prefilter_stats.get('reduction_ratio', 0)}%")
        print(f"Filtered drivers: {prefilter_stats.get('filtered_drivers', 0)}")
        
        if spatial_matches:
            print(f"\n🚗 MATCHING DRIVERS ({len(spatial_matches)} found)")
            print(f"{'='*50}")
            
            for i, driver in enumerate(spatial_matches, 1):
                driver_info = driver.get('driver_info', {})
                
                print(f"\n{i}. {driver.get('driver_label', 'Unknown Driver')}")
                print(f"   ID: {driver.get('driver_id', 'N/A')}")
                print(f"   Database ID: {driver_info.get('database_id', 'N/A')}")
                print(f"   Route: {driver_info.get('starting_location', 'N/A')} → {driver_info.get('destination', 'N/A')}")
                print(f"   Departure: {driver_info.get('departure_datetime', 'N/A')}")
                print(f"   Available seats: {driver_info.get('available_seats', 'N/A')}")
                print(f"   Max detour: {driver_info.get('max_detour_km', 'N/A')}km")
                
                print(f"   Spatial Analysis:")
                print(f"     Pickup intersects: {driver.get('pickup_intersects', False)}")
                print(f"     Destination intersects: {driver.get('destination_intersects', False)}")
                print(f"     Both intersects: {driver.get('both_intersects', False)}")
                print(f"     Distance to pickup: {driver.get('distance_to_pickup_meters', 0):.0f}m")
                print(f"     Distance to destination: {driver.get('distance_to_destination_meters', 0):.0f}m")
                print(f"     Min distance: {driver.get('min_distance_meters', 0):.0f}m")
        else:
            print(f"\n❌ No matching drivers found")
    
    def run_test_scenarios(self):
        """Run multiple test scenarios"""
        
        print("Testing find_nearby_drivers_for_passenger_modified SQL Function")
        print("=" * 70)
        
        # Test scenarios with Edmonton coordinates
        test_cases = [
            # {
            #     'name': 'Downtown to University',
            #     'pickup': [-113.490927, 53.544389],  # Downtown Edmonton
            #     'destination': [-113.526319, 53.523219],  # University of Alberta
            #     'distance': 10000,
            #     'departure_time': None
            # },
            {
                'name': 'random to University',
                'pickup': [-113.606857, 53.430824],  # Downtown Edmonton
                'destination': [-113.52631907, 53.52321192],  # University of Alberta
                'distance': 10000,
                'departure_time': None
            },
            # {
            #     'name': 'West Edmonton Mall to Airport',
            #     'pickup': [-113.624289, 53.522412],  # West Edmonton Mall
            #     'destination': [-113.579636, 53.309700],  # Edmonton Airport
            #     'distance': 15000,
            #     'departure_time': None
            # },
            # {
            #     'name': 'Downtown to University (with time filter)',
            #     'pickup': [-113.490927, 53.544389],
            #     'destination': [-113.526319, 53.523219],
            #     'distance': 10000,
            #     'departure_time': '2025-01-15T08:30:00-07:00'
            # },
            # {
            #     'name': 'Tight Distance Filter (5km)',
            #     'pickup': [-113.490927, 53.544389],
            #     'destination': [-113.526319, 53.523219],
            #     'distance': 5000,
            #     'departure_time': None
            # },
            # {
            #     'name': 'Wide Distance Filter (20km)',
            #     'pickup': [-113.490927, 53.544389],
            #     'destination': [-113.526319, 53.523219],
            #     'distance': 20000,
            #     'departure_time': None
            # }
        ]
        
        results = []
        
        for test_case in test_cases:
            result = self.test_sql_function(
                passenger_pickup=test_case['pickup'],
                passenger_destination=test_case['destination'],
                prefilter_distance_meters=test_case['distance'],
                passenger_departure_time=test_case['departure_time'],
                test_name=test_case['name']
            )
            results.append({
                'test_name': test_case['name'],
                'result': result
            })
        
        # Summary
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}")
        
        for i, test_result in enumerate(results, 1):
            result = test_result['result']
            if result:
                stats = result.get('prefilter_stats', {})
                matches = len(result.get('spatial_matches', []))
                total = stats.get('total_drivers_checked', 0)
                print(f"{i}. {test_result['test_name']}: {matches} matches from {total} drivers")
            else:
                print(f"{i}. {test_result['test_name']}: Failed")
    
    def test_single_scenario(self):
        """Test a single scenario with detailed output"""
        
        print("Single Scenario Test - Downtown Edmonton to University of Alberta")
        
        result = self.test_sql_function(
            passenger_pickup=[-113.490927, 53.544389],  # Downtown Edmonton
            passenger_destination=[-113.526319, 53.523219],  # University of Alberta
            prefilter_distance_meters=10000,
            time_window_hours=2,
            passenger_departure_time='2025-01-15T08:30:00-07:00',
            test_name="Single Scenario Test"
        )
        
        if result:
            print(f"\n💾 Raw JSON Output (first 500 chars):")
            print("-" * 40)
            json_str = json.dumps(result, indent=2, default=str)
            print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

def main():
    """Main function"""
    print("Find Nearby Drivers SQL Function Tester")
    print("=" * 50)
    
    # Initialize tester
    try:
        tester = SQLFunctionTester()
    except Exception as e:
        print(f"Failed to initialize tester: {e}")
        return
    
    # Choose test mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        tester.test_single_scenario()
    else:
        tester.run_test_scenarios()

if __name__ == "__main__":
    main()