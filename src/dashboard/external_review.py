"""Read-only public review readiness, isolated from private participant responses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

_PUBLIC_INSTRUMENT_FILES = (
    "review_portal/catalogue.py",
    "src/dashboard/static/review/instrument.js",
)


def build_external_review_status(repository_root: Path) -> dict[str, Any]:
    """Verify public instrument bytes; neither import the collector nor read responses."""
    unavailable: dict[str, Any] = {
        "available": False,
        "status": "unavailable",
        "human_review_status": "unknown",
        "external_ethics_approval": "not_claimed",
        "automatic_evidence_promotion": False,
        "scientific_evidence": False,
        "response_count": None,
    }
    try:
        raw: object = json.loads(
            (repository_root / "research/external_review/integration.json").read_text(
                encoding="utf-8"
            )
        )
        if not isinstance(raw, dict):
            raise ValueError("Invalid review metadata")
        data = cast(dict[str, Any], raw)
        if (
            data.get("schema_version") != 1
            or data.get("owner") != "research.external_review"
        ):
            raise ValueError("Unknown review metadata schema or owner")
        if data.get("automatic_evidence_promotion") is not False:
            raise ValueError("Review data cannot promote evidence")
        if (
            data.get("human_review_status") != "not_recorded"
            or data.get("external_ethics_approval") != "not_claimed"
        ):
            raise ValueError(
                "This public contract cannot grant review or ethics approval"
            )
        sources_value = data.get("source_files")
        if not isinstance(sources_value, dict):
            raise ValueError("Public instrument sources incomplete")
        sources = cast(dict[str, Any], sources_value)
        if set(sources) != set(_PUBLIC_INSTRUMENT_FILES):
            raise ValueError("Public instrument sources incomplete")
        for relative in _PUBLIC_INSTRUMENT_FILES:
            source = repository_root / relative
            if source.is_symlink() or not source.resolve().is_relative_to(
                repository_root.resolve()
            ):
                raise ValueError("Unsafe public instrument path")
            if hashlib.sha256(source.read_bytes()).hexdigest() != sources[relative]:
                raise ValueError("Public instrument version drift")
        return {
            **data,
            "available": True,
            "status": "instrument_available_assessment_pending",
            "scientific_evidence": False,
            "response_count": None,
            "response_storage": "private_external_not_accessed",
            "public_deployment": "not_verified_by_dashboard",
        }
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {**unavailable, "reason": str(exc)}
