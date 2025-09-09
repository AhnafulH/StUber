#!/usr/bin/env python3
"""
Queue Processor for Ride Requests
Monitors ride_request_queue and processes passenger requests through the matching algorithm
"""
import os
import time
import json
from typing import Dict, Optional, Tuple
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from PassengerDriverMatcher import PassengerDriverMatcher

load_dotenv()

class RideRequestProcessor:
    def __init__(self):
        """Initialize the queue processor"""
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        self.MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA")
        self.QUEUE_NAME = "ride_request_queue"
        
        # Initialize clients
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        self.matcher = PassengerDriverMatcher(
            self.SUPABASE_URL, 
            self.SUPABASE_KEY, 
            self.MAPBOX_TOKEN
        )
        
        print("RideRequestProcessor initialized successfully")
    
    def dequeue_message(self) -> Optional[Dict]:
        """Dequeue a message from the ride_request_queue"""
        try:
            result = self.supabase.rpc('dequeue_full_v2', {
                'queue_name': self.QUEUE_NAME
            }).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error dequeuing message: {e}")
            return None
    
    def parse_departure_time(self, departure_time_str: Optional[str]) -> Optional[datetime]:
        """Parse departure time string to datetime object"""
        if not departure_time_str:
            return None
        
        try:
            # Handle different datetime formats
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    return datetime.strptime(departure_time_str, fmt)
                except ValueError:
                    continue
            
            # Try ISO format parsing
            return datetime.fromisoformat(departure_time_str.replace('Z', '+00:00'))
            
        except Exception as e:
            print(f"Warning: Could not parse departure time '{departure_time_str}': {e}")
            return None
    
    
    def process_ride_request(self, message_data: Dict) -> None:
        """Process a passenger ride request and find matching drivers"""
        try:
            ride_message = message_data['message']
            msg_id = message_data['msg_id']
            
            print(f"\nProcessing message {msg_id}...")
            print(f"Rider ID: {ride_message['request_id']}")
            print(f"Request type: {ride_message.get('request_type', 'request')}")
            # print(f"Pickup: ({ride_message['pickup_longitude']}, {ride_message['pickup_latitude']})")
            # print(f"Destination: ({ride_message['destination_longitude']}, {ride_message['destination_latitude']})")
            print(f"Departure time: {ride_message.get('departure_time', 'Not specified')}")
            
            # Skip if not a ride request
            # if ride_message.get('request_type') != 'request':
            #     print(f"Skipping - not a ride request: {ride_message.get('request_type')}")
            #     return
            
            # Extract coordinates
            pickup_coords = tuple(ride_message['starting_coords'])     # [lng, lat]
            destination_coords = tuple(ride_message['destination_coords'])
            
            # Parse departure time
            departure_time = self.parse_departure_time(ride_message.get('departure_time'))
            
            # Get matching parameters from message or use defaults
            search_radius_km = ride_message.get('search_radius_km', 10)
            time_window_hours = ride_message.get('time_window_hours', 2)
            # max_price = ride_message.get('max_price')
            
            print(f"Search parameters:")
            print(f"  Search radius: {search_radius_km}km")
            print(f"  Time window: ±{time_window_hours}h")
            
            # Find matching drivers using the PassengerDriverMatcher
            print("Finding matching drivers...")
            
            results = self.matcher.find_and_create_matches(
                rider_id=ride_message['request_id'],
                passenger_pickup=pickup_coords,
                passenger_destination=destination_coords,
                departure_time=departure_time,
                search_radius_km=search_radius_km,
                time_window_hours=time_window_hours,
                use_optimized=True  # Use the optimized batch processing
            )
            
            if results:
                self.handle_matching_results(ride_message, results)
            else:
                print("No matching results returned")
                
        except Exception as e:
            print(f"Error processing ride request: {e}")
    
    def handle_matching_results(self, ride_message: Dict, results: Dict) -> None:
        """Handle the results of driver matching"""
        try:
            if not results.get('success', False):
                print(f"MATCHING FAILED: {results.get('error', 'Unknown error')}")
                return
            
            analysis_stats = results.get('analysis_results', {}).get('analysis_stats', {})
            viable_drivers = results.get('viable_drivers', [])
            matches_created = results.get('matches_created', 0)
            
            print(f"\nMATCHING RESULTS:")
            print(f"  Rider ID: {ride_message['request_id']}")
            print(f"  Total drivers checked: {analysis_stats.get('total_drivers', 0)}")
            print(f"  Spatially filtered: {analysis_stats.get('spatially_filtered', 0)}")
            print(f"  Final viable drivers: {analysis_stats.get('final_viable', 0)}")
            print(f"  Matches created in DB: {matches_created}")
            
            if analysis_stats.get('total_drivers', 0) > 0:
                print(f"  Conversion rates:")
                print(f"    Spatial filter: {analysis_stats.get('spatial_conversion', 0)}%")
                print(f"    Corridor analysis: {analysis_stats.get('corridor_conversion', 0)}%")
                print(f"    Overall: {analysis_stats.get('overall_conversion', 0)}%")
            
            if viable_drivers:
                print(f"\nTOP MATCHING DRIVERS:")
                
                # Show top 5 drivers
                for i, driver in enumerate(viable_drivers[:5], 1):
                    driver_info = driver['driver_info']
                    corridor_analysis = driver.get('corridor_analysis', {})
                    
                    print(f"  {i}. Driver ID: {driver['driver_id']} (DB ID: {driver_info['database_id']})")
                    print(f"     Distance: {driver['min_distance_meters']/1000:.1f}km")
                    print(f"     Max detour: {driver_info['max_detour_km']}km")
                    print(f"     Direction aligned: {corridor_analysis.get('direction_aligned', False)}")
                    print(f"     Match score: {driver.get('match_score', 'N/A')}")
                
                if matches_created > 0:
                    print(f"\n✅ Successfully created {matches_created} ride matches in database")
                
            else:
                print("  No viable drivers found")
                self.handle_no_matches(ride_message)
                
        except Exception as e:
            print(f"Error handling matching results: {e}")
    
    
    
    def delete_queue_message(self, message_id: int) -> bool:
        """Delete a specific message from the queue"""
        try:
            result = self.supabase.rpc('delete_queue_message', {
                'queue_name': self.QUEUE_NAME,
                'message_id': message_id
            }).execute()
            
            if result.data:
                print(f"✅ Successfully deleted message {message_id} from queue")
                return True
            else:
                print(f"❌ Failed to delete message {message_id} from queue")
                return False
                
        except Exception as e:
            print(f"Error deleting message {message_id}: {e}")
            return False
    
    def process_and_delete_message(self, message: Dict) -> None:
        """Process a message and delete it only if processing succeeds"""
        msg_id = message['msg_id']
        
        try:
            print(f"\nDequeued message ID: {msg_id}")
            
            # Process the ride request
            self.process_ride_request(message)
            
            # Only delete if processing completed without exceptions
            self.delete_queue_message(msg_id)
            
        except Exception as e:
            print(f"❌ Processing failed for message {msg_id}: {e}")
            print("Message left in queue for potential retry")

    def run_continuous(self, poll_interval: int = 5) -> None:
        """Run continuous queue processing"""
        print(f"\nStarting continuous ride request processing (polling every {poll_interval}s)")
        print("Press Ctrl+C to stop")
        print("=" * 70)
        
        try:
            while True:
                message = self.dequeue_message()
                
                if message:
                    self.process_and_delete_message(message)
                else:
                    print(".", end="", flush=True)  # Show activity when queue is empty
                
                time.sleep(poll_interval)
                
        except KeyboardInterrupt:
            print("\nStopping ride request processor...")
        except Exception as e:
            print(f"Error in continuous processing: {e}")
    

def main():
    """Main function"""
    print("Ride Request Queue Processor")
    print("=" * 60)
    
    # Initialize processor
    try:
        processor = RideRequestProcessor()
    except Exception as e:
        print(f"Failed to initialize processor: {e}")
        return
    
    # Choose mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        processor.run_single()
    else:
        processor.run_continuous()

if __name__ == "__main__":
    main()