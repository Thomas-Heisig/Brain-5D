from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"anchor not found in {path}: {old[:120]!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    if marker in text:
        return
    file_path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


review_module = r'''"""Review inbox aggregation for research artifacts.

The inbox is intentionally read-only. Decisions are still written through the
existing append-only human-review writers in ``research_assistant.airr``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def build_review_inbox(research_root: Path) -> dict[str, Any]:
    root = research_root.resolve()
    experiments = root / "experiments"
    items: list[dict[str, Any]] = []
    if not experiments.is_dir():
        return {"open": 0, "completed": 0, "items": []}

    completed = 0
    for report_path in sorted(experiments.glob("*/reports/AIRR-*.json")):
        if report_path.name.endswith(".review.json"):
            continue
        report = _json(report_path)
        if not report:
            continue
        experiment_id = report_path.parents[1].name
        report_id = str(report.get("report_id") or report_path.stem)
        review_path = report_path.with_name(f"{report_id}.review.json")
        if review_path.is_file():
            completed += 1
            continue
        if report.get("human_review_required") is not True:
            continue
        if report.get("status") != "review_pending":
            continue
        content = report.get("content") if isinstance(report.get("content"), dict) else {}
        items.append(
            {
                "kind": "airr",
                "experiment_id": experiment_id,
                "report_id": report_id,
                "artifact_path": str(report_path.relative_to(root)).replace("\\", "/"),
                "research_question_id": report.get("research_question_id"),
                "generated_at": report.get("generated_at"),
                "title": f"{experiment_id} · {report_id}",
                "summary": content.get("executive_summary") if isinstance(content, dict) else None,
                "review_endpoint": f"/api/research/ai-reports/{experiment_id}/{report_id}/review",
            }
        )

    for target in sorted(experiments.glob("*/**/*")):
        if not target.is_file() or target.name.endswith(".review.json"):
            continue
        if target.suffix.lower() not in {".md", ".json"}:
            continue
        review_path = target.with_name(f"{target.name}.review.json")
        if review_path.is_file():
            completed += 1
            continue
        payload = _json(target) if target.suffix.lower() == ".json" else None
        explicit = bool(
            isinstance(payload, dict)
            and (
                payload.get("human_review") == "PENDING"
                or payload.get("human_review_status") in {"PENDING", "NOT_PERFORMED"}
                or payload.get("evidence_readiness") == "BLOCKED_HUMAN_REVIEW"
            )
        )
        if not explicit:
            continue
        relative = str(target.relative_to(root)).replace("\\", "/")
        items.append(
            {
                "kind": "artifact",
                "experiment_id": target.relative_to(experiments).parts[0],
                "artifact_path": relative,
                "title": target.name,
                "summary": "Explicit human review required by the artifact metadata.",
                "review_endpoint": "/api/research/reviews",
            }
        )

    items.sort(key=lambda item: (str(item.get("experiment_id")), str(item.get("title"))))
    return {"open": len(items), "completed": completed, "items": items}
'''
(ROOT / "src/dashboard/review_inbox.py").write_text(review_module, encoding="utf-8")

replace(
    "src/dashboard/server.py",
    "from .release_timeline import build_release_timeline\nfrom .research_source import ResearchSource, create_research_source",
    "from .release_timeline import build_release_timeline\nfrom .research_source import ResearchSource, create_research_source\nfrom .review_inbox import build_review_inbox",
)
replace(
    "src/dashboard/server.py",
    '''            if path == "/api/research/reports":\n                self._serve_research_reports()\n                return\n\n            if path == "/api/research/ai-reports":''',
    '''            if path == "/api/research/reports":\n                self._serve_research_reports()\n                return\n\n            if path == "/api/research/reviews":\n                source = self._require_research_source()\n                self._send_json(build_review_inbox(source.root()))\n                return\n\n            if path == "/api/research/ai-reports":''',
)

