"""5D spatial indexing for Brain-5D neural networks.

This module provides coordinate manipulation and spatial indexing for
the 5-dimensional neuron space used in Brain-5D. It supports:

- Packing/unpacking 5D coordinates into 64-bit integers
- Conversion between linear indices and 5D coordinates
- Euclidean and weighted distance calculations
- Neighbor iteration within a radius
- Boundary coordinate generation
- LRU-cached offset computation for performance

The 5D space is organized as (x, y, z, d4, d5) where:
- x, y, z: spatial dimensions (0-255)
- d4, d5: functional dimensions (0-255)
"""

from __future__ import annotations

import math
from functools import lru_cache
from itertools import product
from typing import Iterable, Iterator, Tuple, Union

# ============================================================================
# Type Aliases
# ============================================================================

Coord5D = Tuple[int, int, int, int, int]
"""Type alias for a 5D coordinate."""

Dim5D = Tuple[int, int, int, int, int]
"""Type alias for 5D dimensions."""

# ============================================================================
# Constants
# ============================================================================

BITS_PER_DIM: int = 8
"""Number of bits allocated per dimension in packed representation."""

MASK: int = 0xFF
"""Bitmask for extracting a single dimension (8 bits)."""

SHIFTS: Tuple[int, int, int, int, int] = (0, 8, 16, 24, 32)
"""Bit shifts for each dimension in packed representation."""

DIM_NAMES: dict[str, int] = {
    "x": 0,
    "y": 1,
    "z": 2,
    "d4": 3,
    "d5": 4,
}
"""Mapping from dimension names to indices."""

DIM_INDICES: dict[int, str] = {v: k for k, v in DIM_NAMES.items()}
"""Mapping from dimension indices to names."""

MAX_COORD: int = 255
"""Maximum coordinate value (8-bit range)."""


# ============================================================================
# Coordinate Validation
# ============================================================================

def validate_coord(coord: Coord5D) -> None:
    """Validate that all coordinates are within the 0-255 range.

    Args:
        coord: 5D coordinate to validate.

    Raises:
        ValueError: If any coordinate is outside the valid range.
    """
    for i, c in enumerate(coord):
        if c < 0 or c > MAX_COORD:
            raise ValueError(
                f"Coordinate {c} at dimension {i} must be between 0 and {MAX_COORD}"
            )


def validate_dims(dims: Dim5D) -> None:
    """Validate that all dimensions are positive.

    Args:
        dims: 5D dimensions to validate.

    Raises:
        ValueError: If any dimension is <= 0.
    """
    for i, d in enumerate(dims):
        if d <= 0:
            raise ValueError(f"Dimension {i} must be positive, got {d}")


def validate_coord_in_dims(coord: Coord5D, dims: Dim5D) -> None:
    """Validate that a coordinate is within the given dimensions.

    Args:
        coord: 5D coordinate to validate.
        dims: 5D dimensions.

    Raises:
        ValueError: If the coordinate is outside the dimensions.
    """
    validate_dims(dims)
    for i, (c, d) in enumerate(zip(coord, dims)):
        if c < 0 or c >= d:
            raise ValueError(
                f"Coordinate {c} at dimension {i} outside dimension {d}"
            )


def is_valid_coord(coord: Coord5D) -> bool:
    """Check if a coordinate is valid (all coordinates in 0-255 range).

    Args:
        coord: 5D coordinate to check.

    Returns:
        True if valid, False otherwise.
    """
    try:
        validate_coord(coord)
        return True
    except ValueError:
        return False


def is_valid_coord_in_dims(coord: Coord5D, dims: Dim5D) -> bool:
    """Check if a coordinate is valid within the given dimensions.

    Args:
        coord: 5D coordinate to check.
        dims: 5D dimensions.

    Returns:
        True if valid, False otherwise.
    """
    try:
        validate_coord_in_dims(coord, dims)
        return True
    except ValueError:
        return False


# ============================================================================
# Packing / Unpacking
# ============================================================================

