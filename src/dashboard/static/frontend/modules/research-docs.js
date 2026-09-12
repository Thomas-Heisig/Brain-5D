"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-research-docs");
  if (panel) return panel;
  const workspace = document.getElementById("tab-research");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-research-docs";
  panel.className = "mhrn-research-docs card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">RESEARCH REGISTRY · REPORTS · AI REPORTS</span>
        <h2>Research-Dokumente & Berichte</h2>
        <p>Registrierte Research-Dokumente, generierte Berichte und AI-generierte Reports.</p>
      </div>
      <span id="research-docs-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="research-docs-grid">
      <div class="research-docs-section">
        <h3>Research-Dokumente</h3>
        <div id="research-documents-list" class="research-list">lade …</div>
      </div>
      <div class="research-docs-section">
        <h3>Research-Berichte</h3>
        <div id="research-reports-list" class="research-list">lade …</div>
      </div>
      <div class="research-docs-section">
        <h3>AI-Reports</h3>
        <div id="research-ai-reports-list" class="research-list">lade …</div>
      </div>
    </div>
    <div id="research-doc-viewer" class="research-doc-viewer is-hidden">
      <header><h3 id="research-doc-viewer-title">—</h3><button type="button" id="research-doc-viewer-close" class="btn-secondary">Schließen</button></header>
      <pre id="research-doc-viewer-content" class="research-doc-viewer-content"></pre>
    </div>`;
  // Insert into the Registry sub-panel if available, otherwise fall back
  const registryPanel = workspace.querySelector('.research-subpanel[data-subpanel="registry"]');
  if (registryPanel) {
    const placeholder = registryPanel.querySelector("#research-registry-placeholder");
    if (placeholder) placeholder.remove();
    registryPanel.appendChild(panel);
  } else {
    const anchor = workspace.querySelector(".fm-toolbar");
    if (anchor) anchor.insertAdjacentElement("beforebegin", panel);
    else workspace.append(panel);
  }
  panel.querySelector("#research-doc-viewer-close").addEventListener("click", () => {
    panel.querySelector("#research-doc-viewer").classList.add("is-hidden");
  });
  return panel;
}

function renderDocuments(data) {
  const el = document.getElementById("research-documents-list");
  if (!el) return;
  const docs = Array.isArray(data) ? data : (data?.documents || []);
  if (!docs.length) { el.textContent = "Keine Research-Dokumente."; return; }
  el.innerHTML = docs.map(d => {
    const id = d.id || d.ref || d.path || "";
    const title = d.title || d.name || id;
    const date = d.date || d.created || "—";
    return `<div class="research-item" data-path="${escapeAttr(d.path || id)}">
      <strong>${escapeHtml(title)}</strong>
      <small>${escapeHtml(date)}</small>
      <button class="research-item-open" data-path="${escapeAttr(d.path || id)}">Öffnen</button>
    </div>`;
  }).join("");
  el.querySelectorAll(".research-item-open").forEach(btn => {
    btn.addEventListener("click", () => loadResearchFile(btn.dataset.path));
  });
}

function renderReports(data) {
  const el = document.getElementById("research-reports-list");
  if (!el) return;
  const reports = Array.isArray(data) ? data : (data?.reports || []);
  if (!reports.length) { el.textContent = "Keine Research-Berichte."; return; }
  el.innerHTML = reports.map(r => {
    const id = r.id || r.ref || "";
    const title = r.title || r.name || id;
    const date = r.date || r.created || "—";
    const status = r.status || "—";
    return `<div class="research-item" data-ref="${escapeAttr(id)}">
      <strong>${escapeHtml(title)}</strong>
      <small>${escapeHtml(date)} · ${escapeHtml(status)}</small>
      <button class="research-report-open" data-ref="${escapeAttr(id)}">Öffnen</button>
    </div>`;
  }).join("");
  el.querySelectorAll(".research-report-open").forEach(btn => {
    btn.addEventListener("click", () => loadAIReport(btn.dataset.ref));
  });
}

function renderAIReports(data) {
  const el = document.getElementById("research-ai-reports-list");
  if (!el) return;
  const reports = Array.isArray(data) ? data : (data?.reports || []);
  if (!reports.length) { el.textContent = "Keine AI-Reports."; return; }
  el.innerHTML = reports.map(r => {
    const ref = r.ref || r.id || "";
    const title = r.title || r.name || ref;
    const date = r.generated_at || r.date || "—";
    const status = r.review_status || r.status || "—";
    return `<div class="research-item" data-ref="${escapeAttr(ref)}">
      <strong>${escapeHtml(title)}</strong>
      <small>${escapeHtml(date)} · ${escapeHtml(status)}</small>
      <button class="research-ai-report-open" data-ref="${escapeAttr(ref)}">Öffnen</button>
    </div>`;
  }).join("");
  el.querySelectorAll(".research-ai-report-open").forEach(btn => {
    btn.addEventListener("click", () => loadAIReport(btn.dataset.ref));
  });
  const badge = document.getElementById("research-docs-badge");
  if (badge) badge.textContent = `${reports.length} AI-Report(s)`;
}

async function loadResearchFile(path) {
  if (!path) return;
  const viewer = document.getElementById("research-doc-viewer");
  const titleEl = document.getElementById("research-doc-viewer-title");
  const contentEl = document.getElementById("research-doc-viewer-content");
  if (viewer) viewer.classList.remove("is-hidden");
  if (titleEl) titleEl.textContent = path;
  if (contentEl) contentEl.textContent = "lade …";
  try {
    const data = await apiGet(`/api/research-files/${encodeURIComponent(path)}`);
    if (titleEl) titleEl.textContent = data.title || data.name || path;
    if (contentEl) contentEl.textContent = data.content || data.text || data.body || JSON.stringify(data, null, 2);
  } catch (e) {
    if (contentEl) contentEl.textContent = `Fehler: ${e.message}`;
  }
}

async function loadAIReport(ref) {
  if (!ref) return;
  const viewer = document.getElementById("research-doc-viewer");
  const titleEl = document.getElementById("research-doc-viewer-title");
  const contentEl = document.getElementById("research-doc-viewer-content");
  if (viewer) viewer.classList.remove("is-hidden");
  if (titleEl) titleEl.textContent = `AI Report: ${ref}`;
  if (contentEl) contentEl.textContent = "lade …";
  try {
    const data = await apiGet(`/api/research/ai-reports/${encodeURIComponent(ref)}`);
    if (titleEl) titleEl.textContent = data.title || data.name || `AI Report: ${ref}`;
    if (contentEl) contentEl.textContent = data.content || data.text || data.body || JSON.stringify(data, null, 2);
  } catch (e) {
    if (contentEl) contentEl.textContent = `Fehler: ${e.message}`;
  }
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  const [docs, reports, aiReports] = await Promise.allSettled([
    apiGet("/api/research/documents"),
    apiGet("/api/research/reports"),
    apiGet("/api/research/ai-reports"),
  ]);
  if (docs.status === "fulfilled") renderDocuments(docs.value);
  else document.getElementById("research-documents-list").textContent = `Fehler: ${docs.reason.message}`;
  if (reports.status === "fulfilled") renderReports(reports.value);
  else document.getElementById("research-reports-list").textContent = `Fehler: ${reports.reason.message}`;
  if (aiReports.status === "fulfilled") renderAIReports(aiReports.value);
  else document.getElementById("research-ai-reports-list").textContent = `Fehler: ${aiReports.reason.message}`;
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}
function escapeAttr(s) {
  return String(s).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function initResearchDocs() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 30000);
}