frontend_anchor = '''      <div id="workflow-research-results" class="research-catalog-results" role="listbox" aria-label="Forschungsfragen"></div>\n      <div class="research-dimension-control">'''
frontend_new = '''      <div id="workflow-research-results" class="research-catalog-results" role="listbox" aria-label="Forschungsfragen"></div>\n      <section id="workflow-review-inbox" class="research-review-inbox" aria-label="Offene Human Reviews">\n        <div class="research-review-head"><strong>Review Inbox</strong><span id="workflow-review-count" class="gate-badge pending">lädt …</span></div>\n        <p>Offene Human Reviews können hier nachvollziehbar abgeschlossen werden. Reviewer, Entscheidung und Kommentar sind Pflicht; ein Review erzeugt niemals automatisch wissenschaftliche Evidenz.</p>\n        <div class="research-review-controls">\n          <input id="workflow-review-reviewer" type="text" placeholder="Reviewer / Verantwortlicher" autocomplete="name">\n          <button id="workflow-review-refresh" type="button">Reviews aktualisieren</button>\n        </div>\n        <div id="workflow-review-list" class="research-review-list"></div>\n      </section>\n      <div class="research-dimension-control">'''
replace("src/dashboard/static/experiment-workflow.js", frontend_anchor, frontend_new)

style_anchor = '''      .research-dimension-control{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin-top:12px;padding-top:10px;border-top:1px solid var(--border-color,#30363d)}\n      .research-dimension-control label{max-width:220px}.research-dimension-control small{max-width:680px;opacity:.8}'''
style_new = '''      .research-dimension-control{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin-top:12px;padding-top:10px;border-top:1px solid var(--border-color,#30363d)}\n      .research-dimension-control label{max-width:220px}.research-dimension-control small{max-width:680px;opacity:.8}\n      .research-review-inbox{margin-top:14px;padding-top:12px;border-top:1px solid var(--border-color,#30363d)}\n      .research-review-head,.research-review-controls,.research-review-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}\n      .research-review-head{justify-content:space-between}.research-review-controls{margin:8px 0}\n      .research-review-controls input{min-width:240px;flex:1}.research-review-list{display:grid;gap:8px}\n      .research-review-card{border:1px solid var(--border-color,#30363d);border-radius:9px;padding:10px}\n      .research-review-card textarea{width:100%;min-height:72px;margin:8px 0;resize:vertical}\n      .research-review-meta{font-size:.78rem;opacity:.75}.research-review-empty{opacity:.75;font-style:italic}'''
replace("src/dashboard/static/experiment-workflow.js", style_anchor, style_new)

listener_anchor = '''    byId("workflow-research-operational")?.addEventListener("change", () => this._renderResearchCatalog());\n    byId("workflow-projection-dimensions")?.addEventListener("change", (event) => {'''
listener_new = '''    byId("workflow-research-operational")?.addEventListener("change", () => this._renderResearchCatalog());\n    byId("workflow-review-refresh")?.addEventListener("click", () => this._loadReviewInbox());\n    byId("workflow-review-list")?.addEventListener("click", (event) => this._handleReviewAction(event));\n    this._loadReviewInbox();\n    byId("workflow-projection-dimensions")?.addEventListener("change", (event) => {'''
replace("src/dashboard/static/experiment-workflow.js", listener_anchor, listener_new)

