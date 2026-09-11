"use strict";
import { apiGet } from "../core/api.js";

let timer = null;
let lastRefreshAt = 0;
let lastPayload = null;

function runtimeState(status) {
  return status?.status || status?.runtime?.state || status?.runtime?.controller_state || "unknown";
}
function runtimeTick(status) {
  return status?.system?.tick ?? status?.runtime?.tick ?? "unknown";
}
function testStatus(integration) {
  const item = Array.isArray(integration?.items) ? integration.items.find((entry) => entry?.name === "Tests") : null;
  return item?.status || integration?.overall || "unknown";
}
function activeExperiment(mode) {
  const session = mode?.active_session;
  return session?.session_id || session?.experiment_id || "none";
}
function ageLabel() {
  if (!lastRefreshAt) return "unknown";
  const seconds = Math.max(0, Math.floor((Date.now() - lastRefreshAt) / 1000));
  return seconds > 30 ? `stale ${seconds}s` : `${seconds}s`;
}
function ensureBar() {
  let bar = document.getElementById("mhrn-global-status");
  if (bar) return bar;
  bar = document.createElement("section");
  bar.id = "mhrn-global-status";
  bar.className = "mhrn-global-status";
  bar.setAttribute("aria-label", "Globaler System- und Wissenschaftsstatus");
  bar.innerHTML = `
    <span><small>Runtime</small><strong data-gs="runtime">unknown</strong></span>
    <span><small>Tick</small><strong data-gs="tick">unknown</strong></span>
    <span><small>CI</small><strong data-gs="ci">unknown</strong></span>
    <span><small>Scientific Gate</small><strong data-gs="gate">unknown</strong></span>
    <span><small>Modus</small><strong data-gs="mode">unknown</strong></span>
    <span><small>Experiment</small><strong data-gs="experiment">none</strong></span>
    <span><small>Datenalter</small><strong data-gs="age">unknown</strong></span>
    <button type="button" id="mhrn-notification-toggle" aria-label="Benachrichtigungen öffnen">⚠ <b id="mhrn-notification-count">0</b></button>`;
  const nav = document.querySelector(".brain5d-primary-nav");
  const topbar = document.querySelector(".topbar");
  if (nav) nav.insertAdjacentElement("afterend", bar);
  else topbar?.insertAdjacentElement("afterend", bar);
  return bar;
}
function set(bar, key, value) {
  const target = bar.querySelector(`[data-gs="${key}"]`);
  if (!target) return;
  target.textContent = String(value);
  const normalized = String(value).toLowerCase();
  target.dataset.state = /failed|blocked|error/.test(normalized) ? "failed" : /stale|pending|unknown/.test(normalized) ? "pending" : /passed|running|idle|operator|debug/.test(normalized) ? "ok" : "neutral";
}
async function refresh() {
  const bar = ensureBar();
  const [statusResult, integrationResult, gateResult, modeResult] = await Promise.allSettled([
    apiGet("/api/status"), apiGet("/api/integration/status"), apiGet("/api/gate/status"), apiGet("/api/experiment/mode"),
  ]);
  const status = statusResult.status === "fulfilled" ? statusResult.value : null;
  const integration = integrationResult.status === "fulfilled" ? integrationResult.value : null;
  const gate = gateResult.status === "fulfilled" ? gateResult.value : null;
  const mode = modeResult.status === "fulfilled" ? modeResult.value : null;
  if ([statusResult, integrationResult, gateResult, modeResult].some((result) => result.status === "fulfilled")) lastRefreshAt = Date.now();
  lastPayload = { status, integration, gate, mode, failures: [statusResult, integrationResult, gateResult, modeResult].filter((r) => r.status === "rejected").map((r) => String(r.reason?.message || r.reason)) };
  set(bar, "runtime", runtimeState(status));
  set(bar, "tick", runtimeTick(status));
  set(bar, "ci", testStatus(integration));
  set(bar, "gate", gate?.overall || gate?.status || "unknown");
  set(bar, "mode", mode?.current_mode || "unknown");
  set(bar, "experiment", activeExperiment(mode));
  set(bar, "age", ageLabel());
  window.dispatchEvent(new CustomEvent("mhrn:global-status", { detail: lastPayload }));
}
function tickAge() {
  const bar = ensureBar();
  set(bar, "age", ageLabel());
}
export function initStatusBar() {
  ensureBar();
  refresh();
  if (timer) clearInterval(timer);
  timer = setInterval(() => { refresh(); tickAge(); }, 3000);
}
export { refresh as refreshStatusBar };
