from pathlib import Path

from src.research.protocol_registry import protocol_catalog

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "dashboard" / "static"
RESEARCH = ROOT / "research"


def test_operational_protocols_expose_prefill_templates() -> None:
    catalog = protocol_catalog(RESEARCH)
    assert catalog
    for protocol in catalog:
        minimum = protocol["minimum_independent_seeds"]
        assert minimum >= 1
        assert protocol["default_seed_expression"]
        assert "standard" in protocol["condition_profiles"]
        assert protocol["condition_profiles"]["standard"]


def test_experiment_workflow_wrapper_prefills_seed_and_condition_controls() -> None:
    source = (STATIC / "experiment-workflow.js").read_text(encoding="utf-8")
    assert 'from "./experiment-workflow-base.js"' in source
    assert "default_seed_expression" in source
    assert "condition_profiles" in source
    assert "_configureConditionProfiles" in source
    assert "Exploratory / diagnostic protocol" in source
    assert "<details" in source


def test_wesen_shell_merges_embodiment_and_moves_utilities_to_footer() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    assert 'import "./wesen-base.js"' in source
    assert "mergeEmbodimentIntoWesen" in source
    assert 'byId("tab-embodiment")' in source
    assert 'data-footer-tab="settings"' in source
    assert 'data-footer-tab="gate"' in source
    assert 'data-tab="embodiment"' in source
    assert "embodimentButton?.remove()" in source


def test_dashboard_has_theme_safe_three_column_wesen_and_scientific_reader() -> None:
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    wesen = (STATIC / "wesen.css").read_text(encoding="utf-8")
    reader = (STATIC / "scientific-reader.js").read_text(encoding="utf-8")
    assert 'import { initScientificReader } from \'./scientific-reader.js\';' in app
    assert "initScientificReader();" in app
    assert 'id="scientific-reader-toggle"' in html
    assert "grid-template-columns: minmax(165px, .8fr) minmax(360px, 1.7fr) minmax(190px, .9fr)" in wesen
    assert "body[data-theme=\"light\"]" in wesen
    assert "body.contrast-mode" in wesen
    assert "buildReaderText" in reader
    assert "text/plain;charset=utf-8" in reader
    assert "DATA-Artefakt" in reader


def test_project_timeline_is_wired_to_canonical_project_documents() -> None:
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    timeline = (STATIC / "project-timeline.js").read_text(encoding="utf-8")
    popups = (STATIC / "utility-popups.js").read_text(encoding="utf-8")
    assert "initProjectTimeline" in app
    assert "initUtilityPopups" in app
    assert 'id="tab-gate"' in html
    assert '<section class="project-timeline release-timeline"' in html
    assert html.index('id="tab-gate"') < html.index('id="project-timeline"')
    assert 'data-utility-release-view="summary"' in html
    assert 'data-utility-release-view="timeline"' in html
    assert 'data-utility-release-view="gate"' in html
    assert 'data-timeline-horizon="past"' in html
    assert 'data-timeline-horizon="future"' in html
    assert 'data-timeline-horizon="elements"' in html
    assert 'id="release-summary-criteria"' in html
    assert 'id="release-summary-blockers"' in html
    assert 'id="release-summary-next"' in html
    assert 'data-timeline-filter="changelog"' in html
    assert 'data-timeline-filter="roadmap"' in html
    assert 'data-timeline-filter="todo"' in html
    assert 'path: "07-changelog/CHANGELOG.md"' in timeline
    assert 'path: "08-roadmap/ROADMAP.md"' in timeline
    assert 'path: "08-roadmap/TODO.md"' in timeline
    assert 'activeHorizon: "timeline"' in timeline
    assert 'data-timeline-horizon' in timeline
    assert 'gate: { kicker: "VERIFY", title: "Release" }' in popups
    assert 'settings: { kicker: "CONFIGURE", title: "Scientific Settings" }' in popups


def test_dashboard_boxes_have_persistent_minimize_maximize_contract() -> None:
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    controls = (STATIC / "box-controls.js").read_text(encoding="utf-8")
    shell = (STATIC / "dashboard-shell.css").read_text(encoding="utf-8")
    wesen = (STATIC / "wesen.js").read_text(encoding="utf-8")
    assert "initBoxControls" in app
    assert "localStorage" in controls
    assert 'data-box-action="minimize"' in controls
    assert 'data-box-action="maximize"' in controls
    assert 'document.querySelectorAll(".b5d-box-maximized")' in controls
    assert ".b5d-box-maximized" in shell
    assert "wesen-technical-boundary-signals" in wesen
