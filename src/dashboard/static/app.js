/**
 * Brain-5D Operator Dashboard – Main Application
 * 
 * This module initializes all dashboard components and handles tab switching.
 * It integrates the Control Panel, Operator Console, and Documentation Browser
 * into a single cohesive application with lazy loading for performance.
 * 
 * Features:
 * - Tab-based navigation (Dashboard, Control, Console, Docs)
 * - Real-time system monitoring with auto-refresh
 * - Heatmap visualization
 * - Runtime control (step, run, pause, stop, snapshot)
 * - Structural plasticity management (proposals, approve, reject, undo)
 * - Documentation browsing with multi-format support
 * - Keyboard shortcuts for all major actions
 * 
 * @version 2.0.0
 * @license MIT
 */

"use strict";

// ================================================================
// IMPORTS
// ================================================================

// Import component modules (if available as ES modules)
// These will be lazy-initialized when their tab is first activated.
// If the modules are not available, fallback to inline implementations.
let ControlPanel, OperatorConsole;

try {
  // Dynamic import for code splitting – loads only when needed
  // The actual import paths should match your project structure
  const controlModule = await import('./control-panel.js');
  ControlPanel = controlModule.ControlPanel || controlModule.default;
} catch {
  console.warn('ControlPanel module not found, using fallback');
  ControlPanel = null;
}

try {
  const consoleModule = await import('./operator_console.js');
  OperatorConsole = consoleModule.OperatorConsole || consoleModule.default;
} catch {
  console.warn('OperatorConsole module not found, using fallback');
  OperatorConsole = null;
}

// ================================================================
// DOM HELPERS
// ================================================================

const $ = (id) => document.getElementById(id);
const $$ = (sel) => document.querySelectorAll(sel);

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = String(value);
}

function setHTML(id, html) {
  const el = $(id);
  if (el) el.innerHTML = html;
}

function setClass(id, className) {
  const el = $(id);
  if (el) el.className = className;
}

// ================================================================
// UTILITIES
// ================================================================

function formatBytes(value) {
  const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
  let size = Number(value || 0);
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx++;
  }
  return `${size.toFixed(idx === 0 ? 0 : 2)} ${units[idx]}`;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function formatFloat(value, decimals = 3) {
  return Number(value || 0).toFixed(decimals);
}

function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Heatmap color mapping based on value range.
 */
function heatmapColor(value, min, max) {
  const scale = max > min ? (value - min) / (max - min) : 0;
  const t = Math.max(0, Math.min(1, scale));
  const hue = 210 - (195 * t);
  const light = 16 + (46 * t);
  return `hsl(${hue}, 88%, ${light}%)`;
}

// ================================================================
// TAB SWITCHING
// ================================================================

function setupTabs() {
  const buttons = $$('.tab-btn');
  const contents = {
    dashboard: document.getElementById('tab-dashboard'),
    control: document.getElementById('tab-control'),
    console: document.getElementById('tab-console'),
    docs: document.getElementById('tab-docs'),
  };

  // Track initialization state
  const initialized = {
    control: false,
    console: false,
    docs: false,
  };

  // Component instances
  const instances = {
    control: null,
    console: null,
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update button states
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show corresponding tab
      const tabName = btn.dataset.tab;
      Object.keys(contents).forEach(key => {
        const el = contents[key];
        if (el) {
          el.classList.toggle('active', key === tabName);
        }
      });

      // Lazy initialize components when their tab becomes visible
      if (tabName === 'control' && !initialized.control) {
        instances.control = initControlPanel();
        initialized.control = true;
      }
      if (tabName === 'console' && !initialized.console) {
        instances.console = initOperatorConsole();
        initialized.console = true;
      }
      if (tabName === 'docs' && !initialized.docs) {
        initDocumentationBrowser();
        initialized.docs = true;
      }
    });
  });

  // Activate the first tab by default (Dashboard)
  const firstTab = document.querySelector('.tab-btn');
  if (firstTab) {
    firstTab.click();
  }

  return instances;
}

