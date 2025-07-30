import requests
import math
from itertools import repeat
from typing import Optional

token = ""

# URL https://api.mapbox.com/directions-matrix/v1/{profile}/{coordinates}
# Going with the mapbox/driving profile, traffic shouldn't matter for distances
url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"

def calculate_costs(coords: list, config: tuple) -> Optional[list]:
    """
    coords: Coordinates('longitude, latitude') for the start point, pickup points, and destination point
    config: Tuple of gas price ($/L) and fuel efficiency(L/km)

    Returns list of what each hitchhiker pays
    """
    if len(coords) <= 2:
        print("Incorrect usage, there must be intermediate pickup points")
        return None
    
    params = {
        'access_token': token,
        'sources': 'all',
        'annotations': 'distance,duration'
    }

    coords_str = ';'.join(coords)
    response = requests.get(url + coords_str, params=params)

    if response.status_code == 200:
        data = response.json()
        distance_matrix = data['distances']

        costs = []
        for i in range(1, len(coords) - 1):
            c = distance_matrix[i - 1][i] + distance_matrix[i][-1]
            c /= 1000 # Because want in km
            costs.append(c * config[0] * config[1])
        
        return costs
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

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


def get_distance(a, b) -> Optional[float]:
    if not isinstance(a, (str, tuple)) or not isinstance(b, (str, tuple)):
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
    return distance_matrix[0][1] # Distance from a to b


def path_difference_method(coords: list, config: tuple) -> Optional[list]:
    if len(coords) <= 2:
        raise Exception("Insufficient number of coordinates supplied")
    
    split_coords = [c.split(',') for c in coords]
    crds = [[float(c[0]), float(c[1])] for c in split_coords] # Proper type for taking euclidean norm

    waypoints = get_waypoints(coords[0], coords[1])

    if waypoints is None:
        raise Exception("No waypoints in route")
    
    detour_coords = []
    costs = []
    for j in range(1, len(crds) - 1):
        distances = list(map(math.dist, waypoints, repeat(crds[j])))
        detour_index = min(range(len(distances)), key=lambda i: distances[i])
        detour_coord = waypoints[detour_index]
        detour_coords.append(detour_coord)
        detour_dist = get_distance(tuple(crds[j]), tuple(detour_coord)) # 'l' in documentation
        leftover_dist = get_distance(tuple(detour_coord), coords[len(coords) - 1]) # 's' in documentation
        if detour_dist is None or leftover_dist is None:
            raise Exception("Error with getting distances")
        cost = ((2 * detour_dist + leftover_dist) / 1000) * config[0] * config[1]
        costs.append(cost) 
        print(f"Detour for pickup point {crds[j]} is {detour_coord}")
    
    return costs


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
   coords = convert_fmt([
        '53.43914566079182, -113.61880757370292',
        '53.462328050963656, -113.5678950301022', # A
        '53.47578144319133, -113.59709132268893', # B
        '53.474919787885014, -113.56411479387198', # C
        '53.51664209748684, -113.52566898659877'
   ])

   costs = path_difference_method(coords, (2, 1/6))
   print("Costs", costs)