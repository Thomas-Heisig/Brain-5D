"""Engineering validation, not confirmatory biological evidence."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.dashboard.experiment_workflow import (
    ExperimentWorkflowService,
    WorkflowValidationError,
)
from src.embodiment.joint_world import JointParameters, JointWorld
from src.research.connectome_embodiment import RUNNERS, run_protocol
from src.research.connectome_governance import (
    PROTECTED_HYPOTHESES,
    ConnectomeGovernanceError,
    connectome_catalog,
    guard_connectome_launch,
    guard_connectome_promotion,
)
from src.research.connectome_reference import (
    load_reference,
    synthetic_graph,
    transform_graph,
)
from src.research.protocol_registry import (
    PreregistrationError,
    load_operational_protocols,
)
from src.research.registry import ResearchRegistry

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"


def config() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "configs/learning_experiment.yaml").read_text())


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), 0.0, -1.0])
def test_body_rejects_invalid_inertia(bad: float) -> None:
    with pytest.raises(ValueError):
        JointParameters(inertia_kg_m2=bad)


def test_body_has_real_feedback_and_hard_stops() -> None:
    body = JointWorld(JointParameters())
    for _ in range(500):
        body.advance(1.0, 0.001)
    assert body.q_rad == body.parameters.upper_rad
    assert body.contact_count > 0
    assert body.saturation_count == 500
    assert body.modelled_absolute_work_j > 0
    before = body.q_rad
    body.advance(-0.01, 0.001, blocked=True)
    assert body.q_rad == before
    with pytest.raises(ValueError):
        body.advance(float("nan"), 0.001)


@pytest.mark.parametrize(
    "condition", ["degree_preserving", "weight_shuffle", "random_edges"]
)
def test_graph_controls_preserve_declared_budgets(condition: str) -> None:
    parent = synthetic_graph(101)
    control = transform_graph(parent, condition, 101)
    assert control.node_ids == parent.node_ids
    assert len(control.edges) == len(parent.edges)
    assert sorted(e.weight for e in control.edges) == sorted(
        e.weight for e in parent.edges
    )
    assert sorted(e.delay_ticks for e in control.edges) == sorted(
        e.delay_ticks for e in parent.edges
    )
    assert control.provenance["data_kind"] == "SYNTHETIC"
    assert len({(e.source, e.target) for e in control.edges}) == len(control.edges)
    assert all(e.source != e.target for e in control.edges)
    assert control.digest() == transform_graph(parent, condition, 101).digest()
    if condition == "degree_preserving":
        assert control.degrees() == parent.degrees()
        assert {(e.source, e.target) for e in control.edges} != {
            (e.source, e.target) for e in parent.edges
        }


def reference_payload() -> dict[str, Any]:
    graph = synthetic_graph(101)
    provenance = dict(graph.provenance)
    for key in (
        "source_url",
        "license",
        "retrieved_on",
        "selection_rule",
        "transformations",
        "transmitter_uncertainty",
        "adapter_version",
    ):
        provenance[key] = "SYNTHETIC test fixture"
    return dict(
        schema_version="1.0",
        node_ids=list(graph.node_ids),
        edges=[asdict(edge) for edge in graph.edges],
        provenance=provenance,
    )


def test_reference_import_is_bounded_and_hash_checked(tmp_path: Path) -> None:
    path = tmp_path / "reference.json"
    path.write_text(json.dumps(reference_payload()))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    graph = load_reference(path, expected_sha256=digest)
    assert graph.node_ids == tuple(map(str, range(6)))
    with pytest.raises(ValueError, match="hash mismatch"):
        load_reference(path, expected_sha256="0" * 64)
    with pytest.raises(ValueError, match="byte budget"):
        load_reference(path, expected_sha256=digest, max_bytes=20)
    with pytest.raises(ValueError):
        load_reference(path, expected_sha256=digest, max_nodes=3)


@pytest.mark.parametrize(
    "defect", ["missing_license", "duplicate", "nan", "unknown", "bool_delay"]
)
def test_reference_rejects_corrupt_schema(tmp_path: Path, defect: str) -> None:
    payload = reference_payload()
    if defect == "missing_license":
        del payload["provenance"]["license"]
    elif defect == "duplicate":
        payload["node_ids"].append("0")
    elif defect == "nan":
        payload["edges"][0]["weight"] = float("nan")
    elif defect == "unknown":
        payload["edges"][0]["target"] = "not-a-node"
    else:
        payload["edges"][0]["delay_ticks"] = True
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_reference(
            path, expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        )


@pytest.mark.parametrize("protocol", sorted(RUNNERS))
def test_native_screens_execute_registered_arms(protocol: str) -> None:
    runs = run_protocol(protocol, config(), ticks=120)
    contract = next(p for p in connectome_catalog(RESEARCH) if p["id"] == protocol)
    assert len(runs) == 3 * len(contract["conditions"])
    assert {run.condition for run in runs} == set(contract["conditions"])
    for run in runs:
        assert run.runtime_error is None
        assert run.metrics["ticks_executed"] == 120
        assert run.metrics["data_kind"] == "SYNTHETIC"
        assert run.metrics["biological_replication"] is False
        assert run.metrics["learning_enabled"] is False
        assert run.metrics["measured_hardware_energy_j"] is None
        assert len(run.metrics["trace"]) == 120
        assert len(run.metrics["preregistration_sha256"]) == 64
        assert run.metrics["gateway_state_before"] != run.metrics["gateway_state_after"]
        assert run.state_digest_before != run.state_digest_after
    assert sum(run.metrics["total_spikes"] for run in runs) > 0
    assert sum(run.metrics["synaptic_events_delivered"] for run in runs) > 0


def test_batching_does_not_change_scientific_state() -> None:
    runs = run_protocol("embodied_timing_v1", config(), ticks=121)
    for seed in (101, 102, 103):
        batch_runs = [
            run
            for run in runs
            if run.seed == seed and run.condition.startswith("batch_")
        ]
        assert len(batch_runs) == 3
        assert len({run.state_digest_after for run in batch_runs}) == 1
        assert len({run.metrics["closed_loop_state_sha256"] for run in batch_runs}) == 1
        assert len({run.metrics["trace_sha256"] for run in batch_runs}) == 1
        assert all(run.metrics["batch_digest_identity"] for run in batch_runs)
    repeated = run_protocol("embodied_timing_v1", config(), ticks=121)
    assert [run.metrics["trace_sha256"] for run in runs] == [
        run.metrics["trace_sha256"] for run in repeated
    ]


def test_motor_disconnect_and_donor_are_observable() -> None:
    runs = run_protocol("embodied_controller_attribution_v1", config(), ticks=120)
    for run in runs:
        if run.condition == "disconnected_motor":
            assert run.metrics["nonzero_action_ticks"] == 0
        if run.condition == "shuffled_motor":
            assert run.metrics["donor_motor_sha256"]
        if run.condition == "controller_only":
            assert run.metrics["controller"] == "PD_ONLY_IGNORES_SNN"


def test_registry_and_draft_guards() -> None:
    registry = ResearchRegistry(RESEARCH / "registry").load_all()
    records = connectome_catalog(RESEARCH)
    assert len(records) == 12
    assert {item["hypothesis"] for item in records} == PROTECTED_HYPOTHESES
    for item in records:
        question, hypothesis, protocol = (
            item["research_question"],
            item["hypothesis"],
            item["id"],
        )
        assert hypothesis in registry.questions[question].hypotheses
        assert registry.hypotheses[hypothesis].research_question == question
        for source in item["sources"]:
            assert source in registry.sources
        if protocol in RUNNERS:
            guard_connectome_launch(RESEARCH, question, hypothesis, protocol)
        else:
            with pytest.raises(ConnectomeGovernanceError):
                guard_connectome_launch(RESEARCH, question, hypothesis, protocol)
        with pytest.raises(ConnectomeGovernanceError):
            guard_connectome_launch(RESEARCH, question, hypothesis, "runtime_ticks_v1")
        with pytest.raises(ConnectomeGovernanceError):
            guard_connectome_promotion(hypothesis, "CLAIM-TEST")


def test_existing_studies_keep_their_permission() -> None:
    guard_connectome_launch(
        RESEARCH, "RQ-MSBA-E05", "H-MSBA-E05-A", "msba_modality_compensation_v1"
    )
    guard_connectome_launch(
        RESEARCH, "RQ-REG-002", "H-REG-002-A", "closed_loop_regulation_v1"
    )


def test_workflow_cannot_fallback_or_override_draft_status() -> None:
    service = ExperimentWorkflowService(RESEARCH)
    with pytest.raises(WorkflowValidationError, match="CONNECTOME_ADAPTER"):
        service.run_science(
            {
                "experiment_id": "EXP-TEST-NO-FALLBACK",
                "question_id": "RQ-EMB-003",
                "hypothesis_id": "H-EMB-003-A",
                "protocol": "science_suite_v1",
                "title": "Invalid substitution",
                "conditions": "draft",
                "ticks": 120,
            }
        )


def test_protocol_fragments_reject_duplicate_ids(tmp_path: Path) -> None:
    directory = tmp_path / "protocols"
    directory.mkdir()
    payload = {"protocols": [{"id": "duplicate"}]}
    for name in ("a.operational.json", "b.operational.json"):
        (directory / name).write_text(json.dumps(payload))
    with pytest.raises(PreregistrationError, match="duplicate"):
        load_operational_protocols(tmp_path)


def test_wesen_missing_values_are_not_zero() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is not installed; dedicated browser CI remains required")
    for name, function in (("wesen-base.js", "num"), ("wesen-anatomy-v3.js", "finite")):
        source = ROOT / "src/dashboard/static" / name
        script = (
            """const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
