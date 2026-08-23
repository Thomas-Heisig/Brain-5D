from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class SpikeFrame:
    tick: int
    neuron_ids: tuple[int, ...]


class SpikeHistory:
    def __init__(self, maxlen: int) -> None:
        self.data: deque[SpikeFrame] = deque(maxlen=maxlen)

    def append(self, tick: int, neuron_ids: tuple[int, ...]) -> None:
        self.data.append(SpikeFrame(tick, neuron_ids))

    def get_frames(self) -> list[SpikeFrame]:
        return list(self.data)

    def get_spikes_for_tick(self, tick: int) -> tuple[int, ...]:
        for frame in self.data:
            if frame.tick == tick:
                return frame.neuron_ids
        return ()
