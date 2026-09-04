from pathlib import Path


STATIC = Path(__file__).parents[1] / "src" / "dashboard" / "static"


def test_dashboard_shell_covers_every_primary_tab() -> None:
    source = (STATIC / "dashboard-shell.js").read_text(encoding="utf-8")
    for tab in (
        "overview",
        "network",
        "control",
        "research",
        "gate",
        "settings",
        "embodiment",
    ):
        assert f"{tab}:" in source
        assert f"tab-${{tabName}}" in source


def test_dashboard_shell_is_full_width_and_responsive() -> None:
    css = (STATIC / "dashboard-shell.css").read_text(encoding="utf-8")
    assert "max-width: none !important" in css
    assert "grid-template-columns: repeat(7, minmax(0, 1fr))" in css
    assert "@media (max-width: 1180px)" in css
    assert "@media (max-width: 820px)" in css
    assert "@media (max-width: 520px)" in css
    assert "prefers-reduced-motion" in css


def test_dashboard_shell_has_dark_and_light_design_contracts() -> None:
    css = (STATIC / "dashboard-shell.css").read_text(encoding="utf-8")
    assert ":root {" in css
    assert 'body[data-theme="light"]' in css
    assert "--shell-surface" in css
    assert "--shell-text" in css
    assert "--shell-accent" in css


def test_dashboard_shell_does_not_issue_runtime_commands() -> None:
    source = (STATIC / "dashboard-shell.js").read_text(encoding="utf-8")
    forbidden = (
        'fetch("/api/control',
        "fetch('/api/control",
        'fetch("/api/runtime',
        "fetch('/api/runtime",
        'method: "POST"',
        "method: 'POST'",
        'method: "DELETE"',
        "method: 'DELETE'",
        'method: "PUT"',
        "method: 'PUT'",
    )
    for token in forbidden:
        assert token not in source


def test_dashboard_shell_is_loaded_from_main_dashboard_module_graph() -> None:
    console_log = (STATIC / "console-log.js").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    assert 'import "./dashboard-shell.js";' in console_log
    assert "console-log.js" in app
