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
    evidence: list[dict[str, Any]]
    literature_sources: list[dict[str, Any]]
    protocol: dict[str, Any] | None
    known_limitations: list[str]
    previous_analyses: list[dict[str, Any]]
    provenance: dict[str, str]

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
    review: dict[str, str | None]
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
        _validate_output(output, role)
        now = datetime.now(timezone.utc)
        analysis_id = f"AIAR-{role}-{now:%Y%m%d%H%M%S%f}-{packet.digest[:8]}"
        return cls(
            analysis_id=analysis_id,
            role=role,
            model={
                "provider": str(model.get("provider", "unknown")),
                "model_name": str(model.get("model", "unknown")),
                "model_digest": str(model.get("model_digest", "unknown")),
                "quantization": str(model.get("quantization", "unknown")),
                "context_length": str(model.get("context_length", "unknown")),
                "temperature": float(model.get("temperature", 0.0)),
                "top_p": float(model.get("top_p", 1.0)),
                "seed": str(model.get("seed", "not_reported")),
                "backend_version": str(model.get("backend_version", "unknown")),
            },
            inputs={
                "experiment_id": packet.experiment_id,
                "packet_digest": packet.digest,
            },
            output=output,
            provenance={
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "research_packet_digest": packet.digest,
                "prompt_protocol_version": "research_assistant_v1",
                "assistant_schema_version": "1",
                "git_commit": packet.provenance.get("git_commit", "unknown"),
                "model_self_confidence": str(float(output["confidence"])),
            },
            review={
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "disposition": None,
            },
            epistemic_status={
                "evidence": False,
                "interpretation_only": True,
                "human_review_required": True,
            },
            generated_at=now.isoformat(),
        )


def _validate_output(output: dict[str, Any], role: str) -> None:
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
    if role == "scientific_analyst":
        if not isinstance(output.get("effect_direction"), str):
            raise ValueError("Invalid AI analysis output field: effect_direction")
    if not isinstance(output.get("confidence"), (int, float)):
        raise ValueError("Invalid AI analysis output field: confidence")
    confidence = float(output["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("AI analysis confidence must be between 0 and 1.")
