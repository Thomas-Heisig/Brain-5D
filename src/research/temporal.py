"""Multi-timescale state memory and deterministic temporal comparison."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class TemporalStateFrame:
    """Serializable state reference retained without rewinding the runtime."""

    tick: int
    state_digest: str
    metrics: tuple[tuple[str, float], ...] = ()

    @classmethod
    def from_mapping(
        cls, tick: int, state_digest: str, metrics: dict[str, float]
    ) -> "TemporalStateFrame":
        normalized = tuple(
            sorted((str(key), float(value)) for key, value in metrics.items())
        )
        if any(not isfinite(value) for _, value in normalized):
            raise ValueError("temporal metrics must be finite")
        return cls(tick=tick, state_digest=state_digest, metrics=normalized)

    def metric_map(self) -> dict[str, float]:
        return dict(self.metrics)


class TemporalStateMemory:
    """Keep bounded FAST/MEDIUM/SLOW references of observed state frames."""

    def __init__(
        self, *, horizons: dict[str, int] | None = None, capacity: int = 256
    ) -> None:
        self.horizons = dict(horizons or {"fast": 10, "medium": 100, "slow": 1000})
        if not self.horizons or any(value < 1 for value in self.horizons.values()):
            raise ValueError("temporal horizons must be positive")
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._frames: deque[TemporalStateFrame] = deque(maxlen=capacity)

    def append(self, frame: TemporalStateFrame) -> None:
        self._frames.append(frame)

    def reference(self, current_tick: int, horizon: str) -> TemporalStateFrame | None:
        if horizon not in self.horizons:
            raise KeyError(horizon)
        target = current_tick - self.horizons[horizon]
        candidates = [frame for frame in self._frames if frame.tick <= target]
        return max(candidates, key=lambda frame: frame.tick) if candidates else None

    def __len__(self) -> int:
        return len(self._frames)


@dataclass(frozen=True)
class TemporalComparison:
    """Deterministic difference between a current frame and a historical frame."""

    horizon: str
    current_tick: int
    reference_tick: int | None
    discrepancy: float | None
    changed_metrics: tuple[str, ...]
    digest_changed: bool | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "current_tick": self.current_tick,
            "reference_tick": self.reference_tick,
            "discrepancy": self.discrepancy,
            "changed_metrics": list(self.changed_metrics),
            "digest_changed": self.digest_changed,
        }


class TemporalComparator:
    """Compare current measurements to a retained FAST/MEDIUM/SLOW reference."""

    def compare(
        self,
        current: TemporalStateFrame,
        reference: TemporalStateFrame | None,
        *,
        horizon: str,
    ) -> TemporalComparison:
        if reference is None:
            return TemporalComparison(horizon, current.tick, None, None, (), None)
        current_metrics = current.metric_map()
        reference_metrics = reference.metric_map()
        common = sorted(set(current_metrics) & set(reference_metrics))
        differences = {
            name: abs(current_metrics[name] - reference_metrics[name])
            for name in common
        }
        changed = tuple(name for name in common if differences[name] > 0.0)
        discrepancy = (
            sum(differences.values()) / len(differences) if differences else 0.0
        )
        return TemporalComparison(
            horizon=horizon,
            current_tick=current.tick,
            reference_tick=reference.tick,
            discrepancy=discrepancy,
            changed_metrics=changed,
            digest_changed=current.state_digest != reference.state_digest,
        )
