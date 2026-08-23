/**
 * Brain-5D Operator Dashboard – Main Application (Sole Lifecycle Owner)
 *
 * This module is the ONLY component that initializes dashboard sub-modules.
 * ControlPanel and OperatorConsole are pure ES modules that do NOT
 * self-initialize. app.js imports them statically and instantiates each
 * exactly once, when its tab is first activated. This eliminates the
 * duplicate event-handler / duplicate-log symptom.
 *
 * Canonical command contract (unified across Control + Console):
 *   POST /api/control  { "command": "run_ticks", "ticks": 100 }
 *
 * Features:
 * - Tab-based navigation (Dashboard, Control, Console, Research, Docs, Gate)
 * - Real-time system monitoring with auto-refresh
 * - Heatmap visualization
 * - Runtime control (step, run, pause, stop, snapshot)
 * - Structural plasticity management (proposals, approve, reject, undo)
 * - Research registry browser (B5D-SEF)
 * - Alpha.5 Integration Gate status board
 * - Documentation browsing with multi-format support
 * - Keyboard shortcuts for all major actions
 *
 * @version 3.0.0
 * @license MIT
 */

"use strict";

// ================================================================
// IMPORTS — static ES module imports (no dynamic fallback)
// ================================================================

import { ControlPanel } from './control-panel.js';
import { OperatorConsole } from './operator_console.js';

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
    research: document.getElementById('tab-research'),
    docs: document.getElementById('tab-docs'),
    gate: document.getElementById('tab-gate'),
  };

  // Track initialization state
  const initialized = {
    control: false,
    console: false,
    docs: false,
    research: false,
    gate: false,
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
      if (tabName === 'research' && !initialized.research) {
        initResearchBrowser();
        initialized.research = true;
      }
      if (tabName === 'gate' && !initialized.gate) {
        initGateBoard();
        initialized.gate = true;
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

    // Integration status badges (dashboard tab)
    refreshIntegrationStatus();
  } catch (error) {
    const statusEl = $('system-status');
    if (statusEl) {
      statusEl.textContent = '⚠️ offline';
      statusEl.className = 'status-pill error';
    }
  }
}

/**
 * Refresh the integration status badges on the dashboard tab.
 */
async function refreshIntegrationStatus() {
  const checks = [
    { id: 'int-bridge', fn: async () => {
      try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.bridge_exists === true; } catch { return false; }
    }},
    { id: 'int-controller', fn: async () => {
      try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.controller_exists === true; } catch { return false; }
    }},
    { id: 'int-structural', fn: async () => {
      try { const r = await fetch('/api/structural/status'); const d = await r.json(); return d.configured === true; } catch { return false; }
    }},
    { id: 'int-snapshots', fn: async () => {
      try { const r = await fetch('/api/snapshots'); return r.ok; } catch { return false; }
    }},
    { id: 'int-research', fn: async () => {
      try { const r = await fetch('/api/research'); const d = await r.json(); return d.available === true; } catch { return false; }
    }},
    { id: 'int-tests', fn: async () => false }, // not yet automated
  ];

  let passed = 0;
  for (const c of checks) {
    const el = $(c.id);
    if (!el) continue;
    try {
      const ok = await c.fn();
      el.className = `integration-item ${ok ? 'int-passed' : 'int-failed'}`;
      if (ok) passed++;
    } catch {
      el.className = 'integration-item int-failed';
    }
  }

  const badge = $('integration-badge');
  if (badge) {
    badge.textContent = `${passed}/${checks.length} passed`;
    badge.className = passed === checks.length ? 'gate-badge passed' : 'gate-badge pending';
  }
}

/**
 * Refresh snapshot info from /api/snapshot-info
 */
