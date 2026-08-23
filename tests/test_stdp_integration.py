import math
import random
from typing import Any, cast

import pytest
from conftest import base_config

from src.core.network import NeuralNetwork, StepResult
from src.learning.learning_engine import LearningEngine


def _config(stdp: bool = True, eligibility: bool = True) -> dict[str, Any]:
    cfg = cast(dict[str, Any], base_config())
    cfg["stdp"] = {
        "enabled": stdp,
        "a_plus": 0.1,
        "a_minus": 0.12,
        "tau_plus": 20.0,
        "tau_minus": 20.0,
        "min_weight": 0.0,
        "max_weight": 1.0,
    }
    cfg["eligibility"] = {"enabled": eligibility, "tau_ticks": 200.0}
    return cfg


def _result(tick: int, *spike_ids: int) -> StepResult:
    return StepResult(
        tick=tick,
        spike_ids=tuple(spike_ids),
        output_spike_ids=(),
        spikes_this_tick=len(spike_ids),
        total_spikes=len(spike_ids),
        delivered_events=0,
        queued_events=0,
        external_injection_count=0,
        external_total_current=0.0,
        synaptic_current_targets=0,
        mean_v=-65.0,
        min_v=-65.0,
        max_v=-65.0,
        mean_energy=1.0,
        core_step_ms=0.0,
    )


def _two_neuron_network(cfg: dict[str, Any]) -> tuple[NeuralNetwork, int, int]:
    net = NeuralNetwork(cfg, random.Random(123))  # type: ignore[arg-type]
    a = net.add_neuron((1, 1, 1, 1, 1))
    b = net.add_neuron((1, 1, 1, 1, 2))
    net.connect(a, b, 0.5, 1)
    return net, a, b


def test_engine_ltp_pre_before_post() -> None:
    cfg = _config()
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(0, a))
    engine.update(_result(10, b))

    expected = 0.5 + 0.1 * math.exp(-10 / 20.0)
    assert net.synapses[a][0].weight == pytest.approx(expected)


def test_engine_ltd_post_before_pre() -> None:
    cfg = _config()
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(0, b))
    engine.update(_result(10, a))

    expected = 0.5 - 0.12 * math.exp(-10 / 20.0)
    assert net.synapses[a][0].weight == pytest.approx(expected)


def test_disabled_learning_preserves_weight() -> None:
    cfg = _config(stdp=False, eligibility=False)
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(0, a))
    engine.update(_result(10, b))

    assert net.synapses[a][0].weight == 0.5
    assert engine.stats.updates == 0


def test_eligibility_records_pair_without_reward_use() -> None:
    cfg = _config(stdp=False, eligibility=True)
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(0, a))
    engine.update(_result(10, b))

    expected = 0.1 * math.exp(-10 / 20.0)
    assert engine.get_eligibility(a, b) == pytest.approx(expected)
    assert net.synapses[a][0].weight == 0.5


def test_multiple_synapses_receive_post_event() -> None:
    cfg = _config()
    net = NeuralNetwork(cfg, random.Random(123))  # type: ignore[arg-type]
    a = net.add_neuron((1, 1, 1, 1, 1))
    b = net.add_neuron((1, 1, 1, 1, 2))
    c = net.add_neuron((1, 1, 1, 1, 3))
    net.connect(a, c, 0.4, 1)
    net.connect(b, c, 0.4, 1)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(0, a, b))
    engine.update(_result(5, c))

    expected = 0.4 + 0.1 * math.exp(-5 / 20.0)
    assert net.synapses[a][0].weight == pytest.approx(expected)
    assert net.synapses[b][0].weight == pytest.approx(expected)


def test_same_tick_pre_post_are_not_paired_with_each_other() -> None:
    cfg = _config()
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]

    engine.update(_result(5, a, b))

    assert net.synapses[a][0].weight == 0.5


def test_generic_network_hook_drives_learning_after_core_step() -> None:
    cfg = _config()
    net, a, b = _two_neuron_network(cfg)
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]
    engine.attach()

    net.inject_current(a, 100.0)
    first = net.step()
    assert a in first.spike_ids

    # Keep B quiet until a controlled postsynaptic spike at tick 10.
    for _ in range(1, 10):
        net.step()
    net.inject_current(b, 100.0)
    tenth = net.step()
    assert tenth.tick == 10
    assert b in tenth.spike_ids
    assert net.synapses[a][0].weight > 0.5


def test_engine_does_not_change_spike_times_for_controlled_pair() -> None:
    cfg_on = _config()
    cfg_off = _config(stdp=False, eligibility=False)
    net_on, a_on, b_on = _two_neuron_network(cfg_on)
    net_off, a_off, b_off = _two_neuron_network(cfg_off)
    engine = LearningEngine(net_on, cfg_on)  # type: ignore[arg-type]
    engine.attach()

    # Explizite Typannotation für die Spike-Listen, damit Pylance append erkennt.
    spikes_on: list[tuple[int, ...]] = []
    spikes_off: list[tuple[int, ...]] = []
    for tick in range(11):
        if tick == 0:
            net_on.inject_current(a_on, 100.0)
            net_off.inject_current(a_off, 100.0)
        if tick == 10:
            net_on.inject_current(b_on, 100.0)
            net_off.inject_current(b_off, 100.0)
        spikes_on.append(net_on.step().spike_ids)
        spikes_off.append(net_off.step().spike_ids)

    assert spikes_on == spikes_off
    assert net_on.synapses[a_on][0].weight != net_off.synapses[a_off][0].weight


def test_topology_count_change_refreshes_incoming_index() -> None:
    cfg = _config()
    net, a, _ = _two_neuron_network(cfg)
    c = net.add_neuron((1, 1, 1, 1, 3))
    engine = LearningEngine(net, cfg)  # type: ignore[arg-type]
    net.connect(a, c, 0.5, 1)

    engine.update(_result(0, a))
    engine.update(_result(5, c))

    assert net.synapses[a][1].weight > 0.5
