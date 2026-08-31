from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, cast

from src.core.spatial_index import DIM_NAMES, pack_coords, unpack_coords


@dataclass(slots=True)
class StimulusResult:
    tick: int
    mode: str
    target_ids: tuple[int, ...]
    amplitudes: tuple[float, ...]
    total_injected: float


class StimulusEngine:
    """Configurable stimulus injection engine.

    The ``config`` dict must contain a ``"diagnostics"`` key with the
    stimulus parameters (mode, amplitude, timing, target coordinates, etc.).
    """

    def __init__(self, config: dict[str, Any], rng: random.Random) -> None:
        self.config = config
        self.rng = rng
        diag_raw = config.get("diagnostics", {})
        if not isinstance(diag_raw, dict):
            raise ValueError("config['diagnostics'] must be a dictionary")
        self.diag: dict[str, Any] = cast("dict[str, Any]", diag_raw)

    def apply(self, network: Any, tick: int) -> StimulusResult:
        mode: str | None = cast("str | None", self.diag.get("mode"))
        start = int(cast("int | float", self.diag.get("start_tick", 0)))
        duration = int(cast("int | float", self.diag.get("duration_ticks", 0)))
        amp = float(cast("int | float", self.diag.get("amplitude", 0.0)))
        targets: list[int] = []
        amps: list[float] = []

        def add(nid: int, current: float) -> None:
            if nid in network.neurons:
                network.inject_current(nid, current)
                targets.append(nid)
                amps.append(current)

        if mode == "single_pulse":
            if tick == start:
                target_coord = cast(
                    "list[Any] | tuple[Any, ...]", self.diag.get("target_coord", ())
                )
                add(pack_coords(*tuple(target_coord)), amp)
        elif mode == "single_neuron_drive":
            if start <= tick < start + duration:
                target_coord = cast(
                    "list[Any] | tuple[Any, ...]", self.diag.get("target_coord", ())
                )
                add(pack_coords(*tuple(target_coord)), amp)
        elif mode in ("input_plane_pulse", "input_plane_drive"):
            active = (
                tick == start
                if mode == "input_plane_pulse"
                else start <= tick < start + duration
            )
            if active:
                dim_name = cast("str", self.diag.get("input_plane_dim", "x"))
                dim = DIM_NAMES.get(dim_name, 0)
                for nid in network.neurons:
                    if unpack_coords(nid)[dim] == 0:
                        add(nid, amp)
        elif mode == "poisson_noise":
            if tick >= start:
                rate_hz = float(
                    cast("int | float", self.diag.get("poisson_rate_hz", 0.0))
                )
                p = rate_hz * network.dt_ms / 1000.0
                p = min(max(p, 0.0), 1.0)
                noise_amp = float(
                    cast("int | float", self.diag.get("poisson_amplitude", amp))
                )
                for nid in network.neurons:
                    if self.rng.random() < p:
                        add(nid, noise_amp)
        elif mode in ("none", None):
            pass
        else:
            raise ValueError(f"Unknown diagnostic mode: {mode}")

        return StimulusResult(tick, str(mode), tuple(targets), tuple(amps), sum(amps))
