import pytest

from src.research_assistant.ai_research_object import (
    AIR_RESEARCH_QUESTIONS,
    AIResearchComparison,
    BlindAnalysis,
    BorrowedIntelligenceMetric,
    ModelInterpretation,
    ReviewerMetrics,
    borrowed_intelligence_ratio,
    interpretation_distance,
)


def test_multi_model_comparison_requires_identical_packet() -> None:
    first = ModelInterpretation.create("model-a", "packet-sha", "stable result")
    second = ModelInterpretation.create("model-b", "packet-sha", "different result")
    comparison = AIResearchComparison.create((first, second))
    assert comparison.scientific_evidence is False
    assert comparison.agreement_score == 0.5
    with pytest.raises(ValueError, match="identical ResearchPacket"):
        AIResearchComparison.create(
            (first, ModelInterpretation.create("model-c", "other", "result"))
        )


def test_blind_analysis_anonymizes_groups() -> None:
    blinded = BlindAnalysis.create(
        ("control", "treatment"), {"control": "A", "treatment": "B"}
    )
    assert set(blinded.labels.values()) == {"GROUP-001", "GROUP-002"}
    assert blinded.revealed is False


def test_reviewer_metrics_and_air_questions_are_deterministic() -> None:
    assert len(AIR_RESEARCH_QUESTIONS) == 5
    assert ReviewerMetrics(2, 1, 1).to_dict()["reviewer_correction_rate"] == 0.5
    assert (
        borrowed_intelligence_ratio(baseline_score=1, assisted_score=2, ceiling_score=3)
        == 0.5
    )
    metric = BorrowedIntelligenceMetric.create(
        protocol_id="PROTOCOL-AIR-001",
        baseline_score=1,
        assisted_score=2,
        ceiling_score=3,
    )
    assert metric.to_dict()["scientific_evidence"] is False


def test_interpretation_distance_is_zero_for_identical_text() -> None:
    first = ModelInterpretation.create("a", "packet", "same words")
    second = ModelInterpretation.create("b", "packet", "same words")
    assert interpretation_distance(first, second) == 0.0
