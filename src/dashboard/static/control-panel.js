/**
 * Brain-5D Control Panel — ES Module
 *
 * This module is a pure ES module. It does NOT self-initialize and does NOT
 * register any DOMContentLoaded listeners. The sole lifecycle owner is
 * `app.js`, which imports and instantiates `ControlPanel` exactly once when
 * the Control & Console tab is first activated.
 *
 * Responsibility: runtime configuration and self-organization policy.
 * Runtime commands (step/run/pause/resume/stop/snapshot) are handled by
 * OperatorConsole to keep a single source of truth for operator actions.
 *
 * Canonical command contract (unified with OperatorConsole):
 *   POST /api/control  { "command": "run_ticks", "ticks": 100 }
 *
 * No CommonJS fallbacks. No `module.exports`. No global side effects on import.
 *
 * @version 2.2.0
 * @license MIT
 */

"use strict";

// ============================================================================
// DOM Helpers
// ============================================================================

/**
 * Get element by ID.
 * @param {string} id - Element ID
 * @returns {HTMLElement | null}
 */
function byId(id) {
  return document.getElementById(id);
}

/**
 * Get element by ID with type safety.
 * @param {string} id - Element ID
 * @param {string} context - Context for error message
 * @returns {HTMLElement}
 * @throws {Error} If element not found
 */
function requireElement(id, context = 'element') {
  const el = byId(id);
  if (!el) {
    throw new Error(`Required element "${id}" not found (${context})`);
  }
  return el;
}

/**
 * Set text content safely.
 * @param {string} id - Element ID
 * @param {string} text - Text to set
 */
function setText(id, text) {
  const el = byId(id);
  if (el) el.textContent = text;
}

/**
 * Set element disabled state.
 * @param {string} id - Element ID
 * @param {boolean} disabled - Whether to disable
 */
function setDisabled(id, disabled) {
  const el = byId(id);
  if (el) el.disabled = disabled;
}

// ============================================================================
// Utilities
// ============================================================================

/**
 * Debounce a function.
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/**
 * Format a number.
 * @param {number} value - Number to format
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted string
 */
function formatNumber(value, decimals = 2) {
  return Number(value || 0).toFixed(decimals);
}

/**
 * Get numeric value from element.
 * @param {HTMLElement | null} element - Input element
 * @param {number} fallback - Default value
 * @returns {number} Numeric value
 */
function getNumericValue(element, fallback = 0) {
  if (!element) return fallback;
  const value = Number(element.value);
  return Number.isFinite(value) ? value : fallback;
}

/**
 * Get integer value from element.
 * @param {HTMLElement | null} element - Input element
 * @param {number} fallback - Default value
 * @returns {number} Integer value
 */
function getIntegerValue(element, fallback = 0) {
  return Math.trunc(getNumericValue(element, fallback));
}

// ============================================================================
// API Client — canonical command contract
// ============================================================================

export class ControlAPI {
  /**
   * Fetch JSON from the control endpoint.
   * @param {string} endpoint - API endpoint
   * @param {object} options - Fetch options
   * @returns {Promise<Object>} JSON response
   */
  static async fetchJSON(endpoint, options = {}) {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Cache-Control': 'no-store',
        ...(options.headers || {}),
      },
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || data.message || `HTTP ${response.status}`);
    }
    return data;
  }

  /**
   * Get control state.
   * @returns {Promise<Object>} Control state
   */
  static async getState() {
    return this.fetchJSON('/api/control');
  }

  /**
   * Execute a control command.
   * Canonical contract: POST /api/control  { "command": "run_ticks", "ticks": 100 }
   * @param {string} command - Command name
   * @param {object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  static async executeCommand(command, params = {}) {
    return this.fetchJSON('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, ...params }),
    });
  }

  /**
   * Step ticks.
   * @param {number} ticks - Number of ticks
   * @returns {Promise<Object>} Result
   */
  static async step(ticks = 1) {
    return this.executeCommand('step', { ticks });
  }

  /**
   * Run ticks.
   * @param {number} ticks - Number of ticks
   * @returns {Promise<Object>} Result
   */
  static async runTicks(ticks = 100) {
    return this.executeCommand('run_ticks', { ticks });
  }

  /**
   * Start runtime (continuous execution).
   * @returns {Promise<Object>} Result
   */
  static async start() {
    return this.executeCommand('start');
  }

  /**
   * Pause runtime.
   * @returns {Promise<Object>} Result
   */
  static async pause() {
    return this.executeCommand('pause');
  }

  /**
   * Resume runtime.
   * @returns {Promise<Object>} Result
   */
  static async resume() {
    return this.executeCommand('resume');
  }

  /**
   * Stop runtime.
   * @returns {Promise<Object>} Result
   */
  static async stop() {
    return this.executeCommand('stop');
  }

  /**
   * Configure runtime.
   * @param {object} config - Configuration
   * @returns {Promise<Object>} Result
   */
  static async configure(config) {
    return this.executeCommand('configure', config);
  }

  /**
   * Request snapshot.
   * @returns {Promise<Object>} Result
   */
  static async snapshot() {
    return this.executeCommand('snapshot');
  }

  /**
   * Configure self-organization.
   * @param {object} config - Configuration
   * @returns {Promise<Object>} Result
   */
  static async configureSelfOrganization(config) {
    return this.executeCommand('self_organization', config);
  }
}

