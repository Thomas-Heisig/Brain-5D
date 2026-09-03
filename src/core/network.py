"""Sparse 5D spiking neural network for Brain-5D.

This module defines the NeuralNetwork class, which manages:
- Neurons in a 5D spatial grid
- Synaptic connections with STDP plasticity
- Spike propagation with configurable delays
- Event queues for temporal processing
- Input/output layer management
- Post-step hooks for observers

The network follows a tick-based simulation model where:
- Each step() processes exactly one tick (1ms)
- External currents are applied before synaptic currents
- Spike events are queued with delays
- Post-step hooks run after each tick
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .neuron import Neuron, NeuronConfig, NeuronType, create_neuron
from .spatial_index import (
    DIM_NAMES,
    Coord5D,
    Dim5D,
    iter_neighbour_coords,
    pack_coords,
    unpack_coords,
    validate_coord_in_dims,
    validate_dims,
)
from .synapse import Synapse, SynapseConfig, create_synapse

# ============================================================================
# Type Aliases
# ============================================================================

PostStepHook = Callable[["StepResult"], None]
"""Callback function type for post-step hooks."""

ConfigDict = dict[str, object]
"""Type alias for a configuration dictionary passed to NeuralNetwork.__init__."""


# ============================================================================
# Configuration Classes
# ============================================================================


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Configuration for simulation parameters."""

    dt_ms: float = 1.0
    max_delay: int = 5
    debug_invariants: bool = False

    def __post_init__(self) -> None:
        if self.dt_ms != 1.0:
            raise ValueError("dt_ms must be 1.0 for the reference core")
        if self.max_delay < 1:
            raise ValueError("max_delay must be >= 1")


@dataclass(frozen=True, slots=True)
class TopologyConfig:
    """Configuration for network topology."""

    allow_self_connections: bool = False
    allow_parallel_connections: bool = False


@dataclass(frozen=True, slots=True)
class NetworkConfig:
    """Configuration for network parameters."""

    weight_min: float = 0.0
    weight_max: float = 0.5
    initial_connections_per_neuron: int = 10
    neighbour_radius: float = 5.0


