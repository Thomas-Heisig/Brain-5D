"use strict";
import { apiGet, apiPost } from "../core/api.js";

function ensurePanel() {
  let panel = document.getElementById("mhrn-ai-report-tools");
  if (panel) return panel;
  const workspace = document.getElementById("tab-research");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-ai-report-tools";
  panel.className = "mhrn-ai-report-tools card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">AI REPORT GENERATION · REVIEW</span>
        <h2>AI-Report Werkzeuge</h2>
        <p>AI-generierte Berichte erstellen und Review einleiten.</p>
      </div>
    </header>
    <div class="ai-report-grid">
      <div class="ai-report-section">
        <h3>Report generieren</h3>
        <form id="ai-report-generate-form">
          <label>Experiment-Ref<input type="text" id="ai-report-experiment-ref" placeholder="EXP-..." required></label>
          <label>Template (optional)<select id="ai-report-template">
            <option value="">Automatisch</option>
            <option value="standard">Standard</option>
            <option value="detailed">Detailliert</option>
            <option value="summary">Zusammenfassung</option>
          </select></label>
          <label class="ai-report-wide">Zusätzliche Instruktionen<textarea id="ai-report-instructions" rows="3" placeholder="Optionale Hinweise für die Generierung"></textarea></label>
          <button type="submit" class="btn-success">Generieren</button>
        </form>
        <div id="ai-report-generate-result" class="ai-report-result"></div>
      </div>
      <div class="ai-report-section">
        <h3>Review einleiten</h3>
        <form id="ai-report-review-form">
          <label>Report-Ref<input type="text" id="ai-report-review-ref" placeholder="AIRR-..." required></label>
          <label>Reviewer (optional)<input type="text" id="ai-report-reviewer" placeholder="automatisch"></label>
          <label class="ai-report-wide">Review-Notizen<textarea id="ai-report-review-notes" rows="3" placeholder="Optionale Notizen"></textarea></label>
          <button type="submit" class="btn-secondary">Review starten</button>
        </form>
        <div id="ai-report-review-result" class="ai-report-result"></div>
      </div>
    </div>`;
  const anchor = workspace.querySelector(".fm-toolbar");
  if (anchor) anchor.insertAdjacentElement("beforebegin", panel);
  else workspace.append(panel);
  panel.querySelector("#ai-report-generate-form").addEventListener("submit", generateReport);
  panel.querySelector("#ai-report-review-form").addEventListener("submit", reviewReport);
  return panel;
}

async function generateReport(event) {
  event.preventDefault();
  const panel = ensurePanel();
  if (!panel) return;
  const resultEl = panel.querySelector("#ai-report-generate-result");
  const experimentRef = panel.querySelector("#ai-report-experiment-ref").value.trim();
  const template = panel.querySelector("#ai-report-template").value;
  const instructions = panel.querySelector("#ai-report-instructions").value.trim();
  if (!experimentRef) { resultEl.textContent = "Experiment-Ref erforderlich."; return; }
  resultEl.textContent = "Generiere …";
  try {
    const body = { experiment_ref: experimentRef };
    if (template) body.template = template;
    if (instructions) body.instructions = instructions;
    const result = await apiPost("/api/research/ai-reports/generate", body);
    resultEl.innerHTML = `<div class="ai-report-success">
      <strong>✓ Generiert</strong>
      <span>Ref: ${escapeHtml(result.ref || result.id || "—")}</span>
      <span>Status: ${escapeHtml(result.status || "generated")}</span>
    </div>`;
  } catch (e) {
    resultEl.textContent = `Fehler: ${e.message}`;
  }
}

async function reviewReport(event) {
  event.preventDefault();
  const panel = ensurePanel();
  if (!panel) return;
  const resultEl = panel.querySelector("#ai-report-review-result");
  const ref = panel.querySelector("#ai-report-review-ref").value.trim();
  const reviewer = panel.querySelector("#ai-report-reviewer").value.trim();
  const notes = panel.querySelector("#ai-report-review-notes").value.trim();
  if (!ref) { resultEl.textContent = "Report-Ref erforderlich."; return; }
  resultEl.textContent = "Review läuft …";
  try {
    const body = {};
    if (reviewer) body.reviewer = reviewer;
    if (notes) body.notes = notes;
    const result = await apiPost(`/api/research/ai-reports/${encodeURIComponent(ref)}/review`, body);
    resultEl.innerHTML = `<div class="ai-report-success">
      <strong>✓ Review gestartet</strong>
      <span>Ref: ${escapeHtml(result.ref || ref)}</span>
      <span>Review-Status: ${escapeHtml(result.review_status || result.status || "—")}</span>
    </div>`;
  } catch (e) {
    resultEl.textContent = `Fehler: ${e.message}`;
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

export function initAIReportTools() {
  ensurePanel();
}