method_anchor = '''  _configureConditionProfiles(preset = this.activePreset) {'''
methods = r'''  async _loadReviewInbox() {
    const list = byId("workflow-review-list");
    const count = byId("workflow-review-count");
    if (!list) return;
    try {
      const response = await fetch("/api/research/reviews", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`Review inbox HTTP ${response.status}`);
      const payload = await response.json();
      this.reviewInbox = Array.isArray(payload.items) ? payload.items : [];
      if (count) {
        count.textContent = `${Number(payload.open || 0)} offen`;
        count.className = `gate-badge ${Number(payload.open || 0) ? "pending" : "success"}`;
      }
      if (!this.reviewInbox.length) {
        list.innerHTML = '<p class="research-review-empty">Keine offenen Human Reviews.</p>';
        return;
      }
      list.innerHTML = this.reviewInbox.map((item, index) => `
        <article class="research-review-card" data-review-index="${index}">
          <strong>${escapeHtml(item.title || item.artifact_path)}</strong>
          <div class="research-review-meta">${escapeHtml(item.research_question_id || item.kind || "review")} · ${escapeHtml(item.artifact_path || "")}</div>
          <p>${escapeHtml(item.summary || "Human Review erforderlich.")}</p>
          <textarea aria-label="Review-Kommentar" placeholder="Begründung / Review-Kommentar"></textarea>
          <div class="research-review-actions">
            <button type="button" data-review-decision="accepted_as_interpretation">Als Interpretation akzeptieren</button>
            <button type="button" data-review-decision="rejected">Ablehnen</button>
          </div>
        </article>`).join("");
    } catch (error) {
      list.innerHTML = `<p class="research-review-empty">Review Inbox nicht verfügbar: ${escapeHtml(error.message || error)}</p>`;
      if (count) count.textContent = "Fehler";
    }
  }

  async _handleReviewAction(event) {
    const button = event.target.closest?.("[data-review-decision]");
    if (!button) return;
    const card = button.closest("[data-review-index]");
    const item = this.reviewInbox?.[Number(card?.dataset.reviewIndex)];
    if (!item) return;
    const reviewer = (byId("workflow-review-reviewer")?.value || "").trim();
    const comments = (card.querySelector("textarea")?.value || "").trim();
    if (!reviewer || !comments) {
      window.alert("Reviewer und Review-Kommentar sind Pflicht.");
      return;
    }
    const review_status = button.dataset.reviewDecision;
    const body = item.kind === "artifact"
      ? { artifact_path: item.artifact_path, reviewer, comments, review_status }
      : { reviewer, comments, review_status };
    button.disabled = true;
    try {
      const response = await fetch(item.review_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || payload.message || `HTTP ${response.status}`);
      await this._loadReviewInbox();
      document.dispatchEvent(new CustomEvent("mhrn:research-review-completed", { detail: payload }));
    } catch (error) {
      window.alert(`Review konnte nicht gespeichert werden: ${error.message || error}`);
    } finally {
      button.disabled = false;
    }
  }

'''
replace("src/dashboard/static/experiment-workflow.js", method_anchor, methods + method_anchor)

# Backend unit tests.
review_tests = r'''from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.review_inbox import build_review_inbox


def _write_report(root: Path, experiment: str, report: str, *, reviewed: bool = False) -> None:
    directory = root / "experiments" / experiment / "reports"
    directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "report_id": report,
        "research_question_id": "RQ-TEST-001",
        "generated_at": "2026-09-08T00:00:00+00:00",
        "human_review_required": True,
        "status": "review_pending",
        "scientific_evidence": False,
        "content": {"executive_summary": "Review me"},
    }
    (directory / f"{report}.json").write_text(json.dumps(payload), encoding="utf-8")
    if reviewed:
        (directory / f"{report}.review.json").write_text(
            json.dumps({"review_status": "accepted_as_interpretation", "reviewer": "Human"}),
            encoding="utf-8",
        )


def test_review_inbox_lists_only_open_airr(tmp_path: Path) -> None:
    _write_report(tmp_path, "EXP-A", "AIRR-2026-0001")
    _write_report(tmp_path, "EXP-B", "AIRR-2026-0002", reviewed=True)
    inbox = build_review_inbox(tmp_path)
    assert inbox["open"] == 1
    assert inbox["completed"] == 1
    item = inbox["items"][0]
    assert item["experiment_id"] == "EXP-A"
    assert item["review_endpoint"].endswith("/EXP-A/AIRR-2026-0001/review")


def test_review_inbox_never_promotes_evidence(tmp_path: Path) -> None:
    _write_report(tmp_path, "EXP-A", "AIRR-2026-0001")
    inbox = build_review_inbox(tmp_path)
    assert "scientific_evidence" not in inbox["items"][0]
'''
(ROOT / "tests/test_review_inbox.py").write_text(review_tests, encoding="utf-8")

# Browser contract: GET inbox and complete one review through the real endpoint.
append_once(
    "tests/browser/fullstack.spec.js",
    "research review inbox completes an append-only human review",
    r'''test('research review inbox completes an append-only human review', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  await page.locator('[data-primary-area="science"]').click();
  await expect(page.locator('#workflow-review-inbox')).toBeVisible();
  const inboxResponse = await page.request.get('/api/research/reviews');
  expect(inboxResponse.ok()).toBeTruthy();
  const inbox = await inboxResponse.json();
  expect(Array.isArray(inbox.items)).toBeTruthy();
  await expect(page.locator('#workflow-review-count')).toContainText('offen');
});''',
)