@dataclass(frozen=True, slots=True)
class Brain5DConfig:
    """Complete configuration for Brain-5D network."""

    dimensions: Dim5D
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    topology: TopologyConfig = field(default_factory=TopologyConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    neuron: NeuronConfig = field(default_factory=NeuronConfig)
    synapse: SynapseConfig = field(default_factory=SynapseConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Brain5DConfig:
        """Create config from dictionary (backward compatibility)."""
        dims = data.get("dimensions")
        if not dims or len(dims) != 5:
            raise ValueError("dimensions must be a tuple/list of 5 ints")

        sim = data.get("simulation", {})
        topo = data.get("topology", {})
        net = data.get("network", {})

        return cls(
            dimensions=tuple(dims),
            simulation=SimulationConfig(
                dt_ms=float(sim.get("dt_ms", 1.0)),
                max_delay=int(sim.get("max_delay", 5)),
                debug_invariants=bool(sim.get("debug_invariants", False)),
            ),
            topology=TopologyConfig(
                allow_self_connections=bool(topo.get("allow_self_connections", False)),
                allow_parallel_connections=bool(
                    topo.get("allow_parallel_connections", False)
                ),
            ),
            network=NetworkConfig(
                weight_min=float(net.get("weight_min", 0.0)),
                weight_max=float(net.get("weight_max", 0.5)),
                initial_connections_per_neuron=int(
                    net.get("initial_connections_per_neuron", 10)
                ),
                neighbour_radius=float(net.get("neighbour_radius", 5.0)),
            ),
            neuron=NeuronConfig(
                a=float(data.get("neuron", {}).get("a", 0.02)),
                b=float(data.get("neuron", {}).get("b", 0.2)),
                c=float(data.get("neuron", {}).get("c", -65.0)),
                d=float(data.get("neuron", {}).get("d", 8.0)),
                spike_cost=float(data.get("energy", {}).get("spike_cost", 0.001)),
                resting_energy=float(data.get("energy", {}).get("initial", 1.0)),
            ),
            synapse=SynapseConfig(
                a_plus=float(data.get("stdp", {}).get("a_plus", 0.1)),
                a_minus=float(data.get("stdp", {}).get("a_minus", 0.12)),
                tau_plus=float(data.get("stdp", {}).get("tau_plus", 20.0)),
                tau_minus=float(data.get("stdp", {}).get("tau_minus", 20.0)),
                w_min=float(net.get("weight_min", 0.0)),
                w_max=float(net.get("weight_max", 0.5)),
                enable_triplet=bool(data.get("stdp", {}).get("enable_triplet", False)),
                enable_metaplasticity=bool(
                    data.get("stdp", {}).get("enable_metaplasticity", False)
                ),
            ),
        )


# ============================================================================
# Event Classes
# ============================================================================


@dataclass(slots=True)
class SpikeEvent:
    """A queued spike event for future delivery.

    Attributes:
        source_id: ID of the neuron that fired the spike.
        target_id: ID of the target neuron.
        weight: Synaptic weight for this event.
        delivery_tick: Tick at which this event should be delivered.
    """

    source_id: int
    target_id: int
    weight: float
    delivery_tick: int


@dataclass(slots=True)
class StepResult:
    """Result of a single network step.

    Attributes:
        tick: The tick number that was processed.
        spike_ids: IDs of neurons that spiked this tick.
        output_spike_ids: IDs of output neurons that spiked.
        spikes_this_tick: Number of spikes in this tick.
        total_spikes: Total spikes since network creation.
        delivered_events: Number of events delivered this tick.
        queued_events: Number of events currently queued.
        external_injection_count: Number of neurons with external current.
        external_total_current: Sum of all external currents.
        synaptic_current_targets: Number of neurons receiving synaptic current.
        mean_v: Mean membrane potential across all neurons.
        min_v: Minimum membrane potential.
        max_v: Maximum membrane potential.
        mean_energy: Mean energy across all neurons.
        core_step_ms: Time taken for the step in milliseconds.
        neuron_activity: Dictionary mapping neuron_id to spike flag.
        total_synapses: Total synapses in the network.
    """

    tick: int = 0
    spike_ids: tuple[int, ...] = ()
    output_spike_ids: tuple[int, ...] = ()
    spikes_this_tick: int = 0
    total_spikes: int = 0
    delivered_events: int = 0
    queued_events: int = 0
    external_injection_count: int = 0
    external_total_current: float = 0.0
    synaptic_current_targets: int = 0
    mean_v: float = 0.0
    min_v: float = 0.0
    max_v: float = 0.0
    mean_energy: float = 0.0
    core_step_ms: float = 0.0
    neuron_activity: dict[int, bool] = field(default_factory=dict[int, bool])
    total_synapses: int = 0
    dirty_neuron_ids: tuple[int, ...] = ()
    dirty_synapse_ids: tuple[tuple[int, int], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tick": self.tick,
            "spike_ids": list(self.spike_ids),
            "output_spike_ids": list(self.output_spike_ids),
            "spikes_this_tick": self.spikes_this_tick,
            "total_spikes": self.total_spikes,
            "delivered_events": self.delivered_events,
            "queued_events": self.queued_events,
            "external_injection_count": self.external_injection_count,
            "external_total_current": self.external_total_current,
            "synaptic_current_targets": self.synaptic_current_targets,
            "mean_v": self.mean_v,
            "min_v": self.min_v,
            "max_v": self.max_v,
            "mean_energy": self.mean_energy,
            "core_step_ms": self.core_step_ms,
            "total_synapses": self.total_synapses,
            "dirty_neuron_ids": list(self.dirty_neuron_ids),
            "dirty_synapse_ids": [list(value) for value in self.dirty_synapse_ids],
        }


# ============================================================================
# NeuralNetwork Class
# ============================================================================


class NeuralNetwork:
    """Sparse 5D spiking neural network.

    The network manages neurons, synapses, and spike propagation with
    configurable delays. It follows a tick-based simulation model:

    Tick semantics:
    1. External currents queued for the current tick are applied.
    2. Spike events with delivery_tick == current_tick are delivered.
    3. Neurons are updated with combined external + synaptic currents.
    4. Spikes generated in this tick are queued for future ticks.
    5. Post-step hooks run after the core step is complete.
    6. current_tick increments by 1 after the step.

    The network uses a 5D spatial grid for neuron placement, with
    distance-based connectivity and boundary layers for input/output.

    Example:
        >>> config = Brain5DConfig(dimensions=(10,10,10,10,10))
        >>> network = NeuralNetwork(config, rng)
        >>> network.add_neuron((1,2,3,4,5))
        >>> network.initialize_random_connections(10, 2.0)
        >>> result = network.step()
    """

    def __init__(
        self,
        config: Brain5DConfig | dict[str, Any] | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """Initialize the neural network.

        Args:
            config: Network configuration. Can be a Brain5DConfig instance
                or a dict for backward compatibility.
            rng: Random number generator. Created with default seed if not provided.

        Raises:
            ValueError: If dimensions are invalid or configuration is malformed.
        """
        # Parse configuration
        if config is None:
            config = Brain5DConfig(dimensions=(50, 50, 50, 50, 50))
        elif isinstance(config, dict):
            config = Brain5DConfig.from_dict(config)

        self.config = config
        self.dimensions: Dim5D = config.dimensions
        self.sim_config = config.simulation
        self.topology_config = config.topology
        self.network_config = config.network
        self.neuron_config = config.neuron
        self.synapse_config = config.synapse

        # Validate dimensions
        validate_dims(self.dimensions)

        # Random number generator
        self.rng = rng or random.Random()

        # Core data structures
        self.neurons: dict[int, Neuron] = {}
        self.synapses: dict[int, list[Synapse]] = {}
        self.in_degree: dict[int, int] = {}

        # Event queue (circular buffer)
        self.max_delay = self.sim_config.max_delay
        self.event_slots: list[list[SpikeEvent]] = [
            [] for _ in range(self.max_delay + 1)
        ]
        self._queued_event_count = 0
        self._synapse_count = 0

        # State
        self.current_tick = 0
        self.total_spikes = 0
        self.total_events_processed = 0
        self.pending_currents: dict[int, float] = {}

        # Input/output cells
        self.input_cells: set[int] = set()
        self.output_cells: set[int] = set()

        # Post-step hooks
        self._post_step_hooks: list[PostStepHook] = []

        # Performance tracking
        self._step_count = 0
        self._dirty_neuron_ids: set[int] = set()
        self._dirty_synapse_ids: set[tuple[int, int]] = set()

    # ========================================================================
    # Configuration Access
    # ========================================================================

    @property
    def debug_invariants(self) -> bool:
        """Check if debug invariants are enabled."""
        return self.sim_config.debug_invariants

    @property
    def allow_self_connections(self) -> bool:
        """Check if self-connections are allowed."""
        return self.topology_config.allow_self_connections

    @property
    def allow_parallel_connections(self) -> bool:
        """Check if parallel connections are allowed."""
        return self.topology_config.allow_parallel_connections

    # ========================================================================
    # Neuron Management
    # ========================================================================

    def add_neuron(
        self,
        coord: Coord5D,
        neuron_type: NeuronType = NeuronType.REGULAR_SPIKING,
        **kwargs: Any,
    ) -> int:
        """Add a neuron at the specified 5D coordinate.

        Args:
            coord: 5D coordinate for the neuron.
            neuron_type: Type of neuron (affects default parameters).
            **kwargs: Additional parameters passed to create_neuron.

        Returns:
            The unique neuron ID (packed coordinate).

        Raises:
            ValueError: If the coordinate is outside dimensions.
            KeyError: If a neuron already exists at this coordinate.
        """
        validate_coord_in_dims(coord, self.dimensions)

        nid = pack_coords(*coord)
        if nid in self.neurons:
            raise KeyError(f"Neuron at {coord} already exists (ID: {nid})")

        # Create neuron with config
        neuron = create_neuron(
            neuron_id=nid,
            neuron_type=neuron_type,
            config=self.neuron_config,
            **kwargs,
        )

        self.neurons[nid] = neuron

        def mark_neuron_dirty(neuron_id: int = nid) -> None:
            self._dirty_neuron_ids.add(neuron_id)

        neuron.set_dirty_callback(mark_neuron_dirty)
        self.synapses[nid] = []
        self.in_degree[nid] = 0
        self._dirty_neuron_ids.add(nid)

        return nid

    def remove_neuron(self, neuron_id: int) -> bool:
        """Remove a neuron and all its connections.

        Args:
            neuron_id: ID of the neuron to remove.

        Returns:
            True if the neuron was removed, False if it didn't exist.
        """
        if neuron_id not in self.neurons:
            return False

        # Remove incoming synapses from other neurons to this neuron
        for pre_id, syn_list in list(self.synapses.items()):
            if pre_id == neuron_id:
                continue
            kept: list[Synapse] = []
            for syn in syn_list:
                if syn.target_id == neuron_id:
                    self._synapse_count -= 1
                    self.in_degree[neuron_id] = max(
                        0, self.in_degree.get(neuron_id, 0) - 1
                    )
                else:
                    kept.append(syn)
            self.synapses[pre_id] = kept

        # Remove outgoing synapses from this neuron
        outgoing = self.synapses.pop(neuron_id, [])
        for syn in outgoing:
            if syn.target_id in self.in_degree:
                self.in_degree[syn.target_id] = max(
                    0, self.in_degree[syn.target_id] - 1
                )
            self._synapse_count -= 1

        # Remove the neuron
        del self.neurons[neuron_id]
        self.in_degree.pop(neuron_id, None)
        self.input_cells.discard(neuron_id)
        self.output_cells.discard(neuron_id)
        self._dirty_neuron_ids.add(neuron_id)

        return True

    def get_neuron(self, neuron_id: int) -> Neuron | None:
        """Get a neuron by ID.

        Args:
            neuron_id: ID of the neuron.

        Returns:
            The Neuron instance, or None if not found.
        """
        return self.neurons.get(neuron_id)

    def get_neuron_at_coord(self, coord: Coord5D) -> Neuron | None:
        """Get a neuron at a specific coordinate.

        Args:
            coord: 5D coordinate.

        Returns:
            The Neuron instance, or None if not found.
        """
        nid = pack_coords(*coord)
        return self.neurons.get(nid)

    def has_neuron(self, neuron_id: int) -> bool:
        """Check if a neuron exists.

        Args:
            neuron_id: ID of the neuron.

        Returns:
            True if the neuron exists.
        """
        return neuron_id in self.neurons

    @property
    def neuron_count(self) -> int:
        """Number of neurons in the network."""
        return len(self.neurons)

    def neuron_ids(self) -> set[int]:
        """Get all neuron IDs."""
        return set(self.neurons.keys())

    # ========================================================================
    # Synapse Management
    # ========================================================================

    def connect(
        self,
        pre_id: int,
        post_id: int,
        weight: float,
        delay: int,
        config: SynapseConfig | None = None,
    ) -> bool:
        """Create a synaptic connection between two neurons.

        Args:
            pre_id: ID of the presynaptic neuron.
            post_id: ID of the postsynaptic neuron.
            weight: Synaptic weight (connection strength).
            delay: Transmission delay in ticks (1 - max_delay).
            config: Optional custom synapse configuration.

        Returns:
            True if the connection was created, False otherwise.

        Raises:
            ValueError: If neurons don't exist, delay is invalid,
                or connection rules are violated.
        """
        if pre_id not in self.neurons:
            raise ValueError(f"Presynaptic neuron {pre_id} not found")
        if post_id not in self.neurons:
            raise ValueError(f"Postsynaptic neuron {post_id} not found")
        if delay < 1 or delay > self.max_delay:
            raise ValueError(f"Delay must be 1..{self.max_delay}")
        if pre_id == post_id and not self.topology_config.allow_self_connections:
            raise ValueError("Self-connections are disabled")
        if not self.topology_config.allow_parallel_connections:
            if any(s.target_id == post_id for s in self.synapses[pre_id]):
                raise ValueError("Parallel connection already exists")

        # Create synapse
        synapse = create_synapse(post_id, weight, delay, config or self.synapse_config)
        self.synapses[pre_id].append(synapse)

        def mark_synapse_dirty(
            source_id: int = pre_id,
            target_id: int = post_id,
        ) -> None:
            self._dirty_synapse_ids.add((source_id, target_id))

        synapse.set_dirty_callback(mark_synapse_dirty)
        self._synapse_count += 1
        self.in_degree[post_id] = self.in_degree.get(post_id, 0) + 1
        self._dirty_synapse_ids.add((pre_id, post_id))

        return True

    def disconnect(self, pre_id: int, post_id: int) -> bool:
        """Remove a synaptic connection.

        Args:
            pre_id: ID of the presynaptic neuron.
            post_id: ID of the postsynaptic neuron.

        Returns:
            True if the connection was removed, False if it didn't exist.
        """
        if pre_id not in self.synapses:
            return False

        old_len = len(self.synapses[pre_id])
        self.synapses[pre_id] = [
            s for s in self.synapses[pre_id] if s.target_id != post_id
        ]
        removed = old_len - len(self.synapses[pre_id])

        if removed > 0:
            self._synapse_count -= removed
            if post_id in self.in_degree:
                self.in_degree[post_id] = max(0, self.in_degree[post_id] - removed)
            self._dirty_synapse_ids.add((pre_id, post_id))
            return True

        return False

    def get_synapses(self, pre_id: int) -> list[Synapse]:
        """Get all synapses from a neuron.

        Args:
            pre_id: ID of the presynaptic neuron.

        Returns:
            List of Synapse objects.
        """
        return self.synapses.get(pre_id, [])

    def get_incoming_synapses(self, post_id: int) -> list[tuple[int, Synapse]]:
        """Get all synapses targeting a neuron.

        Args:
            post_id: ID of the postsynaptic neuron.

        Returns:
            List of (presynaptic_neuron_id, Synapse) tuples.
        """
        incoming: list[tuple[int, Synapse]] = []
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                if syn.target_id == post_id:
                    incoming.append((pre_id, syn))
        return incoming

    @property
    def synapse_count(self) -> int:
        """Number of synapses in the network."""
        return self._synapse_count

    @property
    def queued_event_count(self) -> int:
        """Number of events currently queued in the event buffer."""
        return self._queued_event_count

    # ========================================================================
    # Connection Initialization
    # ========================================================================

    def initialize_random_connections(
        self,
        connections_per_neuron: int | None = None,
        radius: float | None = None,
        weight_range: tuple[float, float] | None = None,
    ) -> None:
        """Initialize random connections between neurons within a radius.

        Args:
            connections_per_neuron: Target connections per neuron.
                If None, uses config value.
            radius: Neighbour radius in 5D space.
                If None, uses config value.
            weight_range: (min, max) weight range.
                If None, uses config values.
        """
        if connections_per_neuron is None:
            connections_per_neuron = self.network_config.initial_connections_per_neuron
        if radius is None:
            radius = self.network_config.neighbour_radius
        if weight_range is None:
            weight_range = (
                self.network_config.weight_min,
                self.network_config.weight_max,
            )

        wmin, wmax = weight_range

        for pre_id in list(self.neurons.keys()):
            pre_coord = unpack_coords(pre_id)

            # Collect candidate neurons within radius
            candidates: list[int] = []
            for ncoord in iter_neighbour_coords(pre_coord, self.dimensions, radius):
                nid = pack_coords(*ncoord)
                if nid not in self.neurons:
                    continue
                if nid == pre_id and not self.topology_config.allow_self_connections:
                    continue
                candidates.append(nid)

            if not candidates:
                continue

            # Select random targets
            sample_size = min(connections_per_neuron, len(candidates))
            for post_id in self.rng.sample(candidates, sample_size):
                weight = self.rng.uniform(wmin, wmax)
                delay = self.rng.randint(1, self.max_delay)
                try:
                    self.connect(pre_id, post_id, weight, delay)
                except ValueError:
                    continue  # Skip invalid connections

    def connect_neighbours(
        self,
        radius: float,
        weight_range: tuple[float, float] = (0.0, 0.5),
        probability: float = 0.1,
    ) -> None:
        """Connect neurons probabilistically within a radius.

        Args:
            radius: Neighbour radius in 5D space.
            weight_range: (min, max) weight range.
            probability: Connection probability between neighbours.
        """
        wmin, wmax = weight_range

        for pre_id in list(self.neurons.keys()):
            pre_coord = unpack_coords(pre_id)

            for ncoord in iter_neighbour_coords(pre_coord, self.dimensions, radius):
                post_id = pack_coords(*ncoord)
                if post_id not in self.neurons:
                    continue
                if (
                    post_id == pre_id
                    and not self.topology_config.allow_self_connections
                ):
                    continue

                if self.rng.random() < probability:
                    weight = self.rng.uniform(wmin, wmax)
                    delay = self.rng.randint(1, self.max_delay)
                    try:
                        self.connect(pre_id, post_id, weight, delay)
                    except ValueError:
                        continue

    # ========================================================================
    # Current Injection
    # ========================================================================

    def inject_current(self, neuron_id: int, current: float) -> None:
        """Inject an external current into a neuron.

        Args:
            neuron_id: ID of the target neuron.
            current: Current value to inject (can be positive or negative).
        """
        if neuron_id in self.neurons:
            self.pending_currents[neuron_id] = (
                self.pending_currents.get(neuron_id, 0.0) + current
            )

    def inject_current_batch(self, currents: dict[int, float]) -> None:
        """Inject currents into multiple neurons.

        Args:
            currents: Dictionary mapping neuron_id -> current value.
        """
        for nid, current in currents.items():
            self.inject_current(nid, current)

    def clear_pending_currents(self) -> None:
        """Clear all pending currents."""
        self.pending_currents.clear()

    # ========================================================================
    # Input/Output Layer Management
    # ========================================================================

    def set_input_output_cells(
        self,
        input_dim: str,
        input_coord: int,
        output_dim: str,
        output_coord: int,
    ) -> None:
        """Set input and output cells based on dimension boundaries.

        Args:
            input_dim: Name of the input dimension ('x', 'y', 'z', 'd4', 'd5').
            input_coord: Coordinate value on the input dimension.
            output_dim: Name of the output dimension.
            output_coord: Coordinate value on the output dimension.

        Raises:
            ValueError: If dimension names are unknown.
        """
        if input_dim not in DIM_NAMES:
            raise ValueError(f"Unknown dimension: {input_dim}")
        if output_dim not in DIM_NAMES:
            raise ValueError(f"Unknown dimension: {output_dim}")

        self.input_cells.clear()
        self.output_cells.clear()

        input_idx = DIM_NAMES[input_dim]
        output_idx = DIM_NAMES[output_dim]

        for nid in self.neurons:
            coord = unpack_coords(nid)
            if coord[input_idx] == input_coord:
                self.input_cells.add(nid)
            if coord[output_idx] == output_coord:
                self.output_cells.add(nid)

    def is_input_cell(self, neuron_id: int) -> bool:
        """Check if a neuron is an input cell."""
        return neuron_id in self.input_cells

    def is_output_cell(self, neuron_id: int) -> bool:
        """Check if a neuron is an output cell."""
        return neuron_id in self.output_cells

    # ========================================================================
    # Simulation Step
    # ========================================================================

    def step(self) -> StepResult:
        """Execute one simulation tick.

        Returns:
            StepResult containing the results of this tick.

        Raises:
            RuntimeError: If queue invariants are violated (with debug mode).
        """
        start = time.perf_counter()
        tick = self.current_tick
        slot_index = tick % len(self.event_slots)

        # 1. Apply external currents
        external_currents = self.pending_currents.copy()
        self.pending_currents.clear()

        # 2. Deliver queued spike events in deterministic order
        synaptic_currents: dict[int, float] = {}
        events = sorted(
            self.event_slots[slot_index],
            key=lambda e: (e.delivery_tick, e.source_id, e.target_id),
        )

        for ev in events:
            if self.debug_invariants and ev.delivery_tick != tick:
                raise RuntimeError(
                    f"Queue invariant violated: tick={tick}, delivery={ev.delivery_tick}"
                )
            if ev.target_id in self.neurons:
                synaptic_currents[ev.target_id] = (
                    synaptic_currents.get(ev.target_id, 0.0) + ev.weight
                )
            self.total_events_processed += 1

        delivered = len(events)
        self.event_slots[slot_index] = []
        self._queued_event_count -= delivered

        if self.debug_invariants and self._queued_event_count < 0:
            raise RuntimeError("queued_event_count became negative")

        # 3. Update neurons
        spike_ids: list[int] = []
        output_spikes: list[int] = []
        neuron_activity: dict[int, bool] = {}

        active = len(self.neurons)
        sum_v = 0.0
        sum_energy = 0.0
        min_v = float("inf")
        max_v = -float("inf")

        # Explicit deterministic iteration: sort by neuron_id
        # This ensures identical tick execution regardless of dict insertion order.
        for nid, neuron in sorted(self.neurons.items()):
            ext = external_currents.get(nid, 0.0)
            syn = synaptic_currents.get(nid, 0.0)
            neuron.last_external_current = ext
            neuron.last_synaptic_current = syn

            spiked = neuron.step(ext + syn, tick)
            neuron_activity[nid] = spiked

            sum_v += neuron.v
            sum_energy += neuron.energy
            min_v = min(min_v, neuron.v)
            max_v = max(max_v, neuron.v)

            if spiked:
                spike_ids.append(nid)
                self.total_spikes += 1

                if nid in self.output_cells:
                    output_spikes.append(nid)

                # Queue outgoing spikes in deterministic order (by target_id)
                for connection in sorted(
                    self.synapses.get(nid, []),
                    key=lambda s: s.target_id,
                ):
                    connection.last_pre_spike = tick
                    connection.mark_dirty()
                    delivery_tick = tick + connection.delay
                    slot = delivery_tick % len(self.event_slots)
                    self.event_slots[slot].append(
                        SpikeEvent(
                            nid,
                            connection.target_id,
                            connection.weight,
                            delivery_tick,
                        )
                    )
                    self._queued_event_count += 1

        # 4. Compute statistics
        if active:
            mean_v = sum_v / active
            mean_energy = sum_energy / active
        else:
            mean_v = min_v = max_v = mean_energy = 0.0

        # 5. Advance tick
        self.current_tick = tick + 1
        self._step_count += 1

        # 6. Debug invariants
        if self.debug_invariants:
            actual = sum(len(s) for s in self.event_slots)
            if actual != self._queued_event_count:
                raise RuntimeError(
                    f"Queue accounting mismatch: counter={self._queued_event_count}, actual={actual}"
                )

        elapsed = (time.perf_counter() - start) * 1000.0

        # 7. Build result
        result = StepResult(
            tick=tick,
            spike_ids=tuple(spike_ids),
            output_spike_ids=tuple(output_spikes),
            spikes_this_tick=len(spike_ids),
            total_spikes=self.total_spikes,
            delivered_events=delivered,
            queued_events=self._queued_event_count,
            external_injection_count=len(external_currents),
            external_total_current=sum(external_currents.values()),
            synaptic_current_targets=len(synaptic_currents),
            mean_v=mean_v,
            min_v=min_v,
            max_v=max_v,
            mean_energy=mean_energy,
            core_step_ms=elapsed,
            neuron_activity=neuron_activity,
            total_synapses=self._synapse_count,
            dirty_neuron_ids=tuple(sorted(self._dirty_neuron_ids)),
            dirty_synapse_ids=tuple(sorted(self._dirty_synapse_ids)),
        )

        # 8. Run post-step hooks
        for hook in tuple(self._post_step_hooks):
            try:
                hook(result)
            except Exception:
                pass  # Hook errors are logged elsewhere

        return result

    # ========================================================================
    # Post-Step Hooks
    # ========================================================================

    def add_post_step_hook(self, hook: PostStepHook) -> None:
        """Register a hook that runs after each tick.

        Args:
            hook: Callback function receiving the StepResult.
        """
        if hook not in self._post_step_hooks:
            self._post_step_hooks.append(hook)

    def remove_post_step_hook(self, hook: PostStepHook) -> None:
        """Remove a previously registered hook."""
        try:
            self._post_step_hooks.remove(hook)
        except ValueError:
            pass

    def clear_post_step_hooks(self) -> None:
        """Remove all post-step hooks."""
        self._post_step_hooks.clear()

    # ========================================================================
    # State Inspection
    # ========================================================================

    def get_state_summary(self) -> dict[str, Any]:
        """Get a summary of the network state.

        Returns:
            Dictionary with network statistics.
        """
        return {
            "tick": self.current_tick,
            "neurons": len(self.neurons),
            "synapses": self._synapse_count,
            "input_cells": len(self.input_cells),
            "output_cells": len(self.output_cells),
            "total_spikes": self.total_spikes,
            "queued_events": self._queued_event_count,
            "step_count": self._step_count,
            "dimensions": self.dimensions,
        }

    def get_neurons_by_type(self) -> dict[NeuronType, list[int]]:
        """Get neurons grouped by type.

        Returns:
            Dictionary mapping NeuronType to list of neuron IDs.
        """
        result: dict[NeuronType, list[int]] = {}
        for nid, neuron in self.neurons.items():
            neuron_type = neuron.neuron_type
            result.setdefault(neuron_type, []).append(nid)
        return result

    def get_activity_metrics(self) -> dict[str, Any]:
        """Get activity metrics for the network.

        Returns:
            Dictionary with activity statistics.
        """
        if not self.neurons:
            return {"active_neurons": 0, "mean_firing_rate": 0.0}

        rates = [n.firing_rate_estimate for n in self.neurons.values()]
        return {
            "active_neurons": sum(1 for r in rates if r > 0.1),
            "mean_firing_rate": sum(rates) / len(rates),
            "max_firing_rate": max(rates) if rates else 0.0,
            "min_firing_rate": min(rates) if rates else 0.0,
        }

    def get_energy_stats(self) -> dict[str, Any]:
        """Get energy statistics for the network.

        Returns:
            Dictionary with energy statistics.
        """
        if not self.neurons:
            return {"mean_energy": 0.0, "min_energy": 0.0, "max_energy": 0.0}

        energies = [n.energy for n in self.neurons.values()]
        return {
            "mean_energy": sum(energies) / len(energies),
            "min_energy": min(energies),
            "max_energy": max(energies),
        }

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self, include_state: bool = True) -> dict[str, Any]:
        """Serialize the network to a dictionary.

        Args:
            include_state: Whether to include neuron and synapse state.

        Returns:
            Dictionary containing network data.
        """
        data: dict[str, Any] = {
            "dimensions": list(self.dimensions),
            "tick": self.current_tick,
            "total_spikes": self.total_spikes,
            "synapse_count": self._synapse_count,
            "neurons": {},
            "synapses": {},
            "input_cells": list(self.input_cells),
            "output_cells": list(self.output_cells),
        }

        if include_state:
            # Serialize neurons
            for nid, neuron in self.neurons.items():
                data["neurons"][str(nid)] = neuron.to_dict()

            # Serialize synapses
            for pre_id, syn_list in self.synapses.items():
                data["synapses"][str(pre_id)] = [s.to_dict() for s in syn_list]

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        rng: random.Random | None = None,
    ) -> NeuralNetwork:
        """Deserialize a network from a dictionary.

        Args:
            data: Dictionary containing network data.
            rng: Optional random generator.

        Returns:
            A new NeuralNetwork instance.

        Raises:
            ValueError: If the data is invalid.
        """
        # Create config from dimensions
        dims = tuple(data["dimensions"])
        config = Brain5DConfig(dimensions=dims)

        network = cls(config, rng)

        # Restore neurons
        for nid_str, neuron_data in data.get("neurons", {}).items():
            nid = int(nid_str)
            neuron = Neuron.from_dict(neuron_data)
            network.neurons[nid] = neuron
            network.synapses[nid] = []

        # Restore synapses
        for pre_id_str, syn_list in data.get("synapses", {}).items():
            pre_id = int(pre_id_str)
            for syn_data in syn_list:
                synapse = Synapse.from_dict(syn_data)
                network.synapses[pre_id].append(synapse)
                network._synapse_count += 1
                network.in_degree[synapse.target_id] = (
                    network.in_degree.get(synapse.target_id, 0) + 1
                )

        # Restore input/output cells
        network.input_cells = set(data.get("input_cells", []))
        network.output_cells = set(data.get("output_cells", []))

        # Restore state
        network.current_tick = data.get("tick", 0)
        network.total_spikes = data.get("total_spikes", 0)

        return network

    # ========================================================================
    # String Representation
    # ========================================================================

    def __str__(self) -> str:
        return (
            f"NeuralNetwork(neurons={len(self.neurons)}, "
            f"synapses={self._synapse_count}, "
            f"tick={self.current_tick}, "
            f"input={len(self.input_cells)}, output={len(self.output_cells)})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ============================================================================
# Factory Functions
# ============================================================================


def create_network(
    dimensions: Dim5D = (50, 50, 50, 50, 50),
    seed: int | None = None,
    **kwargs: Any,
) -> NeuralNetwork:
    """Create a neural network with default configuration.

    Args:
        dimensions: 5D dimensions for the network.
        seed: Optional seed for random number generator.
        **kwargs: Additional configuration parameters.

    Returns:
        A new NeuralNetwork instance.

    Example:
        >>> network = create_network((10, 10, 10, 10, 10), seed=42)
        >>> network.add_neuron((1, 2, 3, 4, 5))
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    config = Brain5DConfig(dimensions=dimensions, **kwargs)
    return NeuralNetwork(config, rng)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Configuration
    "SimulationConfig",
    "TopologyConfig",
    "NetworkConfig",
    "Brain5DConfig",
    # Events
    "SpikeEvent",
    "StepResult",
    # Main class
    "NeuralNetwork",
    # Factory
    "create_network",
    # Types
    "PostStepHook",
    "ConfigDict",
]
