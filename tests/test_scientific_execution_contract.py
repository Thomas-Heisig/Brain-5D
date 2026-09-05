from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from src.dashboard.experiment_workflow import (
    ExperimentWorkflow,
    ExperimentWorkflowService,
    WorkflowValidationError,
    write_experiment_summary,
)
from src.research.network_probe import NetworkImpulseProbe


class EarlyQuiescentRuntime:
    def __init__(self) -> None:
        self.ticks = 0
        self.injected: dict[int, float] = {}

    def inject_current_batch(self, currents: Mapping[int, float]) -> None:
        self.injected = dict(currents)

    def step(self) -> dict[str, object]:
        self.ticks += 1
        return {
            "spike_ids": (1,) if self.ticks == 2 else (),
            "output_spike_ids": (1,) if self.ticks == 2 else (),
            "quiescent": self.ticks >= 3,
        }


def _workflow(question_id: str, protocol: str = "science_suite_v1") -> ExperimentWorkflow:
    return ExperimentWorkflow(
        experiment_id="EXP-GEN-9999",
        question_id=question_id,
        hypothesis_id="H-TEST-001-A",
        title="contract test",
        conditions="fixed",
        ticks=25,
        notes="",
        protocol=protocol,
        seeds=(42, 43, 44),
    )


def test_probe_executes_complete_requested_window_despite_early_quiescence() -> None:
    runtime = EarlyQuiescentRuntime()
    signature = NetworkImpulseProbe(source_neuron=1, max_ticks=25).run(runtime)

    assert runtime.ticks == 25
    assert signature.ticks_executed == 25
    assert signature.total_spikes == 1
    assert signature.stopped_on_quiescence is False


def test_science_runner_uses_research_question_not_generated_id() -> None:
    assert (
        ExperimentWorkflowService._science_runner(  # pyright: ignore[reportPrivateUsage]
            {"protocol": "science_suite_v1"}, _workflow("RQ-TEMP-001")
        )
        == "run_temporal"
    )
    assert (
        ExperimentWorkflowService._science_runner(  # pyright: ignore[reportPrivateUsage]
            {"protocol": "science_suite_v1"}, _workflow("RQ-PING-001")
        )
        == "run_ping"
    )


def test_dedicated_protocol_rejects_mismatched_research_question() -> None:
    with pytest.raises(WorkflowValidationError, match="RQ-TIME"):
        ExperimentWorkflowService._science_runner(  # pyright: ignore[reportPrivateUsage]
            {"protocol": "science_time_v1"},
            _workflow("RQ-TEMP-001", "science_time_v1"),
        )


def test_detailed_summary_contains_data_formulas_runs_and_tick_contract(
    tmp_path: Path,
) -> None:
    experiment = tmp_path / "experiments" / "EXP-TEMP-TEST"
    (experiment / "DATA").mkdir(parents=True)
    (experiment / "manifest.json").write_text(
        json.dumps(
            {
                "experiment_status": "completed",
                "research_questions": ["RQ-TEMP-001"],
                "hypotheses": ["H-TEMP-001-A"],
                "simulation": {
                    "ticks": 12,
                    "seeds": [42],
                    "protocol": "science_suite_v1",
                },
                "results": {"run_count": 1},
                "research_run_mode": "EXPLORATORY",
                "network_mode": "OFFLINE",
            }
        ),
        encoding="utf-8",
    )
    (experiment / "workflow.json").write_text(
        json.dumps(
            {
                "title": "Temporal contract",
                "conditions": "FAST/MEDIUM/SLOW",
                "ticks": 12,
                "seeds": [42],
                "protocol": "science_suite_v1",
            }
        ),
        encoding="utf-8",
    )
    (experiment / "DATA" / "runs.json").write_text(
        json.dumps(
            [
                {
                    "experiment_id": "EXP-TEMP-TEST",
                    "condition": "fast_medium_slow",
                    "seed": 42,
                    "metrics": {
                        "ticks_requested": 12,
                        "ticks_executed": 12,
                        "total_spikes": 3,
                        "comparisons": [
                            {
                                "horizon": "fast",
                                "reference_tick": 1,
                                "discrepancy": 0.5,
                            },
                            {
                                "horizon": "medium",
                                "reference_tick": 1,
                                "discrepancy": 0.8,
                            },
                            {
                                "horizon": "slow",
                                "reference_tick": 1,
                                "discrepancy": 1.1,
                            },
                        ],
                    },
                    "state_digest_before": "a",
                    "state_digest_after": "b",
                    "runtime_error": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    write_experiment_summary(
        tmp_path,
        "EXP-TEMP-TEST",
        {"status": "unavailable", "reason": "fixture"},
    )

    summary = (experiment / "summary.md").read_text(encoding="utf-8")
    stats = json.loads(
        (experiment / "analysis" / "statistics.json").read_text(encoding="utf-8")
    )
    assert "Tick-Vertrag: `SATISFIED`" in summary
    assert "Semantische Konsistenz" in summary
    assert "Inter-Spike-Intervall" in summary
    assert "Temporal-State-Horizonte" in summary
    assert "Einzelne Läufe" in summary
    assert stats["generated_by"] == "deterministic_statistics_engine"
    assert stats["temporal_horizons"]["slow"]["discrepancy"]["mean"] == 1.1
