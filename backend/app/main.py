#!/usr/bin/env python3
"""
Ride Sharing Matching System - Main Demo

This demonstrates the modular ride matching system with separated time-based 
and proximity-based matching algorithms.
"""

from ride_matcher import RideMatcher
from time_matcher import TimeBasedMatcher
from proximity_matcher import ProximityBasedMatcher
from tests import run_all_tests, get_all_requests_and_offers, create_test_data

def demo_basic_usage():
    """
    Demonstrate basic usage of the matching system.
    """
    print("🚗 Ride Matching System Demo")
    print("=" * 50)
    
    # Get available data
    requests, offers = get_all_requests_and_offers()
    
    if not requests:
        print("\n❌ No ride requests found in database")
        print("💡 Run create_test_data() to add sample data")
        return
    
    # Initialize the unified matcher
    matcher = RideMatcher(default_time_window_minutes=45)
    
    # Use the first request for demo
    test_request = requests[0]
    print(f"\n📍 Demo Request:")
    print(f"   ID: {test_request['id']}")
    print(f"   Route: {test_request['starting_location']} → {test_request['destination']}")
    print(f"   Departure: {test_request['departure_datetime']}")
    print(f"   Seats needed: {test_request['seats_needed']}")
    
    # Find best matches using proximity-based algorithm
    print(f"\n🎯 Finding best matches...")
    best_matches = matcher.get_best_matches(
        test_request, 
        max_results=5, 
        prefer_proximity=True
    )
    
    if best_matches:
        print(f"\n✅ Found {len(best_matches)} matching offers:")
        for i, match in enumerate(best_matches, 1):
            print(f"\n   {i}. Offer ID: {match['id']}")
            print(f"      Route: {match.get('starting_location', 'N/A')} → {match.get('destination', 'N/A')}")
            print(f"      Departure: {match['departure_datetime']}")
            print(f"      Available seats: {match['seats_available']}")
            print(f"      Time difference: {match.get('time_difference_minutes', 'N/A')} minutes")
            print(f"      Match score: {match.get('match_score', 'N/A'):.1f}")
            
            # Show proximity info if available
            if 'pickup_proximity_km' in match:
                print(f"      Pickup proximity: {match['pickup_proximity_km']}km")
                print(f"      Destination proximity: {match['destination_proximity_km']}km")
                print(f"      Max detour allowed: {match['max_detour_km']}km")
    else:
        print(f"\n❌ No matching offers found")

def demo_algorithm_comparison():
    """
    Demonstrate comparison between time-based and proximity-based algorithms.
    """
    print(f"\n🆚 Algorithm Comparison Demo")
    print("=" * 50)
    
    requests, _ = get_all_requests_and_offers()
    
    if not requests:
        print("❌ No requests available for comparison")
        return
    
    matcher = RideMatcher()
    test_request = requests[0]
    
    # Compare algorithms
    comparison = matcher.compare_algorithms(test_request)
    
    if comparison:
        print(f"\n📊 Comparison Summary:")
        print(f"   Time-based matches: {comparison['time_count']}")
        print(f"   Proximity-based matches: {comparison['proximity_count']}")
        
        # Analyze the difference
        if comparison['proximity_count'] < comparison['time_count']:
            print(f"   📍 Proximity filtering eliminated {comparison['time_count'] - comparison['proximity_count']} offers that were too far away")
        elif comparison['proximity_count'] == comparison['time_count']:
            print(f"   ✅ All time-based matches were within proximity range")
        else:
            print(f"   ⚠️ Unexpected: proximity found more matches than time-based")

def demo_individual_matchers():
    """
    Demonstrate using individual matching algorithms directly.
    """
    print(f"\n🔧 Individual Matcher Demo")
    print("=" * 50)
    
    requests, _ = get_all_requests_and_offers()
    
    if not requests:
        print("❌ No requests available")
        return
    
    test_request = requests[0]
    
    # Use time-based matcher directly
    print(f"\n🕐 Time-Based Matcher:")
    time_matcher = TimeBasedMatcher(default_time_window_minutes=60)  # Wider time window
    time_matches = time_matcher.find_matching_offers_for_request(test_request)
    print(f"   Found {len(time_matches)} time-based matches")
    
    # Use proximity-based matcher directly
    print(f"\n🎯 Proximity-Based Matcher:")
    proximity_matcher = ProximityBasedMatcher(default_time_window_minutes=60)
    proximity_matches = proximity_matcher.find_matching_offers_with_proximity(test_request)
    print(f"   Found {len(proximity_matches)} proximity-based matches")

def demo_advanced_features():
    """
    Demonstrate advanced features like fallback and performance analysis.
    """
    print(f"\n🚀 Advanced Features Demo")
    print("=" * 50)
    
    requests, _ = get_all_requests_and_offers()
    
    if not requests:
        print("❌ No requests available")
        return
    
    matcher = RideMatcher()
    test_request = requests[0]
    
    # Smart fallback demo
    print(f"\n🛡️ Smart Fallback Demo:")
    fallback_matches = matcher.get_matches_with_fallback(
        test_request,
        time_window_minutes=30,  # Start narrow
        expand_time_window_on_no_matches=True
    )
    print(f"   Smart fallback found {len(fallback_matches)} matches")
    
    # Performance analysis demo
    print(f"\n⏱️ Performance Analysis Demo:")
    stats = matcher.get_algorithm_performance_stats(test_request)
    print(f"   Performance analysis completed!")
    
    # Batch processing demo (if multiple requests available)
    if len(requests) > 1:
        print(f"\n🚀 Batch Processing Demo:")
        request_ids = [req['id'] for req in requests[:3]]  # First 3 requests
        batch_results = matcher.find_matches_for_multiple_requests(request_ids)
        print(f"   Processed {len(batch_results)} requests in batch")

