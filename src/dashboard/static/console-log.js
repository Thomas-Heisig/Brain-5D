/**
 * Brain-5D Dashboard — Console Log (pure output component)
 *
 * This module provides only the console log output. It does not send
 * control commands; it only displays command results and system events.
 *
 * The dashboard shell, operator experience, real-body embodiment view and
 * Wesen workspace are imported for presentation/read-only side effects.
 *
 * @version 1.4.0
 * @license MIT
 */

"use strict";

import "./dashboard-shell.js";
import "./dashboard-experience.js";
import "./embodiment-self-model.js";
import "./wesen.js";

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
  if (document.querySelector('link[data-wesen-style="true"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/wesen.css";
  link.dataset.wesenStyle = "true";
  document.head.appendChild(link);
}

function activateLegacyWorkspace(name) {
  const button = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (button) {
    button.click();
    return;
  }
  document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => {
    const active = tab.id === `tab-${name}`;
    tab.classList.toggle("active", active);
    tab.hidden = !active;
  });
}

function adaptDashboardNavigation() {
  document.querySelector('.tab-btn[data-tab="network"]')?.setAttribute("aria-hidden", "true");
  document.querySelector('.tab-btn[data-tab="gate"]')?.setAttribute("aria-hidden", "true");

  document.querySelectorAll('.experience-command-item[data-command-id="workspace:network"], .experience-command-item[data-command-id="workspace:gate"]').forEach((node) => node.remove());
  document.querySelectorAll('[data-jump-workspace="network"]').forEach((node) => {
    node.dataset.jumpWorkspace = "wesen";
    const strong = node.querySelector("strong");
    const small = node.querySelector("small");
    if (strong) strong.textContent = "Wesen beobachten";
    if (small) small.textContent = "Körper, Zustände, Rückkopplung";
  });

  const bodyShortcut = document.querySelector('[data-overview-tab="embodiment"]');
  if (bodyShortcut) {
    bodyShortcut.dataset.overviewTab = "wesen";
    bodyShortcut.textContent = "◉ Wesen öffnen";
  }
}

function ensureReleaseFooterButton() {
  const footer = document.querySelector("footer");
  if (!footer || footer.querySelector("[data-footer-release]")) return;
  const target = byId("footer-status") || footer.lastElementChild || footer;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "wesen-release-button";
  button.dataset.footerRelease = "true";
  button.textContent = "Release";
  button.title = "Scientific Gate und Release Readiness öffnen";
  button.addEventListener("click", () => activateLegacyWorkspace("gate"));
  target.appendChild(button);
}

function simplifyEmbodimentCopy() {
  const tab = byId("tab-embodiment");
  if (!tab || tab.querySelector("[data-simple-embodiment-note]")) return;
  const header = tab.querySelector(".workspace-header, .dashboard-generated-header");
  if (header) {
    const title = header.querySelector("h2");
    const paragraph = header.querySelector("p");
    if (title) title.textContent = "Embodiment";
    if (paragraph) paragraph.textContent = "Reale Sensoren, Geräte, Aktoren und Körpergrenzen konfigurieren und beobachten.";
  }
  const note = document.createElement("div");
  note.dataset.simpleEmbodimentNote = "true";
  note.className = "dashboard-utility-bar";
  note.innerHTML = '<span class="dashboard-utility-context">Embodiment bleibt die einfache technische Schnittstellen-Seite. Die lebendige Echtzeitdarstellung befindet sich unter <strong>Wesen</strong>.</span>';
  header?.insertAdjacentElement("afterend", note);
}

function initWesenShellIntegration() {
  ensureWesenStylesheet();
  adaptDashboardNavigation();
  ensureReleaseFooterButton();
  simplifyEmbodimentCopy();
  requestAnimationFrame(() => adaptDashboardNavigation());
}

ensureWesenStylesheet();
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initWesenShellIntegration, { once: true });
} else {
  initWesenShellIntegration();
}

/**
 * Console log output controller.
 */
export class ConsoleLog {
  constructor(containerId, options = {}) {
    this.container = byId(containerId);
    this.entries = [];
    this.maxEntries = options.maxEntries || 1000;
    this.autoScroll = options.autoScroll !== false;
  }

  /**
   * Log a message.
   * @param {string} message
   * @param {string} type - 'info', 'success', 'error', 'warning', 'debug'
   */
  log(message, type = "info") {
    const entry = {
      timestamp: new Date(),
      message: String(message),
      type,
    };
    this.entries.push(entry);
    if (this.entries.length > this.maxEntries) {
      this.entries.shift();
    }
    this.render(entry);
  }

  /**
   * Render a single entry.
   * @param {object} entry
   */
  render(entry) {
    if (!this.container) return;
    const div = document.createElement("div");
    div.className = `log-entry log-${entry.type}`;
    div.innerHTML = `<span class="log-time">[${formatTime(entry.timestamp)}]</span> ${escapeHtml(entry.message)}`;
    this.container.appendChild(div);
    if (this.autoScroll) {
      this.container.scrollTop = this.container.scrollHeight;
    }
    while (this.container.children.length > this.maxEntries) {
      this.container.removeChild(this.container.firstChild);
    }
  }

  /**
   * Clear the log.
   */
  clear() {
    if (this.container) {
      this.container.innerHTML = "";
    }
    this.entries = [];
  }

  /**
   * Get all entries.
   */
  getEntries() {
    return [...this.entries];
  }
}

/**
 * Shared console log instance.
 */
export const consoleLog = new ConsoleLog("console-output");
