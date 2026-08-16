"""CRC tests for the Brain-5D journal."""

from src.storage.crc import compute_crc32, verify_crc32


def test_crc32_known_vector() -> None:
    assert compute_crc32(b"123456789") == 0xCBF43926


def test_crc32_roundtrip() -> None:
    payload = b"brain-5d-journal"
    crc = compute_crc32(payload)
    assert verify_crc32(payload, crc)
    assert not verify_crc32(payload + b"x", crc)


def test_crc32_rejects_invalid_initial() -> None:
    try:
        compute_crc32(b"x", -1)
    except ValueError:
        return
    raise AssertionError("negative initial CRC must be rejected")
