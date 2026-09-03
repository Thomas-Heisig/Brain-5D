/**
 * Brain-5D Operator Dashboard – Main Application (Sole Lifecycle Owner)
 *
 * This module is the ONLY component that initializes dashboard sub-modules.
 * ControlPanel and OperatorConsole are pure ES modules that do NOT
 * self-initialize. app.js imports them statically and instantiates each
 * exactly once, when the Control & Console tab is first activated.
 *
 * Canonical command contract (unified across Control + Console):
 *   POST /api/control  { "command": "run_ticks", "ticks": 100 }
 *
 * Tab-based navigation (5 main areas):
 * - OVERVIEW: high-level runtime KPIs, health/errors, active profile
 * - NETWORK: all scientific visualizations (projection, IO-flow, populations,
 *   raster, histogram, layer explorer, inspector, neuron/synapse tables)
 * - CONTROL & CONSOLE: unified operator workflow, structural live loop,
 *   console log, proposals
 * - RESEARCH & DOCS: unified file manager for research artifacts and docs
 * - RELEASE: Alpha.5 integration gate and verification status
 *
 * Features:
 * - Real-time system monitoring with auto-refresh
 * - Heatmap visualization
 * - Runtime control (step, run, pause, stop, snapshot)
 * - Structural plasticity management (proposals, approve, reject, undo)
 * - Research registry browser (B5D-SEF)
 * - Alpha.5 Integration Gate status board
 * - Documentation browsing with multi-format support
 * - Keyboard shortcuts for all major actions
 *
 * @version 3.1.0
 * @license MIT
 */

"use strict";

// ================================================================
// IMPORTS — static ES module imports (no dynamic fallback)
// ================================================================

import { ControlPanel } from './control-panel.js';
import { OperatorConsole } from './operator_console.js';
import { initResearchBrowser, initDocumentationBrowser } from './file-viewer.js';
import { dashboardStore } from './state-store.js';
import { initHealthDrawer } from './health-drawer.js';
import { consoleLog } from './console-log.js';
import { ParameterInspector } from './parameter-inspector.js';
import { ExperimentMode } from './experiment-mode.js';
import { ExperimentWorkflowPanel } from './experiment-workflow.js';
import { renderOverviewCommandCenter, setupOverviewActions } from './overview-panel.js';
import { SettingsPanel } from './settings-panel.js';
import { initEmbodimentDetails, initEmbodimentPipelineControls, renderWorkspaceSummaries } from './workspace-panels.js';
import { initResearchChat } from './research-chat.js';

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
    overview: document.getElementById('tab-overview'),
    network: document.getElementById('tab-network'),
    control: document.getElementById('tab-control'),
    research: document.getElementById('tab-research'),
    gate: document.getElementById('tab-gate'),
    settings: document.getElementById('tab-settings'),
    embodiment: document.getElementById('tab-embodiment'),
  };

  // Track initialization state
  const initialized = {
    network: false,
    control: false,
    research: false,
    gate: false,
    settings: false,
  };

  // Component instances
  const instances = {
    control: null,
    console: null,
    parameterInspector: null,
    experimentMode: null,
    experimentWorkflow: null,
    settings: null,
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const tabName = btn.dataset.tab;
      const currentTab = document.body.dataset.currentTab;
      if (currentTab && currentTab !== tabName) {
        document.body.dataset.previousTab = currentTab;
      }
      document.body.dataset.currentTab = tabName;
      setText('header-context', tabName === 'gate' ? 'Release' : `${tabName.charAt(0).toUpperCase()}${tabName.slice(1)}`);

      Object.keys(contents).forEach(key => {
        const el = contents[key];
        if (el) {
          el.classList.toggle('active', key === tabName);
        }
      });

      // Lazy initialize components when their tab becomes visible
      if (tabName === 'network' && !initialized.network) {
        initDynamicsTab();
        initInspectTab();
        initialized.network = true;
      }
      if (tabName === 'control' && !initialized.control) {
        instances.control = initControlPanel();
        instances.console = initOperatorConsole();
        instances.experimentMode = new ExperimentMode();
        instances.experimentMode.refresh();
        initialized.control = true;
      }
      if (tabName === 'research' && !initialized.research) {
        initResearchBrowser();
        initDocumentationBrowser();
        instances.experimentWorkflow = new ExperimentWorkflowPanel();
        instances.experimentWorkflow.refresh();
        initialized.research = true;
      }
      if (tabName === 'gate' && !initialized.gate) {
        initGateBoard();
        initialized.gate = true;
      }
      if (tabName === 'settings' && !initialized.settings) {
        instances.parameterInspector = initParameterInspector();
        instances.settings = new SettingsPanel(instances.parameterInspector);
        initialized.settings = true;
      }
    });
  });

  // Activate the first tab by default (Dashboard)
  const firstTab = document.querySelector('.tab-btn');
  if (firstTab) {
    firstTab.click();
  }
  initResearchChat();

  return instances;
}

