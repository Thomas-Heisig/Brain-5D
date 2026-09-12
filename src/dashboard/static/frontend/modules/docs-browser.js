"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;
let currentSource = "research";

function ensurePanel() {
  let panel = document.getElementById("mhrn-docs-browser");
  if (panel) return panel;
  const workspace = document.getElementById("tab-research");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-docs-browser";
  panel.className = "mhrn-docs-browser card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">DOCUMENTATION BROWSER</span>
        <h2>Dokumenten-Browser</h2>
        <p>Projektdokumentation durchsuchen, Statistiken abrufen und Dateiinhalte lesen.</p>
      </div>
      <span id="docs-count-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="docs-toolbar">
      <input type="text" id="docs-search-input" placeholder="Dokumente durchsuchen…" class="docs-search-input">
      <button type="button" id="docs-search-btn" class="btn-secondary">🔍 Suchen</button>
      <button type="button" id="docs-refresh-btn" class="btn-secondary">🔄 Aktualisieren</button>
    </div>
    <div class="docs-grid">
      <div class="docs-section">
        <h3>Dokumentbaum</h3>
        <div id="docs-tree" class="docs-tree">lade …</div>
      </div>
      <div class="docs-section">
        <h3>Statistiken</h3>
        <div id="docs-statistics" class="docs-statistics">lade …</div>
      </div>
      <div class="docs-section docs-viewer-section">
        <h3>Inhalt</h3>
        <div id="docs-content" class="docs-content">Wählen Sie ein Dokument aus dem Baum.</div>
      </div>
    </div>`;
  const anchor = workspace.querySelector(".fm-toolbar");
  if (anchor) anchor.insertAdjacentElement("beforebegin", panel);
  else workspace.append(panel);

  panel.querySelector("#docs-search-btn").addEventListener("click", searchDocs);
  panel.querySelector("#docs-search-input").addEventListener("keydown", (e) => { if (e.key === "Enter") searchDocs(); });
  panel.querySelector("#docs-refresh-btn").addEventListener("click", () => loadAll());
  return panel;
}

function renderTree(data) {
  const el = document.getElementById("docs-tree");
  if (!el) return;
  const entries = Array.isArray(data) ? data : (data?.entries || data?.tree || []);
  if (!entries.length) { el.textContent = "Keine Dokumente gefunden."; return; }
  el.innerHTML = entries.map(e => {
    const name = e.name || e.title || e.path?.split("/").pop() || "—";
    const path = e.path || e.id || "";
    const isDir = e.type === "dir" || e.is_dir;
    return `<div class="docs-tree-item ${isDir ? "docs-tree-dir" : "docs-tree-file"}" data-path="${escapeAttr(path)}">
      <span class="docs-tree-icon">${isDir ? "📁" : "📄"}</span>
      <span class="docs-tree-name">${escapeHtml(name)}</span>
      ${!isDir ? `<button class="docs-tree-open" data-path="${escapeAttr(path)}">Öffnen</button>` : ""}
    </div>`;
  }).join("");
  el.querySelectorAll(".docs-tree-open").forEach(btn => {
    btn.addEventListener("click", () => loadDocContent(btn.dataset.path));
  });
  const badge = document.getElementById("docs-count-badge");
  if (badge) badge.textContent = `${entries.length} Dokument(e)`;
}

function renderStatistics(data) {
  const el = document.getElementById("docs-statistics");
  if (!el) return;
  if (!data) { el.textContent = "Keine Statistiken verfügbar."; return; }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  el.innerHTML = `<dl>${entries.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(String(v))}</dd>`).join("")}</dl>`;
}

function renderSearch(data) {
  const el = document.getElementById("docs-content");
  if (!el) return;
  const results = Array.isArray(data) ? data : (data?.results || []);
  if (!results.length) { el.innerHTML = "<p>Keine Treffer.</p>"; return; }
  el.innerHTML = `<p>${results.length} Treffer:</p><ul class="docs-search-results">${results.map(r => {
    const name = r.name || r.title || r.path?.split("/").pop() || "—";
    const path = r.path || r.id || "";
    const snippet = r.snippet || r.summary || "";
    return `<li><strong>${escapeHtml(name)}</strong> <button class="docs-search-open" data-path="${escapeAttr(path)}">Öffnen</button><br><small>${escapeHtml(snippet)}</small></li>`;
  }).join("")}</ul>`;
  el.querySelectorAll(".docs-search-open").forEach(btn => {
    btn.addEventListener("click", () => loadDocContent(btn.dataset.path));
  });
}

function renderContent(data) {
  const el = document.getElementById("docs-content");
  if (!el) return;
  if (!data) { el.textContent = "Keine Daten."; return; }
  const content = data.content || data.text || data.body || "";
  const title = data.title || data.name || data.path || "Dokument";
  el.innerHTML = `<h4>${escapeHtml(title)}</h4><pre class="docs-content-pre">${escapeHtml(content)}</pre>`;
}

async function loadTree() {
  try {
    const data = await apiGet("/api/docs/tree");
    renderTree(data);
  } catch (e) {
    const el = document.getElementById("docs-tree");
    if (el) el.textContent = `Fehler: ${e.message}`;
  }
}

async function loadStatistics() {
  try {
    const data = await apiGet("/api/docs/statistics");
    renderStatistics(data);
  } catch (e) {
    const el = document.getElementById("docs-statistics");
    if (el) el.textContent = `Fehler: ${e.message}`;
  }
}

async function searchDocs() {
  const input = document.getElementById("docs-search-input");
  if (!input) return;
  const q = input.value.trim();
  if (!q) { loadAll(); return; }
  try {
    const data = await apiGet(`/api/docs/search?q=${encodeURIComponent(q)}`);
    renderSearch(data);
  } catch (e) {
    const el = document.getElementById("docs-content");
    if (el) el.innerHTML = `<p>Fehler: ${escapeHtml(e.message)}</p>`;
  }
}

async function loadDocContent(path) {
  if (!path) return;
  const el = document.getElementById("docs-content");
  if (el) el.textContent = "lade …";
  try {
    const data = await apiGet(`/api/docs-files/${encodeURIComponent(path)}`);
    renderContent(data);
  } catch (e) {
    if (el) el.innerHTML = `<p>Fehler: ${escapeHtml(e.message)}</p>`;
  }
}

async function loadAll() {
  await Promise.allSettled([loadTree(), loadStatistics()]);
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}
function escapeAttr(s) {
  return String(s).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function initDocsBrowser() {
  ensurePanel();
  loadAll();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(loadAll, 30000);
}
