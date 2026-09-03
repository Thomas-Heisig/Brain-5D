"""Protocol-level regression tests for EXP-EMB-0001."""

import json

from src.experiments.embodiment_lab import run_protocol


def test_embodiment_protocol_records_all_conditions_as_data(tmp_path) -> None:
    analysis = run_protocol(
        tmp_path / "EXP-EMB-0001",
        independent_runs=2,
        repetitions_per_condition=2,
    )

    assert analysis["run_count"] == 12
    assert analysis["evidence_eligible"] is False
    assert analysis["sensor_frames_reproducible"] is True
    assert analysis["conditions"]["authorized"]["target_reached_rate"] == 1.0
    assert analysis["conditions"]["unauthorized"]["target_reached_rate"] == 0.0
    assert analysis["conditions"]["unauthorized"]["total_reward"] == 0.0
    assert analysis["conditions"]["authorized"]["all_audits_valid"] is True

    data_path = tmp_path / "EXP-EMB-0001" / "DATA" / "analysis.json"
    assert json.loads(data_path.read_text(encoding="utf-8"))["run_count"] == 12