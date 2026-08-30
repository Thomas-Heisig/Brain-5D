/**
 * Brain-5D Parameter Inspector — ES Module
 *
 * Displays runtime/config parameters, lets operators propose changes,
 * and manages the pending-changes workflow (apply / apply+save / cancel).
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

function formatValue(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function classForPending(change) {
  if (!change) return "";
  if (change.requires_restart) return "pending-restart";
  if (change.scientific_sensitive) return "pending-sensitive";
  return "pending-value";
}

/**
 * API client for parameter and pending-change endpoints.
 */
export class ParameterAPI {
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

  static async listParameters() {
    return this.fetchJSON("/api/parameters");
  }

  static async getParameter(name) {
    return this.fetchJSON(`/api/parameters/${encodeURIComponent(name)}`);
  }

  static async proposeChange(name, value) {
    return this.fetchJSON(`/api/parameters/${encodeURIComponent(name)}/pending`, {
      method: "POST",
      body: JSON.stringify({ value }),
    });
  }

  static async apply(names = null, saveProfile = false) {
    const endpoint = saveProfile ? "/api/parameters/pending/save-profile" : "/api/parameters/pending/apply";
    const body = names === null ? {} : { names };
    return this.fetchJSON(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  static async cancel(names = null) {
    const body = names === null ? {} : { names };
    return this.fetchJSON("/api/parameters/pending/cancel", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  static async pending() {
    return this.fetchJSON("/api/parameters/pending");
  }
}

/**
 * ParameterInspector component.
 */
export class ParameterInspector {
  constructor() {
    this.parameters = {};
    this.pending = {};
    this.history = [];
    this.filter = "";
    this.commandInFlight = false;

    this._elements = {
      tableBody: byId("parameter-table-body"),
      search: byId("parameter-search"),
      reload: byId("parameter-reload"),
      pendingBar: byId("pending-changes-bar"),
      pendingCount: byId("pending-count"),
      pendingRestartHint: byId("pending-restart-hint"),
      applyBtn: byId("pending-apply"),
      saveProfileBtn: byId("pending-save-profile"),
      cancelBtn: byId("pending-cancel"),
      historyList: byId("change-history-list"),
    };

    this._bindEvents();
  }

  _bindEvents() {
    if (this._elements.search) {
      this._elements.search.addEventListener("input", (e) => {
        this.filter = (e.target.value || "").toLowerCase().trim();
        this._render();
      });
    }

    if (this._elements.reload) {
      this._elements.reload.addEventListener("click", () => this.refresh());
    }

    if (this._elements.applyBtn) {
      this._elements.applyBtn.addEventListener("click", () => this._apply(false));
    }

    if (this._elements.saveProfileBtn) {
      this._elements.saveProfileBtn.addEventListener("click", () => this._apply(true));
    }

    if (this._elements.cancelBtn) {
      this._elements.cancelBtn.addEventListener("click", () => this._cancel());
    }

    const table = byId("parameter-table");
    if (table) {
      table.addEventListener("click", (e) => this._handleTableClick(e));
    }
  }

  async refresh() {
    try {
      const paramsData = await ParameterAPI.listParameters();
      const pendingData = await ParameterAPI.pending();
      this.parameters = paramsData.parameters || {};
      this.pending = pendingData.pending || {};
      this.history = pendingData.history || [];
      this._render();
    } catch (error) {
      this._log(`Failed to load parameters: ${error.message}`, "error");
    }
  }

  _handleTableClick(e) {
    const editBtn = e.target.closest(".param-edit");
    if (editBtn) {
      e.preventDefault();
      const name = editBtn.dataset.name;
      if (name) this._editParameter(name);
      return;
    }

    const resetBtn = e.target.closest(".param-reset");
    if (resetBtn) {
      e.preventDefault();
      const name = resetBtn.dataset.name;
      if (name) this._resetToDefault(name);
      return;
    }

    const cancelBtn = e.target.closest(".param-cancel");
    if (cancelBtn) {
      e.preventDefault();
      const name = cancelBtn.dataset.name;
      if (name) this._cancel([name]);
    }
  }

  async _editParameter(name) {
    const parameter = this.parameters[name];
    if (!parameter) return;

    const raw = prompt(`New value for ${name}:`, formatValue(parameter.value));
    if (raw === null) return;

    let value;
    try {
      value = this._parseInput(raw, parameter);
    } catch (error) {
      this._log(`Invalid value for ${name}: ${error.message}`, "error");
      return;
    }

    try {
      await ParameterAPI.proposeChange(name, value);
      this._log(`Pending change recorded for ${name}`, "info");
      await this.refresh();
    } catch (error) {
      this._log(`Failed to propose change: ${error.message}`, "error");
    }
  }

  async _resetToDefault(name) {
    const parameter = this.parameters[name];
    if (!parameter || parameter.default === null || parameter.default === undefined) {
      this._log(`No default value for ${name}`, "warning");
      return;
    }
    try {
      await ParameterAPI.proposeChange(name, parameter.default);
      this._log(`Pending reset to default for ${name}`, "info");
      await this.refresh();
    } catch (error) {
      this._log(`Failed to reset ${name}: ${error.message}`, "error");
    }
  }

  async _apply(saveProfile) {
    if (this.commandInFlight) return;
    this.commandInFlight = true;
    try {
      const result = await ParameterAPI.apply(null, saveProfile);
      this._log(
        `Applied ${result.applied?.length || 0} parameter(s)${saveProfile ? " and saved profile" : ""}`,
        "success"
      );
      await this.refresh();
    } catch (error) {
      this._log(`Apply failed: ${error.message}`, "error");
    } finally {
      this.commandInFlight = false;
    }
  }

  async _cancel(names = null) {
    if (this.commandInFlight) return;
    this.commandInFlight = true;
    try {
      const result = await ParameterAPI.cancel(names);
      this._log(`Cancelled ${result.cancelled?.length || 0} pending change(s)`, "info");
      await this.refresh();
    } catch (error) {
      this._log(`Cancel failed: ${error.message}`, "error");
    } finally {
      this.commandInFlight = false;
    }
  }

  _parseInput(raw, parameter) {
    if (typeof parameter.value === "boolean") {
      return ["true", "1", "yes", "on"].includes(raw.toLowerCase());
    }
    if (typeof parameter.value === "number") {
      const num = Number(raw);
      if (!Number.isFinite(num)) throw new Error("not a number");
      return Number.isInteger(parameter.value) ? Math.trunc(num) : num;
    }
    if (typeof parameter.value === "string") {
      return raw;
    }
    try {
      return JSON.parse(raw);
    } catch {
      return raw;
    }
  }

  _render() {
    this._renderTable();
    this._renderPendingBar();
    this._renderHistory();
  }

  _renderTable() {
    const tbody = this._elements.tableBody;
    if (!tbody) return;

    const names = Object.keys(this.parameters).filter((name) =>
      this.filter ? name.toLowerCase().includes(this.filter) : true
    );

    if (names.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="parameter-empty">No parameters match</td></tr>`;
      return;
    }

    let html = "";
    for (const name of names.sort()) {
      const param = this.parameters[name];
      const change = this.pending[name];
      const pendingClass = classForPending(change);
      const pendingValue = change ? formatValue(change.proposed_value) : "";
      const currentValue = formatValue(param.value);
      const defaultValue = param.default !== null && param.default !== undefined
        ? formatValue(param.default)
        : "—";
      const mutableBadge = param.runtime_mutable
        ? '<span class="param-badge mutable">runtime</span>'
        : '<span class="param-badge immutable">fixed</span>';
      const restartBadge = param.requires_restart
        ? '<span class="param-badge restart" title="Requires restart">R</span>'
        : "";
      const sensitiveBadge = param.scientific_sensitive
        ? '<span class="param-badge sensitive" title="Scientifically sensitive">S</span>'
        : "";
      const actions = change
        ? `<button class="btn-small param-cancel" data-name="${escapeHtml(name)}">Cancel</button>`
        : `<button class="btn-small param-edit" data-name="${escapeHtml(name)}">Edit</button>
           <button class="btn-small param-reset" data-name="${escapeHtml(name)}">Reset</button>`;

      html += `
        <tr class="${pendingClass}" data-name="${escapeHtml(name)}">
          <td class="param-name" title="${escapeHtml(param.description || "")}">
            ${escapeHtml(name)}
            ${sensitiveBadge}
          </td>
          <td class="param-current">${escapeHtml(currentValue)}</td>
          <td class="param-pending">${pendingValue ? escapeHtml(pendingValue) : "—"}</td>
          <td class="param-default">${escapeHtml(defaultValue)}</td>
          <td class="param-source">${escapeHtml(param.source || "—")}</td>
          <td>${mutableBadge}</td>
          <td>${restartBadge}</td>
          <td class="param-actions">${actions}</td>
        </tr>
      `;
    }
    tbody.innerHTML = html;
  }

  _renderPendingBar() {
    const count = Object.keys(this.pending).length;
    if (this._elements.pendingCount) {
      this._elements.pendingCount.textContent = String(count);
    }
    if (this._elements.pendingBar) {
      this._elements.pendingBar.classList.toggle("has-pending", count > 0);
    }
    if (this._elements.pendingRestartHint) {
      const needsRestart = Object.values(this.pending).some((c) => c.requires_restart);
      this._elements.pendingRestartHint.style.display = needsRestart ? "inline" : "none";
    }
  }

  _renderHistory() {
    const container = this._elements.historyList;
    if (!container) return;

    if (this.history.length === 0) {
      container.innerHTML = '<div class="change-history-empty">No changes recorded yet</div>';
      return;
    }

    let html = "";
    for (const record of [...this.history].reverse()) {
      const actionClass = record.action === "applied" ? "applied" : "cancelled";
      const profileBadge = record.saved_profile ? '<span class="param-badge profile">profile</span>' : "";
      html += `
        <div class="change-history-item ${actionClass}">
          <span class="change-history-name">${escapeHtml(record.name)}</span>
          <span class="change-history-action">${escapeHtml(record.action)}</span>
          ${profileBadge}
          <span class="change-history-time">${escapeHtml(record.timestamp || "—")}</span>
          <div class="change-history-values">
            <span>old: ${escapeHtml(formatValue(record.old_value))}</span>
            ${record.new_value !== undefined && record.new_value !== null ? `<span>new: ${escapeHtml(formatValue(record.new_value))}</span>` : ""}
          </div>
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
