"""Tests for evidence feedback from claims to research questions."""

from __future__ import annotations

from src.research.evidence_engine import EvidenceEngine
from src.research.registry import Claim, Hypothesis, ResearchQuestion, ResearchRegistry


def _registry(claim_status: str) -> ResearchRegistry:
    registry = ResearchRegistry()
    registry.questions = {
        "RQ-TEST-001": ResearchQuestion(
            {
                "id": "RQ-TEST-001",
                "domain": "test",
                "question": "Can evidence change maturity?",
                "relevance": "test",
            }
        )
    }
    registry.hypotheses = {
        "H-TEST-001-A": Hypothesis(
            {
                "id": "H-TEST-001-A",
                "research_question": "RQ-TEST-001",
                "hypothesis": "It can.",
            }
        )
    }
    registry.claims = {
        "CLAIM-TEST-001": Claim(
            {
                "id": "CLAIM-TEST-001",
                "claim": "Evidence changes maturity.",
                "research_question": "RQ-TEST-001",
                "hypothesis": "H-TEST-001-A",
                "status": claim_status,
            }
        )
    }
    return registry


def test_inconclusive_claim_marks_question_inconclusive(monkeypatch) -> None:
    registry = _registry("inconclusive")
    monkeypatch.setattr(registry, "save_questions", lambda: None)

    EvidenceEngine(registry)._update_research_question("CLAIM-TEST-001", "EVID-2026-99")

    assert registry.questions["RQ-TEST-001"].status == "inconclusive"
    assert registry.questions["RQ-TEST-001"].evidence == ["EVID-2026-99"]


def test_resolved_claim_marks_question_ready_for_human_answer(monkeypatch) -> None:
    registry = _registry("supported")
    monkeypatch.setattr(registry, "save_questions", lambda: None)

    EvidenceEngine(registry)._update_research_question("CLAIM-TEST-001", "EVID-2026-99")

    question = registry.questions["RQ-TEST-001"]
    assert question.status == "ready_for_answer"
    assert question.answer.current is None