def pack_coords(x: int, y: int, z: int, d4: int, d5: int) -> int:
    """Pack five 8-bit coordinates into a single 64-bit integer.

    This is useful for storing coordinates as keys in dictionaries
    or for efficient hashing.

    Args:
        x: X coordinate (0-255).
        y: Y coordinate (0-255).
        z: Z coordinate (0-255).
        d4: Fourth dimension coordinate (0-255).
        d5: Fifth dimension coordinate (0-255).

    Returns:
        A 64-bit integer with packed coordinates.

    Raises:
        ValueError: If any coordinate is outside the 0-255 range.

    Example:
        >>> packed = pack_coords(1, 2, 3, 4, 5)
        >>> unpack_coords(packed)
        (1, 2, 3, 4, 5)
    """
    coords = (x, y, z, d4, d5)
    for i, c in enumerate(coords):
        if c < 0 or c > MAX_COORD:
            raise ValueError(
                f"Coordinate {c} at dimension {i} must be between 0 and {MAX_COORD}"
            )
    return (
        (x << SHIFTS[0])
        | (y << SHIFTS[1])
        | (z << SHIFTS[2])
        | (d4 << SHIFTS[3])
        | (d5 << SHIFTS[4])
    )


def unpack_coords(index: int) -> Coord5D:
    """Unpack a 64-bit integer into five 8-bit coordinates.

    Args:
        index: Packed 64-bit integer containing 5D coordinates.

    Returns:
        A 5D coordinate tuple (x, y, z, d4, d5).

    Example:
        >>> pack = pack_coords(1, 2, 3, 4, 5)
        >>> unpack_coords(pack)
        (1, 2, 3, 4, 5)
    """
    return (
        (index >> SHIFTS[0]) & MASK,
        (index >> SHIFTS[1]) & MASK,
        (index >> SHIFTS[2]) & MASK,
        (index >> SHIFTS[3]) & MASK,
        (index >> SHIFTS[4]) & MASK,
    )


# ============================================================================
# Linear Index Conversion
# ============================================================================

def coords_to_linear(coord: Coord5D, dims: Dim5D) -> int:
    """Convert 5D coordinates to a linear index (row-major order).

    The linear index is computed as:
        (((x * dims[1] + y) * dims[2] + z) * dims[3] + d4) * dims[4] + d5

    Args:
        coord: 5D coordinate to convert.
        dims: 5D dimensions (must all be positive).

    Returns:
        Linear index in [0, product(dims)).

    Raises:
        ValueError: If dimensions are not positive or coordinate is out of bounds.

    Example:
        >>> dims = (10, 10, 10, 10, 10)
        >>> coords_to_linear((1, 2, 3, 4, 5), dims)
        # Returns a unique index for that coordinate
    """
    validate_dims(dims)
    validate_coord_in_dims(coord, dims)

    x, y, z, d4, d5 = coord
    return (((x * dims[1] + y) * dims[2] + z) * dims[3] + d4) * dims[4] + d5


def linear_to_5d(index: int, dims: Dim5D) -> Coord5D:
    """Convert a linear index back to 5D coordinates (row-major order).

    This is the inverse of coords_to_linear.

    Args:
        index: Linear index in [0, product(dims)).
        dims: 5D dimensions (must all be positive).

    Returns:
        The corresponding 5D coordinate.

    Raises:
        ValueError: If dimensions are not positive or index is out of bounds.

    Example:
        >>> dims = (10, 10, 10, 10, 10)
        >>> linear_to_5d(12345, dims)
        # Returns the original coordinate
    """
    validate_dims(dims)

    total = 1
    for d in dims:
        total *= d

    if index < 0 or index >= total:
        raise ValueError(
            f"Linear index {index} outside [0, {total})"
        )

    # Decode in reverse order (row-major)
    idx = index
    d5 = idx % dims[4]
    idx //= dims[4]
    d4 = idx % dims[3]
    idx //= dims[3]
    z = idx % dims[2]
    idx //= dims[2]
    y = idx % dims[1]
    idx //= dims[1]
    x = idx % dims[0]

    return (x, y, z, d4, d5)


def linear_to_coord(index: int, dims: Dim5D) -> Coord5D:
    """Alias for linear_to_5d."""
    return linear_to_5d(index, dims)


# ============================================================================
# Distance Functions
# ============================================================================

def euclidean_distance_5d(a: Coord5D, b: Coord5D) -> float:
    """Calculate the Euclidean distance between two 5D coordinates.

    Args:
        a: First 5D coordinate.
        b: Second 5D coordinate.

    Returns:
        The Euclidean distance (sqrt of sum of squared differences).
    """
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def distance_5d(a: Coord5D, b: Coord5D) -> float:
    """Alias for euclidean_distance_5d."""
    return euclidean_distance_5d(a, b)


