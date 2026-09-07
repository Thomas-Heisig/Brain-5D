from __future__ import annotations

from scripts.benchmark_ladder import run_tier


def test_scaling_tier_reports_neuron_and_synapse_profile() -> None:
    report = run_tier(
        neuron_count=100,
        ticks=2,
        seed=42,
        connections_per_neuron=2,
    )

    assert report["neurons"] == 100
    assert report["synapses"] > 0
    assert report["connections_per_neuron_requested"] == 2
    assert report["ticks_per_second"] > 0
    assert report["neurons_per_second"] > 0
    assert report["synapses_per_second"] > 0