"""Deterministic replay of committed structural journal records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from src.storage.structural_journal import StructuralChangeRecord, StructuralJournal


class StructuralReplayTarget(Protocol):
    def apply_structural_record(self, record: StructuralChangeRecord) -> bool: ...


@dataclass(frozen=True, slots=True)
class StructuralRecoveryReport:
    applied_records: int
    last_sequence: int
    last_tick: int
    ignored_uncommitted_records: int


class StructuralRecoveryManager:
    def replay(
        self, target: StructuralReplayTarget, journal_path: Path
    ) -> StructuralRecoveryReport:
        journal = StructuralJournal(journal_path)
        scan = journal.scan()
        applied = 0
        last_tick = 0
        last_sequence = 0
        for record in scan.committed:
            if not target.apply_structural_record(record):
                raise RuntimeError(
                    f"structural replay rejected sequence {record.sequence}"
                )
            applied += 1
            last_tick = record.tick
            last_sequence = record.sequence
        return StructuralRecoveryReport(
            applied, last_sequence, last_tick, scan.uncommitted_records
        )
