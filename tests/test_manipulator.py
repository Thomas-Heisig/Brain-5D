import random

from src.core.network import NeuralNetwork
from src.manipulation import Brain5DManipulator
from tests.conftest import base_config


def test_manipulator_create_connect_inspect_and_rollback() -> None:
    net = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    m = Brain5DManipulator(net)
    a = m.create_neuron((1, 1, 1, 1, 1))
    b = m.create_neuron((1, 1, 1, 1, 2))
    m.create_synapse(a, b, 0.2, 2)
    assert m.get_neuron(a)["out_degree"] == 1

    m.begin("voltage-test")
    m.set_neuron(a, v=-50.0, energy=0.8)
    assert net.neurons[a].v == -50.0
    m.rollback()
    assert net.neurons[a].v == -65.0
    assert net.neurons[a].energy == 1.0


def test_optical_sidecar_does_not_modify_core_neuron() -> None:
    net = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    m = Brain5DManipulator(net)
    nid = m.create_neuron((2, 2, 2, 2, 2))
    old_v = net.neurons[nid].v
    m.set_optical(nid, brightness=0.9, dopamine=0.5)
    assert net.neurons[nid].v == old_v
    assert m.get_neuron(nid)["optical"]["dopamine"] == 0.5
