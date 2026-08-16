from collections import deque
from dataclasses import dataclass
from typing import Tuple


@dataclass(slots=True)
class SpikeFrame:
    tick: int
    neuron_ids: Tuple[int, ...]


class SpikeHistory:
    def __init__(self, maxlen: int):
        self.data = deque(maxlen=maxlen)

    def append(self, tick: int, neuron_ids: Tuple[int, ...]) -> None:
        self.data.append(SpikeFrame(tick, neuron_ids))

    def get_frames(self):
        return list(self.data)

    def get_spikes_for_tick(self, tick: int) -> Tuple[int, ...]:
        for frame in self.data:
            if frame.tick == tick:
                return frame.neuron_ids
        return ()
