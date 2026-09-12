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
  if (!lastRefreshAt) return "—";
  const seconds = Math.max(0, Math.floor((Date.now() - lastRefreshAt) / 1000));
  return seconds > 30 ? `stale ${seconds}s` : `${seconds}s`;
}

/** The footer already exists in the HTML — just query it. */
function getBar() {
  return document.getElementById("mhrn-global-status");
}

function set(bar, key, value) {
  const target = bar.querySelector(`[data-gs="${key}"]`);
  if (!target) return;
  target.textContent = String(value);
  const normalized = String(value).toLowerCase();
  target.dataset.state = /failed|blocked|error/.test(normalized) ? "failed" : /stale|pending|unknown/.test(normalized) ? "pending" : /passed|running|idle|operator|debug/.test(normalized) ? "ok" : "neutral";
}

async function refresh() {
  const bar = getBar();
  if (!bar) return;
  const [statusResult, integrationResult, gateResult, modeResult] = await Promise.allSettled([
    apiGet("/api/status"), apiGet("/api/integration/status"), apiGet("/api/gate/status"), apiGet("/api/experiment/mode"),
  ]);
  const status = statusResult.status === "fulfilled" ? statusResult.value : null;
  const integration = integrationResult.status === "fulfilled" ? integrationResult.value : null;
  const gate = gateResult.status === "fulfilled" ? gateResult.value : null;
  const mode = modeResult.status === "fulfilled" ? modeResult.value : null;
  if ([statusResult, integrationResult, gateResult, modeResult].some((result) => result.status === "fulfilled")) lastRefreshAt = Date.now();
  lastPayload = { status, integration, gate, mode, failures: [statusResult, integrationResult, gateResult, modeResult].filter((r) => r.status === "rejected").map((r) => String(r.reason?.message || r.reason)) };

  // Update footer status-pill + tick
  const statusEl = document.getElementById("system-status");
  if (statusEl) {
    const state = runtimeState(status);
    statusEl.textContent = state;
    statusEl.dataset.state = /failed|blocked|error/.test(state) ? "failed" : /stale|pending|unknown/.test(state) ? "pending" : /passed|running|idle|operator|debug/.test(state) ? "ok" : "neutral";
  }
  const tickEl = document.getElementById("footer-runtime-tick");
  if (tickEl) tickEl.textContent = runtimeTick(status);

  // Update footer CI / Gate / Age
  set(bar, "ci", testStatus(integration));
  set(bar, "gate", gate?.overall || gate?.status || "unknown");
  set(bar, "age", ageLabel());

  // Update mode badge (top-right)
  const modeBadge = document.getElementById("mhrn-mode-badge");
  if (modeBadge) {
    const mode = modeResult.status === "fulfilled" ? modeResult.value : null;
    const currentMode = mode?.current_mode || "unknown";
    modeBadge.textContent = `✓ ${currentMode}`;
    modeBadge.className = "mhrn-badge";
    modeBadge.classList.add(/operator|debug/.test(currentMode) ? "mhrn-badge-ok" : "mhrn-badge-warn");
  }

  // Update experiment state in footer
  const expState = document.getElementById("footer-experiment-state");
  const expId = document.getElementById("footer-experiment-id");
  const expSeg = document.getElementById("footer-experiment");
  if (expState) expState.textContent = modeResult.status === "fulfilled" ? (modeResult.value?.current_mode || "inactive") : "inactive";
  if (expId) expId.textContent = activeExperiment(modeResult.status === "fulfilled" ? modeResult.value : null);
  if (expSeg) expSeg.dataset.active = String(modeResult.status === "fulfilled" && modeResult.value?.current_mode && modeResult.value.current_mode !== "operator");

  window.dispatchEvent(new CustomEvent("mhrn:global-status", { detail: lastPayload }));
}

function tickAge() {
  const bar = getBar();
  if (!bar) return;
  set(bar, "age", ageLabel());
}

export function initStatusBar() {
  refresh();
  if (timer) clearInterval(timer);
  timer = setInterval(() => { refresh(); tickAge(); }, 3000);
}
export { refresh as refreshStatusBar };
