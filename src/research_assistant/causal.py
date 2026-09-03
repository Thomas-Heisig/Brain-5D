"""Deterministic attribution reports for AI exposure and controlled runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CausalAttributionReport:
    """Manifest-derived attribution summary; it is not scientific evidence."""

    report_id: str
    experiment_id: str
    exposure: str
    causal_taint: str
    interaction_ids: tuple[str, ...]
    roles: tuple[str, ...]
    treatment: dict[str, Any] | None
    twin_run: dict[str, Any] | None
    ablation: dict[str, Any] | None
    scientific_evidence: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "experiment_id": self.experiment_id,
            "exposure": self.exposure,
            "causal_taint": self.causal_taint,
            "interaction_ids": list(self.interaction_ids),
            "roles": list(self.roles),
            "treatment": self.treatment,
            "twin_run": self.twin_run,
            "ablation": self.ablation,
            "scientific_evidence": self.scientific_evidence,
        }


def generate_causal_attribution_report(
    manifest: Mapping[str, Any],
) -> CausalAttributionReport:
    """Generate a digest-bound report for one exposure manifest."""
    experiment_id = manifest.get("experiment_id")
    exposure = manifest.get("ai_exposure")
    causal_taint = manifest.get("causal_taint")
    card = manifest.get("causal_card")
    if not isinstance(experiment_id, str) or not experiment_id.strip():
        raise ValueError("Causal attribution requires experiment_id")
    if not isinstance(exposure, str) or not exposure.strip():
        raise ValueError("Causal attribution requires ai_exposure")
    if not isinstance(causal_taint, str) or not causal_taint.strip():
        raise ValueError("Causal attribution requires causal_taint")
    if not isinstance(card, Mapping):
        raise ValueError("Causal attribution requires causal_card")
    interaction_ids = _string_tuple(card.get("interaction_ids", []), "interaction_ids")
    roles = _string_tuple(card.get("roles", []), "roles")
    treatment = _optional_mapping(manifest.get("ai_treatment"), "ai_treatment")
    twin_run = _optional_mapping(manifest.get("twin_run"), "twin_run")
    ablation = _optional_mapping(manifest.get("ablation"), "ablation")
    identity = json.dumps(
        {
            "experiment_id": experiment_id,
            "exposure": exposure,
            "causal_taint": causal_taint,
            "interaction_ids": interaction_ids,
            "roles": roles,
            "treatment": treatment,
            "twin_run": twin_run,
            "ablation": ablation,
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    report_id = f"CAR-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
    return CausalAttributionReport(
        report_id=report_id,
        experiment_id=experiment_id,
        exposure=exposure,
        causal_taint=causal_taint,
        interaction_ids=interaction_ids,
        roles=roles,
        treatment=treatment,
        twin_run=twin_run,
        ablation=ablation,
    )


def _string_tuple(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"Causal attribution {field} must contain strings")
    return tuple(value)


def _optional_mapping(value: object, field: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"Causal attribution {field} must be an object")
    return dict(value)