const cutoff = src.lastIndexOf('window.Brain5D');
const sandbox = {window: {}, document: {readyState: 'loading', addEventListener: () => {}}, setTimeout: () => 0};
vm.runInNewContext(src.slice(0, cutoff) + '\\n globalThis.readMetric = """
            + function
            + """;', sandbox);
for (const missing of [null, undefined, '', '   ', false, true, [], {}, NaN, Infinity]) {
 if (sandbox.readMetric(missing) !== null) throw Error('Missing telemetry was converted to a number');
}
if (sandbox.readMetric(0) !== 0 || sandbox.readMetric('1.5') !== 1.5) throw Error('Observed values lost');
"""
        )
        subprocess.run(
            [node, "-e", script, str(source)],
            check=True,
            capture_output=True,
            text=True,
        )


def test_design_lock_fails_closed_on_changed_conditions(tmp_path: Path) -> None:
    from src.research.connectome_governance import verify_design_lock

    for folder in ("protocols", "preregistrations"):
        shutil.copytree(RESEARCH / folder, tmp_path / folder)
    verify_design_lock(tmp_path)
    path = tmp_path / "preregistrations/connectome/embodied_closed_loop_v1.json"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ConnectomeGovernanceError, match="Design changed"):
        verify_design_lock(tmp_path)