// ================================================================
// DASHBOARD – Status & Heatmap (Original functionality)
// ================================================================

let heatmapKind = 'activity';
let refreshInterval = null;
let heatmapInterval = null;

/**
 * Refresh system status from /api/status
 */
async function refreshStatus() {
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    const system = data.system || {};
    const storage = data.storage || {};
    const learning = data.learning || {};
    const selfOrg = data.self_organization || {};
    const homeostasis = data.homeostasis || {};

    // System metrics
    setText('tick', formatNumber(system.tick));
    setText('neurons', formatNumber(system.neurons));
    setText('synapses', formatNumber(system.synapses));
    setText('spikes', formatNumber(system.spikes_total));
    setText('core-ms', formatFloat(system.core_step_ms, 3));
    setText('energy', formatFloat(system.mean_energy, 3));

    // Storage metrics
    setText('deltas', formatNumber(storage.deltas_written));
    setText('bytes', formatBytes(storage.bytes_written));
    setText('write-ms', `${formatFloat(storage.write_latency_ms, 3)} ms`);
    setText('commit-ms', `${formatFloat(storage.commit_latency_ms, 3)} ms`);
    setText('journal-size', formatBytes(storage.journal_size_bytes));
    setText('drops', formatNumber(storage.dropped_batches));

    // Queue progress
    const depth = storage.queue_depth || 0;
    const capacity = storage.queue_capacity || 1;
    setText('queue-badge', `${depth} / ${capacity}`);
    const fill = $('queue-fill');
    if (fill) {
      const percent = Math.min(100, (depth / capacity) * 100);
      fill.style.width = `${percent}%`;
    }

    // Learning metrics
    setText('stdp', formatNumber(learning.stdp_updates));
    setText('reward-updates', formatNumber(learning.reward_updates));
    setText('rewards', `${formatNumber(learning.rewards_applied)} / ${formatNumber(learning.rewards_received)}`);
    setText('pending', formatNumber(learning.pending_rewards));
    setText('learning-ms', `${formatFloat(learning.update_ms, 3)} ms`);

    // Homeostasis
    setText('homeostasis-state', homeostasis.enabled ? 'aktiv' : 'aus');
    setText('target-rate', `${formatFloat(homeostasis.target_rate_hz, 3)} Hz`);
    setText('mean-rate', `${formatFloat(homeostasis.mean_rate_hz || homeostasis.actual_rate_hz, 3)} Hz`);
    setText('rate-error', `${formatFloat(homeostasis.mean_rate_error_hz || homeostasis.rate_error_hz, 3)} Hz`);
    setText('threshold-adaptation', formatFloat(homeostasis.mean_threshold_adaptation, 4));
    setText('energy-error', formatFloat(homeostasis.mean_energy_error, 4));
    setText('active-neurons', formatNumber(homeostasis.active_neurons));

    // Self-organization
    setText('neurons-created', formatNumber(selfOrg.neurons_created));
    setText('neurons-removed', formatNumber(selfOrg.neurons_removed));
    setText('synapses-created', formatNumber(selfOrg.synapses_created));
    setText('synapses-pruned', formatNumber(selfOrg.synapses_pruned));

    // Status badge
    const statusEl = $('system-status');
    if (statusEl) {
      statusEl.textContent = `${data.status || 'idle'} · ${data.version || 'unknown'}`;
      statusEl.className = storage.worker_failed ? 'status-pill error' : 'status-pill online';
    }
  } catch (error) {
    const statusEl = $('system-status');
    if (statusEl) {
      statusEl.textContent = '⚠️ offline';
      statusEl.className = 'status-pill error';
    }
  }
}

/**
 * Refresh heatmap from /api/heatmap
 */
