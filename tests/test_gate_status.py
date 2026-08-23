"""Tests for the dynamic Alpha.5 release-gate status builder.

These tests prove the architectural guarantees:

1. Gate A criteria are evidence-based (test files exist), not hardcoded.
2. A disabled runtime feature is NOT automatically failed at the gate.
3. A disabled runtime feature does NOT automatically pass release verification.
4. Config enabled + component missing = ERROR, not "disabled by config".
5. Pytest 239/0 baseline resolves correctly; stale tree digest = STALE.
6. A registered experiment is NOT the same as an executed experiment.
7. Overall Alpha.5 remains OPEN until required Gate B/C criteria pass.
8. No hardcoded stale checklist remains in index.html.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.dashboard.gate_status import (
    G_FAILED,
    G_PASSED,
    G_PENDING,
    G_STALE,
    IMPLEMENTED,
    INTEGRATED,
    VERIFIED,
    L_ACTIVE,
    L_DISABLED,
    L_ERROR,
    GateStatusBuilder,
)
from src.dashboard.operator_bridge import OperatorBridge
from src.controller.runtime import RuntimeController
from src.core import Brain5DConfig, NeuralNetwork


def _build_network(n: int = 50) -> NeuralNetwork:
    config = Brain5DConfig.from_dict(
        {"dimensions": [10, 10, 10, 10, 10], "network": {"initial_connections_per_neuron": 5, "neighbour_radius": 2.0}}
    )
    import random
    rng = random.Random(42)
    network = NeuralNetwork(config, rng)
    from src.core.spatial_index import linear_to_5d
    dims = config.dimensions
    for i in range(n):
        network.add_neuron(linear_to_5d(i, dims))
    network.initialize_random_connections(5, 2.0)
    return network


def _bridge(network: NeuralNetwork) -> OperatorBridge:
    controller = RuntimeController(network)
    return OperatorBridge(controller=controller)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_gate_a_criteria_carry_test_evidence() -> None:
    """Gate A criteria must reference test files as evidence."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    verified_items = [i for i in status["gate_a"]["items"] if i["category"] == "technical_integration"]
    assert len(verified_items) > 0
    for item in verified_items:
        assert item["source"] == "verified_baseline"
        evidence = item.get("evidence")
        assert evidence is not None
        assert isinstance(evidence, dict)
        test_ids = evidence.get("test_ids")
        assert isinstance(test_ids, list)
        assert len(test_ids) > 0


def test_gate_a_passed_criteria_have_existing_test_files() -> None:
    """Gate A criteria marked passed must have all referenced test files existing."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    for item in status["gate_a"]["items"]:
        if item["category"] == "technical_integration" and item["status"] == G_PASSED:
            evidence = item.get("evidence")
            assert evidence is not None
            test_ids = evidence.get("test_ids")
            assert isinstance(test_ids, list)
            for tid in test_ids:
                assert (_repo_root() / tid).exists(), f"test file {tid} should exist"


def test_disabled_structural_does_not_fail_gate() -> None:
    """When self_organization is disabled by config, structural gate criteria must be pending, not failed."""
    config = {"self_organization": {"enabled": False}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    structural_items = [i for i in status["gate_a"]["items"] if i["category"] == "structural_composition"]
    for item in structural_items:
        assert item["status"] != G_FAILED
        assert item["status"] == G_PENDING


def test_disabled_structural_does_not_pass_gate() -> None:
    """When self_organization is disabled by config, structural gate criteria must not pass."""
    config = {"self_organization": {"enabled": False}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    structural_items = [i for i in status["gate_a"]["items"] if i["category"] == "structural_composition"]
    for item in structural_items:
        assert item["status"] != G_PASSED


def test_config_enabled_but_component_missing_is_error() -> None:
    """Config enabled + component missing = ERROR, not disabled."""
    config = {"self_organization": {"enabled": True}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    live_items = {i["key"]: i for i in status["live_runtime"]}
    assert live_items["structural"]["live_status"] == L_ERROR
    assert live_items["structural_journal"]["live_status"] == L_ERROR


def test_config_disabled_structural_live_is_disabled() -> None:
    """Config disabled = DISABLED, not error or unavailable."""
    config = {"self_organization": {"enabled": False}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    live_items = {i["key"]: i for i in status["live_runtime"]}
    assert live_items["structural"]["live_status"] == L_DISABLED


def test_config_disabled_delta_storage_live_is_disabled() -> None:
    """Config says storage off = DISABLED."""
    config = {"storage": {"enabled": False, "runtime": {"enabled": False}}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    live_items = {i["key"]: i for i in status["live_runtime"]}
    assert live_items["delta_storage"]["live_status"] == L_DISABLED


def test_config_enabled_delta_storage_live_is_active() -> None:
    """Config says storage on = ACTIVE."""
    config = {"storage": {"enabled": True, "runtime": {"enabled": True}}}
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root(), config_dict=config)
    status = builder.build()
    live_items = {i["key"]: i for i in status["live_runtime"]}
    assert live_items["delta_storage"]["live_status"] == L_ACTIVE


def test_gate_b_pytest_baseline_resolves() -> None:
    """Gate B must read the real test_baseline.json and report correct counts."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    gate_b_items = {i["id"]: i for i in status["gate_b"]["items"]}
    coll = gate_b_items["B-TEST-COLLECTION"]
    assert coll["status"] in (G_PASSED, G_STALE)
    evidence = coll.get("evidence")
    assert evidence is not None
    assert "collection_errors" in evidence


