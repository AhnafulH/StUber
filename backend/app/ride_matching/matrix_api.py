import os
import asyncio
import aiohttp
import time
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class MatrixRequest:
    """Data class for Matrix API request configuration."""
    coordinates: List[Tuple[float, float]]  # [(lng, lat), ...]
    profile: str = "mapbox/driving"
    annotations: str = "duration,distance"
    sources: Optional[Union[str, List[int]]] = None
    destinations: Optional[Union[str, List[int]]] = None
    approaches: Optional[List[str]] = None
    bearings: Optional[List[Tuple[int, int]]] = None
    depart_at: Optional[str] = None

@dataclass
class MatrixResponse:
    """Data class for Matrix API response."""
    durations: List[List[Optional[float]]]
    distances: List[List[Optional[float]]]
    sources: List[Dict]
    destinations: List[Dict]
    code: str
    raw_response: Dict

@dataclass
class RouteInfo:
    """Data class for individual route information."""
    from_index: int
    to_index: int
    duration_seconds: Optional[float]
    distance_meters: Optional[float]
    duration_minutes: Optional[float]
    distance_km: Optional[float]
    from_coordinate: Tuple[float, float]
    to_coordinate: Tuple[float, float]

class MapboxMatrixAPIError(Exception):
    """Custom exception for Mapbox Matrix API errors."""
    pass

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]) + 0.1  # Small buffer
            if sleep_time > 0:
                print(f"⏳ Rate limit reached. Waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
        
        # Record this request
        self.requests.append(now)

class MapboxMatrixAPI:
    """
    Mapbox Matrix API client for calculating travel times and distances between multiple points.
    
    Features:
    - Async HTTP requests for better performance
    - Rate limiting to respect API limits
    - Support for all Mapbox profiles (driving, walking, cycling, driving-traffic)
    - Easy-to-use methods for common ride-sharing use cases
    - Comprehensive error handling
    """
    
    def __init__(self, access_token: str = None):
        """
        Initialize the Mapbox Matrix API client.
        
        Args:
            access_token: Mapbox access token. If None, will try to get from MAPBOX_ACCESS_TOKEN env var.
        """
        self.access_token = access_token or os.environ.get('MAPBOX_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("Mapbox access token is required. Set MAPBOX_ACCESS_TOKEN env var or pass it directly.")
        
        self.base_url = "https://api.mapbox.com/directions-matrix/v1"
        
        # Rate limiters for different profiles
        self.rate_limiters = {
            'standard': RateLimiter(60, 60),  # 60 requests per minute for driving/walking/cycling
            'traffic': RateLimiter(30, 60)    # 30 requests per minute for driving-traffic
        }
        
        # Session will be created when needed
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_rate_limiter(self, profile: str) -> RateLimiter:
        """Get the appropriate rate limiter for the profile."""
        if profile == "mapbox/driving-traffic":
            return self.rate_limiters['traffic']
        return self.rate_limiters['standard']
    
    def _validate_request(self, request: MatrixRequest):
        """Validate the matrix request parameters."""
        # Check coordinate limits
        max_coords = 10 if request.profile == "mapbox/driving-traffic" else 25
        if len(request.coordinates) > max_coords:
            raise MapboxMatrixAPIError(f"Too many coordinates. Max {max_coords} for {request.profile}")
        
        if len(request.coordinates) < 2:
            raise MapboxMatrixAPIError("At least 2 coordinates are required")
        
        # Validate profile
        valid_profiles = ["mapbox/driving", "mapbox/walking", "mapbox/cycling", "mapbox/driving-traffic"]
        if request.profile not in valid_profiles:
            raise MapboxMatrixAPIError(f"Invalid profile. Must be one of: {valid_profiles}")
        
        # Validate coordinates format
        for i, (lng, lat) in enumerate(request.coordinates):
            if not (-180 <= lng <= 180):
                raise MapboxMatrixAPIError(f"Invalid longitude at index {i}: {lng}")
            if not (-90 <= lat <= 90):
                raise MapboxMatrixAPIError(f"Invalid latitude at index {i}: {lat}")
    
    def _build_url(self, request: MatrixRequest) -> str:
        """Build the API URL from the request parameters."""
        # Format coordinates
        coord_string = ";".join([f"{lng},{lat}" for lng, lat in request.coordinates])
        
        # Base URL
        url = f"{self.base_url}/{request.profile}/{coord_string}"
        
        # Query parameters
        params = []
        
        # Access token
        params.append(f"access_token={self.access_token}")
        
        # Annotations
        if request.annotations:
            params.append(f"annotations={request.annotations}")
        
        # Sources
        if request.sources is not None:
            if isinstance(request.sources, list):
                sources_str = ";".join(map(str, request.sources))
            else:
                sources_str = request.sources
            params.append(f"sources={sources_str}")
        
        # Destinations
        if request.destinations is not None:
            if isinstance(request.destinations, list):
                destinations_str = ";".join(map(str, request.destinations))
            else:
                destinations_str = request.destinations
            params.append(f"destinations={destinations_str}")
        
        # Approaches
        if request.approaches:
            params.append(f"approaches={';'.join(request.approaches)}")
        
        # Bearings
        if request.bearings:
            bearing_strings = []
            for bearing in request.bearings:
                if bearing is None:
                    bearing_strings.append("")
                else:
                    bearing_strings.append(f"{bearing[0]},{bearing[1]}")
            params.append(f"bearings={';'.join(bearing_strings)}")
        
        # Depart at
        if request.depart_at:
            params.append(f"depart_at={request.depart_at}")
        
        return f"{url}?{'&'.join(params)}"
    
    async def calculate_matrix(self, request: MatrixRequest) -> MatrixResponse:
        """
        Calculate travel time and distance matrix for the given coordinates.
        
        Args:
            request: MatrixRequest object with all parameters
            
        Returns:
            MatrixResponse object with durations, distances, and metadata
        """
        self._validate_request(request)
        
        # Create session if not exists
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Rate limiting
        rate_limiter = self._get_rate_limiter(request.profile)
        await rate_limiter.acquire()
        
        # Build URL
        url = self._build_url(request)
        
        try:
            print(f"🌐 Making Mapbox Matrix API request...")
            print(f"   Profile: {request.profile}")
            print(f"   Coordinates: {len(request.coordinates)} points")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MapboxMatrixAPIError(f"HTTP {response.status}: {error_text}")
                
                data = await response.json()
                
                # Check for API errors
                if data.get('code') != 'Ok':
                    raise MapboxMatrixAPIError(f"API Error: {data.get('code')} - {data.get('message', 'Unknown error')}")
                
                print(f"✅ Matrix API request successful")
                
                return MatrixResponse(
                    durations=data.get('durations', []),
                    distances=data.get('distances', []),
                    sources=data.get('sources', []),
                    destinations=data.get('destinations', []),
                    code=data.get('code'),
                    raw_response=data
                )
                
        except aiohttp.ClientError as e:
            raise MapboxMatrixAPIError(f"Network error: {e}")
    
    async def calculate_simple_matrix(
        self, 
        coordinates: List[Tuple[float, float]], 
        profile: str = "mapbox/driving"
    ) -> MatrixResponse:
        """
        Simple method to calculate a symmetric matrix (all-to-all).
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Mapbox routing profile
            
        Returns:
            MatrixResponse object
        """
        request = MatrixRequest(
            coordinates=coordinates,
            profile=profile,
            annotations="duration,distance"
        )
        return await self.calculate_matrix(request)
    
    async def calculate_one_to_many(
        self, 
        origin: Tuple[float, float], 
        destinations: List[Tuple[float, float]], 
        profile: str = "mapbox/driving"
    ) -> List[RouteInfo]:
        """
        Calculate travel times and distances from one origin to many destinations.
        
        Args:
            origin: (longitude, latitude) of origin point
            destinations: List of (longitude, latitude) tuples for destinations
            profile: Mapbox routing profile
            
        Returns:
            List of RouteInfo objects for each destination
        """
        coordinates = [origin] + destinations
        
        request = MatrixRequest(
            coordinates=coordinates,
            profile=profile,
            sources=[0],  # Only use first coordinate as source
            destinations="all",
            annotations="duration,distance"
        )
        
        response = await self.calculate_matrix(request)
        
        # Convert to RouteInfo objects
        route_infos = []
        for i, dest in enumerate(destinations):
            duration = response.durations[0][i + 1] if response.durations[0][i + 1] is not None else None
            distance = response.distances[0][i + 1] if response.distances[0][i + 1] is not None else None
            
            route_info = RouteInfo(
                from_index=0,
                to_index=i + 1,
                duration_seconds=duration,
                distance_meters=distance,
                duration_minutes=duration / 60 if duration else None,
                distance_km=distance / 1000 if distance else None,
                from_coordinate=origin,
                to_coordinate=dest
            )
            route_infos.append(route_info)
        
        return route_infos
    
    async def calculate_many_to_one(
        self, 
        origins: List[Tuple[float, float]], 
        destination: Tuple[float, float], 
        profile: str = "mapbox/driving"
    ) -> List[RouteInfo]:
        """
        Calculate travel times and distances from many origins to one destination.
        
        Args:
            origins: List of (longitude, latitude) tuples for origins
            destination: (longitude, latitude) of destination point
            profile: Mapbox routing profile
            
        Returns:
            List of RouteInfo objects for each origin
        """
        coordinates = origins + [destination]
        dest_index = len(origins)
        
        request = MatrixRequest(
            coordinates=coordinates,
            profile=profile,
            sources=list(range(len(origins))),  # Use first N coordinates as sources
            destinations=[dest_index],  # Use last coordinate as destination
            annotations="duration,distance"
        )
        
        response = await self.calculate_matrix(request)
        
        # Convert to RouteInfo objects
        route_infos = []
        for i, origin in enumerate(origins):
            duration = response.durations[i][0] if response.durations[i][0] is not None else None
            distance = response.distances[i][0] if response.distances[i][0] is not None else None
            
            route_info = RouteInfo(
                from_index=i,
                to_index=dest_index,
                duration_seconds=duration,
                distance_meters=distance,
                duration_minutes=duration / 60 if duration else None,
                distance_km=distance / 1000 if distance else None,
                from_coordinate=origin,
                to_coordinate=destination
            )
            route_infos.append(route_info)
        
        return route_infos

    def get_route_info(self, response: MatrixResponse, from_index: int, to_index: int) -> RouteInfo:
        """
        Extract route information for a specific origin-destination pair from matrix response.
        
        Args:
            response: MatrixResponse from calculate_matrix
            from_index: Index of origin coordinate
            to_index: Index of destination coordinate
            
        Returns:
            RouteInfo object with travel time and distance
        """
        duration = response.durations[from_index][to_index] if response.durations[from_index][to_index] is not None else None
        distance = response.distances[from_index][to_index] if response.distances[from_index][to_index] is not None else None
        
        # Get coordinates from sources/destinations
        from_coord = None
        to_coord = None
        
        if from_index < len(response.sources):
            source = response.sources[from_index]
            from_coord = (source['location'][0], source['location'][1])
        
        if to_index < len(response.destinations):
            dest = response.destinations[to_index]
            to_coord = (dest['location'][0], dest['location'][1])
        
        return RouteInfo(
            from_index=from_index,
            to_index=to_index,
            duration_seconds=duration,
            distance_meters=distance,
            duration_minutes=duration / 60 if duration else None,
            distance_km=distance / 1000 if distance else None,
            from_coordinate=from_coord,
            to_coordinate=to_coord
        )

# Utility functions for ride-sharing specific use cases

async def calculate_ride_detour(
    api_client: MapboxMatrixAPI,
    driver_start: Tuple[float, float],
    driver_end: Tuple[float, float],
    passenger_pickup: Tuple[float, float],
    passenger_dropoff: Tuple[float, float],
    profile: str = "mapbox/driving"
) -> Dict:
    """
    Calculate detour information for a ride-sharing scenario.
    
    Args:
        api_client: MapboxMatrixAPI instance
        driver_start: Driver's starting location (lng, lat)
        driver_end: Driver's ending location (lng, lat)
        passenger_pickup: Passenger pickup location (lng, lat)
        passenger_dropoff: Passenger dropoff location (lng, lat)
        profile: Mapbox routing profile
        
    Returns:
        Dictionary with detour analysis
    """
    # Define all coordinates
    coordinates = [driver_start, driver_end, passenger_pickup, passenger_dropoff]
    
    # Calculate full matrix
    response = await api_client.calculate_simple_matrix(coordinates, profile)
    
    # Direct route: driver_start -> driver_end
    direct_route = api_client.get_route_info(response, 0, 1)
    
    # Detour route: driver_start -> passenger_pickup -> passenger_dropoff -> driver_end
    leg1 = api_client.get_route_info(response, 0, 2)  # driver_start -> passenger_pickup
    leg2 = api_client.get_route_info(response, 2, 3)  # passenger_pickup -> passenger_dropoff
    leg3 = api_client.get_route_info(response, 3, 1)  # passenger_dropoff -> driver_end
    
    # Calculate total detour
    detour_duration = None
    detour_distance = None
    
    if all(leg.duration_seconds is not None for leg in [leg1, leg2, leg3]):
        total_detour_duration = leg1.duration_seconds + leg2.duration_seconds + leg3.duration_seconds
        detour_duration = total_detour_duration - direct_route.duration_seconds if direct_route.duration_seconds else None
    
    if all(leg.distance_meters is not None for leg in [leg1, leg2, leg3]):
        total_detour_distance = leg1.distance_meters + leg2.distance_meters + leg3.distance_meters
        detour_distance = total_detour_distance - direct_route.distance_meters if direct_route.distance_meters else None
    
    return {
        'direct_route': {
            'duration_minutes': direct_route.duration_minutes,
            'distance_km': direct_route.distance_km
        },
        'detour_route': {
            'total_duration_minutes': (leg1.duration_seconds + leg2.duration_seconds + leg3.duration_seconds) / 60 if all(leg.duration_seconds is not None for leg in [leg1, leg2, leg3]) else None,
            'total_distance_km': (leg1.distance_meters + leg2.distance_meters + leg3.distance_meters) / 1000 if all(leg.distance_meters is not None for leg in [leg1, leg2, leg3]) else None
        },
        'detour': {
            'additional_duration_minutes': detour_duration / 60 if detour_duration else None,
            'additional_distance_km': detour_distance / 1000 if detour_distance else None
        },
        'legs': {
            'driver_to_pickup': leg1,
            'pickup_to_dropoff': leg2,
            'dropoff_to_driver_end': leg3
        }
    }

# Example usage and testing functions

async def test_matrix_api():
    """Test the Mapbox Matrix API implementation."""
    print("🧪 Testing Mapbox Matrix API Implementation")
    print("=" * 50)
    
    # Edmonton coordinates for testing
    university = (-113.5263, 53.5232)  # University of Alberta
    downtown = (-113.4909, 53.5444)   # Downtown Edmonton
    whyte_ave = (-113.5200, 53.5189)  # Whyte Avenue
    west_end = (-113.5600, 53.5300)   # West End
    
    try:
        async with MapboxMatrixAPI() as api:
            
            # Test 1: Simple symmetric matrix
            print("\n1️⃣ Testing symmetric matrix (all-to-all)")
            coordinates = [university, downtown, whyte_ave, west_end]
            response = await api.calculate_simple_matrix(coordinates)
            
            print(f"✅ Matrix calculated for {len(coordinates)} points")
            print(f"   Duration matrix shape: {len(response.durations)}x{len(response.durations[0])}")
            print(f"   Distance matrix shape: {len(response.distances)}x{len(response.distances[0])}")
            
            # Test 2: One-to-many
            print("\n2️⃣ Testing one-to-many (University to other locations)")
            destinations = [downtown, whyte_ave, west_end]
            routes = await api.calculate_one_to_many(university, destinations)
            
            for i, route in enumerate(routes):
                print(f"   Route {i+1}: {route.duration_minutes:.1f}min, {route.distance_km:.1f}km")
            
            # Test 3: Ride detour calculation
            print("\n3️⃣ Testing ride detour calculation")
            detour_info = await calculate_ride_detour(
                api,
                driver_start=university,
                driver_end=downtown,
                passenger_pickup=whyte_ave,
                passenger_dropoff=west_end
            )
            
            print(f"   Direct route: {detour_info['direct_route']['duration_minutes']:.1f}min")
            print(f"   Detour route: {detour_info['detour_route']['total_duration_minutes']:.1f}min")
            print(f"   Additional time: {detour_info['detour']['additional_duration_minutes']:.1f}min")
            print(f"   Additional distance: {detour_info['detour']['additional_distance_km']:.1f}km")
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    """
    Example usage:
    
    1. Set your MAPBOX_ACCESS_TOKEN environment variable
    2. Run this script to test the implementation
    """
    
    # Check if access token is available
    if not os.environ.get('MAPBOX_ACCESS_TOKEN'):
        print("❌ Please set your MAPBOX_ACCESS_TOKEN environment variable")
        print("   You can get one from: https://account.mapbox.com/access-tokens/")
    else:
        # Run the test
        asyncio.run(test_matrix_api())