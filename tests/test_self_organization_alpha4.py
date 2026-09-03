from dataclasses import dataclass, replace

import pytest

from src.self_organization.policy import (
    SelfOrganizationPolicy,
    SelfOrganizationPolicyConfig,
)


@dataclass(frozen=True)
class Signal:
    tick: int = 10
    neuron_count: int = 1000
    target_rate_hz: float = 5.0
    mean_rate_hz: float = 0.5
    low_rate_neurons: int = 900
    high_rate_neurons: int = 0
    low_energy_neurons: int = 0


def test_policy_produces_dry_run_neurogenesis_pressure() -> None:
    report = SelfOrganizationPolicy(SelfOrganizationPolicyConfig()).analyze(Signal())
    assert report.neurogenesis_pressure > 0
    assert report.proposals


def test_policy_hysteresis_requires_release_before_repeating_proposal() -> None:
    policy = SelfOrganizationPolicy(
        SelfOrganizationPolicyConfig(
            neurogenesis_threshold=0.5,
            pruning_enabled=False,
            synapse_sprouting_enabled=False,
            synapse_pruning_enabled=False,
        )
    )
    high = replace(Signal(), low_rate_neurons=800)
    released = replace(Signal(), low_rate_neurons=300)

    assert policy.analyze(high).proposals
    assert not policy.analyze(high).proposals
    assert not policy.analyze(released).proposals
    assert policy.analyze(high).proposals


def test_policy_rejects_invalid_hysteresis_ratio() -> None:
    with pytest.raises(ValueError, match="hysteresis_release_ratio"):
        SelfOrganizationPolicyConfig(hysteresis_release_ratio=1.0)
