"""Runtime adapter connecting ExperienceEngine data to memory and prediction."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.embodiment.models import ActionCommand, EnvironmentObservation, SensorFrame

from .store import MemoryStore, PredictionRecord
from .world_model import TransitionWorldModel, WorldPrediction


class MemoryWorldModelError(ValueError):
    """Raised when the memory/world-model runtime contract is misused."""


@dataclass(slots=True)
class MemoryWorldModel:
    """Observation-only integration for one ExperienceEngine."""

    store: MemoryStore
    world_model: TransitionWorldModel
    run_id: str
    enabled: bool = True
    persistence_path: Path | None = None
    _episode_id: str = "episode-0"

    def reset_episode(self, episode_id: str) -> None:
        self._episode_id = episode_id

    def predict(
        self, frame: SensorFrame, action: ActionCommand | None, tick: int
    ) -> WorldPrediction | None:
        if not self.enabled or not self.store.read_enabled:
            return None
        previous = self.store.recall(limit=1)
        previous_state = (
            None
            if not previous or previous[0].result is None
            else previous[0].result.get("state")
        )
        return self.world_model.predict(
            frame, action, target_tick=tick + 1, persistence_state=previous_state
        )

    def complete(
        self,
        frame: SensorFrame,
        action: ActionCommand | None,
        observation: EnvironmentObservation | None,
        tick: int,
        prediction: WorldPrediction | None,
    ) -> None:
        if not self.enabled:
            return
        self.store.record(frame, action, observation, episode_id=self._episode_id)
        if observation is None:
            return
        if self.store.write_enabled:
            self.world_model.update(frame, action, observation)
        if prediction is not None and self.store.write_enabled:
            self.store.record_prediction(
                PredictionRecord(
                    self.run_id,
                    self._episode_id,
                    tick,
                    prediction.target_tick,
                    prediction.source,
                    prediction.predicted_state,
                    observation.state,
                    self.world_model.error(
                        prediction.predicted_state, observation.state
                    ),
                    prediction.uncertainty,
                )
            )
        if self.persistence_path is not None:
            self.save(self.persistence_path)

    def state_dict(self) -> dict[str, Any]:
        state = {
            "schema_version": 1,
            "owner": "memory.world_model.integration",
            "run_id": self.run_id,
            "enabled": self.enabled,
            "episode_id": self._episode_id,
            "world_model": self.world_model.state_dict(),
            "memory": self.store.state_dict(),
        }
        unsigned = json.dumps(
            state, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        state["integrity_digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
        return state

    def save(self, path: Path | None = None) -> Path:
        destination = path or self.persistence_path
        if destination is None:
            raise MemoryWorldModelError("coupled persistence path is not configured")
        payload = json.dumps(
            self.state_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
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
    def load(cls, path: Path) -> "MemoryWorldModel":
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise MemoryWorldModelError("coupled state could not be read") from error
        if not isinstance(state, dict) or state.get("schema_version") != 1:
            raise MemoryWorldModelError("unsupported coupled state schema")
        unsigned = dict(state)
        digest = unsigned.pop("integrity_digest", None)
        expected = hashlib.sha256(
            json.dumps(
                unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode("utf-8")
        ).hexdigest()
        if state.get("owner") != "memory.world_model.integration" or digest != expected:
            raise MemoryWorldModelError("coupled state integrity check failed")
        store = MemoryStore.from_state_dict(state["memory"])
        try:
            model = TransitionWorldModel.from_state_dict(state["world_model"])
        except (KeyError, TypeError, ValueError) as error:
            raise MemoryWorldModelError(
                "world model state could not be restored"
            ) from error
        return cls(
            store,
            model,
            str(state["run_id"]),
            bool(state["enabled"]),
            path,
            str(state["episode_id"]),
        )
