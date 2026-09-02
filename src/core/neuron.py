"""Izhikevich neuron model used by the sparse Brain-5D core.

This module defines the Neuron class, which implements the Izhikevich
spiking neuron model with:
- Multiple neuron types (excitatory, inhibitory, etc.)
- Adaptive threshold and homeostasis
- Energy consumption and spike cost
- STDP trace support for plasticity
- Serialization and factory functions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

# ============================================================================
# Neuron Types
# ============================================================================


class NeuronType(Enum):
    """Types of neurons with distinct Izhikevich parameters."""

    REGULAR_SPIKING = auto()  # RS - typical excitatory
    FAST_SPIKING = auto()  # FS - fast inhibitory
    INTRINSICALLY_BURSTING = auto()  # IB - bursting neurons
    CHATTERING = auto()  # CH - chattering
    LOW_THRESHOLD_SPIKING = auto()  # LTS - low-threshold
    RESONATOR = auto()  # RZ - resonator
    SENSORY = auto()  # Sensory input neuron
    MOTOR = auto()  # Motor output neuron

    @property
    def default_params(self) -> tuple[float, float, float, float]:
        """Get default Izhikevich parameters for this neuron type.

        Returns:
            (a, b, c, d) tuple.
        """
        params = {
            NeuronType.REGULAR_SPIKING: (0.02, 0.2, -65.0, 8.0),
            NeuronType.FAST_SPIKING: (0.1, 0.2, -65.0, 2.0),
            NeuronType.INTRINSICALLY_BURSTING: (0.02, 0.2, -55.0, 4.0),
            NeuronType.CHATTERING: (0.02, 0.2, -50.0, 2.0),
            NeuronType.LOW_THRESHOLD_SPIKING: (0.02, 0.25, -65.0, 2.0),
            NeuronType.RESONATOR: (0.1, 0.26, -65.0, 2.0),
            NeuronType.SENSORY: (0.02, 0.2, -65.0, 8.0),  # same as RS
            NeuronType.MOTOR: (0.02, 0.2, -65.0, 8.0),  # same as RS
        }
        return params.get(self, (0.02, 0.2, -65.0, 8.0))


# ============================================================================
# Neuron Configuration
# ============================================================================


@dataclass(frozen=True, slots=True)
class NeuronConfig:
    """Configuration parameters for neuron dynamics and plasticity."""

    # Izhikevich parameters (can be overridden per neuron)
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0

    # Threshold adaptation
    threshold_adaptation_rate: float = 0.01  # per spike
    threshold_adaptation_decay: float = 0.999  # per tick (homeostasis)

    # Energy
    spike_cost: float = 0.001
    resting_energy: float = 1.0
    energy_recovery_rate: float = 0.0001  # per tick

    # STDP traces (for neuron-level eligibility)
    trace_decay: float = 0.95  # per tick
    trace_increment: float = 1.0  # on spike

    # Homeostasis
    target_rate_hz: float = 10.0  # desired firing rate
    homeostasis_learning_rate: float = 0.001  # per tick


# ============================================================================
# Neuron Class
# ============================================================================


@dataclass(slots=True)
class Neuron:
    """One deterministic spiking neuron with energy and adaptive threshold.

    This implements the Izhikevich neuron model with:
    - Membrane potential (v) and recovery variable (u)
    - Spike-driven threshold adaptation
    - Energy consumption and recovery
    - STDP trace support
    - Homeostatic rate regulation

    Attributes:
        neuron_id: Unique identifier for this neuron.
        a: Izhikevich parameter (recovery time constant).
        b: Izhikevich parameter (sensitivity of u to v).
        c: Izhikevich parameter (reset potential).
        d: Izhikevich parameter (recovery increment after spike).
        v: Membrane potential (mV).
        u: Recovery variable.
        energy: Current energy level (0.0 - 1.0).
        spike_cost: Energy cost per spike.
        spike_counter: Total number of spikes fired.
        last_spike_tick: Tick of the last spike (-1 if never).
        threshold_adaptation: Adaptive threshold offset (mV).
        last_external_current: Last external input current.
        last_synaptic_current: Last synaptic input current.
        neuron_type: Type of neuron (for parameter lookup).
        config: Configuration for this neuron.
        pre_trace: Presynaptic STDP trace (for triplet STDP).
        post_trace: Postsynaptic STDP trace (for triplet STDP).
        firing_rate_estimate: Smoothed firing rate estimate.
        _spike_count_window: Number of spikes in recent window.
        _last_update_tick: Last tick when traces were updated.
    """

    # === Core fields ===
    neuron_id: int
    a: float = 0.02
    b: float = 0.2
    c: float = -65.0
    d: float = 8.0
    v: float = -65.0
    u: float = -13.0

    # === Energy ===
    energy: float = 1.0
    spike_cost: float = 0.001

    # === Statistics ===
    spike_counter: int = 0
    last_spike_tick: int = -1

    # === Adaptation ===
    threshold_adaptation: float = 0.0

    # === Currents (for debugging) ===
    last_external_current: float = 0.0
    last_synaptic_current: float = 0.0

    # === Type and configuration ===
    neuron_type: NeuronType = NeuronType.REGULAR_SPIKING

    # === STDP traces ===
    pre_trace: float = 0.0  # Presynaptic trace for triplet STDP
    post_trace: float = 0.0  # Postsynaptic trace for triplet STDP

    # === Homeostasis ===
    firing_rate_estimate: float = 0.0

    # === Internal state ===
    _config: NeuronConfig | None = field(default=None, repr=False, init=False)
    _enabled: bool = field(default=True, repr=False, init=False)
    _spike_count_window: int = 0
    _last_update_tick: int = 0
    _dirty_callback: Callable[[], None] | None = field(default=None, repr=False, init=False)

    def set_dirty_callback(self, callback: Callable[[], None] | None) -> None:
        """Attach the runtime callback used to publish state mutations."""
        self._dirty_callback = callback

    def mark_dirty(self) -> None:
        """Publish a mutation to an attached runtime observer."""
        if self._dirty_callback is not None:
            self._dirty_callback()

    @property
    def is_inhibitory(self) -> bool:
        """Whether this neuron is an inhibitory type (FAST_SPIKING)."""
        return self.neuron_type is NeuronType.FAST_SPIKING

    # ========================================================================
    # Initialization
    # ========================================================================

    def __post_init__(self) -> None:
        """Initialize neuron with default config and type parameters."""
        if self._config is None:
            self._config = NeuronConfig()

        # Set default parameters based on neuron type if not manually specified
        if self.neuron_type != NeuronType.REGULAR_SPIKING:
            params = self.neuron_type.default_params
            # Only override if values are still at defaults
            if self.a == 0.02 and self.b == 0.2 and self.c == -65.0 and self.d == 8.0:
                self.a, self.b, self.c, self.d = params

    # ========================================================================
    # Configuration
    # ========================================================================

    @property
    def config(self) -> NeuronConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = NeuronConfig()
        return self._config

    def set_config(self, config: NeuronConfig) -> None:
        """Set the configuration for this neuron."""
        self._config = config

    # ========================================================================
    # Core Dynamics
    # ========================================================================

    def step(self, input_current: float, tick: int) -> bool:
        """Advance the neuron by one millisecond and return whether it spiked.

        Uses the Izhikevich model with adaptive threshold.
        Also updates energy, homeostasis, and traces.

        Args:
            input_current: Total input current (external + synaptic).
            tick: Current simulation tick.

        Returns:
            True if the neuron spiked, False otherwise.
        """
        if not self._enabled:
            return False

        # Store currents for debugging
        self.last_external_current = 0.0  # Will be set by caller
        self.last_synaptic_current = input_current  # Will be set by caller

        # Izhikevich integration (with adaptive threshold)
        # Using two-step Euler method for better stability
        self.v += 0.5 * (
            0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + input_current
        )
        self.v += 0.5 * (
            0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + input_current
        )
        self.u += self.a * (self.b * self.v - self.u)

        # Check spike condition (with adaptive threshold)
        threshold = 30.0 + self.threshold_adaptation
        spiked = False

        if self.v >= threshold:
            # Spike!
            self.v = self.c
            self.u += self.d
            self.spike_counter += 1
            self.last_spike_tick = tick
            self._spike_count_window += 1

            # Energy cost
            self.energy = max(0.0, self.energy - self.spike_cost)

            # Update firing rate estimate
            dt = tick - self._last_update_tick if self._last_update_tick > 0 else 1
            self._update_firing_rate(dt)

            # Update adaptation
            self.threshold_adaptation += self.config.threshold_adaptation_rate

            # Update traces
            self.pre_trace += self.config.trace_increment
            self.post_trace += self.config.trace_increment

            spiked = True

        # Decay traces
        self._decay_traces()

        # Energy recovery
        self.energy = min(1.0, self.energy + self.config.energy_recovery_rate)

        # Threshold adaptation decay (homeostasis)
        self.threshold_adaptation *= self.config.threshold_adaptation_decay

        # Homeostatic rate regulation (slow)
        self._apply_homeostasis()

        # Update tick tracking
        self._last_update_tick = tick

        self.mark_dirty()
        return spiked

    # ========================================================================
    # Traces and Plasticity
    # ========================================================================

    def _decay_traces(self) -> None:
        """Decay STDP traces."""
        decay = self.config.trace_decay
        self.pre_trace *= decay
        self.post_trace *= decay

    def get_pre_trace(self) -> float:
        """Get the presynaptic trace value."""
        return self.pre_trace

    def get_post_trace(self) -> float:
        """Get the postsynaptic trace value."""
        return self.post_trace

    def reset_traces(self) -> None:
        """Reset all trace values."""
        self.pre_trace = 0.0
        self.post_trace = 0.0

    # ========================================================================
    # Homeostasis
    # ========================================================================

    def _update_firing_rate(self, dt: int) -> None:
        """Update the smoothed firing rate estimate."""
        # Simple exponential moving average
        alpha = 1.0 / (10.0 + dt)  # adaptive smoothing
        # Estimate rate from recent spike count
        rate = self._spike_count_window / max(1, dt)
        self.firing_rate_estimate = (
            1.0 - alpha
        ) * self.firing_rate_estimate + alpha * rate
        # Reset window counter periodically
        if dt > 100:
            self._spike_count_window = 0

    def _apply_homeostasis(self) -> None:
        """Apply homeostatic regulation to threshold and energy."""
        config = self.config
        target = config.target_rate_hz
        current = self.firing_rate_estimate

        # Scale threshold adaptation based on error
        error = current - target
        self.threshold_adaptation += config.homeostasis_learning_rate * error

        # Clamp threshold adaptation to prevent runaway
        self.threshold_adaptation = max(-10.0, min(10.0, self.threshold_adaptation))

    # ========================================================================
    # Energy Management
    # ========================================================================

    def drain_energy(self, amount: float) -> float:
        """Drain energy by a specified amount.

        Returns:
            Actual amount drained (capped by available energy).
        """
        drained = min(amount, self.energy)
        self.energy -= drained
        return drained

    def restore_energy(self, amount: float) -> float:
        """Restore energy by a specified amount.

        Returns:
            Actual amount restored (capped by max energy).
        """
        max_energy = 1.0
        restored = min(amount, max_energy - self.energy)
        self.energy += restored
        return restored

    # ========================================================================
    # State Management
    # ========================================================================

    def enable(self) -> None:
        """Enable this neuron (allow spiking and plasticity)."""
        self._enabled = True

    def disable(self) -> None:
        """Disable this neuron (no spiking or plasticity)."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if the neuron is enabled."""
        return self._enabled

    def reset_state(self, reset_v: bool = True) -> None:
        """Reset the neuron's dynamic state (membrane potential, recovery)."""
        if reset_v:
            self.v = self.c
            self.u = self.c * 0.2  # approximate resting u
        self.threshold_adaptation = 0.0
        self.energy = 1.0
        self.firing_rate_estimate = 0.0
        self._spike_count_window = 0
        self.reset_traces()

    def reset_full(self) -> None:
        """Reset all state including statistics."""
        self.reset_state(reset_v=True)
        self.spike_counter = 0
        self.last_spike_tick = -1

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize neuron to dictionary."""
        return {
            "neuron_id": self.neuron_id,
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
            "neuron_type": self.neuron_type.name,
            "pre_trace": self.pre_trace,
            "post_trace": self.post_trace,
            "firing_rate_estimate": self.firing_rate_estimate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Neuron:
        """Deserialize neuron from dictionary."""
        neuron_type = NeuronType[data.get("neuron_type", "REGULAR_SPIKING")]
        return cls(
            neuron_id=data["neuron_id"],
            a=data.get("a", 0.02),
            b=data.get("b", 0.2),
            c=data.get("c", -65.0),
            d=data.get("d", 8.0),
            v=data.get("v", -65.0),
            u=data.get("u", -13.0),
            energy=data.get("energy", 1.0),
            spike_cost=data.get("spike_cost", 0.001),
            spike_counter=data.get("spike_counter", 0),
            last_spike_tick=data.get("last_spike_tick", -1),
            threshold_adaptation=data.get("threshold_adaptation", 0.0),
            neuron_type=neuron_type,
            pre_trace=data.get("pre_trace", 0.0),
            post_trace=data.get("post_trace", 0.0),
            firing_rate_estimate=data.get("firing_rate_estimate", 0.0),
        )

    # ========================================================================
    # String Representation
    # ========================================================================

    def __str__(self) -> str:
        return (
            f"Neuron(id={self.neuron_id}, type={self.neuron_type.name}, "
            f"v={self.v:.1f}mV, spikes={self.spike_counter}, "
            f"rate={self.firing_rate_estimate:.1f}Hz)"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ============================================================================
# Factory Functions
# ============================================================================


def create_neuron(
    neuron_id: int,
    neuron_type: NeuronType = NeuronType.REGULAR_SPIKING,
    config: NeuronConfig | None = None,
    **kwargs: Any,
) -> Neuron:
    """Create a neuron with specified type and optional custom parameters.

    Args:
        neuron_id: Unique identifier for the neuron.
        neuron_type: Type of neuron (affects default Izhikevich parameters).
        config: Optional custom configuration.
        **kwargs: Override any neuron attribute (a, b, c, d, v, u, etc.)

    Returns:
        A new Neuron instance.

    Example:
        >>> neuron = create_neuron(42, NeuronType.FAST_SPIKING, v=-60.0)
        >>> neuron.step(0.0, 0)
    """
    # Get default parameters for this type
    params = neuron_type.default_params
    neuron = Neuron(
        neuron_id=neuron_id,
        a=kwargs.get("a", params[0]),
        b=kwargs.get("b", params[1]),
        c=kwargs.get("c", params[2]),
        d=kwargs.get("d", params[3]),
        v=kwargs.get("v", -65.0),
        u=kwargs.get("u", -13.0),
        energy=kwargs.get("energy", 1.0),
        spike_cost=kwargs.get("spike_cost", 0.001),
        spike_counter=kwargs.get("spike_counter", 0),
        last_spike_tick=kwargs.get("last_spike_tick", -1),
        threshold_adaptation=kwargs.get("threshold_adaptation", 0.0),
        neuron_type=neuron_type,
    )
    if config is not None:
        neuron.set_config(config)
    return neuron


def create_random_neuron(
    neuron_id: int,
    rng: Any,
    neuron_type: NeuronType | None = None,
) -> Neuron:
    """Create a neuron with random Izhikevich parameters.

    Args:
        neuron_id: Unique identifier for the neuron.
        rng: Random number generator with .uniform() and .choice() methods.
        neuron_type: Optional neuron type; if None, random type chosen.

    Returns:
        A new Neuron instance with randomized parameters.

    Example:
        >>> import random
        >>> rng = random.Random(42)
        >>> neuron = create_random_neuron(42, rng)
    """
    if neuron_type is None:
        neuron_type = rng.choice(list(NeuronType))

    # Help Pylance understand that neuron_type is not None
    assert neuron_type is not None

    params = neuron_type.default_params
    # Add small random perturbations
    a = params[0] * (1.0 + rng.uniform(-0.1, 0.1))
    b = params[1] * (1.0 + rng.uniform(-0.1, 0.1))
    c = params[2] + rng.uniform(-5.0, 5.0)
    d = params[3] + rng.uniform(-1.0, 1.0)
    # Ensure parameters stay in reasonable ranges
    a = max(0.01, min(0.2, a))
    b = max(0.1, min(0.5, b))
    c = max(-80.0, min(-40.0, c))
    d = max(1.0, min(15.0, d))

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


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "Neuron",
    "NeuronConfig",
    "NeuronType",
    "create_neuron",
    "create_random_neuron",
]
