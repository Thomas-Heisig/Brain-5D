"""Digital optical equivalent for Brain-5D neuron state.

The on-disk record is exactly 128 bytes. Coordinates are not duplicated because
Brain-5D already encodes the five 8-bit coordinates in ``neuron_id``.

Layout (little endian):
    0..7    neuron_id (uint64; current IDs use 40 bits)
    8..15   tick (uint64)
    16..79  32 spectral bins (uint16 each)
    80..127 optical/electrical/chemical state

This module is intentionally independent of HDF5/Zarr. It defines the stable
binary record that a later chunked backend can store without changing the API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import struct
from typing import Iterable

RECORD_SIZE = 128
SPECTRAL_BINS = 32


def _u16_norm(value: float) -> int:
    return max(0, min(65535, int(round(float(value) * 65535.0))))


def _i16_scaled(value: float, scale: float) -> int:
    return max(-32768, min(32767, int(round(float(value) * scale))))


def _from_u16_norm(value: int) -> float:
    return value / 65535.0


@dataclass(slots=True)
class OpticalPointState:
    """Maximal compact optical equivalent attached to one Brain-5D neuron."""

    spectrum: tuple[int, ...] = field(default_factory=lambda: (0,) * SPECTRAL_BINS)
    brightness: float = 0.0
    phase: float = 0.0               # normalized 0..1 == 0..2pi
    stokes: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    coherence: float = 0.0
    theta: float = 0.0               # normalized 0..1
    phi: float = 0.0                 # normalized 0..1
    membrane_v: float = -65.0        # mV
    recovery_u: float = -13.0
    energy: float = 1.0
    threshold_adaptation: float = 0.0
    glutamate: float = 0.0
    gaba: float = 0.0
    dopamine: float = 0.0
    serotonin: float = 0.0
    acetylcholine: float = 0.0
    norepinephrine: float = 0.0
    calcium: float = 0.0
    sodium: float = 0.0
    potassium: float = 0.0
    flags: int = 0

    def validate(self) -> None:
        if len(self.spectrum) != SPECTRAL_BINS:
            raise ValueError(f"spectrum must contain {SPECTRAL_BINS} uint16 bins")
        if any(not 0 <= int(v) <= 65535 for v in self.spectrum):
            raise ValueError("spectrum values must be 0..65535")


def encode_optical_record(neuron_id: int, tick: int, state: OpticalPointState) -> bytes:
    """Encode one optical neuron snapshot into the fixed 128-byte record."""
    state.validate()
    out = bytearray(RECORD_SIZE)
    struct.pack_into("<QQ", out, 0, int(neuron_id), int(tick))
    struct.pack_into("<32H", out, 16, *(int(v) for v in state.spectrum))
    struct.pack_into("<H", out, 80, _u16_norm(state.brightness))
    struct.pack_into("<H", out, 82, _u16_norm(state.phase))
    struct.pack_into("<4h", out, 84, *(_i16_scaled(v, 32767.0) for v in state.stokes))
    struct.pack_into("<H", out, 92, _u16_norm(state.coherence))
    struct.pack_into("<H", out, 94, _u16_norm(state.theta))
    struct.pack_into("<H", out, 96, _u16_norm(state.phi))
    struct.pack_into("<h", out, 98, _i16_scaled(state.membrane_v, 100.0))
    struct.pack_into("<h", out, 100, _i16_scaled(state.recovery_u, 100.0))
    struct.pack_into("<H", out, 102, _u16_norm(state.energy))
    struct.pack_into("<H", out, 104, _u16_norm(state.threshold_adaptation))
    chemicals = (
        state.glutamate, state.gaba, state.dopamine, state.serotonin,
        state.acetylcholine, state.norepinephrine, state.calcium,
        state.sodium, state.potassium,
    )
    struct.pack_into("<9H", out, 106, *(_u16_norm(v) for v in chemicals))
    struct.pack_into("<I", out, 124, int(state.flags) & 0xFFFFFFFF)
    return bytes(out)


def decode_optical_record(data: bytes) -> tuple[int, int, OpticalPointState]:
    """Decode a fixed optical record."""
    if len(data) != RECORD_SIZE:
        raise ValueError(f"record must be exactly {RECORD_SIZE} bytes")
    neuron_id, tick = struct.unpack_from("<QQ", data, 0)
    spectrum = struct.unpack_from("<32H", data, 16)
    brightness = _from_u16_norm(struct.unpack_from("<H", data, 80)[0])
    phase = _from_u16_norm(struct.unpack_from("<H", data, 82)[0])
    stokes_raw = struct.unpack_from("<4h", data, 84)
    coherence = _from_u16_norm(struct.unpack_from("<H", data, 92)[0])
    theta = _from_u16_norm(struct.unpack_from("<H", data, 94)[0])
    phi = _from_u16_norm(struct.unpack_from("<H", data, 96)[0])
    membrane_v = struct.unpack_from("<h", data, 98)[0] / 100.0
    recovery_u = struct.unpack_from("<h", data, 100)[0] / 100.0
    energy = _from_u16_norm(struct.unpack_from("<H", data, 102)[0])
    threshold = _from_u16_norm(struct.unpack_from("<H", data, 104)[0])
    ch = struct.unpack_from("<9H", data, 106)
    flags = struct.unpack_from("<I", data, 124)[0]
    state = OpticalPointState(
        spectrum=tuple(spectrum), brightness=brightness, phase=phase,
        stokes=tuple(v / 32767.0 for v in stokes_raw), coherence=coherence,
        theta=theta, phi=phi, membrane_v=membrane_v, recovery_u=recovery_u,
        energy=energy, threshold_adaptation=threshold,
        glutamate=_from_u16_norm(ch[0]), gaba=_from_u16_norm(ch[1]),
        dopamine=_from_u16_norm(ch[2]), serotonin=_from_u16_norm(ch[3]),
        acetylcholine=_from_u16_norm(ch[4]), norepinephrine=_from_u16_norm(ch[5]),
        calcium=_from_u16_norm(ch[6]), sodium=_from_u16_norm(ch[7]),
        potassium=_from_u16_norm(ch[8]), flags=flags,
    )
    return neuron_id, tick, state


def state_from_neuron(neuron: object, spectrum: Iterable[int] | None = None) -> OpticalPointState:
    """Create the optical equivalent from the current core Neuron object."""
    spec = tuple(int(v) for v in spectrum) if spectrum is not None else (0,) * SPECTRAL_BINS
    return OpticalPointState(
        spectrum=spec,
        brightness=max(0.0, min(1.0, (float(getattr(neuron, "v", -65.0)) + 90.0) / 120.0)),
        membrane_v=float(getattr(neuron, "v", -65.0)),
        recovery_u=float(getattr(neuron, "u", -13.0)),
        energy=float(getattr(neuron, "energy", 1.0)),
        threshold_adaptation=float(getattr(neuron, "threshold_adaptation", 0.0)),
    )
