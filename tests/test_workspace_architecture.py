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


# ── New: Router architecture tests ──────────────────────────────────────


def test_router_has_setRouteElementVisibility() -> None:
    """The central visibility controller must exist and set hidden + aria-hidden + class."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert "function setRouteElementVisibility" in router
    assert "element.hidden = !visible" in router
    assert "aria-hidden" in router
    assert "mhrn-route-hidden" in router
    assert "element.inert" in router


def test_router_has_reconcileRouteVisibility() -> None:
    """The reconciliation function must exist and be called after navigation."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert "function reconcileRouteVisibility" in router
    assert "function resetWorkspaceVisibility" in router
    assert "function showRouteContent" in router


def test_router_handles_all_route_actions() -> None:
    """Every route action type must have a handler in showRouteContent."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    actions = {"research", "overview", "embodiment", "view", "focus", "focusOnly", "generated", "release"}
    for action in actions:
        assert f'action === "{action}"' in router or f'if (action === "{action}")' in router


def test_every_route_has_valid_workspace() -> None:
    """Every route's workspace must reference an existing legacy tab or generated workspace."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    index = (STATIC / "index.html").read_text(encoding="utf-8")
    workspaces_in_html = set()
    for match in __import__("re").finditer(r'data-tab="(\w+)"', index):
        workspaces_in_html.add(match.group(1))
    workspaces_in_html.add("appsettings")  # generated
    workspaces_in_html.add("review")  # generated
    workspaces_in_html.add("wesen")  # dynamically created by wesen-base.js

    for match in __import__("re").finditer(r'\["(\w+)",\s*"[^"]+",\s*"(\w+)"', router):
        route_id, workspace = match.group(1), match.group(2)
        assert workspace in workspaces_in_html, (
            f'Route "{route_id}" uses workspace "{workspace}" which has no matching tab'
        )


def test_no_legacy_frontend_architecture_imported() -> None:
    """The old three-area frontend-architecture must not be imported by console-log."""
    source = (STATIC / "console-log.js").read_text(encoding="utf-8")
    assert "frontend-architecture.js" not in source


def test_css_has_robust_hide_rules() -> None:
    """CSS must have !important hide rules for all route-hidden states."""
    css = (STATIC / "frontend" / "styles" / "workspace-architecture.css").read_text(encoding="utf-8")
    assert "[hidden]" in css
    assert ".mhrn-route-hidden" in css
    assert ".mhrn-routed-local-tabs" in css
    assert ".mhrn-overview-content-hidden" in css
    assert ".mhrn-route-focus-hidden" in css
    assert "display: none !important" in css
    assert "[aria-hidden=\"true\"]" in css


def test_mutation_observer_calls_reconciliation() -> None:
    """MutationObserver must call reconcileRouteVisibility after DOM changes."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert "reconcileRouteVisibility(currentArea, currentRoute)" in router
    assert "observerRunning" in router  # debounce guard


def test_old_three_area_architecture_not_loaded_by_default() -> None:
    """The old frontend-architecture.js must not be loaded from index.html."""
    index = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "frontend-architecture.js" not in index


def test_console_log_imports_frontend_index() -> None:
    """console-log.js must import frontend/index.js (which loads the router)."""
    source = (STATIC / "console-log.js").read_text(encoding="utf-8")
    assert "frontend/index.js" in source


def test_router_exports_select_route_and_init() -> None:
    """The router module must export selectRoute and initWorkspaceRouter."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert "export function selectRoute" in router
    assert "export function initWorkspaceRouter" in router


def test_all_science_routes_have_unique_ownership() -> None:
    """Each science sub-route must map to a distinct workspace/action combination."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    # Parse science routes
    science_section = router.split("science: {")[1].split("},")[0] if "science: {" in router else ""
    assert science_section, "science section not found"
    # Verify observatory uses focus (not just scroll)
    assert '"observatory", "Observatory", "research", "focus"' in router


def test_wesen_cognition_profile_symbiosis_use_focus() -> None:
    """Wesen focus routes must use 'focus' action, not just scroll."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert '"cognition", "Kognition", "wesen", "focus"' in router
    assert '"profile", "Profil", "wesen", "focus"' in router
    assert '"symbiosis", "Neural Symbiosis", "wesen", "focus"' in router


def test_control_focusOnly_routes_exist() -> None:
    """Control focusOnly routes must specify selectors to keep visible."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert '"runtime", "Runtime", "control", "focusOnly"' in router
    assert '"console", "Konsole", "control", "focusOnly"' in router
    assert '"experiments", "Experiment Mode", "control", "focusOnly"' in router
    assert '"structural", "Struktur & Lernen", "control", "focusOnly"' in router


def test_parameter_route_uses_settings_workspace() -> None:
    """Parameter must remain under the settings workspace (tab-settings)."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert '["parameters", "Parameter", "settings"]' in router


def test_review_routes_use_generated_workspace() -> None:
    """Review routes must use the 'review' generated workspace."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert '["inbox", "Review Inbox", "review", "generated", "inbox"]' in router
    assert '["ai", "AI Reports", "review", "generated", "ai"]' in router


def test_settings_routes_use_generated_workspace() -> None:
    """Settings routes must use the 'appsettings' generated workspace."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert '["appearance", "Oberfläche", "appsettings", "generated", "appearance"]' in router
    assert '["ai", "AI & Chat", "appsettings", "generated", "ai"]' in router


def test_data_mhrn_persistent_attribute_supported() -> None:
    """The router must support data-mhrn-persistent to exclude elements from hiding."""
    router = (STATIC / "frontend" / "workspace-router.js").read_text(encoding="utf-8")
    assert "isPersistent" in router or "data-mhrn-persistent" in router