async function refreshHeatmap() {
  const canvas = $('heatmap');
  if (!canvas) return;

  try {
    const response = await fetch(
      `/api/heatmap?kind=${encodeURIComponent(heatmapKind)}`,
      { cache: 'no-store' }
    );
    if (!response.ok) {
      const data = await response.json();
      setText('heatmap-meta', data.error || `Heatmap HTTP ${response.status}`);
      return;
    }
    drawHeatmap(await response.json());
  } catch (error) {
    setText('heatmap-meta', '⚠️ Heatmap nicht erreichbar.');
  }
}

/**
 * Draw heatmap on canvas
 */
function drawHeatmap(payload) {
  const canvas = $('heatmap');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const rows = payload.values || [];
  if (!rows.length || !rows[0]?.length) {
    setText('heatmap-meta', 'Keine Heatmap-Daten verfügbar.');
    return;
  }

  const flat = rows.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const width = rows[0].length;
  const height = rows.length;
  const cellW = canvas.width / width;
  const cellH = canvas.height / height;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      ctx.fillStyle = heatmapColor(rows[y][x], min, max);
      ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
    }
  }

  setText(
    'heatmap-meta',
    `${payload.kind || heatmapKind} · Tick ${payload.tick || 0} · ${payload.samples || 0} Samples · ${formatFloat(min, 4)}…${formatFloat(max, 4)}`
  );
}

/**
 * Initialize dashboard refresh cycles
 */
function initDashboard() {
  // Initial loads
  refreshStatus();
  refreshHeatmap();

  // Set up intervals
  if (refreshInterval) clearInterval(refreshInterval);
  if (heatmapInterval) clearInterval(heatmapInterval);

  refreshInterval = setInterval(refreshStatus, 1000);
  heatmapInterval = setInterval(refreshHeatmap, 5000);

  // Heatmap kind buttons
  $$('button[data-kind]').forEach(button => {
    button.addEventListener('click', () => {
      heatmapKind = button.dataset.kind;
      $$('button[data-kind]').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      refreshHeatmap();
    });
  });
}

// ================================================================
// CONTROL PANEL INITIALIZATION
// ================================================================

function initControlPanel() {
  console.log('🎮 Control Panel initializing...');

  // If ControlPanel class is available, instantiate it
  if (ControlPanel) {
    try {
      const instance = new ControlPanel();
      console.log('✅ Control Panel initialized (module)');
      return instance;
    } catch (e) {
      console.warn('ControlPanel instantiation failed, using fallback:', e);
    }
  }

  // Fallback: use the control-panel.js logic directly
  // This assumes the control-panel.js script is loaded (via script tag or inline)
  if (typeof initControlPanelFallback === 'function') {
    return initControlPanelFallback();
  }

  // Minimal fallback: bind basic events
  bindControlEvents();
  return null;
}

/**
 * Minimal fallback for control panel events
 */
