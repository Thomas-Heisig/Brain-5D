"""Deterministic routing across independently controlled actuators."""

from __future__ import annotations

from dataclasses import dataclass, field

from .controlled import ControlledEmbodimentAgent
from .models import (
    ActionCommand,
    ActionReceipt,
    EmbodimentMetrics,
    EnvironmentObservation,
)


@dataclass(slots=True)
class ActuatorHub:
    """Route commands to registered controlled actuators by stable identity."""

    agents: dict[str, ControlledEmbodimentAgent] = field(
        default_factory=dict[str, ControlledEmbodimentAgent]
    )
    last_receipt: ActionReceipt | None = None

    def register(self, agent: ControlledEmbodimentAgent) -> None:
        """Register one controlled actuator, rejecting identity mismatches."""
        actuator_id = agent.descriptor.connection_id
        if actuator_id != agent.actuator.actuator_id:
            raise ValueError("actuator descriptor and adapter IDs must match")
        if actuator_id in self.agents:
            raise ValueError("actuator ID is already registered")
        self.agents[actuator_id] = agent

    def reset(self, seed: int | None = None) -> dict[str, EnvironmentObservation]:
        """Reset every registered actuator deterministically."""
        return {
            actuator_id: agent.reset(seed)
            for actuator_id, agent in self.agents.items()
        }

    def step(self, command: ActionCommand) -> EnvironmentObservation | None:
        """Route one command and preserve the target agent's controlled boundary."""
        agent = self.agents.get(command.actuator_id)
        if agent is None:
            self.last_receipt = ActionReceipt(
                f"hub:{command.actuator_id}:{command.tick}",
                False,
                False,
                False,
                True,
                error="actuator is not registered",
                effect_observed=False,
            )
            return None
        observation = agent.step(command)
        self.last_receipt = agent.last_receipt
        return observation

    def metrics(self) -> dict[str, EmbodimentMetrics]:
        """Return per-actuator metrics without merging independent environments."""
        return {
            actuator_id: agent.metrics()
            for actuator_id, agent in self.agents.items()
        }


ActionRouter = ActuatorHub

__all__ = ["ActionRouter", "ActuatorHub"]
