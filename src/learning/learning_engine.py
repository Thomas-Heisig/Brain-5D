"""Optional plasticity layer for Brain 5D.

Sprint 2C extends the Sprint 2B nearest-neighbour STDP/eligibility layer with
reward-modulated three-factor learning. The engine remains outside ``src.core``
and observes completed core steps through the generic post-step hook.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from .eligibility import EligibilityTrace
from .reward import RewardSignal

if TYPE_CHECKING:
    from src.core.network import NeuralNetwork, StepResult
    from src.core.synapse import Synapse

Config = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class LearningParameters:
    """Validated plasticity parameters loaded from configuration."""

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
    def from_config(cls, config: Config) -> "LearningParameters":
        """Build and validate learning parameters from a config mapping."""
        stdp = config.get("stdp", {})
        eligibility = config.get("eligibility", {})
        reward = config.get("reward", {})
        if not isinstance(stdp, Mapping):
            raise TypeError("stdp config must be a mapping")
        if not isinstance(eligibility, Mapping):
            raise TypeError("eligibility config must be a mapping")
        if not isinstance(reward, Mapping):
            raise TypeError("reward config must be a mapping")

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
        """Raise ``ValueError`` for invalid plasticity parameters."""
        non_negative = {
            "stdp.a_plus": self.a_plus,
            "stdp.a_minus": self.a_minus,
            "reward.learning_rate": self.reward_learning_rate,
            "reward.trace_epsilon": self.reward_trace_epsilon,
        }
        for name, value in non_negative.items():
            if value < 0.0 or not math.isfinite(value):
                raise ValueError(f"{name} must be finite and >= 0")
        if self.tau_plus <= 0.0 or not math.isfinite(self.tau_plus):
            raise ValueError("stdp.tau_plus must be finite and > 0")
        if self.tau_minus <= 0.0 or not math.isfinite(self.tau_minus):
            raise ValueError("stdp.tau_minus must be finite and > 0")
        if self.eligibility_tau_ticks <= 0.0 or not math.isfinite(
            self.eligibility_tau_ticks
        ):
            raise ValueError("eligibility.tau_ticks must be finite and > 0")
        if self.min_weight > self.max_weight:
            raise ValueError("stdp.min_weight must be <= stdp.max_weight")
        if self.reward_delay_ticks < 0:
            raise ValueError("reward.delay_ticks must be >= 0")
        if self.reward_enabled and not self.eligibility_enabled:
            raise ValueError("reward learning requires eligibility.enabled=true")


@dataclass(slots=True)
class _SynapseLearningState:
    pre_id: int
    synapse: "Synapse"
    last_pre_tick: int | None = None
    last_post_tick: int | None = None
    eligibility: EligibilityTrace = field(default_factory=EligibilityTrace)


@dataclass(slots=True)
class _SynapseTickEvent:
    pre_id: int
    synapse: "Synapse"
    pre_spiked: bool = False
    post_spiked: bool = False


@dataclass(frozen=True, slots=True)
class LearningStats:
    """Runtime statistics for the optional learning layer."""

    updates: int
    stdp_weight_updates: int
    reward_weight_updates: int
    rewards_received: int
    rewards_applied: int
    pending_rewards: int
    last_update_ms: float
    total_update_ms: float


class LearningEngine:
    """Nearest-neighbour STDP, eligibility and reward-modulated plasticity."""

    def __init__(self, network: "NeuralNetwork", config: Config):
        self.network = network
        self.params = LearningParameters.from_config(config)
        self._states: dict[int, _SynapseLearningState] = {}
        self._incoming: dict[int, list[tuple[int, "Synapse"]]] = {}
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
        """Rebuild indexes while preserving state of still-live synapses."""
        incoming: dict[int, list[tuple[int, "Synapse"]]] = {}
        live_ids: set[int] = set()
        for pre_id, synapses in self.network.synapses.items():
            for synapse in synapses:
                synapse_id = id(synapse)
                live_ids.add(synapse_id)
                incoming.setdefault(synapse.target_id, []).append((pre_id, synapse))
                if synapse_id not in self._states:
                    self._states[synapse_id] = _SynapseLearningState(
                        pre_id=pre_id,
                        synapse=synapse,
                        eligibility=EligibilityTrace(
                            self.params.eligibility_tau_ticks
                        ),
                    )
        self._states = {
            synapse_id: state
            for synapse_id, state in self._states.items()
            if synapse_id in live_ids
        }
        self._incoming = incoming
        self._known_synapse_count = self.network.synapse_count

    def update(self, step_result: "StepResult") -> None:
        """Observe one completed core tick and apply plasticity updates."""
        if not self.enabled:
            return

        start = time.perf_counter()
        if self.network.synapse_count != self._known_synapse_count:
            self.refresh_topology()

        tick = int(step_result.tick)
        spike_ids = set(step_result.spike_ids)
        if spike_ids:
            events: dict[int, _SynapseTickEvent] = {}
            for pre_id in spike_ids:
                for synapse in self.network.synapses.get(pre_id, ()):
                    synapse_id = id(synapse)
                    event = events.setdefault(
                        synapse_id,
                        _SynapseTickEvent(pre_id=pre_id, synapse=synapse),
                    )
                    event.pre_spiked = True

            for post_id in spike_ids:
                for pre_id, synapse in self._incoming.get(post_id, ()):
                    synapse_id = id(synapse)
                    event = events.setdefault(
                        synapse_id,
                        _SynapseTickEvent(pre_id=pre_id, synapse=synapse),
                    )
                    event.post_spiked = True

            for event in events.values():
                self._process_synapse_event(event, tick)

        self._apply_due_rewards(tick)
        self._updates += 1
        self._last_update_ms = (time.perf_counter() - start) * 1000.0
        self._total_update_ms += self._last_update_ms

    def set_reward(self, value: float, tick: int) -> None:
        """Submit an external scalar reward.

        A zero-delay reward is applied immediately at ``tick`` so callers can
        reward the just-completed step. Delayed rewards are queued and applied
        by subsequent ``update`` calls when their due tick is reached.
        """
        if not self.params.reward_enabled:
            return
        reward = RewardSignal(value=float(value), tick=int(tick))
        self._rewards_received += 1
        if self.params.reward_delay_ticks == 0:
            self._apply_reward(reward, tick)
            return
        self._pending_rewards.append(reward)

    def _process_synapse_event(self, event: _SynapseTickEvent, tick: int) -> None:
        state = self._states[id(event.synapse)]
        raw_delta = 0.0

        if event.pre_spiked and state.last_post_tick is not None:
            dt = state.last_post_tick - tick
            if dt < 0:
                raw_delta -= self.params.a_minus * math.exp(
                    dt / self.params.tau_minus
                )

        if event.post_spiked and state.last_pre_tick is not None:
            dt = tick - state.last_pre_tick
            if dt > 0:
                raw_delta += self.params.a_plus * math.exp(
                    -dt / self.params.tau_plus
                )

        if self.params.eligibility_enabled and raw_delta != 0.0:
            state.eligibility.add(raw_delta, tick)

        if self.params.stdp_enabled and raw_delta != 0.0:
            old_weight = event.synapse.weight
            event.synapse.weight = self._bounded_weight(old_weight + raw_delta)
            if event.synapse.weight != old_weight:
                self._stdp_weight_updates += 1

        if event.pre_spiked:
            state.last_pre_tick = tick
        if event.post_spiked:
            state.last_post_tick = tick

    def _apply_due_rewards(self, tick: int) -> None:
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
        changed = False
        for state in self._states.values():
            eligibility = state.eligibility.read(effective_tick)
            if abs(eligibility) <= self.params.reward_trace_epsilon:
                continue
            delta = self.params.reward_learning_rate * reward.value * eligibility
            old_weight = state.synapse.weight
            candidate = old_weight + delta
            if self.params.reward_clamp_weights:
                candidate = self._bounded_weight(candidate)
            state.synapse.weight = candidate
            if candidate != old_weight:
                self._reward_weight_updates += 1
                changed = True
            if self.params.reward_reset_trace:
                state.eligibility.reset()
        self._rewards_applied += 1
        _ = changed

    def _bounded_weight(self, weight: float) -> float:
        return max(self.params.min_weight, min(self.params.max_weight, weight))

    def get_eligibility(
        self, pre_id: int, post_id: int, tick: int | None = None
    ) -> float:
        """Read the eligibility trace for one non-parallel connection."""
        matches = [
            synapse
            for synapse in self.network.synapses.get(pre_id, ())
            if synapse.target_id == post_id
        ]
        if not matches:
            raise KeyError(f"No synapse {pre_id}->{post_id}")
        if len(matches) > 1:
            raise ValueError("Multiple parallel synapses match; query is ambiguous")
        state = self._states[id(matches[0])]
        return state.eligibility.read(tick)

    def reset_state(self) -> None:
        """Forget timing, eligibility and pending rewards without changing weights."""
        for state in self._states.values():
            state.last_pre_tick = None
            state.last_post_tick = None
            state.eligibility.reset()
        self._pending_rewards.clear()
