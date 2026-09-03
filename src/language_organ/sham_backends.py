"""Deterministic sham backends for controlled Language Organ experiments."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from .protocols import LanguageRequest, LanguageResponse


class ReplayLanguageError(ValueError):
    """Raised when a replay sham has no response for a request."""


@dataclass(frozen=True, slots=True)
class RandomLanguageOrgan:
    """Deterministic pseudo-random text control with no model semantics."""

    seed: int = 0
    vocabulary: tuple[str, ...] = ("control_alpha", "control_beta", "control_gamma")

    @property
    def name(self) -> str:
        return "random_sham"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        if not self.vocabulary:
            return LanguageResponse(
                request.request_id, "", self.name, False, "Sham vocabulary is empty."
            )
        digest = hashlib.sha256(
            f"{self.seed}|{request.request_id}|{request.text}".encode("utf-8")
        ).digest()
        choice = self.vocabulary[
            int.from_bytes(digest[:8], "big") % len(self.vocabulary)
        ]
        return LanguageResponse(request.request_id, choice, self.name, True)


@dataclass(frozen=True, slots=True)
class ReplayLanguageOrgan:
    """Digest-addressed replay control with no live fallback."""

    responses: Mapping[str, str]

    @property
    def name(self) -> str:
        return "replay_sham"

    @staticmethod
    def request_digest(request: LanguageRequest) -> str:
        canonical = f"{request.request_id}|{request.purpose}|{request.text}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        digest = self.request_digest(request)
        response = self.responses.get(digest)
        if response is None:
            return LanguageResponse(
                request.request_id,
                "",
                self.name,
                False,
                f"No replay response for request digest {digest}.",
            )
        return LanguageResponse(request.request_id, response, self.name, True)


__all__ = ["RandomLanguageOrgan", "ReplayLanguageError", "ReplayLanguageOrgan"]
