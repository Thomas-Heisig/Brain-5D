"""Typed contracts for bounded scientific AI interactions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping


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


def _digest(value: object) -> str:
    if isinstance(value, str):
        canonical = value
    else:
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
