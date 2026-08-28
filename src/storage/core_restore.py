"""Restore a real Brain-5D core from snapshot, journal, and runtime sidecar."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Protocol, assert_never, cast

from src.config.loader import ConfigDict
from src.core.network import NeuralNetwork, SpikeEvent
from src.core.spatial_index import unpack_coords

from .b5d import B5DReader
from .checkpoint import RuntimeCheckpoint, read_runtime_checkpoint
from .recovery import RecoveryManager
from .structural_journal import StructuralChangeKind, StructuralChangeRecord
from .structural_recovery import StructuralRecoveryManager


class StructuralRestoreManipulator(Protocol):
    def create_neuron(self, coord: tuple[int, int, int, int, int]) -> int: ...
    def delete_neuron(self, neuron_id: int) -> None: ...
    def create_synapse(
        self, source_id: int, target_id: int, weight: float, delay: int
    ) -> None: ...
    def delete_synapse(self, source_id: int, target_id: int) -> None: ...


class _StructuralReplayTarget:
    def __init__(self, manipulator: StructuralRestoreManipulator) -> None:
        self._manipulator = manipulator

    def apply_structural_record(self, record: StructuralChangeRecord) -> bool:
        if record.kind is StructuralChangeKind.NEURON_ADD:
            if record.coord is None:
                return False
            neuron_id = self._manipulator.create_neuron(record.coord)
            return record.neuron_id is None or neuron_id == record.neuron_id
        if record.kind is StructuralChangeKind.NEURON_REMOVE:
            if record.neuron_id is None:
                return False
            self._manipulator.delete_neuron(record.neuron_id)
            return True
        if record.kind is StructuralChangeKind.SYNAPSE_ADD:
            if (
                record.source_id is None
                or record.target_id is None
                or record.weight is None
                or record.delay is None
            ):
                return False
            self._manipulator.create_synapse(
                record.source_id,
                record.target_id,
                record.weight,
                record.delay,
            )
            return True
        if record.kind is StructuralChangeKind.SYNAPSE_REMOVE:
            if record.source_id is None or record.target_id is None:
                return False
            self._manipulator.delete_synapse(record.source_id, record.target_id)
            return True
        assert_never(record.kind)


class RestoredNeuralNetwork(NeuralNetwork):
    """NeuralNetwork subclass exposing a narrow restoration hook."""

    def restore_queued_count(self, value: int) -> None:
        """Restore queue counter after event slots have been reconstructed."""
        self._queued_event_count = value


def restore_network(
    snapshot_path: Path,
    journal_path: Path,
    checkpoint_path: Path,
    config: ConfigDict,
    recovered_path: Path,
    *,
    structural_journal_path: Path | None = None,
) -> RestoredNeuralNetwork:
    """Recover persisted state and return a runnable deterministic network.

    Args:
        snapshot_path: Path to the base `.b5d` snapshot.
        journal_path: Path to the `.b5d.journal` delta journal.
        checkpoint_path: Path to the runtime checkpoint JSON.
        config: Network configuration (dict).
        recovered_path: Path to write the recovered snapshot (if needed).
        structural_journal_path: Optional structural journal path.

    Returns:
        A restored RestoredNeuralNetwork instance.

    Raises:
        RuntimeError: If recovery fails.
        ValueError: If the snapshot is not restart-capable or required fields are missing.
    """
    result = RecoveryManager(snapshot_path, journal_path).recover(recovered_path)
    if not result.success:
        raise RuntimeError(result.error or "snapshot recovery failed")

    checkpoint = read_runtime_checkpoint(checkpoint_path)
    rng = _restore_rng(checkpoint)

    # Cast ConfigDict to dict[str, Any] for the NeuralNetwork constructor
    network = RestoredNeuralNetwork(cast(dict[str, Any], config), rng)

    with B5DReader(recovered_path) as reader:
        for neuron_record in reader.iter_neurons():
            neuron_id = network.add_neuron(unpack_coords(neuron_record.neuron_id))
            neuron = network.neurons[neuron_id]

            # Ensure restart-capable snapshot was used
            if neuron_record.a is None or neuron_record.b is None:
                raise ValueError("restart-capable snapshot required")
            if neuron_record.c is None or neuron_record.d is None:
                raise ValueError("restart-capable snapshot required")
            if neuron_record.spike_cost is None:
                raise ValueError("restart-capable snapshot required")
            if neuron_record.spike_counter is None:
                raise ValueError("restart-capable snapshot required")
            if neuron_record.last_spike_tick is None:
                raise ValueError("restart-capable snapshot required")

            # Restore core neuron parameters
            neuron.a = neuron_record.a
            neuron.b = neuron_record.b
            neuron.c = neuron_record.c
            neuron.d = neuron_record.d
            neuron.spike_cost = neuron_record.spike_cost
            neuron.spike_counter = neuron_record.spike_counter
            neuron.last_spike_tick = neuron_record.last_spike_tick

            # Restore dynamic state from optical record
            neuron.v = neuron_record.optical.membrane_v
            neuron.u = neuron_record.optical.recovery_u
            neuron.energy = neuron_record.optical.energy
            neuron.threshold_adaptation = neuron_record.optical.threshold_adaptation

        for synapse_record in reader.iter_synapses():
            network.connect(
                synapse_record.source_id,
                synapse_record.target_id,
                synapse_record.weight,
                synapse_record.delay,
            )
            synapse = network.synapses[synapse_record.source_id][-1]
            synapse.eligibility = synapse_record.eligibility
            synapse.last_pre_spike = synapse_record.last_pre_spike

    # Replay structural plasticity journal if provided
    if structural_journal_path is not None:
        from src.manipulation.manipulator import Brain5DManipulator

        structural_target = _StructuralReplayTarget(Brain5DManipulator(network))
        StructuralRecoveryManager().replay(
            structural_target,
            structural_journal_path,
        )

    # Restore runtime state and exact neuron/synapse values from checkpoint
    _restore_runtime(network, checkpoint)
    _restore_exact_neuron_state(network, checkpoint)
    _restore_exact_synapse_state(network, checkpoint)

    return network


def _restore_rng(checkpoint: RuntimeCheckpoint) -> random.Random:
    """Restore the random number generator from checkpoint state."""
    rng = random.Random()
    rng.setstate(
        (
            checkpoint.rng.version,
            tuple(checkpoint.rng.state),
            checkpoint.rng.gauss_next,
        )
    )
    return rng


def _restore_runtime(
    network: RestoredNeuralNetwork,
    checkpoint: RuntimeCheckpoint,
) -> None:
    """Restore runtime state from checkpoint."""
    network.current_tick = checkpoint.current_tick
    network.total_spikes = checkpoint.total_spikes
    network.total_events_processed = checkpoint.total_events_processed
    network.pending_currents = dict(checkpoint.pending_currents)
    network.input_cells = set(checkpoint.input_cells)
    network.output_cells = set(checkpoint.output_cells)

    # Rebuild event queue
    network.event_slots = [[] for _ in range(network.max_delay + 1)]
    queued = 0
    for event in checkpoint.queued_events:
        slot = event.delivery_tick % len(network.event_slots)
        network.event_slots[slot].append(
            SpikeEvent(
                source_id=event.source_id,
                target_id=event.target_id,
                weight=event.weight,
                delivery_tick=event.delivery_tick,
            )
        )
        queued += 1
    network.restore_queued_count(queued)


def _restore_exact_neuron_state(
    network: RestoredNeuralNetwork,
    checkpoint: RuntimeCheckpoint,
) -> None:
    """Overlay exact values lost by the compact snapshot representation."""
    for state in checkpoint.neuron_states:
        neuron = network.neurons.get(state.neuron_id)
        if neuron is None:
            raise ValueError(
                f"runtime checkpoint references missing neuron {state.neuron_id}"
            )
        neuron.a = state.a
        neuron.b = state.b
        neuron.c = state.c
        neuron.d = state.d
        neuron.v = state.membrane_v
        neuron.u = state.recovery_u
        neuron.energy = state.energy
        neuron.spike_cost = state.spike_cost
        neuron.threshold_adaptation = state.threshold_adaptation
        neuron.spike_counter = state.spike_counter
        neuron.last_spike_tick = state.last_spike_tick
        neuron.last_external_current = state.last_external_current
        neuron.last_synaptic_current = state.last_synaptic_current


def _restore_exact_synapse_state(
    network: RestoredNeuralNetwork,
    checkpoint: RuntimeCheckpoint,
) -> None:
    """Overlay exact synaptic float state lost by V1 float32 fields."""
    if not checkpoint.synapse_states:
        return

    for state in checkpoint.synapse_states:
        candidates = network.synapses.get(state.source_id)
        if candidates is None:
            raise ValueError(
                f"runtime checkpoint references missing source {state.source_id}"
            )
        synapse = next(
            (item for item in candidates if item.target_id == state.target_id),
            None,
        )
        if synapse is None:
            raise ValueError(
                "runtime checkpoint references missing synapse "
                f"{state.source_id}->{state.target_id}"
            )
        synapse.weight = state.weight
        synapse.delay = state.delay
        synapse.eligibility = state.eligibility
        synapse.last_pre_spike = state.last_pre_spike


def restore_homeostasis_state(
    homeostasis_engine: Any,
    checkpoint: RuntimeCheckpoint,
) -> None:
    """Restore homeostasis engine state from checkpoint v4.

    Args:
        homeostasis_engine: A HomeostasisEngine instance (must have _rates_hz dict).
        checkpoint: The RuntimeCheckpoint with homeostasis_state.

    Raises:
        ValueError: If a neuron referenced in the checkpoint no longer exists.
    """
    if not checkpoint.homeostasis_state:
        return

    rates = {}
    for record in checkpoint.homeostasis_state:
        rates[int(record.neuron_id)] = float(record.rate_hz)

    # Restore the internal rates dict
    if hasattr(homeostasis_engine, "_rates_hz"):
        homeostasis_engine._rates_hz = rates


def restore_learning_state(
    learning_engine: Any,
    checkpoint: RuntimeCheckpoint,
) -> None:
    """Restore learning engine state from checkpoint v4.

    Restores per-synapse traces (last_pre_tick, last_post_tick, eligibility)
    and pending reward signals.

    Args:
        learning_engine: A LearningEngine instance (must have _states dict
            and _pending_rewards list).
        checkpoint: The RuntimeCheckpoint with learning_state and pending_rewards.

    Raises:
        ValueError: If a synapse referenced in the checkpoint no longer exists.
    """
    if not hasattr(learning_engine, "_states"):
        return

    # Restore per-synapse traces
    # Uses stable (pre_id, target_id) key matching LearningEngine's
    # deterministic topology indexing.
    if checkpoint.learning_state:
        states = learning_engine._states
        for record in checkpoint.learning_state:
            pre_id = int(record.pre_id)
            target_id = int(record.target_id)
            key = (pre_id, target_id)
            if key in states:
                state = states[key]
                state.last_pre_tick = record.last_pre_tick
                state.last_post_tick = record.last_post_tick
                # EligibilityTrace uses .value, not ._trace
                state.eligibility.value = record.eligibility_value
                # Restore per-trace last_tick so decay is accurate
                state.eligibility.last_tick = record.eligibility_last_tick

    # Restore pending rewards (independent of learning_state presence)
    if checkpoint.pending_rewards and hasattr(learning_engine, "_pending_rewards"):
        from src.learning.reward import RewardSignal
        learning_engine._pending_rewards = [
            RewardSignal(value=float(r.value), tick=int(r.tick))
            for r in checkpoint.pending_rewards
        ]


# ============================================================================
# Production Restore Bundle
# ============================================================================


class RestoredBundle:
    """Complete production restore result: network + optional engines.

    This bundles the restored neural network together with its optional
    homeostasis and learning engines, providing a single restore-and-continue
    entry point for production use.

    Attributes:
        network: The restored RestoredNeuralNetwork instance.
        homeostasis_engine: Optional restored HomeostasisEngine, or None.
        learning_engine: Optional restored LearningEngine, or None.
    """

    def __init__(
        self,
        network: RestoredNeuralNetwork,
        homeostasis_engine: Any | None = None,
        learning_engine: Any | None = None,
    ) -> None:
        self.network = network
        self.homeostasis_engine = homeostasis_engine
        self.learning_engine = learning_engine


def restore_full(
    snapshot_path: Path,
    journal_path: Path,
    checkpoint_path: Path,
    config: ConfigDict,
    recovered_path: Path,
    *,
    structural_journal_path: Path | None = None,
    create_homeostasis_engine: bool = False,
    create_learning_engine: bool = False,
) -> RestoredBundle:
    """Restore network and optionally create and restore engines.

    This is the production entry point that replaces calling
    ``restore_network()`` followed by manual engine creation and restore.
    It ensures the full restore chain is executed atomically:

    1. Recover snapshot and restore network (same as restore_network())
    2. Optionally create HomeostasisEngine and restore its state
    3. Optionally create LearningEngine and restore its state

    Args:
        snapshot_path: Path to the base ``.b5d`` snapshot.
        journal_path: Path to the ``.b5d.journal`` delta journal.
        checkpoint_path: Path to the runtime checkpoint JSON.
        config: Network configuration (dict).
        recovered_path: Path to write the recovered snapshot.
        structural_journal_path: Optional structural journal path.
        create_homeostasis_engine: If True, create and restore
            HomeostasisEngine from checkpoint.
        create_learning_engine: If True, create and restore
            LearningEngine from checkpoint.

    Returns:
        A RestoredBundle containing the network and optionally the engines.

    Raises:
        RuntimeError: If recovery fails.
        ValueError: If the snapshot is not restart-capable.
    """
    network = restore_network(
        snapshot_path=snapshot_path,
        journal_path=journal_path,
        checkpoint_path=checkpoint_path,
        config=config,
        recovered_path=recovered_path,
        structural_journal_path=structural_journal_path,
    )

    checkpoint = read_runtime_checkpoint(checkpoint_path)
    homeostasis_engine: Any = None
    learning_engine: Any = None

    if create_homeostasis_engine:
        from src.homeostasis.engine import HomeostasisEngine

        homeostasis_engine = HomeostasisEngine(network, dict(config))
        restore_homeostasis_state(homeostasis_engine, checkpoint)
        homeostasis_engine.attach()

    if create_learning_engine:
        from src.learning.learning_engine import LearningEngine

        learning_engine = LearningEngine(network, dict(config))
        restore_learning_state(learning_engine, checkpoint)
        learning_engine.attach()

    return RestoredBundle(
        network=network,
        homeostasis_engine=homeostasis_engine,
        learning_engine=learning_engine,
    )
