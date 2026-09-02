"""Scientific boundary tests for Experience Engine v0."""

from dataclasses import dataclass, field
from typing import Any, Callable, cast

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
from src.experience import ExperienceEngine


@dataclass
class Actuator:
    actuator_id: str = "target-actuator"
    active: bool = True

    def apply(self, command: ActionCommand) -> ActuatorResult:
        return ActuatorResult(True, command.action)


@dataclass
class Network:
    injected: list[dict[int, float]] = field(
        default_factory=lambda: list[dict[int, float]]()
    )

    def inject_current_batch(self, currents: dict[int, float]) -> None:
        self.injected.append(currents)

    def step(self) -> dict[str, tuple[int, ...]]:
        return {"output_spike_ids": (1,)}


@dataclass
class LearningSpy:
    rewards: list[tuple[float, int]] = field(
        default_factory=lambda: list[tuple[float, int]]()
    )

    def set_reward(self, value: float, tick: int) -> None:
        self.rewards.append((value, tick))


@dataclass
class RuntimeSpy:
    pre_hooks: list[Callable[[int], Any]] = field(
        default_factory=lambda: list[Callable[[int], Any]]()
    )
    post_hooks: list[Callable[[int, Any], Any]] = field(
        default_factory=lambda: list[Callable[[int, Any], Any]]()
    )

    def add_pre_hook(self, hook: Callable[..., Any]) -> None:
        self.pre_hooks.append(hook)

    def add_hook(self, hook: Callable[..., Any]) -> None:
        self.post_hooks.append(hook)


def _agent(*, authorized: bool = True) -> ControlledEmbodimentAgent:
    descriptor = ConnectionDescriptor(
        connection_id="target-actuator",
        name="Target actuator",
        kind=ConnectionKind.ACTUATOR,
        relationship=RelationshipClass.CONTROLLABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("right",),
        available=True,
        authorized=authorized,
        active=True,
    )
    agent = ControlledEmbodimentAgent(
        DeterministicTargetEnvironment(), Actuator(), descriptor
    )
    agent.reset(seed=42)
    return agent


def test_system_sensor_provider_is_reproducible() -> None:
    def readings(tick: int) -> dict[str, float]:
        return {"cpu_percent": float(tick), "memory_percent": 10.0}

    first = SystemSensorAdapter(readings)
    second = SystemSensorAdapter(readings)

    assert first.sample(4) == second.sample(4)


def test_host_system_provider_exposes_explicit_live_metrics() -> None:
    readings = host_system_readings(4)

    assert readings["tick"] == 4
    assert isinstance(readings["cpu_percent"], float)
    assert isinstance(readings["memory_percent"], float)
    assert isinstance(readings["network_up"], bool)
    assert isinstance(readings["process_count"], int)


def test_experience_engine_routes_environment_reward_to_learning() -> None:
    learning = LearningSpy()
    engine = ExperienceEngine(
        sensor=SystemSensorAdapter(lambda tick: {"signal": tick}),
        network=Network(),
        encoder=lambda frame: {0: float(cast(dict[str, int], frame.payload)["signal"])},
        decoder=lambda result, frame: ActionCommand(
            "target-actuator", frame.tick, "right"
        ),
        embodiment=_agent(),
        learning=learning,  # type: ignore[arg-type]
    )
    engine.reset(seed=42)

    records = [engine.step(tick) for tick in range(1, 4)]

    assert [record.reward for record in records] == [0.0, 0.0, 1.0]
    assert learning.rewards == [(0.0, 1), (0.0, 2), (1.0, 3)]
    assert records[-1].observation is not None
    assert records[-1].observation.terminated


def test_unauthorized_action_cannot_create_experience_reward() -> None:
    learning = LearningSpy()
    engine = ExperienceEngine(
        sensor=SystemSensorAdapter(lambda tick: {"signal": tick}),
        network=Network(),
        encoder=lambda frame: {0: 1.0},
        decoder=lambda result, frame: ActionCommand(
            "target-actuator", frame.tick, "right"
        ),
        embodiment=_agent(authorized=False),
        learning=learning,  # type: ignore[arg-type]
    )

    record = engine.step(1)

    assert record.observation is None
    assert record.reward == 0.0
    assert learning.rewards == []


def test_runtime_hooks_use_one_existing_network_tick() -> None:
    runtime = RuntimeSpy()
    network = Network()
    engine = ExperienceEngine(
        sensor=SystemSensorAdapter(lambda tick: {"signal": tick}),
        network=network,
        encoder=lambda frame: {0: 1.0},
        decoder=lambda result, frame: ActionCommand(
            "target-actuator", frame.tick, "right"
        ),
        embodiment=_agent(),
    )
    engine.attach_runtime(runtime)

    assert len(runtime.pre_hooks) == 1
    assert len(runtime.post_hooks) == 1
    prepare = runtime.pre_hooks[0]
    complete = runtime.post_hooks[0]
    assert callable(prepare)
    assert callable(complete)
    prepare(1)  # type: ignore[operator]
    result = network.step()
    record = complete(1, result)  # type: ignore[operator]

    assert len(network.injected) == 1
    assert record.observation is not None
    state = cast(dict[str, Any], record.observation.state)
    assert state["position"] == 1
