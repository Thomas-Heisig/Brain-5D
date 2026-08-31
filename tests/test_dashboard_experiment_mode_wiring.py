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
