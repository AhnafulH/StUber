import requests
import math
from itertools import repeat
from typing import Optional
from typing import NamedTuple

token = "pk.eyJ1IjoibW9ub2NsZS1hbW9uIiwiYSI6ImNtZGY5YzhhMTBiMTgya3B0YzdjZXFya3IifQ.coqwpwT5sFC2V4EDKfIfnA"

# URL https://api.mapbox.com/directions-matrix/v1/{profile}/{coordinates}
# Going with the mapbox/driving profile, traffic shouldn't matter for distances
url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"

class FuelPrice(NamedTuple):
    gas_price: float # ($/L)
    fuel_efficiency: float # (L/km)


def get_waypoints(start, end) -> Optional[list]:
    """
    Returns waypoints in the form of list of [longitude, latitude] pairs
    """
    if not isinstance(start, (str, tuple)) or not isinstance(start, (str, tuple)):
        raise TypeError("Invalid type, expected tuple or string")

    base_url = "https://api.mapbox.com/directions/v5/mapbox"

    if type(start) is str:
        if type(end) is str:
            coordinates = start + ';' + end
        else:
            coordinates = start + ';' + f"{end[0]},{end[1]}"
    else:
        if type(end) is str:
            coordinates = f"{start[0]},{start[1]}" + ';' + end
        else:
            coordinates = f"{start[0]},{start[1]};{end[0]},{end[1]}"

    url = f"{base_url}/driving/{coordinates}"

    params = {
        'access_token': token,
        'geometries': 'geojson',
        'steps': 'false',
        'overview': 'full'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

    result = response.json()

    route = result['routes'][0] # First route

    if 'geometry' in route and 'coordinates' in route['geometry']:
        return route['geometry']['coordinates']


def get_distance(a, b) -> Optional[tuple]:
    if not isinstance(a, (str, tuple, list)) or not isinstance(b, (str, tuple, list)):
        raise TypeError("Invalid type, expected tuple or string")

    if type(a) is str:
        if type(b) is str:
            coordinates = a + ';' + b
        else:
            coordinates = a + ';' + f"{b[0]},{b[1]}"
    else:
        if type(b) is str:
            coordinates = f"{a[0]},{a[1]}" + ';' + b
        else:
            coordinates = f"{a[0]},{a[1]};{b[0]},{b[1]}"

    url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/" + coordinates

    params = {
        'access_token': token,
        'sources': 'all',
        'annotations': 'distance,duration'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

    data = response.json()
    distance_matrix = data['distances']
    duration_matrix = data['durations']
    return distance_matrix[0][1], duration_matrix[0][1] # Distance from a to b


def calculate_price(driver_waypoints: list, source, destination, fuel_price: FuelPrice) -> Optional[tuple]:
    """"
    Calculate the price a commuter has to pay given a driver's route

    Args:
        driver_waypoints: List of [Long, Lat] or (Long, Lat) denoting waypoints
        source: Pickup point for the commuter [Long, Lat] or (Long, Lat)
        destination: The commuter's destination [Long, Lat] or (Long, Lat)
        fuel_price: Gas price and fuel efficiency

    Returns:
        Returns [price, detour_distance, detour_time]
    """

    # Figure out from where to take the detour in the path
    distances = list(map(math.dist, driver_waypoints, repeat(source)))
    detour_index = min(range(len(distances)), key=lambda i: distances[i])
    detour_coordinate = driver_waypoints[detour_index]
    try:
        detour_distance, detour_duration = get_distance(detour_coordinate, source)
        destination_distance, destination_duration = get_distance(source, destination)
        dest_to_end_distance, dest_to_end_duration = get_distance(destination, driver_waypoints[-1])
    except requests.exceptions.RequestException:
        return None

    total_distance = (detour_distance + destination_distance) / 1000
    price = total_distance * fuel_price.gas_price * fuel_price.fuel_efficiency
    total_detour = (detour_distance, dest_to_end_distance)
    total_duration = (detour_duration, dest_to_end_duration)
    return price, total_detour, total_duration

def convert_fmt(coords: list) -> list:
    """
    Google Maps returns Lat, Long. This function translates it to Long,Lat
    """
    fmt_coords = []
    for c in coords:
        d = c.split(', ')
        fmt_coords.append(d[1] + ',' + d[0])
    return fmt_coords

if __name__ == "__main__":
    pass
