import os
from dotenv import load_dotenv
from app.ride_matching.integration.direction_aware_corridor_matching import DirectionAwareCorridorMatching

load_dotenv()

def test_database_integration():
    """
    Test the database integration for passenger matching
    """
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    # Validate configuration
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY in environment variables")
        return
    
    # Initialize the matching system
    print("Initializing DirectionAwareCorridorMatching...")
    matcher = DirectionAwareCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    # Define driver route (Edmonton example)
    print("\nSetting up driver route...")
    driver_start = (-113.525540, 53.519250)  # Edmonton start point
    driver_end = (-113.606566, 53.430753)    # Edmonton end point
    
    print(f"Driver route: {driver_start} -> {driver_end}")
    
    # Get driver route from Mapbox
    print("\nFetching route from Mapbox...")
    route_response = matcher.get_route(driver_start, driver_end)
    
    if not route_response or route_response.get("code") != "Ok":
        print("ERROR: Failed to get route from Mapbox")
        print(f"Response: {route_response}")
        return
    
    route = route_response["routes"][0]
    route_geometry = route["geometry"]
    
    print(f"Route obtained: {route['distance']/1000:.1f}km, {route['duration']/60:.1f}min")
    
    # Test database integration
    print("\n" + "="*60)
    print("TESTING DATABASE INTEGRATION")
    print("="*60)
    
    # Test with different buffer distances
    buffer_distances = [1000, 3000, 5000]  # 1km, 3km, 5km
    
    for buffer_distance in buffer_distances:
        print(f"\nTesting with {buffer_distance/1000:.0f}km buffer distance...")
        
        results = matcher.find_matching_passengers_from_db(
            route_geometry=route_geometry,
            buffer_distance_meters=buffer_distance,
            direction_tolerance=0.05  # 5% tolerance
        )
        
        if results:
            print_results_summary(results, buffer_distance)
        else:
            print(f"No results returned for {buffer_distance/1000:.0f}km buffer")
            
        print("-" * 40)

def print_results_summary(results, buffer_distance):
    """
    Print a summary of the matching results
    """
    stats = results['stats']
    eligible_passengers = results.get('eligible_passengers', [])
    
    print(f"RESULTS SUMMARY ({buffer_distance/1000:.0f}km buffer):")
    print(f"  Total passengers analyzed: {stats['total_points']}")
    print(f"  Passengers in corridor: {stats['points_both_in_corridor']}")
    print(f"  Direction-aligned: {stats['direction_aligned_points']}")
    print(f"  Final eligible matches: {stats['final_matches']}")
    print(f"  Corridor area: {stats['corridor_area_km2']:.1f} km²")
    
    if eligible_passengers:
        print(f"\nELIGIBLE PASSENGER DETAILS:")
        for i, match in enumerate(eligible_passengers, 1):
            passenger_info = match['passenger_info']
            pickup_coords = match['pickup_coords']
            dropoff_coords = match['dropoff_coords']
            
            print(f"  {i}. Passenger ID: {match['passenger_id']}")
            print(f"     Pickup: {pickup_coords} -> Dropoff: {dropoff_coords}")
            print(f"     User ID: {passenger_info.get('user_id', 'N/A')}")
            print(f"     Request time: {passenger_info.get('request_time', 'N/A')}")
            print(f"     Pickup address: {passenger_info.get('pickup_address', 'N/A')}")
            print(f"     Dropoff address: {passenger_info.get('dropoff_address', 'N/A')}")
    else:
        print("  No eligible passengers found")

def test_error_handling():
    """
    Test error handling scenarios
    """
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    # Test with invalid credentials
    print("Testing with invalid Supabase credentials...")
    try:
        invalid_matcher = DirectionAwareCorridorMatching(
            "invalid_url", 
            "invalid_key", 
            "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
        )
        
        # This should fail gracefully
        result = invalid_matcher.find_matching_passengers_from_db({})
        print(f"Result with invalid credentials: {result}")
        
    except Exception as e:
        print(f"Expected error with invalid credentials: {e}")

def test_edge_cases():
    """
    Test edge cases and boundary conditions
    """
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Skipping edge case tests - missing credentials")
        return
    
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)
    
    matcher = DirectionAwareCorridorMatching(SUPABASE_URL, SUPABASE_KEY, MAPBOX_TOKEN)
    
    # Get a basic route
    route_response = matcher.get_route((-113.525540, 53.519250), (-113.606566, 53.430753))
    if not route_response:
        print("Cannot test edge cases - failed to get route")
        return
    
    route_geometry = route_response["routes"][0]["geometry"]
    
    # Test with very small buffer
    print("Testing with very small buffer (100m)...")
    results = matcher.find_matching_passengers_from_db(
        route_geometry=route_geometry,
        buffer_distance_meters=100,
        direction_tolerance=0.01
    )
    if results:
        print(f"Small buffer results: {results['stats']['final_matches']} matches")
    
    # Test with very large buffer
    print("Testing with very large buffer (10km)...")
    results = matcher.find_matching_passengers_from_db(
        route_geometry=route_geometry,
        buffer_distance_meters=10000,
        direction_tolerance=0.1
    )
    if results:
        print(f"Large buffer results: {results['stats']['final_matches']} matches")

def main():
    """
    Main test function
    """
    print("DirectionAwareCorridorMatching Database Integration Test")
    print("=" * 60)
    
    # Run tests
    test_database_integration()
    test_error_handling()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    
if __name__ == "__main__":
    main()