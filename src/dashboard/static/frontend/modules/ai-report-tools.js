"use strict";

import { apiPost } from "../core/api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

function mountTarget() {
  return document.getElementById("review-ai-tools-mount")
    || document.querySelector('#tab-research .research-subpanel[data-subpanel="registry"]')
    || document.getElementById("tab-research");
}

function ensurePanel() {
  let panel = document.getElementById("mhrn-ai-report-tools");
  const target = mountTarget();
  if (!target) return null;
  if (panel) {
    if (panel.parentElement !== target) target.appendChild(panel);
    return panel;
  }
  panel = document.createElement("section");
  panel.id = "mhrn-ai-report-tools";
  panel.className = "mhrn-ai-report-tools card";
  panel.dataset.panelInfo = "AI-Reports sind Interpretationsartefakte. Erzeugung und Human Review verleihen niemals automatisch wissenschaftlichen Evidenzstatus.";
  panel.innerHTML = `
    <header>
      <div><span class="workspace-kicker">AI REPORT · HUMAN REVIEW</span><h2>AI-Report Werkzeuge</h2><p>Backend-genaue AIRR-Erzeugung und append-only Interpretations-Review.</p></div>
    </header>
    <div class="ai-report-grid">
      <div class="ai-report-section">
        <h3>Report generieren</h3>
        <form id="ai-report-generate-form">
          <label>Experiment-ID<input type="text" id="ai-report-experiment-id" placeholder="EXP-..." required></label>
          <p class="ai-report-wide">Der Server akzeptiert hier ausschließlich die registrierte Experiment-ID; Template- oder Prompt-Felder werden nicht vorgetäuscht.</p>
          <button type="submit" class="btn-success">AIRR generieren</button>
        </form>
        <div id="ai-report-generate-result" class="ai-report-result" aria-live="polite"></div>
      </div>
      <div class="ai-report-section">
        <h3>Human Review</h3>
        <form id="ai-report-review-form">
          <label>Experiment-ID<input type="text" id="ai-review-experiment-id" placeholder="EXP-..." required></label>
          <label>Report-ID<input type="text" id="ai-review-report-id" placeholder="AIRR-..." required></label>
          <label>Entscheidung<select id="ai-review-status" required><option value="accepted_as_interpretation">Als Interpretation akzeptieren</option><option value="rejected">Interpretation ablehnen</option></select></label>
          <label>Reviewer<input type="text" id="ai-review-reviewer" required></label>
          <label class="ai-report-wide">Kommentare<textarea id="ai-review-comments" rows="4" required placeholder="Begründung der menschlichen Review-Entscheidung"></textarea></label>
          <button type="submit" class="btn-secondary">Review append-only speichern</button>
        </form>
        <div id="ai-report-review-result" class="ai-report-result" aria-live="polite"></div>
      </div>
    </div>
    <p class="mhrn-epistemic-note">Review-Status <code>accepted_as_interpretation</code> ist keine automatische EVID-Promotion.</p>`;
  target.appendChild(panel);
  panel.querySelector("#ai-report-generate-form").addEventListener("submit", generateReport);
  panel.querySelector("#ai-report-review-form").addEventListener("submit", reviewReport);
  return panel;
}

async function generateReport(event) {
  event.preventDefault();
  const panel = ensurePanel();
  if (!panel) return;
  const resultEl = panel.querySelector("#ai-report-generate-result");
  const experimentId = panel.querySelector("#ai-report-experiment-id").value.trim();
  if (!experimentId) return;
  resultEl.textContent = "Generiere AIRR …";
  try {
    const result = await apiPost("/api/research/ai-reports/generate", { experiment_id: experimentId });
    const reportId = result.report_id || "—";
    panel.querySelector("#ai-review-experiment-id").value = experimentId;
    if (result.report_id) panel.querySelector("#ai-review-report-id").value = result.report_id;
    resultEl.innerHTML = `<div class="ai-report-success"><strong>✓ Generiert</strong><span>Report: ${escapeHtml(reportId)}</span><span>Status: ${escapeHtml(result.status || "review_pending")}</span></div>`;
    document.dispatchEvent(new CustomEvent("mhrn:review-data-changed"));
  } catch (error) {
    resultEl.textContent = `Fehler: ${error.message}`;
  }
}

async function reviewReport(event) {
  event.preventDefault();
  const panel = ensurePanel();
  if (!panel) return;
  const resultEl = panel.querySelector("#ai-report-review-result");
  const experimentId = panel.querySelector("#ai-review-experiment-id").value.trim();
  const reportId = panel.querySelector("#ai-review-report-id").value.trim();
  const reviewStatus = panel.querySelector("#ai-review-status").value;
  const reviewer = panel.querySelector("#ai-review-reviewer").value.trim();
  const comments = panel.querySelector("#ai-review-comments").value.trim();
  if (!experimentId || !reportId || !reviewer || !comments) {
    resultEl.textContent = "Experiment-ID, Report-ID, Reviewer und Kommentare sind erforderlich.";
    return;
  }
  resultEl.textContent = "Speichere Review …";
  try {
    const endpoint = `/api/research/ai-reports/${encodeURIComponent(experimentId)}/${encodeURIComponent(reportId)}/review`;
    const result = await apiPost(endpoint, { review_status: reviewStatus, reviewer, comments });
    resultEl.innerHTML = `<div class="ai-report-success"><strong>✓ Review gespeichert</strong><span>${escapeHtml(result.path || reportId)}</span></div>`;
    document.dispatchEvent(new CustomEvent("mhrn:review-data-changed"));
  } catch (error) {
    resultEl.textContent = `Fehler: ${error.message}`;
  }
}

export function initAIReportTools() {
  ensurePanel();
  const observer = new MutationObserver(() => ensurePanel());
  observer.observe(document.querySelector("main") || document.body, { childList: true, subtree: true });
}
