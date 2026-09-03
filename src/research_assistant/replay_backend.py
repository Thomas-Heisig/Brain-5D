"""Offline, digest-addressed replay backend for scientific AI runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping


class FrozenAIReplayError(ValueError):
    """Raised when a replay request is absent or has invalid fixture data."""


@dataclass(frozen=True, slots=True)
class FrozenAIReplayBackend:
    """Return only responses from a pre-recorded, immutable replay corpus."""

    responses: Mapping[str, str]
    model: str = "frozen-replay"

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("Replay model name must not be empty.")
        if any(
            not digest or not isinstance(text, str)
            for digest, text in self.responses.items()
        ):
            raise ValueError(
                "Replay responses must use non-empty digests and text values."
            )

    @staticmethod
    def request_digest(prompt: str) -> str:
        """Return the canonical digest used to address a replay response."""
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def __call__(self, prompt: str) -> tuple[str, dict[str, Any]]:
        request_digest = self.request_digest(prompt)
        if request_digest not in self.responses:
            raise FrozenAIReplayError(
                f"No frozen AI replay response for request digest {request_digest}."
            )
        text = self.responses[request_digest]
        return text, {
            "provider": "frozen_replay",
            "model": self.model,
            "request_digest": request_digest,
            "response_digest": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "retry_count": 0,
            "retry_policy": "disabled",
            "live_fallback": False,
        }

    @classmethod
    def from_records(
        cls,
        records: list[Mapping[str, object]],
        *,
        model: str = "frozen-replay",
    ) -> FrozenAIReplayBackend:
        """Build a replay backend from digest/text records without live access."""
        responses: dict[str, str] = {}
        for record in records:
            digest = record.get("request_digest")
            text = record.get("response")
            if not isinstance(digest, str) or not isinstance(text, str):
                raise FrozenAIReplayError(
                    "Replay records require request_digest and response."
                )
            if digest in responses and responses[digest] != text:
                raise FrozenAIReplayError(f"Conflicting replay response for {digest}.")
            responses[digest] = text
        return cls(responses=responses, model=model)

    def to_json(self) -> str:
        """Serialize fixture metadata only; no live provider is encoded."""
        return json.dumps(
            {"model": self.model, "request_digests": sorted(self.responses)},
            sort_keys=True,
            ensure_ascii=True,
        )
