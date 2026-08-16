from src.storage.optical_codec import (
    RECORD_SIZE,
    OpticalPointState,
    decode_optical_record,
    encode_optical_record,
)


def test_optical_record_is_exactly_128_bytes_and_roundtrips() -> None:
    state = OpticalPointState(
        spectrum=tuple(range(32)),
        brightness=0.75,
        phase=0.25,
        stokes=(1.0, -0.5, 0.25, 0.0),
        coherence=0.8,
        membrane_v=-63.25,
        recovery_u=-12.5,
        energy=0.9,
        dopamine=0.4,
        calcium=0.6,
        flags=0xA5,
    )
    data = encode_optical_record(12345, 2000, state)
    assert len(data) == RECORD_SIZE == 128
    neuron_id, tick, decoded = decode_optical_record(data)
    assert neuron_id == 12345
    assert tick == 2000
    assert decoded.spectrum == tuple(range(32))
    assert abs(decoded.membrane_v - (-63.25)) < 0.02
    assert abs(decoded.dopamine - 0.4) < 0.001
    assert decoded.flags == 0xA5
