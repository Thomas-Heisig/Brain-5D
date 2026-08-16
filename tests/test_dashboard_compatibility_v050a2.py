"""Compatibility tests for dashboard contracts carried into v0.5."""

from src.dashboard.models import DashboardSnapshot, HomeostasisMetrics
from src.embodiment.models import EmbodimentMetrics


def test_alpha6_homeostasis_aliases_remain_supported() -> None:
    """Legacy alpha.6 names resolve to the canonical v0.5 values."""
    metrics = HomeostasisMetrics(
        target_rate_hz=5.0,
        actual_rate_hz=4.25,
        rate_error_hz=0.75,
        mean_threshold_adaptation=0.12,
        mean_energy_error=-0.03,
        active_neurons=42,
    )
    payload = metrics.to_json()
    assert payload["actual_rate_hz"] == 4.25
    assert payload["mean_rate_hz"] == 4.25
    assert payload["rate_error_hz"] == 0.75
    assert payload["mean_rate_error_hz"] == 0.75


def test_alpha7_embodiment_contract_survives_v05_dashboard() -> None:
    """Embodiment remains a first-class dashboard field in v0.5."""
    snapshot = DashboardSnapshot(
        embodiment=EmbodimentMetrics(
            environment_kind="simulated",
            active_sensors=2,
            active_actuators=1,
            episode=4,
            last_reward=0.75,
            last_action="move-left",
        )
    )
    payload = snapshot.to_json()
    embodiment = payload["embodiment"]
    assert isinstance(embodiment, dict)
    assert embodiment["environment_kind"] == "simulated"
    assert embodiment["episode"] == 4
