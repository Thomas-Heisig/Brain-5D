"use strict";
import { apiGet, apiPost } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-cognition");
  if (panel) return panel;
  const workspace = document.getElementById("tab-wesen");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-cognition";
  panel.className = "mhrn-cognition card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">COGNITION · MEMORY · WORLD MODEL</span>
        <h2>Kognitiver Zustand</h2>
        <p>Vollständige Memory-State-Daten, World-Model und globaler Kognitions-Status.</p>
      </div>
      <span id="cognition-state-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="cognition-grid">
      <div class="cognition-section">
        <h3>Globaler Status</h3>
        <div id="cognition-state-detail" class="cognition-detail">lade …</div>
      </div>
      <div class="cognition-section">
        <h3>Memory State</h3>
        <div id="cognition-memory-detail" class="cognition-detail">lade …</div>
      </div>
      <div class="cognition-section">
        <h3>World Model</h3>
        <div id="cognition-world-model-detail" class="cognition-detail">lade …</div>
      </div>
    </div>`;
  const subnav = workspace.querySelector(":scope > .wesen-subnav");
  const anchor = workspace.querySelector(":scope > header");
  if (subnav) subnav.insertAdjacentElement("afterend", panel);
  else if (anchor) anchor.insertAdjacentElement("afterend", panel);
  else workspace.prepend(panel);
  return panel;
}

function renderState(data) {
  const el = document.getElementById("cognition-state-detail");
  if (!el) return;
  const rows = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  if (!rows.length) { el.textContent = "keine Daten"; return; }
  el.innerHTML = `<dl>${rows.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(String(v))}</dd>`).join("")}</dl>`;
  const badge = document.getElementById("cognition-state-badge");
  if (badge) badge.textContent = data.status || data.mode || "aktiv";
}

function renderMemory(data) {
  const el = document.getElementById("cognition-memory-detail");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "Memory nicht verfügbar"; return; }
  const controls = data.controls || {};
  const episodes = data.episodes || [];
  el.innerHTML = `
    <div class="cognition-memory-controls">
      <label><input type="checkbox" id="cognition-read-enabled" ${controls.read_enabled ? "checked" : ""}> Read</label>
      <label><input type="checkbox" id="cognition-write-enabled" ${controls.write_enabled ? "checked" : ""}> Write</label>
    </div>
    <div class="cognition-memory-stats">
      <span>Episoden: <strong>${episodes.length}</strong></span>
      <span>Integrity: <strong>${data.integrity_status || "—"}</strong></span>
    </div>`;
  const readCb = el.querySelector("#cognition-read-enabled");
  const writeCb = el.querySelector("#cognition-write-enabled");
  if (readCb) readCb.addEventListener("change", () => updateControls(readCb, writeCb));
  if (writeCb) writeCb.addEventListener("change", () => updateControls(readCb, writeCb));
}

async function updateControls(readCb, writeCb) {
  try {
    await apiPost("/api/cognition/memory/controls", {
      read_enabled: readCb?.checked ?? false,
      write_enabled: writeCb?.checked ?? false,
    });
  } catch (e) {
    // silently fail — UI reflects backend state on next refresh
  }
}

function renderWorldModel(data) {
  const el = document.getElementById("cognition-world-model-detail");
  if (!el) return;
  if (!data || data.available === false) { el.textContent = "World Model nicht verfügbar"; return; }
  const predictions = data.predictions || [];
  el.innerHTML = `
    <div class="cognition-world-model-stats">
      <span>Mode: <strong>${data.mode || "—"}</strong></span>
      <span>Predictions: <strong>${predictions.length}</strong></span>
      <span>Accuracy: <strong>${data.accuracy != null ? Number(data.accuracy).toFixed(3) : "—"}</strong></span>
    </div>
    ${predictions.length ? `<table class="cognition-prediction-table"><thead><tr><th>Tick</th><th>Predicted</th><th>Observed</th><th>Error</th></tr></thead><tbody>${predictions.slice(0, 10).map(p => `<tr><td>${p.tick ?? "—"}</td><td>${escapeHtml(String(p.predicted ?? "—"))}</td><td>${escapeHtml(String(p.observed ?? "—"))}</td><td>${p.error != null ? Number(p.error).toFixed(4) : "—"}</td></tr>`).join("")}</tbody></table>` : "<p>Keine Vorhersagen verfügbar.</p>"}`;
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel || panel.hidden) return;
  try {
    const [state, memory, worldModel] = await Promise.allSettled([
      apiGet("/api/cognition/state"),
      apiGet("/api/cognition/memory"),
      apiGet("/api/cognition/world-model"),
    ]);
    if (state.status === "fulfilled") renderState(state.value);
    else document.getElementById("cognition-state-detail").textContent = `Fehler: ${state.reason.message}`;
    if (memory.status === "fulfilled") renderMemory(memory.value);
    else document.getElementById("cognition-memory-detail").textContent = `Fehler: ${memory.reason.message}`;
    if (worldModel.status === "fulfilled") renderWorldModel(worldModel.value);
    else document.getElementById("cognition-world-model-detail").textContent = `Fehler: ${worldModel.reason.message}`;
  } catch (e) {
    // panel-level error
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

export function initCognition() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 5000);
}
