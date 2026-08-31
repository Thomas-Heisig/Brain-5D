"""Typed dry-run policy that converts homeostasis signals into proposals."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Protocol, TypeAlias, cast

if TYPE_CHECKING:
    from src.dashboard.models import JSONValue

JSONScalar: TypeAlias = str | int | float | bool | None
ProposalMetadata: TypeAlias = Mapping[str, JSONScalar]
Coord5D: TypeAlias = tuple[int, int, int, int, int]


def _empty_metadata() -> dict[str, JSONScalar]:
    return {}


class HomeostasisSignalLike(Protocol):
    @property
    def tick(self) -> int: ...

    @property
    def neuron_count(self) -> int: ...

    @property
    def target_rate_hz(self) -> float: ...

    @property
    def mean_rate_hz(self) -> float: ...

    @property
    def low_rate_neurons(self) -> int: ...

    @property
    def high_rate_neurons(self) -> int: ...

    @property
    def low_energy_neurons(self) -> int: ...


class ProposalKind(str, Enum):
    NEUROGENESIS = "neurogenesis"
    PRUNING = "pruning"
    SYNAPSE_SPROUTING = "synapse_sprouting"
    SYNAPSE_PRUNING = "synapse_pruning"


class StructuralAction(str, Enum):
    """Legacy alpha.3 structural actions."""

    NONE = "none"
    NEUROGENESIS = "neurogenesis"
    PRUNE = "prune"


@dataclass(frozen=True, slots=True)
class SelfOrganizationParameters:
    """Legacy alpha.3 policy thresholds."""

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
class LegacyStructuralProposal:
    """Legacy alpha.3 bounded structural proposal."""

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


@dataclass(frozen=True, slots=True)
class StructuralProposal:
    proposal_id: str
    kind: ProposalKind
    neuron_id: int | None = None
    coord: Coord5D | None = None
    target_id: int | None = None
    reason: str = ""
    confidence: float = 0.0
    metadata: ProposalMetadata = field(default_factory=_empty_metadata)


@dataclass(frozen=True, slots=True)
class PolicyReport:
    tick: int
    proposals: tuple[StructuralProposal, ...]
    neurogenesis_pressure: float
    pruning_pressure: float
    synapse_sprouting_pressure: float
    synapse_pruning_pressure: float


@dataclass(frozen=True, slots=True)
class SelfOrganizationPolicyConfig:
    enabled: bool = True
    dry_run: bool = True
    neurogenesis_threshold: float = 0.9
    pruning_threshold: float = 0.9
    synapse_sprouting_threshold: float = 0.5
    synapse_pruning_threshold: float = 0.5
    max_neurons: int = 10_000
    min_neurons: int = 100
    # Mechanism enable/disable flags — these gate whether the policy
    # emits proposals of each kind. When a flag is False, the policy
    # must NEVER emit that proposal kind, regardless of pressure.
    neurogenesis_enabled: bool = True
    pruning_enabled: bool = True
    synapse_sprouting_enabled: bool = True
    synapse_pruning_enabled: bool = True

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> SelfOrganizationPolicyConfig:
        """Build a config-authoritative policy config from the YAML
        ``self_organization`` section.

        Maps canonical YAML fields to policy config fields. When a YAML
        field is absent, the default value from this dataclass is used.

        Explicit mapping (YAML key → config field):
            enabled                      → enabled
            interval_ticks               → (used by RuntimeAdapter, not here)
            neurogenesis_enabled         → neurogenesis_enabled
            pruning_enabled              → pruning_enabled
            sprouting_enabled            → synapse_sprouting_enabled
            synapse_pruning_enabled      → synapse_pruning_enabled (note: YAML
                                           uses ``synapse_pruning_enabled`` if
                                           present, otherwise falls back to the
                                           general ``pruning_enabled`` semantic)
            max_neurons                  → max_neurons
            neurogenesis_max_per_cycle   → (used by plasticity limits, not here)

        Thresholds are kept at their dataclass defaults unless explicitly
        overridden in config. The ``dry_run`` field is always False for
        production — it is set by the coordinator, not the policy config.

        Raises:
            TypeError: If a config value has the wrong type.
        """
        section = _string_mapping(config, "self_organization")
        enabled = _bool_value(section.get("enabled", True), "enabled")

        # Mechanism enable flags: explicit YAML fields.
        neurogenesis_enabled = _bool_value(
            section.get("neurogenesis_enabled", True), "neurogenesis_enabled"
        )
        pruning_enabled = _bool_value(
            section.get("pruning_enabled", True), "pruning_enabled"
        )
        # YAML uses ``sprouting_enabled`` for synapse sprouting
        synapse_sprouting_enabled = _bool_value(
            section.get("sprouting_enabled", True), "sprouting_enabled"
        )
        # YAML uses ``synapse_pruning_enabled`` or falls back to pruning_enabled
        synapse_pruning_enabled = _bool_value(
            section.get("synapse_pruning_enabled", pruning_enabled),
            "synapse_pruning_enabled",
        )

        # Thresholds (optional, with dataclass defaults)
        neurogenesis_threshold = _float_value(
            section.get("neurogenesis_threshold", 0.9), "neurogenesis_threshold"
        )
        pruning_threshold = _float_value(
            section.get("pruning_threshold", 0.9), "pruning_threshold"
        )
        synapse_sprouting_threshold = _float_value(
            section.get("synapse_sprouting_threshold", 0.5),
            "synapse_sprouting_threshold",
        )
        synapse_pruning_threshold = _float_value(
            section.get("synapse_pruning_threshold", 0.5),
            "synapse_pruning_threshold",
        )

        # Limits
        max_neurons = _int_value(section.get("max_neurons", 10_000), "max_neurons")
        min_neurons = _int_value(section.get("min_neurons", 100), "min_neurons")

        return cls(
            enabled=enabled,
            dry_run=False,  # production: dry_run is controlled by coordinator
            neurogenesis_enabled=neurogenesis_enabled,
            pruning_enabled=pruning_enabled,
            synapse_sprouting_enabled=synapse_sprouting_enabled,
            synapse_pruning_enabled=synapse_pruning_enabled,
            neurogenesis_threshold=neurogenesis_threshold,
            pruning_threshold=pruning_threshold,
            synapse_sprouting_threshold=synapse_sprouting_threshold,
            synapse_pruning_threshold=synapse_pruning_threshold,
            max_neurons=max_neurons,
            min_neurons=min_neurons,
        )


class SelfOrganizationPolicy:
    """Generate proposals only. No network mutation happens here."""

    def __init__(
        self,
        config: SelfOrganizationPolicyConfig | SelfOrganizationParameters | None = None,
    ) -> None:
        self.config = (
            config
            if isinstance(config, SelfOrganizationPolicyConfig)
            else SelfOrganizationPolicyConfig()
        )
        self.parameters = (
            config
            if isinstance(config, SelfOrganizationParameters)
            else SelfOrganizationParameters()
        )
        self._low_rate_streak = 0
        self._high_pressure_streak = 0
        self._last_neurogenesis_tick = -(10**18)
        self._last_pruning_tick = -(10**18)
        self._last_proposal = LegacyStructuralProposal(
            tick=0,
            action=StructuralAction.NONE,
            count=0,
            reason="initial state",
            pressure=0.0,
        )

    @property
    def last_proposal(self) -> LegacyStructuralProposal:
        """Return the most recent alpha.3 policy result."""
        return self._last_proposal

    def evaluate(self, signal: HomeostasisSignalLike) -> LegacyStructuralProposal:
        """Evaluate the legacy alpha.3 policy without mutating the network."""
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
            high_rate_fraction - self.parameters.high_rate_fraction_trigger,
            low_energy_fraction - self.parameters.low_energy_fraction_trigger,
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
                LegacyStructuralProposal(
                    signal.tick,
                    StructuralAction.NEUROGENESIS,
                    count,
                    "chronically low firing activity",
                    low_rate_pressure,
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
                LegacyStructuralProposal(
                    signal.tick,
                    StructuralAction.PRUNE,
                    count,
                    "chronic high-rate or low-energy pressure",
                    prune_pressure,
                )
            )

        return self._publish_none(signal.tick, "inside structural dead-band")

    def _publish_none(self, tick: int, reason: str) -> LegacyStructuralProposal:
        return self._publish(
            LegacyStructuralProposal(tick, StructuralAction.NONE, 0, reason, 0.0)
        )

    def _publish(self, proposal: LegacyStructuralProposal) -> LegacyStructuralProposal:
        self._last_proposal = proposal
        return proposal

    def analyze(self, signal: HomeostasisSignalLike) -> PolicyReport:
        count = max(1, signal.neuron_count)
        target = max(1e-9, signal.target_rate_hz)
        low_rate_ratio = signal.low_rate_neurons / count
        high_rate_ratio = signal.high_rate_neurons / count
        low_energy_ratio = signal.low_energy_neurons / count

        neuro = max(0.0, (low_rate_ratio - 0.20) * 2.0)
        prune = max(0.0, (high_rate_ratio - 0.20) * 2.0)
        sprout = max(0.0, abs(signal.mean_rate_hz - target) / target - 0.50)
        syn_prune = max(0.0, (low_energy_ratio - 0.10) * 3.0)
        proposals: list[StructuralProposal] = []

        if self.config.enabled:
            # Config-authoritative mechanism gating:
            # Each proposal kind is emitted only when the corresponding
            # enable flag is True in the policy config. These flags are
            # populated from the YAML self_organization section via
            # from_config(). A disabled mechanism never produces proposals.
            if (
                self.config.neurogenesis_enabled
                and neuro > self.config.neurogenesis_threshold
                and signal.neuron_count < self.config.max_neurons
            ):
                proposals.append(
                    self._proposal(
                        signal.tick,
                        ProposalKind.NEUROGENESIS,
                        neuro,
                        f"low-rate ratio={low_rate_ratio:.3f}",
                    )
                )
            if (
                self.config.pruning_enabled
                and prune > self.config.pruning_threshold
                and signal.neuron_count > self.config.min_neurons
            ):
                proposals.append(
                    self._proposal(
                        signal.tick,
                        ProposalKind.PRUNING,
                        prune,
                        f"high-rate ratio={high_rate_ratio:.3f}",
                    )
                )
            if (
                self.config.synapse_sprouting_enabled
                and sprout > self.config.synapse_sprouting_threshold
            ):
                proposals.append(
                    self._proposal(
                        signal.tick,
                        ProposalKind.SYNAPSE_SPROUTING,
                        sprout,
                        f"mean-rate={signal.mean_rate_hz:.3f} Hz",
                    )
                )
            if (
                self.config.synapse_pruning_enabled
                and syn_prune > self.config.synapse_pruning_threshold
            ):
                proposals.append(
                    self._proposal(
                        signal.tick,
                        ProposalKind.SYNAPSE_PRUNING,
                        syn_prune,
                        f"low-energy ratio={low_energy_ratio:.3f}",
                    )
                )

        return PolicyReport(
            tick=signal.tick,
            proposals=tuple(proposals),
            neurogenesis_pressure=neuro,
            pruning_pressure=prune,
            synapse_sprouting_pressure=sprout,
            synapse_pruning_pressure=syn_prune,
        )

    @staticmethod
    def _proposal(
        tick: int, kind: ProposalKind, pressure: float, reason: str
    ) -> StructuralProposal:
        confidence = max(0.0, min(1.0, pressure))
        return StructuralProposal(
            proposal_id=f"{tick}:{kind.value}",
            kind=kind,
            reason=reason,
            confidence=confidence,
        )


# ============================================================================
# Config parsing helpers (mirrored from homeostasis/engine.py to avoid
# circular imports and keep policy.py self-contained)
# ============================================================================


def _string_mapping(value: object, name: str) -> dict[str, object]:
    """Convert a Mapping to a dict with string keys."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} config must be a mapping")

    mapping = cast(Mapping[object, object], value)
    result: dict[str, object] = {}
    for key, item in mapping.items():
        if not isinstance(key, str):
            raise TypeError(f"{name} config keys must be strings")
        result[key] = item
    return result


def _bool_value(value: object, name: str) -> bool:
    """Extract a boolean value from a configuration field."""
    if not isinstance(value, bool):
        raise TypeError(f"self_organization.{name} must be boolean")
    return value


def _float_value(value: object, name: str) -> float:
    """Extract a float value from a configuration field."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"self_organization.{name} must be numeric")
    return float(value)


def _int_value(value: object, name: str) -> int:
    """Extract an int value from a configuration field."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"self_organization.{name} must be numeric")
    return int(value)
