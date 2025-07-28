import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def parse_datetime_safely(datetime_str: str) -> datetime:
    """
    Parse datetime string from Supabase (format: 2025-06-28 20:35:00+00).
    """
    try:
        # Handle the +00 timezone format from Supabase
        if datetime_str.endswith('+00'):
            # Replace +00 with +00:00 for proper ISO format
            datetime_str = datetime_str.replace('+00', '+00:00')
        
        # Parse the datetime
        dt = datetime.fromisoformat(datetime_str)
        
        # If it's naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        return dt
        
    except ValueError as e:
        print(f"Error parsing datetime {datetime_str}: {e}")
        raise

def find_matching_ride_offers(
    ride_request_id: int,
    time_window_minutes: int = 45
) -> List[Dict[Any, Any]]:
    """
    Find ride offers that match a specific ride request based on time and seat availability.
    """
    
    try:
        # Get the ride request details
        request_response = supabase.table('Ride_Request').select('*').eq('id', ride_request_id).execute()
        
        if not request_response.data:
            print(f"Ride request with ID {ride_request_id} not found")
            return []
        
        ride_request = request_response.data[0]
        print(f"Found ride request: {ride_request['id']} - {ride_request['starting_location']} to {ride_request['destination']}")
        print(f"Request departure: {ride_request['departure_datetime']}")
        
        return find_matching_offers_for_request(ride_request, time_window_minutes)
        
    except Exception as e:
        print(f"Error finding matching ride offers: {e}")
        return []

def find_matching_offers_for_request(
    ride_request: Dict[Any, Any],
    time_window_minutes: int = 45
) -> List[Dict[Any, Any]]:
    """
    Find matching ride offers for a given ride request object.
    """
    
    try:
        # Parse the request departure time
        request_departure = parse_datetime_safely(ride_request['departure_datetime'])
        
        # Calculate time window (both timezone-aware)
        start_time = request_departure - timedelta(minutes=time_window_minutes)
        end_time = request_departure + timedelta(minutes=time_window_minutes)
        
        print(f"Request departure time: {request_departure}")
        print(f"Searching for offers between {start_time} and {end_time}")
        print(f"Need {ride_request['seats_needed']} seats")
        
        # Convert back to the format Supabase expects (with +00)
        start_time_str = start_time.isoformat().replace('+00:00', '+00')
        end_time_str = end_time.isoformat().replace('+00:00', '+00')
        
        print(f"Query range: {start_time_str} to {end_time_str}")
        
        # Query ride offers within time window and with enough seats
        response = (supabase.table('Ride_Offer')
                   .select('*')
                   .gte('departure_datetime', start_time_str)
                   .lte('departure_datetime', end_time_str)
                   .gte('seats_available', ride_request['seats_needed'])
                   .execute())
        
        matching_offers = response.data
        print(f"Raw query returned {len(matching_offers)} offers")
        
        # Add match details to each offer
        for offer in matching_offers:
            offer_departure = parse_datetime_safely(offer['departure_datetime'])
            time_diff = abs((offer_departure - request_departure).total_seconds() / 60)
            
            # Add calculated fields
            offer['time_difference_minutes'] = round(time_diff, 1)
            offer['match_score'] = calculate_basic_match_score(offer, ride_request, time_diff)
            
            # Add request details for context
            offer['matched_request'] = {
                'id': ride_request['id'],
                'seats_needed': ride_request['seats_needed'],
                'departure_datetime': ride_request['departure_datetime']
            }
        
        # Sort by match score (best matches first)
        matching_offers.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"Found {len(matching_offers)} matching ride offers for request {ride_request['id']}")
        
        return matching_offers
        
    except Exception as e:
        print(f"Error querying ride offers: {e}")
        return []

def calculate_basic_match_score(
    offer: Dict[Any, Any], 
    request: Dict[Any, Any], 
    time_diff_minutes: float
) -> float:
    """
    Calculate a basic match score based on time and seat availability.
    """
    score = 100  # Base score
    
    # Time factor (closer time = higher score)
    score -= time_diff_minutes * 0.8
    
    # Seat efficiency factor
    seats_offered = offer['seats_available']
    seats_needed = request['seats_needed']
    
    if seats_offered == seats_needed:
        score += 10
    elif seats_offered > seats_needed:
        excess_seats = seats_offered - seats_needed
        score -= excess_seats * 2
    
    return max(0, score)

