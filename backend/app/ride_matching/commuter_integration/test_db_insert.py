#!/usr/bin/env python3
"""
Test script for creating ride matches
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from PassengerDriverMatcher import PassengerDriverMatcher

load_dotenv()

def test_ride_match_creation():
    """Test creating ride matches and inserting into database"""
    
    print("🧪 Testing Ride Match Creation")
    print("=" * 50)
    
    # Initialize matcher
    matcher = PassengerDriverMatcher(
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_KEY"),
        mapbox_token=""
    )
    
    # Test case
    rider_id = 1  # You'll need an actual rider ID from your system
    pickup = [-113.606857, 53.430824]  # Edmonton coordinates
    destination = [-113.52631907, 53.52321192]
    
    print(f"🔍 Creating matches for rider {rider_id}")
    print(f"   Route: {pickup} → {destination}")
    
    # Find matches and create database records
    results = matcher.find_and_create_matches(
        rider_id=rider_id,
        passenger_pickup=pickup,
        passenger_destination=destination,
        departure_time=None,  # No time filtering
        search_radius_km=10.0,
        price=15.50,  # Optional price
        use_optimized=True
    )
    
    if results['success']:
        print(f"✅ Success!")
        print(f"   Matches created: {results['matches_created']}")
        print(f"   Match IDs: {results.get('match_ids', [])}")
        
        # Show analysis summary
        analysis = results['analysis_results']
        stats = analysis['analysis_stats']
        print(f"   Total drivers checked: {stats['total_drivers']}")
        print(f"   Viable drivers found: {stats['final_viable']}")
        print(f"   Overall conversion: {stats['overall_conversion']}%")
        
    else:
        print(f"❌ Failed: {results.get('error', 'Unknown error')}")

def test_duplicate_prevention():
    """Test that duplicate matches are prevented"""
    
    print(f"\n🔒 Testing Duplicate Prevention")
    print("-" * 30)
    
    matcher = PassengerDriverMatcher(
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_KEY"),
        mapbox_token=""
    )
    
    rider_id = 1
    pickup = [-113.606857, 53.430824]
    destination = [-113.52631907, 53.52321192]
    
    # Try to create matches again with same rider
    print(f"Attempting to create matches again for rider {rider_id}...")
    
    results = matcher.find_and_create_matches(
        rider_id=rider_id,
        passenger_pickup=pickup,
        passenger_destination=destination,
        price=15.50
    )
    
    print(f"Matches created: {results['matches_created']}")
    if results['matches_created'] == 0:
        print("✅ Duplicate prevention working!")
    else:
        print("⚠️ Duplicates may have been created")

def view_created_matches():
    """View the matches that were created"""
    
    print(f"\n👀 Viewing Created Matches")
    print("-" * 30)
    
    matcher = PassengerDriverMatcher(
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_KEY"),
        mapbox_token=""
    )
    
    try:
        # Query recent matches
        result = matcher.supabase.table('Ride_Match').select(
            'id, driver_id, rider_id, price, driver_accept, rider_accept'
        ).order('id', desc=True).limit(10).execute()
        
        if result.data:
            print(f"📊 Recent matches:")
            for match in result.data:
                print(f"   Match {match['id']}: Driver {match['driver_id']} ↔ Rider {match['rider_id']}")
                print(f"      Price: ${match['price']}, Driver Accept: {match['driver_accept']}, Rider Accept: {match['rider_accept']}")
        else:
            print("No matches found in database")
            
    except Exception as e:
        print(f"Error viewing matches: {e}")

if __name__ == "__main__":
    # Test creating matches
    test_ride_match_creation()
    
    # Test duplicate prevention
    test_duplicate_prevention()
    
    # View what was created
    view_created_matches()