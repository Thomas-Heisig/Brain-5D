"""Lazy dashboard heatmaps and safe snapshot selection.

This module provides memory-efficient heatmap generation from B5D snapshots
without loading the entire network into RAM. It uses memory-mapped I/O
and lazy projection for efficient visualization of structural data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.storage.b5d import B5DReader
from src.storage.lazy_view import B5DLazyProjector, StorageHeatmapKind

from .models import JSONValue

# ============================================================================
# Custom Exceptions
# ============================================================================


class HeatmapError(Exception):
    """Base exception for heatmap-related errors."""


class InvalidHeatmapKindError(HeatmapError):
    """Raised when an unknown heatmap kind is requested."""


class SnapshotNotFoundError(HeatmapError):
    """Raised when a requested snapshot file does not exist."""


class InvalidSnapshotError(HeatmapError):
    """Raised when a snapshot filename is invalid or unsafe."""


# ============================================================================
# Data Models
# ============================================================================


@dataclass(frozen=True, slots=True)
class HeatmapPayload:
    """JSON-ready heatmap projection.

    Attributes:
        kind: Type of heatmap (e.g., 'spike_activity', 'synaptic_weights').
        tick: The simulation tick at which the snapshot was taken.
        samples: Number of samples used in the projection.
        snapshot: Name of the snapshot file used.
        values: 2D array of heatmap values.
        source: Always "snapshot" to distinguish from live runtime data.
    """

    kind: str
    tick: int
    samples: int
    snapshot: str
    values: list[list[float]]
    source: str = "snapshot"

    def to_json(self) -> dict[str, JSONValue]:
        """Return the projection in JSON-compatible form."""
        return {
            "kind": self.kind,
            "tick": self.tick,
            "samples": self.samples,
            "snapshot": self.snapshot,
            "values": [list(row) for row in self.values],
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class SnapshotEntry:
    """One selectable snapshot beside the configured default snapshot.

    Attributes:
        name: Filename of the snapshot.
        size_bytes: File size in bytes.
    """

    name: str
    size_bytes: int

    def __post_init__(self) -> None:
        """Validate snapshot entry data."""
        if not self.name or not self.name.endswith(".b5d"):
            raise ValueError(f"Invalid snapshot name: {self.name}")
        if self.size_bytes < 0:
            raise ValueError(f"Invalid file size: {self.size_bytes}")

    def to_json(self) -> dict[str, JSONValue]:
        """Return JSON-ready snapshot metadata."""
        return {"name": self.name, "size_bytes": self.size_bytes}


# ============================================================================
# Main Heatmap Source
# ============================================================================


class SnapshotHeatmapSource:
    """Build heatmaps without loading the whole network into RAM.

    This class provides memory-efficient heatmap generation from B5D snapshots
    using memory-mapped I/O and lazy projection. It supports listing available
    snapshots and building heatmaps from specific snapshots.

    The heatmap source is designed to be used with the dashboard for
    visualization of structural and activity patterns.

    Example:
        >>> source = SnapshotHeatmapSource(Path("snapshots/latest.b5d"))
        >>> snapshots = source.list_snapshots()
        >>> heatmap = source.build("spike_activity", snapshot_name="snapshot_1000.b5d")
    """

    def __init__(self, snapshot_path: Path, activity_tau_ticks: float = 50.0) -> None:
        """Initialize the heatmap source.

        Args:
            snapshot_path: Path to the default snapshot file.
            activity_tau_ticks: Time constant for activity decay in ticks.
                Higher values smooth activity over longer windows.
        """
        self.snapshot_path = snapshot_path.resolve()
        self.snapshot_root = self.snapshot_path.parent
        self.activity_tau_ticks = activity_tau_ticks

        if not self.snapshot_path.is_file():
            raise FileNotFoundError(f"Default snapshot not found: {self.snapshot_path}")

    def list_snapshots(self) -> tuple[SnapshotEntry, ...]:
        """List all available B5D snapshots in the snapshot directory.

        Returns:
            Tuple of SnapshotEntry objects, sorted by name (typically timestamp).
            Returns empty tuple if directory does not exist.

        Note:
            Only files with .b5d extension are included. Hidden files and
            directories are excluded.
        """
        if not self.snapshot_root.is_dir():
            return ()

        entries: list[SnapshotEntry] = []

        for path in sorted(self.snapshot_root.glob("*.b5d")):
            if not path.is_file():
                continue
            if path.name.startswith("."):
                continue

            try:
                entries.append(SnapshotEntry(path.name, path.stat().st_size))
            except (OSError, ValueError):
                # Skip files that cannot be read
                continue

        return tuple(entries)

    def build(self, kind_name: str, snapshot_name: str | None = None) -> HeatmapPayload:
        """Build a heatmap from a snapshot.

        Args:
            kind_name: Type of heatmap to build (e.g., 'spike_activity').
                Must be a valid StorageHeatmapKind value.
            snapshot_name: Optional specific snapshot filename. If None or
                empty, uses the default snapshot.

        Returns:
            HeatmapPayload containing the projection data.

        Raises:
            InvalidHeatmapKindError: If kind_name is not a valid heatmap type.
            SnapshotNotFoundError: If the requested snapshot file does not exist.
            InvalidSnapshotError: If the snapshot filename is invalid or unsafe.
            HeatmapError: For other heatmap-related errors.
        """
        # Validate heatmap kind
        try:
            kind = StorageHeatmapKind(kind_name)
        except ValueError as e:
            raise InvalidHeatmapKindError(
                f"Unknown heatmap kind: {kind_name}. "
                f"Valid types: {[k.value for k in StorageHeatmapKind]}"
            ) from e

        # Resolve snapshot path
        try:
            snapshot = self._resolve_snapshot(snapshot_name)
        except ValueError as e:
            raise InvalidSnapshotError(str(e)) from e
        except FileNotFoundError as e:
            raise SnapshotNotFoundError(str(e)) from e

        # Build the heatmap using lazy projection
        try:
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

        except Exception as e:
            raise HeatmapError(f"Failed to build heatmap: {e}") from e

    def _resolve_snapshot(self, snapshot_name: str | None) -> Path:
        """Resolve a snapshot path with security checks.

        Args:
            snapshot_name: Name of the snapshot file, or None for default.

        Returns:
            Resolved Path object.

        Raises:
            ValueError: If the snapshot name is invalid or unsafe.
            FileNotFoundError: If the snapshot file does not exist.
        """
        # Use default if no snapshot name provided
        if snapshot_name is None or not snapshot_name.strip():
            return self.snapshot_path

        # Basic security: prevent path traversal
        if ".." in snapshot_name:
            raise ValueError(f"Invalid snapshot filename: {snapshot_name}")

        # Ensure the filename is clean
        if Path(snapshot_name).name != snapshot_name:
            raise ValueError(f"Invalid snapshot filename: {snapshot_name}")

        # Ensure it's a .b5d file
        if not snapshot_name.endswith(".b5d"):
            raise ValueError(f"Invalid snapshot extension: {snapshot_name}")

        # Resolve and ensure it's within the snapshot root
        candidate = (self.snapshot_root / snapshot_name).resolve()

        if candidate.parent != self.snapshot_root:
            raise ValueError(f"Snapshot not in allowed directory: {snapshot_name}")

        if not candidate.is_file():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_name}")

        return candidate

    def has_snapshot(self, snapshot_name: str) -> bool:
        """Check if a specific snapshot exists.

        Args:
            snapshot_name: Name of the snapshot file.

        Returns:
            True if the snapshot exists and is accessible.
        """
        try:
            candidate = self._resolve_snapshot(snapshot_name)
            return candidate.is_file()
        except (ValueError, FileNotFoundError):
            return False

    def get_snapshot_info(self, snapshot_name: str) -> SnapshotEntry:
        """Get metadata for a specific snapshot.

        Args:
            snapshot_name: Name of the snapshot file.

        Returns:
            SnapshotEntry with file metadata.

        Raises:
            ValueError: If the snapshot name is invalid.
            FileNotFoundError: If the snapshot file does not exist.
        """
        snapshot = self._resolve_snapshot(snapshot_name)
        return SnapshotEntry(snapshot.name, snapshot.stat().st_size)


# ============================================================================
# Demo Heatmap Source (Fallback when no .b5d snapshot exists)
# ============================================================================


class DemoHeatmapSource:
    """Fallback heatmap source that generates synthetic demo data.

    This source is used when no .b5d snapshot file is available. It
    generates realistic-looking synthetic heatmaps so the dashboard
    always has something to display, even without a running simulation.
    """

    def __init__(self) -> None:
        self._tick = 0
        self._rng_seed = 42

    def list_snapshots(self) -> tuple[SnapshotEntry, ...]:
        """Return an empty list (no real snapshots available)."""
        return ()

    def build(
        self,
        kind_name: str,
        snapshot_name: str | None = None,
    ) -> HeatmapPayload:
        """Build a synthetic demo heatmap.

        Args:
            kind_name: Type of heatmap (ignored for demo).
            snapshot_name: Optional snapshot name (ignored for demo).

        Returns:
            A HeatmapPayload with synthetic data.
        """
        self._tick += 1
        import random

        rng = random.Random(self._rng_seed + self._tick)

        # Generate a 40x20 grid of synthetic values with some structure
        rows, cols = 40, 20
        values: list[list[float]] = []
        for y in range(cols):
            row: list[float] = []
            for x in range(rows):
                # Create some spatial structure: clusters of activity
                cx, cy = rows // 2, cols // 2
                dist = ((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2
                cluster = max(0, 1.0 - dist * 0.5)
                noise = rng.gauss(0, 0.15)
                val = max(0.0, min(1.0, cluster + noise))
                row.append(val)
            values.append(row)

        return HeatmapPayload(
            kind=kind_name or "activity",
            tick=self._tick * 100,
            samples=rows * cols,
            snapshot="demo (no .b5d snapshot)",
            values=values,
        )

    def has_snapshot(self, snapshot_name: str) -> bool:
        """Demo source has no real snapshots."""
        return False

    def get_snapshot_info(self, snapshot_name: str) -> SnapshotEntry:
        """Demo source has no real snapshots."""
        raise FileNotFoundError(f"No snapshot available: {snapshot_name}")


# ============================================================================
# Factory Function
# ============================================================================


def create_heatmap_source(
    snapshot_path: str | Path,
    activity_tau_ticks: float = 50.0,
) -> SnapshotHeatmapSource:
    """Factory function for creating a SnapshotHeatmapSource.

    Args:
        snapshot_path: Path to the default snapshot file.
        activity_tau_ticks: Time constant for activity decay.

    Returns:
        Configured SnapshotHeatmapSource instance.

    Example:
        >>> source = create_heatmap_source("snapshots/latest.b5d")
        >>> source.list_snapshots()
    """
    if isinstance(snapshot_path, str):
        snapshot_path = Path(snapshot_path)
    return SnapshotHeatmapSource(snapshot_path, activity_tau_ticks)
