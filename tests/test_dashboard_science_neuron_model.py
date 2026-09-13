"""Regression coverage for the scientific Stage-0 cell-model workbench."""

from __future__ import annotations

from pathlib import Path

STATIC = Path(__file__).parent.parent / "src" / "dashboard" / "static"


def _read(path: str) -> str:
    return (STATIC / path).read_text(encoding="utf-8")


def test_scientific_frontend_initializes_cell_model_module() -> None:
    frontend = _read("frontend/index.js")
    assert 'import { initNeuronModelScience } from "./modules/neuron-model-science.js";' in frontend
    assert "initNeuronModelScience();" in frontend


def test_cell_model_is_a_network_workbench_view() -> None:
    module = _read("frontend/modules/neuron-model-science.js")
    assert 'data-workspace-views="network"' in module
    assert 'button.dataset.workspaceView = "cellmodel"' in module
    assert 'button.textContent = "Cell Model"' in module
    assert 'panel.dataset.networkView = "cellmodel"' in module
    assert 'panel.id = "mhrn-neuron-model-science"' in module


def test_cell_model_workbench_is_independent_of_legacy_parameter_inspector() -> None:
    module = _read("frontend/modules/neuron-model-science.js")
    assert 'readJson("/api/parameters")' in module
    assert 'readJson("/api/parameters/pending")' in module
    assert '"/api/parameters/pending/apply"' in module
    assert '"/api/parameters/pending/save-profile"' in module
    assert '"/api/parameters/pending/cancel"' in module
    assert "ParameterInspector" not in module
    assert "parameter-inspector-card" not in module


def test_cell_model_workbench_exposes_supported_treatments_and_shared_controls() -> None:
    module = _read("frontend/modules/neuron-model-science.js")
    for token in (
        '"izhikevich-2003"',
        '"lif-current-v1"',
        'maturity: "canonical"',
        'maturity: "experimental"',
        '"neuron.izhikevich_threshold"',
        '"neuron.lif_tau_m_ms"',
        '"neuron.lif_threshold"',
        '"neuron.refractory_ticks"',
        '"neuron.enable_threshold_adaptation"',
        '"neuron.enable_energy_dynamics"',
        '"neuron.enable_traces"',
        '"neuron.enable_homeostasis"',
    ):
        assert token in module


def test_cell_model_workbench_keeps_scientific_boundary_visible() -> None:
    module = _read("frontend/modules/neuron-model-science.js")
    assert "scientifically sensitive" in module
    assert "require a new run/restart" in module
    assert "do not constitute biological validation" in module
    assert "matched model comparisons" in module


def test_cell_model_shared_styles_support_science_action_bar() -> None:
    styles = _read("neuron-model-settings.css")
    assert ".neuron-model-actions--science" in styles
    assert "repeat(4, auto)" in styles
    assert "@media (max-width: 720px)" in styles
