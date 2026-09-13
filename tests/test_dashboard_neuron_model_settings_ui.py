"""Regression tests for the dedicated Stage-0 neuron model settings UI."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config.loader import DEFAULT_CONFIG
from src.dashboard.health_builder import build_parameters

STATIC_DIR = Path(__file__).parent.parent / "src" / "dashboard" / "static"


def _read_static(name: str) -> str:
    path = STATIC_DIR / name
    if not path.exists():
        pytest.fail(f"{name} not found in static directory")
    return path.read_text(encoding="utf-8")


def test_neuron_runtime_parameters_are_exposed_to_dashboard() -> None:
    parameters = build_parameters(DEFAULT_CONFIG)
    expected = {
        "neuron.model",
        "neuron.a",
        "neuron.b",
        "neuron.c",
        "neuron.d",
        "neuron.initial_v",
        "neuron.initial_u",
        "neuron.izhikevich_threshold",
        "neuron.lif_resting_potential",
        "neuron.lif_tau_m_ms",
        "neuron.lif_resistance",
        "neuron.lif_threshold",
        "neuron.lif_reset",
        "neuron.refractory_ticks",
        "neuron.enable_threshold_adaptation",
        "neuron.enable_energy_dynamics",
        "neuron.enable_traces",
        "neuron.enable_homeostasis",
    }
    assert expected <= set(parameters)
    for name in expected:
        assert parameters[name].scientific_sensitive is True


def test_neuron_model_editor_uses_declared_model_ids_and_pending_workflow() -> None:
    script = _read_static("parameter-inspector.js")

    assert '"izhikevich-2003"' in script
    assert '"lif-current-v1"' in script
    assert 'maturity: "canonical"' in script
    assert 'maturity: "experimental"' in script
    assert 'version: "mhrn-1.0"' in script
    assert 'ParameterAPI.proposeChange(name, value)' in script
    assert 'ParameterAPI.proposeChange("neuron.model"' not in script
    assert 'unsupported neuron model' in script
    assert 'requires a new run/restart' in script


def test_neuron_model_editor_exposes_model_specific_and_common_fields() -> None:
    script = _read_static("parameter-inspector.js")

    for name in (
        "neuron.a",
        "neuron.b",
        "neuron.c",
        "neuron.d",
        "neuron.izhikevich_threshold",
        "neuron.lif_resting_potential",
        "neuron.lif_tau_m_ms",
        "neuron.lif_resistance",
        "neuron.lif_threshold",
        "neuron.lif_reset",
        "neuron.refractory_ticks",
        "neuron.enable_threshold_adaptation",
        "neuron.enable_energy_dynamics",
        "neuron.enable_traces",
        "neuron.enable_homeostasis",
    ):
        assert f'"{name}"' in script

    assert 'data-settings-filter = "neuron."' not in script
    assert 'neuronFilter.dataset.settingsFilter = "neuron."' in script
    assert 'id="neuron-model-select"' in script
    assert 'id="neuron-model-fields"' in script
    assert 'id="neuron-model-stage"' in script


def test_neuron_model_editor_keeps_global_apply_and_profile_workflow() -> None:
    script = _read_static("parameter-inspector.js")

    assert '"/api/parameters/pending/apply"' in script
    assert '"/api/parameters/pending/save-profile"' in script
    assert "Stage neuron changes" in script
    assert "Review and apply them below" in script
    assert "Existing live neuron state is not silently rewritten" in script


def test_neuron_model_styles_are_responsive_and_state_aware() -> None:
    styles = _read_static("neuron-model-settings.css")

    assert ".neuron-model-settings" in styles
    assert '[data-maturity="canonical"]' in styles
    assert '[data-maturity="experimental"]' in styles
    assert '.neuron-model-status[data-state="error"]' in styles
    assert "@media (max-width: 720px)" in styles
