from __future__ import annotations

from functools import lru_cache
from itertools import product
from math import sqrt
from typing import Iterable, Tuple

Coord5D = Tuple[int, int, int, int, int]
BITS_PER_DIM = 8
MASK = 0xFF
DIM_NAMES = {"x": 0, "y": 1, "z": 2, "d4": 3, "d5": 4}


def pack_coords(x: int, y: int, z: int, d4: int, d5: int) -> int:
    coords = (x, y, z, d4, d5)
    if any(c < 0 or c > MASK for c in coords):
        raise ValueError("Coordinates must be between 0 and 255.")
    return x | (y << 8) | (z << 16) | (d4 << 24) | (d5 << 32)


def unpack_coords(index: int) -> Coord5D:
    return (
        index & MASK,
        (index >> 8) & MASK,
        (index >> 16) & MASK,
        (index >> 24) & MASK,
        (index >> 32) & MASK,
    )


def euclidean_distance_5d(a: Coord5D, b: Coord5D) -> float:
    return sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def coords_to_linear(coord: Coord5D, dims: Coord5D) -> int:
    if any(d <= 0 for d in dims):
        raise ValueError("All dimensions must be positive")
    if any(c < 0 or c >= d for c, d in zip(coord, dims)):
        raise ValueError(f"Coordinate {coord} outside dimensions {dims}")
    x, y, z, d4, d5 = coord
    return (((x * dims[1] + y) * dims[2] + z) * dims[3] + d4) * dims[4] + d5


def linear_to_5d(idx: int, dims: Coord5D) -> Coord5D:
    total = 1
    for d in dims:
        if d <= 0:
            raise ValueError("All dimensions must be positive")
        total *= d
    if idx < 0 or idx >= total:
        raise ValueError(f"Linear index {idx} outside [0,{total})")
    d5 = idx % dims[4]
    idx //= dims[4]
    d4 = idx % dims[3]
    idx //= dims[3]
    z = idx % dims[2]
    idx //= dims[2]
    y = idx % dims[1]
    idx //= dims[1]
    x = idx
    return (x, y, z, d4, d5)


@lru_cache(maxsize=32)
def neighbour_offsets(radius: float) -> tuple[Coord5D, ...]:
    if radius <= 0:
        return ()
    r = int(radius)
    offsets: list[Coord5D] = []
    for off in product(range(-r, r + 1), repeat=5):
        if off == (0, 0, 0, 0, 0):
            continue
        if sqrt(sum(v * v for v in off)) <= radius:
            offsets.append(off)  # type: ignore[arg-type]
    return tuple(offsets)


def iter_neighbour_coords(
    coord: Coord5D, dimensions: Coord5D, radius: float
) -> Iterable[Coord5D]:
    for off in neighbour_offsets(radius):
        candidate = tuple(c + dc for c, dc in zip(coord, off))
        if all(0 <= candidate[i] < dimensions[i] for i in range(5)):
            yield candidate  # type: ignore[misc]


def make_boundary_coord(dims: Coord5D, dimension: str, value: int) -> Coord5D:
    if dimension not in DIM_NAMES:
        raise ValueError(f"Unknown dimension: {dimension}")
    idx = DIM_NAMES[dimension]
    if not 0 <= value < dims[idx]:
        raise ValueError("Boundary coordinate outside dimensions")
    coord = [0, 0, 0, 0, 0]
    coord[idx] = value
    return tuple(coord)  # type: ignore[return-value]
