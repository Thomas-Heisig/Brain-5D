"""Tests for the dependency-free Brain-5D operator dashboard."""

from pathlib import Path

from src.dashboard.models import (
    DashboardSnapshot,
    LearningMetrics,
    StorageMetrics,
    SystemMetrics,
)
from src.dashboard.state import DashboardStateStore


def test_dashboard_snapshot_is_json_ready() -> None:
    snapshot = DashboardSnapshot(
        status="running",
        system=SystemMetrics(tick=42, neurons=10, synapses=20),
        learning=LearningMetrics(stdp_updates=3),
        storage=StorageMetrics(queue_depth=2, queue_capacity=10),
    )
    payload = snapshot.to_json()
    assert payload["status"] == "running"
    assert payload["system"] == {
        "tick": 42,
        "neurons": 10,
        "synapses": 20,
        "spikes_total": 0,
        "spikes_last_tick": 0,
        "core_step_ms": 0.0,
        "mean_energy": 0.0,
    }


def test_dashboard_store_publishes_immutable_snapshot() -> None:
    store = DashboardStateStore()
    updated = DashboardSnapshot(status="running", system=SystemMetrics(tick=7))
    store.publish(updated)
    assert store.snapshot() == updated


def test_static_dashboard_assets_exist() -> None:
    static_root = Path(__file__).parents[1] / "src" / "dashboard" / "static"
    assert (static_root / "index.html").is_file()
    assert (static_root / "styles.css").is_file()
    assert (static_root / "app.js").is_file()
