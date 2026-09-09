"""Technical controls for the bounded memory and observation-only predictor."""

from dataclasses import dataclass
from pathlib import Path

import pytest

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
)
from src.embodiment.models import SensorFrame
from src.experience import ExperienceEngine
from src.memory import (
    MemoryStore,
    MemoryStoreError,
    MemoryWorldModel,
    TransitionWorldModel,
)
from src.profiles import BehaviorProfile


@dataclass
class _Actuator:
    active: bool = True

    def apply(self, command: ActionCommand) -> ActuatorResult:
        return ActuatorResult(True, command.action)


@dataclass
class _Network:
    def inject_current_batch(self, currents: dict[int, float]) -> None:
        del currents

    def step(self) -> dict[str, tuple[int, ...]]:
        return {"output_spike_ids": (1,)}


def _agent() -> ControlledEmbodimentAgent:
    descriptor = ConnectionDescriptor(
        connection_id="target-actuator",
        name="Target actuator",
        kind=ConnectionKind.ACTUATOR,
        relationship=RelationshipClass.CONTROLLABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("right",),
        available=True,
        authorized=True,
        active=True,
    )
    agent = ControlledEmbodimentAgent(
        DeterministicTargetEnvironment(), _Actuator(), descriptor
    )
    agent.reset(seed=42)
    return agent


def test_experience_writes_episode_and_prediction_before_feedback(
    tmp_path: Path,
) -> None:
    store = MemoryStore(run_id="run-1", episode_capacity=4)
    cognition = MemoryWorldModel(store, TransitionWorldModel(), "run-1")
    engine = ExperienceEngine(
        sensor=SystemSensorAdapter(lambda tick: {"cue": "A"}),
        network=_Network(),
        encoder=lambda frame: {0: 1.0},
        decoder=lambda result, frame: ActionCommand(
            "target-actuator", frame.tick, "right"
        ),
        embodiment=_agent(),
        memory=cognition,
    )

    engine.reset(seed=42)
    first = engine.step(1)
    second = engine.step(2)

    assert first.observation is not None
    assert second.observation is not None
    assert len(store.episodes) == 2
    assert store.episodes[0].executed_action is not None
    assert store.episodes[0].result is not None
    assert len(store.predictions) == 2
    assert store.predictions[0].source == "persistence_reference"
    assert store.predictions[1].source == "adaptive_transition"

    state_path = tmp_path / "memory-state.json"
    cognition.save(state_path)
    restored = MemoryWorldModel.load(state_path)
    assert restored.state_dict() == cognition.state_dict()


def test_memory_controls_are_independent() -> None:
    store = MemoryStore(run_id="run-1", read_enabled=False, write_enabled=True)
    frame = SensorFrame("sensor", 1, "cue", {"value": 1})
    store.record(frame, None, None, episode_id="episode-1")
    assert store.recall() == ()
    assert len(store.episodes) == 1

    store.set_controls(read_enabled=True, write_enabled=False)
    store.record(
        SensorFrame("sensor", 2, "cue", {"value": 2}),
        None,
        None,
        episode_id="episode-1",
    )
    assert [item.tick for item in store.recall()] == [1]


def test_memory_capacity_retention_and_corruption_fail_closed(tmp_path: Path) -> None:
    store = MemoryStore(run_id="run-1", episode_capacity=2, retention_ticks=2)
    for tick in range(1, 5):
        store.record(
            SensorFrame("sensor", tick, "cue", {"value": tick}),
            None,
            None,
            episode_id="episode-1",
        )
    assert [item.tick for item in store.episodes] == [3, 4]

    state_path = tmp_path / "memory.json"
    store.save(state_path)
    restored = MemoryStore.load(state_path)
    assert restored.state_dict() == store.state_dict()
    state_path.write_text('{"schema_version": 1}', encoding="utf-8")
    with pytest.raises(MemoryStoreError, match="integrity"):
        MemoryStore.load(state_path)


def test_world_model_prediction_has_no_target_state_input() -> None:
    model = TransitionWorldModel()
    frame = SensorFrame("sensor", 1, "cue", {"value": 1})
    action = ActionCommand("actuator", 1, "right")
    prediction = model.predict(
        frame, action, target_tick=2, persistence_state={"position": 0}
    )

    assert prediction.predicted_state == {"position": 0}
    assert prediction.source == "persistence_reference"


def test_behavior_profile_is_operational_and_auditable(tmp_path: Path) -> None:
    profile = BehaviorProfile("WESEN-0001", initial={"exploration": 1.0})
    candidates = (
        ActionCommand("actuator", 1, "first"),
        ActionCommand("actuator", 1, "second"),
    )

    selected = profile.select_action(candidates, tick=1)
    profile.update(success=False, tick=1)
    profile.save(tmp_path / "behavior.json")
    restored = BehaviorProfile.load(tmp_path / "behavior.json")

    assert selected == candidates[1]
    assert profile.value("persistence") > 0.5
    assert profile.update_log[0]["rule"] == "bounded_ema_to_outcome_target_v1"
    assert restored.state_dict() == profile.state_dict()