// ============================================================================
// Control State
// ============================================================================

export class ControlState {
  constructor() {
    this.runtime = null;
    this.selfOrganization = null;
    this.lastError = null;
    this.lastUpdate = 0;
    this._listeners = [];
  }

  /**
   * Register a state change listener.
   * @param {Function} listener - Listener function
   */
  addListener(listener) {
    this._listeners.push(listener);
  }

  /**
   * Notify listeners of state change.
   */
  notify() {
    this._listeners.forEach(fn => fn(this));
  }

  /**
   * Update state from payload.
   * @param {Object} payload - State payload
   */
  update(payload) {
    this.runtime = payload.runtime || payload;
    this.selfOrganization = payload.self_organization || null;
    this.lastUpdate = Date.now();
    this.lastError = null;
    this.notify();
  }

  /**
   * Set error state.
   * @param {string} error - Error message
   */
  setError(error) {
    this.lastError = error;
    this.notify();
  }

  /**
   * Get runtime mode.
   * @returns {string} Runtime mode
   */
  getMode() {
    return this.runtime?.mode || 'unknown';
  }

  /**
   * Get ticks executed.
   * @returns {number} Ticks executed
   */
  getTicks() {
    return this.runtime?.ticks_executed || 0;
  }

  /**
   * Get queued ticks.
   * @returns {number} Queued ticks
   */
  getQueuedTicks() {
    return this.runtime?.queued_ticks || 0;
  }

  /**
   * Get last batch ticks.
   * @returns {number} Last batch ticks
   */
  getLastBatchTicks() {
    return this.runtime?.last_batch_ticks || 0;
  }

  /**
   * Get last batch time.
   * @returns {number} Last batch time in ms
   */
  getLastBatchMs() {
    return this.runtime?.last_batch_ms || 0;
  }

  /**
   * Check if snapshot is available.
   * @returns {boolean} Whether snapshot is available
   */
  canSnapshot() {
    return this.runtime?.can_snapshot !== false;
  }
}

// ============================================================================
// Control Panel
// ============================================================================

export class ControlPanel {
  constructor() {
    this.state = new ControlState();
    this.pollingInterval = null;
    this.pollingRate = 500; // ms
    this.commandInFlight = false;

    // DOM references
    this._elements = {};
    this._initElements();
    this._initStateListeners();
    this._initEventListeners();
    this._initKeyboardShortcuts();

    // Start polling
    this.startPolling();
  }

  // ========================================================================
  // DOM Initialization
  // ========================================================================

  _initElements() {
    const ids = [
      'runtime-state',
      'runtime-tick',
      'runtime-queued',
      'runtime-last-batch',
      'runtime-last-ms',
      'loop-size',
      'delay-ms',
      'apply-runtime-config',
      'self-org-enabled',
      'self-org-dry-run',
      'self-org-proposal',
      'self-org-status-badge',
      'control-message',
    ];

    for (const id of ids) {
      this._elements[id] = byId(id);
    }

    // Log missing elements (warning only)
    for (const [id, el] of Object.entries(this._elements)) {
      if (!el) {
        console.warn(`Control panel: Element "#${id}" not found`);
      }
    }
  }

  /**
   * Get a DOM element with type safety.
   * @param {string} id - Element ID
   * @param {string} context - Context for error
   * @returns {HTMLElement}
   */
  _getElement(id, context = 'control') {
    const el = this._elements[id];
    if (!el) {
      throw new Error(`Element "#${id}" not found in ${context}`);
    }
    return el;
  }

