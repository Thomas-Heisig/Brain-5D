"""Tests for the alpha.3 homeostasis-to-structure boundary."""

from src.homeostasis.signals import HomeostasisSignal
from src.self_organization.policy import (
    SelfOrganizationParameters,
    SelfOrganizationPolicy,
    StructuralAction,
)


def _signal(
    tick: int, *, low: int = 0, high: int = 0, low_energy: int = 0
) -> HomeostasisSignal:
    return HomeostasisSignal(
        tick=tick,
        neuron_count=100,
        mean_rate_hz=5.0,
        rate_variance_hz2=1.0,
        mean_threshold_adaptation=0.0,
        mean_energy=1.0,
        mean_energy_error=0.0,
        low_rate_neurons=low,
        high_rate_neurons=high,
        low_energy_neurons=low_energy,
        high_energy_neurons=0,
    )


def test_chronic_low_rate_proposes_bounded_neurogenesis() -> None:
    policy = SelfOrganizationPolicy(
        SelfOrganizationParameters(
            chronic_window=3,
            neurogenesis_cooldown_ticks=10,
            max_neurogenesis_per_proposal=4,
        )
    )
    assert policy.evaluate(_signal(1, low=80)).action is StructuralAction.NONE
    assert policy.evaluate(_signal(2, low=80)).action is StructuralAction.NONE
    proposal = policy.evaluate(_signal(3, low=80))
    assert proposal.action is StructuralAction.NEUROGENESIS
    assert 1 <= proposal.count <= 4


def test_dead_band_does_not_mutate_or_propose() -> None:
    policy = SelfOrganizationPolicy(SelfOrganizationParameters(chronic_window=2))
    proposal = policy.evaluate(_signal(100, low=10, high=10, low_energy=10))
    assert proposal.action is StructuralAction.NONE
    assert proposal.count == 0
