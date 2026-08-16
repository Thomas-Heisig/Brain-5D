import random
from conftest import base_config
from src.core.network import NeuralNetwork


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