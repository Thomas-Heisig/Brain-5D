"""Deterministic morphology ages, structural costs, and bounded budgets."""

from __future__ import annotations

from dataclasses import dataclass, field, replace


def _empty_neuron_births() -> dict[int, int]:
    return {}


def _empty_synapse_births() -> dict[tuple[int, int], int]:
    return {}


@dataclass(frozen=True, slots=True)
class StructuralCostModel:
    """Cost units for structural changes."""

    neuron_growth: float = 1.0
    synapse_growth: float = 0.25
    neuron_pruning: float = 1.0
    synapse_pruning: float = 0.25


@dataclass(frozen=True, slots=True)
class MorphologyBudget:
    """Independent bounded budgets for growth and pruning in one window."""

    growth: float
    pruning: float

    def __post_init__(self) -> None:
        if self.growth < 0.0 or self.pruning < 0.0:
            raise ValueError("morphology budgets must not be negative")


@dataclass(frozen=True, slots=True)
class MorphologyLedger:
    """Track structural birth ticks and deterministic budget consumption."""

    costs: StructuralCostModel = field(default_factory=StructuralCostModel)
    budget: MorphologyBudget = field(default_factory=lambda: MorphologyBudget(0.0, 0.0))
    neuron_birth_ticks: dict[int, int] = field(default_factory=_empty_neuron_births)
    synapse_birth_ticks: dict[tuple[int, int], int] = field(
        default_factory=_empty_synapse_births
    )
    growth_spent: float = 0.0
    pruning_spent: float = 0.0

    def neuron_age(self, neuron_id: int, tick: int) -> int | None:
        return _age(self.neuron_birth_ticks.get(neuron_id), tick)

    def synapse_age(self, source_id: int, target_id: int, tick: int) -> int | None:
        return _age(self.synapse_birth_ticks.get((source_id, target_id)), tick)

    def can_afford_growth(self, *, neurons: int = 0, synapses: int = 0) -> bool:
        return self.growth_spent + self._growth_cost(neurons, synapses) <= self.budget.growth

    def can_afford_pruning(self, *, neurons: int = 0, synapses: int = 0) -> bool:
        return self.pruning_spent + self._pruning_cost(neurons, synapses) <= self.budget.pruning

    def consume_growth(self, *, neurons: int = 0, synapses: int = 0) -> "MorphologyLedger":
        cost = self._growth_cost(neurons, synapses)
        if not self.can_afford_growth(neurons=neurons, synapses=synapses):
            raise ValueError("growth budget exceeded")
        return replace(self, growth_spent=self.growth_spent + cost)

    def consume_pruning(self, *, neurons: int = 0, synapses: int = 0) -> "MorphologyLedger":
        cost = self._pruning_cost(neurons, synapses)
        if not self.can_afford_pruning(neurons=neurons, synapses=synapses):
            raise ValueError("pruning budget exceeded")
        return replace(self, pruning_spent=self.pruning_spent + cost)

    def register_neuron(self, neuron_id: int, birth_tick: int) -> "MorphologyLedger":
        births = dict(self.neuron_birth_ticks)
        births.setdefault(neuron_id, birth_tick)
        return replace(self, neuron_birth_ticks=births)

    def register_synapse(self, source_id: int, target_id: int, birth_tick: int) -> "MorphologyLedger":
        births = dict(self.synapse_birth_ticks)
        births.setdefault((source_id, target_id), birth_tick)
        return replace(self, synapse_birth_ticks=births)

    def _growth_cost(self, neurons: int, synapses: int) -> float:
        return neurons * self.costs.neuron_growth + synapses * self.costs.synapse_growth

    def _pruning_cost(self, neurons: int, synapses: int) -> float:
        return neurons * self.costs.neuron_pruning + synapses * self.costs.synapse_pruning

def _age(birth_tick: int | None, tick: int) -> int | None:
    if birth_tick is None:
        return None
    if tick < birth_tick:
        raise ValueError("tick cannot precede birth tick")
    return tick - birth_tick
