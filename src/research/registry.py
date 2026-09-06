"""
Research Registry — Load, save, and query the research registries.

Provides typed access to questions, hypotheses, claims, and sources. Questions
and hypotheses support canonical fragment files (for example
``questions.msba.yaml``) so the registry can grow without turning one YAML file
into an unmaintainable monolith. Duplicate identifiers fail closed.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml


def _parse_date(d: Any) -> date | None:
    """Parse a date from various input formats."""
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        try:
            return date.fromisoformat(d)
        except ValueError:
            return None
    return None


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = REPO_ROOT / "research" / "registry"


class Answer:
    current: str | None
    confidence: str
    limitations: str | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.current = data.get("current")
        self.confidence = data.get("confidence", "none")
        self.limitations = data.get("limitations")


class ResearchQuestion:
    id: str
    domain: str
    question: str
    relevance: str
    literature: list[str]
    hypotheses: list[str]
    evidence: list[str]
    status: str
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
        self.created = _parse_date(data.get("created"))
        self.updated = _parse_date(data.get("updated"))

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
    status: str
    evidence: list[str]
    created: date | None
    updated: date | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data["id"]
        self.research_question = data["research_question"]
        self.hypothesis = data["hypothesis"]
        self.status = data.get("status", "untested")
        self.evidence = data.get("evidence", [])
        self.created = _parse_date(data.get("created"))
        self.updated = _parse_date(data.get("updated"))

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
    evidence: list[str]
    experiments: list[str]
    sources: list[str]
    status: str
    confidence: str
    required_evidence: list[str]
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
        self.created = _parse_date(data.get("created"))
        self.updated = _parse_date(data.get("updated"))

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
    authors: list[str]
    title: str
    year: int
    journal: str | None
    publisher: str | None
    doi: str | None
    topic: list[str]
    claims: list[str]
    brain5d_questions: list[str]
    brain5d_relevance: str | None

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


class ResearchRegistry:
    """Central registry for all research entities.

    ``questions.yaml`` and ``hypotheses.yaml`` remain the historical base files.
    Additional canonical fragments named ``questions.<name>.yaml`` and
    ``hypotheses.<name>.yaml`` are merged deterministically. Duplicate IDs fail
    closed. Save operations preserve the source fragment of existing entries so
    evidence/status updates cannot collapse fragments back into the base file.
    """

    def __init__(self, registry_dir: Path = REGISTRY_DIR):
        self._registry_dir = registry_dir
        self.questions: dict[str, ResearchQuestion] = {}
        self.hypotheses: dict[str, Hypothesis] = {}
        self.claims: dict[str, Claim] = {}
        self.sources: dict[str, Source] = {}

    def load_all(self) -> ResearchRegistry:
        """Load all canonical registry files from disk."""
        self.questions = self._load_yaml_family(
            "questions.yaml", "questions.*.yaml", ResearchQuestion
        )
        self.hypotheses = self._load_yaml_family(
            "hypotheses.yaml", "hypotheses.*.yaml", Hypothesis
        )
        self.claims = self._load_yaml("claims.yaml", Claim)
        self.sources = self._load_yaml("sources.yaml", Source)
        return self

    def _family_paths(self, base_filename: str, fragment_pattern: str) -> list[Path]:
        paths: list[Path] = []
        base_path = self._registry_dir / base_filename
        if base_path.is_file():
            paths.append(base_path)
        paths.extend(
            path
            for path in sorted(self._registry_dir.glob(fragment_pattern))
            if path.name != base_filename and path.is_file()
        )
        return paths

    def _load_yaml_family(
        self, base_filename: str, fragment_pattern: str, cls: type
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for path in self._family_paths(base_filename, fragment_pattern):
            entries = self._load_yaml_path(path, cls)
            duplicates = sorted(set(merged).intersection(entries))
            if duplicates:
                raise ValueError(
                    f"Duplicate research registry IDs in {path.name}: "
                    + ", ".join(duplicates)
                )
            merged.update(entries)
        return merged

    def _load_yaml(self, filename: str, cls: type) -> dict[str, Any]:
        path = self._registry_dir / filename
        if not path.exists():
            return {}
        return self._load_yaml_path(path, cls)

    @staticmethod
    def _read_yaml_items(path: Path) -> list[dict[str, Any]]:
        with open(path, encoding="utf-8") as f:
            raw: Any = yaml.safe_load(f) or []
        if not isinstance(raw, list):
            raise ValueError(f"Registry file must contain a list: {path}")
        return cast("list[dict[str, Any]]", raw)

    @classmethod
    def _load_yaml_path(cls, path: Path, entry_cls: type) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for item in cls._read_yaml_items(path):
            identifier = item.get("id", item.get("source_id", ""))
            if not identifier:
                raise ValueError(f"Registry entry without identifier: {path}")
            if identifier in result:
                raise ValueError(f"Duplicate registry ID {identifier} in {path}")
            result[identifier] = entry_cls(item)
        return result

    def save_questions(self) -> None:
        """Persist question updates to their original canonical fragment."""
        entries = {
            identifier: item.to_dict() for identifier, item in self.questions.items()
        }
        self._save_yaml_family("questions.yaml", "questions.*.yaml", entries)

    def save_hypotheses(self) -> None:
        """Persist hypothesis updates to their original canonical fragment."""
        entries = {
            identifier: item.to_dict() for identifier, item in self.hypotheses.items()
        }
        self._save_yaml_family("hypotheses.yaml", "hypotheses.*.yaml", entries)

    def save_claims(self) -> None:
        self._save_yaml("claims.yaml", [c.to_dict() for c in self.claims.values()])

    def _save_yaml_family(
        self,
        base_filename: str,
        fragment_pattern: str,
        entries: dict[str, dict[str, Any]],
    ) -> None:
        """Save entries while preserving existing file ownership by identifier.

        Identifiers already present in a base/fragment file are written back to
        that same file. Newly created identifiers are appended to the base file.
        This prevents a fragment-aware load followed by ``save_*`` from creating
        duplicate IDs in the historical base registry.
        """
        paths = self._family_paths(base_filename, fragment_pattern)
        base_path = self._registry_dir / base_filename
        if base_path not in paths:
            paths.insert(0, base_path)

        ownership: dict[Path, list[str]] = {path: [] for path in paths}
        assigned: set[str] = set()
        for path in paths:
            if not path.is_file():
                continue
            for raw in self._read_yaml_items(path):
                identifier = raw.get("id", raw.get("source_id", ""))
                if identifier in entries:
                    ownership[path].append(identifier)
                    assigned.add(identifier)

        ownership[base_path].extend(sorted(set(entries) - assigned))
        for path, identifiers in ownership.items():
            if not identifiers and not path.exists():
                continue
            data = [entries[identifier] for identifier in identifiers]
            self._save_yaml_path(path, data)

    def _save_yaml(self, filename: str, data: list[Any]) -> None:
        self._save_yaml_path(self._registry_dir / filename, data)

    @staticmethod
    def _save_yaml_path(path: Path, data: list[Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )

    def questions_by_domain(self, domain: str) -> list[ResearchQuestion]:
        return [
            q for q in self.questions.values() if q.domain.lower() == domain.lower()
        ]

    def questions_by_status(self, status: str) -> list[ResearchQuestion]:
        return [q for q in self.questions.values() if q.status == status]

    def open_questions(self) -> list[ResearchQuestion]:
        return self.questions_by_status("open")

    def hypotheses_for_question(self, question_id: str) -> list[Hypothesis]:
        return [
            h for h in self.hypotheses.values() if h.research_question == question_id
        ]

    def claims_for_question(self, question_id: str) -> list[Claim]:
        return [c for c in self.claims.values() if c.research_question == question_id]

    def evidence_for_claim(self, claim_id: str) -> list[str]:
        claim = self.claims.get(claim_id)
        return claim.evidence if claim else []

    def sources_for_question(self, question_id: str) -> list[Source]:
        question = self.questions.get(question_id)
        if not question:
            return []
        return [self.sources[sid] for sid in question.literature if sid in self.sources]

    def link_issues(self) -> list[dict[str, str]]:
        """Return referential-integrity problems without mutating scientific data."""
        issues: list[dict[str, str]] = []
        for question in self.questions.values():
            for hypothesis_id in question.hypotheses:
                hypothesis = self.hypotheses.get(hypothesis_id)
                if hypothesis is None:
                    issues.append(
                        {
                            "kind": "missing_hypothesis",
                            "question_id": question.id,
                            "hypothesis_id": hypothesis_id,
                        }
                    )
                elif hypothesis.research_question != question.id:
                    issues.append(
                        {
                            "kind": "hypothesis_question_mismatch",
                            "question_id": question.id,
                            "hypothesis_id": hypothesis_id,
                        }
                    )
        for hypothesis in self.hypotheses.values():
            if hypothesis.research_question not in self.questions:
                issues.append(
                    {
                        "kind": "missing_question",
                        "question_id": hypothesis.research_question,
                        "hypothesis_id": hypothesis.id,
                    }
                )
        return issues
