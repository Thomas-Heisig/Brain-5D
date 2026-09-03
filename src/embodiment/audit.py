"""Append-only audit records for external embodiment actions."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from time import time_ns
from typing import cast

from .models import ActionCommand, ActuatorResult, JSONValue


@dataclass(frozen=True, slots=True)
class ActionAuditRecord:
    """Immutable, hash-linked record of an attempted action."""

    sequence: int
    timestamp_ns: int
    connection_id: str
    command: ActionCommand
    result: ActuatorResult
    accepted: bool
    reason: str
    previous_digest: str
    digest: str


class ActionAuditTrail:
    """In-memory append-only audit trail with tamper-evident chaining."""

    def __init__(self, journal_path: Path | None = None) -> None:
        self._records: list[ActionAuditRecord] = []
        self._digest = "0" * 64
        self._journal_path = journal_path
        if journal_path is not None and journal_path.exists():
            self._load(journal_path)

    @property
    def records(self) -> tuple[ActionAuditRecord, ...]:
        return tuple(self._records)

    def append(
        self,
        connection_id: str,
        command: ActionCommand,
        result: ActuatorResult,
        *,
        accepted: bool,
        reason: str,
    ) -> ActionAuditRecord:
        sequence = len(self._records)
        timestamp_ns = time_ns()
        payload = _payload(
            sequence,
            timestamp_ns,
            connection_id,
            command,
            accepted,
            reason,
            self._digest,
        )
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        record = ActionAuditRecord(
            sequence,
            timestamp_ns,
            connection_id,
            command,
            result,
            accepted,
            reason,
            self._digest,
            digest,
        )
        self._records.append(record)
        self._digest = digest
        if self._journal_path is not None:
            self._journal_path.parent.mkdir(parents=True, exist_ok=True)
            with self._journal_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(_record_json(record), sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        return record

    def verify(self) -> bool:
        previous = "0" * 64
        for record in self._records:
            if record.previous_digest != previous:
                return False
            payload = _payload(
                record.sequence,
                record.timestamp_ns,
                record.connection_id,
                record.command,
                record.accepted,
                record.reason,
                previous,
            )
            if hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest() != record.digest:
                return False
            previous = record.digest
        return previous == self._digest

    def _load(self, journal_path: Path) -> None:
        try:
            with journal_path.open(encoding="utf-8") as stream:
                for line in stream:
                    raw = json.loads(line)
                    if not isinstance(raw, dict):
                        raise ValueError("action journal record must be an object")
                    decoded = cast(dict[str, object], raw)
                    command_raw = decoded["command"]
                    if not isinstance(command_raw, dict):
                        raise ValueError("action journal command must be an object")
                    command_data = cast(dict[str, object], command_raw)
                    command = ActionCommand(
                        str(command_data["actuator_id"]),
                        int(cast(str | int | float, command_data["tick"])),
                        str(command_data["action"]),
                        cast(JSONValue, command_data.get("payload")),
                    )
                    result = ActuatorResult(
                        bool(decoded["result_accepted"]),
                        str(decoded["result_message"]),
                    )
                    record = ActionAuditRecord(
                        int(cast(str | int | float, decoded["sequence"])),
                        int(cast(str | int | float, decoded["timestamp_ns"])),
                        str(decoded["connection_id"]),
                        command,
                        result,
                        bool(decoded["accepted"]),
                        str(decoded["reason"]),
                        str(decoded["previous_digest"]),
                        str(decoded["digest"]),
                    )
                    self._records.append(record)
                    self._digest = record.digest
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid action journal") from exc
        if not self.verify():
            raise ValueError("action journal chain verification failed")


def _payload(
    sequence: int,
    timestamp_ns: int,
    connection_id: str,
    command: ActionCommand,
    accepted: bool,
    reason: str,
    previous_digest: str,
) -> dict[str, JSONValue]:
    return {
        "sequence": sequence,
        "timestamp_ns": timestamp_ns,
        "connection_id": connection_id,
        "command": {
            "actuator_id": command.actuator_id,
            "tick": command.tick,
            "action": command.action,
            "payload": command.payload,
        },
        "accepted": accepted,
        "reason": reason,
        "previous_digest": previous_digest,
    }


def _record_json(record: ActionAuditRecord) -> dict[str, JSONValue]:
    return {
        **_payload(
            record.sequence,
            record.timestamp_ns,
            record.connection_id,
            record.command,
            record.accepted,
            record.reason,
            record.previous_digest,
        ),
        "result_accepted": record.result.accepted,
        "result_message": record.result.message,
        "digest": record.digest,
    }
