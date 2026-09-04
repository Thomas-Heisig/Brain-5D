from __future__ import annotations

from collections.abc import Mapping

from src.research.network_probe import NetworkImpulseProbe
from src.research.temporal import (
    TemporalComparator,
    TemporalStateFrame,
    TemporalStateMemory,
)


class ProbeRuntime:
    def __init__(self) -> None:
        self.ticks = 0
        self.injected: dict[int, float] | None = None

    def inject_current_batch(self, currents: Mapping[int, float]) -> None:
        self.injected = dict(currents)

    def step(self) -> dict[str, object]:
        self.ticks += 1
        return {
            "output_spike_ids": {
                1: (),
                2: (7, 8),
                3: (7,),
                4: (3,),
            }.get(self.ticks, ()),
            "quiescent": self.ticks >= 4,
        }


def frame(tick: int, value: float, digest: str = "digest") -> TemporalStateFrame:
    return TemporalStateFrame.from_mapping(
        tick, digest, {"activity": value, "energy": 1.0}
    )


def test_network_impulse_probe_measures_observed_response() -> None:
    runtime = ProbeRuntime()
    signature = NetworkImpulseProbe(
        source_neuron=3,
        current=0.5,
        max_ticks=10,
        state_digest=lambda: "stable",
    ).run(runtime)

    assert runtime.injected == {3: 0.5}
    assert signature.first_response_latency == 1
    assert signature.last_response_latency == 3
    assert signature.activated_neurons == 3
    assert signature.total_spikes == 4
    assert signature.peak_spike_rate == 2.0
    assert signature.return_latency == 3
    assert signature.recurrent_events == 1
    assert signature.network_state_digest_before == signature.network_state_digest_after


def test_temporal_memory_selects_reference_without_rewinding() -> None:
    memory = TemporalStateMemory(horizons={"fast": 10, "slow": 100})
    memory.append(frame(5, 1.0))
    memory.append(frame(10, 2.0))
    memory.append(frame(20, 3.0))

    fast_reference = memory.reference(30, "fast")
    slow_reference = memory.reference(150, "slow")
    assert fast_reference is not None and fast_reference.tick == 20
    assert slow_reference is not None and slow_reference.tick == 20
    assert memory.reference(9, "fast") is None


def test_temporal_comparator_is_deterministic_and_reports_delta() -> None:
    comparator = TemporalComparator()
    unchanged = comparator.compare(frame(20, 1.0), frame(10, 1.0), horizon="fast")
    changed = comparator.compare(frame(20, 3.0, "new"), frame(10, 1.0), horizon="fast")

    assert unchanged.discrepancy == 0.0
    assert unchanged.changed_metrics == ()
    assert unchanged.digest_changed is False
    assert changed.discrepancy == 1.0
    assert changed.changed_metrics == ("activity",)
    assert changed.digest_changed is True