function bindControlEvents() {
  // Step
  const stepBtn = $('step-button');
  if (stepBtn) {
    stepBtn.addEventListener('click', () => {
      const ticks = parseInt($('step-ticks')?.value || '1', 10);
      sendControlCommand('step', { ticks });
    });
  }

  // Run
  const runBtn = $('run-button');
  if (runBtn) {
    runBtn.addEventListener('click', () => {
      const loopSize = parseInt($('loop-size')?.value || '100', 10);
      sendControlCommand('run', { loop_size: loopSize });
    });
  }

  // Pause
  const pauseBtn = $('pause-button');
  if (pauseBtn) {
    pauseBtn.addEventListener('click', () => sendControlCommand('pause'));
  }

  // Stop
  const stopBtn = $('stop-button');
  if (stopBtn) {
    stopBtn.addEventListener('click', () => sendControlCommand('stop'));
  }

  // Snapshot
  const snapshotBtn = $('snapshot-button');
  if (snapshotBtn) {
    snapshotBtn.addEventListener('click', () => sendControlCommand('snapshot'));
  }

  // Configure
  const applyBtn = $('apply-runtime-config');
  if (applyBtn) {
    applyBtn.addEventListener('click', () => {
      const loopSize = parseInt($('loop-size')?.value || '100', 10);
      const delayMs = parseFloat($('delay-ms')?.value || '0');
      sendControlCommand('configure', { loop_size: loopSize, delay_ms: delayMs });
    });
  }

  // Self-organization toggles
  const selfOrgEnabled = $('self-org-enabled');
  const selfOrgDryRun = $('self-org-dry-run');
  if (selfOrgEnabled) {
    selfOrgEnabled.addEventListener('change', updateSelfOrganization);
  }
  if (selfOrgDryRun) {
    selfOrgDryRun.addEventListener('change', updateSelfOrganization);
  }

  // Undo structural
  const undoBtn = $('btn-undo-structural');
  if (undoBtn) {
    undoBtn.addEventListener('click', () => {
      sendStructuralCommand('undo');
    });
  }

  // Auto-approval
  const autoApprovalBtn = $('btn-auto-approval');
  if (autoApprovalBtn) {
    autoApprovalBtn.addEventListener('click', () => {
      const enabled = autoApprovalBtn.dataset.enabled === 'true';
      sendStructuralCommand('auto-approval', { enabled: !enabled });
    });
  }

  console.log('✅ Control Panel initialized (fallback)');
}

/**
 * Send control command via API
 */
async function sendControlCommand(action, params = {}) {
  const msgEl = $('control-message');
  if (msgEl) {
    msgEl.textContent = `⏳ ${action}...`;
    msgEl.dataset.kind = 'info';
  }

  try {
    const response = await fetch('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...params }),
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }
    if (msgEl) {
      msgEl.textContent = `✅ ${action} completed`;
      msgEl.dataset.kind = 'success';
    }
    // Refresh status after command
    refreshStatus();
  } catch (error) {
    if (msgEl) {
      msgEl.textContent = `❌ ${action} failed: ${error.message}`;
      msgEl.dataset.kind = 'error';
    }
  }
}

/**
 * Send structural command via API
 */
