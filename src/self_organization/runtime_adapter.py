"""Runtime adapter that connects HomeostasisSignal to the structural coordinator.

This adapter is the bridge between live runtime measurements and the
canonical structural mutation path. It runs as a post-tick hook and:

1. Captures the real HomeostasisSignal from HomeostasisEngine
2. Feeds it through SelfOrganizationPolicy.analyze()
3. Publishes the resulting PolicyReport to the SelfOrganizationCoordinator

It does NOT mutate the network. Mutation remains exclusively in:
    Proposal -> Approval -> StructuralPlasticityEngine -> Manipulator

This is the missing link that closes Gate A for the production path.
"""

from __future__ import annotations

from typing import Any

from src.homeostasis.engine import HomeostasisEngine
from src.self_organization.coordinator import SelfOrganizationCoordinator
from src.self_organization.policy import SelfOrganizationPolicy, SelfOrganizationPolicyConfig


class SelfOrganizationRuntimeAdapter:
    """Post-tick hook that feeds real HomeostasisSignals into the structural coordinator.

    The adapter is attached to the RuntimeController and runs after every
    tick. It builds a HomeostasisSignal from the live network, passes it
    through the SelfOrganizationPolicy, and publishes the resulting
    PolicyReport to the coordinator.

    The coordinator does NOT automatically execute proposals — approval
    is required (manual or policy-based).
    """

    def __init__(
        self,
        homeostasis_engine: HomeostasisEngine,
        coordinator: SelfOrganizationCoordinator,
        *,
        interval_ticks: int = 10,
        policy_config: SelfOrganizationPolicyConfig | None = None,
    ) -> None:
        self.homeostasis_engine = homeostasis_engine
        self.coordinator = coordinator
        self.interval_ticks = interval_ticks
        self.policy = SelfOrganizationPolicy(
            policy_config or SelfOrganizationPolicyConfig(enabled=True, dry_run=True)
        )
        self._last_tick: int = 0

    def __call__(self, tick: int, _result: Any) -> None:
        """Post-tick hook: build signal, run policy, publish to coordinator.

        Runs every ``interval_ticks`` ticks to avoid excessive overhead.
        """
        if tick - self._last_tick < self.interval_ticks:
            return
        self._last_tick = tick

        try:
            signal = self.homeostasis_engine.build_signal(tick=tick)
            report = self.policy.analyze(signal)
            if report.proposals:
                self.coordinator.publish(report)
        except Exception:
            # Hook must never break the simulation
            pass
