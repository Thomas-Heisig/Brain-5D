"""Digest-backed records for comparing AI interpretations without creating evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ModelInterpretation:
    model_id: str
    research_packet_digest: str
    interpretation: str
    fingerprint: str

    @classmethod
    def create(cls, model_id: str, research_packet_digest: str, interpretation: str) -> ModelInterpretation:
        if not model_id.strip() or not research_packet_digest.strip() or not interpretation.strip():
            raise ValueError("Model interpretation identity and content must not be empty")
        return cls(model_id, research_packet_digest, interpretation, _digest(interpretation))


@dataclass(frozen=True, slots=True)
class AIResearchComparison:
    """Multi-model comparison; agreement is a measurement, never evidence."""

    research_packet_digest: str
    interpretations: tuple[ModelInterpretation, ...]
    disagreement_map: dict[str, tuple[str, ...]]
    agreement_score: float
    scientific_evidence: bool = False

    @classmethod
    def create(cls, interpretations: tuple[ModelInterpretation, ...]) -> AIResearchComparison:
        if not interpretations:
            raise ValueError("At least one model interpretation is required")
        packet_digests = {item.research_packet_digest for item in interpretations}
        if len(packet_digests) != 1:
            raise ValueError("All model interpretations must use the identical ResearchPacket")
        groups: dict[str, list[str]] = {}
        for item in interpretations:
            groups.setdefault(item.fingerprint, []).append(item.model_id)
        disagreement = {fingerprint: tuple(models) for fingerprint, models in groups.items()}
        agreement_score = max(len(models) for models in groups.values()) / len(interpretations)
        return cls(next(iter(packet_digests)), interpretations, disagreement, agreement_score)

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_packet_digest": self.research_packet_digest,
            "models": [item.model_id for item in self.interpretations],
            "disagreement_map": self.disagreement_map,
            "agreement_score": self.agreement_score,
            "scientific_evidence": self.scientific_evidence,
        }


@dataclass(frozen=True, slots=True)
class BlindAnalysis:
    """Anonymized group labels that can be revealed only through an explicit map."""

    labels: dict[str, str]
    reveal_map_digest: str
    revealed: bool = False

    @classmethod
    def create(cls, group_ids: tuple[str, ...], reveal_map: Mapping[str, str]) -> BlindAnalysis:
        if not group_ids or set(group_ids) != set(reveal_map):
            raise ValueError("Blind analysis requires a complete group-to-label map")
        labels = {group_id: f"GROUP-{index + 1:03d}" for index, group_id in enumerate(sorted(group_ids))}
        return cls(labels, _digest(dict(reveal_map)))


@dataclass(frozen=True, slots=True)
class ReviewerMetrics:
    corrected_errors: int
    false_criticisms: int
    missed_errors: int

    def __post_init__(self) -> None:
        if min(self.corrected_errors, self.false_criticisms, self.missed_errors) < 0:
            raise ValueError("Reviewer metrics must not be negative")

    def to_dict(self) -> dict[str, float]:
        total = self.corrected_errors + self.false_criticisms + self.missed_errors
        denominator = float(total or 1)
        return {
            "reviewer_correction_rate": self.corrected_errors / denominator,
            "false_criticism_rate": self.false_criticisms / denominator,
            "missed_error_rate": self.missed_errors / denominator,
        }


@dataclass(frozen=True, slots=True)
class BorrowedIntelligenceMetric:
    """Ablation metric that cannot be mistaken for standalone evidence."""

    protocol_id: str
    baseline_score: float
    assisted_score: float
    ceiling_score: float
    ratio: float
    scientific_evidence: bool = False

    @classmethod
    def create(
        cls,
        *,
        protocol_id: str,
        baseline_score: float,
        assisted_score: float,
        ceiling_score: float,
    ) -> BorrowedIntelligenceMetric:
        if not protocol_id.strip():
            raise ValueError("Borrowed Intelligence Ratio requires a registered protocol")
        ratio = borrowed_intelligence_ratio(
            baseline_score=baseline_score,
            assisted_score=assisted_score,
            ceiling_score=ceiling_score,
        )
        return cls(protocol_id, baseline_score, assisted_score, ceiling_score, ratio)

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "baseline_score": self.baseline_score,
            "assisted_score": self.assisted_score,
            "ceiling_score": self.ceiling_score,
            "borrowed_intelligence_ratio": self.ratio,
            "scientific_evidence": self.scientific_evidence,
        }


AIR_RESEARCH_QUESTIONS = tuple(f"RQ-AIR{i}" for i in range(1, 6))


def interpretation_distance(first: ModelInterpretation, second: ModelInterpretation) -> float:
    """Return a deterministic normalized distance based on token-set overlap."""
    first_tokens = set(first.interpretation.lower().split())
    second_tokens = set(second.interpretation.lower().split())
    union = first_tokens | second_tokens
    return 0.0 if not union else 1.0 - len(first_tokens & second_tokens) / len(union)


def borrowed_intelligence_ratio(*, baseline_score: float, assisted_score: float, ceiling_score: float) -> float:
    """Calculate an ablation ratio; the caller must register its protocol separately."""
    if ceiling_score <= baseline_score:
        raise ValueError("Ablation ceiling must exceed baseline score")
    return (assisted_score - baseline_score) / (ceiling_score - baseline_score)
