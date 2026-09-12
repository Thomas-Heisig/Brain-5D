"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-structural-inspector");
  if (panel) return panel;
  const workspace = document.getElementById("tab-network");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-structural-inspector";
  panel.className = "mhrn-structural-inspector card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">STRUCTURAL HEATMAP · HISTORY · CONFIG</span>
        <h2>Strukturelle Analyse</h2>
        <p>Heatmap der strukturellen Aktivität, Verlaufshistorie und Konfiguration.</p>
      </div>
      <span id="structural-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="structural-grid">
      <div class="structural-section">
        <h3>Heatmap</h3>
        <div id="structural-heatmap" class="structural-heatmap">lade …</div>
      </div>
      <div class="structural-section">
        <h3>Verlaufshistorie</h3>
        <div id="structural-history" class="structural-history">lade …</div>
      </div>
      <div class="structural-section">
        <h3>Konfiguration</h3>
        <div id="structural-config" class="structural-config">lade …</div>
      </div>
    </div>`;
  const anchor = workspace.querySelector(":scope > header");
  if (anchor) anchor.insertAdjacentElement("afterend", panel);
  else workspace.prepend(panel);
  return panel;
}

function renderHeatmap(data) {
  const el = document.getElementById("structural-heatmap");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "Heatmap nicht verfügbar."; return; }
  const cells = data.cells || data.matrix || [];
  const maxVal = data.max_value || 1;
  if (!cells.length) { el.textContent = "Keine Heatmap-Daten."; return; }
  el.innerHTML = `<div class="heatmap-grid" style="grid-template-columns: repeat(${Math.ceil(Math.sqrt(cells.length))}, 1fr);">
    ${cells.map(c => {
      const val = typeof c === "object" ? (c.value ?? c.intensity ?? 0) : c;
      const pct = Math.min(100, (val / maxVal) * 100);
      return `<div class="heatmap-cell" title="${escapeAttr(String(val))}" style="--intensity: ${pct}%"></div>`;
    }).join("")}
  </div>
  <div class="heatmap-legend"><span>0</span><div class="heatmap-gradient"></div><span>${escapeHtml(String(maxVal))}</span></div>`;
}

function renderHistory(data) {
  const el = document.getElementById("structural-history");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "Historie nicht verfügbar."; return; }
  const entries = data.history || data.entries || [];
  if (!entries.length) { el.textContent = "Keine Historie."; return; }
  el.innerHTML = `<table class="structural-history-table"><thead><tr><th>Tick</th><th>Ereignis</th><th>Änderung</th></tr></thead><tbody>
    ${entries.slice(0, 20).map(e => `<tr><td>${e.tick ?? "—"}</td><td>${escapeHtml(e.event || e.type || "—")}</td><td>${escapeHtml(e.change || e.delta || "—")}</td></tr>`).join("")}
  </tbody></table>`;
}

function renderConfig(data) {
  const el = document.getElementById("structural-config");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "Konfiguration nicht verfügbar."; return; }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  el.innerHTML = `<dl>${entries.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(typeof v === "object" ? JSON.stringify(v) : String(v))}</dd>`).join("")}</dl>`;
  const badge = document.getElementById("structural-badge");
  if (badge) badge.textContent = data.status || "aktiv";
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  const [heatmap, history, config] = await Promise.allSettled([
    apiGet("/api/structural/heatmap"),
    apiGet("/api/structural/history"),
    apiGet("/api/structural/config"),
  ]);
  if (heatmap.status === "fulfilled") renderHeatmap(heatmap.value);
  else document.getElementById("structural-heatmap").textContent = `Fehler: ${heatmap.reason.message}`;
  if (history.status === "fulfilled") renderHistory(history.value);
  else document.getElementById("structural-history").textContent = `Fehler: ${history.reason.message}`;
  if (config.status === "fulfilled") renderConfig(config.value);
  else document.getElementById("structural-config").textContent = `Fehler: ${config.reason.message}`;
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}
function escapeAttr(s) {
  return String(s).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function initStructuralInspector() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 5000);
}
