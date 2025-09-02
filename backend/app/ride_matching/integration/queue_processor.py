#!/usr/bin/env python3
"""
Queue Processor for Ride Matching
Monitors ride_matching queue and processes driver offers through the matching algorithm
"""
import os
import time
import json
from typing import Dict, Optional, Tuple
from supabase import create_client
from dotenv import load_dotenv
from direction_aware_corridor_matching import DirectionAwareCorridorMatching

load_dotenv()

class RideMatchingProcessor:
    def __init__(self):
        """Initialize the queue processor"""
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        self.MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
        self.QUEUE_NAME = "ride_matching"
        
        # Initialize clients
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        self.matcher = DirectionAwareCorridorMatching(
            self.SUPABASE_URL, 
            self.SUPABASE_KEY, 
            self.MAPBOX_TOKEN
        )
        
        print("RideMatchingProcessor initialized successfully")
    
    def dequeue_message(self) -> Optional[Dict]:
        """Dequeue a message from the ride_matching queue"""
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
    
    def get_ride_coordinates(self, ride_id: int) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Get start/end coordinates for a ride from the database
        Returns: ((start_lng, start_lat), (end_lng, end_lat)) or None
        """
        try:
            # Query the ride details from your rides table
            # Assuming you have a table with ride coordinates
            result = self.supabase.table('Ride_Offer').select(
                'starting_longitude, starting_latitude, destination_longitude, destination_latitude'
            ).eq('id', ride_id).execute()
            
            if result.data and len(result.data) > 0:
                ride = result.data[0]
                start_coords = (ride['starting_longitude'], ride['starting_latitude'])
                end_coords = (ride['destination_longitude'], ride['destination_latitude'])
                return start_coords, end_coords
            else:
                print(f"No coordinates found for ride ID {ride_id}")
                return None
                
        except Exception as e:
            print(f"Error getting ride coordinates: {e}")
            return None
    
    def process_ride_offer(self, message_data: Dict) -> None:
        """Process a driver ride offer and find matching passengers"""
        try:
            ride_message = message_data['message']
            msg_id = message_data['msg_id']
            
            print(f"\nProcessing message {msg_id}...")
            print(f"Ride ID: {ride_message['ride_id']}")
            print(f"Ride type: {ride_message['ride_type']}")
            print(f"Start: {ride_message['starting_location']}")
            print(f"End: {ride_message['destination']}")
            print(f"Seats available: {ride_message['seats_available']}")
            
            # Skip if not a driver offer
            if ride_message.get('ride_type') != 'offer':
                print(f"Skipping - not a driver offer: {ride_message.get('ride_type')}")
                return
            
            # Get coordinates for this ride
            coordinates = self.get_ride_coordinates(ride_message['ride_id'])
            if not coordinates:
                print("Could not get coordinates for this ride")
                return
            
            start_coords, end_coords = coordinates
            print(f"Driver route: {start_coords} -> {end_coords}")
            
            # Get route from Mapbox
            print("Getting route from Mapbox...")
            route_response = self.matcher.get_route(start_coords, end_coords)
            
            if not route_response or route_response.get("code") != "Ok":
                print(f"Failed to get route from Mapbox: {route_response}")
                return
            
            route = route_response["routes"][0]
            route_geometry = route["geometry"]
            
            print(f"Route: {route['distance']/1000:.1f}km, {route['duration']/60:.1f}min")
            
            # Use driver's preferred detour distance from queue message (convert km to meters)
            buffer_distance_km = ride_message.get('max_detour_distance', 3)  # Default to 3km if not specified
            buffer_distance = buffer_distance_km * 1000  # Convert kilometers to meters
            print(f"Using detour distance: {buffer_distance_km}km ({buffer_distance}m)")
            
            # Find matching passengers
            print("Finding matching passengers...")
            results = self.matcher.find_matching_passengers_from_db(
                route_geometry=route_geometry,
                buffer_distance_meters=buffer_distance,  # Use driver's preference
                direction_tolerance=0.05      # 5% tolerance
            )
            
            if results:
                self.handle_matching_results(ride_message, results)
            else:
                print("No matching results returned")
                
        except Exception as e:
            print(f"Error processing ride offer: {e}")
    
    def handle_matching_results(self, ride_message: Dict, results: Dict) -> None:
        """Handle the results of passenger matching"""
        try:
            stats = results['stats']
            eligible_passengers = results.get('eligible_passengers', [])
            
            print(f"\nMATCHING RESULTS:")
            print(f"  Driver ID: {ride_message['ride_id']}")
            print(f"  Total passengers analyzed: {stats['total_points']}")
            print(f"  Passengers in corridor: {stats['points_both_in_corridor']}")
            print(f"  Direction-aligned: {stats['direction_aligned_points']}")
            print(f"  Final eligible matches: {stats['final_matches']}")
            
            if eligible_passengers:
                print(f"\nFOUND {len(eligible_passengers)} MATCHING PASSENGERS:")
                
                for i, match in enumerate(eligible_passengers, 1):
                    passenger_info = match['passenger_info']
                    print(f"  {i}. Passenger ID: {match['passenger_id']}")
                    print(f"     Coordinates: {match['pickup_coords']} -> {match['dropoff_coords']}")
                    print(f"     Request time: {passenger_info.get('request_time', 'N/A')}")
                
                # Here you could:
                # 1. Send notifications to the driver about potential passengers
                # 2. Store matches in a database table
                # 3. Trigger further business logic
                self.store_matches(ride_message['ride_id'], eligible_passengers)
                
            else:
                print("  No eligible passengers found")
                
        except Exception as e:
            print(f"Error handling matching results: {e}")
    
    def store_matches(self, driver_ride_id: int, matches: list) -> None:
        """Store matching results in Ride_Match table"""
        try:
            print(f"\nStoring {len(matches)} matches in database...")
            
            for match in matches:
                match_record = {
                    'driver_id': driver_ride_id,  # ride_offer id becomes driver_id
                    'rider_id': match['passenger_id'],  # passenger id becomes rider_id
                    'price': None,  # Will be set later during negotiation
                    'driver_accept': None,  # Will be set when driver responds
                    'rider_accept': None   # Will be set when rider responds
                }
                
                # Insert into Ride_Match table
                result = self.supabase.table('Ride_Match').insert(match_record).execute()
                
                if result.data:
                    match_id = result.data[0]['id']
                    print(f"  ✅ Stored match ID {match_id}: Driver {driver_ride_id} <-> Rider {match['passenger_id']}")
                else:
                    print(f"  ❌ Failed to store match: Driver {driver_ride_id} <-> Rider {match['passenger_id']}")
            
            print(f"Successfully stored {len(matches)} ride matches")
                
        except Exception as e:
            print(f"Error storing matches: {e}")
    
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
            
            # Process the ride offer
            self.process_ride_offer(message)
            
            # Only delete if processing completed without exceptions
            self.delete_queue_message(msg_id)
            
        except Exception as e:
            print(f"❌ Processing failed for message {msg_id}: {e}")
            print("Message left in queue for potential retry")

    def run_continuous(self, poll_interval: int = 5) -> None:
        """Run continuous queue processing"""
        print(f"\nStarting continuous queue processing (polling every {poll_interval}s)")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                message = self.dequeue_message()
                
                if message:
                    self.process_and_delete_message(message)
                else:
                    print(".", end="", flush=True)  # Show activity when queue is empty
                
                time.sleep(poll_interval)
                
        except KeyboardInterrupt:
            print("\nStopping queue processor...")
        except Exception as e:
            print(f"Error in continuous processing: {e}")
    
    def run_single(self) -> None:
        """Process a single message from queue"""
        print("\nProcessing single message from queue...")
        print("=" * 50)
        
        message = self.dequeue_message()
        
        if message:
            self.process_and_delete_message(message)
        else:
            print("No messages in queue")

def main():
    """Main function"""
    print("Ride Matching Queue Processor")
    print("=" * 50)
    
    # Initialize processor
    try:
        processor = RideMatchingProcessor()
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