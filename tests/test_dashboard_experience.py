from pathlib import Path

STATIC = Path(__file__).parents[1] / "src" / "dashboard" / "static"
TABS = (
    "overview",
    "network",
    "control",
    "research",
    "gate",
    "settings",
    "embodiment",
)


def test_experience_layer_covers_every_workspace() -> None:
    source = (STATIC / "dashboard-experience.js").read_text(encoding="utf-8")
    for tab in TABS:
        assert f"{tab}:" in source
    assert "activateWorkspace" in source
    assert "Command palette" in source
    assert "Keyboard shortcuts" in source
    assert "Focus mode" in source


def test_experience_layer_is_presentation_only() -> None:
    source = (STATIC / "dashboard-experience.js").read_text(encoding="utf-8")
    assert "fetch(" not in source
    assert "XMLHttpRequest" not in source
    assert 'method: "POST"' not in source
    assert 'method: "PUT"' not in source
    assert 'method: "DELETE"' not in source
    assert "/api/control" not in source
    assert "/api/runtime" not in source


def test_experience_unknown_state_is_explicit() -> None:
    source = (STATIC / "dashboard-experience.js").read_text(encoding="utf-8")
    css = (STATIC / "dashboard-experience.css").read_text(encoding="utf-8")
    assert "experience-unknown-state" in source
    assert "Noch kein beobachteter Wert verfügbar" in source
    assert ".experience-unknown-state" in css


def test_experience_has_responsive_and_accessible_contracts() -> None:
    css = (STATIC / "dashboard-experience.css").read_text(encoding="utf-8")
    assert 'body[data-theme="light"]' in css
    assert "@media (max-width: 1180px)" in css
    assert "@media (max-width: 820px)" in css
    assert "@media (max-width: 520px)" in css
    assert "prefers-reduced-motion" in css
    assert ".experience-dialog::backdrop" in css


def test_experience_is_loaded_from_dashboard_module_graph() -> None:
    console_log = (STATIC / "console-log.js").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    assert 'import "./dashboard-experience.js"' in console_log
    assert "console-log.js" in app


def test_experience_workspace_status_never_targets_body_state() -> None:
    source = (STATIC / "dashboard-experience.js").read_text(encoding="utf-8")
    assert ".experience-status-copy [data-experience-workspace]" in source
    assert 'document.querySelectorAll("[data-experience-workspace]")' not in source
