"""Alpha.7 end-to-end safety and deterministic environment proofs."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.embodiment import (
    ActionCommand,
    ActuatorResult,
    ConnectionDescriptor,
    ConnectionKind,
    ConnectionStatus,
    ControlledEmbodimentAgent,
    ControlledSensorAdapter,
    DeterministicTargetEnvironment,
    RelationshipClass,
    SensorFrame,
)
from src.embodiment.audit import ActionAuditTrail


@dataclass
class FakeActuator:
    calls: int = 0
    active: bool = True
    actuator_id: str = "target-actuator"

    def apply(self, command: ActionCommand) -> ActuatorResult:
        self.calls += 1
        return ActuatorResult(True, command.action)


@dataclass
class FakeSensor:
    active: bool = True
    sensor_id: str = "target-sensor"
    modality: str = "position"

    def sample(self, tick: int) -> SensorFrame:
        return SensorFrame(self.sensor_id, tick, self.modality, {"tick": tick})


def _descriptor(*, authorized: bool = True) -> ConnectionDescriptor:
    return ConnectionDescriptor(
        connection_id="target-actuator",
        name="Deterministic target actuator",
        kind=ConnectionKind.ACTUATOR,
        relationship=RelationshipClass.CONTROLLABLE,
        status=ConnectionStatus.CONNECTED,
        capabilities=("right", "left"),
        available=True,
        authorized=authorized,
        active=True,
    )


def _agent(
    *,
    authorized: bool = True,
    max_actions_per_tick: int = 1,
    require_human_override: bool = False,
) -> tuple[ControlledEmbodimentAgent, FakeActuator]:
    actuator = FakeActuator()
    agent = ControlledEmbodimentAgent(
        DeterministicTargetEnvironment(),
        actuator,
        _descriptor(authorized=authorized),
        max_actions_per_tick=max_actions_per_tick,
        require_human_override=require_human_override,
    )
    agent.reset(seed=42)
    return agent, actuator


def test_deterministic_environment_completes_feedback_loop() -> None:
    agent, actuator = _agent()
    observation = None
    for tick in range(1, 4):
        observation = agent.step(ActionCommand("target-actuator", tick, "right"))
    assert observation is not None
    assert observation.state["position"] == 3
    assert observation.reward == 1.0
    assert observation.terminated
    assert actuator.calls == 3
    assert agent.audit.verify()
    assert all(record.accepted for record in agent.audit.records)


def test_unauthorized_action_is_blocked_and_audited() -> None:
    agent, actuator = _agent(authorized=False)
    assert agent.step(ActionCommand("target-actuator", 1, "right")) is None
    assert actuator.calls == 0
    assert agent.audit.records[-1].reason == "unauthorized"


def test_capability_and_rate_limit_are_enforced() -> None:
    agent, actuator = _agent(max_actions_per_tick=1)
    assert agent.step(ActionCommand("target-actuator", 1, "jump")) is None
    assert agent.step(ActionCommand("target-actuator", 2, "right")) is not None
    assert agent.step(ActionCommand("target-actuator", 2, "right")) is None
    assert actuator.calls == 1
    assert [record.reason for record in agent.audit.records] == [
        "capability_denied",
        "accepted",
        "rate_limited",
    ]


def test_emergency_stop_blocks_until_human_clears_it() -> None:
    agent, actuator = _agent()
    agent.emergency_stop()
    assert agent.step(ActionCommand("target-actuator", 1, "right")) is None
    with pytest.raises(PermissionError):
        agent.clear_emergency_stop(human_approved=False)
    agent.clear_emergency_stop(human_approved=True)
    assert agent.step(ActionCommand("target-actuator", 2, "right")) is not None
    assert actuator.calls == 1


def test_human_override_is_required_below_policy_layer() -> None:
    agent, actuator = _agent(require_human_override=True)
    assert agent.step(ActionCommand("target-actuator", 1, "right")) is None
    agent.approve_override(1, human_approved=True)
    assert agent.step(ActionCommand("target-actuator", 1, "right")) is not None
    assert actuator.calls == 1


def test_audit_chain_is_append_only_and_verifiable() -> None:
    trail = ActionAuditTrail()
    command = ActionCommand("target-actuator", 1, "right")
    trail.append(
        "target-actuator",
        command,
        ActuatorResult(False, "denied"),
        accepted=False,
        reason="unauthorized",
    )
    assert trail.verify()
    assert len(trail.records) == 1


def test_sensor_sampling_is_authorized_and_capability_bound() -> None:
    sensor = FakeSensor()
    descriptor = ConnectionDescriptor(
        connection_id="target-sensor",
        name="Deterministic target sensor",
        kind=ConnectionKind.SENSOR,
        relationship=RelationshipClass.PERCEIVABLE,
        status=ConnectionStatus.CONNECTED,
        modalities=("position",),
        available=True,
        authorized=True,
        active=True,
    )
    controlled = ControlledSensorAdapter(sensor, descriptor)
    assert controlled.sample(4) == SensorFrame(
        "target-sensor", 4, "position", {"tick": 4}
    )
    denied = ConnectionDescriptor(
        connection_id=descriptor.connection_id,
        name=descriptor.name,
        kind=descriptor.kind,
        relationship=descriptor.relationship,
        status=descriptor.status,
        modalities=descriptor.modalities,
        available=True,
        authorized=False,
        active=True,
    )
    assert ControlledSensorAdapter(sensor, denied).sample(5) is None
