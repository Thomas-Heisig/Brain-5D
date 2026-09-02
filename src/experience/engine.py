"""Experience Engine v0 for controlled learning-loop experiments."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from src.embodiment.controlled import ControlledEmbodimentAgent
from src.embodiment.models import ActionCommand, EnvironmentObservation, SensorFrame
from src.embodiment.sensor import SensorAdapter
from src.learning.learning_engine import LearningEngine

Encoder = Callable[[SensorFrame], Mapping[int, float]]
Decoder = Callable[[Any, SensorFrame], ActionCommand | None]


@dataclass(frozen=True, slots=True)
class ExperienceStep:
    """Immutable audit record for one perception-action-feedback cycle."""

    tick: int
    frame: SensorFrame
    action: ActionCommand | None
    observation: EnvironmentObservation | None
    reward: float


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
    last_step: ExperienceStep | None = None
    _pending_frame: SensorFrame | None = None

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        """Reset the controlled environment and clear the last cycle."""

        self.last_step = None
        self._pending_frame = None
        return self.embodiment.reset(seed)

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
        action = self.decoder(result, frame)
        if action is not None:
            observation = self.embodiment.step(action)
        reward = 0.0 if observation is None else observation.reward
        if self.learning is not None and observation is not None:
            self.learning.set_reward(reward, tick)
        record = ExperienceStep(tick, frame, action, observation, reward)
        self.last_step = record
        self._pending_frame = None
        return record

    def attach_runtime(self, runtime: Any) -> None:
        """Attach to a RuntimeController without taking ownership of ticks."""

        runtime.add_pre_hook(self.prepare)
        runtime.add_hook(self.complete)


__all__ = ["ExperienceEngine", "ExperienceStep"]
