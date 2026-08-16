"""Homeostatic self-regulation for Brain-5D v0.5."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.network import NeuralNetwork, StepResult


@dataclass(frozen=True, slots=True)
class HomeostasisParameters:
    """Validated parameters for firing-rate and energy homeostasis."""

    enabled: bool = False
    target_rate_hz: float = 5.0
    rate_tau_ticks: float = 200.0
    threshold_learning_rate: float = 0.001
    threshold_min: float = -15.0
    threshold_max: float = 30.0
    energy_enabled: bool = True
    target_energy: float = 1.0
    energy_recovery_rate: float = 0.001
    energy_min: float = 0.0
    energy_max: float = 1.0

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> "HomeostasisParameters":
        """Load the optional ``homeostasis`` section from configuration."""
        section = _string_mapping(config.get("homeostasis", {}), "homeostasis")
        params = cls(
            enabled=_bool_value(section.get("enabled", False), "enabled"),
            target_rate_hz=_float_value(
                section.get("target_rate_hz", 5.0), "target_rate_hz"
            ),
            rate_tau_ticks=_float_value(
                section.get("rate_tau_ticks", 200.0), "rate_tau_ticks"
            ),
            threshold_learning_rate=_float_value(
                section.get("threshold_learning_rate", 0.001),
                "threshold_learning_rate",
            ),
            threshold_min=_float_value(
                section.get("threshold_min", -15.0), "threshold_min"
            ),
            threshold_max=_float_value(
                section.get("threshold_max", 30.0), "threshold_max"
            ),
            energy_enabled=_bool_value(
                section.get("energy_enabled", True), "energy_enabled"
            ),
            target_energy=_float_value(
                section.get("target_energy", 1.0), "target_energy"
            ),
            energy_recovery_rate=_float_value(
                section.get("energy_recovery_rate", 0.001),
                "energy_recovery_rate",
            ),
            energy_min=_float_value(section.get("energy_min", 0.0), "energy_min"),
            energy_max=_float_value(section.get("energy_max", 1.0), "energy_max"),
        )
        params.validate()
        return params

    def validate(self) -> None:
        """Reject unstable or nonsensical regulator parameters."""
        if self.target_rate_hz < 0.0 or not math.isfinite(self.target_rate_hz):
            raise ValueError("homeostasis.target_rate_hz must be finite and >= 0")
        if self.rate_tau_ticks <= 0.0 or not math.isfinite(self.rate_tau_ticks):
            raise ValueError("homeostasis.rate_tau_ticks must be finite and > 0")
        if self.threshold_learning_rate < 0.0 or not math.isfinite(
            self.threshold_learning_rate
        ):
            raise ValueError("threshold_learning_rate must be finite and >= 0")
        if self.threshold_min > self.threshold_max:
            raise ValueError("threshold_min must be <= threshold_max")
        if not 0.0 <= self.energy_recovery_rate <= 1.0:
            raise ValueError("energy_recovery_rate must be between 0 and 1")
        if self.energy_min > self.energy_max:
            raise ValueError("energy_min must be <= energy_max")
        if not self.energy_min <= self.target_energy <= self.energy_max:
            raise ValueError("target_energy must be inside energy bounds")


@dataclass(frozen=True, slots=True)
class HomeostasisStats:
    """Immutable observable state of the regulator."""

    enabled: bool
    updates: int
    target_rate_hz: float
    mean_rate_hz: float
    mean_rate_error_hz: float
    mean_threshold_adaptation: float
    target_energy: float
    mean_energy: float
    mean_energy_error: float
    active_neurons: int


class HomeostasisEngine:
    """Regulate firing rate and energy through a post-step observer."""

    def __init__(self, network: "NeuralNetwork", config: Mapping[str, object]) -> None:
        self.network = network
        self.params = HomeostasisParameters.from_config(config)
        self._rates_hz: dict[int, float] = {}
        self._attached = False
        self._updates = 0
        self._last_stats = HomeostasisStats(
            enabled=self.params.enabled,
            updates=0,
            target_rate_hz=self.params.target_rate_hz,
            mean_rate_hz=0.0,
            mean_rate_error_hz=-self.params.target_rate_hz,
            mean_threshold_adaptation=0.0,
            target_energy=self.params.target_energy,
            mean_energy=0.0,
            mean_energy_error=self.params.target_energy,
            active_neurons=0,
        )

    @property
    def enabled(self) -> bool:
        """Return whether self-regulation is active."""
        return self.params.enabled

    @property
    def stats(self) -> HomeostasisStats:
        """Return the latest immutable regulator metrics."""
        return self._last_stats

    def attach(self) -> None:
        """Attach the regulator to the network post-step hook."""
        if not self._attached:
            self.network.add_post_step_hook(self.update)
            self._attached = True

    def detach(self) -> None:
        """Detach the regulator from the network."""
        if self._attached:
            self.network.remove_post_step_hook(self.update)
            self._attached = False

    def update(self, step_result: "StepResult") -> None:
        """Observe one completed tick and apply slow homeostatic feedback."""
        if not self.params.enabled:
            return
        spike_ids = set(step_result.spike_ids)
        alpha = 1.0 - math.exp(-1.0 / self.params.rate_tau_ticks)
        instantaneous_hz = 1000.0 / self.network.dt_ms

        rate_sum = 0.0
        threshold_sum = 0.0
        energy_sum = 0.0
        active_neurons = 0
        live_ids = set(self.network.neurons)
        self._rates_hz = {
            neuron_id: rate
            for neuron_id, rate in self._rates_hz.items()
            if neuron_id in live_ids
        }

        for neuron_id, neuron in self.network.neurons.items():
            previous_rate = self._rates_hz.get(neuron_id, 0.0)
            sample = instantaneous_hz if neuron_id in spike_ids else 0.0
            rate = previous_rate + alpha * (sample - previous_rate)
            self._rates_hz[neuron_id] = rate
            if neuron_id in spike_ids:
                active_neurons += 1

            rate_error = rate - self.params.target_rate_hz
            adjustment = self.params.threshold_learning_rate * rate_error
            neuron.threshold_adaptation = _clamp(
                neuron.threshold_adaptation + adjustment,
                self.params.threshold_min,
                self.params.threshold_max,
            )

            if self.params.energy_enabled:
                recovery = self.params.energy_recovery_rate * (
                    self.params.target_energy - neuron.energy
                )
                neuron.energy = _clamp(
                    neuron.energy + recovery,
                    self.params.energy_min,
                    self.params.energy_max,
                )

            rate_sum += rate
            threshold_sum += neuron.threshold_adaptation
            energy_sum += neuron.energy

        self._updates += 1
        count = len(self.network.neurons)
        mean_rate = rate_sum / count if count else 0.0
        mean_threshold = threshold_sum / count if count else 0.0
        mean_energy = energy_sum / count if count else 0.0
        self._last_stats = HomeostasisStats(
            enabled=True,
            updates=self._updates,
            target_rate_hz=self.params.target_rate_hz,
            mean_rate_hz=mean_rate,
            mean_rate_error_hz=mean_rate - self.params.target_rate_hz,
            mean_threshold_adaptation=mean_threshold,
            target_energy=self.params.target_energy,
            mean_energy=mean_energy,
            mean_energy_error=self.params.target_energy - mean_energy,
            active_neurons=active_neurons,
        )

    def rate_hz(self, neuron_id: int) -> float:
        """Return the exponentially smoothed firing rate of one neuron."""
        if neuron_id not in self.network.neurons:
            raise KeyError(neuron_id)
        return self._rates_hz.get(neuron_id, 0.0)


def _string_mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} config must be a mapping")
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{name} config keys must be strings")
        result[key] = item
    return result


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _float_value(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"homeostasis.{name} must be numeric")
    return float(value)


def _bool_value(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"homeostasis.{name} must be boolean")
    return value
