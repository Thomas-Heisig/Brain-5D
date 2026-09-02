"""Immutable, provenance-carrying records for the research assistant."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class ResearchPacket:
    """The complete, deterministic read-only context supplied to an assistant."""

    experiment_id: str
    research_question: dict[str, Any]
    hypotheses: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    manifest: dict[str, Any]
    data: dict[str, Any] | None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=True)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AIAnalysisRecord:
    """Schema-validated interpretation only; never scientific evidence."""

    analysis_id: str
    role: str
    model: dict[str, str | float]
    inputs: dict[str, Any]
    output: dict[str, Any]
    provenance: dict[str, str]
    epistemic_status: dict[str, bool]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        *,
        role: str,
        model: dict[str, str | float],
        packet: ResearchPacket,
        output: dict[str, Any],
        prompt: str,
    ) -> AIAnalysisRecord:
        _validate_output(output)
        now = datetime.now(timezone.utc)
        analysis_id = f"AIAR-{now:%Y-%m-%d-%H%M%S}-{packet.digest[:8]}"
        return cls(
            analysis_id=analysis_id,
            role=role,
            model=model,
            inputs={
                "experiment_id": packet.experiment_id,
                "packet_digest": packet.digest,
            },
            output=output,
            provenance={
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "input_digest": packet.digest,
            },
            epistemic_status={
                "evidence": False,
                "interpretation_only": True,
                "human_review_required": True,
            },
            generated_at=now.isoformat(),
        )


def _validate_output(output: dict[str, Any]) -> None:
    if not isinstance(output.get("assessment"), str):
        raise ValueError("Invalid AI analysis output field: assessment")
    for name in (
        "observations",
        "methodological_concerns",
        "alternative_explanations",
        "recommended_experiments",
        "requested_evidence",
    ):
        if not isinstance(output.get(name), list):
            raise ValueError(f"Invalid AI analysis output field: {name}")
    if not isinstance(output.get("confidence"), (int, float)):
        raise ValueError("Invalid AI analysis output field: confidence")
    confidence = float(output["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("AI analysis confidence must be between 0 and 1.")
