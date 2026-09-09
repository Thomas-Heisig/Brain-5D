"""Bounded, persistent episodic and working memory.

This store contains experimental agent memory only. It does not replace
network snapshots, learning state, or immutable research raw data.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.embodiment.models import ActionCommand, EnvironmentObservation, SensorFrame

MEMORY_SCHEMA_VERSION = 1
MEMORY_OWNER = "memory.layer"


class MemoryStoreError(ValueError):
    """Raised when memory state is invalid or cannot be restored."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _json_copy(value: object) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=True))


def _digest(value: dict[str, Any]) -> str:
    unsigned = _json_copy(value)
    unsigned.pop("integrity_digest", None)
    return hashlib.sha256(_canonical(unsigned)).hexdigest()


@dataclass(frozen=True, slots=True)
class EpisodeRecord:
    """One observed sensor/action/feedback event."""

    run_id: str
    episode_id: str
    tick: int
    source: str
    observation: dict[str, Any]
    executed_action: dict[str, Any] | None
    result: dict[str, Any] | None
    uncertainty: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "tick": self.tick,
            "source": self.source,
            "observation": _json_copy(self.observation),
            "executed_action": _json_copy(self.executed_action),
            "result": _json_copy(self.result),
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True, slots=True)
class PredictionRecord:
    """Prediction and later comparison, kept separate from observations."""

    run_id: str
    episode_id: str
    tick: int
    target_tick: int
    source: str
    predicted_state: dict[str, Any] | None
    actual_state: dict[str, Any] | None
    error: float | None
    uncertainty: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "tick": self.tick,
            "target_tick": self.target_tick,
            "source": self.source,
            "predicted_state": _json_copy(self.predicted_state),
            "actual_state": _json_copy(self.actual_state),
            "error": self.error,
            "uncertainty": self.uncertainty,
        }


