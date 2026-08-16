"""Dashboard bridge tests for v0.4.0-alpha.6."""

from src.dashboard.models import DashboardSnapshot, HomeostasisMetrics


def test_homeostasis_metrics_are_json_ready() -> None:
    """The v0.5 bridge is present without requiring a homeostasis engine."""

    snapshot = DashboardSnapshot(
        homeostasis=HomeostasisMetrics(
            target_rate_hz=5.0,
            actual_rate_hz=4.25,
            rate_error_hz=0.75,
            mean_threshold_adaptation=0.12,
            mean_energy_error=-0.03,
            active_neurons=42,
        )
    )
    payload = snapshot.to_json()
    homeostasis = payload["homeostasis"]
    assert isinstance(homeostasis, dict)
    assert homeostasis["target_rate_hz"] == 5.0
    assert homeostasis["active_neurons"] == 42
