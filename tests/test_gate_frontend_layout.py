from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_board_uses_full_release_workspace_width() -> None:
    css = (ROOT / "src/dashboard/static/styles.css").read_text(encoding="utf-8")
    assert ".gate-board {\n  width: 100%;\n  max-width: none;\n  margin: 0;\n}" in css
    assert ".release-gate-panel {\n  width: 100%;\n  max-width: none;\n}" in css


def test_next_version_todo_is_opened_without_reopening_closed_gate() -> None:
    todo = (ROOT / "docs/08-roadmap/TODO.md").read_text(encoding="utf-8")
    assert "Current release-blocking backlog:** **0**" in todo
    assert "## Next development milestone — v0.6 Scaling & Deterministic Performance" in todo
    assert "- [ ] Freeze the v0.6 compatibility contract" in todo