def test_source_metadata_survives_registry_serialization() -> None:
    from src.research.registry import Source

    source = (
        ResearchRegistry(RESEARCH / "registry").load_all().sources["SRC-CONN-EON-2026"]
    )
    record = source.to_dict()
    assert record["source_type"] == "company_technical_report"
    assert record["verified_on"] == "2026-09-09"
    assert record["limitations"]
    assert Source(record).to_dict() == record


def test_full_integrity_gate() -> None:
    from scripts.check_connectome_integrity import check

    result = check(RESEARCH)
    assert len(result["native_exploratory_protocols"]) == 6
    assert len(result["blocked_designs"]) == 6
    assert result["automatic_evidence_promotion"] is False


def test_existing_science_workflow_records_body_sidecar(tmp_path: Path) -> None:
    for folder in ("registry", "protocols", "preregistrations", "literature", "ethics"):
        shutil.copytree(RESEARCH / folder, tmp_path / "research" / folder)
    (tmp_path / "configs").mkdir()
    shutil.copy2(
        ROOT / "configs/learning_experiment.yaml",
        tmp_path / "configs/learning_experiment.yaml",
    )
    research_root = tmp_path / "research"
    service = ExperimentWorkflowService(research_root)
    body: dict[str, object] = {
        "experiment_id": "EXP-CONN-TEST-001",
        "question_id": "RQ-EMB-001",
        "hypothesis_id": "H-EMB-001-B",
        "protocol": "embodied_closed_loop_v1",
        "title": "Engineering test",
        "conditions": "all registered arms",
        "ticks": 120,
        "seeds": "101,102,103",
    }
    service.run_science(body)
    folder = research_root / "experiments/EXP-CONN-TEST-001"
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["execution_contract"]["source_runtime_consistency"] == "MATCH"
    assert len(manifest["execution_contract"]["connectome_sources"]) == 3
    sidecar = json.loads((folder / "DATA/gateway_state.json").read_text())
    assert sidecar["canonical_snn_state"] is False
    assert len(sidecar["runs"]) == 9
    assert (folder / "analysis/ai_packet.json").is_file()
    with pytest.raises(WorkflowValidationError, match="already exists"):
        service.run_science(body)


def test_native_budget_includes_donor_work() -> None:
    with pytest.raises(ValueError, match="250000"):
        run_protocol(
            "embodied_closed_loop_v1", config(), seeds=tuple(range(8)), ticks=10000
        )


def test_failed_native_trajectory_is_not_discarded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.core.network import NeuralNetwork

    for folder in ("registry", "protocols", "preregistrations", "literature", "ethics"):
        shutil.copytree(RESEARCH / folder, tmp_path / "research" / folder)
    (tmp_path / "configs").mkdir()
    shutil.copy2(
        ROOT / "configs/learning_experiment.yaml",
        tmp_path / "configs/learning_experiment.yaml",
    )

    def injected_failure(self: NeuralNetwork) -> None:
        raise RuntimeError("injected engineering-test failure")

    monkeypatch.setattr(NeuralNetwork, "step", injected_failure)
    root = tmp_path / "research"
    ExperimentWorkflowService(root).run_science(
        {
            "experiment_id": "EXP-CONN-FAIL-001",
            "question_id": "RQ-EMB-001",
            "hypothesis_id": "H-EMB-001-B",
            "protocol": "embodied_closed_loop_v1",
            "title": "Failure-retention test",
            "conditions": "all registered arms",
            "ticks": 120,
            "seeds": "101,102,103",
        }
    )
    folder = root / "experiments/EXP-CONN-FAIL-001"
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["experiment_status"] == "failed"
    assert manifest["execution_contract"]["tick_validation"]["status"] == "VIOLATED"
    assert (folder / "DATA/gateway_state.json").is_file()
    runs = json.loads((folder / "DATA/runs.json").read_text())
    assert len(runs) == 9
    assert all(row["runtime_error"] for row in runs)
