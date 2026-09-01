/**
 * Brain-5D Experiment Mode — ES Module
 *
 * Manages Operator / Experiment / Debug mode switching and structured
 * experiment session metadata (hypothesis, notes, session history).
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(str) {
  if (str == null) return "";
  const div = document.createElement("div");
  div.textContent = String(str);
  return div.innerHTML;
}

/**
 * API client for experiment-mode endpoints.
 */
export class ExperimentAPI {
  static async fetchJSON(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Cache-Control": "no-store",
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || data.message || `HTTP ${response.status}`);
    }
    return data;
  }

  static async getMode() {
    return this.fetchJSON("/api/experiment/mode");
  }

  static async setMode(mode) {
    return this.fetchJSON("/api/experiment/mode", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
  }

  static async startSession(sessionId, mode, hypothesis = "", note = "") {
    return this.fetchJSON("/api/experiment/session/start", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        mode,
        hypothesis,
        note,
      }),
    });
  }

  static async stopSession(endTick = null) {
    const body = endTick !== null ? { end_tick: endTick } : {};
    return this.fetchJSON("/api/experiment/session/stop", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  static async addNote(note) {
    return this.fetchJSON("/api/experiment/note", {
      method: "POST",
      body: JSON.stringify({ note }),
    });
  }

  static async listSessions() {
    return this.fetchJSON("/api/experiment/sessions");
  }
}

/**
 * ExperimentMode component.
 */
export class ExperimentMode {
  constructor() {
    this.mode = "operator";
    this.activeSession = null;
    this.sessions = [];

    this._elements = {
      switcher: byId("experiment-mode-switcher"),
      panelTitle: byId("experiment-panel-title"),
      panelSubtitle: byId("experiment-panel-subtitle"),
      statusBadge: byId("experiment-status-badge"),
      sessionId: byId("experiment-session-id"),
      hypothesis: byId("experiment-hypothesis"),
      startBtn: byId("experiment-start"),
      stopBtn: byId("experiment-stop"),
      noteInput: byId("experiment-note"),
      addNoteBtn: byId("experiment-add-note"),
      sessionList: byId("experiment-session-list"),
    };

    this._bindEvents();
  }

  _bindEvents() {
    if (this._elements.switcher) {
      this._elements.switcher.addEventListener("click", (e) => {
        const btn = e.target.closest(".mode-btn");
        if (!btn) return;
        const mode = btn.dataset.mode;
        if (mode) this._setMode(mode);
      });
    }

    if (this._elements.startBtn) {
      this._elements.startBtn.addEventListener("click", () => this._startSession());
    }

    if (this._elements.stopBtn) {
      this._elements.stopBtn.addEventListener("click", () => this._stopSession());
    }

    if (this._elements.addNoteBtn) {
      this._elements.addNoteBtn.addEventListener("click", () => this._addNote());
    }

    if (this._elements.noteInput) {
      this._elements.noteInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this._addNote();
      });
    }
  }

  async refresh() {
    try {
      const data = await ExperimentAPI.getMode();
      this.mode = data.current_mode || "operator";
      this.activeSession = data.active_session || null;
      this.sessions = data.sessions || [];
      this._render();
    } catch (error) {
      this._log(`Failed to load experiment mode: ${error.message}`, "error");
    }
  }

  async _setMode(mode) {
    try {
      await ExperimentAPI.setMode(mode);
      this._log(`Switched to ${mode} mode`, "info");
      await this.refresh();
    } catch (error) {
      this._log(`Failed to set mode: ${error.message}`, "error");
    }
  }

  async _startSession() {
    const sessionIdInput = this._elements.sessionId;
    const hypothesisInput = this._elements.hypothesis;
    const sessionId = (sessionIdInput?.value || "").trim();
    const hypothesis = (hypothesisInput?.value || "").trim();

    if (!sessionId) {
      this._log("Session ID is required", "warning");
      return;
    }

    try {
      await ExperimentAPI.startSession(sessionId, this.mode, hypothesis);
      this._log(`Started ${this.mode} session '${sessionId}'`, "success");
      if (sessionIdInput) sessionIdInput.value = "";
      if (hypothesisInput) hypothesisInput.value = "";
      await this.refresh();
    } catch (error) {
      this._log(`Failed to start session: ${error.message}`, "error");
    }
  }

  async _stopSession() {
    try {
      await ExperimentAPI.stopSession();
      this._log("Session stopped", "info");
      await this.refresh();
    } catch (error) {
      this._log(`Failed to stop session: ${error.message}`, "error");
    }
  }

  async _addNote() {
    const input = this._elements.noteInput;
    const note = (input?.value || "").trim();
    if (!note) return;

    try {
      await ExperimentAPI.addNote(note);
      this._log("Note added", "info");
      if (input) input.value = "";
      await this.refresh();
    } catch (error) {
      this._log(`Failed to add note: ${error.message}`, "error");
    }
  }

  _render() {
    this._renderSwitcher();
    this._renderPanel();
    this._renderSessionList();
  }

  _renderSwitcher() {
    if (!this._elements.switcher) return;
    this._elements.switcher.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.mode === this.mode);
    });
  }

  _renderPanel() {
    const modeLabels = {
      operator: { icon: "🎮", title: "Operator Session", subtitle: "Normal operation and monitoring" },
      experiment: { icon: "🔬", title: "Experiment Session", subtitle: "Log structured experiment metadata" },
      debug: { icon: "🐛", title: "Debug Session", subtitle: "Extra instrumentation and detailed logging" },
    };
    const label = modeLabels[this.mode] || modeLabels.operator;

    if (this._elements.panelTitle) {
      this._elements.panelTitle.textContent = `${label.icon} ${label.title}`;
    }
    if (this._elements.panelSubtitle) {
      this._elements.panelSubtitle.textContent = label.subtitle;
    }
    if (this._elements.statusBadge) {
      this._elements.statusBadge.textContent = this.mode;
      this._elements.statusBadge.className = `experiment-badge mode-${this.mode}`;
    }

    const hasActive = this.activeSession !== null;
    const footer = byId("footer-experiment");
    if (footer) footer.dataset.active = String(hasActive);
    if (byId("footer-experiment-state")) {
      byId("footer-experiment-state").textContent = hasActive ? "running" : "inactive";
    }
    if (byId("footer-experiment-id")) {
      byId("footer-experiment-id").textContent = this.activeSession?.session_id || "no session";
    }
    if (this._elements.startBtn) {
      this._elements.startBtn.disabled = hasActive;
    }
    if (this._elements.stopBtn) {
      this._elements.stopBtn.disabled = !hasActive;
    }
  }

  _renderSessionList() {
    const container = this._elements.sessionList;
    if (!container) return;

    if (this.sessions.length === 0) {
      container.innerHTML = '<div class="experiment-empty">No sessions recorded yet</div>';
      return;
    }

    let html = "";
    for (const session of [...this.sessions].reverse()) {
      const noteCount = session.notes ? session.notes.length : 0;
      const statusClass = session.active ? "active" : "closed";
      html += `
        <div class="experiment-session-item ${statusClass}">
          <div class="experiment-session-header">
            <span class="experiment-session-mode mode-${session.mode}">${escapeHtml(session.mode)}</span>
            <span class="experiment-session-id">${escapeHtml(session.session_id)}</span>
            <span class="experiment-session-status">${session.active ? "active" : "closed"}</span>
          </div>
          <div class="experiment-session-hypothesis">${escapeHtml(session.hypothesis || "—")}</div>
          <div class="experiment-session-meta">
            <span>Tick ${session.start_tick}${session.end_tick != null ? ` → ${session.end_tick}` : ""}</span>
            <span>${escapeHtml(session.start_time || "—")}</span>
            <span>${noteCount} note(s)</span>
          </div>
          ${session.notes && session.notes.length > 0 ? `<ul class="experiment-session-notes">${session.notes.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>` : ""}
        </div>
      `;
    }
    container.innerHTML = html;
  }

  _log(message, type = "info") {
    import("./console-log.js")
      .then(({ consoleLog }) => consoleLog.log(message, type))
      .catch(() => {});
  }
}
