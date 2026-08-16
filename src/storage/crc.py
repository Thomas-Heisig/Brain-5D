"""CRC32 helpers used by the Brain-5D append-only journal."""

from __future__ import annotations

import zlib

UINT32_MASK = 0xFFFF_FFFF


def compute_crc32(data: bytes, initial: int = 0) -> int:
    """Return the unsigned CRC32 of *data* using the standard library."""
    if not 0 <= initial <= UINT32_MASK:
        raise ValueError("initial CRC must fit uint32")
    return zlib.crc32(data, initial) & UINT32_MASK


def verify_crc32(data: bytes, expected: int) -> bool:
    """Return whether *data* matches the expected unsigned CRC32 value."""
    if not 0 <= expected <= UINT32_MASK:
        return False
    return compute_crc32(data) == expected