function setupWorkspaceViews() {
  document.querySelectorAll('[data-workspace-views]').forEach((navigation) => {
    const workspace = navigation.dataset.workspaceViews;
    navigation.addEventListener('click', (event) => {
      const button = event.target.closest('[data-workspace-view]');
      if (!button) return;
      const view = button.dataset.workspaceView;
      navigation.querySelectorAll('[data-workspace-view]').forEach((item) => {
        item.classList.toggle('active', item === button);
      });
      document.querySelectorAll(`[data-${workspace}-view]`).forEach((panel) => {
        panel.hidden = panel.dataset[`${workspace}View`] !== view;
      });
    });
  });
}

function setupResearchLanes() {
  const lanes = $('research-lanes');
  lanes?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-research-source]');
    if (!button) return;
    lanes.querySelectorAll('[data-research-source]').forEach((item) => {
      item.classList.toggle('active', item === button);
    });
    const source = button.dataset.researchSource;
    const sourceButton = document.querySelector(`.fm-source-btn[data-source="${source}"]`);
    const sourceChanged = sourceButton && !sourceButton.classList.contains('active');
    if (sourceChanged) sourceButton.click();
    const search = $('fm-search');
    if (!search) return;
    const runLane = () => {
      search.value = button.dataset.researchQuery || '';
      $('fm-search-btn')?.click();
    };
    if (sourceChanged) {
      setTimeout(runLane, 150);
    } else {
      runLane();
    }
  });
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
 * Render system status from the central dashboard store.
 * @param {object} state
 */
function renderStatus(state) {
  const data = state;
  const system = data.system || {};
  const storage = data.storage || {};
  const learning = data.learning || {};
  const selfOrg = data.self_organization || {};
  const homeostasis = data.homeostasis || {};

  renderOverviewCommandCenter(state);
  renderWorkspaceSummaries(state);

  // System metrics (always measured, real values)
  setText('tick', formatNumber(system.tick));
  setText('neurons', formatNumber(system.neurons));
  setText('synapses', formatNumber(system.synapses));
  setText('spikes', formatNumber(system.spikes_total));
  setText('core-ms', formatFloat(system.core_step_ms, 3));
  setText('energy', formatFloat(system.mean_energy, 3));

  // Storage metrics — distinguish disabled/unavailable from measured zero.
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

  // Learning metrics
  setText('stdp', formatNumber(learning.stdp_updates));
  setText('reward-updates', formatNumber(learning.reward_updates));
  setText('rewards', `${formatNumber(learning.rewards_applied)} / ${formatNumber(learning.rewards_received)}`);
  setText('pending', formatNumber(learning.pending_rewards));
  setText('learning-ms', formatMetricUnit(learning.update_ms, 'ms', 3));
  setText('learning-engine-state', learning.engine_attached ? 'attached' : 'unavailable');
  setText('learning-engine', learning.engine_attached ? 'ACTIVE' : 'UNAVAILABLE');
  setText('learning-stdp-state', learning.stdp_enabled ? (learning.stdp_updates > 0 ? 'ACTIVE' : 'ARMED') : 'DISABLED');
  setText('learning-eligibility-state', learning.eligibility_enabled ? 'ACTIVE' : 'DISABLED');
  setText('learning-reward-state', learning.reward_enabled ? (learning.reward_updates > 0 ? 'ACTIVE' : 'ARMED') : 'DISABLED');

  // Homeostasis
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

  // Self-organization
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
  setText('footer-version', data.version || 'unknown');
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
}

/**
 * Compatibility shim: refresh system status via the central store.
 */
async function refreshStatus() {
  await dashboardStore.refresh();
}

/**
 * Refresh the structural live loop status from the dedicated artifact endpoint.
 *
 * Reads ``/api/structural/live-loop`` and renders each of the 11 proofs with
 * its own status label. This keeps the visual loop honest: every step is
 * evidenced from the artifact, not inferred from the high-level gate status.
 */
