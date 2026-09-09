from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_board_uses_full_release_workspace_width() -> None:
    css = (ROOT / "src/dashboard/static/styles.css").read_text(encoding="utf-8")
    assert ".gate-board {\n  width: 100%;\n  max-width: none;\n  margin: 0;\n}" in css
    assert ".release-gate-panel {\n  width: 100%;\n  max-width: none;\n}" in css


def test_next_version_todo_tracks_completed_engineering_without_faking_release() -> (
    None
):
    todo = (ROOT / "docs/08-roadmap/TODO.md").read_text(encoding="utf-8")
    assert "Current release-blocking backlog:** **0**" in todo
    assert (
        "## Current development milestone — v0.6 Scaling & Deterministic Performance"
        in todo
    )
    assert "- [x] Freeze the v0.6 compatibility contract" in todo
    assert (
        "Generate the v0.6 release record only after the exact source-freeze CI" in todo
    )
