"""Izhikevich neuron model used by the sparse Brain-5D core."""

from dataclasses import dataclass


@dataclass(slots=True)
class Neuron:
    """One deterministic spiking neuron with energy and adaptive threshold."""

    neuron_id: int
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -65.0
    u: float = -13.0
    energy: float = 1.0
    spike_cost: float = 0.001
    spike_counter: int = 0
    last_spike_tick: int = -1
    threshold_adaptation: float = 0.0
    last_external_current: float = 0.0
    last_synaptic_current: float = 0.0

    def step(self, input_current: float, tick: int) -> bool:
        """Advance the neuron by one millisecond and return whether it spiked."""
        self.v += 0.5 * (
            0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + input_current
        )
        self.v += 0.5 * (
            0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + input_current
        )
        self.u += self.a * (self.b * self.v - self.u)
        threshold = 30.0 + self.threshold_adaptation
        if self.v >= threshold:
            self.v = self.c
            self.u += self.d
            self.spike_counter += 1
            self.last_spike_tick = tick
            self.energy = max(0.0, self.energy - self.spike_cost)
            return True
        return False
