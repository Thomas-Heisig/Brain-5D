"""Optional plasticity layer for Brain 5D.

Sprint 2C extends the Sprint 2B nearest-neighbour STDP/eligibility layer with
reward-modulated three-factor learning. The engine remains outside ``src.core``
and observes completed core steps through the generic post-step hook.

This module provides the LearningEngine class, which implements:
- Pair-based STDP with nearest-neighbour pairing
- Eligibility traces for reward-modulated learning
- Three-factor (reward-modulated) plasticity
- Configurable parameters via LearningParameters

Design Principles:
1. The engine is optional and can be enabled/disabled via configuration.
2. It observes the network via post-step hooks, never owning the runtime loop.
3. All plasticity is bounded (weights clamped to [min_weight, max_weight]).
4. Rewards can be delayed and are applied when due.

Example:
    >>> from src.learning import LearningEngine
    >>> engine = LearningEngine(network, config)
    >>> engine.attach()
    >>> # ... run simulation ...
    >>> stats = engine.stats
    >>> print(f"STDP updates: {stats.stdp_weight_updates}")
    >>> engine.detach()
"""

from __future__ import annotations

import math
import time
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, cast

from .eligibility import EligibilityTrace
from .reward import RewardSignal

if TYPE_CHECKING:
    from src.core.network import NeuralNetwork, StepResult
    from src.core.synapse import Synapse

Config = Mapping[str, Any]


