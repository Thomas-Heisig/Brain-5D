"""Typed contracts for bounded scientific AI interactions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, ClassVar, Mapping, Self


class AIExposure(StrEnum):
    """How much causal access an AI component has to an experiment."""

    NONE = "none"
    OBSERVER_ONLY = "observer_only"
    SEMANTIC_INTERFACE = "semantic_interface"
    ADVISOR = "advisor"
    BOUNDED_CONTROLLER = "bounded_controller"
    ADAPTIVE_CONTROLLER = "adaptive_controller"


class CausalTaint(StrEnum):
    """Scientific classification of AI influence on an experiment."""

    PURE = "PURE"
    OBSERVED = "OBSERVED"
    PROPOSED = "PROPOSED"
    AI_INFLUENCED = "AI_INFLUENCED"


class AIReproducibility(StrEnum):
    """Registered reproducibility level for AI participation in a run."""

    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"


@dataclass(frozen=True, slots=True)
class ScientificContract:
    """Immutable, digest-backed data contract with no execution capability."""

    contract_id: str
    payload_digest: str
    source: str
    authority: str
    created_at: str
    kind: ClassVar[str] = "contract"

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, **asdict(self)}

    @classmethod
    def create(
        cls,
        *,
        payload: object,
        source: str,
        authority: str,
    ) -> Self:
        if not source.strip():
            raise ValueError("contract source must not be empty")
        if not authority.strip():
            raise ValueError("contract authority must not be empty")
        payload_digest = _digest(payload)
        identity = f"{cls.kind}|{source}|{authority}|{payload_digest}"
        contract_id = f"{cls.kind.upper()}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            contract_id=contract_id,
            payload_digest=payload_digest,
            source=source,
            authority=authority,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class Observation(ScientificContract):
    """Read-only observation; it carries no interpretation or action."""

    kind = "observation"


class Interpretation(ScientificContract):
    """Derived interpretation that is not evidence by itself."""

    kind = "interpretation"


class Proposal(ScientificContract):
    """Suggested next step; proposals require an external approval path."""

    kind = "proposal"


class Intervention(ScientificContract):
    """Description of a possible intervention, never an executable command."""

    kind = "intervention"


class Evidence(ScientificContract):
    """Reference to evidence whose scientific authority comes from its source."""

    kind = "evidence"


@dataclass(frozen=True, slots=True)
class AIInteractionRecord:
    """Audit record for one AI interaction; it grants no execution authority."""

    interaction_id: str
    role: str
    experiment_id: str | None
    tick: int | None
    input_digest: str
    prompt_digest: str
    output_digest: str
    model_provenance: dict[str, Any]
    authority: str
    exposure: AIExposure
    causal_effect: CausalTaint
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation for journals and APIs."""
        payload = asdict(self)
        payload["exposure"] = self.exposure.value
        payload["causal_effect"] = self.causal_effect.value
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)

    @classmethod
    def create(
        cls,
        *,
        role: str,
        experiment_id: str | None,
        tick: int | None,
        input_value: object,
        prompt: str,
        output_value: object,
        model_provenance: Mapping[str, Any],
        authority: str,
        exposure: AIExposure = AIExposure.OBSERVER_ONLY,
        causal_effect: CausalTaint = CausalTaint.OBSERVED,
    ) -> AIInteractionRecord:
        """Build a record from canonicalized values without storing their contents."""
        if not role.strip():
            raise ValueError("AI interaction role must not be empty")
        if not authority.strip():
            raise ValueError("AI interaction authority must not be empty")
        if tick is not None and tick < 0:
            raise ValueError("AI interaction tick must not be negative")

        input_digest = _digest(input_value)
        prompt_digest = _digest(prompt)
        output_digest = _digest(output_value)
        created_at = datetime.now(timezone.utc).isoformat()
        identity = "|".join(
            (
                role,
                experiment_id or "",
                str(tick) if tick is not None else "",
                input_digest,
                prompt_digest,
                output_digest,
            )
        )
        interaction_id = f"AIRC-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            interaction_id=interaction_id,
            role=role,
            experiment_id=experiment_id,
            tick=tick,
            input_digest=input_digest,
            prompt_digest=prompt_digest,
            output_digest=output_digest,
            model_provenance=dict(model_provenance),
            authority=authority,
            exposure=exposure,
            causal_effect=causal_effect,
            created_at=created_at,
        )


@dataclass(frozen=True, slots=True)
class AIInferenceFailureEvent:
    """Digest-backed audit record for a failed AI inference attempt."""

    event_id: str
    request_id: str
    backend: str
    request_digest: str
    latency_ms: float
    retry_status: str
    error: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        *,
        request_id: str,
        backend: str,
        request_digest: str,
        latency_ms: float,
        retry_status: str,
        error: str,
    ) -> AIInferenceFailureEvent:
        if not request_id.strip() or not backend.strip():
            raise ValueError("AI failure event identity must not be empty")
        if latency_ms < 0:
            raise ValueError("AI failure latency must not be negative")
        created_at = datetime.now(timezone.utc).isoformat()
        identity = "|".join((request_id, backend, request_digest, error, created_at))
        event_id = f"AIFE-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        return cls(
            event_id=event_id,
            request_id=request_id,
            backend=backend,
            request_digest=request_digest,
            latency_ms=latency_ms,
            retry_status=retry_status,
            error=error,
            created_at=created_at,
        )


def _digest(value: object) -> str:
    if isinstance(value, str):
        canonical = value
    else:
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