def weighted_distance_5d(
    a: Coord5D,
    b: Coord5D,
    weights: Tuple[float, float, float, float, float],
) -> float:
    """Calculate weighted Euclidean distance between two 5D coordinates.

    This allows different importance to be assigned to each dimension.

    Args:
        a: First 5D coordinate.
        b: Second 5D coordinate.
        weights: Weight for each dimension (x, y, z, d4, d5).

    Returns:
        The weighted Euclidean distance.

    Example:
        >>> a = (1, 2, 3, 4, 5)
        >>> b = (2, 3, 4, 5, 6)
        >>> weights = (1.0, 1.0, 1.0, 0.5, 0.5)
        >>> weighted_distance_5d(a, b, weights)
    """
    return math.sqrt(
        sum(weights[i] * (ai - bi) ** 2 for i, (ai, bi) in enumerate(zip(a, b)))
    )


def chebyshev_distance_5d(a: Coord5D, b: Coord5D) -> float:
    """Calculate the Chebyshev distance between two 5D coordinates.

    Chebyshev distance is the maximum absolute difference along any dimension.

    Args:
        a: First 5D coordinate.
        b: Second 5D coordinate.

    Returns:
        The Chebyshev distance.
    """
    return float(max(abs(ai - bi) for ai, bi in zip(a, b)))


def manhattan_distance_5d(a: Coord5D, b: Coord5D) -> float:
    """Calculate the Manhattan distance between two 5D coordinates.

    Manhattan distance is the sum of absolute differences along each dimension.

    Args:
        a: First 5D coordinate.
        b: Second 5D coordinate.

    Returns:
        The Manhattan distance.
    """
    return float(sum(abs(ai - bi) for ai, bi in zip(a, b)))


# ============================================================================
# Neighbor Generation
# ============================================================================

@lru_cache(maxsize=32)
def neighbour_offsets(radius: float) -> tuple[Coord5D, ...]:
    """Generate all 5D offset vectors within a given radius.

    Results are cached for performance.

    Args:
        radius: Maximum distance from origin (inclusive).

    Returns:
        A tuple of 5D offset vectors (excluding the zero vector).

    Note:
        Only integer offsets are considered. The radius is effectively
        the Chebyshev radius (max coordinate difference).
    """
    if radius <= 0:
        return ()

    r = int(math.ceil(radius))
    offsets: list[Coord5D] = []

    for off in product(range(-r, r + 1), repeat=5):
        if off == (0, 0, 0, 0, 0):
            continue
        # Calculate squared distance directly from the offset
        sq_dist = sum(v * v for v in off)
        if math.sqrt(sq_dist) <= radius:
            offsets.append((off[0], off[1], off[2], off[3], off[4]))

    return tuple(offsets)


def iter_neighbour_coords(
    coord: Coord5D,
    dimensions: Dim5D,
    radius: float,
    include_self: bool = False,
) -> Iterator[Coord5D]:
    """Iterate over all neighboring coordinates within a radius.

    Args:
        coord: Center coordinate.
        dimensions: 5D dimensions for bounds checking.
        radius: Search radius.
        include_self: Whether to include the center coordinate.

    Yields:
        Valid neighboring coordinates within the radius and dimensions.

    Example:
        >>> center = (5, 5, 5, 5, 5)
        >>> dims = (10, 10, 10, 10, 10)
        >>> for neighbor in iter_neighbour_coords(center, dims, 2.0):
        ...     print(neighbor)
    """
    validate_dims(dimensions)
    validate_coord_in_dims(coord, dimensions)

    for offset in neighbour_offsets(radius):
        candidate = tuple(c + oc for c, oc in zip(coord, offset))
        if all(0 <= candidate[i] < dimensions[i] for i in range(5)):
            yield (candidate[0], candidate[1], candidate[2], candidate[3], candidate[4])

    if include_self:
        yield coord


def iter_linear_neighbours(
    center_idx: int,
    dims: Dim5D,
    radius: float,
    include_self: bool = False,
) -> Iterator[int]:
    """Iterate over linear indices of neighbors within a radius.

    Args:
        center_idx: Linear index of the center coordinate.
        dims: 5D dimensions.
        radius: Search radius.
        include_self: Whether to include the center index.

    Yields:
        Linear indices of neighboring coordinates.

    Example:
        >>> for idx in iter_linear_neighbours(12345, (10,10,10,10,10), 2.0):
        ...     print(idx)
    """
    center = linear_to_5d(center_idx, dims)
    for coord in iter_neighbour_coords(center, dims, radius, include_self):
        yield coords_to_linear(coord, dims)


