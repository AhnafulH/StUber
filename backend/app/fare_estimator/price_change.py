from price_calculator import FuelPrice
from price_calculator import calculate_price
from price_calculator import convert_fmt
from price_calculator import get_waypoints

if __name__ == "__main__":
    coordinates = [
        '53.43914566079182, -113.61880757370292',
        '53.462328050963656, -113.5678950301022', # A
        '53.47578144319133, -113.59709132268893', # B
        '53.474919787885014, -113.56411479387198', # C
        '53.51664209748684, -113.52566898659877'
    ]
    coordinates = convert_fmt(coordinates)
    A, B, C = coordinates[1:4]
    A = [float(i) for i in A.split(',')]
    B = [float(i) for i in B.split(',')]
    C = [float(i) for i in C.split(',')]
    driver_waypoints = get_waypoints(coordinates[0], coordinates[-1])
    fp = FuelPrice(2, 1/6)

    cost_A = calculate_price(driver_waypoints, A, C, fp)
    cost_B = calculate_price(driver_waypoints, B, C, fp)

    print(f"Price for A to C is {cost_A}, price for B to C is {cost_B}")
