/* Brain-5D persistent footer controller.
 * Adds reliable runtime controls and immediate command/mode feedback without
 * changing the scientific runtime or evidence paths.
 */
"use strict";

import { dashboardStore } from "./state-store.js";

const COMMANDS = {
  "footer-runtime-start": "start",
  "footer-runtime-pause": "pause",
  "footer-runtime-stop": "stop",
};

let commandInFlight = false;
let lastFeedbackKind = "idle";

function byId(id) {
  return document.getElementById(id);
}

function siteFooter() {
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
    .brain5d-footer-control { display:grid; grid-template-columns:auto auto auto auto 1fr; align-items:center; gap:.55rem; width:100%; padding:.42rem .75rem; border-top:1px solid var(--line,rgba(127,127,127,.2)); background:rgba(127,127,127,.04); font-size:.72rem; }
    .brain5d-footer-actions { display:flex; align-items:center; gap:.3rem; }
    .brain5d-footer-actions button { min-width:32px; min-height:28px; border:1px solid var(--line,rgba(127,127,127,.25)); border-radius:7px; background:var(--panel,#101c27); color:inherit; cursor:pointer; }
    .brain5d-footer-actions button:hover:not(:disabled) { background:rgba(127,127,127,.15); }
    .brain5d-footer-actions button:disabled { opacity:.45; cursor:progress; }
    .brain5d-footer-feedback { min-width:220px; font-weight:650; }
    .brain5d-footer-feedback[data-kind="success"] { color:var(--success,#5bd39a); }
    .brain5d-footer-feedback[data-kind="error"] { color:var(--danger,#ff7070); }
    .brain5d-footer-feedback[data-kind="working"] { opacity:.85; }
    .brain5d-footer-pill { display:inline-flex; align-items:center; gap:.3rem; border:1px solid var(--line,rgba(127,127,127,.22)); border-radius:999px; padding:.18rem .48rem; white-space:nowrap; }
    .brain5d-footer-note { justify-self:end; opacity:.6; text-align:right; }
    @media(max-width:900px){.brain5d-footer-control{grid-template-columns:1fr auto auto}.brain5d-footer-feedback{grid-column:1/-1;min-width:0}.brain5d-footer-note{grid-column:1/-1;justify-self:start;text-align:left}}
  `;
  document.head.appendChild(style);
}

function ensureControls() {
  const root = siteFooter();
  if (!root) return null;
  let panel = root.querySelector("[data-brain5d-footer-control]");
  if (panel) return panel;
  panel = document.createElement("div");
  panel.className = "brain5d-footer-control";
  panel.dataset.brain5dFooterControl = "true";
  panel.setAttribute("role", "status");
  panel.setAttribute("aria-live", "polite");
  panel.innerHTML = `
    <div class="brain5d-footer-actions" aria-label="Runtime-Steuerung">
      <button id="footer-runtime-start" type="button" title="Runtime starten" aria-label="Runtime starten">▶</button>
      <button id="footer-runtime-pause" type="button" title="Runtime pausieren" aria-label="Runtime pausieren">Ⅱ</button>
      <button id="footer-runtime-stop" type="button" title="Runtime stoppen" aria-label="Runtime stoppen">■</button>
    </div>
    <span class="brain5d-footer-pill">Runtime <strong id="footer-runtime-state-value">—</strong></span>
    <span class="brain5d-footer-pill">Tick <strong id="footer-runtime-tick">—</strong></span>
    <span class="brain5d-footer-pill">Mode <strong id="footer-mode-value">—</strong></span>
    <span class="brain5d-footer-feedback" id="footer-command-feedback" data-kind="idle">● bereit</span>
    <span class="brain5d-footer-note">Play setzt bei ungebremstem MAX 1 ms Batch-Yield, damit die Oberfläche bedienbar bleibt.</span>`;
  root.appendChild(panel);
  return panel;
}

function feedback(text, kind = "idle") {
  lastFeedbackKind = kind;
  const node = byId("footer-command-feedback");
  if (!node) return;
  const marker = kind === "working" ? "◌" : kind === "success" ? "✓" : kind === "error" ? "!" : "●";
  node.textContent = `${marker} ${text}`;
  node.dataset.kind = kind;
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
  try {
    data = await response.json();
  } catch (_) {
    data = {};
  }
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

function setBusy(busy) {
  Object.keys(COMMANDS).forEach((id) => {
    const button = byId(id);
    if (button) button.disabled = busy;
  });
}

async function ensureResponsiveStart() {
  const state = await json("/api/control");
  const runtime = state.runtime || state.state?.runtime || state.state || state;
  const delay = Number(runtime.loop_delay_ms ?? runtime.delay_ms ?? 0);
  const target = runtime.target_hz;
  const uncapped = target == null || target === 0 || String(target).toUpperCase() === "MAX";
  if (uncapped && delay <= 0) {
    feedback("MAX erkannt · UI-Yield wird gesetzt …", "working");
    await control("configure", { delay_ms: 1 });
  }
}

async function execute(id) {
  const command = COMMANDS[id];
  if (!command) return;
  if (commandInFlight) {
    feedback("Befehl läuft bereits …", "working");
    return;
  }
  commandInFlight = true;
  setBusy(true);
  feedback(`${command} wird gesendet …`, "working");
  try {
    if (command === "start") await ensureResponsiveStart();
    const result = await control(command);
    const runtime = result.runtime || {};
    const state = String(runtime.controller_state || runtime.status || command);
    setText("footer-runtime-state-value", state);
    feedback(`${command} bestätigt · ${state}`, "success");
    await dashboardStore.refresh();
  } catch (error) {
    feedback(`${command} fehlgeschlagen: ${error.message}`, "error");
  } finally {
    commandInFlight = false;
    setBusy(false);
  }
}

function render(state) {
  ensureControls();
  const runtime = state?.runtime || {};
  setText("footer-runtime-state-value", runtime.controller_state || runtime.status || state?.status || "unknown");
  setText("footer-runtime-tick", runtime.tick ?? state?.system?.tick ?? "—");
  const mode = state?.experiment_state?.current_mode || state?.experiment_state?.mode;
  if (mode) setText("footer-mode-value", mode);
  if (!commandInFlight && lastFeedbackKind === "working") feedback("bereit", "idle");
}

function bindRuntime() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest?.("#footer-runtime-start,#footer-runtime-pause,#footer-runtime-stop");
    if (!button) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    execute(button.id);
  }, true);
}

function bindModeFeedback() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest?.("#experiment-mode-switcher .mode-btn");
    if (!button?.dataset.mode) return;
    setText("footer-mode-value", button.dataset.mode);
    feedback(`Mode → ${button.dataset.mode} …`, "working");
  });
  const badge = byId("experiment-status-badge");
  if (badge && typeof MutationObserver !== "undefined") {
    new MutationObserver(() => {
      const mode = badge.textContent?.trim();
      if (!mode) return;
      setText("footer-mode-value", mode);
      if (!commandInFlight) feedback(`Mode bestätigt · ${mode}`, "success");
    }).observe(badge, { childList: true, subtree: true, characterData: true });
  }
}

function init() {
  injectStyles();
  ensureControls();
  bindRuntime();
  bindModeFeedback();
  dashboardStore.subscribe(render);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}

window.Brain5DFooterController = { execute };
