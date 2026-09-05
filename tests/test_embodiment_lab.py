"""Protocol-level regression tests for EXP-EMB-0001."""

import json
from pathlib import Path

from src.experiments.embodiment_lab import run_protocol


def test_embodiment_protocol_records_all_conditions_as_data(tmp_path: Path) -> None:
    analysis = run_protocol(
        tmp_path / "EXP-EMB-0001",
        independent_runs=2,
        repetitions_per_condition=2,
    )

    assert analysis["run_count"] == 24
    assert analysis["evidence_eligible"] is False
    assert analysis["sensor_frames_reproducible"] is True
    assert analysis["conditions"]["authorized"]["target_reached_rate"] == 0.5
    assert analysis["conditions"]["unauthorized"]["target_reached_rate"] == 0.0
    assert analysis["conditions"]["unauthorized"]["total_reward"] == 0.0
    assert analysis["conditions"]["authorized"]["all_audits_valid"] is True
    assert analysis["conditions"]["authorized"]["accepted_action_count"] == 12
    assert analysis["conditions"]["authorized"]["observed_effect_count"] == 12
    assert analysis["conditions"]["unauthorized"]["accepted_action_count"] == 0
    assert analysis["conditions"]["unauthorized"]["observed_effect_count"] == 0
    assert analysis["conditions"]["actuator_failure"]["accepted_action_count"] == 0
    assert analysis["conditions"]["actuator_failure"]["observed_effect_count"] == 0
    assert analysis["conditions"]["sensor_loss"]["runtime_errors"] == 4
    assert analysis["conditions"]["sensor_loss"]["accepted_action_count"] == 0
    assert analysis["conditions"]["open_loop_replay"]["target_reached_rate"] == 0.5
    assert analysis["conditions"]["open_loop_replay"]["action_sources"] == [
        "pre_registered_replay"
    ]
    assert analysis["conditions"]["authorized"]["seed_metrics"] == {
        "42": {"runs": 2, "target_reached_rate": 1.0, "runtime_errors": 0},
        "43": {"runs": 2, "target_reached_rate": 0.0, "runtime_errors": 0},
    }
    assert analysis["replay_plan"]["actions"] == ["right", "right", "right"]
    assert analysis["conditions"]["authorized"]["acceptance_receipts_complete"] is True
    assert analysis["conditions"]["authorized"]["effect_receipts_complete"] is True

    data_path = tmp_path / "EXP-EMB-0001" / "DATA" / "analysis.json"
    assert json.loads(data_path.read_text(encoding="utf-8"))["run_count"] == 24

    runs_path = tmp_path / "EXP-EMB-0001" / "DATA" / "runs.jsonl"
    run_records = [
        json.loads(line) for line in runs_path.read_text(encoding="utf-8").splitlines()
    ]
    first_run = run_records[0]
    assert first_run["action_acceptance_receipts"][0]["accepted"] is True
    assert first_run["observed_effect_receipts"][0]["effect_observed"] is True
    assert first_run["action_source"] == "network_output"
    actuator_failure = next(
        run for run in run_records if run["condition"] == "actuator_failure"
    )
    assert actuator_failure["action_acceptance_receipts"][0]["accepted"] is False
    assert actuator_failure["observed_effect_receipts"][0]["effect_observed"] is False
    sensor_loss = next(run for run in run_records if run["condition"] == "sensor_loss")
    assert sensor_loss["action_acceptance_receipts"] == []
    assert sensor_loss["runtime_error"] == "RuntimeError: experience sensor is inactive"
