"""Contract tests for the read-only scientific research assistant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from src.research_assistant import ResearchAssistant


def _write_research_fixture(root: Path) -> None:
    (root / "experiments" / "EXP-STDP-0001").mkdir(parents=True)
    (root / "generated" / "data").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "experiments" / "EXP-STDP-0001" / "manifest.json").write_text(
        json.dumps(
            {
                "research_questions": ["RQ-STDP-001"],
                "hypotheses": ["H-STDP-001-A"],
                "artifacts": {"data": "research/generated/data/DATA-2026-17.json"},
            }
        ),
        encoding="utf-8",
    )
    (root / "generated" / "data" / "DATA-2026-17.json").write_text(
        "{}", encoding="utf-8"
    )
    (root / "registry" / "questions.yaml").write_text(
        "- id: RQ-STDP-001\n  domain: STDP\n  question: Does timing work?\n  relevance: test\n",
        encoding="utf-8",
    )
    (root / "registry" / "hypotheses.yaml").write_text(
        "- id: H-STDP-001-A\n  research_question: RQ-STDP-001\n  hypothesis: It works.\n",
        encoding="utf-8",
    )
    (root / "registry" / "claims.yaml").write_text(
        "- id: CLAIM-STDP-001\n  research_question: RQ-STDP-001\n  hypothesis: H-STDP-001-A\n  claim: Timing works.\n",
        encoding="utf-8",
    )


def _reviewer_backend(_prompt: str) -> tuple[dict[str, Any], dict[str, str | float]]:
    return (
        {
            "assessment": "inconclusive",
            "observations": ["The record is a pilot."],
            "methodological_concerns": ["Dirty provenance."],
            "alternative_explanations": ["Isolated implementation only."],
            "recommended_experiments": ["Measure the production learning path."],
            "confidence": 0.75,
            "requested_evidence": ["Clean frozen runtime experiment."],
        },
        {"provider": "test", "model": "critical-reviewer", "temperature": 0.0},
    )


def test_critical_reviewer_persists_interpretation_only_record(tmp_path: Path) -> None:
    _write_research_fixture(tmp_path)
    assistant = ResearchAssistant(tmp_path)

    packet = assistant.build_packet("EXP-STDP-0001")
    record = assistant.analyze("EXP-STDP-0001", "critical_reviewer", _reviewer_backend)

    saved = json.loads(
        (
            tmp_path
            / "experiments"
            / "EXP-STDP-0001"
            / "analysis"
            / f"{record.analysis_id}.json"
        ).read_text()
    )
    assert saved["epistemic_status"] == {
        "evidence": False,
        "interpretation_only": True,
        "human_review_required": True,
    }
    assert saved["inputs"]["packet_digest"] == packet.digest
    assert saved["provenance"]["research_packet_digest"] == packet.digest
    assert saved["review"]["status"] == "pending"
    assert saved["output"]["methodological_concerns"] == ["Dirty provenance."]
    assert (
        assistant.build_packet("EXP-STDP-0001").previous_analyses[0]["analysis_id"]
        == record.analysis_id
    )


def test_build_packet_bounds_large_raw_sequences_for_analysis_prompt(
    tmp_path: Path,
) -> None:
    _write_research_fixture(tmp_path)
    data_path = tmp_path / "generated" / "data" / "DATA-2026-17.json"
    raw_runs = [
        {"current_tick": index, "discrepancy": index / 10} for index in range(300)
    ]
    data_path.write_text(json.dumps(raw_runs), encoding="utf-8")

    packet = ResearchAssistant(tmp_path).build_packet("EXP-STDP-0001")

    projected_value: object = packet.data["runs"] if packet.data is not None else None
    assert isinstance(projected_value, dict)
    projected = cast(dict[str, object], projected_value)
    assert projected["_analysis_projection"] == "truncated_sequence"
    assert projected["item_count"] == 300
    head_value = projected["head"]
    tail_value = projected["tail"]
    assert isinstance(head_value, list)
    assert isinstance(tail_value, list)
    head = cast(list[object], head_value)
    tail = cast(list[object], tail_value)
    assert len(head) == 8
    assert len(tail) == 8
    assert len(packet.to_json()) < 20_000
    assert json.loads(data_path.read_text(encoding="utf-8")) == raw_runs