def find_offers_by_datetime_range(
    departure_datetime: str,
    time_window_minutes: int = 45,
    min_seats: int = 1
) -> List[Dict[Any, Any]]:
    """
    Find ride offers within a specific datetime range.
    """
    
    try:
        # If input doesn't have timezone, add UTC
        if '+' not in departure_datetime and 'Z' not in departure_datetime:
            departure_datetime += '+00'
            
        target_time = parse_datetime_safely(departure_datetime)
        start_time = target_time - timedelta(minutes=time_window_minutes)
        end_time = target_time + timedelta(minutes=time_window_minutes)
        
        print(f"Searching for offers between {start_time} and {end_time}")
        
        # Convert to Supabase format
        start_time_str = start_time.isoformat().replace('+00:00', '+00')
        end_time_str = end_time.isoformat().replace('+00:00', '+00')
        
        response = (supabase.table('Ride_Offer')
                   .select('*')
                   .gte('departure_datetime', start_time_str)
                   .lte('departure_datetime', end_time_str)
                   .gte('seats_available', min_seats)
                   .order('departure_datetime')
                   .execute())
        
        offers = response.data
        print(f"Found {len(offers)} offers in database")
        
        # Add time difference for each offer
        for offer in offers:
            offer_time = parse_datetime_safely(offer['departure_datetime'])
            time_diff = abs((offer_time - target_time).total_seconds() / 60)
            offer['time_difference_minutes'] = round(time_diff, 1)
        
        # Sort by time difference
        offers.sort(key=lambda x: x['time_difference_minutes'])
        
        return offers
        
    except Exception as e:
        print(f"Error finding offers by datetime range: {e}")
        return []

def get_all_requests_and_offers():
    """
    Debug function to see what data is actually in the tables.
    """
    try:
        print("=== DEBUG: Current data in tables ===")
        
        # Get all requests
        requests_response = supabase.table('Ride_Request').select('*').execute()
        requests = requests_response.data
        print(f"\nRide_Request table has {len(requests)} records:")
        for req in requests:
            print(f"  ID: {req['id']}, From: {req['starting_location']}, To: {req['destination']}")
            print(f"    Departure: {req['departure_datetime']}, Seats needed: {req['seats_needed']}")
        
        # Get all offers
        offers_response = supabase.table('Ride_Offer').select('*').execute()
        offers = offers_response.data
        print(f"\nRide_Offer table has {len(offers)} records:")
        for offer in offers:
            print(f"  ID: {offer['id']}, From: {offer['starting_location']}, To: {offer['destination']}")
            print(f"    Departure: {offer['departure_datetime']}, Seats available: {offer['seats_available']}")
        
        return requests, offers
        
    except Exception as e:
        print(f"Error getting data: {e}")
        return [], []

def create_test_data():
    """
    Helper function to create some test data if needed.
    """
    try:
        # Current time in the correct format
        current_time = datetime.now(timezone.utc)
        future_time_1 = current_time + timedelta(hours=2)
        future_time_2 = current_time + timedelta(hours=2, minutes=30)
        
        # Format for Supabase (with +00)
        def format_for_supabase(dt):
            return dt.isoformat().replace('+00:00', '+00')
        
        # Sample ride request
        test_request = {
            'starting_location': 'University Campus',
            'starting_latitude': 53.5232,
            'starting_longitude': -113.5263,
            'destination': 'Downtown Edmonton',
            'destination_latitude': 53.5444,
            'destination_longitude': -113.4909,
            'seats_needed': 2,
            'departure_datetime': format_for_supabase(future_time_1)
        }
        
        # Sample ride offer
        test_offer = {
            'starting_location': 'University Campus',
            'starting_latitude': 53.5232,
            'starting_longitude': -113.5263,
            'destination': 'Downtown Edmonton',
            'destination_latitude': 53.5444,
            'destination_longitude': -113.4909,
            'seats_available': 3,
            'departure_datetime': format_for_supabase(future_time_2),
            'max_detour_distance': 5.0
        }
        
        print("Test data formats:")
        print(f"Request datetime: {test_request['departure_datetime']}")
        print(f"Offer datetime: {test_offer['departure_datetime']}")
        
        # Uncomment these lines to actually insert test data
        # supabase.table('Ride_Request').insert(test_request).execute()
        # supabase.table('Ride_Offer').insert(test_offer).execute()
        # print("Test data inserted!")
        
    except Exception as e:
        print(f"Error creating test data: {e}")


