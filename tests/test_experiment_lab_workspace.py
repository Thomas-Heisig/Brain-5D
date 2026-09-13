from pathlib import Path

STATIC = Path("src/dashboard/static")


def test_experiment_lab_has_linear_scientific_workflow() -> None:
    source = (STATIC / "frontend" / "modules" / "experiment-lab.js").read_text(encoding="utf-8")
    for stage in (
        'id: "overview"',
        'id: "question"',
        'id: "plan"',
        'id: "run"',
        'id: "series"',
        'id: "results"',
        'id: "evidence"',
    ):
        assert stage in source
    assert "DATA → Analyse → Human Review → EVIDENCE" in source


def test_experiment_lab_reuses_existing_backend_bound_controls() -> None:
    source = (STATIC / "frontend" / "modules" / "experiment-lab.js").read_text(encoding="utf-8")
    for selector in (
        "#workflow-research-catalog",
        "#workflow-research-contract",
        "#workflow-experiment-library",
        "#workflow-result-actions",
        "#workflow-human-review",
        "#workflow-rq-proposal",
        "#workflow-review-inbox",
        ".research-gateway-experiment",
    ):
        assert selector in source
    assert "workflow-question" in source
    assert "workflow-hypothesis" in source


def test_experiment_lab_isolates_one_stage_at_a_time() -> None:
    source = (STATIC / "frontend" / "modules" / "experiment-lab.js").read_text(encoding="utf-8")
    assert "function setVisibility" in source
    assert 'document.querySelectorAll("[data-lab-stage]")' in source
    assert "panel.dataset.labStage === stageId" in source
    assert "node.hidden = !visible" in source
    assert 'node.setAttribute("aria-hidden"' in source
    assert "node.inert = !visible" in source


def test_experiment_lab_removes_old_mixed_research_surfaces() -> None:
    source = (STATIC / "frontend" / "modules" / "experiment-lab.js").read_text(encoding="utf-8")
    assert 'host.querySelectorAll(".research-lanes, .research-focus-rail")' in source
    assert 'source.classList.remove("card")' in source
    assert 'source.classList.add("experiment-lab-source")' in source


def test_scientific_metrics_are_relocated_to_observatory() -> None:
    source = (STATIC / "frontend" / "modules" / "experiment-lab.js").read_text(encoding="utf-8")
    assert 'metrics.dataset.mhrnRoute = "science:observatory"' in source
    assert "research.appendChild(metrics)" in source
    assert 'document.body.dataset.currentRoute === "observatory"' in source


def test_experiment_lab_css_flattens_nested_legacy_cards() -> None:
    css = (STATIC / "frontend" / "styles" / "experiment-lab.css").read_text(encoding="utf-8")
    assert ".experiment-lab-panel" in css
    assert ".experiment-lab-flat-content" in css
    assert ".research-catalog-selector" in css
    assert ".experiment-library-card" in css
    assert "border-radius: 0 !important" in css
    assert ".experiment-lab-source" in css
    assert "display: none !important" in css


def test_experiment_lab_is_loaded_by_frontend() -> None:
    frontend = (STATIC / "frontend" / "index.js").read_text(encoding="utf-8")
    styles = (STATIC / "frontend" / "styles" / "index.css").read_text(encoding="utf-8")
    assert 'import { initExperimentLab } from "./modules/experiment-lab.js";' in frontend
    assert "initExperimentLab();" in frontend
    assert "experiment-lab.css" in styles