  // ========================================================================
  // State Listeners
  // ========================================================================

  _initStateListeners() {
    this.state.addListener((state) => {
      this._render(state);
    });
  }

  // ========================================================================
  // Rendering
  // ========================================================================

  /**
   * Render the control state.
   * @param {ControlState} state - Control state
   */
  _render(state) {
    this._renderBadge(state);
    this._renderMetrics(state);
    this._renderSelfOrganization(state);
    this._renderMessage(state);
  }

  /**
   * Render the state badge.
   * @param {ControlState} state - Control state
   */
  _renderBadge(state) {
    const badge = this._elements['runtime-state'];
    if (!badge) return;

    const mode = state.getMode();
    badge.textContent = mode;
    badge.dataset.mode = mode;

    // Update visual classes
    badge.className = 'status-pill';
    if (mode === 'running') {
      badge.classList.add('running');
    } else if (mode === 'paused') {
      badge.classList.add('paused');
    } else if (mode === 'stopped') {
      badge.classList.add('stopped');
    } else {
      badge.classList.add('idle');
    }
  }

  /**
   * Render runtime metrics.
   * @param {ControlState} state - Control state
   */
  _renderMetrics(state) {
    setText('runtime-tick', String(state.getTicks()));
    setText('runtime-queued', String(state.getQueuedTicks()));
    setText('runtime-last-batch', String(state.getLastBatchTicks()));
    setText('runtime-last-ms', formatNumber(state.getLastBatchMs(), 2));
  }

  /**
   * Render self-organization state.
   *
   * CONFIG-AUTHORITATIVE: When structural plasticity is disabled by config
   * (self_organization.enabled=false in poc_config.yaml), the controls must
   * be visibly disabled and the badge must read "DISABLED BY CONFIG",
   * not the static "Configured" placeholder.
   * @param {ControlState} state - Control state
   */
  async _renderSelfOrganization(state) {
    const selfOrg = state.selfOrganization;
    const badge = this._elements['self-org-status-badge'];
    const enabled = this._elements['self-org-enabled'];
    const dryRun = this._elements['self-org-dry-run'];
    const proposal = this._elements['self-org-proposal'];

    // Query the real structural config from the backend.
    let configured = false;
    let configEnabled = false;
    try {
      const r = await fetch('/api/structural/status', { cache: 'no-store' });
      if (r.ok) {
        const d = await r.json();
        configured = d.configured === true;
      }
    } catch {
      configured = false;
    }
    if (configured) {
      try {
        const r = await fetch('/api/structural/config', { cache: 'no-store' });
        if (r.ok) {
          const d = await r.json();
          configEnabled = d.enabled === true;
        }
      } catch {
        configEnabled = false;
      }
    }

    if (!configured) {
      // Structural plasticity is disabled by config — disable all controls.
      if (badge) {
        badge.textContent = 'DISABLED BY CONFIG';
        badge.className = 'badge badge-disabled';
      }
      if (enabled) { enabled.checked = false; enabled.disabled = true; }
      if (dryRun) { dryRun.checked = false; dryRun.disabled = true; }
      if (proposal) proposal.textContent = 'disabled by config';
      return;
    }

    // Structural is configured and active.
    if (badge) {
      badge.textContent = configEnabled ? 'ACTIVE' : 'CONFIGURED (disabled)';
      badge.className = configEnabled ? 'badge badge-active' : 'badge badge-disabled';
    }
    if (enabled) { enabled.disabled = false; enabled.checked = Boolean(selfOrg?.enabled); }
    if (dryRun) { dryRun.disabled = false; dryRun.checked = Boolean(selfOrg?.dry_run); }

    if (proposal) {
      const last = selfOrg?.last_proposal;
      proposal.textContent = last
        ? `${last.action || 'unknown'} × ${last.count || 0} — ${last.reason || 'no reason'}`
        : 'none';
    }
  }

  /**
   * Render the message area.
   * @param {ControlState} state - Control state
   */
  _renderMessage(state) {
    const msg = this._elements['control-message'];
    if (!msg) return;

    if (state.lastError) {
      msg.textContent = `⚠️ ${state.lastError}`;
      msg.dataset.kind = 'error';
    } else {
      msg.textContent = '✓ Ready';
      msg.dataset.kind = 'info';
    }
  }

  // ========================================================================
  // Event Listeners
  // ========================================================================

