from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import List, Dict, Any



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Get all data from a table
# try:
#     response = supabase.table('Ride_Offer').select('*').execute()
    
#     if response.data:
#         print(f"Found {len(response.data)} records")
#         for record in response.data:
#             print(record)
#     else:
#         print("No data found")
        
# except Exception as e:
#     print(f"Error: {e}")

# try:
#     response = supabase.table('Ride_Request').select('*').execute()
    
#     if response.data:
#         print(f"Found {len(response.data)} records")
#         for record in response.data:
#             print(record)
#     else:
#         print("No data found")
        
# except Exception as e:
#     print(f"Error: {e}")


def find_matching_drivers(commuter_departure_time: datetime, time_window_minutes: int = 45) -> List[Dict[Any, Any]]:
    """
    Find drivers whose departure time is within the specified time window of the commuter's departure time.
    
    Args:
        commuter_departure_time: The commuter's desired departure time
        time_window_minutes: Time window in minutes (default: 45)
    
    Returns:
        List of matching drivers
    """
    
    # Calculate time range
    start_time = commuter_departure_time - timedelta(minutes=time_window_minutes)
    end_time = commuter_departure_time + timedelta(minutes=time_window_minutes)
    
    # Convert to ISO format for Supabase
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()
    
    try:
        # Query drivers within the time window
        response = supabase.table('drivers').select('*').gte('departure_time', start_time_iso).lte('departure_time', end_time_iso).execute()
        
        matching_drivers = response.data
        print(f"Found {len(matching_drivers)} drivers within ±{time_window_minutes} minutes")
        
        return matching_drivers
        
    except Exception as e:
        print(f"Error querying drivers: {e}")
        return []

def find_matching_drivers_by_date_and_time(commuter_departure_datetime: str, time_window_minutes: int = 45) -> List[Dict[Any, Any]]:
    """
    Find matching drivers using a datetime string input.
    
    Args:
        commuter_departure_datetime: Departure datetime as string (e.g., "2024-01-15 14:30:00")
        time_window_minutes: Time window in minutes (default: 45)
    
    Returns:
        List of matching drivers
    """
    
    # Parse the datetime string
    try:
        commuter_time = datetime.fromisoformat(commuter_departure_datetime)
    except ValueError:
        print(f"Invalid datetime format: {commuter_departure_datetime}")
        return []
    
    return find_matching_drivers(commuter_time, time_window_minutes)

def get_detailed_driver_matches(commuter_departure_time: datetime, time_window_minutes: int = 45) -> List[Dict[Any, Any]]:
    """
    Get detailed driver matches with additional filtering and information.
    
    Args:
        commuter_departure_time: The commuter's desired departure time
        time_window_minutes: Time window in minutes (default: 45)
    
    Returns:
        List of matching drivers with additional details
    """
    
    start_time = commuter_departure_time - timedelta(minutes=time_window_minutes)
    end_time = commuter_departure_time + timedelta(minutes=time_window_minutes)
    
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()
    
    try:
        # Query with additional filters (e.g., available status, capacity)
        response = (supabase.table('drivers')
                   .select('id, user_id, departure_time, origin, destination, available_seats, status, vehicle_info')
                   .gte('departure_time', start_time_iso)
                   .lte('departure_time', end_time_iso)
                   .eq('status', 'available')  # Only available drivers
                   .gt('available_seats', 0)   # Only drivers with available seats
                   .execute())
        
        matching_drivers = response.data
        
        # Add time difference information
        for driver in matching_drivers:
            driver_time = datetime.fromisoformat(driver['departure_time'])
            time_diff = abs((driver_time - commuter_departure_time).total_seconds() / 60)
            driver['time_difference_minutes'] = round(time_diff, 1)
        
        # Sort by time difference (closest matches first)
        matching_drivers.sort(key=lambda x: x['time_difference_minutes'])
        
        print(f"Found {len(matching_drivers)} available drivers within ±{time_window_minutes} minutes")
        
        return matching_drivers
        
    except Exception as e:
        print(f"Error querying drivers: {e}")
        return []

# Example usage and testing
if __name__ == "__main__":
    
    # Test with a sample commuter departure time
    commuter_time_str = "2024-01-15 14:30:00"
    commuter_time = datetime.fromisoformat(commuter_time_str)
    
    print(f"Searching for drivers for commuter departure time: {commuter_time}")
    print(f"Time window: ±45 minutes ({commuter_time - timedelta(minutes=45)} to {commuter_time + timedelta(minutes=45)})")
    print("-" * 50)
    
    # Method 1: Basic matching
    basic_matches = find_matching_drivers(commuter_time)
    print(f"\nBasic matches: {len(basic_matches)}")
    for driver in basic_matches:
        print(f"Driver ID: {driver.get('id')}, Departure: {driver.get('departure_time')}")
    
    print("-" * 50)
    
    # Method 2: Using string input
    string_matches = find_matching_drivers_by_date_and_time(commuter_time_str)
    print(f"\nString input matches: {len(string_matches)}")
    
    print("-" * 50)
    
    # Method 3: Detailed matching with additional filters
    detailed_matches = get_detailed_driver_matches(commuter_time)
    print(f"\nDetailed matches: {len(detailed_matches)}")
    for driver in detailed_matches:
        print(f"Driver ID: {driver.get('id')}, "
              f"Departure: {driver.get('departure_time')}, "
              f"Time diff: {driver.get('time_difference_minutes')} min, "
              f"Available seats: {driver.get('available_seats')}")