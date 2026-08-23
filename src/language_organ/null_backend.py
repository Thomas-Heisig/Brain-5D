"""Null backend that echoes input text — no external model required.

This module provides the :class:`NullBackend` and :class:`NullLanguageBackend`
classes, which implement the :class:`LanguageModelBackend` protocol by simply
echoing back the input text. These are used as default backends when no real
language model is configured.
"""

from __future__ import annotations

from .protocols import LanguageRequest, LanguageResponse


class NullLanguageBackend:
    """Legacy alias for :class:`NullBackend`."""

    @property
    def name(self) -> str:
        return "null"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        return NullBackend().infer(request)


class NullBackend:
    """Null backend that echoes the input text unchanged.

    This backend implements the :class:`LanguageModelBackend` protocol
    and simply returns the input text as the response. It is used when
    no real language model backend is configured.

    Example:
        >>> backend = NullBackend()
        >>> request = LanguageRequest(
        ...     request_id="req_001",
        ...     purpose="translate",
        ...     text="Hello, world!"
        ... )
        >>> response = backend.infer(request)
        >>> print(response.text)
        Hello, world!
    """

    @property
    def name(self) -> str:
        return "null"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        """Echo the request text back unchanged.

        Args:
            request: The language request to process.

        Returns:
            A LanguageResponse containing the original text.
        """
        return LanguageResponse(
            request_id=request.request_id,
            text=request.text,
            backend_name=self.name,
            success=True,
        )


__all__ = [
    "NullBackend",
    "NullLanguageBackend",
]
