"""Scientific contract tests for the registered STDP pair-timing protocol."""

from __future__ import annotations

from src.research.stdp_pair_timing import DELTA_T_MS, REPLICATIONS, run_pair_timing_protocol


def test_pair_timing_protocol_measures_expected_asymmetry() -> None:
    result = run_pair_timing_protocol()
    measurements = result["measurements"]
    changes = {row["delta_t_ms"]: row["mean_delta_weight"] for row in measurements}

    assert result["summary"]["hypothesis_supported"] is True
    assert result["summary"]["total_replications"] == len(DELTA_T_MS) * REPLICATIONS
    assert all(changes[delta_t] > 0 for delta_t in DELTA_T_MS if delta_t > 0)
    assert all(changes[delta_t] < 0 for delta_t in DELTA_T_MS if delta_t < 0)
    assert changes[0] == 0.0