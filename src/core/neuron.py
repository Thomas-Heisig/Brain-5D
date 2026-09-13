"""Deterministic, versioned single-neuron primitive used by the MHRN core.

The historical Izhikevich implementation remains the canonical default. The
membrane-dynamics model is explicit and provenance-bearing, so alternative
models can be compared without silently changing the meaning of an experiment.
Secondary mechanisms can be disabled for an isolated Stage-0 reference cell.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields, replace
from enum import Enum, auto
from typing import Any, Callable

from .neuron_models import (
    NeuronModel,
    apply_spike_reset,
    available_neuron_models,
    coerce_neuron_model,
    get_model_descriptor,
    integrate_membrane,
    spike_threshold,
)


class NeuronType(Enum):
    """Functional neuron labels with established Izhikevich parameter sets."""

    REGULAR_SPIKING = auto()
    FAST_SPIKING = auto()
    INTRINSICALLY_BURSTING = auto()
    CHATTERING = auto()
    LOW_THRESHOLD_SPIKING = auto()
    RESONATOR = auto()
    SENSORY = auto()
    MOTOR = auto()

    @property
    def default_params(self) -> tuple[float, float, float, float]:
        params = {
            NeuronType.REGULAR_SPIKING: (0.02, 0.2, -65.0, 8.0),
            NeuronType.FAST_SPIKING: (0.1, 0.2, -65.0, 2.0),
            NeuronType.INTRINSICALLY_BURSTING: (0.02, 0.2, -55.0, 4.0),
            NeuronType.CHATTERING: (0.02, 0.2, -50.0, 2.0),
            NeuronType.LOW_THRESHOLD_SPIKING: (0.02, 0.25, -65.0, 2.0),
            NeuronType.RESONATOR: (0.1, 0.26, -65.0, 2.0),
            NeuronType.SENSORY: (0.02, 0.2, -65.0, 8.0),
            NeuronType.MOTOR: (0.02, 0.2, -65.0, 8.0),
        }
        return params.get(self, (0.02, 0.2, -65.0, 8.0))


@dataclass(frozen=True, slots=True)
class NeuronConfig:
    """Configuration for membrane dynamics and optional secondary mechanisms."""

    model: NeuronModel | str = NeuronModel.IZHIKEVICH
    dt_ms: float = 1.0
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    initial_v: float = -65.0
    initial_u: float = -13.0
    izhikevich_threshold: float = 30.0
    lif_resting_potential: float = -65.0
    lif_tau_m_ms: float = 20.0
    lif_resistance: float = 1.0
    lif_threshold: float = -50.0
    lif_reset: float = -65.0
    refractory_ticks: int = 0
    threshold_adaptation_rate: float = 0.01
    threshold_adaptation_decay: float = 0.999
    spike_cost: float = 0.001
    resting_energy: float = 1.0
    energy_recovery_rate: float = 0.0001
    trace_decay: float = 0.95
    trace_increment: float = 1.0
    target_rate_hz: float = 10.0
    homeostasis_learning_rate: float = 0.001
    enable_threshold_adaptation: bool = True
    enable_energy_dynamics: bool = True
    enable_traces: bool = True
    enable_homeostasis: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", coerce_neuron_model(self.model))
        if self.dt_ms <= 0.0:
            raise ValueError("dt_ms must be > 0")
        if self.lif_tau_m_ms <= 0.0:
            raise ValueError("lif_tau_m_ms must be > 0")
        if self.refractory_ticks < 0:
            raise ValueError("refractory_ticks must be >= 0")

    @classmethod
    def isolated_reference(
        cls,
        model: NeuronModel | str = NeuronModel.IZHIKEVICH,
        **overrides: Any,
    ) -> "NeuronConfig":
        values: dict[str, Any] = {
            "model": model,
            "enable_threshold_adaptation": False,
            "enable_energy_dynamics": False,
            "enable_traces": False,
            "enable_homeostasis": False,
        }
        values.update(overrides)
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["model"] = coerce_neuron_model(self.model).value
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NeuronConfig":
        names = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in names})


@dataclass(slots=True)
class Neuron:
    """One deterministic spiking neuron with an explicit dynamics model."""

    neuron_id: int
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -65.0
    u: float = -13.0
    energy: float = 1.0
    spike_cost: float = 0.001
    spike_counter: int = 0
    last_spike_tick: int = -1
    threshold_adaptation: float = 0.0
    last_external_current: float = 0.0
    last_synaptic_current: float = 0.0
    neuron_type: NeuronType = NeuronType.REGULAR_SPIKING
    model: NeuronModel | str = NeuronModel.IZHIKEVICH
    pre_trace: float = 0.0
    post_trace: float = 0.0
    firing_rate_estimate: float = 0.0
    model_switch_count: int = 0
    last_model_switch_tick: int = -1
    _config: NeuronConfig | None = field(default=None, repr=False, init=False)
    _enabled: bool = field(default=True, repr=False, init=False)
    _spike_count_window: int = 0
    _last_update_tick: int = 0
    _refractory_until_tick: int = -1
    _has_stepped: bool = False
    _dirty_callback: Callable[[], None] | None = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        self.model = coerce_neuron_model(self.model)
        if self._config is None:
            self._config = NeuronConfig(model=self.model)
        if self.model is NeuronModel.IZHIKEVICH and self.neuron_type is not NeuronType.REGULAR_SPIKING:
            params = self.neuron_type.default_params
            if self.a == 0.02 and self.b == 0.2 and self.c == -65.0 and self.d == 8.0:
                self.a, self.b, self.c, self.d = params

    def set_dirty_callback(self, callback: Callable[[], None] | None) -> None:
        self._dirty_callback = callback

    def mark_dirty(self) -> None:
        if self._dirty_callback is not None:
            self._dirty_callback()

    @property
    def is_inhibitory(self) -> bool:
        return self.neuron_type is NeuronType.FAST_SPIKING

    @property
    def config(self) -> NeuronConfig:
        if self._config is None:
            self._config = NeuronConfig(model=self.model)
        return self._config

    def set_config(self, config: NeuronConfig) -> None:
        target = coerce_neuron_model(config.model)
        if target is not self.model:
            if self._has_stepped:
                raise ValueError(
                    "Cannot change neuron model through set_config after execution; "
                    "use switch_model(..., tick=...) so provenance is recorded"
                )
            self.model = target
        self._config = config

    @property
    def model_provenance(self) -> dict[str, object]:
        descriptor = get_model_descriptor(self.model).to_dict()
        descriptor["parameters"] = self.config.to_dict()
        descriptor["switch_count"] = self.model_switch_count
        descriptor["last_switch_tick"] = self.last_model_switch_tick
        return descriptor

    @property
    def current_threshold(self) -> float:
        base = spike_threshold(
            self.model,
            izhikevich_threshold=self.config.izhikevich_threshold,
            lif_threshold=self.config.lif_threshold,
        )
        return base + self.threshold_adaptation if self.config.enable_threshold_adaptation else base

    def switch_model(
        self,
        model: NeuronModel | str,
        *,
        tick: int,
        config: NeuronConfig | None = None,
        reset_state: bool = True,
    ) -> None:
        target = coerce_neuron_model(model)
        if tick < self._last_update_tick:
            raise ValueError("model switch tick cannot precede the current neuron state")
        next_config = config or replace(self.config, model=target)
        if coerce_neuron_model(next_config.model) is not target:
            raise ValueError("switch_model config.model must match target model")
        if target is self.model and next_config == self.config:
            return
        self.model = target
        self._config = next_config
        self.model_switch_count += 1
        self.last_model_switch_tick = tick
        self._refractory_until_tick = -1
        if reset_state:
            self.v = next_config.lif_resting_potential if target is NeuronModel.LEAKY_INTEGRATE_AND_FIRE else next_config.initial_v
            self.u = next_config.initial_u
            self.threshold_adaptation = 0.0
            self.firing_rate_estimate = 0.0
            self._spike_count_window = 0
            self.reset_traces()
        self.mark_dirty()

    def _record_currents(
        self,
        input_current: float,
        external_current: float | None,
        synaptic_current: float | None,
    ) -> None:
        if external_current is not None or synaptic_current is not None:
            ext = 0.0 if external_current is None else float(external_current)
            syn = 0.0 if synaptic_current is None else float(synaptic_current)
            if not math.isclose(ext + syn, input_current, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("external_current + synaptic_current must equal input_current")
            self.last_external_current = ext
            self.last_synaptic_current = syn
            return
        observed_total = self.last_external_current + self.last_synaptic_current
        if not math.isclose(observed_total, input_current, rel_tol=1e-12, abs_tol=1e-12):
            self.last_external_current = float(input_current)
            self.last_synaptic_current = 0.0

    def _reset_potential(self) -> float:
        return self.config.lif_reset if self.model is NeuronModel.LEAKY_INTEGRATE_AND_FIRE else self.c

    def _finish_tick(self, tick: int) -> None:
        if self.config.enable_traces:
            self._decay_traces()
        if self.config.enable_energy_dynamics:
            self.energy = min(1.0, self.energy + self.config.energy_recovery_rate)
        if self.config.enable_threshold_adaptation:
            self.threshold_adaptation *= self.config.threshold_adaptation_decay
        if self.config.enable_homeostasis:
            self._apply_homeostasis()
        self._last_update_tick = tick
        self._has_stepped = True
        self.mark_dirty()

    def step(
        self,
        input_current: float,
        tick: int,
        *,
        external_current: float | None = None,
        synaptic_current: float | None = None,
    ) -> bool:
        if not self._enabled:
            return False
        self._record_currents(input_current, external_current, synaptic_current)
        if tick <= self._refractory_until_tick:
            self.v = self._reset_potential()
            self._finish_tick(tick)
            return False
        self.v, self.u = integrate_membrane(
            self.model,
            v=self.v,
            u=self.u,
            input_current=input_current,
            dt_ms=self.config.dt_ms,
            a=self.a,
            b=self.b,
            lif_resting_potential=self.config.lif_resting_potential,
            lif_tau_m_ms=self.config.lif_tau_m_ms,
            lif_resistance=self.config.lif_resistance,
        )
        spiked = self.v >= self.current_threshold
        if spiked:
            self.v, self.u = apply_spike_reset(
                self.model,
                v=self.v,
                u=self.u,
                c=self.c,
                d=self.d,
                lif_reset=self.config.lif_reset,
            )
            self.spike_counter += 1
            self.last_spike_tick = tick
            self._spike_count_window += 1
            if self.config.enable_energy_dynamics:
                self.energy = max(0.0, self.energy - self.spike_cost)
            dt = tick - self._last_update_tick if self._last_update_tick > 0 else 1
            self._update_firing_rate(dt)
            if self.config.enable_threshold_adaptation:
                self.threshold_adaptation += self.config.threshold_adaptation_rate
            if self.config.enable_traces:
                self.pre_trace += self.config.trace_increment
                self.post_trace += self.config.trace_increment
            if self.config.refractory_ticks > 0:
                self._refractory_until_tick = tick + self.config.refractory_ticks
        self._finish_tick(tick)
        return spiked

    def _decay_traces(self) -> None:
        self.pre_trace *= self.config.trace_decay
        self.post_trace *= self.config.trace_decay

    def get_pre_trace(self) -> float:
        return self.pre_trace

    def get_post_trace(self) -> float:
        return self.post_trace

    def reset_traces(self) -> None:
        self.pre_trace = 0.0
        self.post_trace = 0.0

    def _update_firing_rate(self, dt: int) -> None:
        alpha = 1.0 / (10.0 + dt)
        rate = self._spike_count_window / max(1, dt)
        self.firing_rate_estimate = (1.0 - alpha) * self.firing_rate_estimate + alpha * rate
        if dt > 100:
            self._spike_count_window = 0

    def _apply_homeostasis(self) -> None:
        error = self.firing_rate_estimate - self.config.target_rate_hz
        self.threshold_adaptation += self.config.homeostasis_learning_rate * error
        self.threshold_adaptation = max(-10.0, min(10.0, self.threshold_adaptation))

    def drain_energy(self, amount: float) -> float:
        drained = min(amount, self.energy)
        self.energy -= drained
        return drained

    def restore_energy(self, amount: float) -> float:
        restored = min(amount, 1.0 - self.energy)
        self.energy += restored
        return restored

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def reset_state(self, reset_v: bool = True) -> None:
        if reset_v:
            self.v = self.config.lif_resting_potential if self.model is NeuronModel.LEAKY_INTEGRATE_AND_FIRE else self.config.initial_v
            self.u = self.config.initial_u
        self.threshold_adaptation = 0.0
        self.energy = self.config.resting_energy
        self.firing_rate_estimate = 0.0
        self._spike_count_window = 0
        self._last_update_tick = 0
        self._refractory_until_tick = -1
        self._has_stepped = False
        self.reset_traces()
        self.mark_dirty()

    def reset_full(self) -> None:
        self.reset_state(reset_v=True)
        self.spike_counter = 0
        self.last_spike_tick = -1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "neuron_id": self.neuron_id,
            "model": coerce_neuron_model(self.model).value,
            "model_version": get_model_descriptor(self.model).version,
            "config": self.config.to_dict(),
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "v": self.v,
            "u": self.u,
            "energy": self.energy,
            "spike_cost": self.spike_cost,
            "spike_counter": self.spike_counter,
            "last_spike_tick": self.last_spike_tick,
            "threshold_adaptation": self.threshold_adaptation,
            "last_external_current": self.last_external_current,
            "last_synaptic_current": self.last_synaptic_current,
            "neuron_type": self.neuron_type.name,
            "pre_trace": self.pre_trace,
            "post_trace": self.post_trace,
            "firing_rate_estimate": self.firing_rate_estimate,
            "model_switch_count": self.model_switch_count,
            "last_model_switch_tick": self.last_model_switch_tick,
            "enabled": self._enabled,
            "spike_count_window": self._spike_count_window,
            "last_update_tick": self._last_update_tick,
            "refractory_until_tick": self._refractory_until_tick,
            "has_stepped": self._has_stepped,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Neuron":
        neuron_type = NeuronType[data.get("neuron_type", "REGULAR_SPIKING")]
        config_data = data.get("config")
        if isinstance(config_data, dict):
            config = NeuronConfig.from_dict(config_data)
        else:
            config = NeuronConfig(
                model=data.get("model", NeuronModel.IZHIKEVICH.value),
                a=float(data.get("a", 0.02)),
                b=float(data.get("b", 0.2)),
                c=float(data.get("c", -65.0)),
                d=float(data.get("d", 8.0)),
                spike_cost=float(data.get("spike_cost", 0.001)),
            )
        model = coerce_neuron_model(data.get("model", config.model))
        neuron = cls(
            neuron_id=int(data["neuron_id"]),
            a=float(data.get("a", config.a)),
            b=float(data.get("b", config.b)),
            c=float(data.get("c", config.c)),
            d=float(data.get("d", config.d)),
            v=float(data.get("v", config.initial_v)),
            u=float(data.get("u", config.initial_u)),
            energy=float(data.get("energy", config.resting_energy)),
            spike_cost=float(data.get("spike_cost", config.spike_cost)),
            spike_counter=int(data.get("spike_counter", 0)),
            last_spike_tick=int(data.get("last_spike_tick", -1)),
            threshold_adaptation=float(data.get("threshold_adaptation", 0.0)),
            last_external_current=float(data.get("last_external_current", 0.0)),
            last_synaptic_current=float(data.get("last_synaptic_current", 0.0)),
            neuron_type=neuron_type,
            model=model,
            pre_trace=float(data.get("pre_trace", 0.0)),
            post_trace=float(data.get("post_trace", 0.0)),
            firing_rate_estimate=float(data.get("firing_rate_estimate", 0.0)),
            model_switch_count=int(data.get("model_switch_count", 0)),
            last_model_switch_tick=int(data.get("last_model_switch_tick", -1)),
        )
        neuron.set_config(config)
        neuron._enabled = bool(data.get("enabled", True))
        neuron._spike_count_window = int(data.get("spike_count_window", 0))
        neuron._last_update_tick = int(data.get("last_update_tick", 0))
        neuron._refractory_until_tick = int(data.get("refractory_until_tick", -1))
        neuron._has_stepped = bool(data.get("has_stepped", neuron.spike_counter > 0 or neuron._last_update_tick != 0))
        return neuron

    def __str__(self) -> str:
        return (
            f"Neuron(id={self.neuron_id}, type={self.neuron_type.name}, "
            f"model={coerce_neuron_model(self.model).value}, v={self.v:.1f}mV, "
            f"spikes={self.spike_counter}, rate={self.firing_rate_estimate:.1f}Hz)"
        )

    def __repr__(self) -> str:
        return self.__str__()


def create_neuron(
    neuron_id: int,
    neuron_type: NeuronType = NeuronType.REGULAR_SPIKING,
    config: NeuronConfig | None = None,
    **kwargs: Any,
) -> Neuron:
    params = neuron_type.default_params
    config_a = config.a if config is not None else params[0]
    config_b = config.b if config is not None else params[1]
    config_c = config.c if config is not None else params[2]
    config_d = config.d if config is not None else params[3]
    initial_v = config.initial_v if config is not None else -65.0
    initial_u = config.initial_u if config is not None else -13.0
    initial_energy = config.resting_energy if config is not None else 1.0
    spike_cost = config.spike_cost if config is not None else 0.001
    configured_model = config.model if config is not None else NeuronModel.IZHIKEVICH
    model = coerce_neuron_model(kwargs.get("model", configured_model))
    if config is not None and model is not coerce_neuron_model(config.model):
        raise ValueError("Explicit model must match config.model")
    neuron = Neuron(
        neuron_id=neuron_id,
        a=kwargs.get("a", config_a),
        b=kwargs.get("b", config_b),
        c=kwargs.get("c", config_c),
        d=kwargs.get("d", config_d),
        v=kwargs.get("v", initial_v),
        u=kwargs.get("u", initial_u),
        energy=kwargs.get("energy", initial_energy),
        spike_cost=kwargs.get("spike_cost", spike_cost),
        spike_counter=kwargs.get("spike_counter", 0),
        last_spike_tick=kwargs.get("last_spike_tick", -1),
        threshold_adaptation=kwargs.get("threshold_adaptation", 0.0),
        neuron_type=neuron_type,
        model=model,
        pre_trace=kwargs.get("pre_trace", 0.0),
        post_trace=kwargs.get("post_trace", 0.0),
        firing_rate_estimate=kwargs.get("firing_rate_estimate", 0.0),
    )
    if config is not None:
        neuron.set_config(config)
    return neuron


def create_random_neuron(
    neuron_id: int,
    rng: Any,
    neuron_type: NeuronType | None = None,
) -> Neuron:
    if neuron_type is None:
        neuron_type = rng.choice(list(NeuronType))
    assert neuron_type is not None
    params = neuron_type.default_params
    a = max(0.01, min(0.2, params[0] * (1.0 + rng.uniform(-0.1, 0.1))))
    b = max(0.1, min(0.5, params[1] * (1.0 + rng.uniform(-0.1, 0.1))))
    c = max(-80.0, min(-40.0, params[2] + rng.uniform(-5.0, 5.0)))
    d = max(1.0, min(15.0, params[3] + rng.uniform(-1.0, 1.0)))
    return create_neuron(
        neuron_id,
        neuron_type,
        a=a,
        b=b,
        c=c,
        d=d,
        v=rng.uniform(-70.0, -50.0),
        u=rng.uniform(-20.0, -5.0),
        energy=rng.uniform(0.8, 1.0),
    )


__all__ = [
    "Neuron",
    "NeuronConfig",
    "NeuronModel",
    "NeuronType",
    "available_neuron_models",
    "create_neuron",
    "create_random_neuron",
]
