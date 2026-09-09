from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.research.workflow_recovery import (
    WorkflowRecoveryError,
    build_retry_request,
    failed_protocol_results,
)


def _write_report(
    root: Path, workflow_id: str, results: list[dict[str, object]]
) -> Path:
    path = root / "workflows" / f"{workflow_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "workflow_id": workflow_id,
                "requested_ticks": 1000,
                "seeds": "42-44",
                "completed": sum(
                    item.get("status") == "completed" for item in results
                ),
                "failed": sum(item.get("status") == "failed" for item in results),
                "results": results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_retry_plan_preserves_failed_child_ticks_and_seeds(tmp_path: Path) -> None:
    workflow_id = "EXP-BATCH-20260906200118"
    source = _write_report(
        tmp_path,
        workflow_id,
        [
            {
                "protocol": "recurrence_map_v1",
                "status": "completed",
                "ticks": 256,
                "seeds": "42-61",
            },
            {
                "protocol": "independent_replication_v1",
                "status": "failed",
                "ticks": 256,
                "seeds": "42-61",
                "error": "ValueError: REPLICATION",
            },
            {
                "protocol": "learning_interference_screen_v1",
                "status": "failed",
                "ticks": 1,
                "seeds": "42-61",
                "error": "RuntimeError: training drive",
            },
        ],
    )
    original = source.read_bytes()

    request = build_retry_request(
        tmp_path,
        workflow_id,
        batch_id="EXP-RETRY-FAILED-PROTOCOLS",
    )

    assert request["protocols"] == [
        "independent_replication_v1",
        "learning_interference_screen_v1",
    ]
    assert request["protocol_options"] == {
        "independent_replication_v1": {"ticks": 256, "seeds": "42-61"},
        "learning_interference_screen_v1": {"ticks": 1, "seeds": "42-61"},
    }
    assert request["recovery_of"] == workflow_id
    assert source.read_bytes() == original


def test_failed_protocol_results_keeps_historical_order() -> None:
    report: dict[str, object] = {
        "results": [
            {"protocol": "a", "status": "failed"},
            {"protocol": "b", "status": "completed"},
            {"protocol": "c", "status": "failed"},
        ]
    }
    assert [item["protocol"] for item in failed_protocol_results(report)] == [
        "a",
        "c",
    ]


def test_retry_plan_rejects_workflow_without_failures(tmp_path: Path) -> None:
    workflow_id = "EXP-BATCH-CLEAN"
    _write_report(
        tmp_path,
        workflow_id,
        [{"protocol": "recurrence_map_v1", "status": "completed"}],
    )

    with pytest.raises(WorkflowRecoveryError, match="contains no failed children"):
        build_retry_request(tmp_path, workflow_id)
