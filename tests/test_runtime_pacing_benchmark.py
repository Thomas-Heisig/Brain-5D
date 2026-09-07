from __future__ import annotations

from scripts.runtime_pacing_benchmark import (
    build_report,
    run_deterministic_batch,
    run_pacing_case,
)


def test_pacing_case_records_controller_measurements() -> None:
    case = run_pacing_case(10.0, duration_seconds=0.05, dt_ms=2.0)

    assert case["target_hz"] == 10.0
    assert case["achieved_hz"] > 0.0
    assert case["realtime_ratio"] > 0.0
    assert case["dt_ms"] == 2.0
    assert case["measurement_duration_seconds"] >= 0.3
    assert case["warmup_ticks"] >= 1
    assert case["warmup_ticks"] + case["ticks"] == case["simulation_tick"]
    assert "network_step" in case["tick_profile_ms"]


def test_pacing_report_covers_targeted_and_unlimited_modes() -> None:
    report = build_report(duration_seconds=0.05, targets=(1.0, None), dt_ms=1.5)

    assert report["benchmark"] == "runtime_pacing"
    assert report["dt_ms"] == 1.5
    assert [case["target_hz"] for case in report["cases"]] == [1.0, None]
    assert report["cases"][0]["realtime_ratio"] is not None
    assert report["cases"][1]["realtime_ratio"] is None
    assert all(case["ticks"] > 0 for case in report["cases"])


def test_pacing_only_changes_do_not_change_deterministic_batch_results() -> None:
    unlimited = run_deterministic_batch(None, ticks=25, dt_ms=1.0)
    targeted = run_deterministic_batch(10.0, ticks=25, dt_ms=1.0)

    assert unlimited["target_hz"] is None
    assert targeted["target_hz"] == 10.0
    assert unlimited["dt_ms"] == targeted["dt_ms"] == 1.0
    assert unlimited["ticks"] == targeted["ticks"] == 25
    assert unlimited["spikes"] == targeted["spikes"]
    assert unlimited["state_digest"] == targeted["state_digest"]