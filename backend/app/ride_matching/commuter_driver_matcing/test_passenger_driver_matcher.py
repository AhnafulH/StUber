#!/usr/bin/env python3
"""
Test suite for PassengerDriverMatcher

This file contains comprehensive tests for the two-step passenger-driver matching system:
1. Spatial pre-filtering tests
2. Two-step analysis with realistic routes
3. Performance demonstrations
4. Debugging tests with lenient parameters
"""

import os
from dotenv import load_dotenv
from passenger_driver_matcher import PassengerDriverMatcher

load_dotenv()


def main():
    """
    Two-Step Passenger-Driver Matching System Test Suite
    
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
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        print("💡 Create a .env file with your Supabase credentials")
        return
    
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
    test_basic_spatial_prefiltering(matcher, passenger_pickup, passenger_destination)
    
    # Test 2: Two-Step Analysis with Realistic Routes
    test_two_step_realistic_routes(matcher, passenger_pickup, passenger_destination)
    
    # Test 3: Two-Step Analysis (Original Random Routes)
    test_two_step_random_routes(matcher, passenger_pickup, passenger_destination)
    
    # Test 4: Debugging with lenient parameters
    test_lenient_parameters(matcher, passenger_pickup, passenger_destination)
    
    # Test 5: Performance demonstration with larger dataset
    test_performance_demonstration(matcher, passenger_pickup, passenger_destination)


def test_basic_spatial_prefiltering(matcher, passenger_pickup, passenger_destination):
    """Test 1: Basic Spatial Pre-Filtering"""
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
    
    return sample_drivers, prefilter_result


def test_two_step_realistic_routes(matcher, passenger_pickup, passenger_destination):
    """Test 2: Two-Step Analysis with Realistic Routes"""
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

    return realistic_drivers, two_step_realistic


def test_two_step_random_routes(matcher, passenger_pickup, passenger_destination):
    """Test 3: Two-Step Analysis (Original Random Routes)"""
    print(f"\n🧪 Test 3: Two-Step Analysis (Original Random Routes)")
    print("-" * 60)
    
    # Generate sample drivers
    sample_drivers = matcher.generate_sample_drivers(
        center_coords=passenger_pickup,
        num_drivers=75,
        radius_km=25.0
    )
    
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

    return sample_drivers, two_step_result


def test_lenient_parameters(matcher, passenger_pickup, passenger_destination):
    """Test 4: Lenient Parameters Test (Debugging)"""
    print(f"\n🧪 Test 4: Lenient Parameters Test (Debugging)")
    print("-" * 50)
    
    # Generate sample drivers for testing
    sample_drivers = matcher.generate_sample_drivers(
        center_coords=passenger_pickup,
        num_drivers=20,  # Just 20 drivers for faster testing
        radius_km=25.0
    )
    
    # Test with more lenient parameters to see if we can get matches
    lenient_result = matcher.two_step_analysis(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        driver_routes=sample_drivers,
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
            viable_drivers = lenient_result['viable_drivers']
            for driver in viable_drivers[:3]:  # Show top 3
                driver_info = driver['driver_info']
                print(f"   ✅ {driver['driver_label']}: {driver_info['max_detour_km']}km detour tolerance")
        else:
            print(f"   ❌ Still no matches even with lenient parameters")

    return lenient_result


def test_performance_demonstration(matcher, passenger_pickup, passenger_destination):
    """Test 5: Performance Demonstration"""
    print(f"\n🧪 Test 5: Performance Demonstration")
    print("-" * 40)
    
    matcher.test_prefilter_performance(
        passenger_pickup=passenger_pickup,
        passenger_destination=passenger_destination,
        num_drivers=100
    )


def test_individual_driver_analysis():
    """Test individual driver analysis functions"""
    print(f"\n🧪 Additional Test: Individual Driver Analysis")
    print("-" * 50)
    
    # This could be expanded to test specific driver-passenger combinations
    # matcher.analyze_single_driver_for_passenger(...)
    pass


def run_specific_test(test_name: str):
    """Run a specific test by name"""
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        return
    
    matcher = PassengerDriverMatcher(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    passenger_pickup = (-113.525540, 53.519250)
    passenger_destination = (-113.606566, 53.430753)
    
    test_functions = {
        'spatial': lambda: test_basic_spatial_prefiltering(matcher, passenger_pickup, passenger_destination),
        'realistic': lambda: test_two_step_realistic_routes(matcher, passenger_pickup, passenger_destination),
        'random': lambda: test_two_step_random_routes(matcher, passenger_pickup, passenger_destination),
        'lenient': lambda: test_lenient_parameters(matcher, passenger_pickup, passenger_destination),
        'performance': lambda: test_performance_demonstration(matcher, passenger_pickup, passenger_destination)
    }
    
    if test_name in test_functions:
        print(f"🔬 Running specific test: {test_name}")
        test_functions[test_name]()
    else:
        print(f"❌ Test '{test_name}' not found. Available tests: {list(test_functions.keys())}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test if provided as command line argument
        test_name = sys.argv[1]
        run_specific_test(test_name)
    else:
        # Run all tests
        main()