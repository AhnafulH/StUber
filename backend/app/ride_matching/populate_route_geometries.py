#!/usr/bin/env python3
"""
Populate route_geometry column in Ride_Offer and Ride_Request tables
using Mapbox Directions API
"""
import requests
import time
import json
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

class RouteGeometryPopulator:
    def __init__(self):
        """Initialize the route geometry populator"""
        self.SUPABASE_URL = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        self.MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
        self.MAPBOX_BASE_URL = "https://api.mapbox.com/directions/v5"
        
        # Initialize Supabase client
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        
        print("RouteGeometryPopulator initialized successfully")
    
    def get_route_from_mapbox(self, start_lon, start_lat, end_lon, end_lat):
        """Get route geometry from Mapbox Directions API"""
        
        coords_str = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{self.MAPBOX_BASE_URL}/mapbox/driving-traffic/{coords_str}"
        
        params = {
            "access_token": self.MAPBOX_TOKEN,
            "geometries": "geojson",
            "overview": "full"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == "Ok" and data.get("routes"):
                return data["routes"][0]["geometry"]
            else:
                print(f"Mapbox API error: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def get_rows_without_geometry(self, table_name):
        """Get rows that don't have route_geometry populated"""
        
        try:
            # Query rows where route_geometry is null or empty
            result = self.supabase.table(table_name).select("*").is_("route_geometry", "null").execute()
            
            if result.data:
                print(f"Found {len(result.data)} rows without geometry in {table_name}")
                return result.data
            else:
                print(f"No rows without geometry found in {table_name}")
                return []
                
        except Exception as e:
            print(f"Error querying {table_name}: {e}")
            return []
    
    def update_row_geometry(self, table_name, row_id, geometry):
        """Update a single row with route geometry"""
        
        try:
            result = self.supabase.table(table_name).update({
                "route_geometry": geometry
            }).eq("id", row_id).execute()
            
            if result.data:
                return True
            else:
                print(f"Failed to update {table_name} row {row_id}")
                return False
                
        except Exception as e:
            print(f"Error updating {table_name} row {row_id}: {e}")
            return False
    
    def process_table(self, table_name, coord_fields):
        """Process a single table to populate route geometries"""
        
        print(f"\n{'='*50}")
        print(f"Processing {table_name}")
        print(f"{'='*50}")
        
        # Get rows without geometry
        rows = self.get_rows_without_geometry(table_name)
        
        if not rows:
            return
        
        successful_updates = 0
        failed_updates = 0
        
        for i, row in enumerate(rows, 1):
            print(f"Processing row {i}/{len(rows)}: ID {row['id']}")
            
            # Extract coordinates
            start_lon = row.get(coord_fields['start_lon'])
            start_lat = row.get(coord_fields['start_lat'])
            end_lon = row.get(coord_fields['end_lon'])
            end_lat = row.get(coord_fields['end_lat'])
            
            # Validate coordinates
            if not all([start_lon, start_lat, end_lon, end_lat]):
                print(f"  Skipping - missing coordinates: {start_lon}, {start_lat}, {end_lon}, {end_lat}")
                failed_updates += 1
                continue
            
            # Get route geometry from Mapbox
            geometry = self.get_route_from_mapbox(start_lon, start_lat, end_lon, end_lat)
            
            if geometry:
                # Update database
                if self.update_row_geometry(table_name, row['id'], geometry):
                    print(f"  ✅ Successfully updated row {row['id']}")
                    successful_updates += 1
                else:
                    print(f"  ❌ Failed to update database for row {row['id']}")
                    failed_updates += 1
            else:
                print(f"  ❌ Failed to get geometry from Mapbox for row {row['id']}")
                failed_updates += 1
            
            # Rate limiting - respect Mapbox API limits
            time.sleep(0.1)  # 100ms delay between requests
            
            # Progress update every 10 rows
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(rows)} rows processed")
        
        print(f"\n{table_name} Summary:")
        print(f"  ✅ Successful updates: {successful_updates}")
        print(f"  ❌ Failed updates: {failed_updates}")
        print(f"  📊 Success rate: {successful_updates/(successful_updates+failed_updates)*100:.1f}%")
    
    def populate_all_geometries(self):
        """Populate route geometries for both tables"""
        
        print("Starting route geometry population for all tables")
        print(f"Using Mapbox token: {self.MAPBOX_TOKEN[:20]}...")
        
        # Define coordinate field mappings for each table
        table_configs = {
            "Ride_Offer": {
                "start_lon": "starting_longitude",
                "start_lat": "starting_latitude", 
                "end_lon": "destination_longitude",
                "end_lat": "destination_latitude"
            },
            "Ride_Request": {
                "start_lon": "starting_longitude",
                "start_lat": "starting_latitude",
                "end_lon": "destination_longitude", 
                "end_lat": "destination_latitude"
            }
        }
        
        total_successful = 0
        total_failed = 0
        
        # Process each table
        for table_name, coord_fields in table_configs.items():
            try:
                self.process_table(table_name, coord_fields)
            except Exception as e:
                print(f"Error processing {table_name}: {e}")
        
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        print("Route geometry population complete!")
        print("Check the individual table summaries above for detailed results.")

def main():
    """Main function"""
    print("Route Geometry Populator")
    print("=" * 50)
    print("This script will populate route_geometry columns using Mapbox API")
    print("Make sure you have valid coordinates in your tables before running.")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed? (y/N): ")
    if response.lower() != 'y':
        print("Aborted by user")
        return
    
    # Initialize and run populator
    try:
        populator = RouteGeometryPopulator()
        populator.populate_all_geometries()
    except Exception as e:
        print(f"Failed to initialize populator: {e}")
        return

if __name__ == "__main__":
    main()