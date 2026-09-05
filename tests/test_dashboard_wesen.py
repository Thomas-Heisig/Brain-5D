from pathlib import Path

STATIC = Path(__file__).parents[1] / "src" / "dashboard" / "static"


def test_wesen_workspace_is_loaded_from_dashboard_module_graph() -> None:
    console = (STATIC / "console-log.js").read_text(encoding="utf-8")
    assert 'import "./wesen.js"' in console
    assert '"/wesen.css"' in console
    assert '"/wesen-adaptive.css"' in console


def test_wesen_is_read_only_and_uses_real_observation_endpoints() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    assert 'wesenReadJson("/api/status"' in source
    assert 'wesenReadJson("/api/embodiment/state"' in source
    assert 'wesenReadJson("/api/embodiment/connections"' in source
    assert 'method: "POST"' not in source
    assert 'method: "PUT"' not in source
    assert 'method: "DELETE"' not in source
    assert "/api/control" not in source


def test_wesen_has_dynamic_machine_native_morphology() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    for token in (
        "dynamicNodes",
        "classifyConnection",
        "layoutNodes",
        "membranePath",
        "recordMorphology",
        "adaptiveProfile",
        'kind: "sensor"',
        'kind: "actuator"',
    ):
        assert token in source
    assert "WESEN_POLL_MS = 750" in source
    assert "sensor-placeholder" in source
    assert "actuator-placeholder" in source


def test_wesen_has_loopback_causality_zoom_and_history_surfaces() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-adaptive.css").read_text(encoding="utf-8")
    assert "renderEcho" in source
    assert "renderSignals" in source
    assert "show-causality" in source
    assert "wheel" in source
    assert "state.zoom" in source
    assert "wesen-morphology-history" in source
    assert ".wesen-self-body" in styles
    assert ".wesen-data-pin" in styles
    assert ".wesen-history" in styles


def test_primary_frontend_hides_network_and_moves_release_to_footer() -> None:
    console = (STATIC / "console-log.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen.css").read_text(encoding="utf-8")
    assert 'data-tab="network"' in console
    assert 'data-tab="gate"' in console
    assert ".remove()" in console
    assert "dataset.footerRelease" in console
    assert "wesen-release-button" in console
    assert '.tab-btn[data-tab="network"]' in styles
    assert '.tab-btn[data-tab="gate"]' in styles


def test_embodiment_is_presented_as_simple_technical_surface() -> None:
    console = (STATIC / "console-log.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen.css").read_text(encoding="utf-8")
    assert (
        "Embodiment bleibt die einfache technische Schnittstellen-Seite" in console
    )
    assert "#tab-embodiment .anatomy-zone" in styles
    assert "#tab-embodiment .legacy-embodiment-details" in styles


def test_wesen_design_is_theme_responsive_and_reduced_motion_safe() -> None:
    styles = (STATIC / "wesen.css").read_text(encoding="utf-8")
    adaptive = (STATIC / "wesen-adaptive.css").read_text(encoding="utf-8")
    assert 'body[data-theme="light"]' in styles
    assert "@media (max-width: 1050px)" in styles
    assert "@media (max-width: 820px)" in styles
    assert "prefers-reduced-motion" in adaptive
