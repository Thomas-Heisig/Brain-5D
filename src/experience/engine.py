"""Experience Engine v0 for controlled learning-loop experiments."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from src.embodiment.controlled import ControlledEmbodimentAgent
from src.embodiment.models import ActionCommand, EnvironmentObservation, SensorFrame
from src.embodiment.sensor import SensorAdapter
from src.embodiment.task_outcome import TaskOutcome, TaskOutcomeVerifier
from src.learning.learning_engine import LearningEngine
from src.memory import MemoryWorldModel
from src.profiles import BehaviorProfile

Encoder = Callable[[SensorFrame], Mapping[int, float]]
Decoder = Callable[[Any, SensorFrame], ActionCommand | tuple[ActionCommand, ...] | None]


@dataclass(frozen=True, slots=True)
class ExperienceStep:
    """Immutable audit record for one perception-action-feedback cycle."""

    tick: int
    frame: SensorFrame
    action: ActionCommand | None
    observation: EnvironmentObservation | None
    reward: float
    outcome: TaskOutcome | None = None


@dataclass(slots=True)
class ExperienceEngine:
    """Connect a controlled sensor loop to the real learning engine.

    Rewards are accepted only from environment observations. No language
    model, configuration value, or decoder output can write a reward.
    """

    sensor: SensorAdapter
    network: Any
    encoder: Encoder
    decoder: Decoder
    embodiment: ControlledEmbodimentAgent
    learning: LearningEngine | None = None
    outcome_verifier: TaskOutcomeVerifier = field(default_factory=TaskOutcomeVerifier)
    memory: MemoryWorldModel | None = None
    behavior_profile: BehaviorProfile | None = None
    last_step: ExperienceStep | None = None
    _pending_frame: SensorFrame | None = None
    _pending_prediction: Any = None

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        """Reset the controlled environment and clear the last cycle."""

        self.last_step = None
        self._pending_frame = None
        self._pending_prediction = None
        observation = self.embodiment.reset(seed)
        if self.memory is not None:
            self.memory.reset_episode(f"episode-{self.embodiment.episode}")
        return observation

    def step(self, tick: int) -> ExperienceStep:
        """Run one complete sensor, network, action, feedback and reward step."""

        self.prepare(tick)
        result = self.network.step()
        return self.complete(tick, result)

    def prepare(self, tick: int) -> SensorFrame:
        """Sample and encode input before an existing runtime tick."""

        if not self.sensor.active:
            raise RuntimeError("experience sensor is inactive")
        frame = self.sensor.sample(tick)
        self.network.inject_current_batch(dict(self.encoder(frame)))
        self._pending_frame = frame
        return frame

    def complete(self, tick: int, result: Any) -> ExperienceStep:
        """Decode feedback after an existing runtime tick has completed."""

        frame = self._pending_frame
        if frame is None or frame.tick != tick:
            raise RuntimeError("complete() requires a matching prepare() call")
        observation = None
        decoded = self.decoder(result, frame)
        action = (
            self.behavior_profile.select_action(decoded, tick=tick)
            if self.behavior_profile is not None and isinstance(decoded, tuple)
            else decoded
        )
        if self.memory is not None:
            self._pending_prediction = self.memory.predict(frame, action, tick)
        if action is not None:
            observation = self.embodiment.step(action)
        outcome = (
            TaskOutcome(False, False, 0.0, "no environment observation")
            if observation is None
            else self.outcome_verifier.verify(observation)
        )
        reward = outcome.reward
        if self.learning is not None and observation is not None:
            self.learning.set_reward(reward, tick)
        record = ExperienceStep(tick, frame, action, observation, reward, outcome)
        if self.memory is not None:
            self.memory.complete(
                frame, action, observation, tick, self._pending_prediction
            )
        if self.behavior_profile is not None and outcome is not None:
            self.behavior_profile.update(success=outcome.success, tick=tick)
        self.last_step = record
        self._pending_frame = None
        self._pending_prediction = None
        return record

    def attach_runtime(self, runtime: Any) -> None:
        """Attach to a RuntimeController without taking ownership of ticks."""

        runtime.add_pre_hook(self.prepare)
        runtime.add_hook(self.complete)


__all__ = ["ExperienceEngine", "ExperienceStep"]
