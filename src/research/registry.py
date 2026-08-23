"""
Research Registry — Load, save, and query the research registries.

Provides typed access to questions.yaml, hypotheses.yaml, claims.yaml,
sources.yaml, and methods.yaml.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = REPO_ROOT / "research" / "registry"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class Answer:
    current: Optional[str]
    confidence: str  # none | low | medium | high | very_high
    limitations: Optional[str]

    def __init__(self, data: dict[str, Any]) -> None:
        self.current = data.get("current")
        self.confidence = data.get("confidence", "none")
        self.limitations = data.get("limitations")


class ResearchQuestion:
    id: str
    domain: str
    question: str
    relevance: str
    literature: List[str]
    hypotheses: List[str]
    evidence: List[str]
    status: str  # open | in_progress | answered | superseded
    answer: Answer
    created: date | None
    updated: date | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data["id"]
        self.domain = data["domain"]
        self.question = data["question"]
        self.relevance = data["relevance"]
        self.literature = data.get("literature", [])
        self.hypotheses = data.get("hypotheses", [])
        self.evidence = data.get("evidence", [])
        self.status = data.get("status", "open")
        self.answer = Answer(data.get("answer", {}))
        self.created = self._parse_date(data.get("created"))
        self.updated = self._parse_date(data.get("updated"))

    @staticmethod
    def _parse_date(d: Any) -> Optional[date]:
        if isinstance(d, date):
            return d
        if isinstance(d, str):
            try:
                return date.fromisoformat(d)
            except ValueError:
                return None
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "question": self.question,
            "relevance": self.relevance,
            "literature": self.literature,
            "hypotheses": self.hypotheses,
            "evidence": self.evidence,
            "status": self.status,
            "answer": {
                "current": self.answer.current,
                "confidence": self.answer.confidence,
                "limitations": self.answer.limitations,
            },
            "created": str(self.created) if self.created else None,
            "updated": str(self.updated) if self.updated else None,
        }


class Hypothesis:
    id: str
    research_question: str
    hypothesis: str
    status: str  # untested | inconclusive | supported | refuted
    evidence: List[str]
    created: date | None
    updated: date | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data["id"]
        self.research_question = data["research_question"]
        self.hypothesis = data["hypothesis"]
        self.status = data.get("status", "untested")
        self.evidence = data.get("evidence", [])
        self.created = ResearchQuestion._parse_date(data.get("created"))
        self.updated = ResearchQuestion._parse_date(data.get("updated"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "research_question": self.research_question,
            "hypothesis": self.hypothesis,
            "status": self.status,
            "evidence": self.evidence,
            "created": str(self.created) if self.created else None,
            "updated": str(self.updated) if self.updated else None,
        }


class Claim:
    id: str
    claim: str
    research_question: str
    hypothesis: str
    evidence: List[str]
    experiments: List[str]
    sources: List[str]
    status: str  # untested | inconclusive | supported | refuted
    confidence: str
    required_evidence: List[str]
    minimum_runs: int
    created: date | None
    updated: date | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data["id"]
        self.claim = data["claim"]
        self.research_question = data["research_question"]
        self.hypothesis = data["hypothesis"]
        self.evidence = data.get("evidence", [])
        self.experiments = data.get("experiments", [])
        self.sources = data.get("sources", [])
        self.status = data.get("status", "untested")
        self.confidence = data.get("confidence", "none")
        self.required_evidence = data.get("required_evidence", [])
        self.minimum_runs = data.get("minimum_runs", 10)
        self.created = ResearchQuestion._parse_date(data.get("created"))
        self.updated = ResearchQuestion._parse_date(data.get("updated"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "claim": self.claim,
            "research_question": self.research_question,
            "hypothesis": self.hypothesis,
            "evidence": self.evidence,
            "experiments": self.experiments,
            "sources": self.sources,
            "status": self.status,
            "confidence": self.confidence,
            "required_evidence": self.required_evidence,
            "minimum_runs": self.minimum_runs,
            "created": str(self.created) if self.created else None,
            "updated": str(self.updated) if self.updated else None,
        }


class Source:
    source_id: str
    authors: List[str]
    title: str
    year: int
    journal: Optional[str]
    publisher: Optional[str]
    doi: Optional[str]
    topic: List[str]
    claims: List[str]
    brain5d_questions: List[str]
    brain5d_relevance: Optional[str]

    def __init__(self, data: dict[str, Any]) -> None:
        self.source_id = data["source_id"]
        self.authors = data.get("authors", [])
        self.title = data.get("title", "")
        self.year = data.get("year", 0)
        self.journal = data.get("journal")
        self.publisher = data.get("publisher")
        self.doi = data.get("doi")
        self.topic = data.get("topic", [])
        self.claims = data.get("claims", [])
        self.brain5d_questions = data.get("brain5d_questions", [])
        self.brain5d_relevance = data.get("brain5d_relevance")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "authors": self.authors,
            "title": self.title,
            "year": self.year,
            "journal": self.journal,
            "publisher": self.publisher,
            "doi": self.doi,
            "topic": self.topic,
            "claims": self.claims,
            "brain5d_questions": self.brain5d_questions,
            "brain5d_relevance": self.brain5d_relevance,
        }


# ---------------------------------------------------------------------------
# Registry loader
# ---------------------------------------------------------------------------


class ResearchRegistry:
    """Central registry for all research entities."""

    def __init__(self, registry_dir: Path = REGISTRY_DIR):
        self._registry_dir = registry_dir
        self.questions: Dict[str, ResearchQuestion] = {}
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.claims: Dict[str, Claim] = {}
        self.sources: Dict[str, Source] = {}

    def load_all(self) -> "ResearchRegistry":
        """Load all registry files from disk."""
        self.questions = self._load_yaml("questions.yaml", ResearchQuestion)
        self.hypotheses = self._load_yaml("hypotheses.yaml", Hypothesis)
        self.claims = self._load_yaml("claims.yaml", Claim)
        self.sources = self._load_yaml("sources.yaml", Source)
        return self

    def _load_yaml(self, filename: str, cls: type) -> dict[str, Any]:
        path = self._registry_dir / filename
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
        return {
            item["id"] if "id" in item else item.get("source_id"): cls(item)
            for item in data
        }

    def save_questions(self) -> None:
        self._save_yaml(
            "questions.yaml", [q.to_dict() for q in self.questions.values()]
        )

    def save_hypotheses(self) -> None:
        self._save_yaml(
            "hypotheses.yaml", [h.to_dict() for h in self.hypotheses.values()]
        )

    def save_claims(self) -> None:
        self._save_yaml("claims.yaml", [c.to_dict() for c in self.claims.values()])

    def _save_yaml(self, filename: str, data: list[Any]) -> None:
        path = self._registry_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )

    # -- Queries ------------------------------------------------------------

    def questions_by_domain(self, domain: str) -> List[ResearchQuestion]:
        return [
            q for q in self.questions.values() if q.domain.lower() == domain.lower()
        ]

    def questions_by_status(self, status: str) -> List[ResearchQuestion]:
        return [q for q in self.questions.values() if q.status == status]

    def open_questions(self) -> List[ResearchQuestion]:
        return self.questions_by_status("open")

    def hypotheses_for_question(self, question_id: str) -> List[Hypothesis]:
        return [
            h for h in self.hypotheses.values() if h.research_question == question_id
        ]

    def claims_for_question(self, question_id: str) -> List[Claim]:
        return [c for c in self.claims.values() if c.research_question == question_id]

    def evidence_for_claim(self, claim_id: str) -> List[str]:
        claim = self.claims.get(claim_id)
        return claim.evidence if claim else []

    def sources_for_question(self, question_id: str) -> List[Source]:
        question = self.questions.get(question_id)
        if not question:
            return []
        return [self.sources[sid] for sid in question.literature if sid in self.sources]
