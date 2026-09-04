/**
 * Brain-5D Dashboard — Console Log (pure output component)
 *
 * This module provides only the console log output.  It does not send
 * control commands; it only displays command results and system events.
 *
 * The real-body embodiment view is imported for its read-only dashboard
 * side effect.  It consumes only published API data and never issues runtime
 * control commands.
 *
 * @version 1.1.0
 * @license MIT
 */

"use strict";

import "./embodiment-self-model.js";

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