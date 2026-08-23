"""Regression tests for the generic post-step hook used by learning layers."""

from __future__ import annotations

import random

from conftest import base_config

from src.core.network import NeuralNetwork, StepResult


def test_post_step_hook_receives_completed_result() -> None:
    """A registered hook must receive the exact completed StepResult."""
    # Die Testkonfiguration enthält zusätzliche Felder; für Tests ist
    # eine Ignorierung der Typprüfung akzeptabel, da die Laufzeitstruktur korrekt ist.
    network = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    network.add_neuron((1, 1, 1, 1, 1))
    observed: list[StepResult] = []
    network.add_post_step_hook(observed.append)

    result = network.step()

    assert observed == [result]
    assert result.tick == 0
    assert network.current_tick == 1


def test_post_step_hook_can_be_removed() -> None:
    """Removing a hook must prevent later callbacks without affecting steps."""
    network = NeuralNetwork(base_config(), random.Random(1))  # type: ignore[arg-type]
    network.add_neuron((1, 1, 1, 1, 1))
    observed: list[StepResult] = []
    network.add_post_step_hook(observed.append)
    network.remove_post_step_hook(observed.append)

    network.step()

    assert observed == []