def interactive_demo():
    """
    Interactive demo allowing user to choose options.
    """
    print(f"\n🎮 Interactive Demo")
    print("=" * 50)
    
    while True:
        print(f"\nChoose an option:")
        print("1. Basic usage demo")
        print("2. Algorithm comparison")
        print("3. Individual matchers demo")
        print("4. Advanced features demo")
        print("5. Run all tests")
        print("6. View database data")
        print("7. Create test data")
        print("8. Help & documentation")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                demo_basic_usage()
            elif choice == "2":
                demo_algorithm_comparison()
            elif choice == "3":
                demo_individual_matchers()
            elif choice == "4":
                demo_advanced_features()
            elif choice == "5":
                run_all_tests()
            elif choice == "6":
                get_all_requests_and_offers()
            elif choice == "7":
                create_test_data()
            elif choice == "8":
                show_help()
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_help():
    """
    Show help and documentation.
    """
    print(f"\n📚 Ride Matching System Help")
    print("=" * 50)
    
    print(f"\n🏗️ System Architecture:")
    print("   📁 config.py         - Database configuration")
    print("   📁 utils.py          - Shared utilities")
    print("   📁 time_matcher.py   - Time-based matching algorithm")
    print("   📁 proximity_matcher.py - Proximity-based matching algorithm")
    print("   📁 ride_matcher.py   - Unified interface")
    print("   📁 tests.py          - Test functions")
    print("   📁 main.py           - This demo file")
    
    print(f"\n🎯 Matching Algorithms:")
    print("   🕐 Time-based: Matches rides by departure time window and seat availability")
    print("   🎯 Proximity-based: Advanced geographic matching using driver detour preferences")
    
    print(f"\n💡 Quick Usage:")
    print("   from ride_matcher import RideMatcher")
    print("   matcher = RideMatcher()")
    print("   matches = matcher.get_best_matches(ride_request)")
    
    print(f"\n🔧 Requirements:")
    print("   - .env file with SUPABASE_URL and SUPABASE_KEY")
    print("   - Supabase database with Ride_Request and Ride_Offer tables")
    print("   - calculate_distance RPC function in Supabase")
    
    print(f"\n🆘 Troubleshooting:")
    print("   - If no matches found: Check if you have test data (option 7)")
    print("   - If distance errors: Verify calculate_distance RPC function exists")
    print("   - If database errors: Check your .env configuration")

def quick_demo():
    """
    Quick demonstration without user interaction.
    """
    print("🚗 Quick Ride Matching Demo")
    print("=" * 40)
    
    try:
        # Check if we have data
        requests, offers = get_all_requests_and_offers()
        
        if not requests or not offers:
            print("📝 No data found - showing test data creation...")
            create_test_data()
            return
        
        # Quick algorithm comparison
        matcher = RideMatcher()
        test_request = requests[0]
        
        print(f"\n🎯 Quick comparison for request {test_request['id']}:")
        comparison = matcher.compare_algorithms(test_request)
        
        if comparison:
            print(f"✅ Time-based: {comparison['time_count']} matches")
            print(f"✅ Proximity-based: {comparison['proximity_count']} matches")
        
        # Show best matches
        best_matches = matcher.get_best_matches(test_request, max_results=3)
        print(f"\n🏆 Top {len(best_matches)} matches:")
        for i, match in enumerate(best_matches, 1):
            score = match.get('match_score', 0)
            time_diff = match.get('time_difference_minutes', 'N/A')
            print(f"   {i}. Offer {match['id']} - Score: {score:.1f}, Time: {time_diff}min")
        
    except Exception as e:
        print(f"❌ Quick demo failed: {e}")
        print("💡 Try running the interactive demo for better error handling")

if __name__ == "__main__":
    print("🚗 Modular Ride Matching System")
    print("=" * 60)
    print("\nThis system uses a modular architecture with separated algorithms:")
    print("🎯 Proximity-based matching (recommended) - Uses driver detour preferences")
    print("🕐 Time-based matching (fallback) - Simple time window matching")
    print("🔄 Smart fallbacks and performance analysis included")
    
    try:
        import sys
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--quick":
                quick_demo()
            elif sys.argv[1] == "--test":
                run_all_tests()
            elif sys.argv[1] == "--help":
                show_help()
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Available options: --quick, --test, --help")
        else:
            # Run interactive demo by default
            interactive_demo()
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Quick start checklist:")
        print("1. ✅ Create .env file with SUPABASE_URL and SUPABASE_KEY")
        print("2. ✅ Ensure Supabase database has Ride_Request and Ride_Offer tables")
        print("3. ✅ Add calculate_distance RPC function to Supabase")
        print("4. ✅ Run option 7 to create test data if needed")
        print("\n💡 For detailed setup, see README.md")