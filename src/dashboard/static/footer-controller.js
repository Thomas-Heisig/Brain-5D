/* Brain-5D persistent footer controller
 *
 * Owns the visible footer interaction contract. Existing app.js controls are
 * intercepted in capture phase to avoid duplicate command dispatch while the
 * legacy dashboard lifecycle remains intact.
 */
"use strict";

import { dashboardStore } from "./state-store.js";

const COMMANDS = {
  "footer-runtime-start": "start",
  "footer-runtime-pause": "pause",
  "footer-runtime-stop": "stop",
};

let commandInFlight = false;
let lastCommand = "bereit";
let lastKind = "idle";

function byId(id) {
  return document.getElementById(id);
}

function footer() {
  return document.querySelector(".site-footer");
}

function setText(id, value) {
  const node = byId(id);
  if (node) node.textContent = String(value);
}

function injectStyles() {
  if (document.querySelector("style[data-footer-controller]")) return;
  const style = document.createElement("style");
  style.dataset.footerController = "true";
  style.textContent = `
    .site-footer { position:relative; z-index:40; pointer-events:auto; }
    .site-footer button,.site-footer input,.site-footer select { pointer-events:auto; }
    .footer-command-strip { grid-column:1 / -1; display:flex; flex-wrap:wrap; align-items:center; gap:.55rem; min-height:30px; padding:.35rem .8rem; border-top:1px solid var(--line,rgba(127,127,127,.18)); background:rgba(127,127,127,.035); font-size:.72rem; }
    .footer-command-feedback { display:inline-flex; align-items:center; min-width:220px; gap:.35rem; font-weight:650; }
    .footer-command-feedback[data-kind="working"] { opacity:.9; }
    .footer-command-feedback[data-kind="success"] { color:var(--success,#60d394); }
    .footer-command-feedback[data-kind="error"] { color:var(--danger,#ff6b6b); }
    .footer-runtime-state { display:inline-flex; gap:.35rem; align-items:center; padding:.18rem .45rem; border:1px solid var(--line,rgba(127,127,127,.22)); border-radius:999px; }
    .footer-runtime-state[data-state="running"] { border-color:rgba(80,210,145,.5); }
    .footer-runtime-state[data-state="paused"] { border-color:rgba(235,180,70,.5); }
    .footer-runtime-state[data-state="stopped"],.footer-runtime-state[data-state="idle"] { opacity:.78; }
    .footer-safe-note { opacity:.62; margin-left:auto; }
    .site-footer [data-command-busy="true"] { cursor:progress; opacity:.62; }
    @media(max-width:850px){.footer-command-strip{align-items:flex-start}.footer-safe-note{width:100%;margin-left:0}}
  `;
  document.head.appendChild(style);
}

function ensureStrip() {
  const root = footer();
  if (!root) return null;
  let strip = root.querySelector(".footer-command-strip");
  if (strip) return strip;
  strip = document.createElement("div");
  strip.className = "footer-command-strip";
  strip.setAttribute("role", "status");
  strip.setAttribute("aria-live", "polite");
  strip.innerHTML = `
    <span class="footer-command-feedback" id="footer-command-feedback" data-kind="idle">● bereit</span>
    <span class="footer-runtime-state" id="footer-runtime-state" data-state="unknown">Runtime: <strong id="footer-runtime-state-value">—</strong></span>
    <span>Tick <strong id="footer-runtime-tick">—</strong></span>
    <span>Mode <strong id="footer-mode-value">—</strong></span>
    <span class="footer-safe-note">Play schützt die Bedienbarkeit: bei ungebremstem MAX wird 1 ms Batch-Yield gesetzt.</span>`;
  root.appendChild(strip);
  return strip;
}

function feedback(text, kind = "idle") {
  lastCommand = text;
  lastKind = kind;
  const node = byId("footer-command-feedback");
  if (!node) return;
  node.textContent = `${kind === "working" ? "◌" : kind === "success" ? "✓" : kind === "error" ? "!" : "●"} ${text}`;
  node.dataset.kind = kind;
}

