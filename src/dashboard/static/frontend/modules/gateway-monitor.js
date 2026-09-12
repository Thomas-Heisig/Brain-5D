"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-gateway-monitor");
  if (panel) return panel;
  const workspace = document.getElementById("tab-embodiment");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-gateway-monitor";
  panel.className = "mhrn-gateway-monitor card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">NEURAL SYMBIOSIS · GATEWAY RUNTIMES</span>
        <h2>Gateway-Runtimes</h2>
        <p>Aktive Gateway-Runtimes und zugehörige Experimente.</p>
      </div>
      <span id="gateway-count-badge" class="maturity-state pending">lade …</span>
    </header>
    <div class="gateway-grid">
      <div class="gateway-section">
        <h3>Gateways</h3>
        <div id="gateway-list" class="gateway-list">lade …</div>
      </div>
      <div class="gateway-section">
        <h3>Gateway-Experimente</h3>
        <div id="gateway-experiment-list" class="gateway-list">lade …</div>
      </div>
    </div>`;
  workspace.append(panel);
  return panel;
}

function renderGateways(data) {
  const el = document.getElementById("gateway-list");
  if (!el) return;
  const gateways = Array.isArray(data) ? data : (data?.gateways || []);
  if (!gateways.length) { el.textContent = "Keine Gateways registriert."; return; }
  el.innerHTML = gateways.map(g => {
    const state = g.state || g.status || "unknown";
    const cls = state === "active" ? "passed" : state === "disabled" ? "stale" : "pending";
    return `<div class="gateway-card gateway-${cls}">
      <div class="gateway-card-header">
        <strong>${escapeHtml(g.gateway_id || g.id || "—")}</strong>
        <span class="maturity-state ${cls}">${escapeHtml(state)}</span>
      </div>
      <div class="gateway-card-body">
        <span>Modality: ${escapeHtml(g.modality || "—")}</span>
        <span>Resource Mode: ${escapeHtml(g.resource_mode || "—")}</span>
        <span>Limits: in=${g.limits?.input_dim ?? "—"} / out=${g.limits?.output_dim ?? "—"}</span>
      </div>
    </div>`;
  }).join("");
  const badge = document.getElementById("gateway-count-badge");
  if (badge) badge.textContent = `${gateways.length} Gateway(s)`;
}

function renderExperiments(data) {
  const el = document.getElementById("gateway-experiment-list");
  if (!el) return;
  const experiments = Array.isArray(data) ? data : (data?.experiments || []);
  if (!experiments.length) { el.textContent = "Keine Gateway-Experimente."; return; }
  el.innerHTML = experiments.map(e => {
    const status = e.status || e.state || "unknown";
    const cls = status === "running" ? "passed" : status === "completed" ? "stale" : "pending";
    return `<div class="gateway-card gateway-${cls}">
      <div class="gateway-card-header">
        <strong>${escapeHtml(e.experiment_id || e.id || "—")}</strong>
        <span class="maturity-state ${cls}">${escapeHtml(status)}</span>
      </div>
      <div class="gateway-card-body">
        <span>Gateway: ${escapeHtml(e.gateway_id || "—")}</span>
        <span>Preregistration: ${escapeHtml(e.preregistration_id || "—")}</span>
        <span>Mode: ${escapeHtml(e.experiment_mode || "—")}</span>
      </div>
    </div>`;
  }).join("");
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  try {
    const [gw, exp] = await Promise.allSettled([
      apiGet("/api/embodiment/gateways"),
      apiGet("/api/embodiment/gateway-experiments"),
    ]);
    if (gw.status === "fulfilled") renderGateways(gw.value);
    else document.getElementById("gateway-list").textContent = `Fehler: ${gw.reason.message}`;
    if (exp.status === "fulfilled") renderExperiments(exp.value);
    else document.getElementById("gateway-experiment-list").textContent = `Fehler: ${exp.reason.message}`;
  } catch (e) {
    // panel-level error
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

export function initGatewayMonitor() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 5000);
}
