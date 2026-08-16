"""Tests for the first-class embodiment architecture contracts."""

from dataclasses import dataclass

from src.embodiment import (
    ActionCommand,
    ActuatorResult,
    EmbodimentAgent,
    EmbodimentRegistry,
    EnvironmentKind,
    EnvironmentObservation,
    SensorFrame,
)


@dataclass(slots=True)
class TextSensor:
    sensor_id: str = "text"
    modality: str = "text"
    active: bool = True

    def sample(self, tick: int) -> SensorFrame:
        return SensorFrame(self.sensor_id, tick, self.modality, "hello")


@dataclass(slots=True)
class TextActuator:
    actuator_id: str = "text-output"
    active: bool = True

    def apply(self, command: ActionCommand) -> ActuatorResult:
        return ActuatorResult(command.actuator_id == self.actuator_id, command.action)


@dataclass(slots=True)
class CounterEnvironment:
    environment_id: str = "counter"
    kind: EnvironmentKind = EnvironmentKind.SIMULATED
    tick: int = 0

    def reset(self, seed: int | None = None) -> EnvironmentObservation:
        self.tick = 0
        return EnvironmentObservation(0, {"seed": seed})

    def step(self, action: ActionCommand) -> EnvironmentObservation:
        self.tick += 1
        return EnvironmentObservation(
            self.tick,
            {"action": action.action},
            reward=0.5,
            terminated=self.tick >= 2,
        )


def test_registry_creates_typed_adapters() -> None:
    registry = EmbodimentRegistry()
    registry.register_sensor("text", TextSensor)
    registry.register_actuator("text", TextActuator)
    registry.register_environment("counter", CounterEnvironment)

    assert registry.create_sensor("text").sample(3).payload == "hello"
    actuator = registry.create_actuator("text")
    assert actuator.apply(ActionCommand("text-output", 3, "say")).accepted
    assert registry.create_environment("counter").kind is EnvironmentKind.SIMULATED


def test_agent_tracks_episode_feedback_without_autonomous_actions() -> None:
    agent = EmbodimentAgent(CounterEnvironment())
    initial = agent.reset(seed=42)
    assert initial.tick == 0
    observation = agent.step(ActionCommand("environment", 0, "advance"))
    metrics = agent.metrics()
    assert observation.reward == 0.5
    assert metrics.episode == 1
    assert metrics.episode_reward == 0.5
    assert metrics.last_action == "advance"
