/**
 * MHRN Dashboard — Alpha.5 Release Gate Board
 *
 * Renders the VERIFY/Gate tab from the central dashboard store.
 * Does NOT issue its own HTTP requests; all data arrives via store subscription.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

import { openDocumentationFile } from './file-viewer.js';

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

  const all = [...releases];
  if (current) all.push(current);

  // Sort by PEP440
  all.sort((a, b) => (a.pep440 || '').localeCompare(b.pep440 || ''));
  const range = $('release-range');
  if (range && all.length) {
    range.textContent = `${all[0].version || '0.1'} bis ${all[all.length - 1].version || 'aktuell'}`;
  }

  container.innerHTML = `
    <div class="release-cards">
      ${all.map((rel) => {
        const status = rel.status || 'unknown';
        const isCurrent = status === 'development';
        const isReleased = status === 'released';
        const statusClass = isReleased ? 'released' : isCurrent ? 'current' : status;
        const gate = rel.gate || '—';
        const gateLabel = gate === 'passed' ? 'Bestanden' : gate === 'open' ? 'Offen' : gate === 'failed' ? 'Fehlgeschlagen' : '—';
        const gateClass = gate === 'passed' ? 'pass' : gate === 'failed' ? 'fail' : 'pending';
        const baseline = rel.baseline;
        const hasTests = baseline && (baseline.passed > 0 || baseline.failed > 0 || baseline.skipped > 0);
        const features = Array.isArray(rel.features) ? rel.features : [];
        const changes = Array.isArray(rel.changelog) ? rel.changelog : [];
        const items = features.length ? features : changes;
        const extraId = `rel-extra-${String(rel.version || '').replace(/\./g, '-')}`;
        const visible = items.slice(0, 4);
        const extra = items.slice(4);

        return `
          <article class="release-card release-${statusClass}">
            <div class="release-card-top">
              <span class="release-version-badge release-version-${statusClass}">${escapeHtml(rel.version || 'unknown')}</span>
              <span class="release-status-pill release-pill-${statusClass}">${isReleased ? 'Veröffentlicht' : isCurrent ? 'In Entwicklung' : status}</span>
              ${isReleased ? `<span class="release-gate-pill release-gate-${gateClass}">Gate: ${gateLabel}</span>` : ''}
              <span class="release-date">${escapeHtml(rel.date || rel.as_of || '—')}</span>
            </div>
            <h3 class="release-card-title">${escapeHtml(rel.title || '')}</h3>
            ${rel.subtitle ? `<p class="release-card-sub">${escapeHtml(rel.subtitle)}</p>` : ''}
            <div class="release-card-meta">
              ${rel.tag ? `<span><b>Tag</b> ${escapeHtml(rel.tag)}</span>` : ''}
              ${rel.commit ? `<span><b>Commit</b> <code>${escapeHtml(rel.commit).slice(0, 12)}</code></span>` : ''}
              ${rel.pep440 ? `<span><b>PEP 440</b> ${escapeHtml(rel.pep440)}</span>` : ''}
            </div>
            ${hasTests ? `
              <div class="release-test-bar">
                <span class="release-test-pass" style="flex:${baseline.passed}">${baseline.passed} passed</span>
                <span class="release-test-fail" style="flex:${baseline.failed}">${baseline.failed} failed</span>
                <span class="release-test-skip" style="flex:${baseline.skipped}">${baseline.skipped} skipped</span>
              </div>
            ` : ''}
            ${items.length ? `
              <div class="release-items">
                <ul class="release-item-list">
                  ${visible.map((item) => `<li>${escapeHtml(typeof item === 'string' ? item : item.text || item.title || '')}</li>`).join('')}
                </ul>
                ${extra.length ? `
                  <div class="release-items-extra" id="${extraId}">
                    <ul class="release-item-list">
                      ${extra.map((item) => `<li>${escapeHtml(typeof item === 'string' ? item : item.text || item.title || '')}</li>`).join('')}
                    </ul>
                  </div>
                  <button type="button" class="release-more-btn" data-rel-extra="${extraId}" aria-expanded="false">+${extra.length} weitere Einträge</button>
                ` : ''}
              </div>
            ` : ''}
            ${isCurrent && rel.note ? `<div class="release-card-note">${escapeHtml(rel.note)}</div>` : ''}
          </article>
        `;
      }).join('')}
    </div>
  `;

  // "Mehr" Toggle
  container.querySelectorAll('[data-rel-extra]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.relExtra);
      if (!target) return;
      const isOpen = target.classList.toggle('is-open');
      btn.classList.toggle('is-open', isOpen);
      btn.setAttribute('aria-expanded', String(isOpen));
      const count = target.querySelectorAll('li').length;
      btn.textContent = isOpen ? 'Weniger anzeigen' : `+${count} weitere Einträge`;
    });
  });

  renderCurrentReleasePreview(current);
}

function renderCurrentReleasePreview(current) {
  const container = $('release-preview');
  if (!container) return;
  if (!current) {
    container.innerHTML = '<p class="release-empty">Keine aktuelle Release-Vorschau verfügbar.</p>';
    return;
  }
  const scope = Array.isArray(current.scope) ? current.scope : [];
  const completed = Array.isArray(current.completed) ? current.completed : [];
  const open = Array.isArray(current.open) ? current.open : [];
  const releaseBlockers = Number.isFinite(Number(current.release_blockers))
    ? Number(current.release_blockers)
    : null;
  const gate = current.gate || 'open';
  const gateClass = gate === 'passed' ? 'pass' : gate === 'failed' ? 'fail' : 'pending';
  const gateLabel = gate === 'passed' ? 'Bestanden' : gate === 'failed' ? 'Fehlgeschlagen' : 'Offen';

  // Aufklappbare Items
  const renderItems = (items, extraId) => {
    if (!items.length) return '';
    const visible = items.slice(0, 5);
    const extra = items.slice(5);
    return `
      <ul class="preview-item-list">
        ${visible.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
      </ul>
      ${extra.length ? `
        <div class="preview-items-extra" id="${extraId}">
          <ul class="preview-item-list">
            ${extra.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </div>
        <button type="button" class="preview-more-btn" data-preview-extra="${extraId}" aria-expanded="false">+${extra.length} weitere</button>
      ` : ''}
    `;
  };

  container.innerHTML = `
    <div class="release-preview-card">
      <div class="preview-head">
        <div class="preview-head-left">
          <span class="preview-version-badge">${escapeHtml(current.version || 'unknown')}</span>
          <span class="preview-status-pill">${escapeHtml(current.status || 'development')}</span>
        </div>
        <div class="preview-head-right">
          <span class="preview-gate-badge preview-gate-${gateClass}">Gate: ${gateLabel}</span>
          <span class="preview-date">${escapeHtml(current.as_of || '—')}</span>
        </div>
      </div>

      <h3 class="preview-title">${escapeHtml(current.title || 'Current release')}</h3>

      <div class="preview-stats">
        <div class="preview-stat">
          <span>Meilenstein</span>
          <strong>${escapeHtml(current.milestone_status || 'development')}</strong>
        </div>
        <div class="preview-stat">
          <span>Release-Blocker</span>
          <strong>${releaseBlockers === null ? '—' : releaseBlockers}</strong>
        </div>
        <div class="preview-stat">
          <span>Abgeschlossen</span>
          <strong>${completed.length}</strong>
        </div>
        <div class="preview-stat">
          <span>Offen</span>
          <strong>${open.length}</strong>
        </div>
      </div>

      ${current.note || current.subtitle ? `<p class="preview-note">${escapeHtml(current.note || current.subtitle)}</p>` : ''}

      <div class="preview-sections">
        ${completed.length ? `
          <section class="preview-section">
            <header><span>✓</span><h4>Abgeschlossen</h4><small>${completed.length}</small></header>
            ${renderItems(completed, 'preview-completed-extra')}
          </section>
        ` : ''}
        ${open.length ? `
          <section class="preview-section">
            <header><span>○</span><h4>Offen</h4><small>${open.length}</small></header>
            ${renderItems(open, 'preview-open-extra')}
          </section>
        ` : ''}
        ${scope.length ? `
          <section class="preview-section preview-section-scope">
            <header><span>◈</span><h4>Meilenstein-Scope</h4><small>${scope.length}</small></header>
            ${renderItems(scope, 'preview-scope-extra')}
          </section>
        ` : ''}
      </div>

      ${current.research_boundary ? `<div class="preview-boundary"><strong>Wissenschaftliche Grenze:</strong> ${escapeHtml(current.research_boundary)}</div>` : ''}
    </div>
  `;

  // "Mehr" Toggle
  container.querySelectorAll('[data-preview-extra]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.previewExtra);
      if (!target) return;
      const isOpen = target.classList.toggle('is-open');
      btn.classList.toggle('is-open', isOpen);
      btn.setAttribute('aria-expanded', String(isOpen));
      const count = target.querySelectorAll('li').length;
      btn.textContent = isOpen ? 'Weniger' : `+${count} weitere`;
    });
  });
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

function renderTimelineEntry(entry) {
  const phase = TIMELINE_PHASES.find((item) => item.key === entry.phase) || TIMELINE_PHASES[1];
  const items = Array.isArray(entry.items)
    ? entry.items.filter((item) => item && typeof item === 'object')
    : [];
  const checks = items.filter((item) => typeof item.done === 'boolean');
  const completed = checks.filter((item) => item.done).length;
  const progress = checks.length ? `${completed}/${checks.length} erledigt` : '';
  const visible = items.slice(0, 3);
  const extra = items.slice(3);
  const hasExtra = extra.length > 0;
  const extraId = `timeline-extra-${String(entry.title || '').replace(/\s+/g, '-').toLowerCase()}`;

  const itemMarkup = (list) => list.map((item) => `
    <li class="${item.done === true ? 'is-done' : ''}">
      <span class="timeline-item-mark">${item.done === true ? '✓' : '·'}</span>
      <span>${escapeHtml(item.text)}</span>
    </li>
  `).join('');

  return `
    <article class="timeline-entry timeline-entry-${phase.key} ${entry.date ? '' : 'is-undated'}">
      <div class="timeline-marker" aria-hidden="true"></div>
      <div class="timeline-card">
        <div class="timeline-card-header">
          <div>
            <h3>${escapeHtml(entry.title)}</h3>
            <span class="timeline-date">${escapeHtml(formatTimelineDate(entry.date))}</span>
          </div>
          <span class="timeline-phase-badge timeline-phase-${phase.key}">${phase.label}</span>
        </div>
        <div class="timeline-tags">
          ${(entry.sources || []).map((source) => `<span>${escapeHtml(source)}</span>`).join('')}
        </div>
        ${items.length ? `
          <ul class="timeline-items">
            ${itemMarkup(visible)}
          </ul>
          ${hasExtra ? `
            <div class="timeline-items-extra" id="${extraId}">
              <ul class="timeline-items">
                ${itemMarkup(extra)}
              </ul>
            </div>
            <button type="button" class="timeline-more-btn" data-timeline-extra="${extraId}" aria-expanded="false">+${extra.length} weitere</button>
          ` : ''}
        ` : ''}
        ${progress ? `<span class="timeline-progress">${escapeHtml(progress)}</span>` : ''}
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
    list.innerHTML = '<p class="timeline-empty">Keine Timeline-Einträge verfügbar.</p>';
    return;
  }

  const chronological = [...entries].sort((a, b) => {
    const dateA = a.date || '9999-12-31';
    const dateB = b.date || '9999-12-31';
    return dateA.localeCompare(dateB) || String(a.title || '').localeCompare(String(b.title || ''));
  });

  list.innerHTML = `
    <div class="timeline-vertical">
      ${chronological.map(renderTimelineEntry).join('')}
    </div>
  `;

  // "Mehr anzeigen" Toggle
  list.querySelectorAll('[data-timeline-extra]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.timelineExtra);
      if (!target) return;
      const isOpen = target.classList.toggle('is-open');
      btn.classList.toggle('is-open', isOpen);
      btn.setAttribute('aria-expanded', String(isOpen));
      btn.textContent = isOpen ? 'weniger' : `+${extraCount(btn)} weitere`;
    });
  });
}

function extraCount(btn) {
  const target = document.getElementById(btn.dataset.timelineExtra);
  if (!target) return 0;
  return target.querySelectorAll('li').length;
}

function scorePercent(value) {
  return `${Math.round(Math.max(0, Math.min(1, Number(value) || 0)) * 100)}%`;
}

function runtimeLabel(value) {
  return value === null || value === undefined ? 'unavailable' : Number(value).toLocaleString('de-DE');
}

function renderDevelopmentScales(data) {
  const container = $('development-scale-grid');
  if (!container) return;
  const runtime = data.current_runtime || {};
  const observed = data.last_observed_runtime || {};
  const valueFor = (key) => (typeof runtime[key] === 'number' ? runtime[key] : observed[key]);
  const scales = [
    { key: 'neurons', label: 'Neuronen', maximum: 11 },
    { key: 'synapses', label: 'Synapsen', maximum: 15 },
  ];
  container.innerHTML = scales.map((scale) => {
    const value = valueFor(scale.key);
    const position = typeof value === 'number' && value > 0
      ? Math.max(0, Math.min(100, Math.log10(value) / scale.maximum * 100))
      : null;
    return `
      <div class="dev-scale" aria-label="Logarithmische ${scale.label}-Skala">
        <header><strong>${scale.label}</strong><span>${runtime.status === 'active' ? 'aktuell' : 'last observed'}</span></header>
        <div class="dev-scale-line">
          ${position === null ? '<span class="dev-scale-na">—</span>' : `<span class="dev-scale-marker" style="left:${position}%" title="${escapeHtml(runtimeLabel(value))}"></span>`}
          <span class="dev-scale-value">${escapeHtml(runtimeLabel(value))}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderDevelopmentTrack(data, containerId) {
  const container = $(containerId);
  if (!container) return;
  const stages = Array.isArray(data.stages) ? data.stages : [];
  const technicalIdx = Math.max(0, Math.min(stages.length - 1, Number(data.current_stage) || 0));
  const scientificIdx = Math.max(0, Math.min(stages.length - 1, Number(data.scientific_stage) || 0));

  container.innerHTML = stages.map((stage, idx) => {
    const isTech = idx === technicalIdx;
    const isSci = idx === scientificIdx;
    const status = stage.status || 'planned';
    const score = Math.round(Math.max(0, Math.min(1, Number(stage.implementation_score) || 0)) * 100);
    return `
      <button type="button" class="dev-node dev-node-${escapeHtml(status)} ${isTech ? 'is-tech-here' : ''} ${isSci ? 'is-sci-here' : ''}" data-development-stage="${stage.stage}" role="listitem" title="Stufe ${stage.stage}: ${escapeHtml(stage.name)}">
        <span class="dev-node-number">${stage.stage}</span>
        <span class="dev-node-label">${escapeHtml(stage.short_label || stage.name)}</span>
        <span class="dev-node-bar"><span class="dev-node-fill" style="width:${score}%"></span></span>
        <span class="dev-node-status">${escapeHtml(status)}</span>
        ${isTech ? '<span class="dev-node-marker dev-node-marker-tech">● hier</span>' : ''}
        ${isSci && !isTech ? '<span class="dev-node-marker dev-node-marker-sci">○ Evidenz</span>' : ''}
      </button>
    `;
  }).join('');
}

function renderDevelopmentDetail(stage) {
  const detail = $('development-detail');
  if (!detail || !stage) return;
  const list = (items) => (Array.isArray(items) && items.length)
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
    : '<p class="development-empty">Keine strukturierten Einträge vorhanden.</p>';
  const criteria = Array.isArray(stage.criteria) ? stage.criteria : [];
  detail.hidden = false;
  detail.innerHTML = `
    <div class="dev-detail-header">
      <div><span class="workspace-kicker">STUFE ${stage.stage}</span><h3>${escapeHtml(stage.name)}</h3></div>
      <button type="button" class="modal-close" data-development-detail-close aria-label="Detail schließen">&times;</button>
    </div>
    <p>${escapeHtml((stage.description || []).join(' · '))}</p>
    <div class="dev-detail-scores">
      <span>Engineering <strong>${scorePercent(stage.implementation_score)}</strong></span>
      <span>Verification <strong>${scorePercent(stage.verification_score)}</strong></span>
      <span>Scientific readiness <strong>${scorePercent(stage.research_readiness_score)}</strong></span>
    </div>
    <div class="dev-criteria-list">
      ${criteria.map((criterion) => `
        <div class="dev-criterion dev-criterion-${escapeHtml(criterion.status || 'missing')}">
          <span>${escapeHtml(criterion.label || criterion.id)}</span>
          <strong>${escapeHtml(criterion.status || 'missing')}</strong>
          ${Array.isArray(criterion.evidence) && criterion.evidence.length ? `<small>${escapeHtml(criterion.evidence.join(' · '))}</small>` : ''}
        </div>
      `).join('')}
    </div>
    <div class="dev-detail-columns">
      <section><h4>Module</h4>${list(stage.relevant_modules)}</section>
      <section><h4>Tests</h4>${list(stage.relevant_tests)}</section>
      <section><h4>Experimente / RQ</h4>${list([...(stage.relevant_experiments || []), ...(stage.relevant_research_questions || [])])}</section>
      <section><h4>Grenzen</h4>${list(stage.known_limits)}</section>
      <section><h4>Offene TODOs</h4>${list(stage.open_todos)}</section>
      <section><h4>Nächste technische Schritte</h4>${list(stage.next_technical_steps)}</section>
    </div>
  `;
}

function renderDevelopmentTimeline(data) {
  const stages = Array.isArray(data.stages) ? data.stages : [];
  const scoreGrid = $('development-score-grid');
  const stageList = $('development-stage-list');
  const notice = $('development-timeline-notice');
  const updated = $('development-timeline-updated');
  if (updated) updated.textContent = `Stand ${formatTimelineDate((data.last_updated || '').slice(0, 10))}`;
  if (notice) notice.innerHTML = `<strong>Research frontier:</strong> ${escapeHtml(data.scientific_note || 'Keine automatische Bewusstseinsbehauptung.')} <span class="dev-consciousness-guard">${escapeHtml(data.consciousness_claim || 'unsupported')}</span>`;
  if (scoreGrid) {
    const runtime = data.current_runtime || {};
    const last = data.last_observed_runtime;
    scoreGrid.innerHTML = [
      ['Engineering', data.engineering_score, 'Implementiert / integriert'],
      ['Verification', data.verification_score, 'Technisch reproduziert'],
      ['Scientific Evidence', data.scientific_evidence_score, 'EVID bleibt gate- und reviewgebunden'],
      ['Neuronen', runtime.status === 'active' ? runtimeLabel(runtime.neurons) : (last ? runtimeLabel(last.neurons) : '—'), runtime.status === 'active' ? 'aktuell' : 'last observed'],
      ['Synapsen', runtime.status === 'active' ? runtimeLabel(runtime.synapses) : (last ? runtimeLabel(last.synapses) : '—'), runtime.status === 'active' ? 'aktuell' : 'last observed'],
      ['Confidence', `${scorePercent(data.confidence)}`, 'Fehlt bei stale/fehlenden Verifikationsdaten'],
    ].map(([label, value, hint]) => `<div class="dev-stat"><span>${label}</span><strong>${value}</strong><small>${hint}</small></div>`).join('');
  }
  renderDevelopmentScales(data);
  renderDevelopmentTrack(data, 'development-timeline-track');
  if (stageList) {
    stageList.innerHTML = stages.map((stage) => `
      <button type="button" class="dev-stage-card dev-stage-${escapeHtml(stage.status || 'planned')}" data-development-stage="${stage.stage}">
        <span class="dev-stage-number">${stage.stage}</span>
        <span class="dev-stage-copy"><strong>${escapeHtml(stage.name)}</strong><small>${escapeHtml((stage.description || []).join(' · '))}</small></span>
        <span class="dev-stage-metrics"><b>${scorePercent(stage.implementation_score)}</b><em>${escapeHtml(stage.status || 'planned')}</em></span>
      </button>
    `).join('');
  }
  window.__mhrnDevelopmentTimeline = data;
}

let developmentTimelineLinksBound = false;

function bindDevelopmentTimeline() {
  if (developmentTimelineLinksBound) return;
  developmentTimelineLinksBound = true;
  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-development-stage]');
    if (target && window.__mhrnDevelopmentTimeline) {
      const stage = window.__mhrnDevelopmentTimeline.stages?.find((item) => String(item.stage) === String(target.dataset.developmentStage));
      renderDevelopmentDetail(stage);
    }
    if (event.target.closest('[data-development-detail-close]')) {
      const detail = $('development-detail');
      if (detail) detail.hidden = true;
    }
  });
}

async function loadDevelopmentTimeline() {
  try {
    const response = await fetch('/api/release/development-timeline', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderDevelopmentTimeline(await response.json());
    bindDevelopmentTimeline();
  } catch (err) {
    const notice = $('development-timeline-notice');
    if (notice) notice.textContent = 'Entwicklungs-Timeline unavailable.';
  }
}

let releaseDocumentLinksBound = false;

function bindReleaseDocumentLinks() {
  if (releaseDocumentLinksBound) return;
  releaseDocumentLinksBound = true;
  document.querySelectorAll('[data-release-document]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector('[data-tab="research"]')?.click();
      openDocumentationFile(button.dataset.releaseDocument || '');
    });
  });
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
  loadDevelopmentTimeline();
  bindReleaseDocumentLinks();
}