async function refreshSnapshotInfo() {
  try {
    const response = await fetch('/api/snapshot-info', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const info = await response.json();
    if (info.active) {
      setText('snapshot-file', info.path || '—');
      setText('snapshot-tick', info.tick != null ? formatNumber(info.tick) : '—');
      setText('snapshot-size', info.size_bytes != null ? formatBytes(info.size_bytes) : '—');
      setText('snapshot-status', '✅ aktiv');
    } else {
      setText('snapshot-file', '—');
      setText('snapshot-tick', '—');
      setText('snapshot-size', '—');
      setText('snapshot-status', '⏳ initializing...');
    }
  } catch {
    setText('snapshot-status', '⚠️ offline');
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

  // Also draw the 5D projection if available
  draw5DProjection(payload);
}

/**
 * Draw a 5D projection visualization alongside the heatmap.
 * Uses a 3D perspective projection of the 5D network space.
 */
function draw5DProjection(payload) {
  const canvas = document.getElementById('projection-5d');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const values = payload.values || [];
  if (!values.length) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const rows = values.length;
  const cols = values[0]?.length || 1;

  // Create a pseudo-3D isometric projection
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const scale = Math.min(canvas.width, canvas.height) * 0.35 / Math.max(rows, cols);

  const flat = values.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  // Draw grid points with height based on value
  for (let y = 0; y < rows; y += 2) {
    for (let x = 0; x < cols; x += 2) {
      const val = (values[y]?.[x] || 0);
      const normalized = (val - min) / range;

      // Isometric projection
      const isoX = (x - y) * scale * 0.7;
      const isoY = (x + y) * scale * 0.35 - normalized * scale * 2;

      const size = 2 + normalized * 4;
      const hue = 210 - normalized * 195;
      const light = 20 + normalized * 50;

      ctx.beginPath();
      ctx.arc(cx + isoX, cy + isoY - 20, size, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
      ctx.fill();

      // Subtle glow for high values
      if (normalized > 0.6) {
        ctx.beginPath();
        ctx.arc(cx + isoX, cy + isoY - 20, size * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${hue}, 85%, ${light}%, 0.15)`;
        ctx.fill();
      }
    }
  }

  // Draw connecting lines for structure
  ctx.strokeStyle = 'rgba(64, 224, 208, 0.08)';
  ctx.lineWidth = 0.5;
  for (let y = 0; y < rows - 2; y += 3) {
    for (let x = 0; x < cols - 2; x += 3) {
      const v1 = (values[y]?.[x] || 0);
      const v2 = (values[y]?.[x + 2] || 0);
      const v3 = (values[y + 2]?.[x] || 0);

      const n1 = (v1 - min) / range;
      const n2 = (v2 - min) / range;
      const n3 = (v3 - min) / range;

      const x1 = cx + (x - y) * scale * 0.7;
      const y1 = cy + (x + y) * scale * 0.35 - n1 * scale * 2 - 20;
      const x2 = cx + ((x + 2) - y) * scale * 0.7;
      const y2 = cy + ((x + 2) + y) * scale * 0.35 - n2 * scale * 2 - 20;
      const x3 = cx + (x - (y + 2)) * scale * 0.7;
      const y3 = cy + (x + (y + 2)) * scale * 0.35 - n3 * scale * 2 - 20;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x3, y3);
      ctx.stroke();
    }
  }
}

/**
 * Initialize dashboard refresh cycles
 */
function initDashboard() {
  // Initial loads
  refreshStatus();
  refreshHeatmap();
  refreshSnapshotInfo();

  // Set up intervals
  if (refreshInterval) clearInterval(refreshInterval);
  if (heatmapInterval) clearInterval(heatmapInterval);

  refreshInterval = setInterval(refreshStatus, 1000);
  heatmapInterval = setInterval(refreshHeatmap, 5000);
  setInterval(refreshSnapshotInfo, 3000);

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
// CONTROL PANEL INITIALIZATION (sole owner)
// ================================================================

function initControlPanel() {
  console.log('🎮 Control Panel initializing...');
  const instance = new ControlPanel();
  console.log('✅ Control Panel initialized');
  return instance;
}

// ================================================================
// OPERATOR CONSOLE INITIALIZATION (sole owner)
// ================================================================

function initOperatorConsole() {
  console.log('📟 Operator Console initializing...');
  const instance = new OperatorConsole();
  console.log('✅ Operator Console initialized');
  return instance;
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
// RESEARCH BROWSER (B5D-SEF)
// ================================================================

let researchLoaded = false;

function initResearchBrowser() {
  console.log('🔬 Research Browser initializing...');
  if (!researchLoaded) {
    refreshResearchSummary();
    loadResearchReports();
    loadResearchDocuments();
    loadResearchExperiments();
    researchLoaded = true;
  }
}

async function refreshResearchSummary() {
  try {
    const res = await fetch('/api/research', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const el = $('research-summary');
    if (!el) return;

    if (!data.available) {
      el.innerHTML = '<span class="research-unavailable">⚠️ Research-Quelle nicht konfiguriert (B5D-SEF registry nicht gefunden)</span>';
      return;
    }

    const cats = data.categories || {};
    const items = Object.entries(cats).map(([k, v]) =>
      `<span class="research-stat"><strong>${v}</strong> ${escapeHtml(k)}</span>`
    ).join('');
    el.innerHTML = `<span class="research-available">✅ B5D-SEF aktiv</span>${items}`;
  } catch (error) {
    const el = $('research-summary');
    if (el) el.innerHTML = `<span class="research-unavailable">⚠️ Research API nicht erreichbar: ${error.message || 'unbekannt'}</span>`;
  }
}

async function loadResearchReports() {
  try {
    const res = await fetch('/api/research/reports', { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    const container = $('research-reports');
    if (!container) return;
    const reports = data.reports || [];
    if (!reports.length) {
      container.innerHTML = '<div class="research-empty">No generated reports</div>';
      return;
    }
    container.innerHTML = reports.map(r => `
      <div class="research-report-item" data-path="${escapeHtml(r.path)}">
        <span class="research-report-name">📄 ${escapeHtml(r.name)}</span>
        <span class="research-report-size">${formatBytes(r.size_bytes)}</span>
      </div>
    `).join('');
    container.querySelectorAll('.research-report-item').forEach(item => {
      item.addEventListener('click', () => openResearchDocument(item.dataset.path));
    });
  } catch {
    // silently fail
  }
}

async function loadResearchDocuments() {
  try {
    const res = await fetch('/api/research/documents', { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    const container = $('research-documents');
    if (!container) return;
    const docs = data.documents || [];
    if (!docs.length) {
      container.innerHTML = '<div class="research-empty">No registry documents</div>';
      return;
    }
    const byCategory = {};
    for (const d of docs) {
      if (!byCategory[d.category]) byCategory[d.category] = [];
      byCategory[d.category].push(d);
    }
    let html = '';
    for (const [cat, items] of Object.entries(byCategory)) {
      html += `<div class="research-category"><h4>${escapeHtml(cat)}</h4><ul>`;
      for (const d of items) {
        html += `<li class="research-doc-item" data-path="${escapeHtml(d.path)}">📄 ${escapeHtml(d.name)} <span class="research-doc-kind">${escapeHtml(d.kind)}</span></li>`;
      }
      html += '</ul></div>';
    }
    container.innerHTML = html;
    container.querySelectorAll('.research-doc-item').forEach(item => {
      item.addEventListener('click', () => openResearchDocument(item.dataset.path));
    });
  } catch {
    // silently fail
  }
}

async function loadResearchExperiments() {
  try {
    const res = await fetch('/api/research/experiments', { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    const container = $('research-experiments');
    if (!container) return;
    const exps = data.experiments || [];
    if (!exps.length) {
      container.innerHTML = '<div class="research-empty">No experiments registered</div>';
      return;
    }
    container.innerHTML = exps.map(e => {
      const m = e.manifest || {};
      return `<div class="research-experiment-item">
        <span class="research-exp-id">${escapeHtml(e.id)}</span>
        <span class="research-exp-tick">Tick ${m.tick_count || '?'}</span>
        <span class="research-exp-neurons">🧠 ${m.final_neuron_count || m.initial_neuron_count || '?'}</span>
      </div>`;
    }).join('');
  } catch {
    // silently fail
  }
}

async function openResearchDocument(path) {
  try {
    const res = await fetch(`/api/research-files/${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const viewer = $('research-viewer');
    if (!viewer) return;
    viewer.innerHTML = `
      <div class="research-doc-header">
        <h3>${escapeHtml(path)}</h3>
        <span>${formatBytes(data.size_bytes)}</span>
      </div>
      <div class="research-doc-content"><pre>${escapeHtml(data.content || '')}</pre></div>
    `;
  } catch (e) {
    const viewer = $('research-viewer');
    if (viewer) viewer.innerHTML = `<div class="research-error">⚠️ ${escapeHtml(e.message)}</div>`;
  }
}

// ================================================================
// ALPHA.5 INTEGRATION GATE STATUS
// ================================================================

let gateLoaded = false;

function initGateBoard() {
  console.log('🚪 Alpha.5 Integration Gate initializing...');
  if (!gateLoaded) {
    refreshGateStatus();
    const refreshBtn = $('gate-refresh');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', refreshGateStatus);
    }
    gateLoaded = true;
  }
}

async function refreshGateStatus() {
  const items = [
    { id: 'gate-process', label: 'One application process', check: async () => {
      try { const r = await fetch('/api/debug/bridge'); return r.ok; } catch { return false; }
    }},
    { id: 'gate-bridge', label: 'OperatorBridge consistently reachable', check: async () => {
      try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.bridge_exists === true; } catch { return false; }
    }},
    { id: 'gate-controller', label: 'Controller exists', check: async () => {
      try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.controller_exists === true; } catch { return false; }
    }},
    { id: 'gate-structural', label: 'Structural Coordinator connected', check: async () => {
      try { const r = await fetch('/api/structural/status'); const d = await r.json(); return d.configured === true; } catch { return false; }
    }},
    { id: 'gate-snapshots', label: 'Snapshot pipeline available', check: async () => {
      try { const r = await fetch('/api/snapshots'); return r.ok; } catch { return false; }
    }},
    { id: 'gate-research', label: 'Research framework (B5D-SEF) active', check: async () => {
      try { const r = await fetch('/api/research'); const d = await r.json(); return d.available === true; } catch { return false; }
    }},
  ];

  for (const item of items) {
    const el = $(item.id);
    if (!el) continue;
    el.className = 'gate-item gate-pending';
    el.querySelector('.gate-status').textContent = '…';
    try {
      const ok = await item.check();
      el.className = `gate-item ${ok ? 'gate-passed' : 'gate-failed'}`;
      el.querySelector('.gate-status').textContent = ok ? '✅' : '❌';
    } catch {
      el.className = 'gate-item gate-failed';
      el.querySelector('.gate-status').textContent = '❌';
    }
  }
}

// ================================================================
// INTEGRATION STATUS MODAL (Popup für alle Versionen)
// ================================================================

/**
 * Build version-specific integration checks.
 * Each version has its own set of checks that reflect what was
 * integrated at that stage of Brain-5D development.
 */
function getVersionChecks() {
  return {
    'v0.4 (Persistenz)': [
      { label: 'Delta-Journal', icon: '💾', check: async () => { try { const r = await fetch('/api/status'); return r.ok; } catch { return false; } }},
      { label: 'Storage Pipeline', icon: '📦', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.storage?.deltas_written !== undefined; } catch { return false; } }},
      { label: 'Crash Recovery', icon: '🛡️', check: async () => { try { const r = await fetch('/api/status'); return r.ok; } catch { return false; } }},
    ],
    'v0.5 (Integration Hardening)': [
      { label: 'OperatorBridge', icon: '🌉', check: async () => { try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.bridge_exists === true; } catch { return false; } }},
      { label: 'Controller', icon: '🎮', check: async () => { try { const r = await fetch('/api/debug/bridge'); const d = await r.json(); return d.controller_exists === true; } catch { return false; } }},
      { label: 'Structural API', icon: '🧠', check: async () => { try { const r = await fetch('/api/structural/status'); return r.ok; } catch { return false; } }},
      { label: 'Snapshots', icon: '💾', check: async () => { try { const r = await fetch('/api/snapshots'); return r.ok; } catch { return false; } }},
      { label: 'Research (B5D-SEF)', icon: '🔬', check: async () => { try { const r = await fetch('/api/research'); const d = await r.json(); return d.available === true; } catch { return false; } }},
      { label: 'Heatmaps', icon: '🔥', check: async () => { try { const r = await fetch('/api/heatmap?kind=activity'); return r.ok; } catch { return false; } }},
      { label: 'Docs Browser', icon: '📄', check: async () => { try { const r = await fetch('/api/docs'); return r.ok; } catch { return false; } }},
    ],
    'v0.5α6 (Morphological Self-Reg)': [
      { label: 'Self-Organization', icon: '🧬', check: async () => { try { const r = await fetch('/api/structural/status'); const d = await r.json(); return d.configured === true; } catch { return false; } }},
      { label: 'Proposals', icon: '📋', check: async () => { try { const r = await fetch('/api/structural/proposals'); return r.ok; } catch { return false; } }},
      { label: 'Homeostasis', icon: '⚖️', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.homeostasis?.enabled !== undefined; } catch { return false; } }},
    ],
    'v0.6 (Skalierung)': [
      { label: 'Large Network', icon: '🌐', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return (d.system?.neurons || 0) > 100; } catch { return false; } }},
      { label: 'Performance', icon: '⚡', check: async () => { try { const r = await fetch('/api/status'); return r.ok; } catch { return false; } }},
    ],
    'v0.7 (Learning Env.)': [
      { label: 'STDP', icon: '🧪', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.learning?.stdp_updates !== undefined; } catch { return false; } }},
      { label: 'Reward System', icon: '🏆', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.learning?.reward_updates !== undefined; } catch { return false; } }},
    ],
    'v0.8+ (Embodiment → HMI → KI)': [
      { label: 'Embodiment', icon: '🤖', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.embodiment !== undefined; } catch { return false; } }},
      { label: 'Signal Bridge', icon: '📡', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return d.signal_metrics !== undefined; } catch { return false; } }},
    ],
  };
}

