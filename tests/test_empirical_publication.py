"""Verify publication traceability, never require positive research outcomes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.publication_empirical import CAMPAIGNS, EDITION, verify
from src.dashboard.research_source import ResearchSource
from src.experiments.learning_lab import run_learning_experiment

ROOT = Path(__file__).resolve().parents[1]


def test_empirical_edition_preserves_history_and_data() -> None:
    verify()


def test_one_current_edition_and_no_evidence_promotion() -> None:
    catalogue: dict[str, Any] = json.loads(
        (ROOT / "research/publications/catalog.json").read_text(encoding="utf-8")
    )
    current = [item for item in catalogue["publications"] if item.get("current")]
    assert len(current) == 1
    assert current[0]["version"] == "1.4"
    assert catalogue["current_publication_id"] == current[0]["id"]
    assert catalogue["current_publication"] == current[0]["id"]
    manifest: dict[str, Any] = json.loads(
        (ROOT / "research/publications" / EDITION / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["new_empirical_findings"] is True
    assert manifest["accepted_evidence"] is False
    assert manifest["human_review"] == "pending"
    assert manifest["automatic_evidence_promotion"] is False


def test_negative_and_failed_original_observations_remain_visible() -> None:
    original = ROOT / "research/experiments" / CAMPAIGNS[0]
    summary: dict[str, Any] = json.loads((original / "summary.json").read_text())
    assert summary["total_runs"] == 1272
    assert summary["status_counts"] == {"completed": 28, "failed": 1}
    assert summary["human_review_pending"] == 22
    assert len(summary["questions_without_specific_runnable_protocol"]) == 43
    assert summary["accepted_evidence"] is False
    receipt: dict[str, Any] = json.loads(
        (original / "028-active_scaling_v1/receipt.json").read_text()
    )
    assert receipt["status"] == "failed"
    assert "Coordinate 256" in receipt["error"]


def test_campaign_navigation_does_not_masquerade_as_evidence() -> None:
    source = ResearchSource(ROOT / "research")
    entries = {item["id"]: item for item in source.list_experiments()}
    for name in CAMPAIGNS:
        assert name in entries
        metadata: dict[str, Any] = json.loads(
            (ROOT / "research/experiments" / name / "manifest.json").read_text()
        )
        assert metadata["record_kind"] == "campaign_index"
        assert metadata["validity"]["valid"] is False
        assert metadata["results"]["accepted_evidence"] is False


def test_declared_trial_partitions_are_not_counted_as_executed_holdout() -> None:
    import yaml

    config = yaml.safe_load((ROOT / "configs/learning_experiment.yaml").read_text())
    result = run_learning_experiment(config)
    assert result.partition_counts_are_declared is True
    assert result.validation_episodes_executed == 0
    assert result.holdout_episodes_executed == 0
    assert result.baseline_probes_executed == result.post_training_probes_executed == 1
