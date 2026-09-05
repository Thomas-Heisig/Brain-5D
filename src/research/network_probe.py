"""Deterministic network impulse probes and observable response signatures."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol


class ImpulseRuntime(Protocol):
    """Minimal runtime boundary required by :class:`NetworkImpulseProbe`."""

    def inject_current_batch(self, currents: Mapping[int, float]) -> None: ...

    def step(self) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class NetworkResponseSignature:
    """Measured response to one controlled input impulse."""

    first_response_latency: int | None
    last_response_latency: int | None
    activated_neurons: int
    total_spikes: int
    peak_spike_rate: float
    propagation_depth: int
    recurrent_events: int
    return_latency: int | None
    spike_sequence: tuple[tuple[int, int], ...] = ()
    network_state_digest_before: str | None = None
    network_state_digest_after: str | None = None
    ticks_executed: int = 0
    delivered_synaptic_events: int = 0
    synaptic_activity_ticks: int = 0
    max_synaptic_current_targets: int = 0
    total_synapses: int = 0
    stopped_on_quiescence: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "first_response_latency": self.first_response_latency,
            "last_response_latency": self.last_response_latency,
            "activated_neurons": self.activated_neurons,
            "total_spikes": self.total_spikes,
            "peak_spike_rate": self.peak_spike_rate,
            "propagation_depth": self.propagation_depth,
            "recurrent_events": self.recurrent_events,
            "return_latency": self.return_latency,
            "spike_sequence": [
                {"tick": tick, "neuron_id": neuron_id}
                for tick, neuron_id in self.spike_sequence
            ],
            "network_state_digest_before": self.network_state_digest_before,
            "network_state_digest_after": self.network_state_digest_after,
            "ticks_executed": self.ticks_executed,
            "delivered_synaptic_events": self.delivered_synaptic_events,
            "synaptic_activity_ticks": self.synaptic_activity_ticks,
            "max_synaptic_current_targets": self.max_synaptic_current_targets,
            "total_synapses": self.total_synapses,
            "stopped_on_quiescence": self.stopped_on_quiescence,
        }


class NetworkImpulseProbe:
    """Inject one bounded impulse and summarize only observed runtime output.

    ``max_ticks`` is the hard upper bound. ``min_ticks`` defines the minimum
    observation window that must be executed even if the runtime reports an
    earlier quiescent state. This distinction is important for registered
    experiments: a requested observation window must not silently collapse to a
    shorter run just because the network becomes temporarily quiescent.
    """

    def __init__(
        self,
        *,
        source_neuron: int,
        current: float = 1.0,
        max_ticks: int = 100,
        min_ticks: int = 0,
        state_digest: Callable[[], str] | None = None,
    ) -> None:
        if max_ticks < 1:
            raise ValueError("max_ticks must be positive")
        if min_ticks < 0:
            raise ValueError("min_ticks must not be negative")
        if min_ticks > max_ticks:
            raise ValueError("min_ticks must not exceed max_ticks")
        self.source_neuron = source_neuron
        self.current = current
        self.max_ticks = max_ticks
        self.min_ticks = min_ticks
        self.state_digest = state_digest

    def run(self, runtime: ImpulseRuntime) -> NetworkResponseSignature:
        """Run until quiescence after ``min_ticks`` or until ``max_ticks``."""
        before = self.state_digest() if self.state_digest else None
        runtime.inject_current_batch({self.source_neuron: self.current})
        response_ticks: list[int] = []
        response_neurons: set[int] = set()
        total_spikes = 0
        peak_rate = 0.0
        recurrent_events = 0
        return_latency: int | None = None
        spike_sequence: list[tuple[int, int]] = []
        ticks_executed = 0
        delivered_synaptic_events = 0
        synaptic_activity_ticks = 0
        max_synaptic_current_targets = 0
        total_synapses = 0
        stopped_on_quiescence = False

        for tick in range(self.max_ticks):
            result = runtime.step()
            ticks_executed = tick + 1
            raw_ids = result.get("spike_ids")
            if raw_ids is None:
                raw_ids = result.get("output_spike_ids")
            if raw_ids is None:
                raw_ids = ()
            spike_ids = tuple(int(value) for value in raw_ids)
            output_ids = tuple(
                int(value) for value in result.get("output_spike_ids", spike_ids)
            )
            delivered = int(result.get("delivered_events", 0) or 0)
            synaptic_targets = int(result.get("synaptic_current_targets", 0) or 0)
            delivered_synaptic_events += delivered
            if delivered > 0 or synaptic_targets > 0:
                synaptic_activity_ticks += 1
            max_synaptic_current_targets = max(
                max_synaptic_current_targets, synaptic_targets
            )
            total_synapses = max(
                total_synapses, int(result.get("total_synapses", 0) or 0)
            )
            if spike_ids:
                spike_sequence.extend((tick, neuron_id) for neuron_id in spike_ids)
                response_neurons.update(spike_ids)
                total_spikes += len(spike_ids)
                peak_rate = max(peak_rate, float(len(spike_ids)))
                if (
                    self.source_neuron in spike_ids
                    and return_latency is None
                    and tick > 0
                ):
                    return_latency = tick
                if tick > 0 and self.source_neuron in spike_ids:
                    recurrent_events += 1
            if output_ids:
                response_ticks.append(tick)
            if result.get("quiescent", False) and ticks_executed >= self.min_ticks:
                stopped_on_quiescence = ticks_executed < self.max_ticks
                break

        after = self.state_digest() if self.state_digest else None
        return NetworkResponseSignature(
            first_response_latency=response_ticks[0] if response_ticks else None,
            last_response_latency=response_ticks[-1] if response_ticks else None,
            activated_neurons=len(response_neurons),
            total_spikes=total_spikes,
            peak_spike_rate=peak_rate,
            propagation_depth=(
                (response_ticks[-1] - response_ticks[0] + 1) if response_ticks else 0
            ),
            recurrent_events=recurrent_events,
            return_latency=return_latency,
            spike_sequence=tuple(spike_sequence),
            network_state_digest_before=before,
            network_state_digest_after=after,
            ticks_executed=ticks_executed,
            delivered_synaptic_events=delivered_synaptic_events,
            synaptic_activity_ticks=synaptic_activity_ticks,
            max_synaptic_current_targets=max_synaptic_current_targets,
            total_synapses=total_synapses,
            stopped_on_quiescence=stopped_on_quiescence,
        )
