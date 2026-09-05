"""Synapse data model with STDP eligibility and plasticity support.

This module defines the Synapse class, which represents a connection between
two neurons in the Brain-5D network. It supports:
- Weighted synaptic transmission with configurable delay
- Spike-Timing-Dependent Plasticity (STDP) eligibility traces
- Pair-based and triplet STDP variants
- Weight bounds and normalization
- Metaplasticity state tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# ============================================================================
# STDP Constants (Default values from Song & Abbott 2000)
# ============================================================================

A_PLUS: float = 0.1  # LTP amplitude
A_MINUS: float = 0.12  # LTD amplitude
TAU_PLUS: float = 20.0  # LTP time constant (ms)
TAU_MINUS: float = 20.0  # LTD time constant (ms)
W_MIN: float = 0.0  # Minimum weight
W_MAX: float = 1.0  # Maximum weight
ELIGIBILITY_DECAY: float = 0.95  # Eligibility trace decay per tick


# ============================================================================
# Synapse Configuration
# ============================================================================


@dataclass(frozen=True, slots=True)
class SynapseConfig:
    """Configuration parameters for synaptic plasticity."""

    a_plus: float = A_PLUS
    a_minus: float = A_MINUS
    tau_plus: float = TAU_PLUS
    tau_minus: float = TAU_MINUS
    w_min: float = W_MIN
    w_max: float = W_MAX
    eligibility_decay: float = ELIGIBILITY_DECAY
    enable_triplet: bool = False  # Triplet STDP (requires additional traces)
    enable_metaplasticity: bool = False


# ============================================================================
# Synapse Class
# ============================================================================


@dataclass(slots=True)
class Synapse:
    """A synaptic connection between two neurons with STDP plasticity.

    Attributes:
        target_id: ID of the postsynaptic neuron.
        weight: Synaptic weight (connection strength).
        delay: Transmission delay in ticks (>= 1).
        eligibility: STDP eligibility trace value.
        last_pre_spike: Tick of the last presynaptic spike.
        last_post_spike: Tick of the last postsynaptic spike.
        pre_trace: Presynaptic trace for triplet STDP (if enabled).
        post_trace: Postsynaptic trace for triplet STDP (if enabled).
        meta_state: Metaplasticity state (if enabled).
        update_count: Number of plasticity updates applied.
        created_tick: Tick when this synapse was created.
    """

    # === Core fields ===
    target_id: int
    weight: float
    delay: int

    # === STDP Eligibility ===
    eligibility: float = 0.0

    # === Spike timing traces (for pair-based STDP) ===
    last_pre_spike: int = -1
    last_post_spike: int = -1

    # === Triplet STDP traces (optional) ===
    pre_trace: float = 0.0  # Presynaptic trace for triplet
    post_trace: float = 0.0  # Postsynaptic trace for triplet

    # === Metaplasticity (optional) ===
    meta_state: float = 0.5  # Metaplasticity state (0.0 - 1.0)

    # === Statistics ===
    update_count: int = 0
    created_tick: int = 0

    # === Internal state ===
    _config: SynapseConfig | None = field(default=None, repr=False, init=False)
    _enabled: bool = field(default=True, repr=False, init=False)
    _dirty_callback: Callable[[], None] | None = field(
        default=None, repr=False, init=False
    )

    def set_dirty_callback(self, callback: Callable[[], None] | None) -> None:
        """Attach the runtime callback used to publish state mutations."""
        self._dirty_callback = callback

    def mark_dirty(self) -> None:
        """Publish a mutation to an attached runtime observer."""
        if self._dirty_callback is not None:
            self._dirty_callback()

    def __post_init__(self) -> None:
        """Validate synapse parameters after initialization."""
        if self.delay < 1:
            raise ValueError(f"Delay must be >= 1, got {self.delay}")

        if self.weight < 0.0:
            raise ValueError(f"Weight must be >= 0, got {self.weight}")

        if self.eligibility < 0.0:
            raise ValueError(f"Eligibility must be >= 0, got {self.eligibility}")

        # Set default config if not provided
        if self._config is None:
            self._config = SynapseConfig()

    # ========================================================================
    # Configuration
    # ========================================================================

    @property
    def config(self) -> SynapseConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = SynapseConfig()
        return self._config

    def set_config(self, config: SynapseConfig) -> None:
        """Set the configuration for this synapse."""
        self._config = config

    # ========================================================================
    # STDP Eligibility Updates
    # ========================================================================

    def update_eligibility(self, _tick: int) -> None:
        """Decay the eligibility trace at each tick."""
        if self._enabled:
            decay = self.config.eligibility_decay
            self.eligibility *= decay
            self.mark_dirty()

    def record_pre_spike(self, tick: int) -> None:
        """Record a presynaptic spike for STDP."""
        self.last_pre_spike = tick
        # For triplet STDP: update pre_trace
        if self.config.enable_triplet:
            self.pre_trace = 1.0
        self.mark_dirty()

    def record_post_spike(self, tick: int) -> None:
        """Record a postsynaptic spike for STDP."""
        self.last_post_spike = tick
        # For triplet STDP: update post_trace
        if self.config.enable_triplet:
            self.post_trace = 1.0
        self.mark_dirty()

    def decay_traces(self) -> None:
        """Decay triplet STDP traces."""
        if self.config.enable_triplet:
            tau_pre = self.config.tau_plus
            tau_post = self.config.tau_minus
            # Simplified decay per tick
            self.pre_trace *= (1.0 - 1.0 / tau_pre) if tau_pre > 0 else 1.0
            self.post_trace *= (1.0 - 1.0 / tau_post) if tau_post > 0 else 1.0

    # ========================================================================
    # STDP Weight Update
    # ========================================================================

    def compute_stdp_update(self, dt: float) -> float:
        """Compute the STDP weight change based on timing difference.

        Args:
            dt: Time difference (post - pre) in ticks/ms.

        Returns:
            Weight change (delta_w).
        """
        if dt == 0.0 or abs(dt) > 100.0:
            return 0.0

        config = self.config

        if dt > 0:
            # LTP: post fires after pre
            delta = config.a_plus * (1.0 - self.meta_state) * self.eligibility
            delta *= self._weight_scale()
            return delta
        else:
            # LTD: post fires before pre
            delta = -config.a_minus * self.meta_state * self.eligibility
            delta *= self._weight_scale()
            return delta

    def _weight_scale(self) -> float:
        """Scale factor based on current weight (soft bounds)."""
        w = self.weight
        w_min = self.config.w_min
        w_max = self.config.w_max
        range_w = w_max - w_min

        if range_w <= 0.0:
            return 1.0

        # Soft bounds: scale LTP down near max, LTD down near min
        scale_plus = (w_max - w) / range_w if w < w_max else 0.0
        scale_minus = (w - w_min) / range_w if w > w_min else 0.0

        return scale_plus if w < w_max else scale_minus

    def apply_stdp(self, dt: float) -> float:
        """Apply STDP weight update based on timing difference.

        Args:
            dt: Time difference (post - pre) in ticks/ms.

        Returns:
            The actual weight change applied.
        """
        if not self._enabled:
            return 0.0

        delta = self.compute_stdp_update(dt)

        if delta != 0.0:
            new_weight = self.weight + delta
            # Clip to bounds
            new_weight = max(self.config.w_min, min(self.config.w_max, new_weight))
            delta = new_weight - self.weight
            self.weight = new_weight
            self.update_count += 1
            # Apply metaplasticity if enabled
            if self.config.enable_metaplasticity:
                self._update_meta_state(delta)

            # Reset eligibility after application
            self.eligibility = 0.0

        return delta

    def _update_meta_state(self, delta: float) -> None:
        """Update metaplasticity state based on weight change."""
        # Simple metaplasticity: state moves toward 0.5 with change
        # Positive delta (LTP) decreases meta_state (makes LTD easier)
        # Negative delta (LTD) increases meta_state (makes LTP easier)
        learning_rate = 0.01
        self.meta_state += learning_rate * (-delta)
        self.meta_state = max(0.0, min(1.0, self.meta_state))

    # ========================================================================
    # Reward-Modulated Plasticity
    # ========================================================================

    def compute_reward_update(self, reward: float) -> float:
        """Compute reward-modulated weight change.

        Args:
            reward: Global reward signal (positive = good, negative = bad).

        Returns:
            Weight change (delta_w).
        """
        if not self._enabled or reward == 0.0:
            return 0.0

        # Reward-modulated STDP: weight change based on eligibility trace
        # and reward signal
        delta = reward * self.eligibility * 0.01

        # Apply weight bounds
        new_weight = self.weight + delta
        new_weight = max(self.config.w_min, min(self.config.w_max, new_weight))
        delta = new_weight - self.weight
        self.weight = new_weight
        self.mark_dirty()

        if delta != 0.0:
            self.update_count += 1
            # Reset eligibility after application
            self.eligibility = 0.0

        return delta

    # ========================================================================
    # State Management
    # ========================================================================

    def enable(self) -> None:
        """Enable plasticity for this synapse."""
        self._enabled = True

    def disable(self) -> None:
        """Disable plasticity for this synapse."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if plasticity is enabled for this synapse."""
        return self._enabled

    def reset_traces(self) -> None:
        """Reset all trace values."""
        self.eligibility = 0.0
        self.pre_trace = 0.0
        self.post_trace = 0.0
        self.last_pre_spike = -1
        self.last_post_spike = -1

    def copy(self) -> Synapse:
        """Create a copy of this synapse."""
        synapse = Synapse(
            target_id=self.target_id,
            weight=self.weight,
            delay=self.delay,
            eligibility=self.eligibility,
            last_pre_spike=self.last_pre_spike,
            last_post_spike=self.last_post_spike,
            pre_trace=self.pre_trace,
            post_trace=self.post_trace,
            meta_state=self.meta_state,
            update_count=self.update_count,
            created_tick=self.created_tick,
        )
        # Copy configuration (if set)
        if self._config is not None:
            synapse._config = self._config
        return synapse

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize synapse to dictionary."""
        return {
            "target_id": self.target_id,
            "weight": self.weight,
            "delay": self.delay,
            "eligibility": self.eligibility,
            "last_pre_spike": self.last_pre_spike,
            "last_post_spike": self.last_post_spike,
            "update_count": self.update_count,
            "created_tick": self.created_tick,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Synapse:
        """Deserialize synapse from dictionary."""
        return cls(
            target_id=data["target_id"],
            weight=data["weight"],
            delay=data["delay"],
            eligibility=data.get("eligibility", 0.0),
            last_pre_spike=data.get("last_pre_spike", -1),
            last_post_spike=data.get("last_post_spike", -1),
            update_count=data.get("update_count", 0),
            created_tick=data.get("created_tick", 0),
        )

    # ========================================================================
    # String Representation
    # ========================================================================

    def __str__(self) -> str:
        return (
            f"Synapse(target={self.target_id}, "
            f"weight={self.weight:.4f}, "
            f"delay={self.delay}, "
            f"eligibility={self.eligibility:.4f}, "
            f"updates={self.update_count})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ============================================================================
# Factory Functions
# ============================================================================


def create_synapse(
    target_id: int,
    weight: float = 0.5,
    delay: int = 1,
    config: SynapseConfig | None = None,
) -> Synapse:
    """Create a new synapse with default configuration.

    Args:
        target_id: ID of the postsynaptic neuron.
        weight: Initial synaptic weight (0.0 - 1.0).
        delay: Transmission delay in ticks (>= 1).
        config: Optional custom configuration.

    Returns:
        A new Synapse instance.
    """
    lower_bound = config.w_min if config is not None else 0.0
    upper_bound = config.w_max if config is not None else 1.0
    synapse = Synapse(
        target_id=target_id,
        weight=max(lower_bound, min(upper_bound, weight)),
        delay=max(1, delay),
    )
    if config is not None:
        synapse.set_config(config)
    return synapse


def create_random_synapse(
    target_id: int,
    rng: Any,
    weight_range: tuple[float, float] = (0.0, 1.0),
    delay_range: tuple[int, int] = (1, 5),
) -> Synapse:
    """Create a synapse with random weight and delay.

    Args:
        target_id: ID of the postsynaptic neuron.
        rng: Random number generator with .uniform() and .randint() methods.
        weight_range: (min, max) weight range.
        delay_range: (min, max) delay range.

    Returns:
        A new Synapse instance with random parameters.
    """
    weight = rng.uniform(weight_range[0], weight_range[1])
    delay = rng.randint(delay_range[0], delay_range[1])
    return create_synapse(target_id, weight, delay)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "A_MINUS",
    "A_PLUS",
    "ELIGIBILITY_DECAY",
    "TAU_MINUS",
    "TAU_PLUS",
    "W_MAX",
    "W_MIN",
    "Synapse",
    "SynapseConfig",
    "create_random_synapse",
    "create_synapse",
]