def find_matching_offers_with_spatial_filtering(
    ride_request: Dict[Any, Any],
    time_window_minutes: int = 45,
    pickup_radius_meters: int = 5000,  # 5km pickup radius
    destination_radius_meters: int = 10000  # 10km destination radius
) -> List[Dict[Any, Any]]:
    """
    Enhanced ride matching using PostGIS spatial filtering + time filtering.
    This builds on your existing logic but adds location awareness.
    """
    
    try:
        # Parse request data (reusing your existing function)
        request_departure = parse_datetime_safely(ride_request['departure_datetime'])
        start_time = request_departure - timedelta(minutes=time_window_minutes)
        end_time = request_departure + timedelta(minutes=time_window_minutes)
        
        # Convert to Supabase format (reusing your existing logic)
        start_time_str = start_time.isoformat().replace('+00:00', '+00')
        end_time_str = end_time.isoformat().replace('+00:00', '+00')
        
        # Extract coordinates from request
        request_start_lng = ride_request['starting_longitude']
        request_start_lat = ride_request['starting_latitude']
        request_dest_lng = ride_request['destination_longitude']
        request_dest_lat = ride_request['destination_latitude']
        
        print(f"🗺️ Spatial search parameters:")
        print(f"  Pickup area: {pickup_radius_meters}m around ({request_start_lat}, {request_start_lng})")
        print(f"  Destination area: {destination_radius_meters}m around ({request_dest_lat}, {request_dest_lng})")
        print(f"  Time window: {start_time} to {end_time}")
        
        # Step 1: Get time-filtered offers (using your existing logic)
        print(f"🕐 Step 1: Time filtering...")
        time_filtered_offers = (supabase.table('Ride_Offer')
                               .select('*')
                               .gte('departure_datetime', start_time_str)
                               .lte('departure_datetime', end_time_str)
                               .gte('seats_available', ride_request['seats_needed'])
                               .execute()).data
        
        print(f"   Found {len(time_filtered_offers)} offers in time window")
        
        if not time_filtered_offers:
            print("   No offers in time window - returning empty results")
            return []
        
        # Step 2: Add spatial filtering using PostGIS
        print(f"🗺️ Step 2: Spatial filtering...")
        spatially_filtered_offers = []
        
        for offer in time_filtered_offers:
            # Check if offer has geography columns populated
            if not offer.get('starting_point_geo') or not offer.get('destination_point_geo'):
                print(f"   ⚠️ Offer {offer['id']} missing geography data - skipping")
                continue
            
            # Calculate pickup distance using PostGIS
            pickup_distance_response = supabase.rpc('calculate_distance', {
                'lat1': request_start_lat,
                'lng1': request_start_lng,
                'lat2': offer['starting_latitude'],
                'lng2': offer['starting_longitude']
            }).execute()
            
            # Calculate destination distance using PostGIS  
            dest_distance_response = supabase.rpc('calculate_distance', {
                'lat1': request_dest_lat,
                'lng1': request_dest_lng,
                'lat2': offer['destination_latitude'],
                'lng2': offer['destination_longitude']
            }).execute()
            
            pickup_distance = pickup_distance_response.data
            dest_distance = dest_distance_response.data
            
            # Apply spatial filters
            if pickup_distance <= pickup_radius_meters and dest_distance <= destination_radius_meters:
                # Add distance information to the offer
                offer['pickup_distance_meters'] = round(pickup_distance, 1)
                offer['destination_distance_meters'] = round(dest_distance, 1)
                offer['pickup_distance_km'] = round(pickup_distance / 1000, 2)
                offer['destination_distance_km'] = round(dest_distance / 1000, 2)
                
                spatially_filtered_offers.append(offer)
                
                print(f"   ✅ Offer {offer['id']}: pickup {offer['pickup_distance_km']}km, dest {offer['destination_distance_km']}km")
            else:
                print(f"   ❌ Offer {offer['id']}: pickup {pickup_distance/1000:.1f}km (>{pickup_radius_meters/1000}km), dest {dest_distance/1000:.1f}km (>{destination_radius_meters/1000}km)")
        
        print(f"   Spatial filtering: {len(time_filtered_offers)} → {len(spatially_filtered_offers)} offers")
        
        # Step 3: Add scoring and sorting (enhanced version of your existing logic)
        print(f"🎯 Step 3: Scoring and ranking...")
        for offer in spatially_filtered_offers:
            offer_departure = parse_datetime_safely(offer['departure_datetime'])
            time_diff = abs((offer_departure - request_departure).total_seconds() / 60)
            
            # Add calculated fields (keeping your existing pattern)
            offer['time_difference_minutes'] = round(time_diff, 1)
            offer['match_score'] = calculate_spatial_match_score(offer, ride_request, time_diff)
            
            # Add request context (keeping your existing pattern)
            offer['matched_request'] = {
                'id': ride_request['id'],
                'seats_needed': ride_request['seats_needed'],
                'departure_datetime': ride_request['departure_datetime']
            }
        
        # Sort by best matches first (using your existing pattern)
        spatially_filtered_offers.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"🎯 Found {len(spatially_filtered_offers)} spatially-filtered matches")
        
        return spatially_filtered_offers
        
    except Exception as e:
        print(f"❌ Error in spatial matching: {e}")
        print("🔄 Falling back to basic time matching...")
        # Graceful fallback to your existing method
        return find_matching_offers_for_request(ride_request, time_window_minutes)