def _as_mapping(value: Any, name: str) -> Mapping[str, Any]:
    """Validate and cast a config subsection to a typed mapping."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} config must be a mapping")
    return cast("Mapping[str, Any]", value)


# ============================================================================
# Learning Parameters
# ============================================================================


@dataclass(frozen=True, slots=True)
class LearningParameters:
    """Validated plasticity parameters loaded from configuration.

    This parameter bundle controls all aspects of the learning engine:
    - STDP: amplitudes, time constants, weight bounds
    - Eligibility: trace decay time constant
    - Reward: learning rate, delay, clamping behavior

    Attributes:
        stdp_enabled: Whether STDP is enabled.
        a_plus: LTP amplitude.
        a_minus: LTD amplitude.
        tau_plus: LTP time constant (ticks).
        tau_minus: LTD time constant (ticks).
        min_weight: Minimum weight (clamping lower bound).
        max_weight: Maximum weight (clamping upper bound).
        eligibility_enabled: Whether eligibility traces are enabled.
        eligibility_tau_ticks: Eligibility trace decay time constant (ticks).
        reward_enabled: Whether reward-modulated plasticity is enabled.
        reward_learning_rate: Learning rate for reward-modulated updates.
        reward_delay_ticks: Delay before rewards are applied.
        reward_clamp_weights: Whether to clamp weights after reward updates.
        reward_reset_trace: Whether to reset eligibility after reward application.
        reward_trace_epsilon: Minimum trace value to consider for updates.
    """

    stdp_enabled: bool = False
    a_plus: float = 0.1
    a_minus: float = 0.12
    tau_plus: float = 20.0
    tau_minus: float = 20.0
    min_weight: float = 0.0
    max_weight: float = 1.0
    eligibility_enabled: bool = False
    eligibility_tau_ticks: float = 200.0
    reward_enabled: bool = False
    reward_learning_rate: float = 0.01
    reward_delay_ticks: int = 0
    reward_clamp_weights: bool = True
    reward_reset_trace: bool = False
    reward_trace_epsilon: float = 1e-12

    @classmethod
    def from_config(cls, config: Config) -> LearningParameters:
        """Build and validate learning parameters from a config mapping.

        Args:
            config: Configuration dictionary containing 'stdp', 'eligibility',
                and 'reward' sections.

        Returns:
            Validated LearningParameters instance.

        Raises:
            TypeError: If any section is not a mapping.
            ValueError: If any parameter is invalid.
        """
        stdp = _as_mapping(config.get("stdp", {}), "stdp")
        eligibility = _as_mapping(config.get("eligibility", {}), "eligibility")
        reward = _as_mapping(config.get("reward", {}), "reward")

        params = cls(
            stdp_enabled=bool(stdp.get("enabled", False)),
            a_plus=float(stdp.get("a_plus", 0.1)),
            a_minus=float(stdp.get("a_minus", 0.12)),
            tau_plus=float(stdp.get("tau_plus", 20.0)),
            tau_minus=float(stdp.get("tau_minus", 20.0)),
            min_weight=float(stdp.get("min_weight", 0.0)),
            max_weight=float(stdp.get("max_weight", 1.0)),
            eligibility_enabled=bool(eligibility.get("enabled", False)),
            eligibility_tau_ticks=float(eligibility.get("tau_ticks", 200.0)),
            reward_enabled=bool(reward.get("enabled", False)),
            reward_learning_rate=float(reward.get("learning_rate", 0.01)),
            reward_delay_ticks=int(reward.get("delay_ticks", 0)),
            reward_clamp_weights=bool(reward.get("clamp_weights", True)),
            reward_reset_trace=bool(reward.get("reset_trace_after_reward", False)),
            reward_trace_epsilon=float(reward.get("trace_epsilon", 1e-12)),
        )
        params.validate()
        return params

    def validate(self) -> None:
        """Raise ValueError for invalid plasticity parameters."""
        # Non-negative values
        non_negative = {
            "stdp.a_plus": self.a_plus,
            "stdp.a_minus": self.a_minus,
            "reward.learning_rate": self.reward_learning_rate,
            "reward.trace_epsilon": self.reward_trace_epsilon,
        }
        for name, value in non_negative.items():
            if value < 0.0 or not math.isfinite(value):
                raise ValueError(f"{name} must be finite and >= 0")

        # Positive time constants
        if self.tau_plus <= 0.0 or not math.isfinite(self.tau_plus):
            raise ValueError("stdp.tau_plus must be finite and > 0")
        if self.tau_minus <= 0.0 or not math.isfinite(self.tau_minus):
            raise ValueError("stdp.tau_minus must be finite and > 0")
        if self.eligibility_tau_ticks <= 0.0 or not math.isfinite(
            self.eligibility_tau_ticks
        ):
            raise ValueError("eligibility.tau_ticks must be finite and > 0")

        # Weight bounds
        if self.min_weight > self.max_weight:
            raise ValueError("stdp.min_weight must be <= stdp.max_weight")

        # Reward delay
        if self.reward_delay_ticks < 0:
            raise ValueError("reward.delay_ticks must be >= 0")

        # Reward requires eligibility
        if self.reward_enabled and not self.eligibility_enabled:
            raise ValueError("reward learning requires eligibility.enabled=true")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


# ============================================================================
# Learning State
# ============================================================================


@dataclass(slots=True)
class _SynapseLearningState:
    """State for a single synapse tracked by the learning engine.

    Attributes:
        pre_id: ID of the presynaptic neuron.
        synapse: Reference to the Synapse object.
        last_pre_tick: Tick of the last presynaptic spike, or None.
        last_post_tick: Tick of the last postsynaptic spike, or None.
        eligibility: Eligibility trace for reward-modulated learning.
    """

    pre_id: int
    synapse: Synapse
    last_pre_tick: int | None = None
    last_post_tick: int | None = None
    eligibility: EligibilityTrace = field(default_factory=EligibilityTrace)


@dataclass(slots=True)
class _SynapseTickEvent:
    """Spike event for a synapse in a single tick.

    Attributes:
        pre_id: ID of the presynaptic neuron.
        synapse: Reference to the Synapse object.
        pre_spiked: Whether the presynaptic neuron spiked this tick.
        post_spiked: Whether the postsynaptic neuron spiked this tick.
    """

    pre_id: int
    synapse: Synapse
    pre_spiked: bool = False
    post_spiked: bool = False


# ============================================================================
# Learning Statistics
# ============================================================================


@dataclass(frozen=True, slots=True)
class LearningStats:
    """Runtime statistics for the optional learning layer.

    Attributes:
        updates: Total number of update calls.
        stdp_weight_updates: Number of STDP weight updates applied.
        reward_weight_updates: Number of reward-modulated weight updates applied.
        rewards_received: Number of rewards received.
        rewards_applied: Number of rewards applied.
        pending_rewards: Number of rewards currently pending (delayed).
        last_update_ms: Time taken for the last update in milliseconds.
        total_update_ms: Total time spent on updates in milliseconds.
    """

    updates: int
    stdp_weight_updates: int
    reward_weight_updates: int
    rewards_received: int
    rewards_applied: int
    pending_rewards: int
    last_update_ms: float
    total_update_ms: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "updates": self.updates,
            "stdp_weight_updates": self.stdp_weight_updates,
            "reward_weight_updates": self.reward_weight_updates,
            "rewards_received": self.rewards_received,
            "rewards_applied": self.rewards_applied,
            "pending_rewards": self.pending_rewards,
            "last_update_ms": self.last_update_ms,
            "total_update_ms": self.total_update_ms,
        }


# ============================================================================
# Learning Engine
# ============================================================================


class LearningEngine:
    """Nearest-neighbour STDP, eligibility and reward-modulated plasticity.

    This engine implements the complete learning pipeline:
    1. STDP: Pair-based, nearest-neighbour with configurable amplitudes and time constants
    2. Eligibility: Trace accumulation for reward-modulated learning
    3. Reward-modulated plasticity: Three-factor learning with delayed rewards

    The engine observes the network via post-step hooks and applies updates
    after each completed tick. It maintains state for each synapse and
    automatically refreshes its topology when the network changes.

    Example:
        >>> engine = LearningEngine(network, config)
        >>> engine.attach()
        >>> # Run simulation...
        >>> stats = engine.stats
        >>> print(f"STDP updates: {stats.stdp_weight_updates}")
        >>> engine.detach()
    """

    def __init__(self, network: NeuralNetwork, config: Config) -> None:
        """Initialize the learning engine.

        Args:
            network: The neural network to observe and modify.
            config: Configuration dictionary with learning parameters.

        Raises:
            TypeError: If configuration sections are invalid.
            ValueError: If parameters are invalid.
        """
        self.network = network
        self.params = LearningParameters.from_config(config)
        # Stable synapse identity: (pre_id, target_id) tuple.
        # This is deterministic across process restarts, unlike id(synapse)
        # which depends on Python object memory addresses (ASLR).
        self._states: dict[tuple[int, int], _SynapseLearningState] = {}
        self._incoming: dict[int, list[tuple[int, Synapse]]] = {}
        self._known_synapse_count = -1
        self._pending_rewards: list[RewardSignal] = []
        self._attached = False
        self._updates = 0
        self._stdp_weight_updates = 0
        self._reward_weight_updates = 0
        self._rewards_received = 0
        self._rewards_applied = 0
        self._last_update_ms = 0.0
        self._total_update_ms = 0.0
        self.refresh_topology()

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def enabled(self) -> bool:
        """Return whether any plasticity component is active."""
        return (
            self.params.stdp_enabled
            or self.params.eligibility_enabled
            or self.params.reward_enabled
        )

    @property
    def stats(self) -> LearningStats:
        """Return an immutable snapshot of learning runtime statistics."""
        return LearningStats(
            updates=self._updates,
            stdp_weight_updates=self._stdp_weight_updates,
            reward_weight_updates=self._reward_weight_updates,
            rewards_received=self._rewards_received,
            rewards_applied=self._rewards_applied,
            pending_rewards=len(self._pending_rewards),
            last_update_ms=self._last_update_ms,
            total_update_ms=self._total_update_ms,
        )

    @property
    def is_attached(self) -> bool:
        """Return whether the engine is attached to the network."""
        return self._attached

    # ========================================================================
    # Lifecycle Management
    # ========================================================================

    def attach(self) -> None:
        """Register this engine on the network's generic post-step hook."""
        if not self._attached:
            self.network.add_post_step_hook(self.update)
            self._attached = True

    def detach(self) -> None:
        """Detach the engine from the network hook."""
        if self._attached:
            self.network.remove_post_step_hook(self.update)
            self._attached = False

    def refresh_topology(self) -> None:
        """Rebuild indexes while preserving state of still-live synapses.

        Uses stable (pre_id, target_id) keys instead of id(synapse) so that
        learning state survives process-restart restore. Parallel synapses
        (disabled in production config) are disambiguated by index.
        """
        incoming: dict[int, list[tuple[int, Synapse]]] = {}
        live_keys: set[tuple[int, int]] = set()

        for pre_id, synapses in self.network.synapses.items():
            for synapse in synapses:
                key = (pre_id, synapse.target_id)
                live_keys.add(key)
                incoming.setdefault(synapse.target_id, []).append((pre_id, synapse))

                if key not in self._states:
                    self._states[key] = _SynapseLearningState(
                        pre_id=pre_id,
                        synapse=synapse,
                        eligibility=EligibilityTrace(self.params.eligibility_tau_ticks),
                    )

        # Remove states for synapses that no longer exist
        self._states = {
            key: state for key, state in self._states.items() if key in live_keys
        }

        self._incoming = incoming
        self._known_synapse_count = self.network.synapse_count

    # ========================================================================
    # Core Update
    # ========================================================================

    def update(self, step_result: StepResult) -> None:
        """Observe one completed core tick and apply plasticity updates.

        This is called automatically by the network's post-step hook.

        Args:
            step_result: The result of the completed network step.
        """
        if not self.enabled:
            return

        start = time.perf_counter()

        # Refresh topology if synapses have changed
        if self.network.synapse_count != self._known_synapse_count:
            self.refresh_topology()

        tick = int(step_result.tick)
        # Use sorted() for deterministic iteration order — set iteration
        # is hash-based and non-deterministic across process restarts.
        spike_ids = sorted(set(step_result.spike_ids))

        if spike_ids:
            events: dict[tuple[int, int], _SynapseTickEvent] = {}

            # Collect presynaptic spikes
            for pre_id in spike_ids:
                for synapse in self.network.synapses.get(pre_id, ()):
                    key = (pre_id, synapse.target_id)
                    event = events.setdefault(
                        key,
                        _SynapseTickEvent(pre_id=pre_id, synapse=synapse),
                    )
                    event.pre_spiked = True

            # Collect postsynaptic spikes
            for post_id in spike_ids:
                for pre_id, synapse in self._incoming.get(post_id, ()):
                    key = (pre_id, synapse.target_id)
                    event = events.setdefault(
                        key,
                        _SynapseTickEvent(pre_id=pre_id, synapse=synapse),
                    )
                    event.post_spiked = True

            # Process each synapse event in deterministic order
            for key in sorted(events):
                event = events[key]
                self._process_synapse_event(event, tick)

        # Apply due rewards
        self._apply_due_rewards(tick)

        # Update statistics
        self._updates += 1
        self._last_update_ms = (time.perf_counter() - start) * 1000.0
        self._total_update_ms += self._last_update_ms

    # ========================================================================
    # Reward Management
    # ========================================================================

    def set_reward(self, value: float, tick: int) -> None:
        """Submit an external scalar reward.

        A zero-delay reward is applied immediately at ``tick`` so callers can
        reward the just-completed step. Delayed rewards are queued and applied
        by subsequent ``update`` calls when their due tick is reached.

        Args:
            value: The reward value (positive = reinforcement, negative = punishment).
            tick: The tick at which the reward is emitted.
        """
        if not self.params.reward_enabled:
            return

        reward = RewardSignal(value=float(value), tick=int(tick))
        self._rewards_received += 1

        if self.params.reward_delay_ticks == 0:
            self._apply_reward(reward, tick)
            return

        self._pending_rewards.append(reward)

    def reset_state(self) -> None:
        """Forget timing, eligibility and pending rewards without changing weights.

        This is useful for resetting the learning state between episodes
        while preserving the learned weights.
        """
        for key in sorted(self._states):
            state = self._states[key]
            state.last_pre_tick = None
            state.last_post_tick = None
            state.eligibility.reset()
        self._pending_rewards.clear()

    # ========================================================================
    # Query Methods
    # ========================================================================

    def get_eligibility(
        self,
        pre_id: int,
        post_id: int,
        tick: int | None = None,
    ) -> float:
        """Read the eligibility trace for one non-parallel connection.

        Args:
            pre_id: ID of the presynaptic neuron.
            post_id: ID of the postsynaptic neuron.
            tick: Tick to read the trace at (default: current tick).

        Returns:
            The eligibility trace value.

        Raises:
            KeyError: If no synapse exists between pre_id and post_id.
            ValueError: If multiple parallel synapses match the query.
        """
        matches = [
            synapse
            for synapse in self.network.synapses.get(pre_id, ())
            if synapse.target_id == post_id
        ]

        if not matches:
            raise KeyError(f"No synapse {pre_id}->{post_id}")
        if len(matches) > 1:
            raise ValueError("Multiple parallel synapses match; query is ambiguous")

        key = (pre_id, post_id)
        state = self._states[key]
        return state.eligibility.read(tick)

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _process_synapse_event(self, event: _SynapseTickEvent, tick: int) -> None:
        """Process a single synapse event with STDP and eligibility.

        Uses stable (pre_id, target_id) key instead of id(synapse) to
        ensure deterministic behaviour across process restarts.
        """
        key = (event.pre_id, event.synapse.target_id)
        state = self._states[key]
        raw_delta = 0.0

        # LTD: POST before PRE
        if event.pre_spiked and state.last_post_tick is not None:
            dt = state.last_post_tick - tick
            if dt < 0:
                raw_delta -= self.params.a_minus * math.exp(dt / self.params.tau_minus)

        # LTP: PRE before POST
        if event.post_spiked and state.last_pre_tick is not None:
            dt = tick - state.last_pre_tick
            if dt > 0:
                raw_delta += self.params.a_plus * math.exp(-dt / self.params.tau_plus)

        # Update eligibility
        if self.params.eligibility_enabled and raw_delta != 0.0:
            state.eligibility.add(raw_delta, tick)

        # Apply STDP weight change
        if self.params.stdp_enabled and raw_delta != 0.0:
            old_weight = event.synapse.weight
            event.synapse.weight = self._bounded_weight(old_weight + raw_delta)
            if event.synapse.weight != old_weight:
                self._stdp_weight_updates += 1

        # Update spike timing
        if event.pre_spiked:
            state.last_pre_tick = tick
        if event.post_spiked:
            state.last_post_tick = tick

    def _apply_due_rewards(self, tick: int) -> None:
        """Apply all rewards that are due at the current tick."""
        if not self.params.reward_enabled or not self._pending_rewards:
            return

        pending: list[RewardSignal] = []
        for reward in self._pending_rewards:
            if reward.is_due(tick, self.params.reward_delay_ticks):
                due_tick = reward.due_tick(self.params.reward_delay_ticks)
                self._apply_reward(reward, due_tick)
            else:
                pending.append(reward)

        self._pending_rewards = pending

    def _apply_reward(self, reward: RewardSignal, effective_tick: int) -> None:
        """Apply a reward to all synapses with non-zero eligibility."""
        changed = False

        for key in sorted(self._states):
            state = self._states[key]
            eligibility = state.eligibility.read(effective_tick)

            # Skip if eligibility is too small
            if abs(eligibility) <= self.params.reward_trace_epsilon:
                continue

            # Compute weight delta
            delta = self.params.reward_learning_rate * reward.value * eligibility

            # Apply weight change
            old_weight = state.synapse.weight
            candidate = old_weight + delta

            if self.params.reward_clamp_weights:
                candidate = self._bounded_weight(candidate)

            state.synapse.weight = candidate

            if candidate != old_weight:
                self._reward_weight_updates += 1
                changed = True

            # Reset trace if configured
            if self.params.reward_reset_trace:
                state.eligibility.reset()

        self._rewards_applied += 1
        _ = changed  # Keep linter happy

    def _bounded_weight(self, weight: float) -> float:
        """Clamp a weight to [min_weight, max_weight]."""
        return max(self.params.min_weight, min(self.params.max_weight, weight))

    # ========================================================================
    # String Representation
    # ========================================================================

    def __repr__(self) -> str:
        """Return a string representation of the learning engine."""
        return (
            f"LearningEngine(enabled={self.enabled}, "
            f"attached={self._attached}, "
            f"updates={self._updates}, "
            f"stdp_updates={self._stdp_weight_updates}, "
            f"reward_updates={self._reward_weight_updates})"
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "LearningEngine",
    "LearningParameters",
    "LearningStats",
    "RewardSignal",
]
