"""Append-only audit records for external embodiment actions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from time import time_ns

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

    def __init__(self) -> None:
        self._records: list[ActionAuditRecord] = []
        self._digest = "0" * 64

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
        payload: dict[str, JSONValue] = {
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
            "previous_digest": self._digest,
        }
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
        return record

    def verify(self) -> bool:
        previous = "0" * 64
        for record in self._records:
            if record.previous_digest != previous:
                return False
            previous = record.digest
        return previous == self._digest
