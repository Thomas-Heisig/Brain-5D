"""Tests for orthogonal runtime state and observability modes."""

from __future__ import annotations

import pytest

from src.runtime.modes import (
    OBSERVABILITY_PROFILES,
    STATE_MODES,
    ObservabilityProfile,
    StateMode,
    validate_modes,
)


def test_mode_axes_are_independent() -> None:
    assert tuple(StateMode) == (
        StateMode.OPERATOR,
        StateMode.EXPERIMENT,
        StateMode.DEV,
    )
    assert tuple(ObservabilityProfile) == (
        ObservabilityProfile.FULL,
        ObservabilityProfile.SCIENTIFIC,
        ObservabilityProfile.MINIMAL,
        ObservabilityProfile.COMPUTE,
    )
    validate_modes("experiment", "compute")


@pytest.mark.parametrize("state_mode", ("observatory", "debug", ""))
def test_invalid_state_mode_is_rejected(state_mode: str) -> None:
    with pytest.raises(ValueError, match="state_mode"):
        validate_modes(state_mode, "minimal")


@pytest.mark.parametrize("observability", ("operator", "headless", ""))
def test_invalid_observability_is_rejected(observability: str) -> None:
    with pytest.raises(ValueError, match="observability"):
        validate_modes("operator", observability)


def test_public_value_lists_match_enum_values() -> None:
    assert STATE_MODES == ("operator", "experiment", "dev")
    assert OBSERVABILITY_PROFILES == ("full", "scientific", "minimal", "compute")
