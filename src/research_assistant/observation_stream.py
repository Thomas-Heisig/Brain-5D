"""Validated append-only observation stream for offline AI replays."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ObservationStreamError(ValueError):
    """Raised when an observation stream is malformed or inconsistent."""


@dataclass(frozen=True, slots=True)
class ObservationStreamRecord:
    """One digest-addressed observation stored in a JSONL stream."""

    sequence: int
    tick: int
    observation_digest: str
    observation: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "tick": self.tick,
            "observation_digest": self.observation_digest,
            "observation": dict(self.observation),
        }


class ObservationStream:
    """Write and validate deterministic observation JSONL files."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, observation: Mapping[str, Any], *, tick: int) -> ObservationStreamRecord:
        if tick < 0:
            raise ObservationStreamError("Observation tick must not be negative.")
        payload = _canonical_json(observation)
        existing = self.read()
        record = ObservationStreamRecord(
            sequence=len(existing),
            tick=tick,
            observation_digest=_digest(payload),
            observation=dict(observation),
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(_canonical_json(record.to_dict()) + "\n")
        return record

    def read(self) -> tuple[ObservationStreamRecord, ...]:
        if not self.path.exists():
            return ()
        records: list[ObservationStreamRecord] = []
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise ObservationStreamError(f"Blank line at JSONL line {line_number}.")
                try:
                    raw: Any = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ObservationStreamError(
                        f"Invalid JSON at JSONL line {line_number}."
                    ) from exc
                if not isinstance(raw, dict):
                    raise ObservationStreamError(f"Record at line {line_number} is not an object.")
                record = _record_from_dict(raw, line_number)
                if record.sequence != len(records):
                    raise ObservationStreamError(f"Unexpected sequence at JSONL line {line_number}.")
                if record.sequence and record.tick < records[-1].tick:
                    raise ObservationStreamError(f"Tick moved backwards at JSONL line {line_number}.")
                records.append(record)
        return tuple(records)


def _record_from_dict(raw: dict[str, Any], line_number: int) -> ObservationStreamRecord:
    sequence = raw.get("sequence")
    tick = raw.get("tick")
    digest = raw.get("observation_digest")
    observation = raw.get("observation")
    if (
        not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or not isinstance(tick, int)
        or isinstance(tick, bool)
        or tick < 0
        or not isinstance(digest, str)
        or not isinstance(observation, dict)
    ):
        raise ObservationStreamError(f"Invalid observation record at JSONL line {line_number}.")
    payload = _canonical_json(observation)
    if _digest(payload) != digest:
        raise ObservationStreamError(f"Observation digest mismatch at JSONL line {line_number}.")
    return ObservationStreamRecord(sequence, tick, digest, observation)


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ObservationStreamError("Observation is not canonical JSON data.") from exc


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