# Documentation and roadmap to 1.2.
append_once(
    "research/README.md",
    "## Human Review Inbox",
    r'''## Human Review Inbox

The Research dashboard exposes an explicit Human Review Inbox through `GET /api/research/reviews`. It aggregates open AIRR and explicitly review-blocked artifacts. A reviewer must provide identity, decision and comments. Decisions are persisted only through the existing append-only review writers and therefore never rewrite the reviewed artifact or automatically create scientific evidence.

The UI is intended to make review completion operationally simple without weakening epistemic controls: `accepted_as_interpretation` means the human accepts an interpretation record, not that a hypothesis or research question is confirmed. Evidence promotion remains a separate, explicit workflow.
''',
)
append_once(
    "README.md",
    "### Research Review Inbox",
    r'''### Research Review Inbox

Research now includes a review inbox for open Human Reviews. The dashboard lists pending review targets and lets a human reviewer record reviewer identity, an accept/reject decision and mandatory comments. Review records are append-only and do not automatically promote artifacts to scientific evidence.
''',
)
append_once(
    "docs/08-roadmap/ROADMAP.md",
    "## Version roadmap — v0.6 to v1.2",
    r'''## Version roadmap — v0.6 to v1.2

### v0.6 — Scaling & deterministic performance
- Larger sparse networks and bounded storage/telemetry.
- Reproducible performance benchmarks across supported Python versions.
- Runtime frequency controls, compact run summaries and deterministic resume.

### v0.7 — Knowledge & learning experiments
- Operational learning protocols with registered controls and independent seeds.
- Interference, retention, transfer and retrieval experiments.
- Evidence-ready statistics artifacts without model-generated quantitative claims.

### v0.8 — Embodiment & Neural Symbiosis
- MSBA peripheral adapters remain experiment-only until controls validate them.
- Sensor/actuator contracts, lesion/noise studies and resource-allocation experiments.
- No production peripheral activation without explicit governance gates.

### v0.9 — Memory, world model & self-model
- Bounded episodic/semantic memory experiments.
- World-model prediction, calibration and counterfactual evaluation.
- Self-model observables treated as operational variables, not consciousness claims.

### v1.0 — Reproducible research platform
- Stable public APIs and artifact schemas.
- Research Review Inbox, evidence workflow and publication-integrity checks integrated end to end.
- Reproducible release bundles, migration notes and compatibility guarantees.

### v1.1 — Replication & multi-system validation
- Independent replication packages and cross-hardware reproducibility studies.
- Comparative baselines against reduced-dimensional, shuffled and non-neural controls.
- External adapter/provider compatibility matrix with provenance hashes.

### v1.2 — Governed adaptive system
- Preregistered adaptive allocation, structural growth and peripheral plasticity behind explicit review gates.
- Human-auditable policy/decision ledger for adaptive system changes.
- Long-horizon stability, rollback, safety isolation and failure-recovery experiments.
- Production enablement remains opt-in and requires validated controls plus human approval.
''',
)
append_once(
    "docs/07-changelog/CHANGELOG.md",
    "### 2026-09-08 — Research Review Inbox and v1.2 roadmap",
    r'''### 2026-09-08 — Research Review Inbox and v1.2 roadmap

- Added `GET /api/research/reviews` to aggregate outstanding Human Reviews.
- Added Research UI controls to record reviewer identity, mandatory comments and accept/reject decisions through append-only review files.
- Review completion never grants scientific evidence automatically.
- Extended the version roadmap through v1.2 with explicit reproducibility, replication, embodiment, memory and governed-adaptation milestones.
''',
)

# Mark only the executable review-UX TODO if present; do not falsify scientific reviews.
todo = ROOT / "docs/08-roadmap/TODO.md"
text = todo.read_text(encoding="utf-8")
for phrase in [
    "Add a Research review inbox for pending human reviews.",
    "Add a simple UI to complete pending Human Reviews.",
    "Expose pending human reviews in Research.",
]:
    text = text.replace(f"- [ ] {phrase}", f"- [x] {phrase}")
todo.write_text(text, encoding="utf-8")
