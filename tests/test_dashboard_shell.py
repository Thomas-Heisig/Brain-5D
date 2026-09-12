from pathlib import Path

# fmt: off
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


def test_dashboard_shell_covers_every_primary_tab() -> None:
    source = (STATIC / "dashboard-shell.js").read_text(encoding="utf-8")
    for tab in TABS:
        assert f"{tab}:" in source
    assert "tab-${tabName}" in source


def test_dashboard_shell_is_full_width_and_responsive() -> None:
    css = (STATIC / "frontend" / "styles" / "shell.css").read_text(encoding="utf-8")
    # Shell CSS now provides structural display rules and utility classes.
    assert ".tab-content" in css
    assert ".is-hidden" in css
    assert ".tab-nav" in css


def test_dashboard_shell_has_dark_and_light_design_contracts() -> None:
    css = (STATIC / "frontend" / "styles" / "shell.css").read_text(encoding="utf-8")
    # Shell CSS provides utility classes for JS-driven display toggling.
    assert ".is-hidden" in css
    assert ".is-clickable" in css


def test_dashboard_shell_does_not_issue_runtime_commands() -> None:
    source = (STATIC / "dashboard-shell.js").read_text(encoding="utf-8")
    assert "fetch(" not in source
    assert "XMLHttpRequest" not in source


def test_dashboard_shell_is_loaded_from_main_dashboard_module_graph() -> None:
    console_log = (STATIC / "console-log.js").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "dashboard-shell.js" in console_log
    assert "console-log.js" in app


def test_dashboard_tabs_are_hidden_before_external_styles_load() -> None:
    """Tab visibility rules are now in shell.css, not inline in index.html."""
    css = (STATIC / "frontend" / "styles" / "shell.css").read_text(encoding="utf-8")
    assert ".tab-content { display: none; }" in css
    assert ".tab-content.active { display: block; }" in css
    # index.html must NOT contain inline <style> blocks
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "<style>" not in html


def test_print_styles_do_not_capture_screen_rules() -> None:
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert "color: black !important;\n  }\n}\n\n/* ============================================================================\n   BIBTEX VIEWER" in css


def test_bibtex_year_columns_reserve_four_digit_width() -> None:
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert ".bibtex-cell-year" in css
    assert "min-width: 5.5rem" in css
    assert "font-variant-numeric: tabular-nums" in css
    assert ".file-renderer-bibtex td:nth-child(4)" in css


def test_shared_speech_reader_covers_viewer_and_chat() -> None:
    speech = (STATIC / "speech-reader.js").read_text(encoding="utf-8")
    renderer = (STATIC / "file-renderer.js").read_text(encoding="utf-8")
    chat = (STATIC / "research-chat.js").read_text(encoding="utf-8")
    assert 'lang = "de-DE"' in speech
    assert "createSpeechControls" in renderer
    assert "createSpeechControls" in chat
    assert "speech-reader-status" in speech
# fmt: on
