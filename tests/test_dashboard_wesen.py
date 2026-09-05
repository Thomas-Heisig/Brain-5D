from pathlib import Path

STATIC = Path(__file__).parents[1] / "src" / "dashboard" / "static"


def test_wesen_workspace_is_loaded_from_dashboard_module_graph() -> None:
    console = (STATIC / "console-log.js").read_text(encoding="utf-8")
    assert 'import "./wesen.js"' in console
    assert 'import "./wesen-organism-v2.js"' in console
    assert 'import "./wesen-anatomy-v3.js"' in console
    assert '"/wesen.css"' in console
    assert '"/wesen-adaptive.css"' in console
    assert '"/wesen-organism.css"' in console
    assert '"/wesen-anatomy-v3.css"' in console


def test_wesen_is_read_only_and_uses_real_observation_endpoints() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    organism = (STATIC / "wesen-organism-v2.js").read_text(encoding="utf-8")
    anatomy = (STATIC / "wesen-anatomy-v3.js").read_text(encoding="utf-8")
    assert 'wesenReadJson("/api/status"' in source
    assert 'wesenReadJson("/api/embodiment/state"' in source
    assert 'wesenReadJson("/api/embodiment/connections"' in source
    for endpoint in (
        "/api/embodiment/metrics",
        "/api/embodiment/history?limit=24",
        "/api/embodiment/pipeline",
        "/api/live/io-flow",
        "/api/live/population",
    ):
        assert endpoint in anatomy
    combined = source + organism + anatomy
    assert 'method: "POST"' not in combined
    assert 'method: "PUT"' not in combined
    assert 'method: "DELETE"' not in combined
    assert "/api/control" not in combined


def test_wesen_has_dynamic_machine_native_morphology() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    organism = (STATIC / "wesen-organism-v2.js").read_text(encoding="utf-8")
    for token in (
        "dynamicNodes",
        "classifyConnection",
        "recordMorphology",
        'kind: "sensor"',
        'kind: "actuator"',
    ):
        assert token in source
    for token in (
        "function layout",
        "function hullPath",
        "function satellites",
        "function ringRadius",
        "minDistance",
    ):
        assert token in organism
    assert "WESEN_POLL_MS = 750" in source
    assert "sensor-placeholder" in source
    assert "actuator-placeholder" in source


def test_wesen_has_icon_first_collision_safe_accessibility() -> None:
    organism = (STATIC / "wesen-organism-v2.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-organism.css").read_text(encoding="utf-8")
    for token in (
        "deviceType",
        "iconFor",
        "decorateNodes",
        "ensureIconDock",
        "bindKeyboard",
        "wesen-icon-dock",
        'setAttribute("aria-label"',
        'setAttribute("tabindex", "0")',
    ):
        assert token in organism
    assert "count < 8" in organism
    assert "7200" in organism
    assert "#wesen-organ-layer .wesen-organ-label" in styles
    assert "#wesen-organ-layer .wesen-organ-value" in styles
    assert "#wesen-pin-layer .wesen-data-pin" in styles
    assert ".wesen-icon-dock" in styles
    assert 'data-device-type="gpu"' in styles


def test_wesen_has_body_like_machine_anatomy() -> None:
    anatomy = (STATIC / "wesen-anatomy-v3.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-anatomy-v3.css").read_text(encoding="utf-8")
    for token in (
        "wesen-body-head",
        "wesen-body-torso",
        "wesen-body-spine",
        "wesen-body-limb",
        "bodyAnchor",
        '"head"',
        '"arm"',
        '"leg"',
        '"torso"',
    ):
        assert token in anatomy or token in styles
    assert "Sinneszone" not in anatomy  # visual semantics, not biological labeling
    assert "pointer-events: none" in styles


def test_wesen_empirical_overlay_uses_backend_data_without_fallback_values() -> None:
    anatomy = (STATIC / "wesen-anatomy-v3.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-anatomy-v3.css").read_text(encoding="utf-8")
    for token in (
        "sensory_integrity",
        "resource_pressure",
        "continuity_risk",
        "active_fraction",
        "spike_count",
        "input_rate",
        "output_rate",
        "LIVE_RUNTIME",
        "wesen-pipeline-body",
    ):
        assert token in anatomy
    assert 'return "—"' in anatomy
    assert "--wesen-pressure" in styles
    assert "--wesen-integrity" in styles
    assert "--wesen-continuity" in styles


def test_wesen_has_loopback_causality_camera_and_time_travel() -> None:
    source = (STATIC / "wesen.js").read_text(encoding="utf-8")
    organism = (STATIC / "wesen-organism-v2.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-organism.css").read_text(encoding="utf-8")
    assert "renderEcho" in source
    assert "show-causality" in organism
    assert "delayedClone" in organism
    assert "brain5d.wesen.morphology.v2" in organism
    assert "wesen-timeline" in organism
    assert "pointermove" in organism
    assert "stopImmediatePropagation" in organism
    assert "Kausal-Tracer" in organism
    assert ".wesen-satellite" in styles
    assert ".wesen-delayed-clone" in styles


def test_wesen_has_neutral_terminology_and_differentiated_states() -> None:
    organism = (STATIC / "wesen-organism-v2.js").read_text(encoding="utf-8")
    styles = (STATIC / "wesen-organism.css").read_text(encoding="utf-8")
    for term in (
        "SNN-Kern",
        "Adaptive Regelstruktur",
        "Sensor-Endpunkt",
        "Aktor-Endpunkt",
        "Interozeption",
    ):
        assert term in organism
    for state in (
        "thermal",
        "sensor-loss",
        "network-isolation",
        "actuator-fault",
        "recovery",
        "unknown",
        "pressure",
    ):
        assert state in organism
        assert state in styles


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
    assert "Embodiment bleibt die einfache technische Schnittstellen-Seite" in console
    assert "#tab-embodiment .anatomy-zone" in styles
    assert "#tab-embodiment .legacy-embodiment-details" in styles


def test_wesen_design_is_theme_responsive_and_reduced_motion_safe() -> None:
    styles = (STATIC / "wesen.css").read_text(encoding="utf-8")
    adaptive = (STATIC / "wesen-adaptive.css").read_text(encoding="utf-8")
    organism = (STATIC / "wesen-organism.css").read_text(encoding="utf-8")
    anatomy = (STATIC / "wesen-anatomy-v3.css").read_text(encoding="utf-8")
    assert 'body[data-theme="light"]' in styles
    assert "@media (max-width: 1050px)" in styles
    assert "@media (max-width: 820px)" in styles
    assert "prefers-reduced-motion" in adaptive
    assert "prefers-reduced-motion" in organism
    assert "prefers-reduced-motion" in anatomy
