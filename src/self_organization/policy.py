"""Policy boundary between homeostasis and structural self-organization.

Alpha.3 turns homeostasis signals into typed proposals.  The policy itself never
mutates the network; execution remains a separate, auditable concern.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.dashboard.models import JSONValue
from src.homeostasis.signals import HomeostasisSignal


class StructuralAction(StrEnum):
    """Supported structural actions."""

    NONE = "none"
    NEUROGENESIS = "neurogenesis"
    PRUNE = "prune"


@dataclass(frozen=True, slots=True)
class SelfOrganizationParameters:
    """Conservative policy thresholds for structural proposals."""

    minimum_neurons_for_pruning: int = 10
    chronic_window: int = 20
    low_rate_fraction_trigger: float = 0.50
    high_rate_fraction_trigger: float = 0.50
    low_energy_fraction_trigger: float = 0.35
    neurogenesis_cooldown_ticks: int = 1_000
    pruning_cooldown_ticks: int = 1_000
    max_neurogenesis_per_proposal: int = 4
    max_pruning_per_proposal: int = 4


@dataclass(frozen=True, slots=True)
class StructuralProposal:
    """Read-only request for a later mutation layer."""

    tick: int
    action: StructuralAction
    count: int
    reason: str
    pressure: float

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tick": self.tick,
            "action": self.action.value,
            "count": self.count,
            "reason": self.reason,
            "pressure": self.pressure,
        }


class SelfOrganizationPolicy:
    """Convert chronic homeostasis imbalance into bounded proposals."""

    def __init__(self, parameters: SelfOrganizationParameters | None = None) -> None:
        self.parameters = parameters or SelfOrganizationParameters()
        self._low_rate_streak = 0
        self._high_pressure_streak = 0
        self._last_neurogenesis_tick = -10**18
        self._last_pruning_tick = -10**18
        self._last_proposal = StructuralProposal(
            tick=0,
            action=StructuralAction.NONE,
            count=0,
            reason="initial state",
            pressure=0.0,
        )

    @property
    def last_proposal(self) -> StructuralProposal:
        """Return the most recent policy result."""
        return self._last_proposal

    def evaluate(self, signal: HomeostasisSignal) -> StructuralProposal:
        """Evaluate one homeostasis sample without mutating the network."""
        if signal.neuron_count <= 0:
            return self._publish_none(signal.tick, "no neurons")

        low_rate_fraction = signal.low_rate_neurons / signal.neuron_count
        high_rate_fraction = signal.high_rate_neurons / signal.neuron_count
        low_energy_fraction = signal.low_energy_neurons / signal.neuron_count

        low_rate_pressure = max(
            0.0,
            low_rate_fraction - self.parameters.low_rate_fraction_trigger,
        )
        prune_pressure = max(
            0.0,
            max(
                high_rate_fraction - self.parameters.high_rate_fraction_trigger,
                low_energy_fraction - self.parameters.low_energy_fraction_trigger,
            ),
        )

        self._low_rate_streak = (
            self._low_rate_streak + 1 if low_rate_pressure > 0.0 else 0
        )
        self._high_pressure_streak = (
            self._high_pressure_streak + 1 if prune_pressure > 0.0 else 0
        )

        if (
            self._low_rate_streak >= self.parameters.chronic_window
            and signal.tick - self._last_neurogenesis_tick
            >= self.parameters.neurogenesis_cooldown_ticks
        ):
            count = max(
                1,
                min(
                    self.parameters.max_neurogenesis_per_proposal,
                    round(low_rate_pressure * signal.neuron_count),
                ),
            )
            self._last_neurogenesis_tick = signal.tick
            self._low_rate_streak = 0
            return self._publish(
                StructuralProposal(
                    tick=signal.tick,
                    action=StructuralAction.NEUROGENESIS,
                    count=count,
                    reason="chronically low firing activity",
                    pressure=low_rate_pressure,
                )
            )

        if (
            signal.neuron_count >= self.parameters.minimum_neurons_for_pruning
            and self._high_pressure_streak >= self.parameters.chronic_window
            and signal.tick - self._last_pruning_tick
            >= self.parameters.pruning_cooldown_ticks
        ):
            count = max(
                1,
                min(
                    self.parameters.max_pruning_per_proposal,
                    round(prune_pressure * signal.neuron_count),
                ),
            )
            self._last_pruning_tick = signal.tick
            self._high_pressure_streak = 0
            return self._publish(
                StructuralProposal(
                    tick=signal.tick,
                    action=StructuralAction.PRUNE,
                    count=count,
                    reason="chronic high-rate or low-energy pressure",
                    pressure=prune_pressure,
                )
            )

        return self._publish_none(signal.tick, "inside structural dead-band")

    def _publish_none(self, tick: int, reason: str) -> StructuralProposal:
        return self._publish(
            StructuralProposal(
                tick=tick,
                action=StructuralAction.NONE,
                count=0,
                reason=reason,
                pressure=0.0,
            )
        )

    def _publish(self, proposal: StructuralProposal) -> StructuralProposal:
        self._last_proposal = proposal
        return proposal