/**
 * Open the integration status modal with all version checks.
 */
async function openIntegrationModal() {
  const modal = document.getElementById('integration-modal');
  const body = document.getElementById('integration-modal-body');
  if (!modal || !body) return;

  modal.style.display = 'flex';
  body.innerHTML = '<div class="modal-loading">🔄 Lade Integrationsdaten…</div>';

  const versions = getVersionChecks();
  let html = '';

  for (const [version, checks] of Object.entries(versions)) {
    html += `<div class="int-version-section"><h3>${escapeHtml(version)}</h3><div class="int-version-grid">`;
    for (const c of checks) {
      let status = 'unknown';
      let icon = '⏳';
      try {
        const ok = await c.check();
        status = ok ? 'passed' : 'failed';
        icon = ok ? '✅' : '❌';
      } catch {
        status = 'unknown';
        icon = '⚠️';
      }
      html += `<div class="int-version-item int-${status}">
        <span class="int-version-icon">${icon}</span>
        <span class="int-version-label">${c.icon} ${escapeHtml(c.label)}</span>
      </div>`;
    }
    html += '</div></div>';
  }

  body.innerHTML = html;
}

/**
 * Close the integration modal.
 */
function closeIntegrationModal() {
  const modal = document.getElementById('integration-modal');
  if (modal) modal.style.display = 'none';
}