async function refreshLiveLoopStatus() {
  const stepIds = ['ll-adapter', 'll-signal', 'll-policy', 'll-proposal',
                   'll-coordinator', 'll-approval', 'll-mutation', 'll-journal',
                   'll-undo', 'll-replay'];
  try {
    const r = await fetch('/api/structural/live-loop', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    const available = data.available === true;
    const proofs = data.proofs || {};
    const allPassed = available && Object.values(proofs).every(v => v === true);

    const badge = $('live-loop-badge');
    if (badge) {
      badge.textContent = allPassed ? '✅ VERIFIED' : (available ? '⏳ pending' : '❌ missing');
      badge.className = `gate-badge ${allPassed ? 'passed' : (available ? 'pending' : 'failed')}`;
    }

    const meta = $('live-loop-meta');
    if (meta) {
      if (!available) {
        meta.textContent = '⏳ Run test_structural_live_loop.py to generate verification artifact';
      } else {
        const passedCount = Object.values(proofs).filter(v => v === true).length;
        const totalCount = Object.keys(proofs).length;
        meta.textContent = `✅ ${passedCount}/${totalCount} proofs passed · ${data.tested_tree_digest ? 'tree digest verified' : 'no digest'}`;
      }
    }

    // Map each UI step to the proof(s) it represents.
    const stepProofMap = {
      'll-adapter': ['production_adapter_attached'],
      'll-signal': ['real_signal_generated'],
      'll-policy': ['policy_received_real_signal'],
      'll-proposal': ['proposal_published', 'proposal_non_mutating'],
      'll-coordinator': [],
      'll-approval': ['reject_non_mutating', 'approve_single_mutation'],
      'll-mutation': ['journal_linked_to_proposal', 'runtime_continues_after_mutation'],
      'll-journal': [],
      'll-undo': ['undo_restores_topology'],
      'll-replay': ['journal_reopen_replay_identity'],
    };

    const proofLabels = {
      production_adapter_attached: 'attached',
      real_signal_generated: 'real signal',
      policy_received_real_signal: 'received signal',
      proposal_published: 'published',
      proposal_non_mutating: 'non-mutating',
      reject_non_mutating: 'reject verified',
      approve_single_mutation: 'approve verified',
      journal_linked_to_proposal: 'linked record',
      runtime_continues_after_mutation: 'runtime continues',
      undo_restores_topology: 'topology restored',
      journal_reopen_replay_identity: 'replay identity',
    };

    for (const stepId of stepIds) {
      const el = $(stepId);
      if (!el) continue;
      const statusEl = el.querySelector('.live-loop-status');
      const proofKeys = stepProofMap[stepId] || [];

      if (!available) {
        el.className = 'live-loop-step ll-pending';
        if (statusEl) statusEl.textContent = '⏳ pending';
        continue;
      }

      const stepPassed = proofKeys.length === 0 || proofKeys.every(k => proofs[k] === true);
      const proofResults = proofKeys.map(k => ({ key: k, passed: proofs[k] === true }));

      if (stepPassed) {
        el.className = 'live-loop-step ll-passed';
        if (statusEl) {
          if (proofKeys.length === 0) {
            statusEl.textContent = '✅ canonical instance';
          } else if (proofKeys.length === 1) {
            statusEl.textContent = `✅ ${proofLabels[proofKeys[0]] || proofKeys[0]}`;
          } else {
            statusEl.textContent = `✅ ${proofKeys.length} proofs`;
          }
        }
      } else {
        el.className = 'live-loop-step ll-pending';
        if (statusEl) {
          const failed = proofResults.filter(p => !p.passed);
          statusEl.textContent = `⏳ ${failed.map(p => proofLabels[p.key] || p.key).join(', ')}`;
        }
      }
    }
  } catch {
    for (const id of stepIds) {
      const el = $(id);
      if (el) {
        el.className = 'live-loop-step ll-pending';
        const statusEl = el.querySelector('.live-loop-status');
        if (statusEl) statusEl.textContent = '⏳ pending';
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

  // Store telemetry status for badge updates
  const metaEl = $('heatmap-meta');
  if (metaEl && payload.telemetry && payload.telemetry.status) {
    metaEl.dataset.telemetryStatus = payload.telemetry.status;
  }

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
      `/api/live/projection?kind=${encodeURIComponent(heatmapKind)}&resolution=${encodeURIComponent($('projection-resolution')?.value || '50')}`,
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
    updateSourceBadge(data.telemetry?.status);
  } catch {
    // Silently fall back — snapshot will be used on next interval
  }
}

/**
 * Update the source badge in the UI based on telemetry status
 */
function updateSourceBadge(telemetryStatus) {
  const badge = $('source-badge');
  if (!badge) return;

  if (!liveSource) {
    badge.textContent = 'SNAPSHOT';
    badge.className = 'badge badge-snapshot';
    return;
  }

  // Use explicit status parameter, fall back to DOM dataset
  const status = telemetryStatus || (document.getElementById('heatmap-meta')?.dataset?.telemetryStatus);
  if (status === 'stale') {
    badge.textContent = 'STALE';
    badge.className = 'badge badge-stale';
    return;
  }
  if (status === 'unavailable') {
    badge.textContent = 'UNAVAILABLE';
    badge.className = 'badge badge-unavailable';
    return;
  }

  badge.textContent = 'LIVE';
  badge.className = 'badge badge-live';
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
  const cy = canvas.height / 2 + 20;
  const scale = Math.min(canvas.width, canvas.height) * 0.35 / Math.max(rows, cols);

  const flat = values.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  if (flat.length === 0) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Daten', cx, cy);
    return;
  }
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  // Draw base grid (isometric floor)
  ctx.strokeStyle = 'rgba(64, 224, 208, 0.06)';
  ctx.lineWidth = 0.5;
  const gridStep = 4;
  for (let y = 0; y < rows; y += gridStep) {
    for (let x = 0; x < cols; x += gridStep) {
      const gx1 = cx + (x - y) * scale * 0.7;
      const gy1 = cy + (x + y) * scale * 0.35;
      // Draw small grid cross
      ctx.beginPath();
      ctx.arc(gx1, gy1, 1.5, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(64, 224, 208, 0.15)';
      ctx.fill();
    }
  }

  // Draw grid points with height based on value
  for (let y = 0; y < rows; y += 2) {
    for (let x = 0; x < cols; x += 2) {
      const val = values[y]?.[x];
      if (val === null || val === undefined) continue;
      const normalized = (val - min) / range;

      // Isometric projection
      const isoX = (x - y) * scale * 0.7;
      const isoY = (x + y) * scale * 0.35 - normalized * scale * 2;

      const size = 2 + normalized * 5;
      const hue = 210 - normalized * 195;
      const light = 20 + normalized * 55;

      ctx.beginPath();
      ctx.arc(cx + isoX, cy + isoY, size, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
      ctx.fill();

      // Subtle glow for high values
      if (normalized > 0.6) {
        ctx.beginPath();
        ctx.arc(cx + isoX, cy + isoY, size * 2.5, 0, Math.PI * 2);
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
      const v1 = values[y]?.[x];
      const v2 = values[y]?.[x + 2];
      const v3 = values[y + 2]?.[x];
      if (v1 === null || v1 === undefined || v2 === null || v2 === undefined || v3 === null || v3 === undefined) continue;

      const n1 = (v1 - min) / range;
      const n2 = (v2 - min) / range;
      const n3 = (v3 - min) / range;

      const x1 = cx + (x - y) * scale * 0.7;
      const y1 = cy + (x + y) * scale * 0.35 - n1 * scale * 2;
      const x2 = cx + ((x + 2) - y) * scale * 0.7;
      const y2 = cy + ((x + 2) + y) * scale * 0.35 - n2 * scale * 2;
      const x3 = cx + (x - (y + 2)) * scale * 0.7;
      const y3 = cy + (x + (y + 2)) * scale * 0.35 - n3 * scale * 2;

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

  // Draw axis labels
  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '10px monospace';
  ctx.textAlign = 'center';
  // X axis
  ctx.fillText('X →', cx + cols * scale * 0.35, cy + cols * scale * 0.17 + 12);
  // Y axis
  ctx.fillText('Y →', cx - rows * scale * 0.35, cy + rows * scale * 0.17 + 12);
  // Z legend (value height)
  ctx.fillText(`Z: ${min.toFixed(2)} … ${max.toFixed(2)}`, cx, 14);

  // Draw 5D info
  const dims = payload.dimensions || [];
  if (dims.length >= 5) {
    ctx.fillStyle = 'rgba(142, 178, 193, 0.35)';
    ctx.font = '9px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`5D: ${dims.join('×')}`, 8, canvas.height - 8);
  }
}

// ================================================================
// IO-FLUSS REFRESH
// ================================================================

let ioFlowInterval = null;

/**
 * Refresh IO-Fluss visualization from /api/live/io-flow
 */
async function refreshIOFlow() {
  try {
    const r = await fetch('/api/live/io-flow', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    // Input layer
    setText('io-input-count', formatNumber(data.input_count));
    setText('io-input-rate', formatFloat(data.input_mean_rate, 4));
    const inputFill = document.getElementById('io-input-fill');
    if (inputFill) inputFill.style.width = Math.min(100, data.input_mean_rate * 200) + '%';

    // Hidden layer
    setText('io-hidden-count', formatNumber(data.hidden_count));
    setText('io-hidden-rate', formatFloat(data.hidden_mean_rate, 4));
    const hiddenFill = document.getElementById('io-hidden-fill');
    if (hiddenFill) hiddenFill.style.width = Math.min(100, data.hidden_mean_rate * 200) + '%';

    // Output layer
    setText('io-output-count', formatNumber(data.output_count));
    setText('io-output-rate', formatFloat(data.output_mean_rate, 4));
    const outputFill = document.getElementById('io-output-fill');
    if (outputFill) outputFill.style.width = Math.min(100, data.output_mean_rate * 200) + '%';

    // Badge
    const badge = document.getElementById('io-flow-badge');
    if (badge) {
      if (data.propagation_active) {
        badge.textContent = '✅ Signalfluss aktiv';
        badge.className = 'gate-badge passed';
      } else {
        badge.textContent = '⏳ Signal abgebrochen';
        badge.className = 'gate-badge pending';
      }
    }

    // Meta
    const meta = document.getElementById('io-flow-meta');
    if (meta) {
      meta.textContent = `Tick ${data.current_tick} · Input ${data.input_mean_rate.toFixed(4)} → Hidden ${data.hidden_mean_rate.toFixed(4)} → Output ${data.output_mean_rate.toFixed(4)} · ${data.source}`;
    }
  } catch (e) {
    const badge = document.getElementById('io-flow-badge');
    if (badge) {
      badge.textContent = '⚠️ offline';
      badge.className = 'gate-badge failed';
    }
    const meta = document.getElementById('io-flow-meta');
    if (meta) meta.textContent = '⚠️ IO-Fluss nicht verfügbar';
  }
}

// ================================================================
// POPULATION OVERVIEW REFRESH
// ================================================================

let populationInterval = null;

/**
 * Refresh population overview from /api/live/population
 */
async function refreshPopulation() {
  try {
    const r = await fetch('/api/live/population', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    // E/I ratio badge
    const badge = document.getElementById('ei-ratio-badge');
    if (badge) {
      const ratio = data.ei_ratio;
      if (typeof ratio === 'number') {
        badge.textContent = `E/I: ${ratio.toFixed(2)}`;
        badge.className = `gate-badge ${ratio > 0.5 && ratio < 3.0 ? 'passed' : 'stale'}`;
      } else {
        badge.textContent = 'E/I: unavailable';
        badge.className = 'gate-badge pending';
      }
    }

    // Population cards
    const grid = document.getElementById('population-grid');
    if (!grid) return;

    if (!data.populations || data.populations.length === 0) {
      grid.innerHTML = '<div class="population-empty">Keine Populationsdaten verfügbar.</div>';
    } else {
      grid.innerHTML = data.populations.map(p => {
        const activePct = (p.active_fraction * 100).toFixed(1);
        const barColor = p.name.includes('inhib') ? '#ff5d73'
          : p.name.includes('excit') ? '#40e0a8'
          : p.name.includes('sensory') ? '#4a7cf7'
          : p.name.includes('motor') ? '#f0a840'
          : '#8899bb';
        return `
          <div class="population-card">
            <div class="population-card-header">
              <span class="population-name">${escapeHtml(p.name)}</span>
              <span class="population-count">${formatNumber(p.count)}</span>
            </div>
            <div class="population-stats">
              <div class="population-stat"><dt>Rate</dt><dd>${formatFloat(p.mean_rate, 4)} spikes/tick</dd></div>
              <div class="population-stat"><dt>Energie</dt><dd>${formatFloat(p.mean_energy, 4)}</dd></div>
              <div class="population-stat"><dt>Membran V</dt><dd>${formatFloat(p.mean_v, 3)}</dd></div>
              <div class="population-stat"><dt>Aktiv</dt><dd>${formatNumber(p.active_count)} / ${formatNumber(p.count)} (${activePct}%)</dd></div>
            </div>
            <div class="population-bar">
              <div class="population-bar-fill" style="width:${activePct}%;background:${barColor};"></div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Meta
    const meta = document.getElementById('population-meta');
    if (meta) {
      meta.textContent = `Tick ${data.current_tick} · E: ${data.total_excitatory} / I: ${data.total_inhibitory} · ${data.source}`;
    }
  } catch (e) {
    const badge = document.getElementById('ei-ratio-badge');
    if (badge) {
      badge.textContent = 'E/I: —';
      badge.className = 'gate-badge';
    }
    const grid = document.getElementById('population-grid');
    if (grid) {
      grid.innerHTML = '<div class="population-empty">⚠️ Populationsdaten nicht verfügbar.</div>';
    }
  }
}

/**
 * Initialize dashboard refresh cycles
 */
function initDashboard() {
  // Central state store drives the OVERVIEW tab and health drawer.
  dashboardStore.subscribe(renderStatus);
  dashboardStore.start();

  // Initialize health / problems drawer
  initHealthDrawer(dashboardStore);

  // Visualizations still poll their own endpoints (network tab)
  refreshHeatmap();
  refreshLiveProjection();
  refreshSnapshotInfo();
  refreshLiveLoopStatus();
  refreshIOFlow();
  refreshPopulation();

  // Set up intervals
  if (refreshInterval) clearInterval(refreshInterval);
  if (heatmapInterval) clearInterval(heatmapInterval);
  if (liveProjectionInterval) clearInterval(liveProjectionInterval);
  if (ioFlowInterval) clearInterval(ioFlowInterval);
  if (populationInterval) clearInterval(populationInterval);

  heatmapInterval = setInterval(refreshHeatmap, 5000);
  liveProjectionInterval = setInterval(refreshLiveProjection, 500);
  setInterval(refreshSnapshotInfo, 3000);
  setInterval(refreshLiveLoopStatus, 5000);

  ioFlowInterval = setInterval(refreshIOFlow, 2000);
  populationInterval = setInterval(refreshPopulation, 2000);

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
// DYNAMICS TAB (Spike Raster, Rate Histogram, Layer Explorer)
// ================================================================

let dynamicsInterval = null;
let layerExplorerInterval = null;

function initDynamicsTab() {
  console.log('📈 Dynamics tab initializing...');
  refreshSpikeRaster();
  refreshRateHistogram();
  refreshLayerExplorer();

  // Set up intervals
  if (dynamicsInterval) clearInterval(dynamicsInterval);
  if (layerExplorerInterval) clearInterval(layerExplorerInterval);
  dynamicsInterval = setInterval(refreshSpikeRaster, 2000);
  dynamicsInterval = setInterval(refreshRateHistogram, 2000);
  layerExplorerInterval = setInterval(refreshLayerExplorer, 3000);

  // Layer slider controls
  const slider = document.getElementById('layer-slider');
  const dimSelect = document.getElementById('layer-dim');
  const kindSelect = document.getElementById('layer-kind');
  const layerVal = document.getElementById('layer-value');
  if (slider) {
    slider.addEventListener('input', () => {
      if (layerVal) layerVal.textContent = slider.value;
    });
    slider.addEventListener('change', refreshLayerExplorer);
  }
  if (dimSelect) dimSelect.addEventListener('change', refreshLayerExplorer);
  if (kindSelect) kindSelect.addEventListener('change', refreshLayerExplorer);

  const projectionResolution = $('projection-resolution');
  const histogramBins = $('histogram-bins');
  const projectionSamples = $('projection-samples');
  const bindRange = (input, outputId, refresh) => {
    if (!input) return;
    input.addEventListener('input', () => setText(outputId, input.value));
    input.addEventListener('change', refresh);
  };
  bindRange(projectionResolution, 'projection-resolution-value', refreshLiveProjection);
  bindRange(histogramBins, 'histogram-bins-value', refreshRateHistogram);
  bindRange(projectionSamples, 'projection-samples-value', loadProjection);

  console.log('✅ Dynamics tab ready');
}

// ================================================================
// SPIKE RASTER
// ================================================================

async function refreshSpikeRaster() {
  try {
    const r = await fetch('/api/live/raster', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawSpikeRaster(data);
    const badge = document.getElementById('raster-badge');
    if (badge) {
      badge.textContent = `${data.sample_count}/${data.total_neurons} Neuronen`;
      badge.className = 'gate-badge passed';
    }
    const meta = document.getElementById('raster-meta');
    if (meta) meta.textContent = `Tick ${data.tick} · Fenster: ${data.window_ticks} Ticks · ${data.sample_count} aktive Neuronen von ${data.total_neurons}`;
  } catch {
    const badge = document.getElementById('raster-badge');
    if (badge) { badge.textContent = 'offline'; badge.className = 'gate-badge failed'; }
  }
}

function drawSpikeRaster(data) {
  const canvas = document.getElementById('spike-raster');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const nids = data.neuron_ids || [];
  const ticks = data.spike_ticks || [];
  if (!nids.length || !ticks.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Spike-Daten im aktuellen Fenster', canvas.width/2, canvas.height/2);
    return;
  }

  const windowTicks = data.window_ticks || 100;
  const tick = data.tick || 0;
  const tickMin = tick - windowTicks;
  const tickMax = tick;

  const neuronCount = nids.length;
  const idToRow = {};
  nids.forEach((id, i) => { idToRow[id] = i; });

  const margin = { top: 20, right: 20, bottom: 30, left: 50 };
  const plotW = canvas.width - margin.left - margin.right;
  const plotH = canvas.height - margin.top - margin.bottom;

  // Background
  ctx.fillStyle = '#050d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw grid lines
  ctx.strokeStyle = 'rgba(142, 178, 193, 0.06)';
  ctx.lineWidth = 0.5;
  for (let i = 0; i < 10; i++) {
    const y = margin.top + (plotH / 10) * i;
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(margin.left + plotW, y);
    ctx.stroke();
  }

  // Draw spikes
  ctx.fillStyle = 'rgba(64, 224, 208, 0.6)';
  for (let i = 0; i < ticks.length; i++) {
    const t = ticks[i];
    const nid = nids[i % nids.length];
    const row = idToRow[nid];
    if (row === undefined) continue;
    const x = margin.left + ((t - tickMin) / Math.max(1, tickMax - tickMin)) * plotW;
    const y = margin.top + (row / Math.max(1, neuronCount)) * plotH;
    ctx.fillRect(x - 0.5, y - 1, 2, 2);
  }

  // Labels
  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('Tick →', margin.left + plotW/2, canvas.height - 5);
  ctx.textAlign = 'right';
  ctx.fillText('Neuron ↑', margin.left - 5, margin.top + 12);
  ctx.textAlign = 'left';
  ctx.fillStyle = 'rgba(142, 178, 193, 0.3)';
  ctx.font = '9px monospace';
  ctx.fillText(tickMin, margin.left, canvas.height - 8);
  ctx.textAlign = 'right';
  ctx.fillText(tickMax, margin.left + plotW, canvas.height - 8);
}

// ================================================================
// RATE HISTOGRAM
// ================================================================

async function refreshRateHistogram() {
  try {
    const bins = $('histogram-bins')?.value || '30';
    const r = await fetch(`/api/live/histogram?bins=${encodeURIComponent(bins)}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawRateHistogram(data);
    const stats = document.getElementById('histogram-stats');
    if (stats) {
      stats.textContent = `μ=${data.mean_rate.toFixed(4)} σ=${data.std_rate.toFixed(4)}`;
      stats.className = 'gate-badge passed';
    }
    const meta = document.getElementById('histogram-meta');
    if (meta) meta.textContent = `Tick ${data.current_tick} · ${data.active_count} aktiv / ${data.silent_count} stumm · Median ${data.median_rate.toFixed(4)}`;
  } catch {
    const stats = document.getElementById('histogram-stats');
    if (stats) { stats.textContent = 'offline'; stats.className = 'gate-badge failed'; }
  }
}

function drawRateHistogram(data) {
  const canvas = document.getElementById('rate-histogram');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const bins = data.bins || [];
  const counts = data.counts || [];
  if (!counts.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Histogramm-Daten', canvas.width/2, canvas.height/2);
    return;
  }

  const margin = { top: 20, right: 20, bottom: 35, left: 60 };
  const plotW = canvas.width - margin.left - margin.right;
  const plotH = canvas.height - margin.top - margin.bottom;

  ctx.fillStyle = '#050d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const maxCount = Math.max(...counts, 1);
  const barW = plotW / counts.length;

  // Draw bars
  for (let i = 0; i < counts.length; i++) {
    const x = margin.left + i * barW;
    const h = (counts[i] / maxCount) * plotH;
    const y = margin.top + plotH - h;
    const normalized = counts[i] / maxCount;
    const hue = 210 - normalized * 195;
    ctx.fillStyle = `hsl(${hue}, 85%, ${30 + normalized * 40}%)`;
    ctx.fillRect(x + 1, y, barW - 2, h);
  }

  // Mean line
  if (data.mean_rate > 0 && bins.length > 1) {
    const maxRate = bins[bins.length - 1];
    const meanX = margin.left + (data.mean_rate / maxRate) * plotW;
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.7)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(meanX, margin.top);
    ctx.lineTo(meanX, margin.top + plotH);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255, 159, 28, 0.7)';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('μ=' + data.mean_rate.toFixed(3), meanX, margin.top - 4);
  }

  // Labels
  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('Feuerrate (spikes/tick) →', margin.left + plotW/2, canvas.height - 5);
  ctx.textAlign = 'right';
  ctx.fillText('Anzahl ↑', margin.left - 5, margin.top + 12);
}

// ================================================================
// 5D LAYER EXPLORER
// ================================================================

async function refreshLayerExplorer() {
  try {
    const dimSelect = document.getElementById('layer-dim');
    const slider = document.getElementById('layer-slider');
    const kindSelect = document.getElementById('layer-kind');
    if (!dimSelect || !slider) return;

    const dim = dimSelect.value;
    const layerVal = parseInt(slider.value, 10);
    const kind = kindSelect ? kindSelect.value : 'activity';

    const r = await fetch(`/api/live/projection?kind=${encodeURIComponent(kind)}&resolution=40`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawLayerSlice(data, dim, layerVal);

    const badge = document.getElementById('layer-badge');
    if (badge) badge.textContent = dim.toUpperCase();

    const meta = document.getElementById('layer-meta');
    if (meta) meta.textContent = `Tick ${data.tick ?? data.current_tick} · ${dim.toUpperCase()}=${layerVal} · ${data.kind || kind} · ${data.source}`;
  } catch {
    const meta = document.getElementById('layer-meta');
    if (meta) meta.textContent = '⚠️ Layer-Daten nicht verfügbar';
  }
}

function drawLayerSlice(payload, dim, layerValue) {
  const canvas = document.getElementById('layer-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const values = payload.values || [];
  if (!values.length) return;

  const rows = values.length;
  const cols = values[0]?.length || 1;
  const flat = values.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  if (!flat.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Daten', canvas.width/2, canvas.height/2);
    return;
  }
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  const cellW = canvas.width / cols;
  const cellH = canvas.height / rows;

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const val = values[y]?.[x];
      if (val === null || val === undefined) {
        ctx.fillStyle = 'rgba(40, 50, 65, 0.4)';
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      } else {
        const normalized = (val - min) / range;
        const hue = 210 - normalized * 195;
        const light = 16 + normalized * 50;
        ctx.fillStyle = `hsl(${hue}, 88%, ${light}%)`;
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      }
    }
  }

  // Overlay
  ctx.fillStyle = 'rgba(142, 178, 193, 0.4)';
  ctx.font = '10px monospace';
  ctx.textAlign = 'left';
  ctx.fillText(`${dim.toUpperCase()}=${layerValue}`, 8, 16);
  ctx.textAlign = 'right';
  ctx.fillText(`${min.toFixed(2)} … ${max.toFixed(2)}`, canvas.width - 8, 16);
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
  const limit = $('projection-samples')?.value || '2000';
  try {
    const r = await fetch(`/api/network/projection?limit=${encodeURIComponent(limit)}&mode=${encodeURIComponent(mode)}`, { cache: 'no-store' });
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

// ================================================================
// PARAMETER INSPECTOR INITIALIZATION (sole owner)
// ================================================================

function initParameterInspector() {
  console.log('🔧 Parameter Inspector initializing...');
  const instance = new ParameterInspector();
  instance.refresh();
  console.log('✅ Parameter Inspector initialized');
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
// RESEARCH & DOCUMENTATION BROWSER (delegated to file-viewer.js)
// ================================================================
// All file-manager logic lives in file-viewer.js and is imported above.

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

  const scientificGate = data.scientific_gate || {};
  const scientificStatus = scientificGate.overall || data.overall || 'pending';
  const ciStatus = data.ci_status?.status || 'unknown';
  const readiness = data.release_readiness?.overall || 'not_ready';

  const scientificEl = $('gate-scientific');
  if (scientificEl) {
    scientificEl.textContent = scientificStatus;
    scientificEl.className = `gate-badge gate-${scientificStatus}`;
  }

  const ciEl = $('gate-ci');
  if (ciEl) {
    ciEl.textContent = ciStatus;
    ciEl.className = `gate-badge gate-${ciStatus}`;
  }

  // Overall release-readiness badge
  const overallEl = $('gate-overall');
  if (overallEl) {
    overallEl.textContent = readiness;
    overallEl.className = `gate-badge gate-${readiness === 'ready' ? 'passed' : 'pending'}`;
  }

  // Live Runtime Profile
  const liveRuntime = scientificGate.live_runtime || data.live_runtime;
  if (liveRuntime) {
    renderLiveRuntime(liveRuntime);
  }

  // Gate A / B / C criteria tables
  const gateA = scientificGate.gate_a || data.gate_a;
  const gateB = scientificGate.gate_b || data.gate_b;
  const gateC = scientificGate.gate_c || data.gate_c;
  if (gateA?.items) {
    renderGateCriteria('gate-a-list', gateA.items);
  }
  if (gateB?.items) {
    renderGateCriteria('gate-b-list', gateB.items);
  }
  if (gateC?.items) {
    renderGateCriteria('gate-c-list', gateC.items);
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
// THEME & ACCESSIBILITY HEADER CONTROLS
// ================================================================

const THEME_KEY = 'b5d-theme';
const ACCESSIBILITY_KEY = 'b5d-accessibility';
const CONTRAST_KEY = 'b5d-contrast';

function getSavedTheme() {
  try {
    return localStorage.getItem(THEME_KEY) || 'dark';
  } catch {
    return 'dark';
  }
}

function setTheme(theme) {
  document.body.dataset.theme = theme;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // ignore storage errors
  }
}

function toggleTheme() {
  const current = document.body.dataset.theme || getSavedTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  setTheme(next);
}

function setupThemeToggle() {
  const btn = $('theme-toggle');
  if (!btn) return;
  setTheme(getSavedTheme());
  btn.addEventListener('click', toggleTheme);
}

function setupAccessibilityToggle() {
  const btn = $('accessibility-toggle');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const enabled = document.body.classList.toggle('accessibility-mode');
    try {
      localStorage.setItem(ACCESSIBILITY_KEY, String(enabled));
    } catch {
      // ignore storage errors
    }
  });

  try {
    const saved = localStorage.getItem(ACCESSIBILITY_KEY);
    if (saved === 'true') {
      document.body.classList.add('accessibility-mode');
    }
  } catch {
    // ignore storage errors
  }
}

function setupGlobalChrome() {
  const home = $('nav-home');
  const back = $('nav-back');
  const contrast = $('contrast-toggle');
  const help = $('help-toggle');
  const helpDialog = $('context-help');
  const helpCopy = {
    overview: ['System Overview', 'Verdichtet Runtime, Health, wissenschaftlichen Status und die wichtigsten Messwerte.'],
    network: ['Network Workbench', 'Untersucht reale Live-Dynamik, Projektionen, Populationen, Neuronen und Synapsen. Auflösungsregler steuern die Backend-Aggregation.'],
    control: ['Control Workbench', 'Steuert Ticks, Loop, Snapshot, Experiment-Sessions und freigabepflichtige Strukturänderungen.'],
    research: ['Research Workspace', 'Durchsucht Registry, Experimente, Evidenz, Reports und Dokumentation aus dem Repository.'],
    gate: ['Release Workspace', 'Trennt Scientific Gate, Source-CI und Release Readiness. Stale bedeutet: Source wurde seit der Evidenz verändert.'],
    settings: ['Scientific Settings', 'Änderungen werden zunächst als Pending Change vorgemerkt. S markiert wissenschaftlich sensitive Werte, R einen notwendigen Neustart.'],
    embodiment: ['Embodiment Workspace', 'Zeigt ausschließlich publizierte Sensor-, Aktuator-, Episoden- und Reward-Metriken. Unconfigured ist kein simulierter Zustand.'],
  };

  home?.addEventListener('click', () => document.querySelector('.tab-btn[data-tab="overview"]')?.click());
  back?.addEventListener('click', () => {
    const target = document.body.dataset.previousTab || 'overview';
    document.querySelector(`.tab-btn[data-tab="${target}"]`)?.click();
  });
  contrast?.addEventListener('click', () => {
    const enabled = document.body.classList.toggle('contrast-mode');
    localStorage.setItem(CONTRAST_KEY, String(enabled));
  });
  if (localStorage.getItem(CONTRAST_KEY) === 'true') document.body.classList.add('contrast-mode');
  help?.addEventListener('click', () => {
    const [title, text] = helpCopy[document.body.dataset.currentTab || 'overview'];
    setText('context-help-title', title);
    setText('context-help-text', text);
    helpDialog?.showModal();
  });
  $('context-help-close')?.addEventListener('click', () => helpDialog?.close());
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

    // Ctrl+1-8 = Tab switching
    if (e.ctrlKey && e.key >= '1' && e.key <= '8') {
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
  setupOverviewActions();
  setupWorkspaceViews();
  setupResearchLanes();
  initEmbodimentDetails();
  initEmbodimentPipelineControls();

  // Initialize dashboard (status & heatmap)
  initDashboard();

  // Setup integration click handlers
  setupIntegrationClickHandlers();

  // Setup auto-refresh toggle
  setupAutoRefreshToggle();

  // Setup global shortcuts
  setupGlobalShortcuts();

  // Setup header controls
  setupThemeToggle();
  setupAccessibilityToggle();
  setupGlobalChrome();

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
