"""Configuration-driven composition for the controlled experience loop."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from src.embodiment import (
    ActionCommand,
    ActuatorResult,
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionStatus,
    ControlledEmbodimentAgent,
    DeterministicTargetEnvironment,
    RelationshipClass,
    SystemSensorAdapter,
    host_system_readings,
)
from src.experience.engine import ExperienceEngine
from src.learning.learning_engine import LearningEngine


@dataclass(slots=True)
class DeterministicActuator:
    """Actuator boundary for the fully controlled digital environment."""

    actuator_id: str = "target-actuator"
    active: bool = True

    def apply(self, command: ActionCommand) -> ActuatorResult:
        return ActuatorResult(True, command.action)


def _numeric(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _system_encoder(frame: Any) -> Mapping[int, float]:
    payload = frame.payload
    if not isinstance(payload, dict):
        return {}
    values = (
        _numeric(payload.get("cpu_percent")),
        _numeric(payload.get("memory_percent")),
        _numeric(payload.get("temperature_c")),
        1.0 if payload.get("network_up") is True else 0.0,
    )
    return {index: value / 100.0 for index, value in enumerate(values)}


def _controlled_decoder(result: Any, frame: Any) -> ActionCommand | None:
    spikes = getattr(result, "output_spike_ids", ())
    if not spikes:
        return None
    return ActionCommand("target-actuator", frame.tick, "right")


def build_experience_subsystem(
    config: Mapping[str, Any],
    network: Any,
    learning: LearningEngine | None,
) -> ExperienceEngine | None:
    """Build the configured experience subsystem, or return ``None`` disabled."""

    raw = config.get("experience", {})
    if not isinstance(raw, Mapping):
        raise TypeError("experience config must be a mapping")
    if not bool(raw.get("enabled", False)):
        return None

    sensor_config = raw.get("sensor", {})
    encoder_config = raw.get("encoder", {})
    decoder_config = raw.get("decoder", {})
    environment_config = raw.get("environment", {})
    for name, value in (
        ("experience.sensor", sensor_config),
        ("experience.encoder", encoder_config),
        ("experience.decoder", decoder_config),
        ("experience.environment", environment_config),
    ):
        if not isinstance(value, Mapping):
            raise TypeError(f"{name} config must be a mapping")

    if sensor_config.get("type", "system") != "system":
        raise ValueError("unsupported experience sensor type")
    provider_name = sensor_config.get("provider", "host")
    if provider_name == "host":
        provider = host_system_readings
    elif provider_name == "deterministic_trace":
        trace = sensor_config.get("trace")
        if not isinstance(trace, list):
            raise ValueError("deterministic_trace requires a list trace")

        def provider(tick: int) -> Mapping[str, Any]:
            if tick >= len(trace) or not isinstance(trace[tick], Mapping):
                raise ValueError("deterministic_trace has no mapping for this tick")
            return cast(Mapping[str, Any], trace[tick])

    else:
        raise ValueError("unknown experience sensor provider")

    if encoder_config.get("type", "system_v1") != "system_v1":
        raise ValueError("unknown experience encoder type")
    if decoder_config.get("type", "controlled_v1") != "controlled_v1":
        raise ValueError("unknown experience decoder type")
    if environment_config.get("type", "deterministic_target") != "deterministic_target":
        raise ValueError("unknown experience environment type")
    if learning is None:
        raise RuntimeError("enabled experience requires the learning engine")

    descriptor = ConnectionDescriptor(
        connection_id="target-actuator",
        name="Deterministic target actuator",
        kind=ConnectionKind.ACTUATOR,
        relationship=RelationshipClass.CONTROLLABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("right",),
        available=True,
        authorized=True,
        active=True,
    )
    embodiment = ControlledEmbodimentAgent(
        environment=DeterministicTargetEnvironment(),
        actuator=DeterministicActuator(),
        descriptor=descriptor,
    )
    embodiment.reset(seed=int(config.get("seed", 42)))
    return ExperienceEngine(
        sensor=SystemSensorAdapter(provider),
        network=network,
        encoder=_system_encoder,
        decoder=_controlled_decoder,
        embodiment=embodiment,
        learning=learning,
    )


__all__ = ["DeterministicActuator", "build_experience_subsystem"]
