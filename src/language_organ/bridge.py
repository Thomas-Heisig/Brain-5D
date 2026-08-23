"""Non-invasive data bridge between signal interpretation and a language backend.

This module provides the LanguageOrgan class, which acts as a controlled,
read-only bridge between the Brain-5D signal processing subsystem and an
optional language model backend.

The LanguageOrgan is designed to be:
- Non-invasive – Never mutates Brain-5D state
- Replaceable – Uses the LanguageModelBackend protocol
- Optional – Can be disabled without affecting the simulation
- Observable – Provides status information for the dashboard

It translates between symbolic instructions (text) and subsymbolic
SignalFrames, enabling semantic interpretation and monitoring without
allowing direct network mutation.

Design Principle:
    The LanguageOrgan does not own the Brain-5D runtime loop. It only
    processes requests and returns data. The simulation continues even
    if the language organ is disabled or fails.

Example:
    >>> from src.language_organ import LanguageOrgan, NullBackend
    >>> from src.signal_processing.models import SignalFrame
    >>> backend = NullBackend()
    >>> organ = LanguageOrgan(backend, enabled=True)
    >>> frame = SignalFrame(...)  # from signal processing
    >>> response = organ.interpret_signal(
    ...     request_id="req_001",
    ...     frame=frame,
    ...     instruction="Describe the current network activity."
    ... )
    >>> print(response.text)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.signal_processing.models import SignalFrame

from .protocols import LanguageModelBackend, LanguageRequest, LanguageResponse

# ============================================================================
# Status Model
# ============================================================================


@dataclass(frozen=True, slots=True)
class LanguageOrganStatus:
    """Status of the language organ for dashboard and monitoring.

    Attributes:
        enabled: Whether the language organ is enabled.
        backend_name: Name of the configured backend (or 'null').
    """

    enabled: bool
    backend_name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "backend_name": self.backend_name,
        }


# ============================================================================
# Language Organ
# ============================================================================


class LanguageOrgan:
    """Own only language requests; never own the Brain-5D runtime loop.

    This class acts as a controlled adapter between the signal processing
    subsystem and a language model backend. It processes requests for
    signal interpretation and text translation, but never mutates the
    Brain-5D state.

    The LanguageOrgan is designed to be used with the dashboard and
    operator console for semantic interpretation of network activity.

    Attributes:
        backend: The language model backend (must implement LanguageModelBackend).
        enabled: Whether the language organ is enabled (default: False).

    Example:
        >>> organ = LanguageOrgan(backend, enabled=True)
        >>> status = organ.status
        >>> print(status.enabled)
        True
    """

    def __init__(self, backend: LanguageModelBackend, *, enabled: bool = False) -> None:
        """Initialize the language organ.

        Args:
            backend: The language model backend to use.
            enabled: Whether the language organ is enabled initially.
        """
        self._backend = backend
        self._enabled = enabled

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def status(self) -> LanguageOrganStatus:
        """Return the current status of the language organ.

        Returns:
            LanguageOrganStatus with enabled state and backend name.
        """
        return LanguageOrganStatus(
            enabled=self._enabled,
            backend_name=self._backend.name,
        )

    @property
    def enabled(self) -> bool:
        """Check whether the language organ is enabled."""
        return self._enabled

    @property
    def backend_name(self) -> str:
        """Return the name of the configured backend."""
        return self._backend.name

    # ========================================================================
    # Control Methods
    # ========================================================================

    def enable(self) -> None:
        """Enable the language organ."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the language organ."""
        self._enabled = False

    def set_enabled(self, enabled: bool) -> None:
        """Set the enabled state of the language organ.

        Args:
            enabled: Whether to enable or disable the organ.
        """
        self._enabled = enabled

    # ========================================================================
    # Request Methods
    # ========================================================================

    def interpret_signal(
        self,
        *,
        request_id: str,
        frame: SignalFrame,
        instruction: str,
    ) -> LanguageResponse:
        """Interpret a signal frame using the language backend.

        This method sends a SignalFrame along with an instruction to the
        language backend for interpretation. The response is a text-based
        interpretation of the signal.

        Args:
            request_id: Unique identifier for the request (for traceability).
            frame: The SignalFrame to interpret.
            instruction: Natural language instruction for the interpretation.

        Returns:
            A LanguageResponse containing the interpretation or error.
        """
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

    def translate_text(
        self,
        *,
        request_id: str,
        text: str,
        purpose: str = "translate",
    ) -> LanguageResponse:
        """Translate text using the language backend.

        This method sends a text request to the language backend without
        any accompanying SignalFrame. It is useful for pure text operations
        like translation, summarization, or question answering.

        Args:
            request_id: Unique identifier for the request (for traceability).
            text: The text to process.
            purpose: The purpose of the request (default: 'translate').

        Returns:
            A LanguageResponse containing the result or error.
        """
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
                purpose=purpose,
                text=text,
                signal_frame=None,
            )
        )

    def describe_network(
        self,
        *,
        request_id: str,
        frame: SignalFrame,
    ) -> LanguageResponse:
        """Describe the current network state using the language backend.

        This is a convenience method that calls interpret_signal with a
        standard instruction for network description.

        Args:
            request_id: Unique identifier for the request.
            frame: The SignalFrame to describe.

        Returns:
            A LanguageResponse containing the description or error.
        """
        return self.interpret_signal(
            request_id=request_id,
            frame=frame,
            instruction="Describe the current neural network activity.",
        )

    def monitor_network(
        self,
        *,
        request_id: str,
        frame: SignalFrame,
    ) -> LanguageResponse:
        """Monitor the network state for anomalies using the language backend.

        This is a convenience method that calls interpret_signal with a
        standard instruction for network monitoring.

        Args:
            request_id: Unique identifier for the request.
            frame: The SignalFrame to monitor.

        Returns:
            A LanguageResponse containing the monitoring report or error.
        """
        return self.interpret_signal(
            request_id=request_id,
            frame=frame,
            instruction="Analyze the network activity for anomalies or patterns.",
        )

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        """Return a string representation of the language organ."""
        return (
            f"LanguageOrgan(backend={self._backend.name!r}, "
            f"enabled={self._enabled})"
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "LanguageOrgan",
    "LanguageOrganStatus",
]
