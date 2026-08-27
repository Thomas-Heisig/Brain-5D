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
  // null/undefined => unavailable, NOT fake zero
  if (value === null || value === undefined) return '—';
  const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
  let size = Number(value);
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx++;
  }
  return `${size.toFixed(idx === 0 ? 0 : 2)} ${units[idx]}`;
}

function formatNumber(value) {
  // null/undefined => unavailable, NOT fake zero
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString();
}

function formatFloat(value, decimals = 3) {
  // null/undefined => unavailable, NOT fake zero
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(decimals);
}

/**
 * Format an optional metric with a unit suffix.
 * null/undefined => "—" (unavailable), measured zero => "0.000 unit".
 */
function formatMetricUnit(value, unit, decimals = 3) {
  if (value === null || value === undefined) return '—';
  return `${Number(value).toFixed(decimals)} ${unit}`;
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
    inspect: document.getElementById('tab-inspect'),
    control: document.getElementById('tab-control'),
    console: document.getElementById('tab-console'),
    research: document.getElementById('tab-research'),
    docs: document.getElementById('tab-docs'),
    gate: document.getElementById('tab-gate'),
  };

  // Track initialization state
  const initialized = {
    inspect: false,
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
      if (tabName === 'inspect' && !initialized.inspect) {
        initInspectTab();
        initialized.inspect = true;
      }
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
let liveSource = true;  // true = LIVE_RUNTIME, false = SNAPSHOT
let refreshInterval = null;
let heatmapInterval = null;
let liveProjectionInterval = null;

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

    // System metrics (always measured, real values)
    setText('tick', formatNumber(system.tick));
    setText('neurons', formatNumber(system.neurons));
    setText('synapses', formatNumber(system.synapses));
    setText('spikes', formatNumber(system.spikes_total));
    setText('core-ms', formatFloat(system.core_step_ms, 3));
    setText('energy', formatFloat(system.mean_energy, 3));

    // Storage metrics — distinguish disabled/unavailable from measured zero.
    // storage.available=false (poc_config) => "disabled by config", all metrics "—".
    if (storage.available === false) {
      setText('deltas', '—');
      setText('bytes', '—');
      setText('write-ms', '—');
      setText('commit-ms', '—');
      setText('journal-size', '—');
      setText('drops', '—');
      setText('queue-badge', 'disabled');
      const fill = $('queue-fill');
      if (fill) fill.style.width = '0%';
    } else {
      setText('deltas', formatNumber(storage.deltas_written));
      setText('bytes', formatBytes(storage.bytes_written));
      setText('write-ms', formatMetricUnit(storage.write_latency_ms, 'ms', 3));
      setText('commit-ms', formatMetricUnit(storage.commit_latency_ms, 'ms', 3));
      setText('journal-size', formatBytes(storage.journal_size_bytes));
      setText('drops', formatNumber(storage.dropped_batches));

      // Queue progress
      const depth = storage.queue_depth;
      const capacity = storage.queue_capacity;
      if (depth === null || depth === undefined || capacity === null || capacity === undefined) {
        setText('queue-badge', '—');
        const fill = $('queue-fill');
        if (fill) fill.style.width = '0%';
      } else {
        setText('queue-badge', `${depth} / ${capacity}`);
        const fill = $('queue-fill');
        if (fill) {
          const percent = capacity > 0 ? Math.min(100, (depth / capacity) * 100) : 0;
          fill.style.width = `${percent}%`;
        }
      }
    }

    // Learning metrics — when STDP/Reward disabled by config, show "—" not fake 0.
    // The backend reports 0 for disabled counters because no updates occur,
    // but we surface the disabled state via the homeostasis/self-org flags.
    // Learning counters are real measured zeros when disabled (0 updates happened),
    // so we keep formatNumber here.
    setText('stdp', formatNumber(learning.stdp_updates));
    setText('reward-updates', formatNumber(learning.reward_updates));
    setText('rewards', `${formatNumber(learning.rewards_applied)} / ${formatNumber(learning.rewards_received)}`);
    setText('pending', formatNumber(learning.pending_rewards));
    setText('learning-ms', formatMetricUnit(learning.update_ms, 'ms', 3));

    // Homeostasis — disabled by config => explicit "disabled", not fake zeros.
    if (homeostasis.enabled === false) {
      setText('homeostasis-state', 'disabled by config');
      setText('target-rate', '—');
      setText('mean-rate', '—');
      setText('rate-error', '—');
      setText('threshold-adaptation', '—');
      setText('energy-error', '—');
      setText('active-neurons', '—');
    } else {
      setText('homeostasis-state', 'aktiv');
      setText('target-rate', formatMetricUnit(homeostasis.target_rate_hz, 'Hz', 3));
      setText('mean-rate', formatMetricUnit(homeostasis.mean_rate_hz || homeostasis.actual_rate_hz, 'Hz', 3));
      setText('rate-error', formatMetricUnit(homeostasis.mean_rate_error_hz || homeostasis.rate_error_hz, 'Hz', 3));
      setText('threshold-adaptation', formatFloat(homeostasis.mean_threshold_adaptation, 4));
      setText('energy-error', formatFloat(homeostasis.mean_energy_error, 4));
      setText('active-neurons', formatNumber(homeostasis.active_neurons));
    }

    // Self-organization — disabled by config => explicit "—", not fake 0.
    if (selfOrg.available === false) {
      setText('neurons-created', '—');
      setText('neurons-removed', '—');
      setText('synapses-created', '—');
      setText('synapses-pruned', '—');
    } else {
      setText('neurons-created', formatNumber(selfOrg.neurons_created));
      setText('neurons-removed', formatNumber(selfOrg.neurons_removed));
      setText('synapses-created', formatNumber(selfOrg.synapses_created));
      setText('synapses-pruned', formatNumber(selfOrg.synapses_pruned));
    }

    // Status badge
    const statusEl = $('system-status');
    if (statusEl) {
      statusEl.textContent = `${data.status || 'idle'} · ${data.version || 'unknown'}`;
      const workerFailed = storage.worker_failed;
      statusEl.className = workerFailed === true
        ? 'status-pill error'
        : (workerFailed === false ? 'status-pill online' : 'status-pill');
    }

    // Integration status badges (dashboard tab)
    refreshIntegrationStatus();

    // Structural live loop status
    refreshLiveLoopStatus();

    // Runtime error visibility
    refreshErrorVisibility();
  } catch (error) {
    const statusEl = $('system-status');
    if (statusEl) {
      statusEl.textContent = '⚠️ offline';
      statusEl.className = 'status-pill error';
    }
  }
}

