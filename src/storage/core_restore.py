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
