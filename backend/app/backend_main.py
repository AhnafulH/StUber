import logging

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase client
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
backend = FastAPI()


# Request models (without ID - for creating new records)
class RideRequestCreate(BaseModel):
    uuid: str = Field(..., description="Unique User ID")
    starting_location: str = Field(..., description="Starting location name")
    destination: str = Field(..., description="Destination location name")
    seats_needed: int = Field(..., ge=1, le=8, description="Number of available seats")
    starting_latitude: float = Field(..., ge=-90, le=90, description="Starting latitude")
    starting_longitude: float = Field(..., ge=-180, le=180, description="Starting longitude")
    destination_latitude: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_longitude: float = Field(..., ge=-180, le=180, description="Destination longitude")
    departure_datetime: datetime = Field(..., description="When the ride departs")


class RideOfferCreate(BaseModel):
    uuid: str = Field(..., description="Unique User ID")
    starting_location: str = Field(..., description="Starting location name")
    destination: str = Field(..., description="Destination location name")
    seats_available: int = Field(..., ge=1, le=8, description="Number of seats needed")
    starting_latitude: float = Field(..., ge=-90, le=90, description="Starting latitude")
    starting_longitude: float = Field(..., ge=-180, le=180, description="Starting longitude")
    destination_latitude: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_longitude: float = Field(..., ge=-180, le=180, description="Destination longitude")
    departure_datetime: datetime = Field(..., description="When the ride is needed")
    max_detour_distance: float = Field(..., ge=0, description="Maximum detour distance in km")


# Response models (with ID - what gets returned)
class RideRequest(BaseModel):
    id: int
    uuid: str
    starting_location: str
    destination: str
    seats_needed: int
    starting_latitude: float
    starting_longitude: float
    destination_latitude: float
    destination_longitude: float
    departure_datetime: datetime
    created_at: Optional[datetime] = None


class RideOffer(BaseModel):
    id: int
    uuid: str
    starting_location: str
    destination: str
    seats_available: int
    starting_latitude: float
    starting_longitude: float
    destination_latitude: float
    destination_longitude: float
    departure_datetime: datetime
    max_detour_distance: float
    created_at: Optional[datetime] = None

class RideMatchQuery(BaseModel):
    uuid: str

class RideMatchResponse(BaseModel):
    driver_name: str
    price: float
    # departure_datetime: datetime

