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
