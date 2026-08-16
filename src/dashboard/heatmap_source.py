"""Lazy dashboard heatmaps and safe snapshot selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.storage.b5d import B5DReader
from src.storage.lazy_view import B5DLazyProjector, StorageHeatmapKind

from .models import JSONValue


@dataclass(frozen=True, slots=True)
class HeatmapPayload:
    """JSON-ready heatmap projection."""

    kind: str
    tick: int
    samples: int
    snapshot: str
    values: list[list[float]]

    def to_json(self) -> dict[str, JSONValue]:
        """Return the projection in JSON-compatible form."""
        return {
            "kind": self.kind,
            "tick": self.tick,
            "samples": self.samples,
            "snapshot": self.snapshot,
            "values": [list(row) for row in self.values],
        }


@dataclass(frozen=True, slots=True)
class SnapshotEntry:
    """One selectable snapshot beside the configured default snapshot."""

    name: str
    size_bytes: int

    def to_json(self) -> dict[str, JSONValue]:
        """Return JSON-ready snapshot metadata."""
        return {"name": self.name, "size_bytes": self.size_bytes}


class SnapshotHeatmapSource:
    """Build heatmaps without loading the whole network into RAM."""

    def __init__(self, snapshot_path: Path, activity_tau_ticks: float = 50.0) -> None:
        self.snapshot_path = snapshot_path.resolve()
        self.snapshot_root = self.snapshot_path.parent
        self.activity_tau_ticks = activity_tau_ticks

    def list_snapshots(self) -> tuple[SnapshotEntry, ...]:
        """List safe sibling snapshots for the dashboard selector."""
        if not self.snapshot_root.is_dir():
            return ()
        return tuple(
            SnapshotEntry(path.name, path.stat().st_size)
            for path in sorted(self.snapshot_root.glob("*.b5d"))
            if path.is_file()
        )

    def build(self, kind_name: str, snapshot_name: str | None = None) -> HeatmapPayload:
        """Build one mmap-backed X-Y projection."""
        kind = StorageHeatmapKind(kind_name)
        snapshot = self._resolve_snapshot(snapshot_name)
        with B5DReader(snapshot) as reader:
            projector = B5DLazyProjector(reader, self.activity_tau_ticks)
            result = projector.build(kind)
        return HeatmapPayload(
            kind=result.kind.value,
            tick=result.snapshot_tick,
            samples=result.samples,
            snapshot=snapshot.name,
            values=result.values.tolist(),
        )

    def _resolve_snapshot(self, snapshot_name: str | None) -> Path:
        if snapshot_name is None or not snapshot_name.strip():
            return self.snapshot_path
        if Path(snapshot_name).name != snapshot_name:
            raise ValueError("invalid snapshot filename")
        candidate = (self.snapshot_root / snapshot_name).resolve()
        if candidate.parent != self.snapshot_root or candidate.suffix != ".b5d":
            raise ValueError("invalid snapshot filename")
        if not candidate.is_file():
            raise FileNotFoundError(snapshot_name)
        return candidate
