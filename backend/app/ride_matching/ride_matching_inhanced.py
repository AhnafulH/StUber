import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client, Client
from typing import List, Dict, Any, Optional



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


def find_matching_offers_with_proximity(
    ride_request: Dict[Any, Any],
    time_window_minutes: int = 45
) -> List[Dict[Any, Any]]:
    """
    ✅ CORRECT: Find drivers using proximity matching based on driver's max detour distance.
    - Passenger pickup within driver's max detour from driver's start
    - Passenger destination within driver's max detour from driver's destination
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
        passenger_pickup_lat = ride_request['starting_latitude']
        passenger_pickup_lng = ride_request['starting_longitude']
        passenger_dest_lat = ride_request['destination_latitude']
        passenger_dest_lng = ride_request['destination_longitude']
        
        print(f"🎯 Proximity-based matching:")
        print(f"   Passenger pickup: ({passenger_pickup_lat}, {passenger_pickup_lng})")
        print(f"   Passenger destination: ({passenger_dest_lat}, {passenger_dest_lng})")
        print(f"   Time window: {start_time} to {end_time}")
        
        # Step 1: Get time-filtered offers (using your existing logic)
        print(f"🕐 Step 1: Time and seat filtering...")
        time_filtered_offers = (supabase.table('Ride_Offer')
                               .select('*')
                               .gte('departure_datetime', start_time_str)
                               .lte('departure_datetime', end_time_str)
                               .gte('seats_available', ride_request['seats_needed'])
                               .execute()).data
        
        print(f"   Found {len(time_filtered_offers)} offers in time window with enough seats")
        
        if not time_filtered_offers:
            print("   No offers in time window - returning empty results")
            return []
        
        # Step 2: Proximity filtering using driver's max detour distance
        print(f"📍 Step 2: Proximity filtering...")
        proximity_matches = []
        
        for offer in time_filtered_offers:
            # Skip offers without max_detour_distance
            if not offer.get('max_detour_distance') or offer['max_detour_distance'] <= 0:
                print(f"   ⚠️ Offer {offer['id']}: No max_detour_distance set - skipping")
                continue
            
            max_detour_meters = offer['max_detour_distance'] * 1000  # Convert km to meters
            
            # ✅ CORRECT: Check if passenger pickup is within driver's detour range from driver start
            pickup_distance_response = supabase.rpc('calculate_distance', {
                'lat1': offer['starting_latitude'],      # Driver start point
                'lng1': offer['starting_longitude'],
                'lat2': passenger_pickup_lat,            # Passenger pickup point
                'lng2': passenger_pickup_lng
            }).execute()
            pickup_distance_meters = pickup_distance_response.data
            
            # ✅ CORRECT: Check if passenger destination is within driver's detour range from driver destination
            dest_distance_response = supabase.rpc('calculate_distance', {
                'lat1': offer['destination_latitude'],   # Driver destination point
                'lng1': offer['destination_longitude'],
                'lat2': passenger_dest_lat,              # Passenger destination point
                'lng2': passenger_dest_lng
            }).execute()
            dest_distance_meters = dest_distance_response.data
            
            # Check if both are within detour tolerance
            pickup_within_range = pickup_distance_meters <= max_detour_meters
            dest_within_range = dest_distance_meters <= max_detour_meters
            
            pickup_km = pickup_distance_meters / 1000
            dest_km = dest_distance_meters / 1000
            max_detour_km = offer['max_detour_distance']
            
            if pickup_within_range and dest_within_range:
                # Add proximity information to offer
                offer['pickup_proximity_km'] = round(pickup_km, 2)
                offer['destination_proximity_km'] = round(dest_km, 2)
                offer['pickup_within_range'] = True
                offer['destination_within_range'] = True
                offer['max_detour_km'] = max_detour_km
                
                proximity_matches.append(offer)
                
                print(f"   ✅ Offer {offer['id']}: pickup {pickup_km:.1f}km (≤{max_detour_km}km), dest {dest_km:.1f}km (≤{max_detour_km}km)")
            else:
                pickup_status = "✅" if pickup_within_range else "❌"
                dest_status = "✅" if dest_within_range else "❌"
                print(f"   ❌ Offer {offer['id']}: pickup {pickup_status}{pickup_km:.1f}km, dest {dest_status}{dest_km:.1f}km (max: {max_detour_km}km)")
        
        print(f"   Proximity filtering: {len(time_filtered_offers)} → {len(proximity_matches)} offers")
        
        # Step 3: Add scoring and sorting (enhanced version of your existing logic)
        print(f"🏆 Step 3: Scoring and ranking...")
        for offer in proximity_matches:
            offer_departure = parse_datetime_safely(offer['departure_datetime'])
            time_diff = abs((offer_departure - request_departure).total_seconds() / 60)
            
            # Add calculated fields (keeping your existing pattern)
            offer['time_difference_minutes'] = round(time_diff, 1)
            offer['match_score'] = calculate_proximity_match_score(offer, ride_request, time_diff)
            
            # Add request context (keeping your existing pattern)
            offer['matched_request'] = {
                'id': ride_request['id'],
                'seats_needed': ride_request['seats_needed'],
                'departure_datetime': ride_request['departure_datetime']
            }
        
        # Sort by best matches first (using your existing pattern)
        proximity_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"🎯 Found {len(proximity_matches)} proximity-based matches")
        
        return proximity_matches
        
    except Exception as e:
        print(f"❌ Error in proximity matching: {e}")
        print("🔄 Falling back to basic time matching...")
        # Graceful fallback to your existing method
        return find_matching_offers_for_request(ride_request, time_window_minutes)

def calculate_proximity_match_score(
    offer: Dict[Any, Any], 
    request: Dict[Any, Any], 
    time_diff_minutes: float
) -> float:
    """
    ✅ CORRECT: Calculate match score based on proximity within driver's detour tolerance.
    """
    # Start with your existing logic
    score = calculate_basic_match_score(offer, request, time_diff_minutes)
    
    # Add proximity bonuses (closer within allowed range = better)
    if 'pickup_proximity_km' in offer and 'max_detour_km' in offer:
        pickup_km = offer['pickup_proximity_km']
        max_detour = offer['max_detour_km']
        
        # Bonus for being close within the allowed range
        proximity_ratio = 1 - (pickup_km / max_detour)  # 1 = very close, 0 = at max distance
        pickup_bonus = proximity_ratio * 15  # Up to 15 point bonus
        score += pickup_bonus
    
    if 'destination_proximity_km' in offer and 'max_detour_km' in offer:
        dest_km = offer['destination_proximity_km']
        max_detour = offer['max_detour_km']
        
        proximity_ratio = 1 - (dest_km / max_detour)
        dest_bonus = proximity_ratio * 10  # Up to 10 point bonus
        score += dest_bonus
    
    # Overall proximity efficiency bonus
    if 'pickup_proximity_km' in offer and 'destination_proximity_km' in offer:
        avg_proximity = (offer['pickup_proximity_km'] + offer['destination_proximity_km']) / 2
        if avg_proximity <= 1.0:  # Both very close (within 1km)
            score += 20  # Excellent proximity bonus
        elif avg_proximity <= 2.0:  # Both reasonably close
            score += 10  # Good proximity bonus
    
    return max(0, score)

def test_proximity_vs_basic_matching():
    """
    ✅ CORRECT: Compare time-based vs proximity-based matching.
    """
    print("\n=== 🆚 Proximity vs Basic Matching Comparison ===")
    
    try:
        # Get test data
        requests, offers = get_all_requests_and_offers()
        
        if not requests:
            print("❌ No requests available for testing")
            return
            
        # Ensure offers have max_detour_distance for testing
        for offer in offers:
            if not offer.get('max_detour_distance') or offer['max_detour_distance'] <= 0:
                # Set test detour distances
                if "University" in offer.get('starting_location', ''):
                    test_detour = 8.0  # University area - longer detour tolerance
                else:
                    test_detour = 6.0  # Default detour tolerance
                
                supabase.table('Ride_Offer').update({
                    'max_detour_distance': test_detour
                }).eq('id', offer['id']).execute()
                print(f"🔧 Set max_detour_distance = {test_detour}km for offer {offer['id']}")
        
        test_request = requests[0]
        print(f"\n📍 Testing with request:")
        print(f"   Route: {test_request['starting_location']} → {test_request['destination']}")
        print(f"   Coordinates: ({test_request['starting_latitude']}, {test_request['starting_longitude']}) → ({test_request['destination_latitude']}, {test_request['destination_longitude']})")
        
        # Test 1: Your existing method
        print(f"\n1️⃣ 🕐 Basic Time-Based Matching:")
        basic_matches = find_matching_offers_for_request(test_request)
        
        # Test 2: New proximity method
        print(f"\n2️⃣ 🎯 Proximity-Based Matching:")
        proximity_matches = find_matching_offers_with_proximity(test_request)
        
        # Show comparison
        print(f"\n📊 COMPARISON:")
        print(f"   🕐 Basic time matching: {len(basic_matches)} results")
        print(f"   🎯 Proximity matching: {len(proximity_matches)} results")
        
        # Show detailed analysis for proximity matches
        if proximity_matches:
            print(f"\n🏆 Proximity match details:")
            for i, match in enumerate(proximity_matches[:2], 1):  # Show top 2
                print(f"   {i}. Offer {match['id']}: {match['starting_location']} → {match['destination']}")
                print(f"      Max detour allowed: {match['max_detour_km']}km")
                print(f"      Pickup proximity: {match['pickup_proximity_km']}km (driver start → passenger pickup)")
                print(f"      Destination proximity: {match['destination_proximity_km']}km (driver dest → passenger dest)")
                print(f"      Time difference: {match['time_difference_minutes']} minutes")
                print(f"      Match score: {match['match_score']:.1f}")
        else:
            print(f"\n❌ No proximity matches found")
            print(f"💡 Try increasing max_detour_distance values or check your coordinate data")
            
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
            req = requests[4]
            offer = offers[3]
            
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
# Update your main test section
if __name__ == "__main__":
    
    print("=== Ride Matching System Test ===")
    
    # First, let's see what data we have
    requests, offers = get_all_requests_and_offers()
    
    if not requests:
        print("\nNo ride requests found. You can create test data using create_test_data()")
    if not offers:
        print("No ride offers found. You can create test data using create_test_data()")
    
    print("\n" + "="*50)
    
    # Test distance calculation
    test_distance_calculation()
    
    print("\n" + "="*50)
    
    # Test with actual data if available
    if requests and offers:
        print(f"\n1️⃣ 🕐 Testing basic matching with request ID: {requests[4]['id']}")
        basic_matches = find_matching_ride_offers(requests[4]['id'])
        
        print(f"\n2️⃣ 🎯 Testing proximity matching:")
        try:
            proximity_matches = find_matching_offers_with_proximity(requests[4])
            print(f"✅ Proximity matching working!")
        except Exception as e:
            print(f"⚠️ Proximity matching issue: {e}")
        
        # Run comparison test
        test_proximity_vs_basic_matching()
    
    # Show test data creation option
    print("\n" + "-"*50)
    print("\n3️⃣ To create test data, uncomment the insert lines in create_test_data()")
    create_test_data()