// ================================================================
// ENHANCED DASHBOARD – Interactive Features
// ================================================================

/**
 * Make integration status items clickable – opens the modal
 * with detailed version-by-version integration info.
 */
function setupIntegrationClickHandlers() {
  // Click on the integration section header or badge opens the modal
  const header = document.querySelector('.integration-status .panel-title h2');
  if (header) {
    header.style.cursor = 'pointer';
    header.addEventListener('click', openIntegrationModal);
  }

  const badge = document.getElementById('integration-badge');
  if (badge) {
    badge.style.cursor = 'pointer';
    badge.addEventListener('click', openIntegrationModal);
  }

  // Each integration item shows a tooltip with detail on click
  document.querySelectorAll('.integration-item.clickable').forEach(el => {
    el.addEventListener('click', openIntegrationModal);
  });

  // Modal close handlers
  const closeBtns = document.querySelectorAll('#modal-close-btn, #modal-close-btn2');
  closeBtns.forEach(btn => btn.addEventListener('click', closeIntegrationModal));

  const modal = document.getElementById('integration-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeIntegrationModal();
    });
  }

  // Refresh button
  const refreshBtn = document.getElementById('modal-refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', openIntegrationModal);
  }

  // Escape key closes modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeIntegrationModal();
  });
}

