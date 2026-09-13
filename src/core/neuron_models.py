"""Versioned, deterministic single-neuron dynamics models for MHRN.

The registry in this module is deliberately small. A model is added only when
its transition equations, spike rule, reset rule and version are explicit.
This keeps model selection a scientific treatment rather than an untracked
implementation detail.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class NeuronModel(str, Enum):
    """Implemented membrane-dynamics model families."""

    IZHIKEVICH = "izhikevich-2003"
    LEAKY_INTEGRATE_AND_FIRE = "lif-current-v1"


@dataclass(frozen=True, slots=True)
class NeuronModelDescriptor:
    """Stable provenance metadata for one implemented dynamics model."""

    model: NeuronModel
    version: str
    family: str
    state_variables: tuple[str, ...]
    integration_rule: str
    spike_rule: str
    reset_rule: str
    canonical: bool
    citation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "model": self.model.value,
            "version": self.version,
            "family": self.family,
            "state_variables": list(self.state_variables),
            "integration_rule": self.integration_rule,
            "spike_rule": self.spike_rule,
            "reset_rule": self.reset_rule,
            "canonical": self.canonical,
            "citation": self.citation,
        }


MODEL_REGISTRY: Final[dict[NeuronModel, NeuronModelDescriptor]] = {
    NeuronModel.IZHIKEVICH: NeuronModelDescriptor(
        model=NeuronModel.IZHIKEVICH,
        version="mhrn-1.0",
        family="quadratic integrate-and-fire with recovery variable",
        state_variables=("v", "u"),
        integration_rule="two half Euler steps for v, one Euler step for u",
        spike_rule="v >= 30 mV plus optional adaptive threshold offset",
        reset_rule="v = c; u = u + d",
        canonical=True,
        citation=(
            "E. M. Izhikevich, Simple model of spiking neurons, "
            "IEEE Transactions on Neural Networks 14(6), 2003, "
            "doi:10.1109/TNN.2003.820440"
        ),
    ),
    NeuronModel.LEAKY_INTEGRATE_AND_FIRE: NeuronModelDescriptor(
        model=NeuronModel.LEAKY_INTEGRATE_AND_FIRE,
        version="mhrn-1.0",
        family="current-based leaky integrate-and-fire",
        state_variables=("v",),
        integration_rule="forward Euler membrane leak/current integration",
        spike_rule="v >= configured lif_threshold plus optional adaptation",
        reset_rule="v = configured lif_reset",
        canonical=False,
        citation="Reference current-based LIF implementation; model parameters are persisted.",
    ),
}

_MODEL_ALIASES: Final[dict[str, NeuronModel]] = {
    "izhikevich": NeuronModel.IZHIKEVICH,
    "izhikevich-2003": NeuronModel.IZHIKEVICH,
    "izh": NeuronModel.IZHIKEVICH,
    "lif": NeuronModel.LEAKY_INTEGRATE_AND_FIRE,
    "leaky-integrate-and-fire": NeuronModel.LEAKY_INTEGRATE_AND_FIRE,
    "lif-current-v1": NeuronModel.LEAKY_INTEGRATE_AND_FIRE,
}


def coerce_neuron_model(value: NeuronModel | str) -> NeuronModel:
    """Resolve a model enum or documented alias to a stable model identifier."""

    if isinstance(value, NeuronModel):
        return value
    key = str(value).strip().lower()
    try:
        return _MODEL_ALIASES[key]
    except KeyError as exc:
        supported = ", ".join(model.value for model in NeuronModel)
        raise ValueError(f"Unknown neuron model {value!r}; supported: {supported}") from exc


def get_model_descriptor(value: NeuronModel | str) -> NeuronModelDescriptor:
    """Return immutable provenance metadata for an implemented model."""

    return MODEL_REGISTRY[coerce_neuron_model(value)]


def available_neuron_models() -> tuple[NeuronModelDescriptor, ...]:
    """Return model descriptors in stable enum order."""

    return tuple(MODEL_REGISTRY[model] for model in NeuronModel)


def integrate_membrane(
    model: NeuronModel | str,
    *,
    v: float,
    u: float,
    input_current: float,
    dt_ms: float,
    a: float,
    b: float,
    lif_resting_potential: float,
    lif_tau_m_ms: float,
    lif_resistance: float,
) -> tuple[float, float]:
    """Advance only membrane-model state by one deterministic time step."""

    selected = coerce_neuron_model(model)
    if selected is NeuronModel.IZHIKEVICH:
        half_dt = 0.5 * dt_ms
        v += half_dt * (0.04 * v * v + 5.0 * v + 140.0 - u + input_current)
        v += half_dt * (0.04 * v * v + 5.0 * v + 140.0 - u + input_current)
        u += dt_ms * a * (b * v - u)
        return v, u

    dv = (
        (lif_resting_potential - v) + lif_resistance * input_current
    ) * (dt_ms / lif_tau_m_ms)
    return v + dv, u


def spike_threshold(
    model: NeuronModel | str,
    *,
    izhikevich_threshold: float,
    lif_threshold: float,
) -> float:
    """Return the non-adaptive spike threshold for a model."""

    selected = coerce_neuron_model(model)
    if selected is NeuronModel.IZHIKEVICH:
        return izhikevich_threshold
    return lif_threshold


def apply_spike_reset(
    model: NeuronModel | str,
    *,
    v: float,
    u: float,
    c: float,
    d: float,
    lif_reset: float,
) -> tuple[float, float]:
    """Apply the model-specific state transition immediately after a spike."""

    selected = coerce_neuron_model(model)
    if selected is NeuronModel.IZHIKEVICH:
        return c, u + d
    return lif_reset, u


__all__ = [
    "MODEL_REGISTRY",
    "NeuronModel",
    "NeuronModelDescriptor",
    "apply_spike_reset",
    "available_neuron_models",
    "coerce_neuron_model",
    "get_model_descriptor",
    "integrate_membrane",
    "spike_threshold",
]