class MemoryStore:
    """A deterministic, bounded store with independent read/write controls."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        run_id: str = "run-unknown",
        episode_capacity: int = 128,
        working_capacity: int = 16,
        prediction_capacity: int = 128,
        retention_ticks: int = 1024,
        read_enabled: bool = True,
        write_enabled: bool = True,
    ) -> None:
        if min(episode_capacity, working_capacity, prediction_capacity) <= 0:
            raise ValueError("memory capacities must be positive")
        if retention_ticks <= 0:
            raise ValueError("retention_ticks must be positive")
        self.root = root
        self.run_id = run_id
        self.episode_capacity = episode_capacity
        self.working_capacity = working_capacity
        self.prediction_capacity = prediction_capacity
        self.retention_ticks = retention_ticks
        self.read_enabled = read_enabled
        self.write_enabled = write_enabled
        self.episodes: list[EpisodeRecord] = []
        self.working: list[EpisodeRecord] = []
        self.predictions: list[PredictionRecord] = []

    def controls(self) -> dict[str, bool]:
        return {"read_enabled": self.read_enabled, "write_enabled": self.write_enabled}

    def set_controls(self, *, read_enabled: bool, write_enabled: bool) -> None:
        self.read_enabled = read_enabled
        self.write_enabled = write_enabled

    def record(
        self,
        frame: SensorFrame,
        action: ActionCommand | None,
        observation: EnvironmentObservation | None,
        *,
        episode_id: str,
        uncertainty: float = 0.0,
        source: str = "experience.engine",
    ) -> EpisodeRecord | None:
        if not self.write_enabled:
            return None
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError("uncertainty must be between 0 and 1")
        result = (
            None
            if observation is None
            else {
                "tick": observation.tick,
                "state": _json_copy(observation.state),
                "reward": observation.reward,
                "terminated": observation.terminated,
                "truncated": observation.truncated,
            }
        )
        record = EpisodeRecord(
            self.run_id,
            episode_id,
            frame.tick,
            source,
            {
                "sensor_id": frame.sensor_id,
                "modality": frame.modality,
                "payload": _json_copy(frame.payload),
            },
            (
                None
                if action is None
                else {
                    "actuator_id": action.actuator_id,
                    "tick": action.tick,
                    "action": action.action,
                    "payload": _json_copy(action.payload),
                }
            ),
            result,
            uncertainty,
        )
        if not any(
            existing.to_dict() == record.to_dict() for existing in self.episodes
        ):
            self.episodes.append(record)
            cutoff = frame.tick - self.retention_ticks + 1
            self.episodes = [item for item in self.episodes if item.tick >= cutoff]
            self.episodes = self.episodes[-self.episode_capacity :]
            self.working.append(record)
            self.working = [item for item in self.working if item.tick >= cutoff]
            self.working = self.working[-self.working_capacity :]
        return record

    def record_prediction(self, prediction: PredictionRecord) -> None:
        if not self.write_enabled:
            return
        self.predictions.append(prediction)
        self.predictions = self.predictions[-self.prediction_capacity :]

    def recall(
        self, *, modality: str | None = None, limit: int = 8
    ) -> tuple[EpisodeRecord, ...]:
        if not self.read_enabled:
            return ()
        if limit <= 0:
            return ()
        candidates = [
            record
            for record in self.episodes
            if modality is None or record.observation.get("modality") == modality
        ]
        return tuple(
            sorted(
                candidates, key=lambda item: (item.tick, item.episode_id), reverse=True
            )[:limit]
        )

    def state_dict(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "schema_version": MEMORY_SCHEMA_VERSION,
            "owner": MEMORY_OWNER,
            "run_id": self.run_id,
            "configuration": {
                "episode_capacity": self.episode_capacity,
                "working_capacity": self.working_capacity,
                "prediction_capacity": self.prediction_capacity,
                "retention_ticks": self.retention_ticks,
            },
            "controls": self.controls(),
            "episodes": [record.to_dict() for record in self.episodes],
            "working": [record.to_dict() for record in self.working],
            "predictions": [record.to_dict() for record in self.predictions],
        }
        state["integrity_digest"] = _digest(state)
        return state

    def save(self, path: Path | None = None) -> Path:
        destination = path or self.root
        if destination is None:
            raise MemoryStoreError("memory persistence path is not configured")
        payload = _canonical(self.state_dict())
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(
            prefix=f".{destination.name}.", dir=str(destination.parent)
        )
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return destination

    @classmethod
    def load(cls, path: Path) -> "MemoryStore":
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise MemoryStoreError("memory state could not be read") from error
        if not isinstance(state, dict):
            raise MemoryStoreError("memory state must be an object")
        return cls.from_state_dict(state)

    @classmethod
    def from_state_dict(cls, state: dict[str, Any]) -> "MemoryStore":
        if state.get("schema_version") != MEMORY_SCHEMA_VERSION:
            raise MemoryStoreError("unsupported memory schema")
        if state.get("owner") != MEMORY_OWNER or state.get(
            "integrity_digest"
        ) != _digest(state):
            raise MemoryStoreError("memory integrity check failed")
        configuration = cast(dict[str, Any], state.get("configuration"))
        controls = cast(dict[str, bool], state.get("controls"))
        store = cls(
            run_id=str(state["run_id"]),
            episode_capacity=int(configuration["episode_capacity"]),
            working_capacity=int(configuration["working_capacity"]),
            prediction_capacity=int(configuration["prediction_capacity"]),
            retention_ticks=int(configuration["retention_ticks"]),
            read_enabled=bool(controls["read_enabled"]),
            write_enabled=bool(controls["write_enabled"]),
        )
        store.episodes = [
            _episode_from_dict(item) for item in cast(list[Any], state["episodes"])
        ]
        store.working = [
            _episode_from_dict(item) for item in cast(list[Any], state["working"])
        ]
        store.predictions = [
            _prediction_from_dict(item)
            for item in cast(list[Any], state["predictions"])
        ]
        if (
            len(store.episodes) > store.episode_capacity
            or len(store.working) > store.working_capacity
        ):
            raise MemoryStoreError("memory state exceeds configured capacity")
        return store


def _episode_from_dict(value: object) -> EpisodeRecord:
    item = cast(dict[str, Any], value)
    return EpisodeRecord(
        str(item["run_id"]),
        str(item["episode_id"]),
        int(item["tick"]),
        str(item["source"]),
        cast(dict[str, Any], item["observation"]),
        (
            None
            if item["executed_action"] is None
            else cast(dict[str, Any], item["executed_action"])
        ),
        None if item["result"] is None else cast(dict[str, Any], item["result"]),
        float(item["uncertainty"]),
    )


def _prediction_from_dict(value: object) -> PredictionRecord:
    item = cast(dict[str, Any], value)
    return PredictionRecord(
        str(item["run_id"]),
        str(item["episode_id"]),
        int(item["tick"]),
        int(item["target_tick"]),
        str(item["source"]),
        (
            None
            if item["predicted_state"] is None
            else cast(dict[str, Any], item["predicted_state"])
        ),
        (
            None
            if item["actual_state"] is None
            else cast(dict[str, Any], item["actual_state"])
        ),
        None if item["error"] is None else float(item["error"]),
        float(item["uncertainty"]),
    )
