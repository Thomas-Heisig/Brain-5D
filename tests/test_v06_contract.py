from __future__ import annotations

from pathlib import Path

import pytest

from scripts.benchmark_ladder import run_tier
from src.diagnostics.performance_contract import (
    PerformanceContractError,
    evaluate_pacing,
    evaluate_runtime_profile,
    evaluate_scaling_tier,
    load_performance_budgets,
)
from src.storage.b5d import B5DSnapshotWriter, FORMAT_VERSION
from src.storage.delta_journal import JOURNAL_VERSION
from src.storage.v06_contract import (
    V06CompatibilityError,
    V06_CONTRACT,
    migration_plan,
    sha256_file,
    validate_v06_snapshot,
)


def _budgets() -> dict[str, object]:
    return load_performance_budgets(Path("configs/v06_performance_budgets.json"))


def test_v06_persistence_contract_freezes_existing_binary_formats() -> None:
    assert V06_CONTRACT.snapshot_format_version == FORMAT_VERSION == 1
    assert V06_CONTRACT.journal_format_version == JOURNAL_VERSION == 1
    assert migration_plan(FORMAT_VERSION, JOURNAL_VERSION) == "NOOP_FROZEN_FORMAT"
    with pytest.raises(V06CompatibilityError):
        migration_plan(FORMAT_VERSION + 1, JOURNAL_VERSION)
    with pytest.raises(V06CompatibilityError):
        migration_plan(FORMAT_VERSION, JOURNAL_VERSION + 1)


def test_v06_snapshot_migration_and_rollback_are_byte_identity(tmp_path: Path) -> None:
    from scripts.benchmark_ladder import build_network

    network = build_network(8, seed=42, connections_per_neuron=1)
    path = tmp_path / "runtime.b5d"
    B5DSnapshotWriter(restart_capable=True).write(path, network)
    before = sha256_file(path)

    receipt = validate_v06_snapshot(path)

    assert receipt["compatible"] is True
    assert receipt["migration"] == "NOOP_FROZEN_FORMAT"
    assert receipt["rollback"] == "BYTE_IDENTITY"
    assert receipt["sha256_before"] == before
    assert receipt["sha256_after"] == before == sha256_file(path)


def test_scaling_benchmark_reports_explicit_memory_and_tick_cost() -> None:
    tier = run_tier(neuron_count=50, ticks=2, seed=42, connections_per_neuron=1)
    assert tier["python_peak_memory_bytes"] > 0
    assert tier["python_peak_bytes_per_neuron"] > 0
    assert tier["mean_tick_cost_ms"] >= 0
    assert evaluate_scaling_tier(tier, _budgets()) == ()


def test_performance_contract_covers_every_runtime_phase() -> None:
    phases = {
        "learning": 0.1,
        "homeostasis": 0.1,
        "structural": 0.1,
        "embodiment": 0.1,
        "neural_symbiosis_msba": 0.1,
        "dashboard_telemetry": 0.1,
        "storage": 0.1,
    }
    assert (
        evaluate_runtime_profile(
            tick_latency_ms=1.0, phases_ms=phases, budgets=_budgets()
        )
        == ()
    )
    incomplete = dict(_budgets())
    incomplete["phases_ms_per_tick"] = {"learning": 1.0}
    with pytest.raises(PerformanceContractError, match="missing subsystem"):
        evaluate_runtime_profile(
            tick_latency_ms=1.0, phases_ms=phases, budgets=incomplete
        )


def test_targeted_and_unlimited_pacing_have_explicit_acceptance_criteria() -> None:
    budgets = _budgets()
    assert evaluate_pacing(
        target_hz=100.0,
        achieved_hz=95.0,
        realtime_ratio=0.095,
        dt_seconds=0.001,
        runtime_mode="TARGETED",
        budgets=budgets,
    ) == ()
    assert evaluate_pacing(
        target_hz=None,
        achieved_hz=1250.0,
        realtime_ratio=1.25,
        dt_seconds=0.001,
        runtime_mode="MAX",
        budgets=budgets,
    ) == ()
    violations = evaluate_pacing(
        target_hz=100.0,
        achieved_hz=50.0,
        realtime_ratio=0.05,
        dt_seconds=0.001,
        runtime_mode="COMPUTE LIMITED",
        budgets=budgets,
    )
    assert any("below" in item for item in violations)