def neighbour_count(dims: Dim5D, radius: float) -> int:
    """Count the number of neighbors within a radius for a given dimension.

    Note: This is an upper bound estimate, as it doesn't account for boundary
    effects (coordinates at the edges have fewer neighbors).

    Args:
        dims: 5D dimensions.
        radius: Search radius.

    Returns:
        Maximum number of neighbors within the radius.
    """
    offsets = neighbour_offsets(radius)
    return len(offsets)


# ============================================================================
# Boundary Coordinates
# ============================================================================

def make_boundary_coord(
    dims: Dim5D,
    dimension: str,
    value: int,
) -> Coord5D:
    """Create a coordinate on a specific dimension boundary.

    This is used for defining input and output layers on specific
    dimensions of the 5D space.

    Args:
        dims: 5D dimensions.
        dimension: Name of the dimension ('x', 'y', 'z', 'd4', 'd5').
        value: Coordinate value on that dimension.

    Returns:
        A 5D coordinate with all other dimensions set to 0.

    Raises:
        ValueError: If the dimension name is unknown or the value is out of bounds.

    Example:
        >>> dims = (10, 10, 10, 10, 10)
        >>> make_boundary_coord(dims, 'x', 5)
        (5, 0, 0, 0, 0)
    """
    if dimension not in DIM_NAMES:
        raise ValueError(
            f"Unknown dimension: {dimension}. "
            f"Valid dimensions: {', '.join(DIM_NAMES.keys())}"
        )

    idx = DIM_NAMES[dimension]
    if value < 0 or value >= dims[idx]:
        raise ValueError(
            f"Value {value} outside dimension {dimension} (0-{dims[idx]-1})"
        )

    coord = [0, 0, 0, 0, 0]
    coord[idx] = value
    return (coord[0], coord[1], coord[2], coord[3], coord[4])


def get_dimension_name(index: int) -> str | None:
    """Get the name of a dimension by its index.

    Args:
        index: Dimension index (0-4).

    Returns:
        Dimension name, or None if index is invalid.
    """
    return DIM_INDICES.get(index)


def get_dimension_index(name: str) -> int | None:
    """Get the index of a dimension by its name.

    Args:
        name: Dimension name ('x', 'y', 'z', 'd4', 'd5').

    Returns:
        Dimension index, or None if name is invalid.
    """
    return DIM_NAMES.get(name)


# ============================================================================
# Utility Functions
# ============================================================================

def total_cells(dims: Dim5D) -> int:
    """Calculate the total number of cells in the 5D grid.

    Args:
        dims: 5D dimensions.

    Returns:
        Product of all dimensions.
    """
    total = 1
    for d in dims:
        total *= d
    return total


def linear_to_coords_batch(
    indices: Iterable[int],
    dims: Dim5D,
) -> Iterator[Coord5D]:
    """Convert multiple linear indices to coordinates.

    Args:
        indices: Iterable of linear indices.
        dims: 5D dimensions.

    Yields:
        5D coordinates for each index.
    """
    for idx in indices:
        yield linear_to_5d(idx, dims)


def coords_to_linear_batch(
    coords: Iterable[Coord5D],
    dims: Dim5D,
) -> Iterator[int]:
    """Convert multiple coordinates to linear indices.

    Args:
        coords: Iterable of 5D coordinates.
        dims: 5D dimensions.

    Yields:
        Linear indices for each coordinate.
    """
    for coord in coords:
        yield coords_to_linear(coord, dims)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Type aliases
    "Coord5D",
    "Dim5D",
    # Constants
    "BITS_PER_DIM",
    "MASK",
    "SHIFTS",
    "DIM_NAMES",
    "DIM_INDICES",
    "MAX_COORD",
    # Validation
    "validate_coord",
    "validate_dims",
    "validate_coord_in_dims",
    "is_valid_coord",
    "is_valid_coord_in_dims",
    # Packing
    "pack_coords",
    "unpack_coords",
    # Linear conversion
    "coords_to_linear",
    "linear_to_5d",
    "linear_to_coord",
    "linear_to_coords_batch",
    "coords_to_linear_batch",
    # Distance
    "euclidean_distance_5d",
    "distance_5d",
    "weighted_distance_5d",
    "chebyshev_distance_5d",
    "manhattan_distance_5d",
    # Neighbors
    "neighbour_offsets",
    "iter_neighbour_coords",
    "iter_linear_neighbours",
    "neighbour_count",
    # Boundary
    "make_boundary_coord",
    "get_dimension_name",
    "get_dimension_index",
    # Utilities
    "total_cells",
]