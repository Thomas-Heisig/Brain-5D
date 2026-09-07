from __future__ import annotations

from pathlib import Path

import yaml

from src.research.followup_experiments import run_learning_interference
from src.research_assistant.governance import ResearchRunMode


ROOT = Path(__file__).parents[1]


def test_replication_run_mode_is_supported() -> None:
    assert ResearchRunMode("REPLICATION") is ResearchRunMode.REPLICATION


def test_learning_interference_completes_all_tasks_for_registered_seeds() -> None:
    config = yaml.safe_load(
        (ROOT / "configs" / "learning_experiment.yaml").read_text(encoding="utf-8")
    )
    runs = run_learning_interference(config, seeds=(42, 43, 44))
    assert len(runs) == 3
    for run in runs:
        assert run.runtime_error is None
        assert run.metrics["task_successes"] == [True, True, True]
        assert run.metrics["retained_success_fraction"] == 1.0
