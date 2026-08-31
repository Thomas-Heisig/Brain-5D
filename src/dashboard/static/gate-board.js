/**
 * Brain-5D Dashboard — Alpha.5 Release Gate Board
 *
 * Renders the VERIFY/Gate tab from the central dashboard store.
 * Does NOT issue its own HTTP requests; all data arrives via store subscription.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

const $ = (id) => document.getElementById(id);

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

function renderReleaseTree(releases, current) {
  const container = $('release-tree');
  if (!container) return;
  container.innerHTML = '';

  const tree = document.createElement('div');
  tree.className = 'release-tree-list';

  const all = [...releases];
  if (current) {
    all.push(current);
  }

  // Sort by PEP440 version string roughly matching the release order.
  all.sort((a, b) => (a.pep440 || '').localeCompare(b.pep440 || ''));

  for (const rel of all) {
    const status = rel.status || 'unknown';
    const isCurrent = status === 'development';
    const isReleased = status === 'released';
    const statusClass = isReleased ? 'released' : isCurrent ? 'current' : status;
    const statusIcon = isReleased ? '✅' : isCurrent ? '🚧' : '❓';
    const gate = rel.gate || '—';
    const gateIcon = gate === 'passed' ? '✅' : gate === 'open' ? '🔓' : '—';

    const row = document.createElement('div');
    row.className = `release-tree-node release-${statusClass}`;
    row.innerHTML = `
      <div class="release-node-header">
        <span class="release-node-icon">${statusIcon}</span>
        <span class="release-node-version">${rel.version || 'unknown'}</span>
        <span class="release-node-status release-status-${statusClass}">${status}</span>
        ${isReleased ? `<span class="release-node-gate" title="gate: ${gate}">${gateIcon}</span>` : ''}
      </div>
      <div class="release-node-body">
        <strong>${rel.title || ''}</strong>
        ${rel.subtitle ? `<p>${rel.subtitle}</p>` : ''}
        ${isReleased && rel.baseline ? `<p>Tests: ${rel.baseline.passed} / ${rel.baseline.failed} / ${rel.baseline.skipped}</p>` : ''}
        ${isReleased && rel.tag ? `<p class="release-node-meta">tag: ${rel.tag} · commit: ${(rel.commit || '').slice(0, 9)} · ${rel.date || ''}</p>` : ''}
        ${isCurrent && rel.note ? `<p class="release-node-note">${rel.note}</p>` : ''}
      </div>
    `;
    tree.appendChild(row);
  }

  container.appendChild(tree);
}

async function loadReleaseTree() {
  try {
    const r = await fetch('/api/releases', { cache: 'no-store' });
    if (!r.ok) return;
    const data = await r.json();
    renderReleaseTree(data.releases || [], data.current || null);
  } catch (err) {
    const container = $('release-tree');
    if (container) container.textContent = 'Release history unavailable.';
  }
}

/**
 * Render the release board from store state.
 * @param {object} state
 */
export function renderGateBoard(state) {
  const data = state.gate;
  if (!data) {
    const overallEl = $('gate-overall');
    if (overallEl) {
      overallEl.textContent = 'unavailable';
      overallEl.className = 'gate-badge gate-failed';
    }
    return;
  }

  const overallEl = $('gate-overall');
  if (overallEl) {
    overallEl.textContent = data.overall || 'pending';
    overallEl.className = `gate-badge gate-${data.overall || 'pending'}`;
  }

  if (data.live_runtime) {
    renderLiveRuntime(data.live_runtime);
  }
  if (data.gate_a && data.gate_a.items) {
    renderGateCriteria('gate-a-list', data.gate_a.items);
  }
  if (data.gate_b && data.gate_b.items) {
    renderGateCriteria('gate-b-list', data.gate_b.items);
  }
  if (data.gate_c && data.gate_c.items) {
    renderGateCriteria('gate-c-list', data.gate_c.items);
  }

  // Load immutable release history once per render cycle.
  loadReleaseTree();
}