function runtimeStateFrom(state) {
  const runtime = state?.runtime || {};
  return String(
    runtime.controller_state || runtime.status || state?.status || "unknown"
  ).toLowerCase();
}

function renderState(state) {
  ensureStrip();
  const runtimeState = runtimeStateFrom(state);
  const stateNode = byId("footer-runtime-state");
  if (stateNode) stateNode.dataset.state = runtimeState;
  setText("footer-runtime-state-value", runtimeState);
  setText("footer-runtime-tick", state?.runtime?.tick ?? state?.system?.tick ?? "—");
  const mode = state?.experiment_state?.current_mode || state?.experiment_state?.mode;
  if (mode) setText("footer-mode-value", mode);
  if (!commandInFlight && lastKind === "working") feedback("bereit", "idle");
}

async function json(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  let data = {};
  try { data = await response.json(); } catch { data = {}; }
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || data.message || `HTTP ${response.status}`);
  }
  return data;
}

async function control(command, params = {}) {
  return json("/api/control", {
    method: "POST",
    body: JSON.stringify({ command, ...params }),
  });
}

function setButtonsBusy(busy) {
  for (const id of Object.keys(COMMANDS)) {
    const button = byId(id);
    if (!button) continue;
    button.disabled = busy;
    button.dataset.commandBusy = String(busy);
  }
}

async function makeStartResponsive() {
  const state = await json("/api/control");
  const runtime = state.runtime || state.state?.runtime || state.state || state;
  const delay = Number(runtime.loop_delay_ms ?? runtime.delay_ms ?? 0);
  const target = runtime.target_hz;
  if ((target == null || target === 0 || String(target).toUpperCase() === "MAX") && delay <= 0) {
    feedback("MAX erkannt · UI-Yield wird gesetzt …", "working");
    await control("configure", { delay_ms: 1 });
  }
}

async function executeFooterCommand(id) {
  if (commandInFlight) {
    feedback("Befehl läuft bereits …", "working");
    return;
  }
  const command = COMMANDS[id];
  if (!command) return;
  commandInFlight = true;
  setButtonsBusy(true);
  feedback(`${command} wird gesendet …`, "working");
  try {
    if (command === "start") await makeStartResponsive();
    const result = await control(command);
    const runtime = result.runtime || {};
    const state = String(runtime.controller_state || runtime.status || command);
    feedback(`${command} bestätigt · ${state}`, "success");
    setText("footer-runtime-state-value", state);
    await dashboardStore.refresh();
  } catch (error) {
    feedback(`${command} fehlgeschlagen: ${error.message}`, "error");
  } finally {
    commandInFlight = false;
    setButtonsBusy(false);
  }
}

function bindCaptureControls() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest?.("#footer-runtime-start,#footer-runtime-pause,#footer-runtime-stop");
    if (!button) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    executeFooterCommand(button.id);
  }, true);
}

function bindModeFeedback() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest?.("#experiment-mode-switcher .mode-btn");
    if (!button) return;
    const mode = button.dataset.mode;
    if (!mode) return;
    feedback(`Mode → ${mode} …`, "working");
    setText("footer-mode-value", mode);
  });
  const badge = byId("experiment-status-badge");
  if (badge && typeof MutationObserver !== "undefined") {
    new MutationObserver(() => {
      const value = badge.textContent?.trim();
      if (!value) return;
      setText("footer-mode-value", value);
      if (!commandInFlight) feedback(`Mode bestätigt · ${value}`, "success");
    }).observe(badge, { childList: true, subtree: true, characterData: true });
  }
}

function init() {
  injectStyles();
  ensureStrip();
  bindCaptureControls();
  bindModeFeedback();
  dashboardStore.subscribe(renderState);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}

window.Brain5DFooterController = { execute: executeFooterCommand };
