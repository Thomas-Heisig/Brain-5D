"""Operational, non-psychological behavior profile for controlled tasks."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.embodiment.models import ActionCommand

BEHAVIOR_SCHEMA_VERSION = 1
_DIMENSIONS = (
    "exploration",
    "novelty_response",
    "persistence",
    "strategy_switching",
    "cost_weight",
)


def _digest(value: dict[str, Any]) -> str:
    unsigned = json.loads(json.dumps(value, ensure_ascii=True))
    unsigned.pop("integrity_digest", None)
    return hashlib.sha256(
        json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(slots=True)
class BehaviorProfile:
    """Three-level profile with deterministic, slowly changing disposition."""

    profile_id: str
    initial: dict[str, float] = field(default_factory=dict)
    situational: dict[str, float] = field(default_factory=dict)
    disposition: dict[str, float] = field(default_factory=dict)
    update_rate: float = 0.05
    update_log: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    max_update_log: int = 256
    schema_version: int = BEHAVIOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        defaults = {
            "exploration": 0.2,
            "novelty_response": 0.5,
            "persistence": 0.5,
            "strategy_switching": 0.3,
            "cost_weight": 0.5,
        }
        for dimension in _DIMENSIONS:
            self.initial[dimension] = _bounded(
                self.initial.get(dimension, defaults[dimension])
            )
            self.situational[dimension] = _bounded(self.situational.get(dimension, 0.0))
            self.disposition[dimension] = _bounded(
                self.disposition.get(dimension, self.initial[dimension])
            )
        if not 0.0 < self.update_rate <= 1.0:
            raise ValueError("update_rate must be between 0 and 1")
        if self.max_update_log <= 0:
            raise ValueError("max_update_log must be positive")
        self.update_log = self.update_log[-self.max_update_log :]

    def value(self, dimension: str) -> float:
        if dimension not in _DIMENSIONS:
            raise KeyError(dimension)
        return _bounded(self.disposition[dimension] + self.situational[dimension])

    def select_action(
        self, candidates: tuple[ActionCommand, ...], *, tick: int
    ) -> ActionCommand | None:
        """Select a candidate using profile state and simulation tick only."""

        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        exploration = self.value("exploration")
        bucket = (tick * 1103515245 + 12345) % 1000
        if bucket < int(exploration * 1000):
            index = tick % len(candidates)
            return candidates[index]
        return candidates[0]

    def update(self, *, success: bool, tick: int, source: str = "task_outcome") -> None:
        """Apply the disclosed bounded update rule using simulation time."""

        target = 0.0 if success else 1.0
        old = dict(self.disposition)
        for dimension in _DIMENSIONS:
            if dimension == "persistence":
                target = 0.0 if success else 1.0
            elif dimension == "strategy_switching":
                target = 1.0 if not success else 0.0
            else:
                target = self.initial[dimension]
            self.disposition[dimension] = _bounded(
                self.disposition[dimension]
                + self.update_rate * (target - self.disposition[dimension])
            )
        self.situational["persistence"] = _bounded(0.2 if success else 0.6)
        self.situational["strategy_switching"] = _bounded(0.2 if not success else 0.0)
        self.update_log.append(
            {
                "tick": tick,
                "source": source,
                "rule": "bounded_ema_to_outcome_target_v1",
                "success": success,
                "before": old,
                "after": dict(self.disposition),
            }
        )
        self.update_log = self.update_log[-self.max_update_log :]

    def state_dict(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "schema_version": self.schema_version,
            "owner": "profiles.behavior",
            "profile_id": self.profile_id,
            "initial": dict(self.initial),
            "situational": dict(self.situational),
            "disposition": dict(self.disposition),
            "update_rate": self.update_rate,
            "update_log": list(self.update_log),
            "max_update_log": self.max_update_log,
        }
        state["integrity_digest"] = _digest(state)
        return state

    def save(self, path: Path) -> Path:
        payload = json.dumps(
            self.state_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return path

    @classmethod
    def load(cls, path: Path) -> "BehaviorProfile":
        state = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(state, dict)
            or state.get("schema_version") != BEHAVIOR_SCHEMA_VERSION
        ):
            raise ValueError("unsupported behavior profile schema")
        if state.get("owner") != "profiles.behavior" or state.get(
            "integrity_digest"
        ) != _digest(state):
            raise ValueError("behavior profile integrity check failed")
        return cls(
            str(state["profile_id"]),
            dict(state["initial"]),
            dict(state["situational"]),
            dict(state["disposition"]),
            float(state["update_rate"]),
            list(state["update_log"]),
            int(state.get("max_update_log", 256)),
        )
