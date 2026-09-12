"""Focused tests for the live scientific metrics contract."""

from types import SimpleNamespace

from src.dashboard.live_projection import ActivityWindowAccumulator
from src.dashboard.scientific_metrics import build_scientific_metrics


def test_scientific_metrics_preserve_window_and_criticality_values() -> None:
    accumulator = ActivityWindowAccumulator(window_ticks=8)
    accumulator.record_tick(1, [1, 2])
    accumulator.record_tick(2, [1])
    accumulator.record_tick(3, [1, 2, 3])
    accumulator.record_tick(5, [2])

    network = SimpleNamespace(
        current_tick=5,
        neurons={},
        synapses={},
        dimensions=(2, 2, 1, 1, 1),
    )
    snapshot = SimpleNamespace(
        to_json=lambda: {
            "network": {
                "synchrony": 0.25,
                "burst_index": 0.5,
                "clustering_coefficient": 0.1,
                "mean_path_length": 2.0,
            },
            "learning": {"stdp_updates": 3},
            "homeostasis": {"target_rate_hz": 10.0},
            "experiment": {},
        }
    )

    payload = build_scientific_metrics(
        network,
        accumulator,
        snapshot,
        {"status": "live", "frame_age_ticks": 0},
    )

    spike_trains = payload["spike_trains"]
    assert spike_trains["window"]["events"] == 7
    assert spike_trains["isi_ticks"]["available"] is True
    assert spike_trains["fano_factor"]["available"] is True
    assert payload["criticality"]["branching_parameter"]["available"] is True
    assert payload["network"]["synchrony"] == 0.25
    assert payload["learning"]["stdp_updates"] == 3


def test_unavailable_advanced_metrics_are_null() -> None:
    network = SimpleNamespace(
        current_tick=0,
        neurons={},
        synapses={},
        dimensions=(1, 1, 1, 1, 1),
    )
    snapshot = SimpleNamespace(
        to_json=lambda: {
            "network": {},
            "learning": {},
            "homeostasis": {},
            "experiment": {},
        }
    )

    payload = build_scientific_metrics(network, None, snapshot, None)

    assert payload["topology"]["modularity"] is None
    assert payload["criticality"]["lyapunov_exponent"] is None
    assert payload["statistics"]["confidence_intervals"] is None