/**
 * Brain-5D Dashboard — Overview Panel
 *
 * Renders the OVERVIEW tab from the central dashboard store.
 * Does NOT issue its own HTTP requests; all data arrives via store subscription.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

const $ = (id) => document.getElementById(id);

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = String(value);
}

function formatBytes(value) {
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
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString();
}

function formatFloat(value, decimals = 3) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(decimals);
}

function formatMetricUnit(value, unit, decimals = 3) {
  if (value === null || value === undefined) return '—';
  return `${Number(value).toFixed(decimals)} ${unit}`;
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Render system status from the central dashboard store.
 * @param {object} state
 */
function renderSystemMetrics(state) {
  const data = state;
  const system = data.system || {};
  const storage = data.storage || {};
  const learning = data.learning || {};
  const selfOrg = data.self_organization || {};
  const homeostasis = data.homeostasis || {};

  setText('tick', formatNumber(system.tick));
  setText('neurons', formatNumber(system.neurons));
  setText('synapses', formatNumber(system.synapses));
  setText('spikes', formatNumber(system.spikes_total));
  setText('core-ms', formatFloat(system.core_step_ms, 3));
  setText('energy', formatFloat(system.mean_energy, 3));

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

  setText('stdp', formatNumber(learning.stdp_updates));
  setText('reward-updates', formatNumber(learning.reward_updates));
  setText('rewards', `${formatNumber(learning.rewards_applied)} / ${formatNumber(learning.rewards_received)}`);
  setText('pending', formatNumber(learning.pending_rewards));
  setText('learning-ms', formatMetricUnit(learning.update_ms, 'ms', 3));

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

  const statusEl = $('system-status');
  if (statusEl) {
    statusEl.textContent = `${data.status || 'idle'} · ${data.version || 'unknown'}`;
    const workerFailed = storage.worker_failed;
    statusEl.className = workerFailed === true
      ? 'status-pill error'
      : (workerFailed === false ? 'status-pill online' : 'status-pill');
  }
}

/**
 * Render snapshot info from the store.
 * @param {object} state
 */
function renderSnapshotInfo(state) {
  const info = state.snapshot_info || {};
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
}

/**
 * Render integration status badges from the store.
 * @param {object} state
 */
function renderIntegrationStatus(state) {
  const itemIds = ['int-bridge', 'int-controller', 'int-structural', 'int-snapshots', 'int-research', 'int-tests'];
  const nameToId = {
    'Bridge': 'int-bridge',
    'Controller': 'int-controller',
    'Structural': 'int-structural',
    'Snapshot': 'int-snapshots',
    'Research': 'int-research',
    'Tests': 'int-tests',
  };

  const data = state.integration;
  if (!data) {
    for (const id of itemIds) {
      const el = $(id);
      if (el) el.className = 'integration-item int-failed';
    }
    const badge = $('integration-badge');
    if (badge) {
      badge.textContent = 'offline';
      badge.className = 'gate-badge failed';
    }
    return;
  }

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
}

/**
 * Render structural live loop status from the store.
 * @param {object} state
 */
function renderLiveLoopStatus(state) {
  const itemIds = ['ll-adapter', 'll-signal', 'll-policy', 'll-coordinator',
                   'll-approval', 'll-mutation', 'll-journal', 'll-undo', 'll-replay'];
  const data = state.gate;
  if (!data) {
    for (const id of itemIds) {
      const el = $(id);
      if (el) {
        el.className = 'live-loop-item ll-pending';
        el.textContent = `⏳ ${el.textContent.replace(/^[✅⏳❌🔄]\s*/, '')}`;
      }
    }
    const badge = $('live-loop-badge');
    if (badge) {
      badge.textContent = 'offline';
      badge.className = 'gate-badge failed';
    }
    const meta = $('live-loop-meta');
    if (meta) meta.textContent = 'Requires poc_structural_live.yaml config';
    return;
  }

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

  const structuralItems = gateA.filter(i => i.category === 'structural_composition');
  const idMap = {
    'A-STRUCT-RUNTIME-ADAPTER': 'll-adapter',
    'A-STRUCT-COORDINATOR': 'll-coordinator',
    'A-STRUCT-PLASTICITY': 'll-mutation',
    'A-STRUCT-MANIPULATOR': 'll-mutation',
    'A-STRUCT-APPROVAL': 'll-approval',
    'A-STRUCT-JOURNAL': 'll-journal',
    'A-STRUCT-PROVENANCE': 'll-signal',
  };
  for (const item of structuralItems) {
    const targetId = idMap[item.id];
    if (!targetId) continue;
    const el = $(targetId);
    if (!el) continue;
    if (item.status === 'passed') {
      el.className = 'live-loop-item ll-passed';
      el.textContent = `✅ ${el.textContent.replace(/^[✅⏳❌🔄]\s*/, '')}`;
    } else if (item.status === 'stale') {
      el.className = 'live-loop-item ll-stale';
      el.textContent = `🔄 ${el.textContent.replace(/^[✅⏳❌🔄]\s*/, '')}`;
    } else {
      el.className = 'live-loop-item ll-pending';
      el.textContent = `⏳ ${el.textContent.replace(/^[✅⏳❌🔄]\s*/, '')}`;
    }
  }
}

/**
 * Render runtime error visibility from the store.
 * @param {object} state
 */
/**
 * Render the entire overview panel from store state.
 * @param {object} state
 */
export function renderOverview(state) {
  renderSystemMetrics(state);
  renderSnapshotInfo(state);
  renderIntegrationStatus(state);
  renderLiveLoopStatus(state);
}
