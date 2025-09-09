#!/usr/bin/env python3
"""
Test script for PassengerDriverMatcher
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import your matcher class
from PassengerDriverMatcher import PassengerDriverMatcher

load_dotenv()

def test_passenger_driver_matcher():
    """Test the PassengerDriverMatcher functionality"""
    
    print("🧪 Testing PassengerDriverMatcher")
    print("=" * 50)
    
    # Initialize the matcher
    try:
        matcher = PassengerDriverMatcher(
            supabase_url=os.environ.get("SUPABASE_URL"),
            supabase_key=os.environ.get("SUPABASE_KEY"),
            mapbox_token=os.environ.get("MAPBOX_ACCESS_TOKEN")  # Optional, not used in your current code
        )
        print("✅ Matcher initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize matcher: {e}")
        return
    
    # Test coordinates (Edmonton area)
    test_cases = [
        {
            'name': 'Downtown to University',
            'pickup': [-113.606857, 53.430824],  # Downtown Edmonton
            'destination': [-113.52631907, 53.52321192],  # University of Alberta
            'search_radius': 10.0,
            'departure_time': None
        },
        # {
        #     'name': 'Airport to Mall',
        #     'pickup': [-113.579636, 53.309700],  # Edmonton Airport
        #     'destination': [-113.624289, 53.522412],  # West Edmonton Mall
        #     'search_radius': 15.0,
        #     'departure_time': None
        # }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📍 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Test the convenience method
            results = matcher.find_matches_for_passenger(
                passenger_pickup=test_case['pickup'],
                passenger_destination=test_case['destination'],
                departure_time=test_case['departure_time'],
                search_radius_km=test_case['search_radius'],
                time_window_hours=2
            )
            
            if results:
                print_test_results(results, test_case['name'])
            else:
                print("❌ No results returned")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Test optimized version if available
    print(f"\n🚀 Testing Optimized Version")
    print("-" * 30)
    
    if hasattr(matcher, 'two_step_analysis_optimized'):
        try:
            optimized_results = matcher.two_step_analysis_optimized(
                passenger_pickup=test_cases[0]['pickup'],
                passenger_destination=test_cases[0]['destination'],
                prefilter_distance_meters=10000,
                direction_tolerance=0.05,
                time_window_hours=2,
                passenger_departure_time=test_cases[0]['departure_time'].isoformat() if test_cases[0]['departure_time'] else None
            )
            
            if optimized_results:
                print_test_results(optimized_results, "Optimized Analysis")
                print(f"🎯 Performance: {optimized_results['timing']['performance_improvement']}")
            else:
                print("❌ No optimized results returned")
                
        except Exception as e:
            print(f"❌ Optimized test failed: {e}")
    else:
        print("ℹ️ Optimized version not available")

def print_test_results(results: dict, test_name: str):
    """Print formatted test results"""
    
    print(f"✅ {test_name} Results:")
    
    # Timing information
    timing = results.get('timing', {})
    print(f"   ⏱️  Total time: {timing.get('total_time', 0):.2f}s")
    print(f"   ⏱️  Pre-filter: {timing.get('prefilter_time', 0):.2f}s")
    print(f"   ⏱️  Corridor: {timing.get('corridor_time', 0):.2f}s")
    
    # Statistics
    stats = results.get('analysis_stats', {})
    print(f"   📊 Total drivers: {stats.get('total_drivers', 0)}")
    print(f"   📊 Spatially filtered: {stats.get('spatially_filtered', 0)}")
    print(f"   📊 Final viable: {stats.get('final_viable', 0)}")
    print(f"   📊 Overall conversion: {stats.get('overall_conversion', 0)}%")
    
    # Driver details
    viable_drivers = results.get('viable_drivers', [])
    print(f"   🚗 Viable drivers: {len(viable_drivers)}")
    
    for i, driver in enumerate(viable_drivers[:3], 1):  # Show top 3
        driver_info = driver.get('driver_info', {})
        corridor = driver.get('corridor_analysis', {})
        print(f"     {i}. Driver {driver_info.get('database_id', 'N/A')}")
        print(f"        Distance: {driver.get('min_distance_meters', 0):.0f}m")
        print(f"        Max detour: {driver_info.get('max_detour_km', 'N/A')}km")
        print(f"        Match eligible: {corridor.get('match_eligible', False)}")
    
    # Detour distribution
    detour_dist = results.get('detour_distribution', {})
    if detour_dist:
        print(f"   📈 Detour preferences: {detour_dist}")

def test_spatial_prefilter_only():
    """Test just the spatial pre-filter function"""
    
    print(f"\n🔍 Testing Spatial Pre-filter Only")
    print("-" * 30)
    
    try:
        matcher = PassengerDriverMatcher(
            supabase_url=os.environ.get("SUPABASE_URL"),
            supabase_key=os.environ.get("SUPABASE_KEY"),
            mapbox_token=""  # Not needed for this test
        )
        
        result = matcher.spatial_prefilter(
            passenger_pickup=[-113.490927, 53.544389],
            passenger_destination=[-113.526319, 53.523219],
            prefilter_distance_meters=10000,
            time_window_hours=2,
            passenger_departure_time=None
        )
        
        if result:
            stats = result.get('prefilter_stats', {})
            matches = result.get('spatial_matches', [])
            
            print(f"✅ Spatial pre-filter successful")
            print(f"   📊 Total drivers checked: {stats.get('total_drivers_checked', 0)}")
            print(f"   📊 Filtered drivers: {stats.get('filtered_drivers', 0)}")
            print(f"   📊 Reduction ratio: {stats.get('reduction_ratio', 0)}%")
            print(f"   📊 Spatial matches: {len(matches)}")
            
            # Show first few matches
            for i, match in enumerate(matches[:3], 1):
                driver_info = match.get('driver_info', {})
                print(f"     {i}. Driver {driver_info.get('database_id', 'N/A')}")
                print(f"        Pickup intersects: {match.get('pickup_intersects', False)}")
                print(f"        Destination intersects: {match.get('destination_intersects', False)}")
                print(f"        Min distance: {match.get('min_distance_meters', 0):.0f}m")
        else:
            print("❌ No spatial pre-filter results")
            
    except Exception as e:
        print(f"❌ Spatial pre-filter test failed: {e}")

def check_prerequisites():
    """Check if all prerequisites are met"""
    
    print("🔧 Checking Prerequisites")
    print("-" * 30)
    
    # Check environment variables
    required_env = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_env = [var for var in required_env if not os.environ.get(var)]
    
    if missing_env:
        print(f"❌ Missing environment variables: {missing_env}")
        print("   Create a .env file with:")
        for var in missing_env:
            print(f"   {var}=your_value_here")
        return False
    else:
        print("✅ Environment variables configured")
    
    # Check if required SQL functions exist (this would require a database connection)
    print("ℹ️ Make sure these SQL functions are deployed:")
    print("   - find_nearby_drivers_for_passenger_modified")
    print("   - analyze_passenger_against_multiple_drivers (for optimized version)")
    print("   - check_direction_alignment")
    
    return True

if __name__ == "__main__":
    if check_prerequisites():
        test_spatial_prefilter_only()
        test_passenger_driver_matcher()
    else:
        print("❌ Prerequisites not met. Please fix the issues above.")