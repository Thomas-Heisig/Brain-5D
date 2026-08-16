from dataclasses import dataclass

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