  _initEventListeners() {
    // Configure button
    const applyBtn = this._elements['apply-runtime-config'];
    if (applyBtn) {
      applyBtn.addEventListener('click', () => this._handleConfigure());
    }

    // Runtime command buttons
    const stepBtn = byId('step-button');
    if (stepBtn) {
      stepBtn.addEventListener('click', () => this._handleStep());
    }

    const runBtn = byId('run-button');
    if (runBtn) {
      runBtn.addEventListener('click', () => this._handleRunTicks());
    }

    const startBtn = byId('start-button');
    if (startBtn) {
      startBtn.addEventListener('click', () => this._executeCommand(() => ControlAPI.start(), 'start'));
    }

    const pauseBtn = byId('pause-button');
    if (pauseBtn) {
      pauseBtn.addEventListener('click', () => this._executeCommand(() => ControlAPI.pause(), 'pause'));
    }

    const resumeBtn = byId('resume-button');
    if (resumeBtn) {
      resumeBtn.addEventListener('click', () => this._executeCommand(() => ControlAPI.resume(), 'resume'));
    }

    const stopBtn = byId('stop-button');
    if (stopBtn) {
      stopBtn.addEventListener('click', () => this._executeCommand(() => ControlAPI.stop(), 'stop'));
    }

    const snapshotBtn = byId('snapshot-button');
    if (snapshotBtn) {
      snapshotBtn.addEventListener('click', () => this._executeCommand(() => ControlAPI.snapshot(), 'snapshot'));
    }

    // Self-organization toggles
    const selfOrgEnabled = this._elements['self-org-enabled'];
    const selfOrgDryRun = this._elements['self-org-dry-run'];

    if (selfOrgEnabled) {
      selfOrgEnabled.addEventListener('change', () => this._handleSelfOrganization());
    }
    if (selfOrgDryRun) {
      selfOrgDryRun.addEventListener('change', () => this._handleSelfOrganization());
    }

    // Structural undo / auto-approval
    const undoBtn = byId('btn-undo-structural');
    if (undoBtn) {
      undoBtn.addEventListener('click', () => this._handleUndoStructural());
    }

    const autoBtn = byId('btn-auto-approval');
    if (autoBtn) {
      autoBtn.addEventListener('click', () => this._handleAutoApproval());
    }
  }

  /**
   * Handle step command.
   */
  async _handleStep() {
    const ticks = getIntegerValue(byId('step-ticks'), 1);
    await this._executeCommand(() => ControlAPI.step(ticks), 'step');
  }

  /**
   * Handle run ticks command.
   */
  async _handleRunTicks() {
    const ticks = getIntegerValue(byId('loop-size'), 100);
    await this._executeCommand(() => ControlAPI.runTicks(ticks), 'run_ticks');
  }

  /**
   * Handle structural undo.
   */
  async _handleUndoStructural() {
    await this._executeCommand(
      async () => {
        const response = await fetch('/api/structural/undo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        if (!response.ok || data.ok === false) {
          throw new Error(data.error || data.message || `HTTP ${response.status}`);
        }
        return data;
      },
      'undo'
    );
  }

