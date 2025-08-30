import os
import time
import signal
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
# supabase_url = os.environ.get("SUPABASE_URL")
# supabase_key = os.environ.get("SUPABASE_KEY")
supabase_url = "https://tzxmancfyapahphvzwcw.supabase.co"
supabase_key = "sb_secret_G1w1RKJDm2MJmkdsC-lzyw_Dgw223aJ"
supabase: Client = create_client(supabase_url, supabase_key)

# Global flag for signal handling
wake_up = False


def signal_handler(signum, frame):
    global wake_up
    wake_up = True


def process_matches():
    # Fetch all matches where both parties accepted
    response = supabase.table('Ride_Match') \
        .select('*') \
        .eq('driver_accept', True) \
        .eq('rider_accept', True) \
        .execute()

    matches = response.data
    print(f"Found {len(matches)} matches to process")

    # Process each match
    for match in matches:
        try:
            # Insert into Ride_Confirmed table
            supabase.table('Ride_Confirmed').insert({
                'driver_id': match['driver_id'],
                'rider_id': match['rider_id'],
                'price': match['price']
            }).execute()

            print(f"Created confirmed ride for match ID {match['id']}")

        except Exception as e:
            print(f"Error processing match {match['id']}: {str(e)}")


def main():
    # Set up signal handler
    signal.signal(signal.SIGUSR1, signal_handler)

    print(f"Daemon PID: {os.getpid()}")
    print("Waiting for signal SIGUSR1 to wake up...")

    while True:
        global wake_up
        if wake_up:
            print("Woken up! Processing matches...")
            process_matches()
            wake_up = False
            print("Processing complete. Going back to sleep...")
        time.sleep(0.1)  # Small delay to prevent CPU overload


if __name__ == "__main__":
    main()