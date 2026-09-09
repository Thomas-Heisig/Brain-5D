"""Controlled, experiment-only gateway runtime for Neural Symbiosis.

The runtime owns gateway state outside the canonical SNN.  It is deliberately
small and deterministic: controls and plasticity operate on a separately
persistable topology, and no method accepts a core network or an AI write
command.
"""

from __future__ import annotations

import base64
import hashlib
import json
import random
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

from .models import JSONValue
from .neural_symbiosis import (
    PlasticGatewayConfig,
    homeostatic_scale,
    pair_stdp_delta,
    reward_modulated_delta,
)


class GatewayState(StrEnum):
    DISABLED = "disabled"
    REGISTERED = "registered"
    EXPERIMENT_READY = "experiment_ready"
    ACTIVE_FROZEN = "active_frozen"
    ACTIVE_RANDOM = "active_random"
    ACTIVE_SHUFFLE = "active_shuffle"
    ACTIVE_PLASTIC = "active_plastic"
    PAUSED = "paused"
    ERROR = "error"


class GatewayCondition(StrEnum):
    FROZEN = "frozen"
    RANDOM = "random"
    SHUFFLE = "shuffle"
    PLASTIC = "plastic"


class GatewayResourceMode(StrEnum):
    NORMAL = "normal"
    CONSERVE = "conserve"
    CRITICAL = "critical"
    SURVIVAL = "survival"


class GatewayRuntimeError(RuntimeError):
    """Base error for fail-closed gateway operations."""


class GatewayGuardError(GatewayRuntimeError):
    """Raised when an activation contract is incomplete or invalid."""


class GatewayLimitError(GatewayRuntimeError):
    """Raised when a gateway cannot continue within configured limits."""


@dataclass(frozen=True, slots=True)
class GatewayEdge:
    source_channel: int
    target_channel: int
    weight: float = 0.5
    delay_ms: float = 0.0

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "source_channel": self.source_channel,
            "target_channel": self.target_channel,
            "weight": self.weight,
            "delay_ms": self.delay_ms,
        }


@dataclass(frozen=True, slots=True)
class GatewayTopology:
    gateway_id: str
    source_area: str
    target_area: str
    source_channels: int
    target_channels: int
    modality: str
    edges: tuple[GatewayEdge, ...]
    plasticity_rule: str = "none"
    creation_source: str = "experiment"
    experiment_id: str | None = None
    seed: int | None = None
    generation: int = 0
    provenance: str = ""

    def __post_init__(self) -> None:
        if not self.gateway_id.strip():
            raise ValueError("gateway_id must not be empty")
        if not self.source_area.strip() or not self.target_area.strip():
            raise ValueError("source_area and target_area must not be empty")
        if self.source_channels < 1 or self.target_channels < 1:
            raise ValueError("gateway channels must be positive")
        if len(self.edges) > 100_000:
            raise ValueError("gateway topology exceeds the hard edge limit")

    @classmethod
    def create(
        cls,
        gateway_id: str,
        *,
        source_area: str,
        target_area: str,
        source_channels: int,
        target_channels: int,
        modality: str,
        seed: int,
        condition: GatewayCondition = GatewayCondition.FROZEN,
        max_edges: int = 10_000,
        plasticity_rule: str = "none",
        experiment_id: str | None = None,
    ) -> "GatewayTopology":
        if max_edges < 1:
            raise ValueError("max_edges must be positive")
        count = min(source_channels * target_channels, max_edges)
        rng = random.Random(seed)
        targets = list(range(target_channels))
        if condition is GatewayCondition.SHUFFLE:
            rng.shuffle(targets)
        edges: list[GatewayEdge] = []
        for index in range(count):
            source_channel = index % source_channels
            target_channel = targets[index % target_channels]
            weight = (
                rng.uniform(0.0, 1.0) if condition is GatewayCondition.RANDOM else 0.5
            )
            edges.append(
                GatewayEdge(
                    source_channel=source_channel,
                    target_channel=target_channel,
                    weight=weight,
                    delay_ms=float((source_channel + target_channel) % 4),
                )
            )
        provenance = hashlib.sha256(
            json.dumps(
                {
                    "gateway_id": gateway_id,
                    "source_area": source_area,
                    "target_area": target_area,
                    "modality": modality,
                    "seed": seed,
                    "condition": condition.value,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        return cls(
            gateway_id=gateway_id,
            source_area=source_area,
            target_area=target_area,
            source_channels=source_channels,
            target_channels=target_channels,
            modality=modality,
            edges=tuple(edges),
            plasticity_rule=plasticity_rule,
            experiment_id=experiment_id,
            seed=seed,
            provenance=provenance,
        )

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "gateway_id": self.gateway_id,
            "source_area": self.source_area,
            "target_area": self.target_area,
            "source_channels": self.source_channels,
            "target_channels": self.target_channels,
            "modality": self.modality,
            "edges": len(self.edges),
            "edge_records": [edge.to_json() for edge in self.edges],
            "plasticity_rule": self.plasticity_rule,
            "creation_source": self.creation_source,
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "generation": self.generation,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, slots=True)
class GatewayLimits:
    max_events_per_tick: int = 10_000
    max_spikes_per_tick: int = 10_000
    max_edges: int = 10_000
    max_structural_changes_window: int = 256
    max_weight_delta_window: float = 100.0
    max_queue_depth: int = 10_000
    max_latency_ms: float = 1_000.0
    max_memory_bytes: int = 64 * 1024 * 1024

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "max_events_per_tick": self.max_events_per_tick,
            "max_spikes_per_tick": self.max_spikes_per_tick,
            "max_edges": self.max_edges,
            "max_structural_changes_window": self.max_structural_changes_window,
            "max_weight_delta_window": self.max_weight_delta_window,
            "max_queue_depth": self.max_queue_depth,
            "max_latency_ms": self.max_latency_ms,
            "max_memory_bytes": self.max_memory_bytes,
        }


@dataclass(frozen=True, slots=True)
class GatewayJournalEvent:
    event: str
    tick: int
    gateway_id: str
    source: int | str | None = None
    target: int | str | None = None
    previous_value: float | str | None = None
    new_value: float | str | None = None
    rule: str = ""
    experiment_id: str | None = None
    causal_signal: float | None = None

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "event": self.event,
            "tick": self.tick,
            "gateway_id": self.gateway_id,
            "source": self.source,
            "target": self.target,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "rule": self.rule,
            "experiment_id": self.experiment_id,
            "causal_signal": self.causal_signal,
        }


