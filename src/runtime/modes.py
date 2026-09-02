"""Orthogonal runtime state and observability modes."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class StateMode(StrEnum):
    """Persistence and lifecycle boundary for a running Brain-5D state."""

    OPERATOR = "operator"
    EXPERIMENT = "experiment"
    DEV = "dev"


class ObservabilityProfile(StrEnum):
    """Independent amount of telemetry and rendering work."""

    FULL = "full"
    SCIENTIFIC = "scientific"
    MINIMAL = "minimal"
    COMPUTE = "compute"


STATE_MODES: Final[tuple[str, ...]] = tuple(item.value for item in StateMode)
OBSERVABILITY_PROFILES: Final[tuple[str, ...]] = tuple(
    item.value for item in ObservabilityProfile
)


def validate_modes(state_mode: str, observability: str) -> None:
    """Reject invalid mode values at configuration boundaries."""
    if state_mode not in STATE_MODES:
        raise ValueError(
            f"state_mode must be one of {STATE_MODES}, got {state_mode!r}"
        )
    if observability not in OBSERVABILITY_PROFILES:
        raise ValueError(
            "observability must be one of "
            f"{OBSERVABILITY_PROFILES}, got {observability!r}"
        )
