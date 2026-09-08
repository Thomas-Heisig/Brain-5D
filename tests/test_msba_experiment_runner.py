from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.embodiment.peripheral_adapters import (
    PRODUCTION_PERIPHERAL_ACTIVATION_ENABLED,
    AdapterDeclaration,
    ExperimentAdapterFactory,
    declaration_artifact_hash,
)
from src.experiments import msba_lab
from src.research import followup_experiments
from src.research.protocol_registry import OPERATIONAL_RUNNERS, protocol_catalog

SEEDS = (101, 102, 103)


def test_peripheral_adapter_is_experiment_only_and_records_provenance() -> None:
    artifact = {"weights": [1, 2, 3], "model": "test"}
    declaration = AdapterDeclaration(
        area_id="test.area",
        adapter_class="DeterministicPeripheralAdapter",
        framework="python-reference",
        model="test-model",
        version="1.2.3",
        artifact_sha256=declaration_artifact_hash(artifact),
        endpoint_identity="experiment://test/area",
        modality="digital",
    )
    assert PRODUCTION_PERIPHERAL_ACTIVATION_ENABLED is False
    with pytest.raises(RuntimeError, match="experiment mode"):
        ExperimentAdapterFactory.create(declaration, experiment_mode=False)
    with pytest.raises(RuntimeError, match="production peripheral activation"):
        ExperimentAdapterFactory.create(
            declaration, experiment_mode=True, production_activation=True
        )
    adapter = ExperimentAdapterFactory.create(declaration, experiment_mode=True)
    assert adapter.process("payload", 1) == "payload"
    provenance = declaration.provenance()
    assert provenance["adapter_class"] == "DeterministicPeripheralAdapter"
    assert provenance["framework"] == "python-reference"
    assert provenance["model"] == "test-model"
    assert provenance["version"] == "1.2.3"
    assert provenance["artifact_sha256"] == declaration.artifact_sha256
    assert provenance["endpoint_identity"] == "experiment://test/area"
    assert provenance["production_activation_enabled"] is False


def test_adaptive_gateway_fails_closed_without_preregistration() -> None:
    with pytest.raises(msba_lab.MSBAPreregistrationError, match="preregistration"):
        msba_lab.run_msba_e02({}, seeds=SEEDS)
    with pytest.raises(msba_lab.MSBAPreregistrationError, match="independent seeds"):
        msba_lab.run_msba_e03({}, seeds=(101, 101, 101), preregistration={})


def test_operational_catalog_exposes_all_msba_protocols() -> None:
    catalog = {item["id"]: item for item in protocol_catalog(msba_lab.Path("research"))}
    expected = {
        "msba_energy_efficiency_v1": "run_msba_e01",
        "msba_resource_allocation_v1": "run_msba_e02",
        "msba_visual_roi_v1": "run_msba_e03",
        "msba_digital_integrity_v1": "run_msba_e04",
        "msba_modality_compensation_v1": "run_msba_e05",
    }
    for protocol_id, runner in expected.items():
        assert OPERATIONAL_RUNNERS[protocol_id] == runner
        assert catalog[protocol_id]["minimum_independent_seeds"] == 3
        assert catalog[protocol_id]["freeze"]["status"] == "FROZEN"


def test_e01_energy_and_projection_information_controls_execute() -> None:
    runs = followup_experiments.run_msba_e01({}, seeds=SEEDS)
    assert len(runs) == 9
    assert {run.condition for run in runs} == {"audio", "vision", "digital"}
    for run in runs:
        assert run.state_digest_before == run.state_digest_after
        assert run.metrics["canonical_snn_synapse_state"] == "not_accessed"
        matrix = run.metrics["control_matrix"]
        assert set(matrix["projection_treatments"]) == {
            "structured",
            "shuffled",
            "random",
            "reduced_dimensional",
            "increased_dimensional",
        }
        assert (
            matrix["information_controls"]["activity_matched_information_destroyed"][
                "activity_matched"
            ]
            is True
        )


def test_e02_equal_budget_frozen_random_noise_and_rewards_execute() -> None:
    runs = followup_experiments.run_msba_e02({}, seeds=SEEDS)
    assert len(runs) == 9
    assert {run.condition for run in runs} == {"adaptive", "fixed", "random"}
    for run in runs:
        assert run.metrics["resource_budget_consumed"] <= run.metrics["resource_budget"]
        matrix = run.metrics["control_matrix"]
        assert matrix["frozen_gateway_control"]["allocation_mode"] == "frozen"
        assert matrix["noisy_area_suppression"]["noisy_area_suppressed"] is True
        assert set(matrix["reward_formulations"]) == {
            "signed",
            "absolute",
            "squared",
            "local_homeostatic",
        }


def test_e03_roi_controls_and_projection_dimensions_execute() -> None:
    runs = followup_experiments.run_msba_e03({}, seeds=SEEDS)
    assert len(runs) == 12
    assert {run.condition for run in runs} == {
        "adaptive_roi",
        "fixed_center_roi",
        "random_roi",
        "full_image",
    }
    projection = runs[0].metrics["control_matrix"]["projection_treatments"]
    assert projection["structured"]["dimensions"] == 8
    assert projection["reduced_dimensional"]["dimensions"] == 4
    assert projection["increased_dimensional"]["dimensions"] == 16


def test_e04_exact_digital_integrity_and_replay_execute() -> None:
    runs = followup_experiments.run_msba_e04({}, seeds=SEEDS)
    assert len(runs) == 9
    for run in runs:
        assert run.metrics["checksum_mismatches"] == 0
        assert run.metrics["exact_payload_mismatches"] == 0
        assert run.metrics["exact_integrity_pass"] is True
        for checksum in run.metrics["checksums"]:
            assert checksum["input_sha256"] == checksum["output_sha256"]
            assert checksum["input_sha256"] == checksum["recorded_sha256"]


def test_e05_lesion_compensation_and_gateway_controls_execute() -> None:
    runs = followup_experiments.run_msba_e05({}, seeds=SEEDS)
    assert len(runs) == 12
    assert {run.condition for run in runs} == {
        "adaptive_compensation",
        "fixed_allocation",
        "shuffled_utility",
        "no_compensation",
    }
    adaptive = next(run for run in runs if run.condition == "adaptive_compensation")
    assert adaptive.metrics["compensatory_gate_change"] > 0
    matrix = adaptive.metrics["control_matrix"]
    assert matrix["sensor_lesion_compensation"] is True
    assert matrix["random_gateway_control"]["allocation_mode"] == "random"
    assert matrix["frozen_gateway_control"]["allocation_mode"] == "frozen"


def test_gateway_state_persists_to_separate_sidecar(tmp_path: Path) -> None:
    prereg = json.loads(
        msba_lab.Path("research/preregistrations/PREREG-MSBA-E01.json").read_text(
            encoding="utf-8"
        )
    )
    runs = msba_lab.run_msba_e01({}, seeds=SEEDS, preregistration=prereg)
    serialized = [asdict(run) for run in runs]
    path = msba_lab.persist_gateway_state_sidecar(tmp_path, serialized)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["namespace"] == "experiment_gateway_state"
    assert payload["canonical_snn_synapse_state"] == "not_accessed"
    assert len(payload["records"]) == len(runs)
    assert all("gateway_state" not in run["metrics"] for run in serialized)