@backend.post("/ride-requests", response_model=RideRequest)
def create_ride_request(ride_request: RideRequestCreate):
    """
    Create a new ride request and insert it into Supabase
    """
    try:
        print(f"Received a request for a ride from {ride_request.starting_location} to {ride_request.destination}")
        print(f"Seats needed: {ride_request.seats_needed}, Departure: {ride_request.departure_datetime}")

        # Convert Pydantic model to dictionary for Supabase
        ride_data = ride_request.model_dump()

        # Convert datetime to ISO string for Supabase
        ride_data['departure_datetime'] = ride_request.departure_datetime.isoformat()

        # Insert into Supabase
        result = supabase.table('Ride_Request').insert(ride_data).execute()

        # Check if insertion was successful
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create ride request")

        # Get the inserted record (includes the auto-generated ID)
        created_ride = result.data[0]

        # Convert back to datetime object
        created_ride['departure_datetime'] = datetime.fromisoformat(
            created_ride['departure_datetime'].replace('Z', '+00:00'))

        print(f"Successfully created ride request with ID: {created_ride['id']}")

        return RideRequest(**created_ride)

    except Exception as e:
        print(f"Error creating ride request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@backend.post("/ride-offers", response_model=RideOffer)
def create_ride_offer(ride_offer: RideOfferCreate):
    """
    Create a new ride offer and insert it into Supabase
    """
    try:
        print(f"Received an offer for a ride from {ride_offer.starting_location} to {ride_offer.destination}")
        print(f"Seats available: {ride_offer.seats_available}, Departure: {ride_offer.departure_datetime}")

        # Convert Pydantic model to dictionary for Supabase
        offer_data = ride_offer.model_dump()

        # Convert datetime to ISO string for Supabase
        offer_data['departure_datetime'] = ride_offer.departure_datetime.isoformat()

        # Insert into Supabase
        result = supabase.table('Ride_Offer').insert(offer_data).execute()

        # Check if insertion was successful
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create ride offer")

        # Get the inserted record (includes the auto-generated ID)
        created_offer = result.data[0]

        # Convert back to datetime object
        created_offer['departure_datetime'] = datetime.fromisoformat(
            created_offer['departure_datetime'].replace('Z', '+00:00'))

        print(f"Successfully created ride offer with ID: {created_offer['id']}")

        return RideOffer(**created_offer)

    except Exception as e:
        print(f"Error creating ride offer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@backend.get("/ride-matches", response_model=List[RideMatchResponse])
def get_ride_matches(uuid: str = Query(..., description="User UUID to find ride matches for")):
    """
    Get all ride matches for a specific user.

    Process:
    1. Find all ride request IDs for the given user UUID
    2. Find all matches for those ride requests with driver IDs and prices
    3. Get driver UUIDs from the ride offers
    4. Get driver full names from profiles
    5. Return combined driver names and prices
    """
    try:
        logging.info(f"🔍 Finding ride matches for UUID: {uuid}")

        # Step 1: Get all ride request IDs for this user
        ride_requests_result = supabase.table('Ride_Request').select('id').eq('uuid', uuid).execute()

        if not ride_requests_result.data:
            logging.info(f"❌ No ride requests found for UUID: {uuid}")
            return []  # Return empty list if no ride requests found

        ride_request_ids = [request['id'] for request in ride_requests_result.data]
        logging.info(f"📋 Found {len(ride_request_ids)} ride requests: {ride_request_ids}")

        # Step 2: Get all matches for these ride requests (driver_id and price)
        # Note: Using 'in_' filter to match multiple IDs
        ride_matches_result = supabase.table('Ride_Match').select('driver_id, price').in_('id',
                                                                                          ride_request_ids).execute()

        if not ride_matches_result.data:
            logging.info(f"❌ No ride matches found for ride requests: {ride_request_ids}")
            return []  # Return empty list if no matches found

        # Extract driver IDs and create a mapping of driver_id to price
        driver_prices = {}
        driver_ids = []
        for match in ride_matches_result.data:
            driver_id = match['driver_id']
            price = match['price']
            driver_ids.append(driver_id)
            driver_prices[driver_id] = price

        logging.info(f"🚗 Found {len(driver_ids)} driver matches: {driver_ids}")
        logging.info(f"💰 Driver prices: {driver_prices}")

        # Step 3: Get driver UUIDs from Ride_Offer table
        ride_offers_result = supabase.table('Ride_Offer').select('id, uuid').in_('id', driver_ids).execute()

        if not ride_offers_result.data:
            logging.info(f"❌ No ride offers found for driver IDs: {driver_ids}")
            return []

        # Create mapping of driver_id to driver_uuid
        driver_uuid_mapping = {}
        driver_uuids = []
        for offer in ride_offers_result.data:
            driver_id = offer['id']
            driver_uuid = offer['uuid']
            driver_uuid_mapping[driver_id] = driver_uuid
            driver_uuids.append(driver_uuid)

        logging.info(f"👥 Driver UUID mapping: {driver_uuid_mapping}")

        # Step 4: Get full names from profiles table
        profiles_result = supabase.table('profiles').select('uuid, full_name').in_('uuid', driver_uuids).execute()

        if not profiles_result.data:
            logging.info(f"❌ No profiles found for driver UUIDs: {driver_uuids}")
            return []

        # Create mapping of uuid to full_name
        uuid_name_mapping = {}
        for profile in profiles_result.data:
            uuid_name_mapping[profile['uuid']] = profile['full_name']

        logging.info(f"📇 UUID to name mapping: {uuid_name_mapping}")

        # Step 5: Combine everything into response
        ride_matches = []
        for driver_id in driver_ids:
            if driver_id in driver_uuid_mapping:
                driver_uuid = driver_uuid_mapping[driver_id]
                if driver_uuid in uuid_name_mapping:
                    driver_name = uuid_name_mapping[driver_uuid]
                    price = driver_prices[driver_id]

                    ride_match = RideMatchResponse(
                        driver_name=driver_name,
                        price=price
                    )
                    ride_matches.append(ride_match)
                    logging.info(f"✅ Added match: {driver_name} - ${price}")
                else:
                    logging.warning(f"⚠️ No profile found for driver UUID: {driver_uuid}")
            else:
                logging.warning(f"⚠️ No UUID found for driver ID: {driver_id}")

        logging.info(f"🎉 Returning {len(ride_matches)} ride matches")
        return ride_matches

    except Exception as e:
        logging.error(f"💥 Error in get_ride_matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint
@backend.get("/health")
def health_check():
    """Check if the API and Supabase connection are working"""
    try:
        # Test Supabase connection
        result = supabase.table('Ride_Request').select('count', count='exact').execute()
        return {
            "status": "healthy",
            "supabase_connected": True,
            "total_ride_requests": result.count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "supabase_connected": False,
            "error": str(e)
        }