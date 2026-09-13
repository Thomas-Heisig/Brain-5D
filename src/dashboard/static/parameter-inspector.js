/**
 * MHRN Parameter Inspector — ES Module
 *
 * Displays runtime/config parameters, lets operators propose changes,
 * and manages the pending-changes workflow (apply / apply+save / cancel).
 *
 * The dedicated neuron model editor intentionally stages changes through the
 * same ParameterAPI. Model selection therefore keeps the existing provenance,
 * scientific-sensitivity and restart semantics instead of bypassing them.
 *
 * @version 1.1.0
 * @license MIT
 */

"use strict";

const NEURON_MODEL_CATALOG = Object.freeze({
  "izhikevich-2003": Object.freeze({
    label: "Izhikevich 2003",
    version: "mhrn-1.0",
    maturity: "canonical",
    equation: "Izhikevich two-variable spiking model",
    note: "Canonical Stage-0 reference model. Model changes require a new run/restart.",
    fields: [
      "neuron.a",
      "neuron.b",
      "neuron.c",
      "neuron.d",
      "neuron.initial_v",
      "neuron.initial_u",
      "neuron.izhikevich_threshold",
    ],
  }),
  "lif-current-v1": Object.freeze({
    label: "Current-based LIF",
    version: "mhrn-1.0",
    maturity: "experimental",
    equation: "Current-based leaky integrate-and-fire",
    note: "Alternative experimental treatment. Selecting it is a scientific condition change and requires a new run/restart.",
    fields: [
      "neuron.initial_v",
      "neuron.lif_resting_potential",
      "neuron.lif_tau_m_ms",
      "neuron.lif_resistance",
      "neuron.lif_threshold",
      "neuron.lif_reset",
    ],
  }),
});

const COMMON_NEURON_FIELDS = Object.freeze([
  "neuron.refractory_ticks",
  "neuron.enable_threshold_adaptation",
  "neuron.enable_energy_dynamics",
  "neuron.enable_traces",
  "neuron.enable_homeostasis",
]);

