from cost_calculator import calculate_costs
from cost_calculator import convert_fmt
from cost_calculator import path_difference_method

if __name__ == "__main__":
    coords = [
        '53.43914566079182, -113.61880757370292',
        '53.462328050963656, -113.5678950301022', # A
        '53.47578144319133, -113.59709132268893', # B
        '53.474919787885014, -113.56411479387198', # C
        '53.51664209748684, -113.52566898659877'
    ]
    coords = convert_fmt(coords)
    A, B, C = coords[1:4]
    
    # First ordering
    c1 = path_difference_method(coords, (2, 1/6))
    if c1 is not None:
        print("Order A, B, C")
        for c, n in zip(c1, list('ABC')):
            print(f"{n} pays {c}")
        print('-'*40)

    # Second ordering B, A, C
    coords[1], coords[2] = B, A
    c2 = path_difference_method(coords, (2, 1/6))
    if c2 is not None:
        c2[0], c2[1] = c2[1], c2[0]
        print("Order B, A, C")
        for c, n in zip(c2, list('ABC')):
            print(f"{n} pays {c}")
        print('-'*40)
    coords[1], coords[2] = A, B # Reset

    # Third ordering C, A, B
    coords[1] = C
    coords[2] = A
    coords[3] = B
    c3 = path_difference_method(coords, (2, 1/6))
    if c3 is not None:
        c3[0], c3[1], c3[2] = c3[2], c3[0], c3[1]
        print("Order C, A, B")
        for c, n in zip(c3, list('ABC')):
            print(f"{n} pays {c}")
        print('-'*40)
    coords[1] = A
    coords[2] = B
    coords[3] = C