/**
 * Refresh the structural live loop status from the gate status endpoint.
 */
async function refreshLiveLoopStatus() {
  const itemIds = ['ll-adapter', 'll-signal', 'll-policy', 'll-coordinator',
                   'll-approval', 'll-mutation', 'll-journal', 'll-undo', 'll-replay'];
  try {
    const r = await fetch('/api/gate/status', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    // Check live loop artifact via the gate status builder
    const gateA = data.gate_a?.items || [];
    const adapterItem = gateA.find(i => i.id === 'A-STRUCT-RUNTIME-ADAPTER');
    const liveLoopVerified = adapterItem?.status === 'passed';

    const badge = $('live-loop-badge');
    if (badge) {
      badge.textContent = liveLoopVerified ? '✅ VERIFIED' : '⏳ pending';
      badge.className = `gate-badge ${liveLoopVerified ? 'passed' : 'pending'}`;
    }

    const meta = $('live-loop-meta');
    if (meta) {
      meta.textContent = liveLoopVerified
        ? '✅ Structural live loop verified via verification artifact'
        : '⏳ Run test_structural_live_loop.py to generate verification artifact';
    }

    // Update individual items
    const liveItems = data.live_runtime || [];
    const structuralLive = liveItems.find(i => i.key === 'structural');
    const soActive = structuralLive?.live_status === 'active';

    // Structural items status
    const structuralItems = gateA.filter(i => i.category === 'structural_composition');
    for (const item of structuralItems) {
      const id = item.id || '';
      const elId = id.toLowerCase().replace(/[^a-z0-9]/g, '-');
      // Map known IDs to our element IDs
      const idMap = {
        'A-STRUCT-RUNTIME-ADAPTER': 'll-adapter',
        'A-STRUCT-COORDINATOR': 'll-coordinator',
        'A-STRUCT-PLASTICITY': 'll-mutation',
        'A-STRUCT-MANIPULATOR': 'll-mutation',
        'A-STRUCT-APPROVAL': 'll-approval',
        'A-STRUCT-JOURNAL': 'll-journal',
        'A-STRUCT-PROVENANCE': 'll-signal',
      };
      const targetId = idMap[id];
      if (!targetId) continue;
      const el = $(targetId);
      if (!el) continue;
      if (item.status === 'passed') {
        el.className = 'live-loop-item ll-passed';
        el.textContent = `✅ ${el.textContent.replace(/^[✅⏳❌]\s*/, '')}`;
      } else if (item.status === 'stale') {
        el.className = 'live-loop-item ll-stale';
        el.textContent = `🔄 ${el.textContent.replace(/^[✅⏳❌]\s*/, '')}`;
      } else {
        el.className = 'live-loop-item ll-pending';
        el.textContent = `⏳ ${el.textContent.replace(/^[✅⏳❌]\s*/, '')}`;
      }
    }
  } catch {
    for (const id of itemIds) {
      const el = $(id);
      if (el) {
        el.className = 'live-loop-item ll-pending';
        el.textContent = `⏳ ${el.textContent.replace(/^[✅⏳❌]\s*/, '')}`;
      }
    }
    const badge = $('live-loop-badge');
    if (badge) {
      badge.textContent = 'offline';
      badge.className = 'gate-badge failed';
    }
  }
}

/**
 * Refresh runtime error visibility from /api/structural/errors.
 */
async function refreshErrorVisibility() {
  try {
    const r = await fetch('/api/structural/errors', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    const errors = data.errors || [];

    const badge = $('error-count-badge');
    if (badge) {
      badge.textContent = `${errors.length} error${errors.length !== 1 ? 's' : ''}`;
      badge.className = `gate-badge ${errors.length === 0 ? 'passed' : 'failed'}`;
    }

    const list = $('error-list');
    if (!list) return;

    if (errors.length === 0) {
      list.innerHTML = '<div class="error-empty">✅ No runtime errors recorded.</div>';
    } else {
      list.innerHTML = errors.map(e => `
        <div class="error-item error-${e.fatal ? 'fatal' : 'warning'}">
          <span class="error-tick">Tick ${e.tick}</span>
          <span class="error-phase">${e.phase}</span>
          <span class="error-type">${e.exception_type}</span>
          <span class="error-msg">${e.message}</span>
          <span class="error-hash">#${e.traceback_hash || ''}</span>
        </div>
      `).join('');
    }

    const meta = $('error-meta');
    if (meta) {
      meta.textContent = `Structured RuntimeErrorEvent buffer · ${errors.length} event(s)`;
    }
  } catch {
    const badge = $('error-count-badge');
    if (badge) {
      badge.textContent = 'offline';
      badge.className = 'gate-badge failed';
    }
  }
}

/**
 * Refresh the integration status badges on the dashboard tab.
 *
 * Uses the real backend endpoint /api/integration/status (Phase 14)
 * instead of the previous frontend-only heuristic that hardcoded
 * int-tests to false.
 */
async function refreshIntegrationStatus() {
  const itemIds = ['int-bridge', 'int-controller', 'int-structural', 'int-snapshots', 'int-research', 'int-tests'];
  const nameToId = {
    'Bridge': 'int-bridge',
    'Controller': 'int-controller',
    'Structural': 'int-structural',
    'Snapshot': 'int-snapshots',
    'Research': 'int-research',
    'Tests': 'int-tests',
  };

  try {
    const r = await fetch('/api/integration/status', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    const items = data.items || [];

    let passed = 0;
    for (const item of items) {
      const id = nameToId[item.name];
      if (!id) continue;
      const el = $(id);
      if (!el) continue;
      const status = item.status || 'pending';
      const cls = status === 'passed' ? 'int-passed'
        : status === 'disabled' ? 'int-disabled'
        : status === 'stale' ? 'int-stale'
        : status === 'failed' ? 'int-failed'
        : 'int-pending';
      el.className = `integration-item clickable ${cls}`;
      el.title = item.message || '';
      if (status === 'passed') passed++;
    }

    const badge = $('integration-badge');
    if (badge) {
      const overall = data.overall || 'pending';
      const label = overall === 'passed' ? `${passed}/${data.total} passed`
        : overall === 'stale' ? `STALE (${data.stale})`
        : overall === 'failed' ? `FAILED (${data.failed})`
        : `${passed}/${data.total} passed`;
      badge.textContent = label;
      badge.className = overall === 'passed' ? 'gate-badge passed'
        : overall === 'stale' ? 'gate-badge stale'
        : overall === 'failed' ? 'gate-badge failed'
        : 'gate-badge pending';
    }
  } catch {
    for (const id of itemIds) {
      const el = $(id);
      if (el) el.className = 'integration-item int-failed';
    }
    const badge = $('integration-badge');
    if (badge) {
      badge.textContent = 'offline';
      badge.className = 'gate-badge failed';
    }
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

  // Filter out null/undefined values for range computation
  const valid = rows.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  const min = valid.length > 0 ? Math.min(...valid) : 0;
  const max = valid.length > 0 ? Math.max(...valid) : 0;
  const width = rows[0].length;
  const height = rows.length;
  const cellW = canvas.width / width;
  const cellH = canvas.height / height;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const val = rows[y][x];
      if (val === null || val === undefined) {
        // No-data cell: draw a neutral pattern
        ctx.fillStyle = 'rgba(40, 50, 65, 0.4)';
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
        // Draw a subtle crosshatch to indicate "no data"
        ctx.strokeStyle = 'rgba(60, 70, 85, 0.3)';
        ctx.lineWidth = 0.5;
        const cx = x * cellW;
        const cy = y * cellH;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + cellW, cy + cellH);
        ctx.moveTo(cx + cellW, cy);
        ctx.lineTo(cx, cy + cellH);
        ctx.stroke();
      } else {
        ctx.fillStyle = heatmapColor(val, min, max);
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      }
    }
  }

  setText(
    'heatmap-meta',
    `${payload.source === 'live_runtime' ? 'LIVE' : 'SNAPSHOT'} · ${payload.kind || heatmapKind} · Tick ${payload.tick || 0} · ${payload.sample_count || 0} Samples · ${formatFloat(min, 4)}…${formatFloat(max, 4)}`
  );

  // Also draw the 5D projection if available
  draw5DProjection(payload);
}

/**
 * Refresh live projection from /api/live/projection (LIVE_RUNTIME source)
 */
async function refreshLiveProjection() {
  const canvas = $('heatmap');
  if (!canvas) return;
  if (!liveSource) return;  // Only when live mode is active

  try {
    const response = await fetch(
      `/api/live/projection?kind=${encodeURIComponent(heatmapKind)}&resolution=50`,
      { cache: 'no-store' }
    );
    if (!response.ok) {
      // Fall back to snapshot heatmap if live unavailable
      if (liveSource) {
        liveSource = false;
        updateSourceBadge();
      }
      return;
    }
    const data = await response.json();
    drawHeatmap(data);
  } catch {
    // Silently fall back — snapshot will be used on next interval
  }
}

/**
 * Update the source badge in the UI
 */
function updateSourceBadge() {
  const badge = $('source-badge');
  if (badge) {
    badge.textContent = liveSource ? 'LIVE' : 'SNAPSHOT';
    badge.className = liveSource ? 'badge badge-live' : 'badge badge-snapshot';
  }
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

  const flat = values.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  if (flat.length === 0) return;
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  // Draw grid points with height based on value
  for (let y = 0; y < rows; y += 2) {
    for (let x = 0; x < cols; x += 2) {
      const val = values[y]?.[x];
      if (val === null || val === undefined) continue;  // Skip no-data cells
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

  // Draw connecting lines for structure (only between valid cells)
  ctx.strokeStyle = 'rgba(64, 224, 208, 0.08)';
  ctx.lineWidth = 0.5;
  for (let y = 0; y < rows - 2; y += 3) {
    for (let x = 0; x < cols - 2; x += 3) {
      const v1 = values[y]?.[x];
      const v2 = values[y]?.[x + 2];
      const v3 = values[y + 2]?.[x];
      // Skip if any endpoint is null
      if (v1 === null || v1 === undefined || v2 === null || v2 === undefined || v3 === null || v3 === undefined) continue;

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
  refreshLiveProjection();
  refreshSnapshotInfo();
  refreshLiveLoopStatus();
  refreshErrorVisibility();

  // Set up intervals
  if (refreshInterval) clearInterval(refreshInterval);
  if (heatmapInterval) clearInterval(heatmapInterval);
  if (liveProjectionInterval) clearInterval(liveProjectionInterval);

  refreshInterval = setInterval(refreshStatus, 1000);
  heatmapInterval = setInterval(refreshHeatmap, 5000);
  liveProjectionInterval = setInterval(refreshLiveProjection, 500);
  setInterval(refreshSnapshotInfo, 3000);
  setInterval(refreshLiveLoopStatus, 5000);
  setInterval(refreshErrorVisibility, 5000);

  // Heatmap kind buttons
  $$('button[data-kind]').forEach(button => {
    button.addEventListener('click', () => {
      heatmapKind = button.dataset.kind;
      $$('button[data-kind]').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      if (liveSource) {
        refreshLiveProjection();
      } else {
        refreshHeatmap();
      }
    });
  });

  // Live / Snapshot toggle
  const liveToggle = $('live-toggle');
  if (liveToggle) {
    liveToggle.addEventListener('click', () => {
      liveSource = !liveSource;
      updateSourceBadge();
      if (liveSource) {
        refreshLiveProjection();
      } else {
        refreshHeatmap();
      }
    });
  }

  updateSourceBadge();
}

// ================================================================
// INSPECT TAB (real 5D network inspector, Phase 8/9)
// ================================================================

let inspectInterval = null;

function initInspectTab() {
  console.log('🔍 Inspect tab initializing...');
  refreshNetworkSummary();
  loadNeuronPage();
  loadSynapsePage();
  loadProjection();

  const refreshBtn = $('inspect-refresh');
  if (refreshBtn) refreshBtn.addEventListener('click', () => {
    refreshNetworkSummary();
    loadNeuronPage();
    loadSynapsePage();
    loadProjection();
  });

  const neuronLoad = $('neuron-load');
  if (neuronLoad) neuronLoad.addEventListener('click', loadNeuronPage);

  const synapseLoad = $('synapse-load');
  if (synapseLoad) synapseLoad.addEventListener('click', loadSynapsePage);

  const projMode = $('projection-mode');
  if (projMode) projMode.addEventListener('change', loadProjection);

  // Auto-refresh summary every 2s while inspect tab is active
  if (inspectInterval) clearInterval(inspectInterval);
  inspectInterval = setInterval(refreshNetworkSummary, 2000);
  console.log('✅ Inspect tab ready');
}

async function refreshNetworkSummary() {
  try {
    const r = await fetch('/api/network/summary', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    setText('inspect-dimensions', (d.dimensions || []).join(' × '));
    setText('inspect-neuron-count', formatNumber(d.neuron_count));
    setText('inspect-synapse-count', formatNumber(d.synapse_count));
    setText('inspect-input-count', formatNumber(d.input_count));
    setText('inspect-output-count', formatNumber(d.output_count));
    setText('inspect-active-neurons', formatNumber(d.active_neurons));
    setText('inspect-silent-neurons', formatNumber(d.silent_neurons));
    setText('inspect-queue-depth', formatNumber(d.queue_depth));
    setText('inspect-tick', formatNumber(d.current_tick));
    setText('inspect-total-spikes', formatNumber(d.total_spikes));
    setText('inspect-mean-energy', formatFloat(d.mean_energy, 4));
    setText('inspect-mean-v', formatFloat(d.mean_v, 4));
  } catch {
    ['inspect-dimensions','inspect-neuron-count','inspect-synapse-count','inspect-input-count',
     'inspect-output-count','inspect-active-neurons','inspect-silent-neurons','inspect-queue-depth',
     'inspect-tick','inspect-total-spikes','inspect-mean-energy','inspect-mean-v']
      .forEach(id => setText(id, '—'));
  }
}

async function loadNeuronPage() {
  const limit = parseInt($('neuron-limit')?.value || '200', 10);
  const offset = parseInt($('neuron-offset')?.value || '0', 10);
  const activeOnly = $('neuron-active-only')?.checked || false;
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (activeOnly) params.set('active_only', 'true');
    const r = await fetch(`/api/network/neurons?${params}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    const body = $('neuron-table-body');
    if (!body) return;
    const rows = d.neurons || [];
    body.innerHTML = rows.map(n => `
      <tr>
        <td>${n.neuron_id}</td>
        <td>${n.x1}</td><td>${n.x2}</td><td>${n.x3}</td><td>${n.x4}</td><td>${n.x5}</td>
        <td>${formatFloat(n.v, 3)}</td>
        <td>${formatFloat(n.u, 3)}</td>
        <td>${formatFloat(n.energy, 4)}</td>
        <td>${n.last_spike < 0 ? '—' : n.last_spike}</td>
        <td>${n.spike_count}</td>
        <td>${n.is_input ? 'I' : (n.is_output ? 'O' : '')}</td>
      </tr>`).join('');
    setText('neuron-page-meta',
      `${d.returned}/${d.total} (offset ${d.offset}, limit ${d.limit}) · source: ${d.source}`);
  } catch (e) {
    const body = $('neuron-table-body');
    if (body) body.innerHTML = `<tr><td colspan="12">⚠️ ${escapeHtml(e.message)}</td></tr>`;
    setText('neuron-page-meta', '—');
  }
}

async function loadSynapsePage() {
  const limit = parseInt($('synapse-limit')?.value || '200', 10);
  const offset = parseInt($('synapse-offset')?.value || '0', 10);
  const sourceRaw = $('synapse-source')?.value;
  const minWeightRaw = $('synapse-min-weight')?.value;
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (sourceRaw) params.set('source', sourceRaw);
    if (minWeightRaw) params.set('min_weight', minWeightRaw);
    const r = await fetch(`/api/network/synapses?${params}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    const body = $('synapse-table-body');
    if (!body) return;
    const rows = d.synapses || [];
    body.innerHTML = rows.map(s => `
      <tr>
        <td>${s.source_id}</td>
        <td>${s.target_id ?? '—'}</td>
        <td>${formatFloat(s.weight, 4)}</td>
        <td>${s.delay ?? '—'}</td>
        <td>${formatFloat(s.eligibility, 4)}</td>
      </tr>`).join('');
    setText('synapse-page-meta',
      `${d.returned}/${d.total} (offset ${d.offset}, limit ${d.limit}) · source: ${d.source}`);
  } catch (e) {
    const body = $('synapse-table-body');
    if (body) body.innerHTML = `<tr><td colspan="5">⚠️ ${escapeHtml(e.message)}</td></tr>`;
    setText('synapse-page-meta', '—');
  }
}

async function loadProjection() {
  const canvas = $('inspect-projection');
  if (!canvas) return;
  const mode = $('projection-mode')?.value || 'activity';
  try {
    const r = await fetch(`/api/network/projection?limit=2000&mode=${encodeURIComponent(mode)}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    drawInspectProjection(canvas, d);
    setText('projection-meta',
      `${d.label} · ${d.sample_count}/${d.total_count} samples · ${d.sampling_method} · source: ${d.source}`);
  } catch (e) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setText('projection-meta', `⚠️ ${e.message}`);
  }
}

function drawInspectProjection(canvas, payload) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const points = payload.points || [];
  if (!points.length) {
    setText('projection-meta', 'No projection data.');
    return;
  }

  // Determine value range for colour mapping.
  const vals = points.map(p => p.value);
  const vMin = Math.min(...vals);
  const vMax = Math.max(...vals);
  const range = vMax - vMin || 1;

  // Spatial range for x,y,z (first three dims).
  const xs = points.map(p => p.x);
  const ys = points.map(p => p.y);
  const zs = points.map(p => p.z);
  const xMin = Math.min(...xs), xMax = Math.max(...xs);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const zMin = Math.min(...zs), zMax = Math.max(...zs);

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const scale = Math.min(canvas.width, canvas.height) * 0.35 / Math.max(xMax - xMin, yMax - yMin, zMax - zMin, 1);

  // Draw points: x,y as visible axes, z as depth (size), d4/d5 carried as data.
  for (const p of points) {
    const nx = (p.x - xMin) / Math.max(xMax - xMin, 1);
    const ny = (p.y - yMin) / Math.max(yMax - yMin, 1);
    const nz = (p.z - zMin) / Math.max(zMax - zMin, 1);
    const valN = (p.value - vMin) / range;

    // Isometric-ish projection: x,y visible, z shifts vertically.
    const px = cx + (nx - 0.5) * canvas.width * 0.8;
    const py = cy + (ny - 0.5) * canvas.height * 0.7 - nz * scale * 1.5;

    const size = 1.5 + valN * 4 + (p.is_input || p.is_output ? 2 : 0);
    const hue = 210 - valN * 195;
    const light = 20 + valN * 50;

    ctx.beginPath();
    ctx.arc(px, py, size, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
    ctx.fill();

    // Highlight input/output cells.
    if (p.is_input || p.is_output) {
      ctx.strokeStyle = p.is_input ? '#40e0a8' : '#f0a840';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(px, py, size + 2, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  // Legend for d4/d5 (carried as filter attributes, not visualised here).
  ctx.fillStyle = '#8899bb';
  ctx.font = '11px monospace';
  ctx.fillText('X,Y visible · Z=depth · D4/D5 in point data (filter TBD)', 10, canvas.height - 10);
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
    // queue_depth is part of controller telemetry, surfaced via /api/control state;
    // here it is not present in /api/status.system, so show "—" not fake 0.
    setText('metric-queue', formatNumber(system.queue_depth));

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
  // Fetch the dynamic Alpha.5 release-gate status from the backend.
  // The browser NEVER infers scientific completion — the gate truth is
  // built by the backend GateStatusBuilder from real evidence.
  let data = null;
  try {
    const r = await fetch('/api/gate/status', { cache: 'no-store' });
    if (r.ok) data = await r.json();
  } catch {
    data = null;
  }

  if (!data) {
    // Fallback: show unavailable message
    const overallEl = $('gate-overall');
    if (overallEl) {
      overallEl.textContent = 'unavailable';
      overallEl.className = 'gate-badge gate-failed';
    }
    return;
  }

  // Overall badge
  const overallEl = $('gate-overall');
  if (overallEl) {
    overallEl.textContent = data.overall || 'pending';
    overallEl.className = `gate-badge gate-${data.overall || 'pending'}`;
  }

  // Live Runtime Profile
  if (data.live_runtime) {
    renderLiveRuntime(data.live_runtime);
  }

  // Gate A / B / C criteria tables
  if (data.gate_a && data.gate_a.items) {
    renderGateCriteria('gate-a-list', data.gate_a.items);
  }
  if (data.gate_b && data.gate_b.items) {
    renderGateCriteria('gate-b-list', data.gate_b.items);
  }
  if (data.gate_c && data.gate_c.items) {
    renderGateCriteria('gate-c-list', data.gate_c.items);
  }
}

// ----------------------------------------------------------------
// Render helpers for the dynamic gate
// ----------------------------------------------------------------

const GATE_STATUS_ICON = {
  passed: '✅',
  pending: '⏳',
  blocked: '🚫',
  stale: '🔄',
  failed: '❌',
};

const LIVE_STATUS_ICON = {
  active: '✅',
  disabled: '⊘',
  unavailable: '—',
  error: '❌',
};

function renderLiveRuntime(items) {
  const container = $('gate-live-list');
  if (!container) return;
  container.innerHTML = '';
  for (const item of items) {
    const ls = item.live_status || 'unavailable';
    const icon = LIVE_STATUS_ICON[ls] || '—';
    const div = document.createElement('div');
    div.className = `gate-live-item live-${ls}`;
    div.innerHTML = `
      <span class="gate-live-icon">${icon}</span>
      <div class="gate-live-label">
        <strong>${item.name}</strong>
        <span class="gate-live-msg">${item.message || ''}</span>
      </div>
    `;
    container.appendChild(div);
  }
}

function renderGateCriteria(containerId, items) {
  const container = $(containerId);
  if (!container) return;
  container.innerHTML = '';

  // Table header
  const header = document.createElement('div');
  header.className = 'gate-row gate-row-header';
  header.innerHTML = `
    <span class="gate-col-criterion">Criterion</span>
    <span class="gate-col-live">Live</span>
    <span class="gate-col-maturity">Maturity</span>
    <span class="gate-col-result">Gate</span>
  `;
  container.appendChild(header);

  for (const item of items) {
    const status = item.status || 'pending';
    const maturity = item.maturity || 'implemented';
    const live = item.live_status || null;
    const icon = GATE_STATUS_ICON[status] || '…';
    const liveIcon = live ? (LIVE_STATUS_ICON[live] || '—') : 'n/a';

    const row = document.createElement('div');
    row.className = `gate-row gate-row-${status}`;
    row.innerHTML = `
      <span class="gate-col-criterion" title="${item.id || ''}">
        <strong>${item.label}</strong>
        <span class="gate-col-msg">${item.message || ''}</span>
      </span>
      <span class="gate-col-live live-${live || 'na'}">${liveIcon}</span>
      <span class="gate-col-maturity maturity-${maturity}">${maturity.toUpperCase()}</span>
      <span class="gate-col-result gate-${status}">${icon} ${status}</span>
    `;
    container.appendChild(row);
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
      { label: 'Self-Organization', icon: '🧬', check: async () => { try { const r = await fetch('/api/gate/status'); const d = await r.json(); const struct = (d.live_runtime || []).find(i => i.key === 'structural'); const s = struct?.live_status; return s === 'active' ? 'passed' : s === 'disabled' ? 'disabled' : s === 'error' ? 'failed' : s === 'unavailable' ? 'unavailable' : 'unknown'; } catch { return false; } }},
      { label: 'Proposals', icon: '📋', check: async () => { try { const r = await fetch('/api/structural/proposals'); return r.ok ? 'passed' : false; } catch { return false; } }},
      { label: 'Homeostasis', icon: '⚖️', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); const e = d.homeostasis?.enabled; return e === true ? 'passed' : e === false ? 'disabled' : 'unknown'; } catch { return false; } }},
    ],
    'v0.6 (Skalierung)': [
      { label: 'Large Network', icon: '🌐', check: async () => { try { const r = await fetch('/api/status'); const d = await r.json(); return (d.system?.neurons || 0) > 100 ? 'passed' : 'pending'; } catch { return false; } }},
      { label: 'Performance', icon: '⚡', check: async () => { try { const r = await fetch('/api/status'); return r.ok ? 'passed' : false; } catch { return false; } }},
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
        if (ok === 'passed') { status = 'passed'; icon = '✅'; }
        else if (ok === 'disabled') { status = 'disabled'; icon = '⊘'; }
        else if (ok === 'unavailable') { status = 'unavailable'; icon = '⚠'; }
        else if (ok === 'pending') { status = 'pending'; icon = '⏳'; }
        else if (ok === 'unknown') { status = 'unknown'; icon = '？'; }
        else if (ok === true) { status = 'passed'; icon = '✅'; }
        else { status = 'failed'; icon = '❌'; }
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
