"""Regression tests for effective learning configuration preservation."""

from __future__ import annotations

from pathlib import Path

from src.config.loader import load_config
from src.learning.learning_engine import LearningParameters


def test_live_profile_preserves_all_learning_enable_flags() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_config(root / "configs" / "poc_alpha5_live.yaml")
    params = LearningParameters.from_config(config)

    assert config.get("stdp", {}).get("enabled") is True
    assert config.get("eligibility", {}).get("enabled") is True
    assert config.get("reward", {}).get("enabled") is True
    assert params.stdp_enabled is True
    assert params.eligibility_enabled is True
    assert params.reward_enabled is True
    assert params.reward_delay_ticks == 5
    assert config.get("dashboard", {}).get("state_publish_interval_ticks") == 10
    assert (
        config.get("dashboard", {})
        .get("live_telemetry", {})
        .get("capture_interval_ticks")
        == 20
    )
    assert config.get("state_mode", "operator") == "operator"
    assert config.get("observability", "minimal") == "minimal"
