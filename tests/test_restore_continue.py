"""End-to-end deterministic restore-and-continue test against the real core."""

from __future__ import annotations

from pathlib import Path
import random
from typing import cast

from src.core.network import ConfigDict, NeuralNetwork
from src.core.spatial_index import pack_coords
from src.manipulation.manipulator import Brain5DManipulator
from src.storage.checkpoint import (
    CheckpointNetworkLike,
    capture_runtime_checkpoint,
    write_runtime_checkpoint,
)
from src.storage.core_restore import restore_network
from src.storage.runtime import RuntimeNetworkLike, StorageRuntimeConfig, StorageSession
from src.storage.structural_journal import (
    StructuralChangeKind,
    StructuralChangeRecord,
    StructuralJournal,
)


def _config() -> ConfigDict:
    return {
        "dimensions": [4, 1, 1, 1, 1],
        "simulation": {"dt_ms": 1.0, "max_delay": 4, "debug_invariants": True},
        "neuron": {
            "a": 0.020000000000000004,
            "b": 0.20000000000000004,
            "c": -65.0,
            "d": 8.000000000000002,
        },
        "energy": {"initial": 1.0, "spike_cost": 0.0010000000000000002},
        "topology": {
            "allow_self_connections": False,
            "allow_parallel_connections": False,
        },
        "network": {"weight_min": 0.0, "weight_max": 1.0},
    }


def _signature(network: NeuralNetwork, steps: int) -> tuple[tuple[object, ...], ...]:
    rows: list[tuple[object, ...]] = []
    ids = tuple(sorted(network.neurons))
    for _ in range(steps):
        result = network.step()
        rows.append(
            (
                result.tick,
                result.spike_ids,
                network.queued_event_count,
                tuple(network.neurons[nid].v for nid in ids),
                tuple(network.neurons[nid].u for nid in ids),
                tuple(network.neurons[nid].energy for nid in ids),
                tuple(
                    synapse.weight
                    for source_id in ids
                    for synapse in network.synapses[source_id]
                ),
            )
        )
    return tuple(rows)


def test_restore_and_continue_matches_continuous_reference(tmp_path: Path) -> None:
    config = _config()
    network = NeuralNetwork(config, random.Random(1234))
    source = network.add_neuron((0, 0, 0, 0, 0))
    target = network.add_neuron((1, 0, 0, 0, 0))
    network.connect(source, target, 0.3333333333333333, 2)
    network.synapses[source][0].eligibility = 0.1234567890123456

    runtime = StorageRuntimeConfig(
        snapshot_path=tmp_path / "base.b5d",
        journal_path=tmp_path / "base.b5d.journal",
        commit_interval_ticks=1,
    )
    with StorageSession(cast(RuntimeNetworkLike, network), runtime):
        network.inject_current(source, 100.0)
        network.step()

    structural_path = tmp_path / "structural.journal"
    structural_journal = StructuralJournal(structural_path)
    added_coord = (2, 0, 0, 0, 0)
    added_id = Brain5DManipulator(network).create_neuron(added_coord)
    assert added_id == pack_coords(*added_coord)
    structural_journal.append_and_commit(
        StructuralChangeRecord(
            sequence=1,
            tick=network.current_tick,
            kind=StructuralChangeKind.NEURON_ADD,
            neuron_id=added_id,
            coord=added_coord,
            reason="restore order test",
        )
    )

    checkpoint_path = tmp_path / "runtime.json"
    write_runtime_checkpoint(
        checkpoint_path,
        capture_runtime_checkpoint(cast(CheckpointNetworkLike, network)),
    )
    reference = _signature(network, 5)

    restored = restore_network(
        runtime.snapshot_path,
        runtime.journal_path,
        checkpoint_path,
        config,
        tmp_path / "recovered.b5d",
        structural_journal_path=structural_path,
    )
    resumed = _signature(restored, 5)
    assert resumed == reference
