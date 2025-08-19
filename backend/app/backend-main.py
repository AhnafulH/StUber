from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import os
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
backend = FastAPI()


# Request models (without ID - for creating new records)
class RideRequestCreate(BaseModel):
    starting_location: str = Field(..., description="Starting location name")
    destination: str = Field(..., description="Destination location name")
    seats_available: int = Field(..., ge=1, le=8, description="Number of available seats")
    starting_latitude: float = Field(..., ge=-90, le=90, description="Starting latitude")
    starting_longitude: float = Field(..., ge=-180, le=180, description="Starting longitude")
    destination_latitude: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_longitude: float = Field(..., ge=-180, le=180, description="Destination longitude")
    departure_datetime: datetime = Field(..., description="When the ride departs")
    max_detour_distance: float = Field(..., ge=0, description="Maximum detour distance in km")


class RideOfferCreate(BaseModel):
    starting_location: str = Field(..., description="Starting location name")
    destination: str = Field(..., description="Destination location name")
    seats_needed: int = Field(..., ge=1, le=8, description="Number of seats needed")
    starting_latitude: float = Field(..., ge=-90, le=90, description="Starting latitude")
    starting_longitude: float = Field(..., ge=-180, le=180, description="Starting longitude")
    destination_latitude: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_longitude: float = Field(..., ge=-180, le=180, description="Destination longitude")
    departure_datetime: datetime = Field(..., description="When the ride is needed")
    max_detour_distance: float = Field(..., ge=0, description="Maximum detour distance in km")


# Response models (with ID - what gets returned)
class RideRequest(BaseModel):
    id: int
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


class RideOffer(BaseModel):
    id: int
    starting_location: str
    destination: str
    seats_needed: int
    starting_latitude: float
    starting_longitude: float
    destination_latitude: float
    destination_longitude: float
    departure_datetime: datetime
    max_detour_distance: float
    created_at: Optional[datetime] = None


@backend.post("/ride-requests", response_model=RideRequest)
def create_ride_request(ride_request: RideRequestCreate):
    """
    Create a new ride request and insert it into Supabase
    """
    try:
        print(f"Received a request for a ride from {ride_request.starting_location} to {ride_request.destination}")
        print(f"Seats available: {ride_request.seats_available}, Departure: {ride_request.departure_datetime}")

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
        print(f"Seats needed: {ride_offer.seats_needed}, Departure: {ride_offer.departure_datetime}")

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


# Additional helper endpoints
@backend.get("/ride-requests", response_model=list[RideRequest])
def get_all_ride_requests():
    """Get all ride requests from Supabase"""
    try:
        result = supabase.table('Ride_Request').select('*').execute()

        # Convert datetime strings back to datetime objects
        rides = []
        for ride in result.data:
            ride['departure_datetime'] = datetime.fromisoformat(ride['departure_datetime'].replace('Z', '+00:00'))
            rides.append(RideRequest(**ride))

        return rides

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@backend.get("/ride-offers", response_model=list[RideOffer])
def get_all_ride_offers():
    """Get all ride offers from Supabase"""
    try:
        result = supabase.table('Ride_Offer').select('*').execute()

        # Convert datetime strings back to datetime objects
        offers = []
        for offer in result.data:
            offer['departure_datetime'] = datetime.fromisoformat(offer['departure_datetime'].replace('Z', '+00:00'))
            offers.append(RideOffer(**offer))

        return offers

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@backend.get("/ride-requests/{request_id}", response_model=RideRequest)
def get_ride_request(request_id: int):
    """Get a specific ride request by ID"""
    try:
        result = supabase.table('Ride_Request').select('*').eq('id', request_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Ride request not found")

        ride = result.data[0]
        ride['departure_datetime'] = datetime.fromisoformat(ride['departure_datetime'].replace('Z', '+00:00'))

        return RideRequest(**ride)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@backend.get("/ride-offers/{offer_id}", response_model=RideOffer)
def get_ride_offer(offer_id: int):
    """Get a specific ride offer by ID"""
    try:
        result = supabase.table('Ride_Offer').select('*').eq('id', offer_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Ride offer not found")

        offer = result.data[0]
        offer['departure_datetime'] = datetime.fromisoformat(offer['departure_datetime'].replace('Z', '+00:00'))

        return RideOffer(**offer)

    except HTTPException:
        raise
    except Exception as e:
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