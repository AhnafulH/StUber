import os
import time
from supabase import create_client
from typing import Dict, Optional
from dotenv import load_dotenv
from price_calculator import FuelPrice
from price_calculator import calculate_price

load_dotenv()

class PriceProcessor:
    def __init__(self):
        """Initialize the queue processor"""
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        self.QUEUE_NAME = "cost_calculator_queue"

        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)

    def dequeue_message(self) -> Optional[Dict]:
        try:
            result = self.supabase.rpc('dequeue_full_v2', {
                'queue_name': self.QUEUE_NAME
            }).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return None

        except Exception as e:
            print(f"Error de-queueing message: {e}")
            return None

    def process_message(self, _message: Dict) -> None:
        message = _message['message']
        match_id = message['match_id']
        rider_id = message['rider_id']
        driver_id = message['driver_id']

        try:
            result = self.supabase.table('Ride_Offer').select('route_geometry').eq('id', driver_id).execute()

            if len(result.data) <= 0:
                print("Something went wrong, no matches found")

            waypoints = result.data[0]['route_geometry']['coordinates']

            result = self.supabase.table('Ride_Request').select(
                'starting_longitude', 'starting_latitude', 'destination_longitude', 'destination_latitude').eq(
                'id', rider_id).execute()

            source = (result.data[0]['starting_longitude'], result.data[0]['starting_latitude'])
            destination = (result.data[0]['destination_longitude'], result.data[0]['destination_latitude'])

            price, detour_distance, detour_duration = calculate_price(waypoints, source, destination, FuelPrice(2, 1/6))

            self.supabase.table('Ride_Match').update({
                'price': price,
                'detour_distance': detour_distance,
                'detour_duration': detour_duration
            }).eq('id', match_id).execute()

        except Exception as e:
            print(f"Error querying supabase: {e}")
            return None

    def delete_message(self, message_id: int):
        try:
            result = self.supabase.rpc('delete_queue_message', {
                'queue_name': self.QUEUE_NAME,
                'message_id': message_id
            }).execute()
        except Exception as e:
            print(f"Error deleting message {message_id}: {e}")

    def run(self, sleep_seconds: float = 0.5):
        try:
            while True:
                message = self.dequeue_message()
                if message:
                    print("There's a message on the queue")
                    self.process_message(message) # TODO: if successful then delete
                    message_id = message['msg_id']
                    self.delete_message(message_id)
                else:
                    print(".", end="", flush=True)

                time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            print("\nStopping queue processor...")
        except Exception as e:
            print(f"Error in processing: {e}")

if __name__ == "__main__":
    processor = PriceProcessor()
    processor.run()
