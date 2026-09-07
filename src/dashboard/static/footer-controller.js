/* Brain-5D persistent footer controller.
 * Adds reliable runtime controls and immediate command/mode feedback without
 * changing the scientific runtime or evidence paths.
 */
"use strict";

import { readJson } from "./api-client.js";

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

function ensureControls() {
  const root = siteFooter();
  if (!root) return null;
  return root.querySelector("#footer-runtime-start") ? root : null;
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
    data = await readJson(response);
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
    setText("system-status", state);
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
  if (!byId("footer-runtime-state-value")) {
    setText("system-status", runtime.controller_state || runtime.status || state?.status || "unknown");
  }
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
