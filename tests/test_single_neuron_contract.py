"""Stage-0 single-cell contract and model-family regression tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.neuron import (
    Neuron,
    NeuronConfig,
    NeuronModel,
    NeuronType,
    available_neuron_models,
    create_neuron,
)
from src.core.neuron_models import integrate_membrane

ROOT = Path(__file__).parents[1]


def test_isolated_reference_disables_secondary_dynamics() -> None:
    n = create_neuron(1, config=NeuronConfig.isolated_reference())
    for tick in range(20):
        n.step(10.0, tick)
    assert n.energy == 1.0
    assert n.threshold_adaptation == 0.0
    assert n.pre_trace == 0.0
    assert n.post_trace == 0.0


def test_izhikevich_golden_trajectory() -> None:
    fixture = json.loads(
        (
            ROOT / "research/generated/verification/single_neuron_reference.json"
        ).read_text(encoding="utf-8")
    )
    n = create_neuron(1, config=NeuronConfig.isolated_reference())
    for reference in fixture["trajectory"]:
        tick = int(reference["tick"])
        spiked = n.step(float(fixture["protocol"]["input_current"]), tick)
        assert spiked is reference["spike"]
        assert n.v == pytest.approx(reference["v"], abs=1e-12)
        assert n.u == pytest.approx(reference["u"], abs=1e-12)


def test_deterministic_replay_is_exact() -> None:
    config = NeuronConfig.isolated_reference()
    left = create_neuron(1, config=config)
    right = create_neuron(1, config=config)
    currents = [0.0, 3.0, 10.0, 10.0, 0.0, 100.0, -4.0] * 25
    assert [left.step(v, t) for t, v in enumerate(currents)] == [
        right.step(v, t) for t, v in enumerate(currents)
    ]
    assert left.to_dict() == right.to_dict()


def test_spike_reset_matches_izhikevich_contract() -> None:
    config = NeuronConfig.isolated_reference()
    n = create_neuron(1, config=config)
    integrated_v, integrated_u = integrate_membrane(
        NeuronModel.IZHIKEVICH,
        v=n.v,
        u=n.u,
        input_current=100.0,
        dt_ms=config.dt_ms,
        a=n.a,
        b=n.b,
        lif_resting_potential=config.lif_resting_potential,
        lif_tau_m_ms=config.lif_tau_m_ms,
        lif_resistance=config.lif_resistance,
    )
    assert integrated_v >= config.izhikevich_threshold
    assert n.step(100.0, 0)
    assert n.v == n.c
    assert n.u == pytest.approx(integrated_u + n.d, abs=1e-12)


def test_optional_absolute_refractory_extension_is_explicit() -> None:
    n = create_neuron(1, config=NeuronConfig.isolated_reference(refractory_ticks=2))
    assert n.step(100.0, 0)
    assert not n.step(100.0, 1)
    assert not n.step(100.0, 2)
    assert n.step(100.0, 3)


@pytest.mark.parametrize(
    ("neuron_type", "expected"),
    [
        (NeuronType.REGULAR_SPIKING, (0.02, 0.2, -65.0, 8.0)),
        (NeuronType.FAST_SPIKING, (0.1, 0.2, -65.0, 2.0)),
        (NeuronType.INTRINSICALLY_BURSTING, (0.02, 0.2, -55.0, 4.0)),
        (NeuronType.CHATTERING, (0.02, 0.2, -50.0, 2.0)),
        (NeuronType.LOW_THRESHOLD_SPIKING, (0.02, 0.25, -65.0, 2.0)),
        (NeuronType.RESONATOR, (0.1, 0.26, -65.0, 2.0)),
        (NeuronType.SENSORY, (0.02, 0.2, -65.0, 8.0)),
        (NeuronType.MOTOR, (0.02, 0.2, -65.0, 8.0)),
    ],
)
def test_declared_izhikevich_type_defaults(
    neuron_type: NeuronType, expected: tuple[float, float, float, float]
) -> None:
    n = create_neuron(1, neuron_type=neuron_type)
    assert (n.a, n.b, n.c, n.d) == expected


def test_lif_is_a_real_alternative_model() -> None:
    config = NeuronConfig.isolated_reference(model=NeuronModel.LEAKY_INTEGRATE_AND_FIRE)
    n = create_neuron(1, config=config)
    spikes = [n.step(20.0, tick) for tick in range(28)]
    assert spikes[:27] == [False] * 27
    assert spikes[27] is True
    assert n.v == config.lif_reset


def test_model_registry_has_stable_canonical_identity() -> None:
    descriptors = available_neuron_models()
    assert {item.model for item in descriptors} == {
        NeuronModel.IZHIKEVICH,
        NeuronModel.LEAKY_INTEGRATE_AND_FIRE,
    }
    canonical = next(item for item in descriptors if item.canonical)
    assert canonical.model is NeuronModel.IZHIKEVICH
    assert canonical.version


def test_live_model_change_requires_explicit_switch() -> None:
    n = create_neuron(1, config=NeuronConfig.isolated_reference())
    n.step(0.0, 0)
    with pytest.raises(ValueError, match="switch_model"):
        n.set_config(
            NeuronConfig.isolated_reference(model=NeuronModel.LEAKY_INTEGRATE_AND_FIRE)
        )
    n.switch_model(NeuronModel.LEAKY_INTEGRATE_AND_FIRE, tick=1)
    assert n.model_switch_count == 1
    assert n.last_model_switch_tick == 1
    assert n.model_provenance["model"] == "lif-current-v1"


def test_serialization_roundtrip_preserves_continuation_state() -> None:
    original = create_neuron(
        7,
        config=NeuronConfig(refractory_ticks=1, threshold_adaptation_rate=0.02),
    )
    prefix = [10.0, 10.0, 0.0, 100.0, 0.0, 4.0] * 9
    for tick, current in enumerate(prefix):
        original.step(current, tick)
    restored = Neuron.from_dict(original.to_dict())
    assert restored.to_dict() == original.to_dict()
    future = [0.0, 10.0, 50.0, -2.0, 0.0, 100.0] * 8
    for tick, current in enumerate(future, start=len(prefix)):
        assert restored.step(current, tick) == original.step(current, tick)
        assert restored.to_dict() == original.to_dict()


def test_legacy_state_payload_remains_readable() -> None:
    n = Neuron.from_dict(
        {
            "neuron_id": 11,
            "v": -60.0,
            "u": -12.0,
            "spike_counter": 3,
            "last_spike_tick": 22,
            "neuron_type": "REGULAR_SPIKING",
        }
    )
    assert n.model is NeuronModel.IZHIKEVICH
    assert n.v == -60.0
    assert n.spike_counter == 3


def test_current_components_are_kept_separate() -> None:
    n = create_neuron(1, config=NeuronConfig.isolated_reference())
    n.step(5.0, 0, external_current=2.0, synaptic_current=3.0)
    assert n.last_external_current == 2.0
    assert n.last_synaptic_current == 3.0
    with pytest.raises(ValueError, match="must equal"):
        n.step(5.0, 1, external_current=2.0, synaptic_current=2.0)


def test_invalid_model_and_refractory_config_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown neuron model"):
        NeuronConfig(model="not-a-model")
    with pytest.raises(ValueError, match="refractory_ticks"):
        NeuronConfig(refractory_ticks=-1)
