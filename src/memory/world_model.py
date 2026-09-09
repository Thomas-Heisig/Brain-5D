"""A small observation-only transition predictor.

The predictor sees only the sensor frame and executed action before an
environment step. It stores aggregate observed successor states afterwards;
it never reads hidden environment state or the neural network.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from src.embodiment.models import ActionCommand, EnvironmentObservation, SensorFrame


@dataclass(frozen=True, slots=True)
class WorldPrediction:
    predicted_state: dict[str, Any] | None
    uncertainty: float
    source: str
    target_tick: int


@dataclass(slots=True)
class _TransitionStats:
    count: int = 0
    numeric_sum: dict[str, float] = field(default_factory=dict[str, float])
    categorical: dict[str, Counter[str]] = field(
        default_factory=dict[str, Counter[str]]
    )


class TransitionWorldModel:
    """Bounded one-step model with an explicit persistence reference."""

    model_version = 1

    def __init__(self, *, max_contexts: int = 128) -> None:
        if max_contexts <= 0:
            raise ValueError("max_contexts must be positive")
        self.max_contexts = max_contexts
        self._contexts: dict[str, _TransitionStats] = {}

    @staticmethod
    def _context(frame: SensorFrame, action: ActionCommand | None) -> str:
        value = {
            "modality": frame.modality,
            "payload": frame.payload,
            "action": None if action is None else action.action,
            "action_payload": None if action is None else action.payload,
        }
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )

    def predict(
        self,
        frame: SensorFrame,
        action: ActionCommand | None,
        *,
        target_tick: int,
        persistence_state: dict[str, Any] | None,
    ) -> WorldPrediction:
        stats = self._contexts.get(self._context(frame, action))
        if stats is None or stats.count == 0:
            return WorldPrediction(
                persistence_state, 1.0, "persistence_reference", target_tick
            )
        predicted: dict[str, Any] = {}
        for key, total in stats.numeric_sum.items():
            predicted[key] = total / stats.count
        for key, values in stats.categorical.items():
            predicted[key] = sorted(
                values.items(), key=lambda item: (-item[1], item[0])
            )[0][0]
        return WorldPrediction(
            predicted, 1.0 / (1.0 + stats.count), "adaptive_transition", target_tick
        )

    def update(
        self,
        frame: SensorFrame,
        action: ActionCommand | None,
        observation: EnvironmentObservation,
    ) -> None:
        key = self._context(frame, action)
        if key not in self._contexts and len(self._contexts) >= self.max_contexts:
            oldest = next(iter(self._contexts))
            del self._contexts[oldest]
        stats = self._contexts.setdefault(key, _TransitionStats())
        stats.count += 1
        for field_name, value in observation.state.items():
            if isinstance(value, bool):
                bucket = stats.categorical.setdefault(field_name, Counter[str]())
                bucket[str(value).lower()] += 1
            elif isinstance(value, (int, float)):
                stats.numeric_sum[field_name] = stats.numeric_sum.get(
                    field_name, 0.0
                ) + float(value)
            elif isinstance(value, str):
                bucket = stats.categorical.setdefault(field_name, Counter[str]())
                bucket[value] += 1

    @staticmethod
    def error(
        predicted: dict[str, Any] | None, actual: dict[str, Any] | None
    ) -> float | None:
        if predicted is None or actual is None or not actual:
            return None
        values: list[float] = []
        for key, expected in predicted.items():
            observed = actual.get(key)
            if isinstance(expected, (int, float)) and isinstance(
                observed, (int, float)
            ):
                values.append(abs(float(expected) - float(observed)))
            elif observed is not None:
                values.append(0.0 if expected == observed else 1.0)
        return None if not values else sum(values) / len(values)

    def state_dict(self) -> dict[str, Any]:
        contexts: dict[str, Any] = {}
        for key, stats in self._contexts.items():
            contexts[key] = {
                "count": stats.count,
                "numeric_sum": stats.numeric_sum,
                "categorical": {
                    name: dict(values) for name, values in stats.categorical.items()
                },
            }
        return {
            "model_version": self.model_version,
            "max_contexts": self.max_contexts,
            "contexts": contexts,
        }

    @classmethod
    def from_state_dict(cls, state: dict[str, Any]) -> "TransitionWorldModel":
        if state.get("model_version") != cls.model_version:
            raise ValueError("unsupported world model version")
        model = cls(max_contexts=int(state["max_contexts"]))
        for key, raw in dict(state["contexts"]).items():
            item = dict(raw)
            stats = _TransitionStats(count=int(item["count"]))
            stats.numeric_sum = {
                str(name): float(value)
                for name, value in dict(item["numeric_sum"]).items()
            }
            stats.categorical = {
                str(name): Counter(
                    {str(label): int(count) for label, count in dict(values).items()}
                )
                for name, values in dict(item["categorical"]).items()
            }
            model._contexts[str(key)] = stats
        return model
