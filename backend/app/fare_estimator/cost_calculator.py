import requests

token = ""

# URL https://api.mapbox.com/directions-matrix/v1/{profile}/{coordinates}
# Going with the mapbox/driving profile, traffic shouldn't matter for distances
url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"

def calculate_costs(coords: list, config: tuple) -> list:
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
    # Careful Google Maps returns Lat, Long but function expects Long, Lat
    coords = [
        '-113.50974601605492,53.519392233019815', # Start
        '-113.52003528048324,53.52784175302008', # Rutherford House
        '-113.5272245620243,53.52486208867297' # UofA SUB
    ]

    config = (2, 1/6)
    costs = calculate_costs(coords, config)
    print(costs)
    # Google Maps gives the total distance to be 3.3km
    # With 2$ per Litre and 6km per Litre that would be $1.1 paid for the trip
