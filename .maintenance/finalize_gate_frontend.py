from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


styles = ROOT / "src/dashboard/static/styles.css"
replace_once(
    styles,
    ".gate-board {\n  max-width: 900px;\n  margin: 0 auto;\n}",
    ".gate-board {\n  width: 100%;\n  max-width: none;\n  margin: 0;\n}\n\n.release-gate-panel {\n  width: 100%;\n  max-width: none;\n}\n\n.release-gate-panel .gate-section,\n.release-gate-panel .gate-live-runtime {\n  width: 100%;\n}\n\n.release-gate-panel .gate-row {\n  grid-template-columns: minmax(360px, 3fr) minmax(90px, 0.55fr) minmax(130px, 0.75fr) minmax(140px, 0.8fr);\n}\n\n@media (max-width: 900px) {\n  .release-gate-panel .gate-row {\n    grid-template-columns: minmax(220px, 2.4fr) minmax(70px, 0.55fr) minmax(110px, 0.8fr) minmax(115px, 0.85fr);\n  }\n}",
)

todo = ROOT / "docs/08-roadmap/TODO.md"
todo_text = todo.read_text(encoding="utf-8")
marker = "## Future work is roadmap work, not an open release blocker\n"
if marker not in todo_text:
    raise RuntimeError("TODO future-work marker missing")
next_version = """## Next development milestone — v0.6 Scaling & Deterministic Performance\n\nThe reviewed v0.5.0a7 release gate is closed. The following checklist opens the **next version milestone**; these items are development targets, not retroactive blockers for the closed v0.5 gate.\n\n- [ ] Freeze the v0.6 compatibility contract for runtime state, snapshots and resumable runs.\n- [ ] Add reproducible scaling benchmarks across increasing neuron/synapse counts with explicit memory and tick-cost budgets.\n- [ ] Introduce bounded telemetry/storage compaction so long experiment histories never require an AI consumer to ingest unbounded `runs.json` files.\n- [ ] Persist one compact current-run packet plus immutable raw-run indexes with SHA-verified provenance.\n- [ ] Verify deterministic pause/resume/restart identity for the v0.6 runtime contract across supported Python versions.\n- [ ] Add performance regression thresholds for RuntimeController, structural phases, learning, storage and dashboard telemetry.\n- [ ] Make target-Hz pacing and unlimited mode observable with achieved-Hz/realtime-ratio acceptance criteria.\n- [ ] Add clean migration/rollback tests for all v0.6 persisted-state schema changes.\n- [ ] Require full Python 3.11/3.12/3.13, browser, type, lint, security, build and Docker gates before v0.6 release.\n- [ ] Generate the v0.6 release record only after the exact source-freeze CI and release-readiness snapshot are both green.\n\n"""
if "## Next development milestone — v0.6" not in todo_text:
    todo_text = todo_text.replace(marker, next_version + marker, 1)
    todo.write_text(todo_text, encoding="utf-8")

changelog = ROOT / "docs/07-changelog/CHANGELOG.md"
change_text = changelog.read_text(encoding="utf-8")
entry = """## 2026-09-08 — Gate board truth-source and full-width preparation\n\n- Expanded the Release/Gate board from the legacy 900 px cap to the full available workspace width while retaining responsive criterion columns.\n- Opened the actionable v0.6 Scaling & Deterministic Performance TODO milestone after closing the reviewed v0.5 gate.\n- Prepared regeneration of the canonical test/source freeze and CI-bound gate snapshot so the dashboard reports current verification rather than stale historical artifacts.\n\n"""
if entry not in change_text:
    changelog.write_text(change_text.replace("# Changelog\n\n", "# Changelog\n\n" + entry, 1), encoding="utf-8")

test_path = ROOT / "tests/test_gate_frontend_layout.py"
test_path.write_text(
    '''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\n\ndef test_gate_board_uses_full_release_workspace_width() -> None:\n    css = (ROOT / "src/dashboard/static/styles.css").read_text(encoding="utf-8")\n    assert ".gate-board {\\n  width: 100%;\\n  max-width: none;\\n  margin: 0;\\n}" in css\n    assert ".release-gate-panel {\\n  width: 100%;\\n  max-width: none;\\n}" in css\n\n\ndef test_next_version_todo_is_opened_without_reopening_closed_gate() -> None:\n    todo = (ROOT / "docs/08-roadmap/TODO.md").read_text(encoding="utf-8")\n    assert "Current release-blocking backlog:** **0**" in todo\n    assert "## Next development milestone — v0.6 Scaling & Deterministic Performance" in todo\n    assert "- [ ] Freeze the v0.6 compatibility contract" in todo\n''',
    encoding="utf-8",
)

(ROOT / ".maintenance/gate-finalize-ready").write_text("ready\n", encoding="utf-8")
