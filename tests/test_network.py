import random
from dataclasses import replace

from src.core.network import NeuralNetwork
from tests.conftest import base_config


def test_exact_event_delivery() -> None:
    # Testkonfiguration enthält zusätzliche Felder; Typprüfung für Tests deaktiviert.
    net = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    a = net.add_neuron((1, 1, 1, 1, 1))
    b = net.add_neuron((1, 1, 1, 1, 2))
    net.connect(a, b, 0.0, 2)
    net.neurons[a].v = 30.0
    r0 = net.step()
    assert r0.spike_ids == (a,) and r0.queued_events == 1
    r1 = net.step()
    assert r1.delivered_events == 0 and r1.queued_events == 1
    r2 = net.step()
    assert r2.delivered_events == 1 and r2.spike_ids == () and r2.queued_events == 0


def test_remove_updates_degrees() -> None:
    net = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    a = net.add_neuron((1, 1, 1, 1, 1))
    b = net.add_neuron((1, 1, 1, 1, 2))
    c = net.add_neuron((1, 1, 1, 1, 3))
    net.connect(a, b, 1, 1)
    net.connect(a, c, 1, 1)
    net.remove_neuron(a)
    assert net.synapse_count == 0 and net.in_degree[b] == 0 and net.in_degree[c] == 0


def test_dirty_ids_are_emitted_once_per_tick_and_include_topology() -> None:
    net = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    a = net.add_neuron((1, 1, 1, 1, 1))
    b = net.add_neuron((1, 1, 1, 1, 2))
    net.connect(a, b, 0.5, 1)

    first = net.step()
    second = net.step()

    assert a in first.dirty_neuron_ids and b in first.dirty_neuron_ids
    assert (a, b) in first.dirty_synapse_ids
    assert (a, b) in second.dirty_synapse_ids

    assert net.disconnect(a, b)
    third = net.step()
    assert (a, b) in third.dirty_synapse_ids


def test_step_batch_matches_single_tick_execution() -> None:
    single = NeuralNetwork(base_config(), random.Random(7))  # type: ignore[arg-type]
    batched = NeuralNetwork(base_config(), random.Random(7))  # type: ignore[arg-type]
    for network in (single, batched):
        first = network.add_neuron((1, 1, 1, 1, 1))
        second = network.add_neuron((1, 1, 1, 1, 2))
        network.connect(first, second, 0.5, 1)
        network.inject_current(first, 30.0)

    expected = tuple(single.step() for _ in range(4))
    actual = batched.step_batch(4)

    assert tuple(replace(result, core_step_ms=0.0) for result in actual) == tuple(
        replace(result, core_step_ms=0.0) for result in expected
    )
    assert batched.current_tick == single.current_tick == 4
    assert batched.queued_event_count == single.queued_event_count
