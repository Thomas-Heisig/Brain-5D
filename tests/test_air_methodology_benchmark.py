"""Structural contract for the AI-assisted research methodology benchmark."""

from __future__ import annotations

import json
from pathlib import Path


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