"use strict";
import { apiGet, apiPost } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-learning-prep");
  if (panel) return panel;
  const workspace = document.getElementById("tab-control");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-learning-prep";
  panel.className = "mhrn-learning-prep card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">LEARNING PREPARATION</span>
        <h2>Lern-Vorbereitung</h2>
        <p>Vorbereitungsdaten für Lern-Phasen abrufen und konfigurieren.</p>
      </div>
      <span id="learning-prep-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="learning-prep-grid">
      <div class="learning-prep-section">
        <h3>Aktuelle Vorbereitung</h3>
        <div id="learning-prep-detail" class="learning-prep-detail">lade …</div>
      </div>
      <div class="learning-prep-section">
        <h3>Vorbereitung auslösen</h3>
        <form id="learning-prep-form">
          <label>Modus<select id="learning-prep-mode">
            <option value="standard">Standard</option>
            <option value="intensive">Intensiv</option>
            <option value="explorative">Explorativ</option>
          </select></label>
          <label>Epochen<input type="number" id="learning-prep-epochs" min="1" max="10000" value="10"></label>
          <label>Lernrate<input type="number" id="learning-prep-rate" step="0.001" min="0" max="1" value="0.01"></label>
          <button type="submit" class="btn-success">Vorbereitung starten</button>
        </form>
        <div id="learning-prep-result" class="learning-prep-result"></div>
      </div>
    </div>`;
  const anchor = workspace.querySelector(":scope > header");
  if (anchor) anchor.insertAdjacentElement("afterend", panel);
  else workspace.prepend(panel);
  panel.querySelector("#learning-prep-form").addEventListener("submit", triggerPrep);
  return panel;
}

function renderDetail(data) {
  const el = document.getElementById("learning-prep-detail");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "Keine Vorbereitungsdaten verfügbar."; return; }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  el.innerHTML = `<dl>${entries.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(typeof v === "object" ? JSON.stringify(v) : String(v))}</dd>`).join("")}</dl>`;
  const badge = document.getElementById("learning-prep-badge");
  if (badge) badge.textContent = data.status || data.mode || "ready";
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  try {
    const data = await apiGet("/api/learning/preparation");
    renderDetail(data);
  } catch (e) {
    const el = document.getElementById("learning-prep-detail");
    if (el) el.textContent = `Fehler: ${e.message}`;
  }
}

async function triggerPrep(event) {
  event.preventDefault();
  const panel = ensurePanel();
  if (!panel) return;
  const resultEl = panel.querySelector("#learning-prep-result");
  const mode = panel.querySelector("#learning-prep-mode").value;
  const epochs = Number(panel.querySelector("#learning-prep-epochs").value);
  const rate = Number(panel.querySelector("#learning-prep-rate").value);
  resultEl.textContent = "Vorbereitung läuft …";
  try {
    const result = await apiPost("/api/learning/preparation", { mode, epochs, learning_rate: rate });
    resultEl.innerHTML = `<div class="learning-prep-success">
      <strong>✓ Vorbereitung gestartet</strong>
      <span>Status: ${escapeHtml(result.status || "started")}</span>
    </div>`;
    await refresh();
  } catch (e) {
    resultEl.textContent = `Fehler: ${e.message}`;
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

export function initLearningPrep() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 10000);
}