const NEURON_FIELD_LABELS = Object.freeze({
  "neuron.a": "a · recovery time scale",
  "neuron.b": "b · recovery sensitivity",
  "neuron.c": "c · reset potential",
  "neuron.d": "d · recovery reset increment",
  "neuron.initial_v": "Initial membrane potential",
  "neuron.initial_u": "Initial recovery variable",
  "neuron.izhikevich_threshold": "Spike threshold",
  "neuron.lif_resting_potential": "Resting potential",
  "neuron.lif_tau_m_ms": "Membrane time constant",
  "neuron.lif_resistance": "Input resistance",
  "neuron.lif_threshold": "Spike threshold",
  "neuron.lif_reset": "Reset potential",
  "neuron.refractory_ticks": "Absolute refractory ticks",
  "neuron.enable_threshold_adaptation": "Threshold adaptation",
  "neuron.enable_energy_dynamics": "Energy dynamics",
  "neuron.enable_traces": "STDP traces",
  "neuron.enable_homeostasis": "Homeostatic regulation",
});

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

    this._ensureNeuronModelUI();

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
      neuronCard: byId("neuron-model-settings"),
      neuronModel: byId("neuron-model-select"),
      neuronMaturity: byId("neuron-model-maturity"),
      neuronVersion: byId("neuron-model-version"),
      neuronEquation: byId("neuron-model-equation"),
      neuronNotice: byId("neuron-model-notice"),
      neuronFields: byId("neuron-model-fields"),
      neuronStage: byId("neuron-model-stage"),
      neuronFocus: byId("neuron-model-focus-parameters"),
      neuronStatus: byId("neuron-model-status"),
    };

    this._bindEvents();
  }

  _ensureNeuronModelUI() {
    if (!document.querySelector('link[data-neuron-model-settings]')) {
      const stylesheet = document.createElement("link");
      stylesheet.rel = "stylesheet";
      stylesheet.href = "/neuron-model-settings.css";
      stylesheet.dataset.neuronModelSettings = "true";
      document.head.appendChild(stylesheet);
    }

    const filterRoot = byId("settings-domain-filter");
    if (filterRoot && !filterRoot.querySelector('[data-settings-filter="neuron."]')) {
      const neuronFilter = document.createElement("button");
      neuronFilter.type = "button";
      neuronFilter.dataset.settingsFilter = "neuron.";
      neuronFilter.textContent = "Neuron";
      const networkButton = filterRoot.querySelector('[data-settings-filter="network."]');
      if (networkButton?.nextSibling) {
        filterRoot.insertBefore(neuronFilter, networkButton.nextSibling);
      } else {
        filterRoot.appendChild(neuronFilter);
      }
    }

    if (byId("neuron-model-settings")) return;
    const parameterCard = byId("parameter-inspector-card");
    if (!parameterCard?.parentElement) return;

    const card = document.createElement("section");
    card.className = "card neuron-model-settings";
    card.id = "neuron-model-settings";
    card.setAttribute("aria-labelledby", "neuron-model-settings-title");
    card.innerHTML = `
      <div class="panel-title neuron-model-settings__header">
        <div>
          <span class="workspace-kicker">STAGE 0 · SINGLE CELL</span>
          <h2 id="neuron-model-settings-title">Neuron / Cell Model</h2>
          <p class="panel-subtitle">Select the membrane model and stage scientifically sensitive construction parameters.</p>
        </div>
        <div class="neuron-model-provenance" aria-label="Model provenance">
          <span id="neuron-model-maturity" class="neuron-model-badge">unknown</span>
          <span><b id="neuron-model-version">—</b><small>implementation</small></span>
        </div>
      </div>
      <div class="neuron-model-selector-row">
        <label for="neuron-model-select">Dynamics model
          <select id="neuron-model-select" aria-describedby="neuron-model-notice">
            <option value="izhikevich-2003">Izhikevich 2003 · canonical</option>
            <option value="lif-current-v1">Current-based LIF · experimental</option>
          </select>
        </label>
        <div class="neuron-model-equation">
          <span>Equation family</span>
          <strong id="neuron-model-equation">—</strong>
        </div>
      </div>
      <div id="neuron-model-notice" class="neuron-model-warning" role="note">
        Model and construction parameter changes are scientifically sensitive and require a new run/restart. Existing live neuron state is not silently rewritten.
      </div>
      <div id="neuron-model-fields" class="neuron-model-fields" aria-live="polite"></div>
      <div class="neuron-model-actions">
        <span id="neuron-model-status" class="neuron-model-status">Load parameters to edit the Stage-0 cell model.</span>
        <button id="neuron-model-focus-parameters" type="button" class="btn-secondary">Show raw neuron parameters</button>
        <button id="neuron-model-stage" type="button" class="btn-primary">Stage neuron changes</button>
      </div>
    `;
    parameterCard.parentElement.insertBefore(card, parameterCard);
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

    if (this._elements.neuronModel) {
      this._elements.neuronModel.addEventListener("change", () => this._renderNeuronModelEditor());
    }

    if (this._elements.neuronStage) {
      this._elements.neuronStage.addEventListener("click", () => this._stageNeuronModelChanges());
    }

    if (this._elements.neuronFocus) {
      this._elements.neuronFocus.addEventListener("click", () => this._focusNeuronParameters());
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
      this._setNeuronStatus(`Failed to load neuron settings: ${error.message}`, "error");
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
      value = this._parseInput(raw, parameter, name);
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

  _parseInput(raw, parameter, name = parameter?.name || "") {
    if (typeof parameter.value === "boolean") {
      const normalized = raw.toLowerCase().trim();
      if (!["true", "1", "yes", "on", "false", "0", "no", "off"].includes(normalized)) {
        throw new Error("expected true/false");
      }
      return ["true", "1", "yes", "on"].includes(normalized);
    }
    if (typeof parameter.value === "number") {
      const num = Number(raw);
      if (!Number.isFinite(num)) throw new Error("not a finite number");
      if (parameter.min !== null && parameter.min !== undefined && num < Number(parameter.min)) {
        throw new Error(`must be >= ${parameter.min}`);
      }
      if (parameter.max !== null && parameter.max !== undefined && num > Number(parameter.max)) {
        throw new Error(`must be <= ${parameter.max}`);
      }
      return Number.isInteger(parameter.value) ? Math.trunc(num) : num;
    }
    if (typeof parameter.value === "string") {
      if (name === "neuron.model" && !Object.hasOwn(NEURON_MODEL_CATALOG, raw)) {
        throw new Error(`unsupported neuron model '${raw}'`);
      }
      return raw;
    }
    try {
      return JSON.parse(raw);
    } catch {
      return raw;
    }
  }

  _effectiveParameterValue(name) {
    const pending = this.pending[name];
    if (pending && Object.hasOwn(pending, "proposed_value")) return pending.proposed_value;
    return this.parameters[name]?.value;
  }

  _renderNeuronModelEditor() {
    const select = this._elements.neuronModel;
    const fieldsRoot = this._elements.neuronFields;
    if (!select || !fieldsRoot) return;

    const configuredModel = this._effectiveParameterValue("neuron.model");
    if (!select.dataset.userTouched && configuredModel && Object.hasOwn(NEURON_MODEL_CATALOG, configuredModel)) {
      select.value = configuredModel;
    }
    select.oninput = () => {
      select.dataset.userTouched = "true";
    };

    const selectedModel = Object.hasOwn(NEURON_MODEL_CATALOG, select.value)
      ? select.value
      : "izhikevich-2003";
    const descriptor = NEURON_MODEL_CATALOG[selectedModel];

    if (this._elements.neuronMaturity) {
      this._elements.neuronMaturity.textContent = descriptor.maturity;
      this._elements.neuronMaturity.dataset.maturity = descriptor.maturity;
    }
    if (this._elements.neuronVersion) this._elements.neuronVersion.textContent = descriptor.version;
    if (this._elements.neuronEquation) this._elements.neuronEquation.textContent = descriptor.equation;
    if (this._elements.neuronNotice) this._elements.neuronNotice.textContent = descriptor.note;

    const names = [...descriptor.fields, ...COMMON_NEURON_FIELDS];
    fieldsRoot.innerHTML = names.map((name) => this._renderNeuronField(name)).join("");

    const modelPending = this.pending["neuron.model"];
    const modelChanged = modelPending
      ? modelPending.proposed_value !== this.parameters["neuron.model"]?.value
      : selectedModel !== configuredModel;
    this._setNeuronStatus(
      modelChanged
        ? "Model treatment differs from the active configuration. Stage changes, then apply through the global pending-change bar."
        : "Editor is synchronized with the active/pending neuron configuration.",
      modelChanged ? "warning" : "ok"
    );
  }

  _renderNeuronField(name) {
    const parameter = this.parameters[name];
    if (!parameter) {
      return `<label class="neuron-model-field neuron-model-field--missing"><span>${escapeHtml(NEURON_FIELD_LABELS[name] || name)}</span><input disabled value="not exposed" /></label>`;
    }

    const value = this._effectiveParameterValue(name);
    const label = NEURON_FIELD_LABELS[name] || name;
    const pending = this.pending[name];
    const pendingBadge = pending ? '<small class="neuron-field-pending">pending</small>' : "";

    if (typeof parameter.value === "boolean") {
      return `
        <label class="neuron-model-field neuron-model-field--toggle" title="${escapeHtml(parameter.description || name)}">
          <span>${escapeHtml(label)} ${pendingBadge}</span>
          <input type="checkbox" data-neuron-parameter="${escapeHtml(name)}" ${value ? "checked" : ""} />
        </label>
      `;
    }

    const min = parameter.min !== null && parameter.min !== undefined ? ` min="${escapeHtml(parameter.min)}"` : "";
    const max = parameter.max !== null && parameter.max !== undefined ? ` max="${escapeHtml(parameter.max)}"` : "";
    const step = Number.isInteger(parameter.value) ? "1" : "any";
    const unit = parameter.unit ? `<small>${escapeHtml(parameter.unit)}</small>` : "";
    return `
      <label class="neuron-model-field" title="${escapeHtml(parameter.description || name)}">
        <span>${escapeHtml(label)} ${pendingBadge}</span>
        <div class="neuron-model-field__input">
          <input type="number" data-neuron-parameter="${escapeHtml(name)}" value="${escapeHtml(value)}" step="${step}"${min}${max} />
          ${unit}
        </div>
      </label>
    `;
  }

  async _stageNeuronModelChanges() {
    if (this.commandInFlight) return;
    const select = this._elements.neuronModel;
    const fieldsRoot = this._elements.neuronFields;
    if (!select || !fieldsRoot) return;

    const model = select.value;
    if (!Object.hasOwn(NEURON_MODEL_CATALOG, model)) {
      this._setNeuronStatus(`Unsupported neuron model: ${model}`, "error");
      return;
    }

    const proposals = [];
    const modelParameter = this.parameters["neuron.model"];
    if (!modelParameter) {
      this._setNeuronStatus("neuron.model is not exposed by the runtime configuration.", "error");
      return;
    }
    if (this._effectiveParameterValue("neuron.model") !== model) {
      proposals.push(["neuron.model", model]);
    }

    for (const input of fieldsRoot.querySelectorAll("[data-neuron-parameter]")) {
      const name = input.dataset.neuronParameter;
      const parameter = this.parameters[name];
      if (!name || !parameter) continue;

      let value;
      try {
        value = typeof parameter.value === "boolean"
          ? Boolean(input.checked)
          : this._parseInput(input.value, parameter, name);
      } catch (error) {
        this._setNeuronStatus(`${name}: ${error.message}`, "error");
        input.focus();
        return;
      }

      if (value !== this._effectiveParameterValue(name)) proposals.push([name, value]);
    }

    if (proposals.length === 0) {
      this._setNeuronStatus("No neuron changes to stage.", "ok");
      return;
    }

    this.commandInFlight = true;
    this._elements.neuronStage.disabled = true;
    try {
      for (const [name, value] of proposals) {
        await ParameterAPI.proposeChange(name, value);
      }
      delete select.dataset.userTouched;
      this._log(`Staged ${proposals.length} neuron parameter change(s)`, "info");
      this._setNeuronStatus(`Staged ${proposals.length} change(s). Review and apply them below; restart/new run is required for fixed model parameters.`, "warning");
      await this.refresh();
    } catch (error) {
      this._setNeuronStatus(`Failed to stage neuron changes: ${error.message}`, "error");
      this._log(`Failed to stage neuron changes: ${error.message}`, "error");
    } finally {
      this.commandInFlight = false;
      this._elements.neuronStage.disabled = false;
    }
  }

  _focusNeuronParameters() {
    if (!this._elements.search) return;
    this._elements.search.value = "neuron.";
    this._elements.search.dispatchEvent(new Event("input", { bubbles: true }));
    byId("parameter-inspector-card")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  _setNeuronStatus(message, state = "ok") {
    if (!this._elements?.neuronStatus) return;
    this._elements.neuronStatus.textContent = message;
    this._elements.neuronStatus.dataset.state = state;
  }

  _render() {
    this._renderTable();
    this._renderPendingBar();
    this._renderHistory();
    this._renderNeuronModelEditor();
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
            <span class="parameter-help" tabindex="0" title="${escapeHtml(param.description || `Configuration value ${name}`)}">?</span>
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
      this._elements.pendingRestartHint.classList.toggle("is-hidden", !needsRestart);
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