/**
 * Add auto-refresh toggle to the dashboard.
 */
function setupAutoRefreshToggle() {
  const statusEl = document.getElementById('system-status');
  if (!statusEl) return;

  statusEl.addEventListener('dblclick', () => {
    // Toggle auto-refresh on/off
    if (refreshInterval) {
      clearInterval(refreshInterval);
      clearInterval(heatmapInterval);
      refreshInterval = null;
      heatmapInterval = null;
      statusEl.textContent += ' (paused)';
    } else {
      refreshInterval = setInterval(refreshStatus, 1000);
      heatmapInterval = setInterval(refreshHeatmap, 5000);
      statusEl.textContent = statusEl.textContent.replace(' (paused)', '');
    }
  });
}

/**
 * Add a system command runner to the dashboard header.
 */
function setupQuickActions() {
  // Ctrl+Shift+R = force refresh all
  // Ctrl+Shift+M = open integration modal
  // Already handled by keyboard shortcuts below
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

    // Ctrl+Shift+I = Open Integration Modal
    if (e.ctrlKey && e.shiftKey && e.key === 'I') {
      e.preventDefault();
      openIntegrationModal();
      return;
    }

    // Ctrl+1-6 = Tab switching
    if (e.ctrlKey && e.key >= '1' && e.key <= '6') {
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
  console.log('🧠 Brain-5D Operator Dashboard v3.0.0');

  // Setup tab navigation (also initializes components lazily)
  setupTabs();

  // Initialize dashboard (status & heatmap)
  initDashboard();

  // Setup integration click handlers
  setupIntegrationClickHandlers();

  // Setup auto-refresh toggle
  setupAutoRefreshToggle();

  // Setup global shortcuts
  setupGlobalShortcuts();

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
