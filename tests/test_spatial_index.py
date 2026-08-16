import pytest
from src.core.spatial_index import *


def test_pack_roundtrip():
    c = (1, 2, 3, 4, 5)
    assert unpack_coords(pack_coords(*c)) == c


def test_pack_bounds():
    with pytest.raises(ValueError):
        pack_coords(-1, 0, 0, 0, 0)
    with pytest.raises(ValueError):
        pack_coords(256, 0, 0, 0, 0)


def test_linear_roundtrip():
    dims = (10, 10, 10, 10, 10)
    for c in [(0, 0, 0, 0, 0), (9, 9, 9, 9, 9), (3, 4, 5, 6, 7)]:
        assert linear_to_5d(coords_to_linear(c, dims), dims) == c


def test_neighbours_inside_radius():
    dims = (10, 10, 10, 10, 10)
    c = (5, 5, 5, 5, 5)
    ns = list(iter_neighbour_coords(c, dims, 2.0))
    assert ns and all(euclidean_distance_5d(c, n) <= 2.0 for n in ns)
