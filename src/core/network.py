from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Set, Tuple

from .neuron import Neuron
from .spatial_index import DIM_NAMES, Coord5D, iter_neighbour_coords, pack_coords, unpack_coords
from .synapse import Synapse


@dataclass(slots=True)
class SpikeEvent:
    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


@dataclass(slots=True)
class StepResult:
    tick: int
    spike_ids: Tuple[int, ...]
    output_spike_ids: Tuple[int, ...]
    spikes_this_tick: int
    total_spikes: int
    delivered_events: int
    queued_events: int
    external_injection_count: int
    external_total_current: float
    synaptic_current_targets: int
    mean_v: float
    min_v: float
    max_v: float
    mean_energy: float
    core_step_ms: float


PostStepHook = Callable[[StepResult], None]


class NeuralNetwork:
    """Sparse 5D spiking network.

    Tick semantics:
    - step() processes exactly current_tick=t.
    - external currents already queued for t are read first.
    - events with delivery_tick=t are delivered in t.
    - spikes emitted in t schedule events for t+delay.
    - post-step hooks run after the core result is complete and after events
      for this tick have been queued.
    - current_tick becomes t+1 only after the whole core step is complete.
    """

    def __init__(self, config: dict, rng: random.Random):
        self.config = config
        self.rng = rng
        self.dimensions: Coord5D = tuple(config["dimensions"])  # type: ignore[assignment]
        self.max_delay = int(config["simulation"]["max_delay"])
        self.dt_ms = float(config["simulation"]["dt_ms"])
        if self.dt_ms != 1.0:
            raise ValueError("Sprint 1 reference core supports dt_ms=1.0 only")
        self.debug_invariants = bool(config["simulation"].get("debug_invariants", False))
        self.neurons: Dict[int, Neuron] = {}
        self.synapses: Dict[int, List[Synapse]] = {}
        self.in_degree: Dict[int, int] = {}
        self._synapse_count = 0
        self._queued_event_count = 0
        self.event_slots: List[List[SpikeEvent]] = [[] for _ in range(self.max_delay + 1)]
        self.current_tick = 0
        self.pending_currents: Dict[int, float] = {}
        self.total_spikes = 0
        self.total_events_processed = 0
        self.input_cells: Set[int] = set()
        self.output_cells: Set[int] = set()
        self._post_step_hooks: list[PostStepHook] = []
        topology = config.get("topology", {})
        self.allow_self_connections = bool(topology.get("allow_self_connections", False))
        self.allow_parallel_connections = bool(topology.get("allow_parallel_connections", False))

    def add_post_step_hook(self, hook: PostStepHook) -> None:
        """Register a generic observer that runs after each completed core tick."""
        if hook not in self._post_step_hooks:
            self._post_step_hooks.append(hook)

    def remove_post_step_hook(self, hook: PostStepHook) -> None:
        """Remove a previously registered post-step observer."""
        try:
            self._post_step_hooks.remove(hook)
        except ValueError:
            pass

    def add_neuron(self, coord: Coord5D) -> int:
        nid = pack_coords(*coord)
        if nid in self.neurons:
            raise KeyError(f"Neuron at {coord} already exists")
        ncfg = self.config["neuron"]
        self.neurons[nid] = Neuron(
            neuron_id=nid,
            a=float(ncfg["a"]), b=float(ncfg["b"]), c=float(ncfg["c"]), d=float(ncfg["d"]),
            v=float(ncfg["c"]), u=float(ncfg["b"]) * float(ncfg["c"]),
            energy=float(self.config["energy"]["initial"]),
            spike_cost=float(self.config["energy"]["spike_cost"]),
        )
        self.synapses[nid] = []
        self.in_degree[nid] = 0
        return nid

    def remove_neuron(self, neuron_id: int) -> None:
        if neuron_id not in self.neurons:
            return
        for pre_id, syn_list in list(self.synapses.items()):
            if pre_id == neuron_id:
                continue
            kept = []
            for syn in syn_list:
                if syn.target_id == neuron_id:
                    self._synapse_count -= 1
                    self.in_degree[neuron_id] = max(0, self.in_degree.get(neuron_id, 0) - 1)
                else:
                    kept.append(syn)
            self.synapses[pre_id] = kept
        outgoing = self.synapses.pop(neuron_id, [])
        for syn in outgoing:
            if syn.target_id in self.in_degree:
                self.in_degree[syn.target_id] = max(0, self.in_degree[syn.target_id] - 1)
            self._synapse_count -= 1
        del self.neurons[neuron_id]
        self.in_degree.pop(neuron_id, None)
        self.input_cells.discard(neuron_id)
        self.output_cells.discard(neuron_id)

    def connect(self, pre_id: int, post_id: int, weight: float, delay: int) -> None:
        if pre_id not in self.neurons or post_id not in self.neurons:
            raise ValueError("Neuron not present")
        if delay < 1 or delay > self.max_delay:
            raise ValueError(f"delay must be 1..{self.max_delay}")
        if pre_id == post_id and not self.allow_self_connections:
            raise ValueError("Self-connections are disabled")
        if not self.allow_parallel_connections and any(s.target_id == post_id for s in self.synapses[pre_id]):
            raise ValueError("Parallel connection already exists")
        self.synapses[pre_id].append(Synapse(post_id, float(weight), int(delay)))
        self._synapse_count += 1
        self.in_degree[post_id] += 1

    def disconnect(self, pre_id: int, post_id: int) -> None:
        if pre_id not in self.synapses:
            return
        old = len(self.synapses[pre_id])
        self.synapses[pre_id] = [s for s in self.synapses[pre_id] if s.target_id != post_id]
        removed = old - len(self.synapses[pre_id])
        self._synapse_count -= removed
        if post_id in self.in_degree:
            self.in_degree[post_id] = max(0, self.in_degree[post_id] - removed)

    def inject_current(self, neuron_id: int, current: float) -> None:
        if neuron_id in self.neurons:
            self.pending_currents[neuron_id] = self.pending_currents.get(neuron_id, 0.0) + float(current)

    def initialize_random_connections(self, connections_per_neuron: int, radius: float) -> None:
        wmin = float(self.config["network"].get("weight_min", 0.0))
        wmax = float(self.config["network"].get("weight_max", 0.5))
        for pre_id in list(self.neurons):
            pre_coord = unpack_coords(pre_id)
            candidates = []
            for ncoord in iter_neighbour_coords(pre_coord, self.dimensions, radius):
                nid = pack_coords(*ncoord)
                if nid not in self.neurons:
                    continue
                if nid == pre_id and not self.allow_self_connections:
                    continue
                candidates.append(nid)
            if not candidates:
                continue
            for post_id in self.rng.sample(candidates, min(connections_per_neuron, len(candidates))):
                self.connect(pre_id, post_id, self.rng.uniform(wmin, wmax), self.rng.randint(1, self.max_delay))

    def set_input_output_cells(self, input_dim: str, input_coord: int, output_dim: str, output_coord: int) -> None:
        self.input_cells.clear(); self.output_cells.clear()
        if input_dim not in DIM_NAMES or output_dim not in DIM_NAMES:
            raise ValueError("Unknown topology dimension")
        ii, oi = DIM_NAMES[input_dim], DIM_NAMES[output_dim]
        for nid in self.neurons:
            coord = unpack_coords(nid)
            if coord[ii] == input_coord:
                self.input_cells.add(nid)
            if coord[oi] == output_coord:
                self.output_cells.add(nid)

    def step(self) -> StepResult:
        start = time.perf_counter()
        tick = self.current_tick
        slot_index = tick % len(self.event_slots)
        external_currents = self.pending_currents.copy()
        self.pending_currents.clear()
        synaptic_currents: Dict[int, float] = {}
        events = self.event_slots[slot_index]
        for ev in events:
            if ev.delivery_tick != tick:
                raise RuntimeError(f"Queue invariant violated: tick={tick}, delivery={ev.delivery_tick}")
            if ev.target_id in self.neurons:
                synaptic_currents[ev.target_id] = synaptic_currents.get(ev.target_id, 0.0) + ev.weight
            self.total_events_processed += 1
        delivered = len(events)
        self.event_slots[slot_index] = []
        self._queued_event_count -= delivered
        if self._queued_event_count < 0:
            raise RuntimeError("queued_event_count became negative")
        spike_ids: list[int] = []
        output_spikes: list[int] = []
        active = len(self.neurons)
        sum_v = sum_energy = 0.0
        min_v = float("inf"); max_v = -float("inf")
        for nid, neuron in self.neurons.items():
            ext = external_currents.get(nid, 0.0)
            syn = synaptic_currents.get(nid, 0.0)
            neuron.last_external_current = ext
            neuron.last_synaptic_current = syn
            spiked = neuron.step(ext + syn, tick)
            sum_v += neuron.v; sum_energy += neuron.energy
            min_v = min(min_v, neuron.v); max_v = max(max_v, neuron.v)
            if spiked:
                spike_ids.append(nid); self.total_spikes += 1
                if nid in self.output_cells:
                    output_spikes.append(nid)
                for connection in self.synapses[nid]:
                    connection.last_pre_spike = tick
                    delivery_tick = tick + connection.delay
                    slot = delivery_tick % len(self.event_slots)
                    self.event_slots[slot].append(SpikeEvent(nid, connection.target_id, connection.weight, delivery_tick))
                    self._queued_event_count += 1
        if active:
            mean_v = sum_v / active; mean_energy = sum_energy / active
        else:
            mean_v = min_v = max_v = mean_energy = 0.0

        self.current_tick = tick + 1
        if self.debug_invariants:
            actual = sum(len(s) for s in self.event_slots)
            if actual != self._queued_event_count:
                raise RuntimeError(f"Queue accounting mismatch: counter={self._queued_event_count}, actual={actual}")
        elapsed = (time.perf_counter() - start) * 1000.0
        result = StepResult(
            tick=tick,
            spike_ids=tuple(spike_ids), output_spike_ids=tuple(output_spikes),
            spikes_this_tick=len(spike_ids), total_spikes=self.total_spikes,
            delivered_events=delivered, queued_events=self._queued_event_count,
            external_injection_count=len(external_currents), external_total_current=sum(external_currents.values()),
            synaptic_current_targets=len(synaptic_currents), mean_v=mean_v, min_v=min_v, max_v=max_v,
            mean_energy=mean_energy, core_step_ms=elapsed,
        )
        for hook in tuple(self._post_step_hooks):
            hook(result)
        return result

    @property
    def synapse_count(self) -> int:
        return self._synapse_count

    @property
    def queued_event_count(self) -> int:
        return self._queued_event_count
