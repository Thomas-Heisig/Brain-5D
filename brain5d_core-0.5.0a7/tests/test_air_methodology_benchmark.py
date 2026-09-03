"""Structural contract for the AI-assisted research methodology benchmark."""

from __future__ import annotations

import json
from pathlib import Path

from src.research_assistant import ResearchAssistant


def test_air_methodology_gold_standard_has_30_unique_held_out_cases() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "benchmarks"
        / "air_methodology_gold_v1.json"
    )
    benchmark = json.loads(path.read_text(encoding="utf-8"))
    cases = benchmark["cases"]

    assert benchmark["research_question"] == "RQ-AIR-001"
    assert len(cases) == 30
    assert len({case["id"] for case in cases}) == 30
    assert benchmark["rules"]["model_must_not_receive_gold_labels"] is True
    assert benchmark["rules"]["assistant_access"] == "denied"
    controls = [case for case in cases if case["defects"] == ["clean_control_case"]]
    ambiguous = [
        case for case in cases if case["defects"] == ["ambiguous_control_case"]
    ]
    assert len(controls) == 7
    assert len(ambiguous) == 3


def test_research_packet_excludes_nearby_benchmark_labels(tmp_path: Path) -> None:
    (tmp_path / "experiments" / "EXP-AIR-0001").mkdir(parents=True)
    (tmp_path / "registry").mkdir()
    (tmp_path / "benchmarks").mkdir()
    (tmp_path / "experiments" / "EXP-AIR-0001" / "manifest.json").write_text(
        '{"research_questions":["RQ-AIR-001"],"hypotheses":["H-AIR-001-A"]}',
        encoding="utf-8",
    )
    (tmp_path / "registry" / "questions.yaml").write_text(
        "- id: RQ-AIR-001\n  domain: AIR\n  question: q\n  relevance: r\n",
        encoding="utf-8",
    )
    (tmp_path / "registry" / "hypotheses.yaml").write_text(
        "- id: H-AIR-001-A\n  research_question: RQ-AIR-001\n  hypothesis: h\n",
        encoding="utf-8",
    )
    (tmp_path / "registry" / "claims.yaml").write_text("[]", encoding="utf-8")
    (tmp_path / "benchmarks" / "gold.json").write_text(
        '{"secret_gold_label":"dirty_provenance"}', encoding="utf-8"
    )

    packet = ResearchAssistant(tmp_path).build_packet("EXP-AIR-0001")

    assert "secret_gold_label" not in packet.to_json()
