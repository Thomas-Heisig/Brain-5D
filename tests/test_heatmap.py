"""Numerical heatmap tests that do not require an interactive GUI."""

import random

import numpy as np
import pytest

from src.core.network import NeuralNetwork
from src.visualization.heatmap import HeatmapProjector
from tests.conftest import base_config


def _network() -> tuple[NeuralNetwork, int, int, int]:
    # Die Testkonfiguration enthält zusätzliche Felder, die in ConfigDict nicht
    # deklariert sind. Für Tests ist es akzeptabel, die Typprüfung hier zu
    # deaktivieren, da die Laufzeitstruktur korrekt ist.
    network = NeuralNetwork(base_config(), random.Random(9))  # type: ignore[arg-type]
    first = network.add_neuron((1, 2, 0, 0, 0))
    second = network.add_neuron((1, 2, 1, 0, 0))
    third = network.add_neuron((3, 4, 0, 0, 0))
    network.connect(first, second, 0.4, 1)
    network.connect(third, second, 0.8, 1)
    return network, first, second, third


def test_all_heatmaps_have_xy_shape_and_finite_values() -> None:
    network, _, _, _ = _network()
    projector = HeatmapProjector(network, activity_tau_ticks=50.0)
    for kind in ("activity", "weights", "energy"):
        data = projector.build(kind)  # type: ignore[arg-type]  # valid kind values
        assert data.values.shape == (5, 5)
        assert np.isfinite(data.values).all()


def test_weight_projection_averages_incoming_weights_per_neuron() -> None:
    network, _, second, _ = _network()
    projector = HeatmapProjector(network)
    values = projector.weights()
    # Both neurons at X=1,Y=2 are averaged in the final XY cell. The first has
    # no incoming weight (0.0); the second has mean incoming weight 0.6.
    assert values[1, 2] == pytest.approx(0.3)  # type: ignore[reportUnknownMemberType]
    assert network.in_degree[second] == 2


def test_energy_projection_averages_hidden_dimensions() -> None:
    network, first, second, _ = _network()
    network.neurons[first].energy = 0.4
    network.neurons[second].energy = 0.8
    values = HeatmapProjector(network).energy()
    assert values[1, 2] == pytest.approx(0.6)  # type: ignore[reportUnknownMemberType]


def test_activity_uses_recent_spike_decay() -> None:
    network, first, second, _ = _network()
    network.current_tick = 20
    network.neurons[first].last_spike_tick = 20
    network.neurons[second].last_spike_tick = 10
    values = HeatmapProjector(network, activity_tau_ticks=10.0).activity()
    expected = (1.0 + np.exp(-1.0)) / 2.0
    assert values[1, 2] == pytest.approx(expected)  # type: ignore[reportUnknownMemberType]


def test_invalid_heatmap_kind_is_rejected() -> None:
    network, _, _, _ = _network()
    with pytest.raises(ValueError, match="Unsupported heatmap kind"):
        HeatmapProjector(network).build("invalid")  # type: ignore[arg-type]
