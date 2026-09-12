"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-system-info");
  if (panel) return panel;
  const workspace = document.getElementById("tab-overview");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-system-info";
  panel.className = "mhrn-system-info card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">SYSTEM INFO · RELEASE · SNAPSHOTS</span>
        <h2>System-Informationen</h2>
        <p>Aktuelle Konfiguration, System-State, Release-Info und Snapshots.</p>
      </div>
      <span id="system-info-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="system-info-grid">
      <div class="system-info-section">
        <h3>System-Konfiguration</h3>
        <div id="system-config-detail" class="system-info-detail">lade …</div>
      </div>
      <div class="system-info-section">
        <h3>System-State</h3>
        <div id="system-state-detail" class="system-info-detail">lade …</div>
      </div>
      <div class="system-info-section">
        <h3>Aktuelles Release</h3>
        <div id="system-release-detail" class="system-info-detail">lade …</div>
      </div>
      <div class="system-info-section">
        <h3>Snapshots</h3>
        <div id="system-snapshots-detail" class="system-info-detail">lade …</div>
      </div>
    </div>`;
  workspace.append(panel);
  return panel;
}

function renderConfig(data) {
  const el = document.getElementById("system-config-detail");
  if (!el) return;
  if (!data) { el.textContent = "Keine Konfigurationsdaten."; return; }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  el.innerHTML = `<dl>${entries.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(typeof v === "object" ? JSON.stringify(v) : String(v))}</dd>`).join("")}</dl>`;
}

function renderState(data) {
  const el = document.getElementById("system-state-detail");
  if (!el) return;
  if (!data) { el.textContent = "Keine State-Daten."; return; }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined);
  el.innerHTML = `<dl>${entries.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(typeof v === "object" ? JSON.stringify(v) : String(v))}</dd>`).join("")}</dl>`;
  const badge = document.getElementById("system-info-badge");
  if (badge) badge.textContent = data.status || data.mode || "aktiv";
}

function renderRelease(data) {
  const el = document.getElementById("system-release-detail");
  if (!el) return;
  if (!data) { el.textContent = "Keine Release-Info."; return; }
  el.innerHTML = `
    <div class="release-info">
      <span>Version: <strong>${escapeHtml(data.version || "—")}</strong></span>
      <span>Tag: <strong>${escapeHtml(data.tag || "—")}</strong></span>
      <span>Datum: <strong>${escapeHtml(data.date || data.created || "—")}</strong></span>
      <span>Status: <strong>${escapeHtml(data.status || "—")}</strong></span>
      ${data.commit ? `<span>Commit: <code>${escapeHtml(data.commit)}</code></span>` : ""}
      ${data.notes ? `<details><summary>Release Notes</summary><pre>${escapeHtml(data.notes)}</pre></details>` : ""}
    </div>`;
}

function renderSnapshots(data) {
  const el = document.getElementById("system-snapshots-detail");
  if (!el) return;
  const snapshots = Array.isArray(data) ? data : (data?.snapshots || []);
  if (!snapshots.length) { el.textContent = "Keine Snapshots."; return; }
  el.innerHTML = `<table class="snapshots-table"><thead><tr><th>ID</th><th>Tick</th><th>Erstellt</th><th>Größe</th></tr></thead><tbody>
    ${snapshots.slice(0, 10).map(s => `<tr><td>${escapeHtml(s.id || s.snapshot_id || "—")}</td><td>${s.tick ?? "—"}</td><td>${escapeHtml(s.created_at || s.date || "—")}</td><td>${escapeHtml(s.size || "—")}</td></tr>`).join("")}
  </tbody></table>`;
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  const [config, state, release, snapshots] = await Promise.allSettled([
    apiGet("/api/config"),
    apiGet("/api/state"),
    apiGet("/api/releases/current"),
    apiGet("/api/snapshots"),
  ]);
  if (config.status === "fulfilled") renderConfig(config.value);
  else document.getElementById("system-config-detail").textContent = `Fehler: ${config.reason.message}`;
  if (state.status === "fulfilled") renderState(state.value);
  else document.getElementById("system-state-detail").textContent = `Fehler: ${state.reason.message}`;
  if (release.status === "fulfilled") renderRelease(release.value);
  else document.getElementById("system-release-detail").textContent = `Fehler: ${release.reason.message}`;
  if (snapshots.status === "fulfilled") renderSnapshots(snapshots.value);
  else document.getElementById("system-snapshots-detail").textContent = `Fehler: ${snapshots.reason.message}`;
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

export function initSystemInfo() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 5000);
}
