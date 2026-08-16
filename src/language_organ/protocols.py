"""Read-only, replaceable language model backend contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.signal_processing.models import SignalFrame


@dataclass(frozen=True, slots=True)
class LanguageRequest:
    """A bounded request to the optional language organ."""

    request_id: str
    purpose: str
    text: str
    signal_frame: SignalFrame | None = None


@dataclass(frozen=True, slots=True)
class LanguageResponse:
    """Language-organ result. It is data, never a runtime command."""

    request_id: str
    text: str
    backend_name: str
    success: bool
    error: str | None = None


class LanguageModelBackend(Protocol):
    """Backend contract that deliberately exposes no Brain-5D runtime object."""

    @property
    def name(self) -> str:
        """Return the backend identifier."""

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        """Return text data only; never mutate Brain-5D state."""
