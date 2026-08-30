"""Dashboard contract tests for v0.5 homeostasis metrics."""

from src.dashboard.adapters import homeostasis_metrics
from src.dashboard.models import DashboardSnapshot
from src.homeostasis import HomeostasisStats


def test_homeostasis_metrics_are_json_ready() -> None:
    stats = HomeostasisStats(
        enabled=True,
        updates=10,
        target_rate_hz=5.0,
        mean_rate_hz=4.5,
        mean_rate_error_hz=-0.5,
        mean_threshold_adaptation=0.2,
        target_energy=1.0,
        mean_energy=0.9,
        mean_energy_error=0.1,
        active_neurons=3,
    )
    metrics = homeostasis_metrics(stats)  # type: ignore[arg-type]
    payload = DashboardSnapshot(homeostasis=metrics).to_json()
    assert payload["homeostasis"] == metrics.to_json()
