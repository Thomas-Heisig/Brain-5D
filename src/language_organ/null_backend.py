"""No-op backend used when the language organ is disabled."""

from __future__ import annotations

from .protocols import LanguageRequest, LanguageResponse


class NullLanguageBackend:
    """A deterministic backend that performs no model inference."""

    @property
    def name(self) -> str:
        return "null"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        return LanguageResponse(
            request_id=request.request_id,
            text="",
            backend_name=self.name,
            success=False,
            error="language organ disabled",
        )
