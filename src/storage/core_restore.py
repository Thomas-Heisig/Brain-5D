"""Restore a real Brain-5D core from snapshot, journal, and runtime sidecar."""

from __future__ import annotations

from pathlib import Path
import random

from src.core.network import ConfigDict, NeuralNetwork, SpikeEvent
from src.core.spatial_index import unpack_coords

from .b5d import B5DReader
from .checkpoint import RuntimeCheckpoint, read_runtime_checkpoint
from .recovery import RecoveryManager


class RestoredNeuralNetwork(NeuralNetwork):
    """NeuralNetwork subclass exposing a narrow restoration hook."""

    def restore_queued_count(self, value: int) -> None:
        """Restore the queue counter after event slots have been reconstructed."""
        self._queued_event_count = value


def restore_network(
    snapshot_path: Path,
    journal_path: Path,
    checkpoint_path: Path,
    config: ConfigDict,
    recovered_path: Path,
) -> RestoredNeuralNetwork:
    """Recover persisted state and return a runnable deterministic network."""
    result = RecoveryManager(snapshot_path, journal_path).recover(recovered_path)
    if not result.success:
        raise RuntimeError(result.error or "snapshot recovery failed")
    checkpoint = read_runtime_checkpoint(checkpoint_path)
    rng = _restore_rng(checkpoint)
    network = RestoredNeuralNetwork(config, rng)
    with B5DReader(recovered_path) as reader:
        for neuron_record in reader.iter_neurons():
            neuron_id = network.add_neuron(unpack_coords(neuron_record.neuron_id))
            neuron = network.neurons[neuron_id]
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
            neuron.a = neuron_record.a
            neuron.b = neuron_record.b
            neuron.c = neuron_record.c
            neuron.d = neuron_record.d
            neuron.spike_cost = neuron_record.spike_cost
            neuron.spike_counter = neuron_record.spike_counter
            neuron.last_spike_tick = neuron_record.last_spike_tick
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
    _restore_runtime(network, checkpoint)
    return network


def _restore_rng(checkpoint: RuntimeCheckpoint) -> random.Random:
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
    network: RestoredNeuralNetwork, checkpoint: RuntimeCheckpoint
) -> None:
    network.current_tick = checkpoint.current_tick
    network.total_spikes = checkpoint.total_spikes
    network.total_events_processed = checkpoint.total_events_processed
    network.pending_currents = dict(checkpoint.pending_currents)
    network.input_cells = set(checkpoint.input_cells)
    network.output_cells = set(checkpoint.output_cells)
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
