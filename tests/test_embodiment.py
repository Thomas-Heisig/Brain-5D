"""Tests for the first-class embodiment architecture contracts."""

from dataclasses import dataclass

from src.embodiment import (
    ActionCommand,
    ActuatorResult,
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionManager,
    ConnectionStatus,
    EmbodimentAgent,
    EmbodimentRegistry,
    EnvironmentKind,
    EnvironmentObservation,
    RelationshipClass,
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
    assert metrics.last_observation_state == {"action": "advance"}
    assert metrics.last_observation_tick == 1
    assert metrics.last_observation_terminated is False


def test_connection_manager_discovers_without_authorizing_devices() -> None:
    manager = ConnectionManager(cache_seconds=60)
    connections = {item.connection_id: item for item in manager.snapshot(refresh=True)}

    assert connections["resource.compute"].available is True
    assert connections["resource.compute"].authorized is False
    assert connections["sensor.camera"].active is False
    assert connections["sensor.microphone"].active is False
    assert connections["network.internet"].relationship in {
        RelationshipClass.PERCEIVABLE,
        RelationshipClass.REACHABLE,
    }


def test_connection_manager_accepts_explicit_adapter_metadata() -> None:
    manager = ConnectionManager(cache_seconds=60)
    manager.register(
        ConnectionDescriptor(
            connection_id="sensor.lab-camera",
            name="Lab camera",
            kind=ConnectionKind.SENSOR,
            relationship=RelationshipClass.USABLE,
            status=ConnectionStatus.CONNECTED,
            capabilities=("frames",),
            permissions=("capture",),
            modalities=("vision",),
            available=True,
            authorized=True,
            active=True,
            latency_ms=12.5,
            hazard_level="medium",
            source="configured_adapter",
        )
    )

    item = next(
        entry
        for entry in manager.snapshot()
        if entry.connection_id == "sensor.lab-camera"
    )
    assert item.active is True
    assert item.permissions == ("capture",)
