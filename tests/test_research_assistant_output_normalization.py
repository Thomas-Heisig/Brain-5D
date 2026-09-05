"""Regression tests for tolerant but auditable AI output normalization."""

from __future__ import annotations

from src.research_assistant.models import (
    _normalize_output,
)  # pyright: ignore[reportPrivateUsage]


def _payload(confidence: object) -> dict[str, object]:
    return {
        "assessment": "fixture",
        "observations": [],
        "effect_direction": "not_determined",
        "methodological_concerns": [],
        "alternative_explanations": [],
        "recommended_experiments": [],
        "requested_evidence": [],
        "confidence": confidence,
    }


def test_numeric_confidence_string_is_normalized() -> None:
    normalized = _normalize_output(_payload("0.85"))
    assert normalized["confidence"] == 0.85
    assert "confidence_original" not in normalized


def test_percentage_confidence_is_normalized() -> None:
    normalized = _normalize_output(_payload("85%"))
    assert normalized["confidence"] == 0.85
    assert "confidence_original" not in normalized


def test_decimal_comma_confidence_is_normalized() -> None:
    normalized = _normalize_output(_payload("0,85"))
    assert normalized["confidence"] == 0.85


def test_qualitative_confidence_does_not_abort_airr_chain() -> None:
    normalized = _normalize_output(_payload("high"))
    assert normalized["confidence"] == 0.0
    assert normalized["confidence_original"] == "high"
    concerns = normalized["methodological_concerns"]
    assert isinstance(concerns, list)
    assert any("confidence" in str(item) for item in list(concerns))


def test_out_of_range_confidence_is_preserved_and_zeroed() -> None:
    normalized = _normalize_output(_payload(85))
    assert normalized["confidence"] == 0.0
    assert normalized["confidence_original"] == 85