def test_gate_b_stale_tree_digest_is_stale_not_failed() -> None:
    """Stale tree digest = STALE, not FAILED."""
    repo_root = _repo_root()
    real_baseline = repo_root / "tests" / "test_baseline.json"
    original = real_baseline.read_text(encoding="utf-8")
    try:
        fake = json.loads(original)
        fake["tested_tree_digest"] = "0" * 64
        real_baseline.write_text(json.dumps(fake), encoding="utf-8")
        builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=repo_root)
        status = builder.build()
        gate_b_items = {i["id"]: i for i in status["gate_b"]["items"]}
        assert gate_b_items["B-TEST-COLLECTION"]["status"] == G_STALE
        assert gate_b_items["B-ZERO-FAILURES"]["status"] == G_STALE
        assert gate_b_items["B-FULL-SUITE"]["status"] == G_STALE
    finally:
        real_baseline.write_text(original, encoding="utf-8")


def test_gate_b_structural_proofs_remain_pending() -> None:
    """Structural E2E proofs must remain pending."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    proof_items = [i for i in status["gate_b"]["items"] if i["category"] == "structural_e2e"]
    assert len(proof_items) == 10
    for item in proof_items:
        assert item["status"] == G_PENDING


def test_gate_c_registered_experiment_not_executed() -> None:
    """Registered experiment is not executed (status=not_started)."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    gate_c_items = {i["id"]: i for i in status["gate_c"]["items"]}
    assert gate_c_items["C-EXP-DET-REGISTERED"]["status"] == G_PASSED
    assert gate_c_items["C-EXP-DET-EXECUTED"]["status"] == G_PENDING


def test_experiment_completed_means_executed() -> None:
    """experiment_status=completed means executed."""
    repo_root = _repo_root()
    manifest_path = repo_root / "research" / "experiments" / "EXP-DET-0001" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(original)
        manifest["experiment_status"] = "completed"
        manifest["timestamp"] = "2026-08-23T12:00:00"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=repo_root)
        assert builder._experiment_executed("EXP-DET-0001") is True
    finally:
        manifest_path.write_text(original, encoding="utf-8")


def test_experiment_running_means_not_executed() -> None:
    """experiment_status=running means NOT executed (attempted, not complete)."""
    repo_root = _repo_root()
    manifest_path = repo_root / "research" / "experiments" / "EXP-DET-0001" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(original)
        manifest["experiment_status"] = "running"
        manifest["timestamp"] = "2026-08-23T12:00:00"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=repo_root)
        assert builder._experiment_executed("EXP-DET-0001") is False
    finally:
        manifest_path.write_text(original, encoding="utf-8")


def test_experiment_failed_means_not_executed() -> None:
    """experiment_status=failed means NOT executed (attempted, invalid)."""
    repo_root = _repo_root()
    manifest_path = repo_root / "research" / "experiments" / "EXP-DET-0001" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(original)
        manifest["experiment_status"] = "failed"
        manifest["timestamp"] = "2026-08-23T12:00:00"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=repo_root)
        assert builder._experiment_executed("EXP-DET-0001") is False
    finally:
        manifest_path.write_text(original, encoding="utf-8")


def test_experiment_template_means_not_executed() -> None:
    """experiment_status=template means NOT executed (never ran)."""
    repo_root = _repo_root()
    manifest_path = repo_root / "research" / "experiments" / "EXP-DET-0001" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(original)
        manifest["experiment_status"] = "template"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=repo_root)
        assert builder._experiment_executed("EXP-DET-0001") is False
    finally:
        manifest_path.write_text(original, encoding="utf-8")


def test_overall_alpha5_remains_open() -> None:
    """Alpha.5 must NOT be passed overall."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    assert status["overall"] != G_PASSED
    assert status["overall"] in (G_PENDING, G_STALE)


def test_no_hardcoded_gate_checklist_in_index_html() -> None:
    """index.html must not contain hardcoded gate-todo/gate-done items."""
    html_path = _repo_root() / "src" / "dashboard" / "static" / "index.html"
    content = html_path.read_text(encoding="utf-8")
    assert "gate-todo" not in content
    assert "gate-done" not in content
    assert 'id="gate-a-list"' in content
    assert 'id="gate-b-list"' in content
    assert 'id="gate-c-list"' in content


def test_live_runtime_excludes_tests() -> None:
    """Tests are not a live runtime subsystem."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    live_keys = [i["key"] for i in status["live_runtime"]]
    assert "tests" not in live_keys


def test_live_runtime_uses_research_source_key() -> None:
    """Live runtime must use 'research_source' not 'research'."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    live_keys = [i["key"] for i in status["live_runtime"]]
    assert "research_source" in live_keys
    assert "research" not in live_keys


def test_research_registry_counts_are_correct() -> None:
    """Registry counts must come from the typed ResearchRegistry API."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    counts = builder._research_registry_counts()
    assert counts["questions"] >= 27
    assert counts["hypotheses"] >= 27
    assert counts["claims"] >= 5
    assert counts["sources"] >= 8


def test_three_separate_gates_exist() -> None:
    """The response must contain gate_a, gate_b, gate_c separately."""
    builder = GateStatusBuilder(bridge=_bridge(_build_network()), repo_root=_repo_root())
    status = builder.build()
    assert "gate_a" in status
    assert "gate_b" in status
    assert "gate_c" in status
    assert "live_runtime" in status
    assert len(status["gate_a"]["items"]) > 0
    assert len(status["gate_b"]["items"]) > 0
    assert len(status["gate_c"]["items"]) > 0