def calculate_spatial_match_score(
    offer: Dict[Any, Any], 
    request: Dict[Any, Any], 
    time_diff_minutes: float
) -> float:
    """
    Enhanced version of your calculate_basic_match_score with spatial factors.
    """
    # Start with your existing logic
    score = calculate_basic_match_score(offer, request, time_diff_minutes)
    
    # Add spatial bonuses if distance data is available
    if 'pickup_distance_meters' in offer:
        pickup_km = offer['pickup_distance_meters'] / 1000
        # Closer pickup = higher score
        if pickup_km <= 1:
            score += 15  # Very close pickup bonus
        elif pickup_km <= 3:
            score += 5   # Reasonable pickup bonus
        else:
            score -= pickup_km * 2  # Penalty for far pickups
    
    if 'destination_distance_meters' in offer:
        dest_km = offer['destination_distance_meters'] / 1000
        # Closer destination = higher score
        if dest_km <= 2:
            score += 10  # Close destination bonus
        elif dest_km <= 5:
            score += 3   # Reasonable destination bonus
        else:
            score -= dest_km * 1  # Small penalty for far destinations
    
    return max(0, score)

def test_spatial_vs_basic_matching():
    """
    Compare your existing time-based matching vs new spatial matching.
    """
    print("\n=== 🆚 Spatial vs Basic Matching Comparison ===")
    
    try:
        # Get test data
        requests, offers = get_all_requests_and_offers()
        
        if not requests:
            print("❌ No requests available for testing")
            return
            
        test_request = requests[0]
        print(f"\n📍 Testing with request:")
        print(f"   Route: {test_request['starting_location']} → {test_request['destination']}")
        print(f"   Coordinates: ({test_request['starting_latitude']}, {test_request['starting_longitude']}) → ({test_request['destination_latitude']}, {test_request['destination_longitude']})")
        
        # Test 1: Your existing method
        print(f"\n1️⃣ 🕐 Basic Time-Based Matching:")
        basic_matches = find_matching_offers_for_request(test_request)
        
        # Test 2: New spatial method with different radius settings
        radius_tests = [
            {"pickup": 2000, "dest": 3000, "name": "Strict (2km/3km)"},
            {"pickup": 5000, "dest": 7000, "name": "Moderate (5km/7km)"},
            {"pickup": 10000, "dest": 15000, "name": "Loose (10km/15km)"}
        ]
        
        for i, test_params in enumerate(radius_tests, 2):
            print(f"\n{i}️⃣ 🗺️ Spatial Matching - {test_params['name']}:")
            spatial_matches = find_matching_offers_with_spatial_filtering(
                test_request,
                pickup_radius_meters=test_params['pickup'],
                destination_radius_meters=test_params['dest']
            )
        
        # Show summary
        print(f"\n📊 SUMMARY:")
        print(f"   🕐 Basic time matching: {len(basic_matches)} results")
        for i, test_params in enumerate(radius_tests):
            spatial_matches = find_matching_offers_with_spatial_filtering(
                test_request,
                pickup_radius_meters=test_params['pickup'],
                destination_radius_meters=test_params['dest']
            )
            print(f"   🗺️ {test_params['name']}: {len(spatial_matches)} results")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_distance_calculation():
    """
    Test the distance calculation function.
    """
    print("\n=== 📏 Distance Calculation Test ===")
    
    try:
        # Test known distances in Edmonton
        university_lat, university_lng = 53.5232, -113.5263  # University of Alberta
        downtown_lat, downtown_lng = 53.309092, -113.583353     # Downtown Edmonton
        
        distance_response = supabase.rpc('calculate_distance', {
            'lat1': university_lat,
            'lng1': university_lng,
            'lat2': downtown_lat,
            'lng2': downtown_lng
        }).execute()
        
        distance_meters = distance_response.data
        distance_km = distance_meters / 1000
        
        print(f"📍 University of Alberta to Downtown Edmonton:")
        print(f"   Distance: {distance_meters:.0f} meters ({distance_km:.2f} km)")
        print(f"   Expected: ~7-8 km (seems reasonable: {'✅' if 6 <= distance_km <= 10 else '❌'})")
        
        # Test with your actual data
        requests, offers = get_all_requests_and_offers()
        if requests and offers:
            req = requests[0]
            offer = offers[0]
            
            test_distance = supabase.rpc('calculate_distance', {
                'lat1': req['starting_latitude'],
                'lng1': req['starting_longitude'],
                'lat2': offer['starting_latitude'],
                'lng2': offer['starting_longitude']
            }).execute()
            
            print(f"\n📍 Your data test:")
            print(f"   Request: {req['starting_location']} ({req['starting_latitude']}, {req['starting_longitude']})")
            print(f"   Offer: {offer['starting_location']} ({offer['starting_latitude']}, {offer['starting_longitude']})")
            print(f"   Distance: {test_distance.data:.0f} meters ({test_distance.data/1000:.2f} km)")
        
    except Exception as e:
        print(f"❌ Distance test failed: {e}")
        print("💡 Make sure you've added the calculate_distance function to Supabase")



# Example usage and testing
if __name__ == "__main__":
    
    print("=== Ride Matching System Test ===")
    
    # First, let's see what data we have
    requests, offers = get_all_requests_and_offers()
    
    if not requests:
        print("\nNo ride requests found. You can create test data using create_test_data()")
    if not offers:
        print("No ride offers found. You can create test data using create_test_data()")
    
    print("\n" + "="*50)
    
    # Test distance calculation first
    test_distance_calculation()
    
    print("\n" + "="*50)
    
    # Test with actual data if available
    if requests and offers:
        print(f"\n1️⃣ 🕐 Testing basic matching with request ID: {requests[0]['id']}")
        basic_matches = find_matching_ride_offers(requests[0]['id'])
        
        print(f"\n2️⃣ 🗺️ Testing spatial matching:")
        try:
            spatial_matches = find_matching_offers_with_spatial_filtering(requests[0])
            print(f"✅ Spatial matching working!")
        except Exception as e:
            print(f"⚠️ Spatial matching issue: {e}")
        
        # Run comparison test
        test_spatial_vs_basic_matching()
    
    # Show test data creation option
    print("\n" + "-"*50)
    print("\n3️⃣ To create test data, uncomment the insert lines in create_test_data()")
    create_test_data()
