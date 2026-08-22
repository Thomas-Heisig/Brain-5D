"""Crash-safe generation compaction for Brain-5D persistence."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Any, cast

from .b5d import B5DReader
from .delta_journal import DeltaJournal
from .recovery import RecoveryManager


@dataclass(frozen=True, slots=True)
class StorageGeneration:
    """One snapshot/journal generation selected by an atomic manifest."""

    generation: int
    snapshot: str
    journal: str
    base_tick: int


@dataclass(frozen=True, slots=True)
class CompactionResult:
    """Result of one successful or skipped compaction."""

    compacted: bool
    generation: int
    base_tick: int
    snapshot_path: Path
    journal_path: Path
    manifest_path: Path


class StorageManifest:
    """Atomic pointer to the active snapshot/journal generation."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> StorageGeneration:
        """Read the currently active storage generation."""
        raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw_data, dict):
            raise ValueError("invalid storage manifest: root must be a dict")

        raw = cast(dict[str, Any], raw_data)

        if raw.get("version") != 1:
            raise ValueError("invalid storage manifest: version must be 1")

        # Extract values with explicit type conversion
        generation_raw = raw.get("generation")
        if not isinstance(generation_raw, int):
            raise ValueError("manifest missing 'generation' field")
        generation = int(generation_raw)

        snapshot = raw.get("snapshot")
        if not isinstance(snapshot, str):
            raise ValueError("manifest missing 'snapshot' field")
        snapshot = str(snapshot)

        journal = raw.get("journal")
        if not isinstance(journal, str):
            raise ValueError("manifest missing 'journal' field")
        journal = str(journal)

        base_tick_raw = raw.get("base_tick")
        if not isinstance(base_tick_raw, int):
            raise ValueError("manifest missing 'base_tick' field")
        base_tick = int(base_tick_raw)

        return StorageGeneration(
            generation=generation,
            snapshot=snapshot,
            journal=journal,
            base_tick=base_tick,
        )

    def write_atomic(self, generation: StorageGeneration) -> None:
        """Atomically publish one fully prepared storage generation."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "version": 1,
                "generation": generation.generation,
                "snapshot": generation.snapshot,
                "journal": generation.journal,
                "base_tick": generation.base_tick,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=self.path.name + ".",
            suffix=".tmp",
            dir=self.path.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


class StorageCompactor:
    """Compact committed journal state into a new immutable generation."""

    def __init__(self, root: Path, stem: str = "brain5d") -> None:
        self.root = root
        self.stem = stem
        self.manifest = StorageManifest(root / f"{stem}.manifest.json")

    def initialize(self, snapshot_path: Path, journal_path: Path) -> StorageGeneration:
        """Create generation zero manifest for an existing pair."""
        with B5DReader(snapshot_path) as reader:
            base_tick = reader.header.snapshot_tick
        generation = StorageGeneration(
            generation=0,
            snapshot=snapshot_path.name,
            journal=journal_path.name,
            base_tick=base_tick,
        )
        self.manifest.write_atomic(generation)
        return generation

    def compact(self) -> CompactionResult:
        """Recover committed deltas into a new generation and publish atomically."""
        active = self.manifest.read()
        snapshot_path = self.root / active.snapshot
        journal_path = self.root / active.journal

        with DeltaJournal(journal_path, base_tick=active.base_tick) as journal:
            scan = journal.validate()
            marker = scan.last_commit
            if marker is None:
                return CompactionResult(
                    compacted=False,
                    generation=active.generation,
                    base_tick=active.base_tick,
                    snapshot_path=snapshot_path,
                    journal_path=journal_path,
                    manifest_path=self.manifest.path,
                )
            committed_tick = marker.tick

        next_generation = active.generation + 1
        next_snapshot = self.root / f"{self.stem}.g{next_generation}.b5d"
        next_journal = self.root / f"{self.stem}.g{next_generation}.b5d.journal"

        recovery = RecoveryManager(snapshot_path, journal_path).recover(next_snapshot)
        if not recovery.success:
            raise RuntimeError(recovery.error or "compaction recovery failed")

        with B5DReader(next_snapshot) as reader:
            reader.validate_invariants()
            if reader.header.snapshot_tick != committed_tick:
                raise RuntimeError("compacted snapshot tick does not match commit")

        with DeltaJournal(next_journal, base_tick=committed_tick):
            pass

        published = StorageGeneration(
            generation=next_generation,
            snapshot=next_snapshot.name,
            journal=next_journal.name,
            base_tick=committed_tick,
        )
        self.manifest.write_atomic(published)

        return CompactionResult(
            compacted=True,
            generation=next_generation,
            base_tick=committed_tick,
            snapshot_path=next_snapshot,
            journal_path=next_journal,
            manifest_path=self.manifest.path,
        )