from src.core.neuron import Neuron


def test_regular_spiking():
    n = Neuron(1)
    spikes = 0
    for t in range(200):
        spikes += int(n.step(10.0, t))
    assert spikes > 0 and n.spike_counter == spikes


def test_high_current_spikes():
    n = Neuron(1)
    assert n.step(100.0, 0)