def _encoded_rng_state(state: object) -> str:
    import pickle

    return base64.b64encode(pickle.dumps(state, protocol=4)).decode("ascii")


def _decoded_rng_state(value: object) -> object:
    import pickle

    if not isinstance(value, str):
        raise GatewayRuntimeError("checkpoint RNG state is missing")
    return pickle.loads(base64.b64decode(value.encode("ascii")))


class PreregistrationGuard:
    """Validate the minimum frozen contract before gateway plasticity."""

    REQUIRED = (
        "research_question",
        "hypothesis",
        "protocol_id",
        "conditions",
        "seed_strategy",
        "stopping_rule",
        "inclusion_criteria",
        "exclusion_criteria",
        "primary_outcomes",
        "ai_authority_boundaries",
        "freeze",
    )

    @classmethod
    def validate(
        cls,
        preregistration: Mapping[str, Any] | None,
        *,
        condition: GatewayCondition,
        seed: object,
        experiment_mode: bool,
    ) -> None:
        if not experiment_mode:
            raise GatewayGuardError("gateway activation requires experiment mode")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise GatewayGuardError("gateway experiment seed must be an integer")
        if preregistration is None:
            raise GatewayGuardError("frozen preregistration is required")
        missing = [key for key in cls.REQUIRED if key not in preregistration]
        if missing:
            raise GatewayGuardError("preregistration is missing: " + ", ".join(missing))
        freeze = preregistration.get("freeze")
        if not isinstance(freeze, Mapping):
            raise GatewayGuardError("preregistration freeze block is invalid")
        freeze = cast(Mapping[str, Any], freeze)
        if freeze.get("status") not in {"REGISTERED", "FROZEN", "AMENDED"}:
            raise GatewayGuardError("preregistration is not frozen/registered")
        if freeze.get("immutable_after_first_run") is not True:
            raise GatewayGuardError("preregistration must be immutable after first run")
        if freeze.get("human_review_required") is not True:
            raise GatewayGuardError("preregistration must require human review")
        conditions = preregistration.get("conditions")
        if not isinstance(conditions, Sequence) or isinstance(conditions, (str, bytes)):
            raise GatewayGuardError("preregistration conditions must be a list")
        labels = {
            (
                str(cast(Mapping[str, Any], item).get("id"))
                if isinstance(item, Mapping)
                else str(item)
            )
            for item in cast(Sequence[Any], conditions)
        }
        required = {item.value for item in GatewayCondition}
        if not required.issubset(labels):
            raise GatewayGuardError(
                "preregistration must declare frozen/random/shuffle/plastic controls"
            )
        seed_strategy = preregistration.get("seed_strategy")
        if not isinstance(seed_strategy, Mapping):
            raise GatewayGuardError("seed_strategy must be an object")
        minimum = cast(Mapping[str, Any], seed_strategy).get(
            "minimum_independent_seeds"
        )
        if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
            raise GatewayGuardError(
                "seed_strategy.minimum_independent_seeds is invalid"
            )
        if condition is GatewayCondition.PLASTIC and minimum < 3:
            raise GatewayGuardError(
                "plastic gateway experiments require at least three independent seeds"
            )


