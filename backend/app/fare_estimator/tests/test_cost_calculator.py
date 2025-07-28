import pytest

from cost_calculator import convert_fmt
from cost_calculator import calculate_costs

def test_convert_fmt():
    coords = [
        '53.519392233019815, -113.50974601605492',
        '53.52784175302008, -113.52003528048324',
        '53.52486208867297, -113.5272245620243'
    ]

    res = convert_fmt(coords)

    expected = [
        '-113.50974601605492,53.519392233019815', # Start
        '-113.52003528048324,53.52784175302008', # Rutherford House
        '-113.5272245620243,53.52486208867297' # UofA SUB
    ]

    assert expected == res

