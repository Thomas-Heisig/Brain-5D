"""Explicit perception-action-feedback orchestration for embodiment."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from .controlled import ControlledEmbodimentAgent
from .models import ActionCommand, EmbodimentMetrics, SensorFrame
from .sensor import SensorAdapter

Encoder = Callable[[SensorFrame], Mapping[int, float]]
Decoder = Callable[[Any, SensorFrame], ActionCommand | None]


@dataclass(slots=True)
class EmbodimentPipeline:
    """Connect one real sensor path to an existing network and safe actuator.

    The pipeline does not manufacture observations: the sensor, network,
    actuator and environment are injected by the caller and every feedback
    value comes from those components.
    """

    sensor: SensorAdapter
    network: Any
    encoder: Encoder
    decoder: Decoder
    controller: ControlledEmbodimentAgent
    last_frame: SensorFrame | None = None
    stage_enabled: dict[str, bool] = field(
        default_factory=lambda: {
            "sensor": True,
            "encoder": True,
            "snn": True,
            "decoder": True,
            "actuator": True,
            "feedback": True,
        }
    )

    def set_stage_enabled(self, stage: str, enabled: bool) -> None:
        """Update one pipeline stage, rejecting unknown stages."""
        if stage not in self.stage_enabled:
            raise ValueError(f"unknown embodiment pipeline stage: {stage}")
        self.stage_enabled[stage] = enabled

    def reset(self, seed: int | None = None) -> None:
        """Reset the environment before processing a new episode."""
        self.controller.reset(seed)

    def step(self, tick: int) -> tuple[SensorFrame | None, Any, ActionCommand | None]:
        """Process one complete input, action and feedback cycle."""
        if not self.stage_enabled["sensor"]:
            return None, None, None
        frame = self.sensor.sample(tick)
        self.last_frame = frame
        if not self.stage_enabled["encoder"]:
            return frame, None, None
        self.network.inject_current_batch(dict(self.encoder(frame)))
        if not self.stage_enabled["snn"]:
            return frame, None, None
        result = self.network.step()
        if not self.stage_enabled["decoder"]:
            return frame, result, None
        action = self.decoder(result, frame)
        if (
            action is not None
            and self.stage_enabled["actuator"]
            and self.stage_enabled["feedback"]
        ):
            self.controller.step(action)
        return frame, result, action

    def metrics(self) -> EmbodimentMetrics:
        """Return metrics backed by the controlled environment observation."""
        metrics = self.controller.metrics()
        return replace(
            metrics,
            active_sensors=1 if self.sensor.active else 0,
            last_text_input=(
                self.last_frame.payload
                if self.last_frame is not None
                and isinstance(self.last_frame.payload, str)
                else metrics.last_text_input
            ),
        )
