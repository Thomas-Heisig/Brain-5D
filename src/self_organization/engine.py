"""Conservative topology self-organization for Brain-5D.

The engine is optional and disabled by default. It uses the public manipulator
instead of mutating core dictionaries directly. STDP/reward learning stays in
``src.learning``; this engine only changes topology and performs slow structural
adaptation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.spatial_index import (
    Coord5D,
    iter_neighbour_coords,
    pack_coords,
    unpack_coords,
)
from src.manipulation.manipulator import Brain5DManipulator


@dataclass(frozen=True, slots=True)
class SelfOrganizationParameters:
    enabled: bool = False
    interval_ticks: int = 100
    pruning_enabled: bool = False
    pruning_weight_threshold: float = 0.005
    pruning_min_age_ticks: int = 1000
    sprouting_enabled: bool = False
    sprouting_max_out_degree: int = 12
    sprouting_radius: float = 2.0
    sprouting_weight: float = 0.05
    sprouting_delay: int = 1
    neurogenesis_enabled: bool = False
    neurogenesis_spike_delta_threshold: int = 50
    neurogenesis_radius: float = 1.0
    neurogenesis_max_per_cycle: int = 1
    max_neurons: int = 0  # 0 = unlimited

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> SelfOrganizationParameters:
        c = config.get("self_organization", {})
        params = cls(
            **{k: c[k] for k in cls.__dataclass_fields__ if k in c}
        )  # pylint: disable=no-member
        # Also support top-level max_neurons for backward compatibility
        if params.max_neurons == 0 and "max_neurons" in config:
            object.__setattr__(params, "max_neurons", int(config["max_neurons"]))
        return params

    def validate(self) -> None:
        if self.interval_ticks < 1:
            raise ValueError("self_organization.interval_ticks must be >= 1")
        if self.sprouting_max_out_degree < 0:
            raise ValueError("sprouting_max_out_degree must be >= 0")
        if self.sprouting_delay < 1:
            raise ValueError("sprouting_delay must be >= 1")
        if self.neurogenesis_max_per_cycle < 0:
            raise ValueError("neurogenesis_max_per_cycle must be >= 0")


@dataclass(frozen=True, slots=True)
class SelfOrganizationStats:
    cycles: int
    pruned_synapses: int
    created_synapses: int
    created_neurons: int


class SelfOrganizationEngine:
    """Slow structural adaptation layer attached through a post-step hook."""

    def __init__(
        self, network: Any, manipulator: Brain5DManipulator, config: dict[str, Any]
    ):
        self.network = network
        self.manipulator = manipulator
        self.params = SelfOrganizationParameters.from_config(config)
        self.params.validate()
        self._attached = False
        self._cycles = 0
        self._pruned = 0
        self._created_synapses = 0
        self._created_neurons = 0
        self._last_spike_counter: dict[int, int] = {}

    @property
    def stats(self) -> SelfOrganizationStats:
        return SelfOrganizationStats(
            self._cycles, self._pruned, self._created_synapses, self._created_neurons
        )

    def attach(self) -> None:
        if not self._attached:
            self.network.add_post_step_hook(self.update)
            self._attached = True

    def detach(self) -> None:
        if self._attached:
            self.network.remove_post_step_hook(self.update)
            self._attached = False

    def update(self, step_result: Any) -> None:
        if not self.params.enabled:
            return
        tick = int(step_result.tick)
        if (tick + 1) % self.params.interval_ticks != 0:
            return
        self.run_cycle(tick)

    def run_cycle(self, tick: int | None = None) -> SelfOrganizationStats:
        tick = int(self.network.current_tick if tick is None else tick)
        if self.params.pruning_enabled:
            self._run_pruning(tick)
        if self.params.sprouting_enabled:
            self._run_sprouting(tick)
        if self.params.neurogenesis_enabled:
            self._run_neurogenesis(tick)
        self._cycles += 1
        return self.stats

    def _run_pruning(self, tick: int) -> None:
        to_remove: list[tuple[int, int]] = []
        for source_id, synapses in tuple(self.network.synapses.items()):
            for syn in tuple(synapses):
                meta = self.manipulator.synapse_metadata.get((source_id, syn.target_id))
                created_tick = 0 if meta is None else int(meta.created_tick)
                age = tick - created_tick
                if (
                    age >= self.params.pruning_min_age_ticks
                    and abs(float(syn.weight)) < self.params.pruning_weight_threshold
                ):
                    to_remove.append((source_id, syn.target_id))
        for source_id, target_id in to_remove:
            self.manipulator.delete_synapse(source_id, target_id)
            self._pruned += 1

    def _run_sprouting(self, tick: int) -> None:
        for source_id in tuple(self.network.neurons):
            outgoing = self.network.synapses.get(source_id, ())
            if len(outgoing) >= self.params.sprouting_max_out_degree:
                continue
            connected = {s.target_id for s in outgoing}
            coord = unpack_coords(source_id)
            target_id = None
            for ncoord in iter_neighbour_coords(
                coord, self.network.dimensions, self.params.sprouting_radius
            ):
                candidate = pack_coords(*ncoord)
                if (
                    candidate == source_id
                    or candidate not in self.network.neurons
                    or candidate in connected
                ):
                    continue
                target_id = candidate
                break
            if target_id is None:
                continue
            self.manipulator.create_synapse(
                source_id,
                target_id,
                self.params.sprouting_weight,
                min(self.params.sprouting_delay, int(self.network.max_delay)),
            )
            self._created_synapses += 1

    def _run_neurogenesis(self, tick: int) -> None:
        if (
            self.params.max_neurons
            and len(self.network.neurons) >= self.params.max_neurons
        ):
            return
        created = 0
        ranked = sorted(
            self.network.neurons.items(),
            key=lambda item: int(item[1].spike_counter)
            - self._last_spike_counter.get(item[0], 0),
            reverse=True,
        )
        for parent_id, neuron in ranked:
            delta = int(neuron.spike_counter) - self._last_spike_counter.get(
                parent_id, 0
            )
            self._last_spike_counter[parent_id] = int(neuron.spike_counter)
            if delta < self.params.neurogenesis_spike_delta_threshold:
                continue
            free_coord = self._find_free_coord(parent_id)
            if free_coord is None:
                continue
            child_id = self.manipulator.create_neuron(free_coord)
            self.manipulator.set_neuron(
                child_id,
                a=neuron.a,
                b=neuron.b,
                c=neuron.c,
                d=neuron.d,
                v=neuron.c,
                u=neuron.b * neuron.c,
                energy=min(1.0, max(0.0, float(neuron.energy))),
            )
            self.manipulator.create_synapse(
                parent_id, child_id, self.params.sprouting_weight, 1
            )
            self._created_neurons += 1
            self._created_synapses += 1
            created += 1
            if created >= self.params.neurogenesis_max_per_cycle:
                break

    def _find_free_coord(self, neuron_id: int) -> Coord5D | None:
        coord = unpack_coords(neuron_id)
        for candidate in iter_neighbour_coords(
            coord, self.network.dimensions, self.params.neurogenesis_radius
        ):
            nid = pack_coords(*candidate)
            if nid not in self.network.neurons:
                return candidate
        return None
