"""Lazy dashboard heatmap source backed by a `.b5d` snapshot."""

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
    values: list[list[float]]

    def to_json(self) -> dict[str, JSONValue]:
        """Return the projection in JSON-compatible form."""
        return {
            "kind": self.kind,
            "tick": self.tick,
            "samples": self.samples,
            "values": [list(row) for row in self.values],
        }


class SnapshotHeatmapSource:
    """Build dashboard heatmaps without loading the whole network into RAM."""

    def __init__(self, snapshot_path: Path, activity_tau_ticks: float = 50.0) -> None:
        self.snapshot_path = snapshot_path
        self.activity_tau_ticks = activity_tau_ticks

    def build(self, kind_name: str) -> HeatmapPayload:
        """Build one mmap-backed X-Y projection."""
        kind = StorageHeatmapKind(kind_name)
        with B5DReader(self.snapshot_path) as reader:
            projector = B5DLazyProjector(reader, self.activity_tau_ticks)
            result = projector.build(kind)
        return HeatmapPayload(
            kind=result.kind.value,
            tick=result.snapshot_tick,
            samples=result.samples,
            values=result.values.tolist(),
        )
