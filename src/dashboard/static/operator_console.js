/**
 * Brain-5D Operator Console
 * 
 * Professional operator console for Brain-5D dashboard providing:
 * - Real-time system control (start, pause, stop, step, run_ticks)
 * - Structural plasticity management (proposals, approve, reject, undo)
 * - Snapshot management
 * - Command history and autocomplete
 * - Real-time status updates
 * - Keyboard shortcuts
 * - Robust error handling with user feedback
 * 
 * @version 2.0.0
 * @license MIT
 */

"use strict";

// ============================================================================
// DOM Helpers
// ============================================================================

/**
 * Get element by ID with type safety.
 * @param {string} id - Element ID
 * @returns {HTMLElement | null}
 */
function byId(id) {
  return document.getElementById(id);
}

/**
 * Get element by ID or throw.
 * @param {string} id - Element ID
 * @param {string} context - Context for error message
 * @returns {HTMLElement}
 * @throws {Error} If element not found
 */
function requireElement(id, context = 'console') {
  const el = byId(id);
  if (!el) {
    throw new Error(`Required element "#${id}" not found in ${context}`);
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
  if (el) el.textContent = String(text);
}

/**
 * Set HTML content safely.
 * @param {string} id - Element ID
 * @param {string} html - HTML content
 */
function setHTML(id, html) {
  const el = byId(id);
  if (el) el.innerHTML = html;
}

// ============================================================================
// Utilities
// ============================================================================

/**
 * Format a timestamp.
 * @param {Date} date - Date object
 * @returns {string} Formatted time
 */
function formatTime(date = new Date()) {
  return date.toLocaleTimeString('en-US', { hour12: false });
}

/**
 * Escape HTML to prevent XSS.
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

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

// ============================================================================
// API Client
// ============================================================================

class OperatorAPI {
  /**
   * Fetch JSON from the dashboard API.
   * @param {string} url - API endpoint
   * @param {object} options - Fetch options
   * @returns {Promise<object>} JSON response
   * @throws {Error} On HTTP error or invalid response
   */
  static async fetchJSON(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Cache-Control': 'no-store',
        ...(options.headers || {}),
      },
    });
    
    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error(`Invalid JSON response from ${url}`);
    }
    
    if (!response.ok) {
      const message = data.error || data.message || `HTTP ${response.status}`;
      throw new Error(message);
    }
    
    return data;
  }

  /**
   * Send a control command.
   * @param {string} command - Command name
   * @param {object} params - Command parameters
   * @returns {Promise<object>} Command result
   */
  static async sendCommand(command, params = {}) {
    const body = { command, ...params };
    return this.fetchJSON('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  }

  /**
   * Get system status.
   * @returns {Promise<object>} Status data
   */
  static async getStatus() {
    return this.fetchJSON('/api/status');
  }

  /**
   * Get structural proposals.
   * @returns {Promise<object>} Proposals data
   */
  static async getProposals() {
    return this.fetchJSON('/api/structural/proposals');
  }

  /**
   * Approve a structural proposal.
   * @param {string} proposalId - Proposal ID
   * @returns {Promise<object>} Result
   */
  static async approveProposal(proposalId) {
    return this.fetchJSON('/api/structural/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal_id: proposalId }),
    });
  }

  /**
   * Reject a structural proposal.
   * @param {string} proposalId - Proposal ID
   * @returns {Promise<object>} Result
   */
  static async rejectProposal(proposalId) {
    return this.fetchJSON('/api/structural/reject', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal_id: proposalId }),
    });
  }

  /**
   * Undo the last structural change.
   * @returns {Promise<object>} Result
   */
  static async undoStructural() {
    return this.fetchJSON('/api/structural/undo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
  }

  /**
   * Set auto-approval mode.
   * @param {boolean} enabled - Whether to enable
   * @returns {Promise<object>} Result
   */
  static async setAutoApproval(enabled) {
    return this.fetchJSON('/api/structural/auto-approval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
  }

  /**
   * Run ticks.
   * @param {number} count - Number of ticks
   * @returns {Promise<object>} Result
   */
  static async runTicks(count) {
    return this.sendCommand('run_ticks', { ticks: count });
  }

  /**
   * Single step.
   * @returns {Promise<object>} Result
   */
  static async step() {
    return this.sendCommand('step');
  }

  /**
   * Start the runtime.
   * @returns {Promise<object>} Result
   */
  static async start() {
    return this.sendCommand('start');
  }

  /**
   * Pause the runtime.
   * @returns {Promise<object>} Result
   */
  static async pause() {
    return this.sendCommand('pause');
  }

  /**
   * Resume the runtime.
   * @returns {Promise<object>} Result
   */
  static async resume() {
    return this.sendCommand('resume');
  }

  /**
   * Stop the runtime.
   * @returns {Promise<object>} Result
   */
  static async stop() {
    return this.sendCommand('stop');
  }

  /**
   * Request a snapshot.
   * @returns {Promise<object>} Result
   */
  static async snapshot() {
    return this.sendCommand('snapshot');
  }
}

// ============================================================================
// Console Logger
// ============================================================================

class ConsoleLogger {
  constructor(containerId) {
    this.container = byId(containerId);
    this.entries = [];
    this.maxEntries = 1000;
  }

  /**
   * Log a message to the console.
   * @param {string} message - Message to log
   * @param {string} type - Log type ('info', 'success', 'error', 'warning')
   */
  log(message, type = 'info') {
    const entry = {
      timestamp: new Date(),
      message: String(message),
      type: type,
    };
    
    this.entries.push(entry);
    if (this.entries.length > this.maxEntries) {
      this.entries.shift();
    }
    
    this.render(entry);
  }

  /**
   * Render a single log entry.
   * @param {object} entry - Log entry
   */
  render(entry) {
    if (!this.container) return;
    
    const time = formatTime(entry.timestamp);
    const classes = `log-entry log-${entry.type}`;
    
    const div = document.createElement('div');
    div.className = classes;
    div.innerHTML = `<span class="log-time">[${time}]</span> ${escapeHtml(entry.message)}`;
    
    this.container.appendChild(div);
    
    // Auto-scroll
    this.container.scrollTop = this.container.scrollHeight;
    
    // Limit DOM entries
    while (this.container.children.length > this.maxEntries) {
      this.container.removeChild(this.container.firstChild);
    }
  }

  /**
   * Clear the console.
   */
  clear() {
    if (this.container) {
      this.container.innerHTML = '';
    }
    this.entries = [];
  }

  /**
   * Get all log entries.
   * @returns {Array} Log entries
   */
  getEntries() {
    return [...this.entries];
  }
}

// ============================================================================
// Operator Console
// ============================================================================

class OperatorConsole {
  constructor() {
    this.logger = null;
    this.pollingInterval = null;
    this.pollingRate = 1000;
    this.commandInFlight = false;
    this.status = null;
    this.proposals = [];
    
    // Bind methods
    this.handleCommand = this.handleCommand.bind(this);
    this.refreshStatus = this.refreshStatus.bind(this);
    this.renderProposals = this.renderProposals.bind(this);
    
    this.init();
  }

  /**
   * Initialize the console.
   */
  init() {
    // Initialize logger
    this.logger = new ConsoleLogger('console-output');
    this.logger.log('🧠 Brain-5D Operator Console initialized', 'info');
    this.logger.log(`📡 API endpoint: /api/control`, 'info');
    
    // Bind event listeners
    this.bindEvents();
    this.bindKeyboardShortcuts();
    
    // Initial load
    this.refreshStatus();
    this.loadProposals();
    
    // Start polling
    this.startPolling();
  }

  /**
   * Bind DOM event listeners.
   */
  bindEvents() {
    // Control buttons
    const controls = [
      { id: 'b5d-step', action: 'step' },
      { id: 'b5d-start', action: 'start' },
      { id: 'b5d-pause', action: 'pause' },
      { id: 'b5d-resume', action: 'resume' },
      { id: 'b5d-stop', action: 'stop' },
      { id: 'b5d-snapshot', action: 'snapshot' },
    ];
    
    for (const { id, action } of controls) {
      const el = byId(id);
      if (el) {
        el.addEventListener('click', () => this.handleCommand(action));
      }
    }
    
    // Run ticks
    const runBtn = byId('b5d-run-ticks');
    if (runBtn) {
      runBtn.addEventListener('click', () => {
        const input = byId('b5d-tick-count');
        const count = parseInt(input?.value || '1', 10);
        if (count > 0) {
          this.handleCommand('run_ticks', { ticks: count });
        }
      });
    }
    
    // Undo structural change
    const undoBtn = byId('b5d-undo');
    if (undoBtn) {
      undoBtn.addEventListener('click', () => this.handleUndo());
    }
    
    // Clear console
    const clearBtn = byId('b5d-clear-console');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.logger.clear());
    }
  }

  /**
   * Bind keyboard shortcuts.
   */
  bindKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+Enter = Step
      if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        this.handleCommand('step');
        return;
      }
      
      // Ctrl+Shift+S = Start
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        this.handleCommand('start');
        return;
      }
      
      // Ctrl+Shift+P = Pause
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        this.handleCommand('pause');
        return;
      }
      
      // Ctrl+Shift+R = Resume
      if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        this.handleCommand('resume');
        return;
      }
      
      // Ctrl+Shift+Space = Stop
      if (e.ctrlKey && e.shiftKey && e.key === ' ') {
        e.preventDefault();
        this.handleCommand('stop');
        return;
      }
      
      // Ctrl+Shift+N = Snapshot
      if (e.ctrlKey && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        this.handleCommand('snapshot');
        return;
      }
      
      // Ctrl+L = Clear console (if focus is on console)
      if (e.ctrlKey && e.key === 'l' && document.activeElement?.id === 'console-output') {
        e.preventDefault();
        this.logger.clear();
        return;
      }
    });
  }

  /**
   * Handle a command.
   * @param {string} action - Command action
   * @param {object} params - Command parameters
   */
  async handleCommand(action, params = {}) {
    if (this.commandInFlight) {
      this.logger.log(`⏳ Command '${action}' already in progress...`, 'warning');
      return;
    }
    
    this.commandInFlight = true;
    this.logger.log(`▶ Executing: ${action}${params.ticks ? ` (${params.ticks} ticks)` : ''}`, 'info');
    
    try {
      let result;
      switch (action) {
        case 'start':
          result = await OperatorAPI.start();
          break;
        case 'pause':
          result = await OperatorAPI.pause();
          break;
        case 'resume':
          result = await OperatorAPI.resume();
          break;
        case 'stop':
          result = await OperatorAPI.stop();
          break;
        case 'step':
          result = await OperatorAPI.step();
          break;
        case 'run_ticks':
          result = await OperatorAPI.runTicks(params.ticks || 1);
          break;
        case 'snapshot':
          result = await OperatorAPI.snapshot();
          break;
        default:
          throw new Error(`Unknown command: ${action}`);
      }
      
      this.logger.log(`✅ ${action} completed successfully`, 'success');
      await this.refreshStatus();
      await this.loadProposals();
      
    } catch (error) {
      this.logger.log(`❌ ${action} failed: ${error.message}`, 'error');
    } finally {
      this.commandInFlight = false;
    }
  }

  /**
   * Handle undo structural change.
   */
  async handleUndo() {
    if (this.commandInFlight) {
      this.logger.log('⏳ Command in progress...', 'warning');
      return;
    }
    
    this.commandInFlight = true;
    this.logger.log('↩ Undoing last structural change...', 'info');
    
    try {
      const result = await OperatorAPI.undoStructural();
      if (result.ok) {
        this.logger.log(`✅ ${result.message || 'Change undone'}`, 'success');
        await this.refreshStatus();
        await this.loadProposals();
      } else {
        this.logger.log(`❌ Undo failed: ${result.message || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      this.logger.log(`❌ Undo failed: ${error.message}`, 'error');
    } finally {
      this.commandInFlight = false;
    }
  }

  /**
   * Refresh system status.
   */
  async refreshStatus() {
    try {
      const data = await OperatorAPI.getStatus();
      this.status = data;
      this.renderStatus(data);
    } catch (error) {
      this.logger.log(`⚠️ Failed to refresh status: ${error.message}`, 'warning');
    }
  }

  /**
   * Load structural proposals.
   */
  async loadProposals() {
    try {
      const data = await OperatorAPI.getProposals();
      this.proposals = data.proposals || [];
      this.renderProposals(this.proposals);
    } catch (error) {
      this.logger.log(`⚠️ Failed to load proposals: ${error.message}`, 'warning');
    }
  }

  /**
   * Render system status.
   * @param {object} data - Status data
   */
  renderStatus(data) {
    // Update status badge
    const badge = byId('b5d-state-badge');
    if (badge) {
      const state = data.state || 'idle';
      badge.textContent = state;
      badge.className = `status-badge status-${state}`;
    }
    
    // Update tick count
    const tickEl = byId('b5d-tick-display');
    if (tickEl) {
      tickEl.textContent = String(data.tick || 0);
    }
    
    // Update metrics
    const metrics = byId('b5d-metrics');
    if (metrics && data.system) {
      const s = data.system;
      metrics.innerHTML = `
        <span>🧠 ${(s.neurons || 0).toLocaleString()}</span>
        <span>🔗 ${(s.synapses || 0).toLocaleString()}</span>
        <span>⚡ ${(s.spikes_total || 0).toLocaleString()}</span>
      `;
    }
  }

  /**
   * Render structural proposals.
   * @param {Array} proposals - Proposals list
   */
  renderProposals(proposals) {
    const container = byId('b5d-proposals');
    if (!container) return;
    
    if (!proposals || proposals.length === 0) {
      container.innerHTML = '<div class="proposal-empty">No pending proposals</div>';
      return;
    }
    
    let html = '';
    for (const p of proposals) {
      const confidence = (p.confidence || 0) * 100;
      html += `
        <div class="proposal-item" data-id="${escapeHtml(p.proposal_id)}">
          <span class="proposal-kind">${escapeHtml(p.kind || 'unknown')}</span>
          <span class="proposal-desc">
            Neuron ${p.neuron_id || '?'} → ${p.target_id || '?'}
          </span>
          <span class="proposal-conf" style="--conf: ${confidence}%">
            ${confidence.toFixed(0)}%
          </span>
          <span class="proposal-reason">${escapeHtml(p.reason || '')}</span>
          <div class="proposal-actions">
            <button class="btn-approve" data-id="${escapeHtml(p.proposal_id)}">✓ Approve</button>
            <button class="btn-reject" data-id="${escapeHtml(p.proposal_id)}">✗ Reject</button>
          </div>
        </div>
      `;
    }
    
    container.innerHTML = html;
    
    // Bind approve/reject events
    container.querySelectorAll('.btn-approve').forEach(btn => {
      btn.addEventListener('click', () => this.handleApprove(btn.dataset.id));
    });
    container.querySelectorAll('.btn-reject').forEach(btn => {
      btn.addEventListener('click', () => this.handleReject(btn.dataset.id));
    });
  }

  /**
   * Handle approve proposal.
   * @param {string} proposalId - Proposal ID
   */
  async handleApprove(proposalId) {
    if (this.commandInFlight) {
      this.logger.log('⏳ Command in progress...', 'warning');
      return;
    }
    
    this.commandInFlight = true;
    this.logger.log(`✓ Approving proposal ${proposalId}...`, 'info');
    
    try {
      const result = await OperatorAPI.approveProposal(proposalId);
      if (result.ok) {
        this.logger.log(`✅ Proposal ${proposalId} approved and applied`, 'success');
        await this.loadProposals();
        await this.refreshStatus();
      } else {
        this.logger.log(`❌ Failed to approve: ${result.message || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      this.logger.log(`❌ Failed to approve: ${error.message}`, 'error');
    } finally {
      this.commandInFlight = false;
    }
  }

  /**
   * Handle reject proposal.
   * @param {string} proposalId - Proposal ID
   */
  async handleReject(proposalId) {
    if (this.commandInFlight) {
      this.logger.log('⏳ Command in progress...', 'warning');
      return;
    }
    
    this.commandInFlight = true;
    this.logger.log(`✗ Rejecting proposal ${proposalId}...`, 'info');
    
    try {
      const result = await OperatorAPI.rejectProposal(proposalId);
      if (result.ok) {
        this.logger.log(`✅ Proposal ${proposalId} rejected`, 'success');
        await this.loadProposals();
        await this.refreshStatus();
      } else {
        this.logger.log(`❌ Failed to reject: ${result.message || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      this.logger.log(`❌ Failed to reject: ${error.message}`, 'error');
    } finally {
      this.commandInFlight = false;
    }
  }

  /**
   * Start polling for status updates.
   */
  startPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
    
    this.pollingInterval = setInterval(() => {
      if (!this.commandInFlight) {
        this.refreshStatus().catch(() => {});
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
      this.startPolling();
    }
  }

  /**
   * Destroy the console instance.
   */
  destroy() {
    this.stopPolling();
    this.logger.log('🛑 Operator Console shutting down', 'info');
  }
}

// ============================================================================
// Initialization
// ============================================================================

let consoleInstance = null;

/**
 * Initialize the operator console.
 */
function initOperatorConsole() {
  if (consoleInstance) {
    consoleInstance.destroy();
  }
  consoleInstance = new OperatorConsole();
  return consoleInstance;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initOperatorConsole);
} else {
  initOperatorConsole();
}

// ============================================================================
// Module Exports (for bundlers)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    OperatorAPI,
    OperatorConsole,
    ConsoleLogger,
    initOperatorConsole,
  };
}