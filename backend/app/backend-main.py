from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

backend = FastAPI(title="StUber", description="Ride-sharing")

class RideRequest(BaseModel):
    id: int
    start: float
    end: float
    time: datetime
    seats: int

class RideOffer(BaseModel):
    id: int
    start: float
    end: float
    time: datetime
    seats: int

@backend.post("/ride-requests", response_model=RideRequest)
def create_ride_request(ride_request: RideRequest):
    print(f"Received a request for a ride by {ride_request.id} from {ride_request.start} to {ride_request.end}")

@backend.post("/ride-offers", response_model=RideOffer)
def create_ride_offer(ride_offer: RideOffer):
    print(f"Received an offer for a ride by {ride_offer.id} from {ride_offer.start} to {ride_offer.end}")

