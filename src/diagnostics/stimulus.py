from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Tuple

from src.core.spatial_index import DIM_NAMES, pack_coords, unpack_coords


@dataclass(slots=True)
class StimulusResult:
    tick: int
    mode: str
    target_ids: Tuple[int, ...]
    amplitudes: Tuple[float, ...]
    total_injected: float


class StimulusEngine:
    def __init__(self, config: dict, rng: random.Random):
        self.config = config
        self.rng = rng
        self.diag = config["diagnostics"]

    def apply(self, network, tick: int) -> StimulusResult:
        mode = self.diag["mode"]
        start = int(self.diag["start_tick"])
        duration = int(self.diag["duration_ticks"])
        amp = float(self.diag["amplitude"])
        targets: list[int] = []
        amps: list[float] = []

        def add(nid: int, current: float) -> None:
            if nid in network.neurons:
                network.inject_current(nid, current)
                targets.append(nid); amps.append(current)

        if mode == "single_pulse":
            if tick == start:
                add(pack_coords(*tuple(self.diag["target_coord"])), amp)
        elif mode == "single_neuron_drive":
            if start <= tick < start + duration:
                add(pack_coords(*tuple(self.diag["target_coord"])), amp)
        elif mode in ("input_plane_pulse", "input_plane_drive"):
            active = tick == start if mode == "input_plane_pulse" else start <= tick < start + duration
            if active:
                dim = DIM_NAMES[self.diag.get("input_plane_dim", "x")]
                for nid in network.neurons:
                    if unpack_coords(nid)[dim] == 0:
                        add(nid, amp)
        elif mode == "poisson_noise":
            if tick >= start:
                rate_hz = float(self.diag.get("poisson_rate_hz", 0.0))
                p = rate_hz * network.dt_ms / 1000.0
                p = min(max(p, 0.0), 1.0)
                noise_amp = float(self.diag.get("poisson_amplitude", amp))
                for nid in network.neurons:
                    if self.rng.random() < p:
                        add(nid, noise_amp)
        elif mode in ("none", None):
            pass
        else:
            raise ValueError(f"Unknown diagnostic mode: {mode}")

        return StimulusResult(tick, str(mode), tuple(targets), tuple(amps), sum(amps))