  /**
   * Handle auto-approval toggle.
   */
  async _handleAutoApproval() {
    const btn = byId('btn-auto-approval');
    const currentlyEnabled = btn?.dataset.enabled === 'true';
    const nextEnabled = !currentlyEnabled;
    await this._executeCommand(
      async () => {
        const response = await fetch('/api/structural/auto-approval', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: nextEnabled }),
        });
        const data = await response.json();
        if (!response.ok || data.ok === false) {
          throw new Error(data.error || data.message || `HTTP ${response.status}`);
        }
        return data;
      },
      'auto-approval'
    );
    if (btn) {
      btn.dataset.enabled = String(nextEnabled);
      btn.textContent = nextEnabled ? 'Disable Auto-Approval' : 'Enable Auto-Approval';
    }
  }

  // ========================================================================
  // Command Handlers
  // ========================================================================

  /**
   * Execute a command with debouncing.
   * @param {Function} command - Command function
   * @param {string} actionName - Action name for messages
   */
  async _executeCommand(command, actionName = 'command') {
    if (this.commandInFlight) {
      this._setMessage('⏳ Command already in progress...', 'info');
      return;
    }

    this.commandInFlight = true;
    this._setMessage(`⏳ Executing '${actionName}'...`, 'info');
    this._log(`▶ Executing: ${actionName}`, 'info');

    try {
      const result = await command();
      this._setMessage(`✓ '${actionName}' completed`, 'info');
      this._log(`✅ ${actionName} completed`, 'success');
      await this._refreshState();
      return result;
    } catch (error) {
      this._setMessage(`✗ ${actionName} failed: ${error.message}`, 'error');
      this._log(`❌ ${actionName} failed: ${error.message}`, 'error');
      this.state.setError(error.message);
      throw error;
    } finally {
      this.commandInFlight = false;
    }
  }

  /**
   * Emit a log entry to the shared console log.
   * @param {string} message
   * @param {string} type
   */
  _log(message, type = 'info') {
    // Import is dynamic to avoid a hard dependency cycle; console-log.js
    // is a leaf module and can be imported lazily.
    import('./console-log.js').then(({ consoleLog }) => {
      consoleLog.log(message, type);
    }).catch(() => {});
  }

  /**
   * Handle configure command.
   */
  async _handleConfigure() {
    const loopSize = getIntegerValue(this._elements['loop-size'], 100);
    const delayMs = getNumericValue(this._elements['delay-ms'], 0);
    await this._executeCommand(
      () => ControlAPI.configure({ loop_size: loopSize, delay_ms: delayMs }),
      'configure'
    );
  }

  /**
   * Handle self-organization configuration.
   */
  async _handleSelfOrganization() {
    const enabled = this._elements['self-org-enabled']?.checked || false;
    const dryRun = this._elements['self-org-dry-run']?.checked || false;

    await this._executeCommand(
      () => ControlAPI.configureSelfOrganization({ enabled, dry_run: dryRun }),
      'self-organization'
    );
  }

  // ========================================================================
  // State Management
  // ========================================================================

  /**
   * Refresh state from the server.
   */
  async _refreshState() {
    try {
      const data = await ControlAPI.getState();
      this.state.update(data);
    } catch (error) {
      this.state.setError(error.message);
      this._setMessage(`✗ Failed to refresh: ${error.message}`, 'error');
    }
  }

  /**
   * Set message.
   * @param {string} text - Message text
   * @param {string} kind - Message kind ('info', 'error')
   */
  _setMessage(text, kind = 'info') {
    const msg = this._elements['control-message'];
    if (!msg) return;
    msg.textContent = text;
    msg.dataset.kind = kind;
  }

  // ========================================================================
  // Polling
  // ========================================================================

  /**
   * Start polling for state updates.
   */
  startPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    // Initial load
    this._refreshState();

    // Periodic polling
    this.pollingInterval = setInterval(() => {
      // Only refresh if no command is in flight
      if (!this.commandInFlight) {
        this._refreshState().catch(() => {});
      }
    }, this.pollingRate);
  }

  /**
   * Stop polling.
   */
  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Set polling rate.
   * @param {number} ms - Milliseconds
   */
  setPollingRate(ms) {
    if (ms < 100) ms = 100;
    this.pollingRate = ms;
    if (this.pollingInterval) {
      this.startPolling(); // Restart with new rate
    }
  }

  // ========================================================================
  // Keyboard Shortcuts
  // ========================================================================

  _initKeyboardShortcuts() {
    this._keyboardHandler = (e) => {
      if (!(e.ctrlKey && e.shiftKey)) return;

      switch (e.key) {
        case 'Enter':
          e.preventDefault();
          this._handleStep();
          break;
        case 'R':
          e.preventDefault();
          this._handleRunTicks();
          break;
        case 'S':
          e.preventDefault();
          this._executeCommand(() => ControlAPI.start(), 'start');
          break;
        case 'P':
          e.preventDefault();
          this._executeCommand(() => ControlAPI.pause(), 'pause');
          break;
        case ' ':
          e.preventDefault();
          this._executeCommand(() => ControlAPI.stop(), 'stop');
          break;
        case 'N':
          e.preventDefault();
          this._executeCommand(() => ControlAPI.snapshot(), 'snapshot');
          break;
      }
    };
    document.addEventListener('keydown', this._keyboardHandler);
  }

  // ========================================================================
  // Cleanup
  // ========================================================================

  /**
   * Destroy the control panel instance.
   */
  destroy() {
    this.stopPolling();
    if (this._keyboardHandler) {
      document.removeEventListener('keydown', this._keyboardHandler);
      this._keyboardHandler = null;
    }
  }
}
