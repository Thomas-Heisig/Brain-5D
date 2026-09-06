/**
 * Brain-5D Dashboard — Console Log (pure output component)
 *
 * This module provides only the console log output. It does not send
 * control commands; it only displays command results and system events.
 *
 * The dashboard shell, operator experience, real-body embodiment view and
 * Wesen workspace are imported for presentation/read-only side effects.
 *
 * @version 1.4.5
 * @license MIT
 */

"use strict";

import "./dashboard-shell.js";
import "./dashboard-experience.js";
import "./embodiment-self-model.js";
import "./wesen.js";
import "./wesen-organism-v2.js";
import "./wesen-anatomy-v3.js";
import "./wesen-neural-symbiosis.js";
import "./neuron-model-viewer.js";
import "./frontend-architecture.js";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = String(str);
  return div.innerHTML;
}

function formatTime(date = new Date()) {
  return date.toLocaleTimeString("en-US", { hour12: false });
}

function ensureWesenStylesheet() {
  const stylesheets = [
    ["wesen-base", "/wesen.css"],
    ["wesen-adaptive", "/wesen-adaptive.css"],
    ["wesen-organism", "/wesen-organism.css"],
    ["wesen-anatomy", "/wesen-anatomy-v3.css"],
    ["wesen-neural-symbiosis", "/wesen-neural-symbiosis.css"],
  ];
  stylesheets.forEach(([name, href]) => {
    if (document.querySelector(`link[data-wesen-style="${name}"]`)) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    link.dataset.wesenStyle = name;
    document.head.appendChild(link);
  });
  if (!document.querySelector('style[data-wesen-navigation="true"]')) {
    const style = document.createElement("style");
    style.dataset.wesenNavigation = "true";
    style.textContent = `
      .experience-command-item[data-command-id="workspace:network"],
      .experience-command-item[data-command-id="workspace:gate"] { display: none !important; }
    `;
    document.head.appendChild(style);
  }
}

function activateLegacyWorkspace(name) {
  const button = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (button) {
    button.click();
    return;
  }
  document.querySelectorAll(".tab-btn[data-tab]").forEach((item) => item.classList.remove("active"));
  document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => {
    const active = tab.id === `tab-${name}`;
    tab.classList.toggle("active", active);
    tab.hidden = !active;
  });
  document.body.dataset.currentTab = name;
  document.body.dataset.experienceWorkspace = name;
}

function ensureWesenNavigation() {
  ensureWesenStylesheet();
  const nav = document.querySelector(".tab-nav") || document.querySelector("nav");
  if (!nav || document.querySelector('.tab-btn[data-tab="wesen"]')) return;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "tab-btn";
  button.dataset.tab = "wesen";
  button.textContent = "◉ WESEN";
  button.addEventListener("click", () => activateLegacyWorkspace("wesen"));
  nav.appendChild(button);
}

ensureWesenNavigation();

/**
 * Append one formatted log message to the console output.
 * @param {string} message
 * @param {"info"|"success"|"warning"|"error"} level
 */
function appendLog(message, level = "info") {
  const output = byId("console-output");
  if (!output) return;
  const entry = document.createElement("div");
  entry.className = `log-entry log-${level}`;
  entry.innerHTML = `<span class="log-time">[${formatTime()}]</span> ${escapeHtml(message)}`;
  output.appendChild(entry);
  while (output.children.length > 1000) output.removeChild(output.firstChild);
  output.scrollTop = output.scrollHeight;
}

export const consoleLog = {
  info(message) { appendLog(message, "info"); },
  success(message) { appendLog(message, "success"); },
  warning(message) { appendLog(message, "warning"); },
  error(message) { appendLog(message, "error"); },
};