async function sendStructuralCommand(action, params = {}) {
  const msgEl = $('control-message');
  if (msgEl) {
    msgEl.textContent = `⏳ Structural ${action}...`;
    msgEl.dataset.kind = 'info';
  }

  try {
    const response = await fetch(`/api/structural/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.message || data.error || `HTTP ${response.status}`);
    }
    if (msgEl) {
      msgEl.textContent = `✅ Structural ${action}: ${data.message || 'completed'}`;
      msgEl.dataset.kind = 'success';
    }
    refreshStatus();
  } catch (error) {
    if (msgEl) {
      msgEl.textContent = `❌ Structural ${action} failed: ${error.message}`;
      msgEl.dataset.kind = 'error';
    }
  }
}

/**
 * Update self-organization configuration
 */
function updateSelfOrganization() {
  const enabled = $('self-org-enabled')?.checked || false;
  const dryRun = $('self-org-dry-run')?.checked || false;
  sendControlCommand('self_organization', { enabled, dry_run: dryRun });
}

// ================================================================
// OPERATOR CONSOLE INITIALIZATION
// ================================================================

function initOperatorConsole() {
  console.log('📟 Operator Console initializing...');

  // If OperatorConsole class is available, instantiate it
  if (OperatorConsole) {
    try {
      const instance = new OperatorConsole();
      console.log('✅ Operator Console initialized (module)');
      return instance;
    } catch (e) {
      console.warn('OperatorConsole instantiation failed, using fallback:', e);
    }
  }

  // Fallback: bind console events
  bindConsoleEvents();
  return null;
}

/**
 * Minimal fallback for operator console events
 */
function bindConsoleEvents() {
  // Step
  const stepBtn = $('b5d-step');
  if (stepBtn) {
    stepBtn.addEventListener('click', () => {
      sendConsoleCommand('step');
    });
  }

  // Run N Ticks
  const runBtn = $('b5d-run-ticks');
  if (runBtn) {
    runBtn.addEventListener('click', () => {
      const count = parseInt($('b5d-tick-count')?.value || '100', 10);
      sendConsoleCommand('run_ticks', { ticks: count });
    });
  }

  // Start
  const startBtn = $('b5d-start');
  if (startBtn) {
    startBtn.addEventListener('click', () => sendConsoleCommand('start'));
  }

  // Pause
  const pauseBtn = $('b5d-pause');
  if (pauseBtn) {
    pauseBtn.addEventListener('click', () => sendConsoleCommand('pause'));
  }

  // Resume
  const resumeBtn = $('b5d-resume');
  if (resumeBtn) {
    resumeBtn.addEventListener('click', () => sendConsoleCommand('resume'));
  }

  // Stop
  const stopBtn = $('b5d-stop');
  if (stopBtn) {
    stopBtn.addEventListener('click', () => sendConsoleCommand('stop'));
  }

  // Snapshot
  const snapshotBtn = $('b5d-snapshot');
  if (snapshotBtn) {
    snapshotBtn.addEventListener('click', () => sendConsoleCommand('snapshot'));
  }

  // Undo
  const undoBtn = $('b5d-undo');
  if (undoBtn) {
    undoBtn.addEventListener('click', () => sendConsoleCommand('undo'));
  }

  // Clear console
  const clearBtn = $('b5d-clear-console');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const output = $('console-output');
      if (output) {
        output.innerHTML = `<div class="log-entry log-info">
          <span class="log-time">[${new Date().toLocaleTimeString()}]</span> 🧹 Console cleared
        </div>`;
      }
    });
  }

  // Keyboard shortcuts for console
  document.addEventListener('keydown', (e) => {
    // Ctrl+Enter = Step
    if (e.ctrlKey && e.key === 'Enter' && document.activeElement?.id !== 'b5d-tick-count') {
      e.preventDefault();
      sendConsoleCommand('step');
      return;
    }
    // Ctrl+Shift+S = Start
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
      e.preventDefault();
      sendConsoleCommand('start');
      return;
    }
    // Ctrl+Shift+P = Pause
    if (e.ctrlKey && e.shiftKey && e.key === 'P') {
      e.preventDefault();
      sendConsoleCommand('pause');
      return;
    }
    // Ctrl+Shift+Space = Stop
    if (e.ctrlKey && e.shiftKey && e.key === ' ') {
      e.preventDefault();
      sendConsoleCommand('stop');
      return;
    }
    // Ctrl+Shift+N = Snapshot
    if (e.ctrlKey && e.shiftKey && e.key === 'N') {
      e.preventDefault();
      sendConsoleCommand('snapshot');
      return;
    }
  });

  console.log('✅ Operator Console initialized (fallback)');
}

/**
 * Send console command via API with logging
 */
async function sendConsoleCommand(action, params = {}) {
  const output = $('console-output');
  const time = new Date().toLocaleTimeString();

  // Log command to console
  if (output) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry log-info';
    logEntry.innerHTML = `<span class="log-time">[${time}]</span> ▶ ${action}${params.ticks ? ` (${params.ticks} ticks)` : ''}`;
    output.appendChild(logEntry);
    output.scrollTop = output.scrollHeight;
  }

  try {
    const response = await fetch('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: action, ...params }),
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    // Log success
    if (output) {
      const logEntry = document.createElement('div');
      logEntry.className = 'log-entry log-success';
      logEntry.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ✅ ${action} completed`;
      output.appendChild(logEntry);
      output.scrollTop = output.scrollHeight;
    }

    refreshStatus();
    refreshConsoleStatus();

  } catch (error) {
    // Log error
    if (output) {
      const logEntry = document.createElement('div');
      logEntry.className = 'log-entry log-error';
      logEntry.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ❌ ${action} failed: ${error.message}`;
      output.appendChild(logEntry);
      output.scrollTop = output.scrollHeight;
    }
  }
}

/**
 * Refresh console status display
 */
async function refreshConsoleStatus() {
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    if (!response.ok) return;
    const data = await response.json();

    // Update console status badge
    const badge = $('b5d-state-badge');
    if (badge) {
      const state = data.status || 'idle';
      badge.textContent = state;
      badge.className = `status-badge status-${state}`;
    }

    // Update tick display
    const tickEl = $('b5d-tick-display');
    if (tickEl) {
      tickEl.textContent = String(data.system?.tick || 0);
    }

    // Update metrics
    const system = data.system || {};
    setText('metric-neurons', formatNumber(system.neurons));
    setText('metric-synapses', formatNumber(system.synapses));
    setText('metric-spikes', formatNumber(system.spikes_total));
    setText('metric-queue', formatNumber(system.queue_depth || 0));

    // Load proposals
    loadProposals();
  } catch {
    // Silently fail
  }
}

/**
 * Load structural proposals
 */
async function loadProposals() {
  try {
    const response = await fetch('/api/structural/proposals', { cache: 'no-store' });
    if (!response.ok) return;
    const data = await response.json();
    const proposals = data.proposals || [];

    // Update badge count
    const countEl = $('proposals-count');
    if (countEl) {
      countEl.textContent = `${proposals.length} pending`;
      countEl.className = `badge${proposals.length > 0 ? ' has-proposals' : ''}`;
    }

    // Render proposals
    const container = $('b5d-proposals');
    if (!container) return;

    if (proposals.length === 0) {
      container.innerHTML = '<div class="proposal-empty">No pending proposals</div>';
      return;
    }

    container.innerHTML = proposals.map(p => `
      <div class="proposal-item" data-id="${escapeHtml(p.proposal_id)}">
        <span class="proposal-kind">${escapeHtml(p.kind || 'unknown')}</span>
        <span class="proposal-desc">Neuron ${p.neuron_id || '?'} → ${p.target_id || '?'}</span>
        <span class="proposal-conf" data-level="${(p.confidence || 0) > 0.7 ? 'high' : (p.confidence || 0) > 0.4 ? 'medium' : 'low'}">
          ${((p.confidence || 0) * 100).toFixed(0)}%
        </span>
        <span class="proposal-reason">${escapeHtml(p.reason || '')}</span>
        <div class="proposal-actions">
          <button class="btn-approve" data-id="${escapeHtml(p.proposal_id)}">✓ Approve</button>
          <button class="btn-reject" data-id="${escapeHtml(p.proposal_id)}">✗ Reject</button>
        </div>
      </div>
    `).join('');

    // Bind approve/reject events
    container.querySelectorAll('.btn-approve').forEach(btn => {
      btn.addEventListener('click', () => handleProposal(btn.dataset.id, 'approve'));
    });
    container.querySelectorAll('.btn-reject').forEach(btn => {
      btn.addEventListener('click', () => handleProposal(btn.dataset.id, 'reject'));
    });

  } catch (e) {
    // Silently fail
  }
}

/**
 * Handle proposal approval/rejection
 */
async function handleProposal(proposalId, action) {
  const output = $('console-output');
  const time = new Date().toLocaleTimeString();

  if (output) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry log-info';
    logEntry.innerHTML = `<span class="log-time">[${time}]</span> ${action === 'approve' ? '✓' : '✗'} ${action}ing proposal ${proposalId}...`;
    output.appendChild(logEntry);
    output.scrollTop = output.scrollHeight;
  }

  try {
    const response = await fetch(`/api/structural/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal_id: proposalId }),
    });
    const data = await response.json();
    if (!response.ok || data.ok === false) {
      throw new Error(data.message || data.error || `HTTP ${response.status}`);
    }

    if (output) {
      const logEntry = document.createElement('div');
      logEntry.className = 'log-entry log-success';
      logEntry.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ✅ Proposal ${proposalId} ${action}ed`;
      output.appendChild(logEntry);
      output.scrollTop = output.scrollHeight;
    }

    refreshStatus();
    loadProposals();

  } catch (error) {
    if (output) {
      const logEntry = document.createElement('div');
      logEntry.className = 'log-entry log-error';
      logEntry.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ❌ ${action} failed: ${error.message}`;
      output.appendChild(logEntry);
      output.scrollTop = output.scrollHeight;
    }
  }
}

