import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Get all data from a table
try:
    response = supabase.table('Ride_Offer').select('*').execute()
    
    if response.data:
        print(f"Found {len(response.data)} records")
        for record in response.data:
            print(record)
    else:
        print("No data found")
        
except Exception as e:
    print(f"Error: {e}")

try:
    response = supabase.table('Ride_Request').select('*').execute()
    
    if response.data:
        print(f"Found {len(response.data)} records")
        for record in response.data:
            print(record)
    else:
        print("No data found")
        
except Exception as e:
    print(f"Error: {e}")