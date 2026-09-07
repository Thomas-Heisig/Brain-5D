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

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[character]));

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
  const range = $('release-range');
  if (range && all.length) {
    range.textContent = `${all[0].version || '0.1'} bis ${all[all.length - 1].version || 'aktuell'}`;
  }

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
  renderCurrentReleasePreview(current);
}

function renderCurrentReleasePreview(current) {
  const container = $('release-preview');
  if (!container) return;
  if (!current) {
    container.innerHTML = '<p class="release-timeline-empty">Keine aktuelle Release-Vorschau verfügbar.</p>';
    return;
  }
  const scope = Array.isArray(current.scope) ? current.scope : [];
  container.innerHTML = `
    <div class="release-preview-header">
      <div><span class="release-node-version">${escapeHtml(current.version || 'unknown')}</span><span class="release-node-status release-status-current">${escapeHtml(current.status || 'development')}</span></div>
      <span class="release-preview-gate">Gate: ${escapeHtml(current.gate || 'open')}</span>
    </div>
    <h3>${escapeHtml(current.title || 'Current release')}</h3>
    <p class="release-preview-note">${escapeHtml(current.note || current.subtitle || '')}</p>
    ${scope.length ? `<ul>${scope.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : ''}
  `;
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

function formatTimelineDate(date) {
  if (!date) return 'Current backlog';
  const parsed = new Date(`${date}T00:00:00`);
  return Number.isNaN(parsed.getTime()) ? date : parsed.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

const TIMELINE_PHASES = [
  { key: 'past', label: 'Was war', hint: 'abgeschlossen / historisch' },
  { key: 'current', label: 'Was ist', hint: 'aktueller Stand' },
  { key: 'future', label: 'Was wird', hint: 'offen / geplant' },
];

const RELEASE_DOCUMENTS = [
  { key: 'todo', path: '08-roadmap/TODO.md' },
  { key: 'changelog', path: '07-changelog/CHANGELOG.md' },
  { key: 'roadmap', path: '08-roadmap/ROADMAP.md' },
];

let releaseDocumentsLoaded = false;

function renderTimelineEntry(entry) {
  const phase = TIMELINE_PHASES.find((item) => item.key === entry.phase) || TIMELINE_PHASES[1];
  const items = Array.isArray(entry.items)
    ? entry.items.filter((item) => item && typeof item === 'object')
    : [];
  const checks = items.filter((item) => typeof item.done === 'boolean');
  const completed = checks.filter((item) => item.done).length;
  const itemMarkup = items.slice(0, 5).map((item) => `
    <li class="${item.done === true ? 'is-done' : ''}">
      <span class="timeline-item-mark">${item.done === true ? '✓' : '·'}</span>
      <span>${escapeHtml(item.text)}</span>
    </li>
  `).join('');
  const remaining = items.length - Math.min(items.length, 5);
  const progress = checks.length ? `${completed}/${checks.length} erledigt` : '';
  return `
    <article class="release-timeline-entry release-timeline-entry-${phase.key} ${entry.date ? '' : 'is-undated'}">
      <div class="release-timeline-marker" aria-hidden="true"></div>
      <div class="release-timeline-date">${escapeHtml(formatTimelineDate(entry.date))}</div>
      <div class="release-timeline-content">
        <div class="release-timeline-entry-header">
          <h3>${escapeHtml(entry.title)}</h3>
          <span class="release-timeline-progress">${escapeHtml(progress)}</span>
        </div>
        <span class="release-timeline-phase-badge release-timeline-phase-badge-${phase.key}">${phase.label}</span>
        <div class="release-timeline-tags">
          ${(entry.sources || []).map((source) => `<span>${escapeHtml(source)}</span>`).join('')}
        </div>
        ${items.length ? `<ul>${itemMarkup}</ul>` : ''}
        ${remaining > 0 ? `<p class="release-timeline-more">+${remaining} weitere Punkte in den Quelldokumenten</p>` : ''}
      </div>
    </article>
  `;
}

function renderReleaseTimeline(entries, sources, asOf) {
  const list = $('release-timeline-list');
  const count = $('release-timeline-count');
  const sourceList = $('release-timeline-sources');
  if (!list) return;

  list.innerHTML = '';
  if (count) count.textContent = `${entries.length} Meilensteine · Stand ${asOf || '—'}`;
  if (sourceList) {
    sourceList.innerHTML = (sources || []).map((source) => `
      <span class="release-timeline-source ${source.available ? 'is-available' : 'is-missing'}">
        ${source.available ? '●' : '○'} ${escapeHtml(source.name)}
      </span>
    `).join('');
  }

  if (!entries.length) {
    list.innerHTML = '<p class="release-timeline-empty">No timeline entries available.</p>';
    return;
  }

  const groups = { past: [], current: [], future: [] };
  for (const entry of entries) {
    const phase = groups[entry.phase] ? entry.phase : 'current';
    groups[phase].push(entry);
  }
  const chronological = [...entries].sort((a, b) => {
    const dateA = a.date || '9999-12-31';
    const dateB = b.date || '9999-12-31';
    return dateA.localeCompare(dateB) || String(a.title || '').localeCompare(String(b.title || ''));
  });
  list.innerHTML = `
    <div class="release-timeline-phase-summary">
      ${TIMELINE_PHASES.map((phase) => `
        <div class="release-timeline-phase-summary-item release-timeline-phase-${phase.key}" data-timeline-phase="${phase.key}">
          <span>${phase.label}</span><strong>${groups[phase.key].length}</strong><small>${phase.hint}</small>
        </div>
      `).join('')}
    </div>
    <div class="release-timeline-chronological">
      ${chronological.map(renderTimelineEntry).join('')}
    </div>
  `;
}

async function loadReleaseDocuments() {
  if (releaseDocumentsLoaded) return;
  releaseDocumentsLoaded = true;
  await Promise.all(RELEASE_DOCUMENTS.map(async (document) => {
    const target = $(`release-doc-${document.key}`);
    if (!target) return;
    try {
      const response = await fetch(`/api/files/content/${encodeURIComponent(document.path)}?source=docs`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const content = await response.text();
      target.textContent = content.length > 12000 ? `${content.slice(0, 12000)}\n\n[Preview gekürzt]` : content;
    } catch (err) {
      target.textContent = 'Dokument konnte nicht geladen werden.';
    }
  }));
}

async function loadReleaseTimeline() {
  try {
    const response = await fetch('/api/releases/timeline', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderReleaseTimeline(data.entries || [], data.sources || [], data.as_of);
  } catch (err) {
    const list = $('release-timeline-list');
    if (list) list.textContent = 'Release timeline unavailable.';
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
  loadReleaseTimeline();
  loadReleaseDocuments();
}
