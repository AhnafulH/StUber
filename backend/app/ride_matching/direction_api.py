import requests
import json
from typing import Dict, List, Tuple, Optional

class MapboxDirections:
    def __init__(self, access_token: str):
        """
        Initialize Mapbox Directions API client
        
        Args:
            access_token: Your Mapbox API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.mapbox.com/directions/v5"
    
    def get_directions(
        self,
        coordinates: List[Tuple[float, float]],
        profile: str = "mapbox/driving-traffic",
        geometries: str = "polyline",
        overview: str = "full",
        alternatives: bool = False
    ) -> Dict:
        """
        Get directions between waypoints
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Routing profile (driving-traffic, driving, walking, cycling)
            geometries: Response format (polyline, polyline6, geojson)
            overview: Geometry detail (full, simplified, false)
            alternatives: Whether to return alternative routes
            
        Returns:
            JSON response from Mapbox API
        """
        
        # Format coordinates as semicolon-separated string
        coords_str = ";".join([f"{lng},{lat}" for lng, lat in coordinates])
        
        # Build URL
        url = f"{self.base_url}/{profile}/{coords_str}"
        
        # Parameters - only include non-default values
        params = {
            "access_token": self.access_token,
        }
        
        # Only add parameters if they're not default values
        if geometries != "polyline":
            params["geometries"] = geometries
        if overview != "simplified":
            params["overview"] = overview
        if alternatives:  # Only add if True
            params["alternatives"] = "true"
        
        # Make request
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            # Try to get more error details
            try:
                error_response = response.json()
                print(f"API Error Details: {error_response}")
            except:
                print(f"Raw response: {response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    def print_route_info(self, response: Dict) -> None:
        """Print basic route information"""
        if not response or response.get("code") != "Ok":
            print("❌ No valid route found")
            return
            
        routes = response.get("routes", [])
        if not routes:
            print("❌ No routes in response")
            return
            
        print(f"✅ Found {len(routes)} route(s)")
        print("-" * 50)
        
        for i, route in enumerate(routes):
            print(f"🛣️  Route {i+1}:")
            print(f"   Distance: {route['distance']:.1f} meters")
            print(f"   Duration: {route['duration']:.1f} seconds ({route['duration']/60:.1f} minutes)")
            print(f"   Geometry type: {type(route['geometry'])}")
            
            if isinstance(route['geometry'], str):
                print(f"   Geometry preview: {route['geometry'][:50]}...")
            else:
                print(f"   Geometry: {route['geometry']}")
            print()


def main():
    # 🔑 Replace with your actual Mapbox token
    MAPBOX_TOKEN = "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4bnMycDAwbWl1MnJwdDI4YjVobGEyIn0.xE6vOmQFwMHQsH9t0IUsMA"
    
    
    # Initialize client
    client = MapboxDirections(MAPBOX_TOKEN)
    
    # Example coordinates (matching Mapbox docs examples - SF area)
    coordinates = [
        (-122.42, 37.78),  # San Francisco (lng, lat)
        (-77.03, 38.91)    # Washington DC (lng, lat) - from docs example
    ]
    
    print("🗺️  Testing Mapbox Directions API")
    print("=" * 50)
    
    # Test 1: Basic request (minimal parameters)
    print("📍 Test 1: Basic Request (Minimal Parameters)")
    response1 = client.get_directions(
        coordinates=coordinates
    )
    client.print_route_info(response1)
    
    # Test 2: GeoJSON format with full overview
    print("📍 Test 2: GeoJSON Format") 
    response2 = client.get_directions(
        coordinates=coordinates,
        geometries="geojson",
        overview="full" 
    )
    client.print_route_info(response2)
    
    # Test 3: With alternatives
    print("📍 Test 3: With Alternative Routes")
    response3 = client.get_directions(
        coordinates=coordinates,
        alternatives=True
    )
    client.print_route_info(response3)
    
    # Test 4: Try simpler driving profile
    print("📍 Test 4: Simple Driving Profile")
    response4 = client.get_directions(
        coordinates=coordinates,
        profile="mapbox/driving"
    )
    client.print_route_info(response4)
    
    # Show raw geometry examples
    if response1 and response1.get("routes"):
        print("🔍 Raw Geometry Examples:")
        print("-" * 30)
        print("Polyline:", response1["routes"][0]["geometry"][:100] + "...")
        
    if response2 and response2.get("routes"):
        geometry = response2["routes"][0]["geometry"]
        if isinstance(geometry, str):
            print("GeoJSON:", geometry[:100] + "...")
        else:
            print("GeoJSON coords preview:", str(geometry.get("coordinates", [])[:3]) + "...")


if __name__ == "__main__":
    main()