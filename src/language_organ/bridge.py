"""Non-invasive data bridge between signal interpretation and a language backend."""

from __future__ import annotations

from dataclasses import dataclass

from src.signal_processing.models import SignalFrame

from .protocols import LanguageModelBackend, LanguageRequest, LanguageResponse


@dataclass(frozen=True, slots=True)
class LanguageOrganStatus:
    enabled: bool
    backend_name: str


class LanguageOrgan:
    """Own only language requests; never own the Brain-5D runtime loop."""

    def __init__(self, backend: LanguageModelBackend, *, enabled: bool = False) -> None:
        self._backend = backend
        self._enabled = enabled

    @property
    def status(self) -> LanguageOrganStatus:
        return LanguageOrganStatus(
            enabled=self._enabled,
            backend_name=self._backend.name,
        )

    def interpret_signal(
        self, *, request_id: str, frame: SignalFrame, instruction: str
    ) -> LanguageResponse:
        if not self._enabled:
            return LanguageResponse(
                request_id=request_id,
                text="",
                backend_name=self._backend.name,
                success=False,
                error="language organ disabled",
            )
        return self._backend.infer(
            LanguageRequest(
                request_id=request_id,
                purpose="signal_interpretation",
                text=instruction,
                signal_frame=frame,
            )
        )
