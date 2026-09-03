from __future__ import annotations

from pathlib import Path


STATIC_ROOT = Path(__file__).resolve().parents[1] / "src" / "dashboard" / "static"


def _read(name: str) -> str:
    return (STATIC_ROOT / name).read_text(encoding="utf-8")


def test_learning_studio_is_loaded_through_existing_workspace_module() -> None:
    workspace = _read("workspace-panels.js")
    studio = _read("learning-studio.js")

    assert 'from "./learning-studio.js"' in workspace
    assert "ensureLearningStudio();" in workspace
    assert "renderLearningStudio(state);" in workspace
    assert 'data-tab="learning"' in studio
    assert 'section.id = "tab-learning"' in studio
    assert 'button.addEventListener("click", activateLearningTab)' not in studio

    app = _read("app.js")
    assert "navigation.addEventListener('click'" in app
    assert "document.querySelectorAll('.tab-content')" in app
    assert "el.id === `tab-${tabName}`" in app
    assert "el.hidden = !active" in app


def test_learning_studio_ai_is_visibly_proposal_only_and_non_executing() -> None:
    studio = _read("learning-studio.js")

    assert "PROPOSAL ONLY" in studio
    assert "AI PROPOSAL · NOT APPLIED" in studio
    assert 'fetch("/api/research/chat"' in studio
    assert 'action: "ask"' in studio
    assert "never provide synaptic weights" in studio
    assert "reward values" in studio

    # The Learning Studio must not expose a learning-run or mutation endpoint.
    assert "/api/learning/execute" not in studio
    assert "/api/learning/apply" not in studio
    assert "execute_registered_experiment" not in studio


def test_learning_studio_exposes_pre_post_and_holdout_diagnostics() -> None:
    studio = _read("learning-studio.js")

    for expected in (
        "Pre Task Baseline",
        "Pre Impulse Probe",
        "Temporal Reference",
        "Post Task Evaluation",
        "Post Impulse Probe",
        "Holdout / Generalization",
    ):
        assert expected in studio


def test_learning_studio_prepare_form_and_reset_are_wired() -> None:
    studio = _read("learning-studio.js")

    for field_id in (
        "learning-goal",
        "learning-success-metric",
        "learning-source-notes",
        "learning-constraints",
    ):
        assert f'id="{field_id}"' in studio
        assert f'byId("{field_id}")' in studio
    assert 'id="learning-ai-prepare"' in studio
    assert 'id="learning-clear-proposal"' in studio
