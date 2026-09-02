"""Typed data contracts for the Brain-5D embodiment layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class EnvironmentKind(StrEnum):
    """Supported environment categories."""

    SIMULATED = "simulated"
    PHYSICAL = "physical"
    DIGITAL = "digital"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class SensorFrame:
    """One timestamped sensor observation."""

    sensor_id: str
    tick: int
    modality: str
    payload: JSONValue


@dataclass(frozen=True, slots=True)
class ActionCommand:
    """One typed command produced for an actuator or environment."""

    actuator_id: str
    tick: int
    action: str
    payload: JSONValue = None


@dataclass(frozen=True, slots=True)
class ActuatorResult:
    """Result returned by one actuator invocation."""

    accepted: bool
    message: str = ""


@dataclass(frozen=True, slots=True)
class EnvironmentObservation:
    """Observation returned by an environment after reset or action."""

    tick: int
    state: dict[str, JSONValue]
    reward: float = 0.0
    terminated: bool = False
    truncated: bool = False


@dataclass(frozen=True, slots=True)
class EmbodimentMetrics:
    """Read-only operating metrics for dashboard publication."""

    environment_kind: str = "unconfigured"
    active_sensors: int = 0
    active_actuators: int = 0
    episode: int = 0
    episode_reward: float = 0.0
    last_reward: float = 0.0
    last_action: str = ""
    last_text_input: str = ""
    last_observation_state: dict[str, JSONValue] | None = None
    last_observation_tick: int | None = None
    last_observation_terminated: bool | None = None
    last_observation_truncated: bool | None = None

    def to_json(self) -> dict[str, JSONValue]:
        """Return a JSON-ready representation."""

        return {
            "environment_kind": self.environment_kind,
            "active_sensors": self.active_sensors,
            "active_actuators": self.active_actuators,
            "episode": self.episode,
            "episode_reward": self.episode_reward,
            "last_reward": self.last_reward,
            "last_action": self.last_action,
            "last_text_input": self.last_text_input,
            "last_observation_state": self.last_observation_state,
            "last_observation_tick": self.last_observation_tick,
            "last_observation_terminated": self.last_observation_terminated,
            "last_observation_truncated": self.last_observation_truncated,
        }