// ================================================================
// DOCUMENTATION BROWSER
// ================================================================

let docsTreeLoaded = false;

function initDocumentationBrowser() {
  console.log('📄 Documentation Browser initializing...');
  if (!docsTreeLoaded) {
    loadDocsTree();
    setupDocSearch();
    docsTreeLoaded = true;
  }
}

async function loadDocsTree() {
  try {
    const res = await fetch('/api/docs/tree');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const tree = await res.json();
    renderDocTree(tree);
    updateDocStats();
  } catch (e) {
    const treeEl = $('doc-tree');
    if (treeEl) {
      treeEl.innerHTML = `<span style="color:#f06070;">⚠️ ${escapeHtml(e.message)}</span>`;
    }
  }
}

function renderDocTree(node, container = $('doc-tree'), depth = 0) {
  if (!container) return;

  const ul = document.createElement('ul');
  ul.style.paddingLeft = depth * 16 + 'px';

  if (node.type === 'directory') {
    const li = document.createElement('li');
    li.className = 'directory';
    const toggle = document.createElement('span');
    toggle.className = 'toggle';
    toggle.textContent = '📁';
    toggle.style.cursor = 'pointer';
    toggle.onclick = () => {
      const childUl = li.querySelector('ul');
      if (childUl) {
        childUl.style.display = childUl.style.display === 'none' ? '' : 'none';
      }
    };

    const nameSpan = document.createElement('span');
    nameSpan.textContent = ' ' + node.name;
    nameSpan.style.cursor = 'pointer';

    li.appendChild(toggle);
    li.appendChild(nameSpan);
    li.appendChild(ul);
    container.appendChild(li);

    if (node.children) {
      node.children.forEach(child => renderDocTree(child, ul, depth + 1));
    }
  } else if (node.type === 'file') {
    const li = document.createElement('li');
    li.className = 'file';
    li.dataset.path = node.path;

    const nameSpan = document.createElement('span');
    nameSpan.textContent = '📄 ' + node.name;
    nameSpan.style.cursor = 'pointer';
    nameSpan.onclick = () => openDocument(node.path);

    const sizeSpan = document.createElement('span');
    sizeSpan.className = 'file-size';
    sizeSpan.textContent = formatBytes(node.size_bytes);

    li.appendChild(nameSpan);
    li.appendChild(sizeSpan);
    container.appendChild(li);
  }
}