@dataclass
class GatewayRuntime:
    """One bounded gateway runtime with an experiment-only activation gate."""

    limits: GatewayLimits = field(default_factory=GatewayLimits)
    plasticity: PlasticGatewayConfig = field(default_factory=PlasticGatewayConfig)
    journal_capacity: int = 512

    def __post_init__(self) -> None:
        if self.journal_capacity < 1:
            raise ValueError("journal_capacity must be positive")
        self.state = GatewayState.DISABLED
        self.condition: GatewayCondition | None = None
        self.resource_mode = GatewayResourceMode.NORMAL
        self.topology: GatewayTopology | None = GatewayTopology.create(
            "GW-AUDIO-SNN-001",
            source_area="audio_encoder",
            target_area="mhrn_core",
            source_channels=8,
            target_channels=8,
            modality="audio",
            seed=0,
            max_edges=self.limits.max_edges,
        )
        self.experiment_id: str | None = None
        self.seed: int | None = None
        self.tick = 0
        self._rng = random.Random(0)
        self._resume_state = GatewayState.DISABLED
        self._journal: deque[GatewayJournalEvent] = deque(maxlen=self.journal_capacity)
        self._metrics: dict[str, float | int] = {
            "gateway_events": 0,
            "spikes": 0,
            "synaptic_operations": 0,
            "queue_depth": 0,
            "cpu_time_ms": 0.0,
            "estimated_energy": 0.0,
            "measured_energy": 0.0,
            "latency_ms": 0.0,
            "dropped_events": 0,
            "throttled_ticks": 0,
            "plasticity_updates": 0,
            "structural_changes": 0,
        }
        self._weight_delta_window: deque[float] = deque(maxlen=100)
        self._structural_window: deque[int] = deque(maxlen=100)
        self.last_error: str | None = None

    @classmethod
    def load(cls, path: Path, **kwargs: Any) -> "GatewayRuntime":
        """Restore a runtime checkpoint when one exists, otherwise start clean."""
        runtime = cls(**kwargs)
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise GatewayRuntimeError("gateway checkpoint root must be an object")
            runtime.restore(cast(Mapping[str, Any], payload))
        return runtime

    @property
    def gateway_id(self) -> str:
        return self.topology.gateway_id if self.topology is not None else ""

    def register_gateway(self, topology: GatewayTopology) -> None:
        if len(topology.edges) > self.limits.max_edges:
            raise GatewayLimitError("gateway topology exceeds max_edges")
        self.topology = topology
        self.state = GatewayState.REGISTERED
        self.last_error = None

    def prepare_experiment(self, experiment_id: str) -> None:
        if not experiment_id.strip():
            raise GatewayGuardError("experiment_id must not be empty")
        if self.topology is None:
            raise GatewayRuntimeError("gateway is not registered")
        self.experiment_id = experiment_id
        self.state = GatewayState.EXPERIMENT_READY

    def activate(
        self,
        condition: GatewayCondition | str,
        *,
        experiment_id: str,
        seed: int,
        preregistration: Mapping[str, Any] | None = None,
        experiment_mode: bool = False,
    ) -> dict[str, JSONValue]:
        selected = GatewayCondition(condition)
        if self.topology is None:
            raise GatewayRuntimeError("gateway is not registered")
        if not experiment_id.strip():
            raise GatewayGuardError("experiment_id must not be empty")
        if selected is GatewayCondition.PLASTIC or preregistration is not None:
            PreregistrationGuard.validate(
                preregistration,
                condition=selected,
                seed=seed,
                experiment_mode=experiment_mode,
            )
        elif not experiment_mode:
            raise GatewayGuardError("gateway activation requires experiment mode")
        self.experiment_id = experiment_id
        self.seed = seed
        self.condition = selected
        self._rng = random.Random(seed)
        self.tick = 0
        self._weight_delta_window.clear()
        self._structural_window.clear()
        self.last_error = None
        self._apply_condition(selected, experiment_id)
        self._resume_state = {
            GatewayCondition.FROZEN: GatewayState.ACTIVE_FROZEN,
            GatewayCondition.RANDOM: GatewayState.ACTIVE_RANDOM,
            GatewayCondition.SHUFFLE: GatewayState.ACTIVE_SHUFFLE,
            GatewayCondition.PLASTIC: GatewayState.ACTIVE_PLASTIC,
        }[selected]
        self.state = self._resume_state
        return self.status()

    def _apply_condition(self, condition: GatewayCondition, experiment_id: str) -> None:
        assert self.topology is not None
        replacement = GatewayTopology.create(
            self.topology.gateway_id,
            source_area=self.topology.source_area,
            target_area=self.topology.target_area,
            source_channels=self.topology.source_channels,
            target_channels=self.topology.target_channels,
            modality=self.topology.modality,
            seed=int(self.seed or 0),
            condition=condition,
            max_edges=self.limits.max_edges,
            plasticity_rule=(
                "three_factor_stdp" if condition is GatewayCondition.PLASTIC else "none"
            ),
            experiment_id=experiment_id,
        )
        self.topology = replacement

    def pause(self, reason: str = "operator_pause") -> dict[str, JSONValue]:
        if self.state not in {
            GatewayState.ACTIVE_FROZEN,
            GatewayState.ACTIVE_RANDOM,
            GatewayState.ACTIVE_SHUFFLE,
            GatewayState.ACTIVE_PLASTIC,
        }:
            raise GatewayRuntimeError("only an active gateway can be paused")
        self._resume_state = self.state
        self.state = GatewayState.PAUSED
        self._journal.append(
            GatewayJournalEvent(
                "gate_closed",
                self.tick,
                self.gateway_id,
                rule=reason,
                experiment_id=self.experiment_id,
            )
        )
        return self.status()

    def resume(self) -> dict[str, JSONValue]:
        if self.state is not GatewayState.PAUSED:
            raise GatewayRuntimeError("gateway is not paused")
        self.state = self._resume_state
        self._journal.append(
            GatewayJournalEvent(
                "gate_opened",
                self.tick,
                self.gateway_id,
                rule="resume",
                experiment_id=self.experiment_id,
            )
        )
        return self.status()

    def stop(self) -> dict[str, JSONValue]:
        self.state = GatewayState.DISABLED
        self.condition = None
        self._resume_state = GatewayState.DISABLED
        self._journal.append(
            GatewayJournalEvent(
                "gate_closed",
                self.tick,
                self.gateway_id,
                rule="stop",
                experiment_id=self.experiment_id,
            )
        )
        return self.status()

    def step(
        self,
        source_activity: Sequence[float] = (),
        target_activity: Sequence[float] = (),
        *,
        reward: float = 0.0,
        queue_depth: int = 0,
        latency_ms: float = 0.0,
        memory_bytes: int = 0,
    ) -> dict[str, JSONValue]:
        if self.state not in {
            GatewayState.ACTIVE_FROZEN,
            GatewayState.ACTIVE_RANDOM,
            GatewayState.ACTIVE_SHUFFLE,
            GatewayState.ACTIVE_PLASTIC,
        }:
            return self.status()
        self.tick += 1
        events = len(source_activity) * max(len(target_activity), 1)
        requested_events = events
        spikes = sum(1 for value in source_activity if float(value) > 0.0)
        self._metrics["queue_depth"] = max(0, queue_depth)
        self._metrics["latency_ms"] = float(latency_ms)
        self._metrics["cpu_time_ms"] = float(self._metrics["cpu_time_ms"]) + float(
            latency_ms
        )
        if (
            queue_depth > self.limits.max_queue_depth
            or latency_ms > self.limits.max_latency_ms
            or memory_bytes > self.limits.max_memory_bytes
        ):
            self.resource_mode = GatewayResourceMode.CRITICAL
            self._metrics["throttled_ticks"] = int(self._metrics["throttled_ticks"]) + 1
            events = min(events, self.limits.max_events_per_tick // 2)
        else:
            self.resource_mode = GatewayResourceMode.NORMAL
        accepted = min(events, self.limits.max_events_per_tick)
        self._metrics["gateway_events"] = (
            int(self._metrics["gateway_events"]) + accepted
        )
        self._metrics["dropped_events"] = int(self._metrics["dropped_events"]) + max(
            0, requested_events - accepted
        )
        self._metrics["spikes"] = int(self._metrics["spikes"]) + min(
            spikes, self.limits.max_spikes_per_tick
        )
        self._metrics["synaptic_operations"] = (
            int(self._metrics["synaptic_operations"]) + accepted
        )
        self._metrics["estimated_energy"] = (
            float(self._metrics["estimated_energy"]) + accepted + spikes
        )
        if (
            self.condition is GatewayCondition.PLASTIC
            and self.topology is not None
            and self.resource_mode is GatewayResourceMode.NORMAL
        ):
            self._plastic_step(source_activity, target_activity, reward)
        return self.status()

    def _plastic_step(
        self,
        source_activity: Sequence[float],
        target_activity: Sequence[float],
        reward: float,
    ) -> None:
        assert self.topology is not None
        source_rate = sum(float(value) for value in source_activity) / max(
            len(source_activity), 1
        )
        target_rate = sum(float(value) for value in target_activity) / max(
            len(target_activity), 1
        )
        updated: list[GatewayEdge] = []
        for edge in self.topology.edges:
            delta = pair_stdp_delta(
                edge.weight, target_rate - source_rate, self.plasticity
            )
            delta = reward_modulated_delta(delta, reward, self.plasticity)
            new_weight = homeostatic_scale(
                edge.weight + delta, target_rate, self.plasticity
            )
            bounded_delta = new_weight - edge.weight
            self._weight_delta_window.append(abs(bounded_delta))
            updated.append(
                GatewayEdge(
                    edge.source_channel, edge.target_channel, new_weight, edge.delay_ms
                )
            )
            if bounded_delta:
                self._journal.append(
                    GatewayJournalEvent(
                        "weight_changed",
                        self.tick,
                        self.gateway_id,
                        source=edge.source_channel,
                        target=edge.target_channel,
                        previous_value=edge.weight,
                        new_value=new_weight,
                        rule="reward_modulated_stdp_homeostasis",
                        experiment_id=self.experiment_id,
                        causal_signal=reward,
                    )
                )
        if sum(self._weight_delta_window) > self.limits.max_weight_delta_window:
            self.resource_mode = GatewayResourceMode.CONSERVE
            self._metrics["throttled_ticks"] = int(self._metrics["throttled_ticks"]) + 1
            return
        self.topology = GatewayTopology(
            gateway_id=self.topology.gateway_id,
            source_area=self.topology.source_area,
            target_area=self.topology.target_area,
            source_channels=self.topology.source_channels,
            target_channels=self.topology.target_channels,
            modality=self.topology.modality,
            edges=tuple(updated),
            plasticity_rule=self.topology.plasticity_rule,
            creation_source=self.topology.creation_source,
            experiment_id=self.topology.experiment_id,
            seed=self.topology.seed,
            generation=self.topology.generation + 1,
            provenance=self.topology.provenance,
        )
        self._metrics["plasticity_updates"] = int(
            self._metrics["plasticity_updates"]
        ) + len(updated)

    def checkpoint(self) -> dict[str, JSONValue]:
        return self.status(include_checkpoint=True)

    def restore(self, checkpoint: Mapping[str, Any]) -> dict[str, JSONValue]:
        topology_value = checkpoint.get("topology")
        if not isinstance(topology_value, Mapping):
            raise GatewayRuntimeError("checkpoint topology is missing")
        topology_value = cast(Mapping[str, Any], topology_value)
        edges_value = topology_value.get("edge_records", [])
        if not isinstance(edges_value, Sequence):
            raise GatewayRuntimeError("checkpoint edge records are invalid")
        edges = tuple(
            GatewayEdge(
                int(edge["source_channel"]),
                int(edge["target_channel"]),
                float(edge["weight"]),
                float(edge["delay_ms"]),
            )
            for edge in (
                cast(Mapping[str, Any], value)
                for value in cast(Sequence[Any], edges_value)
                if isinstance(value, Mapping)
            )
        )
        self.topology = GatewayTopology(
            gateway_id=str(topology_value["gateway_id"]),
            source_area=str(topology_value["source_area"]),
            target_area=str(topology_value["target_area"]),
            source_channels=int(topology_value["source_channels"]),
            target_channels=int(topology_value["target_channels"]),
            modality=str(topology_value["modality"]),
            edges=edges,
            plasticity_rule=str(topology_value.get("plasticity_rule", "none")),
            creation_source=str(topology_value.get("creation_source", "experiment")),
            experiment_id=cast(str | None, topology_value.get("experiment_id")),
            seed=cast(int | None, topology_value.get("seed")),
            generation=int(topology_value.get("generation", 0)),
            provenance=str(topology_value.get("provenance", "")),
        )
        self.state = GatewayState(str(checkpoint["state"]))
        resume_value = checkpoint.get("resume_state", self.state.value)
        self._resume_state = GatewayState(str(resume_value))
        condition_value = checkpoint.get("condition")
        self.condition = (
            GatewayCondition(str(condition_value)) if condition_value else None
        )
        self.resource_mode = GatewayResourceMode(
            str(checkpoint.get("resource_mode", "normal"))
        )
        self.experiment_id = cast(str | None, checkpoint.get("experiment_id"))
        seed_value = checkpoint.get("seed")
        self.seed = int(seed_value) if seed_value is not None else None
        self.tick = int(checkpoint.get("tick", 0))
        self._rng.setstate(
            cast(tuple[Any, ...], _decoded_rng_state(checkpoint.get("rng_state")))
        )
        metrics_value = checkpoint.get("metrics")
        if isinstance(metrics_value, Mapping):
            self._metrics = {
                str(key): cast(float | int, value)
                for key, value in cast(Mapping[str, Any], metrics_value).items()
            }
        self._weight_delta_window.clear()
        weight_window = checkpoint.get("weight_delta_window", [])
        if isinstance(weight_window, Sequence):
            self._weight_delta_window.extend(
                float(value) for value in cast(Sequence[Any], weight_window)
            )
        self._structural_window.clear()
        structural_window = checkpoint.get("structural_window", [])
        if isinstance(structural_window, Sequence):
            self._structural_window.extend(
                int(value) for value in cast(Sequence[Any], structural_window)
            )
        journal_value = checkpoint.get("journal", [])
        self._journal.clear()
        if isinstance(journal_value, Sequence):
            for event in cast(Sequence[Any], journal_value):
                if isinstance(event, Mapping):
                    self._journal.append(
                        GatewayJournalEvent(**cast(dict[str, Any], event))
                    )
        return self.status()

    def status(self, *, include_checkpoint: bool = False) -> dict[str, JSONValue]:
        payload: dict[str, JSONValue] = {
            "gateway_id": self.gateway_id,
            "state": self.state.value,
            "condition": self.condition.value if self.condition else None,
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "resource_mode": self.resource_mode.value,
            "gateway_plasticity_allowed": self.state is GatewayState.ACTIVE_PLASTIC,
            "productive_gateway": {
                "available": False,
                "reason": "experimental_validation_incomplete",
            },
            "topology": self.topology.to_json() if self.topology else None,
            "metrics": dict(self._metrics),
            "limits": self.limits.to_json(),
            "journal": [event.to_json() for event in self._journal],
            "journal_bounded": True,
            "last_error": self.last_error,
            "scientific_boundary": {
                "experiment_only": True,
                "canonical_core_mutation": False,
                "direct_llm_write": False,
                "gateway_activity_is_not_learning_evidence": True,
                "ai_interpretation_is_non_evidentiary": True,
            },
        }
        if include_checkpoint:
            payload["tick"] = self.tick
            payload["rng_state"] = _encoded_rng_state(self._rng.getstate())
            payload["resume_state"] = self._resume_state.value
            payload["weight_delta_window"] = list(self._weight_delta_window)
            payload["structural_window"] = list(self._structural_window)
        return payload

    def persist(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.checkpoint(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


__all__ = [
    "GatewayCondition",
    "GatewayEdge",
    "GatewayGuardError",
    "GatewayJournalEvent",
    "GatewayLimits",
    "GatewayResourceMode",
    "GatewayRuntime",
    "GatewayRuntimeError",
    "GatewayState",
    "GatewayTopology",
    "PreregistrationGuard",
]
