"""Thread-safe dashboard state publication."""

from __future__ import annotations

from threading import RLock

from .models import DashboardSnapshot


class DashboardStateStore:
    """Publish and retrieve immutable dashboard snapshots safely."""

    def __init__(self, initial: DashboardSnapshot | None = None) -> None:
        self._lock = RLock()
        self._snapshot = initial or DashboardSnapshot()

    def publish(self, snapshot: DashboardSnapshot) -> None:
        """Replace the currently visible snapshot atomically."""
        with self._lock:
            self._snapshot = snapshot

    def snapshot(self) -> DashboardSnapshot:
        """Return the latest immutable snapshot."""
        with self._lock:
            return self._snapshot
