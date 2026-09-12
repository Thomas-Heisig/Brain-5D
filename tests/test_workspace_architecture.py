from pathlib import Path

STATIC = Path("src/dashboard/static")


def test_seven_first_class_workspaces_and_parameter_ownership() -> None:
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    for area in ("dashboard", "science", "wesen", "control", "release", "settings", "review"):
        assert f"  {area}: {{" in router
    assert 'number: "07"' in router
    assert '["parameters", "Parameter", "settings"]' in router
    assert 'owner: "appsettings"' in router
    assert 'owner: "review"' in router


def test_every_main_area_has_overview_howto_and_backend_contracts() -> None:
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert router.count('["overview", "Übersicht"') >= 7
    assert "howto:" in router
    assert "contracts:" in router
    for endpoint in (
        "/api/status", "/api/science/metrics", "/api/embodiment/state",
        "/api/control", "/api/gate/status", "/api/research/chat/settings",
        "/api/research/reviews",
    ):
        assert endpoint in router


def test_review_and_airr_frontend_match_backend_contracts() -> None:
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    tools = (STATIC / "frontend" / "modules" / "ai-report-tools.js").read_text(encoding="utf-8")
    assert "/api/research/reviews" in router
    assert "/api/research/external-review" in router
    assert '{ experiment_id: experimentId }' in tools
    assert "experiment_ref" not in tools
    assert "review_status: reviewStatus" in tools
    assert "encodeURIComponent(experimentId)" in tools
    assert "encodeURIComponent(reportId)" in tools


def test_learning_preparation_matches_guarded_nonexecuting_schema() -> None:
    source = (STATIC / "frontend" / "modules" / "learning-prep.js").read_text(encoding="utf-8")
    assert 'action: "create"' in source
    assert 'action: "approve"' in source
    assert "objective_id" in source
    assert "baseline_protocol" in source
    assert "evaluation_protocol" in source
    assert "approved_by" in source
    assert "learning_rate" not in source


def test_canonical_file_viewer_owns_docs_and_research_rendering() -> None:
    docs = (STATIC / "frontend" / "modules" / "docs-browser.js").read_text(encoding="utf-8")
    research = (STATIC / "frontend" / "modules" / "research-docs.js").read_text(encoding="utf-8")
    assert "brain5d:open-file" in docs
    assert "brain5d:open-file" in research
    assert "/api/docs-files/" not in docs
    assert "research-doc-viewer" not in research
    assert "json_path" in research


def test_panels_have_minimize_standard_maximize_fullscreen_and_info() -> None:
    source = (STATIC / "box-state-controller.js").read_text(encoding="utf-8")
    for label in ("Minimieren", "Standardgröße", "Maximieren", "Vollbild", "Information"):
        assert label in source
    assert "requestFullscreen" in source
    assert "box-info-popover" in source
    assert "research-workspace-tabs" not in source


def test_workspace_and_review_css_are_loaded() -> None:
    index = (STATIC / "frontend" / "styles" / "index.css").read_text(encoding="utf-8")
    assert 'workspace-architecture.css' in index
    review_css = STATIC / "review" / "review.css"
    assert review_css.is_file()
    assert "#f4efe6" in review_css.read_text(encoding="utf-8")
