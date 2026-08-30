"""Digital optical equivalent for a Brain-5D neuron state.

The on-disk optical record is exactly 128 bytes. Five-dimensional coordinates
are not duplicated because Brain-5D already packs five 8-bit coordinates into
the neuron ID.
"""

from __future__ import annotations

import struct
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol

RECORD_SIZE = 128
SPECTRAL_BINS = 32


class NeuronOpticalLike(Protocol):
    """Neuron attributes required to derive an optical sidecar state."""

    v: float
    u: float
    energy: float
    threshold_adaptation: float


def _u16_norm(value: float) -> int:
    return max(0, min(65_535, int(round(value * 65_535.0))))


def _i16_scaled(value: float, scale: float) -> int:
    return max(-32_768, min(32_767, int(round(value * scale))))


def _from_u16_norm(value: int) -> float:
    return value / 65_535.0


@dataclass(slots=True)
class OpticalPointState:
    """Compact optical/electrical/chemical equivalent of one neuron."""

    spectrum: tuple[int, ...] = field(default_factory=lambda: (0,) * SPECTRAL_BINS)
    brightness: float = 0.0
    phase: float = 0.0
    stokes: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    coherence: float = 0.0
    theta: float = 0.0
    phi: float = 0.0
    membrane_v: float = -65.0
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
        """Validate fixed-size optical record constraints."""
        if len(self.spectrum) != SPECTRAL_BINS:
            raise ValueError(f"spectrum must contain {SPECTRAL_BINS} uint16 bins")
        if any(not 0 <= int(value) <= 65_535 for value in self.spectrum):
            raise ValueError("spectrum values must be 0..65535")


def encode_optical_record(
    neuron_id: int,
    tick: int,
    state: OpticalPointState,
) -> bytes:
    """Encode one optical neuron snapshot into the fixed 128-byte record."""
    state.validate()
    out = bytearray(RECORD_SIZE)
    struct.pack_into("<QQ", out, 0, int(neuron_id), int(tick))
    struct.pack_into("<32H", out, 16, *(int(value) for value in state.spectrum))
    struct.pack_into("<H", out, 80, _u16_norm(state.brightness))
    struct.pack_into("<H", out, 82, _u16_norm(state.phase))
    struct.pack_into(
        "<4h",
        out,
        84,
        *(_i16_scaled(value, 32_767.0) for value in state.stokes),
    )
    struct.pack_into("<H", out, 92, _u16_norm(state.coherence))
    struct.pack_into("<H", out, 94, _u16_norm(state.theta))
    struct.pack_into("<H", out, 96, _u16_norm(state.phi))
    struct.pack_into("<h", out, 98, _i16_scaled(state.membrane_v, 100.0))
    struct.pack_into("<h", out, 100, _i16_scaled(state.recovery_u, 100.0))
    struct.pack_into("<H", out, 102, _u16_norm(state.energy))
    struct.pack_into("<H", out, 104, _u16_norm(state.threshold_adaptation))
    chemicals = (
        state.glutamate,
        state.gaba,
        state.dopamine,
        state.serotonin,
        state.acetylcholine,
        state.norepinephrine,
        state.calcium,
        state.sodium,
        state.potassium,
    )
    struct.pack_into(
        "<9H",
        out,
        106,
        *(_u16_norm(value) for value in chemicals),
    )
    struct.pack_into("<I", out, 124, int(state.flags) & 0xFFFF_FFFF)
    return bytes(out)


def decode_optical_record(data: bytes) -> tuple[int, int, OpticalPointState]:
    """Decode a fixed 128-byte optical record."""
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
    chemicals = struct.unpack_from("<9H", data, 106)
    flags = struct.unpack_from("<I", data, 124)[0]
    state = OpticalPointState(
        spectrum=tuple(spectrum),
        brightness=brightness,
        phase=phase,
        stokes=tuple(value / 32_767.0 for value in stokes_raw),  # type: ignore[arg-type]
        coherence=coherence,
        theta=theta,
        phi=phi,
        membrane_v=membrane_v,
        recovery_u=recovery_u,
        energy=energy,
        threshold_adaptation=threshold,
        glutamate=_from_u16_norm(chemicals[0]),
        gaba=_from_u16_norm(chemicals[1]),
        dopamine=_from_u16_norm(chemicals[2]),
        serotonin=_from_u16_norm(chemicals[3]),
        acetylcholine=_from_u16_norm(chemicals[4]),
        norepinephrine=_from_u16_norm(chemicals[5]),
        calcium=_from_u16_norm(chemicals[6]),
        sodium=_from_u16_norm(chemicals[7]),
        potassium=_from_u16_norm(chemicals[8]),
        flags=flags,
    )
    return int(neuron_id), int(tick), state


def state_from_neuron(
    neuron: NeuronOpticalLike,
    spectrum: Iterable[int] | None = None,
) -> OpticalPointState:
    """Create the optical equivalent from a typed neuron surface."""
    spec = (
        tuple(int(value) for value in spectrum)
        if spectrum is not None
        else (0,) * SPECTRAL_BINS
    )
    return OpticalPointState(
        spectrum=spec,
        brightness=max(0.0, min(1.0, (float(neuron.v) + 90.0) / 120.0)),
        membrane_v=float(neuron.v),
        recovery_u=float(neuron.u),
        energy=float(neuron.energy),
        threshold_adaptation=float(neuron.threshold_adaptation),
    )
