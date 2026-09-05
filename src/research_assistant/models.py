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
        normalized_output = normalize_output(output)
        _validate_output(normalized_output, role)
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
            output=normalized_output,
            provenance={
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "research_packet_digest": packet.digest,
                "prompt_protocol_version": "research_assistant_v1",
                "assistant_schema_version": "1.2",
                "git_commit": packet.provenance.get("git_commit", "unknown"),
                "model_self_confidence": str(float(normalized_output["confidence"])),
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


def normalize_output(output: dict[str, Any]) -> dict[str, Any]:
    """Normalize common model-format variations before schema validation.

    Numeric strings and percentages are converted losslessly. If a model emits a
    qualitative, missing, boolean, non-finite, or out-of-range confidence value,
    the analysis itself is retained but its confidence is conservatively set to
    0.0. The original representation is preserved in ``confidence_original`` and
    the repair is recorded as a methodological concern. A formatting defect must
    not destroy an otherwise auditable analyst/reviewer/writer chain.
    """

    normalized = dict(output)
    raw_confidence = normalized.get("confidence")
    parsed: float | None = None

    if isinstance(raw_confidence, (int, float)) and not isinstance(raw_confidence, bool):
        parsed = float(raw_confidence)
    elif isinstance(raw_confidence, str):
        text = raw_confidence.strip().replace(",", ".")
        percentage = text.endswith("%")
        if percentage:
            text = text[:-1].strip()
        try:
            parsed = float(text)
        except ValueError:
            parsed = None
        if parsed is not None and percentage:
            parsed /= 100.0

    if parsed is not None and parsed == parsed and 0.0 <= parsed <= 1.0:
        normalized["confidence"] = parsed
        return normalized

    normalized["confidence_original"] = raw_confidence
    normalized["confidence"] = 0.0
    concerns = normalized.get("methodological_concerns")
    if not isinstance(concerns, list):
        concerns = []
    else:
        concerns = list(concerns)
    concerns.append(
        "Die vom Modell ausgegebene confidence war schemawidrig oder ausserhalb "
        "des Bereichs 0..1. Sie wurde fuer die AIRR-Provenienz konservativ auf "
        "0.0 gesetzt; der Originalwert bleibt als confidence_original erhalten."
    )
    normalized["methodological_concerns"] = concerns
    return normalized


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
    if role == "scientific_analyst" and not isinstance(output.get("effect_direction"), str):
        raise ValueError("Invalid AI analysis output field: effect_direction")
    confidence_value = output.get("confidence")
    if isinstance(confidence_value, bool) or not isinstance(confidence_value, (int, float)):
        raise ValueError("Invalid AI analysis output field: confidence")
    confidence = float(confidence_value)
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("AI analysis confidence must be between 0 and 1.")
