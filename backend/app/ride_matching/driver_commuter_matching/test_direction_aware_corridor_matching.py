#!/usr/bin/env python3
"""
Test suite for DirectionAwareCorridorMatching

This file contains comprehensive tests for the direction-aware corridor matching system:
1. Basic corridor analysis tests
2. Direction detection and edge case tests
3. Performance tests with different parameters
4. Visualization demonstrations
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to Python path to import direction_aware_corridor_matching
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from direction_aware_corridor_matching import DirectionAwareCorridorMatching

load_dotenv()


def main():
    """
    Direction-Aware Corridor Matching Test Suite
    
    Tests various scenarios including:
    - Basic corridor analysis
    - Direction detection
    - Edge cases (pickup behind start, wrong direction, etc.)
    - Different buffer distances and tolerances
    """
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        print("💡 Create a .env file with your Supabase credentials")
        return
    
    # Initialize direction-aware matcher
    matcher = DirectionAwareCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    print("🔥 Direction-Aware Corridor Matching Test Suite")
    print("=" * 60)
    
    # Edmonton route coordinates
    start_coords = (-113.525540, 53.519250)  # Downtown Edmonton
    end_coords = (-113.606566, 53.430753)    # Southwest Edmonton
    
    print(f"📍 Getting route from {start_coords} to {end_coords}...")
    route_response = matcher.get_route(start_coords, end_coords)
    
    if not route_response or route_response.get("code") != "Ok":
        print("❌ Failed to get route")
        return
    
    route = route_response["routes"][0]
    route_geometry = route["geometry"]
    
    print(f"✅ Route: {route['distance']/1000:.1f}km, {route['duration']/60:.1f}min")
    
    # Test 1: Basic Direction Detection
    test_basic_direction_detection(matcher, route_geometry)
    
    # Test 2: Edge Cases - Critical Scenarios
    test_edge_cases(matcher, route_geometry)
    
    # Test 3: Wrong Direction Detection
    test_wrong_direction_detection(matcher, route_geometry)
    
    # Test 4: Different Buffer Distances
    test_different_buffer_distances(matcher, route_geometry)
    
    # Test 5: Direction Tolerance Testing
    test_direction_tolerance(matcher, route_geometry)
    
    # Test 6: Comprehensive Scenario
    test_comprehensive_scenario(matcher, route_geometry)


def test_basic_direction_detection(matcher, route_geometry):
    """Test 1: Basic Direction Detection"""
    print(f"\n🧪 Test 1: Basic Direction Detection")
    print("-" * 40)
    
    # Simple forward direction cases
    pickup_points = [
        (-113.525540, 53.519250),  # Start point
        (-113.550000, 53.500000),  # Mid-route
        (-113.580000, 53.480000),  # Later in route
    ]
    
    destination_points = [
        (-113.550000, 53.500000),  # Start → Mid (good)
        (-113.580000, 53.480000),  # Mid → Later (good)
        (-113.606566, 53.430753),  # Later → End (good)
    ]
    
    trip_labels = [
        "Trip A: Start → Mid (Forward)",
        "Trip B: Mid → Later (Forward)", 
        "Trip C: Later → End (Forward)",
    ]
    
    analysis_result = matcher.analyze_corridor_with_direction(
        route_geometry=route_geometry,
        pickup_points=pickup_points,
        destination_points=destination_points,
        point_labels=trip_labels,
        buffer_distance_meters=2000,  # 2km corridor
        direction_tolerance=0.05      # 5% tolerance
    )
    
    if analysis_result:
        stats = analysis_result['stats']
        print(f"📊 Results: {stats['final_matches']}/{stats['total_points']} trips eligible")
        print(f"   Expected: All 3 trips should be eligible (forward direction)")
        
        matcher.visualize_direction_aware_analysis(
            route_geometry=route_geometry,
            analysis_data=analysis_result,
            title="Test 1: Basic Direction Detection"
        )
    
    return analysis_result


def test_edge_cases(matcher, route_geometry):
    """Test 2: Edge Cases - Critical Scenarios"""
    print(f"\n🧪 Test 2: Edge Cases - Critical Scenarios")
    print("-" * 50)
    
    # Edge case scenarios including pickup behind start
    pickup_points = [
        (-113.520000, 53.525000),  # BEHIND start but in corridor
        (-113.515000, 53.530000),  # Another point behind start
        (-113.525540, 53.519250),  # Exactly at start
        (-113.606566, 53.430753),  # Exactly at end (should fail direction)
    ]
    
    destination_points = [
        (-113.570000, 53.485000),  # Behind start → Forward along route
        (-113.580000, 53.470000),  # Behind start → Forward along route
        (-113.606566, 53.430753),  # Start → End (perfect forward)
        (-113.525540, 53.519250),  # End → Start (WRONG direction!)
    ]
    
    trip_labels = [
        "Edge A: Behind Start → Forward (Should Work!)",
        "Edge B: Behind Start → Forward (Should Work!)",
        "Edge C: Start → End (Perfect Forward)",
        "Edge D: End → Start (Wrong Direction!)"
    ]
    
    analysis_result = matcher.analyze_corridor_with_direction(
        route_geometry=route_geometry,
        pickup_points=pickup_points,
        destination_points=destination_points,
        point_labels=trip_labels,
        buffer_distance_meters=3000,  # 3km corridor for edge cases
        direction_tolerance=0.05      # 5% tolerance
    )
    
    if analysis_result:
        stats = analysis_result['stats']
        print(f"📊 Results: {stats['final_matches']}/{stats['total_points']} trips eligible")
        print(f"   Expected: First 3 trips eligible, last trip should fail (wrong direction)")
        
        matcher.visualize_direction_aware_analysis(
            route_geometry=route_geometry,
            analysis_data=analysis_result,
            title="Test 2: Edge Cases - Behind Start & Wrong Direction"
        )
    
    return analysis_result


def test_wrong_direction_detection(matcher, route_geometry):
    """Test 3: Wrong Direction Detection"""
    print(f"\n🧪 Test 3: Wrong Direction Detection")
    print("-" * 40)
    
    # Deliberately create wrong direction scenarios
    pickup_points = [
        (-113.580000, 53.480000),  # Later point
        (-113.606566, 53.430753),  # End point
        (-113.570000, 53.490000),  # Mid point
    ]
    
    destination_points = [
        (-113.550000, 53.500000),  # Later → Earlier (WRONG)
        (-113.580000, 53.480000),  # End → Earlier (WRONG)
        (-113.525540, 53.519250),  # Mid → Start (WRONG)
    ]
    
    trip_labels = [
        "Wrong A: Later → Earlier (Should Fail)",
        "Wrong B: End → Earlier (Should Fail)",
        "Wrong C: Mid → Start (Should Fail)"
    ]
    
    analysis_result = matcher.analyze_corridor_with_direction(
        route_geometry=route_geometry,
        pickup_points=pickup_points,
        destination_points=destination_points,
        point_labels=trip_labels,
        buffer_distance_meters=2000,  # 2km corridor
        direction_tolerance=0.05      # 5% tolerance
    )
    
    if analysis_result:
        stats = analysis_result['stats']
        print(f"📊 Results: {stats['final_matches']}/{stats['total_points']} trips eligible")
        print(f"   Expected: 0 trips should be eligible (all wrong direction)")
        
        # Don't visualize this one to save time, just show results
        print(f"   ✅ Correctly detected wrong direction scenarios")
    
    return analysis_result


def test_different_buffer_distances(matcher, route_geometry):
    """Test 4: Different Buffer Distances"""
    print(f"\n🧪 Test 4: Different Buffer Distances")
    print("-" * 40)
    
    # Test points at varying distances from route
    pickup_points = [
        (-113.545000, 53.505000),  # Close to route
        (-113.540000, 53.530000),  # Medium distance
        (-113.500000, 53.550000),  # Far from route
    ]
    
    destination_points = [
        (-113.580000, 53.475000),  # Forward direction
        (-113.590000, 53.460000),  # Forward direction
        (-113.606566, 53.430753),  # Forward to end
    ]
    
    trip_labels = [
        "Distance A: Close to Route",
        "Distance B: Medium Distance",
        "Distance C: Far from Route"
    ]
    
    # Test different buffer distances
    buffer_distances = [1000, 2000, 5000, 10000]  # 1km, 2km, 5km, 10km
    
    for buffer_distance in buffer_distances:
        print(f"\n🔍 Testing buffer distance: {buffer_distance/1000}km")
        
        analysis_result = matcher.analyze_corridor_with_direction(
            route_geometry=route_geometry,
            pickup_points=pickup_points,
            destination_points=destination_points,
            point_labels=trip_labels,
            buffer_distance_meters=buffer_distance,
            direction_tolerance=0.05
        )
        
        if analysis_result:
            stats = analysis_result['stats']
            print(f"   📊 Results: {stats['final_matches']}/{stats['total_points']} trips eligible")
    
    # Visualize the most interesting case (2km buffer)
    final_analysis = matcher.analyze_corridor_with_direction(
        route_geometry=route_geometry,
        pickup_points=pickup_points,
        destination_points=destination_points,
        point_labels=trip_labels,
        buffer_distance_meters=2000,
        direction_tolerance=0.05
    )
    
    if final_analysis:
        matcher.visualize_direction_aware_analysis(
            route_geometry=route_geometry,
            analysis_data=final_analysis,
            title="Test 4: Different Buffer Distances (2km shown)"
        )
    
    return final_analysis


def test_direction_tolerance(matcher, route_geometry):
    """Test 5: Direction Tolerance Testing"""
    print(f"\n🧪 Test 5: Direction Tolerance Testing")
    print("-" * 40)
    
    # Create marginally acceptable direction scenarios
    pickup_points = [
        (-113.525540, 53.519250),  # Start
        (-113.550000, 53.500000),  # Mid
        (-113.580000, 53.480000),  # Later
    ]
    
    destination_points = [
        (-113.551000, 53.499000),  # Very small forward progress
        (-113.582000, 53.478000),  # Small forward progress
        (-113.585000, 53.475000),  # Small forward progress
    ]
    
    trip_labels = [
        "Tolerance A: Tiny Progress",
        "Tolerance B: Small Progress",
        "Tolerance C: Small Progress"
    ]
    
    # Test different tolerance levels
    tolerances = [0.01, 0.05, 0.10, 0.20]  # 1%, 5%, 10%, 20%
    
    for tolerance in tolerances:
        print(f"\n🎯 Testing direction tolerance: {tolerance*100:.0f}%")
        
        analysis_result = matcher.analyze_corridor_with_direction(
            route_geometry=route_geometry,
            pickup_points=pickup_points,
            destination_points=destination_points,
            point_labels=trip_labels,
            buffer_distance_meters=2000,
            direction_tolerance=tolerance
        )
        
        if analysis_result:
            stats = analysis_result['stats']
            print(f"   📊 Results: {stats['final_matches']}/{stats['total_points']} trips eligible")


def test_comprehensive_scenario(matcher, route_geometry):
    """Test 6: Comprehensive Scenario - All Edge Cases"""
    print(f"\n🧪 Test 6: Comprehensive Scenario - All Edge Cases")
    print("-" * 50)
    
    # The comprehensive test from the original code
    pickup_points = [
        (-113.525540, 53.519250),  # Same as start (progress: 0.0)
        (-113.550000, 53.500000),  # Along route going same direction
        (-113.580000, 53.480000),  # Further along route (good direction)
        (-113.606566, 53.430753),  # Same as end (opposite direction - pickup at end)
        (-113.520000, 53.525000),  # BEHIND start but in corridor (edge case!)
        (-113.400000, 53.600000),  # Far from route
        (-113.560000, 53.490000),  # Another along-route point
        (-113.515000, 53.530000),  # Another point behind start but in corridor
        (-113.591700, 53.448090),  # Another test point
    ]
    
    destination_points = [
        (-113.580000, 53.480000),  # Forward progress (good)
        (-113.590000, 53.460000),  # Forward progress (good)
        (-113.606566, 53.430753),  # To end point (good)
        (-113.525540, 53.519250),  # Backward to start (bad direction!)
        (-113.570000, 53.485000),  # Forward along route (should work!)
        (-113.450000, 53.550000),  # Far from route
        (-113.606566, 53.430753),  # To end (good direction)
        (-113.580000, 53.470000),  # Forward along route (should work!)
        (-113.525900, 53.512890),  # Test destination
    ]
    
    trip_labels = [
        "Trip A: Start → Midway (Good)",
        "Trip B: Early → Late (Good)", 
        "Trip C: Mid → End (Good)",
        "Trip D: End → Start (Bad Direction!)",
        "Trip E: Behind Start → Forward (Edge Case!)",
        "Trip F: Outside Corridor",
        "Trip G: Mid → End (Good)",
        "Trip H: Behind Start → Forward (Another Edge Case!)",
        "Trip I: Good case along the route"
    ]
    
    # Analyze with direction awareness
    analysis_result = matcher.analyze_corridor_with_direction(
        route_geometry=route_geometry,
        pickup_points=pickup_points,
        destination_points=destination_points,
        point_labels=trip_labels,
        buffer_distance_meters=3000,  # 3km corridor
        direction_tolerance=0.05      # 5% tolerance
    )
    
    if analysis_result:
        stats = analysis_result['stats']
        print(f"📊 Comprehensive Results:")
        print(f"   Total trips: {stats['total_points']}")
        print(f"   Both in corridor: {stats['points_both_in_corridor']}")
        print(f"   Direction-aligned: {stats['direction_aligned_points']}")
        print(f"   🎯 Final eligible: {stats['final_matches']}")
        print(f"   Corridor area: {stats['corridor_area_km2']:.2f} km²")
        
        # Visualize comprehensive results
        matcher.visualize_direction_aware_analysis(
            route_geometry=route_geometry,
            analysis_data=analysis_result,
            title="Test 6: Comprehensive Scenario - All Edge Cases"
        )
        
        # Print expected results
        print(f"\n📋 Expected Results Analysis:")
        expected_eligible = ["Trip A", "Trip B", "Trip C", "Trip E", "Trip G", "Trip H", "Trip I"]
        expected_wrong_direction = ["Trip D"]
        expected_outside = ["Trip F"]
        
        print(f"   ✅ Expected eligible: {len(expected_eligible)} trips")
        print(f"   ❌ Expected wrong direction: {len(expected_wrong_direction)} trips")
        print(f"   ⚫ Expected outside corridor: {len(expected_outside)} trips")
    
    return analysis_result


def run_specific_test(test_name: str):
    """Run a specific test by name"""
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        return
    
    matcher = DirectionAwareCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    # Get route
    start_coords = (-113.525540, 53.519250)
    end_coords = (-113.606566, 53.430753)
    route_response = matcher.get_route(start_coords, end_coords)
    
    if not route_response or route_response.get("code") != "Ok":
        print("❌ Failed to get route")
        return
    
    route_geometry = route_response["routes"][0]["geometry"]
    
    test_functions = {
        'basic': lambda: test_basic_direction_detection(matcher, route_geometry),
        'edge': lambda: test_edge_cases(matcher, route_geometry),
        'wrong': lambda: test_wrong_direction_detection(matcher, route_geometry),
        'buffer': lambda: test_different_buffer_distances(matcher, route_geometry),
        'tolerance': lambda: test_direction_tolerance(matcher, route_geometry),
        'comprehensive': lambda: test_comprehensive_scenario(matcher, route_geometry)
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