async function openDocument(path) {
  try {
    const res = await fetch(`/api/docs-files/${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    displayDocument(data);
  } catch (e) {
    const viewer = $('doc-viewer');
    if (viewer) {
      viewer.innerHTML = `<div style="color:#f06070;">⚠️ ${escapeHtml(e.message)}</div>`;
    }
  }
}

function displayDocument(data) {
  const viewer = $('doc-viewer');
  if (!viewer) return;

  const meta = data.metadata || {};
  const content = data.content || '';

  viewer.innerHTML = `
    <div class="doc-header">
      <h3>${escapeHtml(meta.name || 'Document')}</h3>
      <div class="doc-meta">
        <span>Type: ${escapeHtml(meta.file_type || 'unknown')}</span>
        <span>Size: ${formatBytes(meta.size_bytes || 0)}</span>
        ${meta.word_count ? `<span>Words: ${meta.word_count}</span>` : ''}
        ${meta.sheet_names ? `<span>Sheets: ${meta.sheet_names.join(', ')}</span>` : ''}
      </div>
    </div>
    <div class="doc-content"><pre>${escapeHtml(content)}</pre></div>
  `;
}

async function updateDocStats() {
  try {
    const res = await fetch('/api/docs/statistics');
    if (!res.ok) return;
    const stats = await res.json();
    const el = $('doc-stats');
    if (el) {
      el.innerHTML = `
        <span>📄 ${stats.total_files || 0} files</span>
        <span>📦 ${((stats.total_size_bytes || 0) / (1024 * 1024)).toFixed(1)} MB</span>
        <span>✅ ${stats.supported_files || 0} supported</span>
      `;
    }
  } catch {
    // Silently fail
  }
}

function setupDocSearch() {
  const input = $('doc-search');
  if (!input) return;

  input.addEventListener('input', debounce(async () => {
    const q = input.value.trim();
    if (q.length < 2) {
      loadDocsTree();
      return;
    }
    try {
      const res = await fetch(`/api/docs/search?q=${encodeURIComponent(q)}`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      const treeEl = $('doc-tree');
      if (treeEl) {
        if (data.results.length === 0) {
          treeEl.innerHTML = '<div class="no-results">No documents found</div>';
        } else {
          treeEl.innerHTML = data.results.map(r => `
            <div class="file" style="cursor:pointer;padding:4px 8px;border-radius:4px;" 
                 onclick="openDocument('${r.path}')" 
                 onmouseover="this.style.backgroundColor='rgba(255,255,255,0.05)'" 
                 onmouseout="this.style.backgroundColor='transparent'">
              📄 ${escapeHtml(r.name)}
              <span style="font-size:11px;color:#666;margin-left:8px;">${formatBytes(r.size_bytes || 0)}</span>
            </div>
          `).join('');
        }
      }
    } catch {
      // Silently fail
    }
  }, 300));
}

// ================================================================
// KEYBOARD SHORTCUTS (Global)
// ================================================================

function setupGlobalShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl+R = Refresh (if not on docs tab)
    if (e.ctrlKey && e.key === 'r') {
      e.preventDefault();
      refreshStatus();
      refreshHeatmap();
      return;
    }

    // Ctrl+1-4 = Tab switching
    if (e.ctrlKey && e.key >= '1' && e.key <= '4') {
      e.preventDefault();
      const index = parseInt(e.key) - 1;
      const tabs = $$('.tab-btn');
      if (tabs[index]) {
        tabs[index].click();
      }
      return;
    }
  });
}

// ================================================================
// INITIALIZE APPLICATION
// ================================================================

function init() {
  console.log('🧠 Brain-5D Operator Dashboard v2.0.0');

  // Setup tab navigation (also initializes components lazily)
  setupTabs();

  // Initialize dashboard (status & heatmap)
  initDashboard();

  // Setup global shortcuts
  setupGlobalShortcuts();

  // Make functions globally accessible for inline onclick handlers
  window.openDocument = openDocument;
  window.refreshStatus = refreshStatus;
  window.refreshHeatmap = refreshHeatmap;

  console.log('✅ Dashboard ready');
}

// ================================================================
// START
// ================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// ================================================================
// MODULE EXPORTS (for bundlers/testing)
// ================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    // Dashboard
    refreshStatus,
    refreshHeatmap,
    drawHeatmap,
    initDashboard,

    // Control Panel
    initControlPanel,
    sendControlCommand,
    sendStructuralCommand,

    // Operator Console
    initOperatorConsole,
    sendConsoleCommand,
    loadProposals,
    handleProposal,

    // Documentation Browser
    initDocumentationBrowser,
    loadDocsTree,
    openDocument,
    displayDocument,

    // Utilities
    formatBytes,
    formatNumber,
    formatFloat,
    debounce,
    escapeHtml,

    // Main
    init,
  };
}