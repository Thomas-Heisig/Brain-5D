"""Frontend wiring regression tests for experiment-mode switching."""

from __future__ import annotations

from pathlib import Path

import pytest

STATIC_DIR = Path(__file__).parent.parent / "src" / "dashboard" / "static"


def _read_static(name: str) -> str:
    path = STATIC_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not found in static directory")
    return path.read_text(encoding="utf-8")


class TestExperimentModeFrontendWiring:
    def test_index_html_has_mode_buttons(self) -> None:
        html = _read_static("index.html")
        for mode in ("operator", "experiment", "debug"):
            assert f'data-mode="{mode}"' in html, f"Missing {mode} mode button"

    def test_app_js_owns_experiment_mode_lifecycle(self) -> None:
        app_js = _read_static("app.js")
        assert "import { ExperimentMode } from './experiment-mode.js'" in app_js
        assert "experimentMode: null" in app_js
        assert "instances.experimentMode = new ExperimentMode()" in app_js
        assert "instances.experimentMode.refresh()" in app_js

    def test_experiment_mode_js_does_not_self_initialize(self) -> None:
        experiment_js = _read_static("experiment-mode.js")
        assert "new ExperimentMode()" not in experiment_js
        assert "document.addEventListener" not in experiment_js
        assert "DOMContentLoaded" not in experiment_js

    def test_experiment_workflow_renders_science_suite_results(self) -> None:
        workflow_js = _read_static("experiment-workflow.js")
        app_js = _read_static("app.js")
        html = _read_static("index.html")
        assert "const runResult = result.result" in workflow_js
        assert "runResult.run_count" in workflow_js
        assert "result.result.start.tick" not in workflow_js
        assert "onCompleted" in workflow_js
        assert "refreshFileManager" in app_js
        assert 'id="fm-experiment-sort"' in html

    def test_release_summary_uses_canonical_status_sections(self) -> None:
        html = _read_static("index.html")
        app_js = _read_static("app.js")
        assert 'id="gate-scientific"' in html
        assert 'id="gate-ci"' in html
        assert 'id="gate-overall"' in html
        assert "data.scientific_gate" in app_js
        assert "data.ci_status?.status" in app_js
        assert "data.release_readiness?.overall" in app_js

    def test_plantuml_encoder_uses_existing_distribution(self) -> None:
        html = _read_static("index.html")
        assert "cdn.jsdelivr.net/npm/plantuml-encoder@1.4.0" in html
        assert "cdnjs.cloudflare.com/ajax/libs/plantuml-encoder" not in html

    def test_overview_command_center_is_store_driven(self) -> None:
        html = _read_static("index.html")
        app_js = _read_static("app.js")
        store_js = _read_static("state-store.js")
        overview_js = _read_static("overview-panel.js")

        for element_id in (
            "overview-runtime-status",
            "overview-health-status",
            "overview-scientific-status",
            "overview-ci-status",
            "overview-release-status",
            "overview-component-grid",
            "overview-problem-list",
        ):
            assert f'id="{element_id}"' in html
        assert "renderOverviewCommandCenter(state)" in app_js
        assert "setupOverviewActions()" in app_js
        assert 'fetch("/api/gate/status"' in store_js
        assert 'fetch("/api/experiment/mode"' in store_js
        assert "export function renderOverviewCommandCenter" in overview_js

    def test_major_workspaces_and_scientific_settings_are_wired(self) -> None:
        html = _read_static("index.html")
        app_js = _read_static("app.js")
        settings_js = _read_static("settings-panel.js")
        workspace_js = _read_static("workspace-panels.js")

        for tab in ("network", "control", "research", "gate", "settings"):
            assert f'data-tab="{tab}"' in html
            assert f'id="tab-{tab}"' in html
        assert 'id="settings-domain-filter"' in html
        assert 'id="settings-mode-selector"' in html
        assert 'id="parameter-inspector-card"' in html
        assert "new SettingsPanel(instances.parameterInspector)" in app_js
        assert "renderWorkspaceSummaries(state)" in app_js
        assert "class SettingsPanel" in settings_js
        assert "ExperimentAPI.setMode(mode)" in settings_js
        assert "renderWorkspaceSummaries" in workspace_js

    def test_unified_chrome_network_controls_and_embodiment_are_wired(self) -> None:
        html = _read_static("index.html")
        app_js = _read_static("app.js")
        store_js = _read_static("state-store.js")

        for element_id in (
            "nav-back",
            "nav-home",
            "help-toggle",
            "contrast-toggle",
            "projection-resolution",
            "histogram-bins",
            "projection-samples",
            "context-help",
        ):
            assert f'id="{element_id}"' in html
        assert 'data-tab="embodiment"' in html
        assert 'id="tab-embodiment"' in html
        assert "CONTRAST_KEY" in app_js
        assert "setupGlobalChrome()" in app_js
        assert "projection-resolution" in app_js
        assert "histogram-bins" in app_js
        assert "projection-samples" in app_js
        assert "embodiment: payload.embodiment || {}" in store_js

    def test_control_effects_use_current_runtime_telemetry_contract(self) -> None:
        control_js = _read_static("control-panel.js")
        assert "this.runtime?.controller_state" in control_js
        assert "this.runtime?.tick" in control_js
        assert "this.runtime?.queue_depth" in control_js
        assert "this.runtime?.completed_ticks" in control_js
        assert "this.runtime?.batch_duration_ms" in control_js

    def test_control_structural_strip_and_experiment_footer_are_wired(self) -> None:
        html = _read_static("index.html")
        experiment_js = _read_static("experiment-mode.js")
        workspace_js = _read_static("workspace-panels.js")

        assert '<details class="structural-live-card"' in html
        assert 'id="structural-live-strip"' in html
        assert 'id="footer-experiment"' in html
        assert 'id="footer-experiment-state"' in html
        assert 'id="footer-experiment-id"' in html
        assert 'id="control-causal-flow"' in html
        assert 'id="control-effects"' in html
        assert "footer.dataset.active = String(hasActive)" in experiment_js
        assert "footerExperiment.dataset.active" in workspace_js

    def test_stable_workspace_views_and_research_lanes_are_wired(self) -> None:
        html = _read_static("index.html")
        app_js = _read_static("app.js")
        styles = _read_static("styles.css")

        for view in ("visual", "dynamics", "inspect", "data"):
            assert f'data-workspace-view="{view}"' in html
            assert f'data-network-view="{view}"' in html
        for view in ("summary", "gate-a", "gate-b", "gate-c"):
            assert f'data-workspace-view="{view}"' in html
            assert f'data-release-view="{view}"' in html
        for query in ("EVID", "EXP", "MATRIX"):
            assert f'data-research-query="{query}"' in html
        assert "setupWorkspaceViews()" in app_js
        assert "setupResearchLanes()" in app_js
        assert "height: 1029px" in styles

    def test_embodiment_closed_loop_uses_read_only_endpoints(self) -> None:
        html = _read_static("index.html")
        store_js = _read_static("state-store.js")
        workspace_js = _read_static("workspace-panels.js")

        for phase in ("environment", "sensor", "encoder", "snn", "decoder", "actuator"):
            assert f'data-loop-node="{phase}"' in html
            assert f'id="embodiment-loop-{phase}"' in html
        assert 'fetch("/api/embodiment/state"' in store_js
        assert 'fetch("/api/embodiment/history?limit=100"' in store_js
        assert "embodimentDetail.loop" in workspace_js
        assert "embodimentHistory.history" in workspace_js
