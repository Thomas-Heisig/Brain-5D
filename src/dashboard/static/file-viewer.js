/**
 * MHRN Operator Dashboard – Unified File Manager Module
 *
 * Self-contained ES module for browsing, searching, and previewing
 * research and documentation files. Exports:
 *   - initFileManager()          — one-shot initializer (safe to call multiple times)
 *   - initResearchBrowser()      — alias for initFileManager (legacy API)
 *   - initDocumentationBrowser() — alias for initFileManager (legacy API)
 *
 * This module owns the following DOM elements:
 *   fm-toolbar, fm-source-selector, fm-search-bar, fm-breadcrumb,
 *   fm-filters, fm-sidebar, fm-tree, fm-recent, fm-viewer
 *
 * @module file-viewer
 * @requires No external dependencies — self-contained helpers only.
 */

"use strict";

// ================================================================
// BibTeX Viewer import (for structured .bib file display)
// ================================================================

import { renderFile, createTextFile, renderMessage, iconButton } from './file-renderer.js';

// ================================================================
// Local helpers (mirrored from app.js to keep this module standalone)
// ================================================================

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML.replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function formatBytes(value) {
  if (value === null || value === undefined) return '\u2014';
  const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
  let size = Number(value);
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx++;
  }
  return `${size.toFixed(idx === 0 ? 0 : 2)} ${units[idx]}`;
}

// ================================================================
// Editability helpers
// ================================================================

// ================================================================
// Module state
// ================================================================

let fmInitialized = false;
let fmCurrentSource = 'research';
let fmActiveFilter = 'all';
let fmExperimentSort = 'newest';
let fmRecentFiles = [];
let fmCurrentPath = '';
let fmCurrentFileSource = '';
let fmViewerHistory = [];
let fmUsePopup = localStorage.getItem('mhrn-fm-popup') !== 'false';
const FM_RECENT_KEY = 'brain5d_fm_recent';
const FM_RECENT_MAX = 20;

// Load recent files from localStorage
function loadFMRecent() {
  try {
    const stored = localStorage.getItem(FM_RECENT_KEY);
    if (stored) fmRecentFiles = JSON.parse(stored);
  } catch { fmRecentFiles = []; }
}

function saveFMRecent() {
  try {
    localStorage.setItem(FM_RECENT_KEY, JSON.stringify(fmRecentFiles.slice(0, FM_RECENT_MAX)));
  } catch { /* ignore */ }
}

function addFMRecent(path, name, source) {
  // Remove duplicate
  fmRecentFiles = fmRecentFiles.filter(r => !(r.path === path && r.source === source));
  fmRecentFiles.unshift({ path, name, source, time: Date.now() });
  if (fmRecentFiles.length > FM_RECENT_MAX) fmRecentFiles.length = FM_RECENT_MAX;
  saveFMRecent();
  renderFMRecent();
}

function renderFMRecent() {
  const list = document.getElementById('fm-recent-list');
  if (!list) return;
  if (fmRecentFiles.length === 0) {
    list.innerHTML = '<div class="fm-empty fm-empty-recent">(no recent files)</div>';
    return;
  }
  list.innerHTML = fmRecentFiles.map(r => {
    const icon = /\.(png|jpg|jpeg|gif|webp|svg|bmp)$/i.test(r.name) ? '🖼️' :
                 /\.(mp4|webm|ogg|mov|avi)$/i.test(r.name) ? '🎬' :
                 /\.(mp3|wav|flac|aac|m4a|opus)$/i.test(r.name) ? '🎵' :
                 /\.(xlsx|xls|xlsm|ods)$/i.test(r.name) ? '📊' :
                 /\.(docx|doc)$/i.test(r.name) ? '📘' :
                 /\.(md|markdown)$/i.test(r.name) ? '📝' :
                 /\.(py)$/i.test(r.name) ? '🐍' :
                 /\.(json)$/i.test(r.name) ? '📋' : '📄';
    const srcLabel = r.source === 'research' ? '🔬' : '📄';
    return `<div class="fm-recent-item" data-path="${escapeHtml(r.path)}" data-source="${escapeHtml(r.source)}">
      <span class="fm-recent-icon">${icon}</span>
      <span class="fm-recent-name">${escapeHtml(r.name)}</span>
      <span class="fm-recent-source">${srcLabel}</span>
    </div>`;
  }).join('');
  list.querySelectorAll('.fm-recent-item').forEach(el => {
    el.addEventListener('click', () => {
      const path = el.dataset.path;
      const source = el.dataset.source;
      // Switch source if needed
      if (source !== fmCurrentSource) {
        fmCurrentSource = source;
        const buttons = document.querySelectorAll('.fm-source-btn');
        buttons.forEach(b => {
          b.classList.toggle('active', b.dataset.source === source);
        });
        updateFMBreadcrumb();
      }
      openFMFile(path);
    });
  });
}

function initFileManager() {
  console.log('📁 Unified File Manager initializing...');
  if (!fmInitialized) {
    document.addEventListener('brain5d:files-changed', () => refreshFileManager());
    const toolbar = document.querySelector('.fm-toolbar');
    if (toolbar && !document.getElementById('fm-create-file')) {
      const create = document.createElement('button'); create.id = 'fm-create-file'; create.type = 'button'; create.textContent = 'Neue Textdatei';
      create.addEventListener('click', async () => {
        const path = window.prompt('Relativer Dateipfad', 'notes/new.md');
        if (!path) return;
        try { await createTextFile({ source: fmCurrentSource, path }); await refreshFileManager(); await openFMFile(path); }
        catch (error) { window.alert(error.message); }
      });
      toolbar.append(create);
    }
    if (toolbar && !document.getElementById('fm-open-publication')) {
      const publication = document.createElement('button');
      publication.id = 'fm-open-publication';
      publication.type = 'button';
      publication.textContent = 'Abhandlung lesen';
      publication.addEventListener('click', async () => {
        publication.disabled = true;
        try {
          fmCurrentSource = 'research';
          fmCurrentPath = '';
          document.querySelectorAll('.fm-source-btn').forEach(control => {
            control.classList.toggle('active', control.dataset.source === 'research');
          });
          updateFMExperimentSortControl();
          updateFMBreadcrumb();
          await refreshFileManager();
          await openFMFile('publications/README.md');
        } catch (error) {
          window.alert(`Abhandlung konnte nicht geoeffnet werden: ${error.message}`);
        } finally {
          publication.disabled = false;
        }
      });
      toolbar.append(publication);
    }
    // Popup toggle checkbox
    if (toolbar && !document.getElementById('fm-popup-toggle')) {
      const label = document.createElement('label');
      label.className = 'fm-popup-toggle';
      label.title = 'Datei im Popup öffnen';
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.id = 'fm-popup-toggle';
      cb.checked = fmUsePopup;
      cb.addEventListener('change', () => { fmUsePopup = cb.checked; localStorage.setItem('mhrn-fm-popup', String(cb.checked)); });
      label.append(cb, ' Popup');
      // Insert before the refresh button
      const refBtn = document.getElementById('fm-refresh');
      if (refBtn) toolbar.insertBefore(label, refBtn);
      else toolbar.append(label);
    }

    loadFMRecent();
    setupFMSourceButtons();
    setupFMExperimentSort();
    setupFMSearch();
    setupFMRefresh();
    setupFMFilters();
    setupFMOpenOS();
    setupFMToggleRecent();
    setupFMClearRecent();
    loadFMStats();
    loadFMTree();
    renderFMRecent();
    fmInitialized = true;
  }
}

async function refreshFileManager() {
  await Promise.all([loadFMStats(), loadFMTree()]);
}

function updateFMBreadcrumb() {
  const bc = document.getElementById('fm-breadcrumb');
  if (!bc) return;
  const rootLabel = fmCurrentSource === 'research' ? '🔬 research/' : '📄 docs/';
  bc.innerHTML = `<span class="fm-bc-item fm-bc-root" data-path="">📁 <span class="fm-bc-source-label">${rootLabel}</span></span>`;
}

function setupFMSourceButtons() {
  const buttons = document.querySelectorAll('.fm-source-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      fmCurrentSource = btn.dataset.source;
      updateFMExperimentSortControl();
      updateFMBreadcrumb();
      loadFMStats();
      loadFMTree();
    });
  });
}

function setupFMExperimentSort() {
  const select = document.getElementById('fm-experiment-sort');
  if (!select) return;
  select.value = fmExperimentSort;
  select.addEventListener('change', () => {
    fmExperimentSort = select.value === 'oldest' ? 'oldest' : 'newest';
    loadFMTree();
  });
  updateFMExperimentSortControl();
}

function updateFMExperimentSortControl() {
  const select = document.getElementById('fm-experiment-sort');
  // Always enabled — sorts experiment directories by date for all sources
  if (select) select.disabled = false;
}

function setupFMRefresh() {
  const btn = document.getElementById('fm-refresh');
  if (btn) {
    btn.addEventListener('click', () => {
      loadFMStats();
      loadFMTree();
    });
  }
}

function setupFMSearch() {
  const input = document.getElementById('fm-search');
  const btn = document.getElementById('fm-search-btn');
  if (!input) return;

  const doSearch = () => {
    const q = input.value.trim();
    if (q.length < 2) {
      loadFMTree();
      return;
    }
    performFMSearch(q);
  };

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
  });
  if (btn) btn.addEventListener('click', doSearch);
}

function setupFMFilters() {
  const chips = document.querySelectorAll('.fm-filter-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      fmActiveFilter = chip.dataset.ext;
      // Re-apply filter to currently loaded tree
      const treeEl = document.getElementById('fm-tree');
      if (treeEl && treeEl.querySelector('.fm-tree-list')) {
        applyFMFilter();
      } else {
        // Reload tree if no tree is showing (e.g. after search)
        loadFMTree();
      }
    });
  });
}

function applyFMFilter() {
  const items = document.querySelectorAll('.fm-tree-file');
  if (fmActiveFilter === 'all') {
    items.forEach(el => el.classList.remove('is-hidden'));
    return;
  }
  const exts = fmActiveFilter.split(',');
  items.forEach(el => {
    const label = el.querySelector('.fm-file-label');
    if (!label) return;
    const name = label.textContent || '';
    const ext = '.' + name.split('.').pop().split(' ')[0].toLowerCase();
    const match = exts.some(e => name.toLowerCase().endsWith(e) || ext === e);
    el.classList.toggle('is-hidden', !match);
  });
}

function setupFMOpenOS() {
  const btn = document.getElementById('fm-open-os');
  if (!btn) return;
  btn.addEventListener('click', () => {
    // Open the source folder in the OS file explorer
    const src = fmCurrentSource;
    fetch(`/api/files/tree?source=${encodeURIComponent(src)}`)
      .then(r => r.json())
      .then(tree => {
        // Tell the backend to open the folder
        fetch(`/api/files/open?source=${encodeURIComponent(src)}`)
          .catch(() => {});
      })
      .catch(() => {});
  });
}

function setupFMToggleRecent() {
  const btn = document.getElementById('fm-toggle-recent');
  const panel = document.getElementById('fm-recent');
  if (!btn || !panel) return;
  btn.addEventListener('click', () => {
    const visible = !panel.classList.contains('is-hidden');
    panel.classList.toggle('is-hidden', visible);
    btn.classList.toggle('fm-toggle-active', !visible);
  });
}

function setupFMClearRecent() {
  const btn = document.getElementById('fm-clear-recent');
  if (!btn) return;
  btn.addEventListener('click', () => {
    fmRecentFiles = [];
    saveFMRecent();
    renderFMRecent();
  });
}

async function performFMSearch(query) {
  const treeEl = document.getElementById('fm-tree');
  if (!treeEl) return;
  treeEl.innerHTML = '<span class="fm-loading">🔍 Searching...</span>';

  try {
    const res = await fetch(`/api/files/search?source=${encodeURIComponent(fmCurrentSource)}&q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const results = data.results || [];

    if (results.length === 0) {
      treeEl.innerHTML = '<div class="fm-no-results">No files found</div>';
      return;
    }

    treeEl.innerHTML = results.map(r => {
      const icon = r.is_binary ? (/\.(png|jpg|jpeg|gif|webp|svg|bmp)$/i.test(r.ext) ? '🖼️' : '📎') : '📄';
      return `<div class="fm-search-result" data-path="${escapeHtml(r.path)}">
        <span class="fm-file-icon">${icon}</span>
        <span class="fm-file-name">${escapeHtml(r.name)}</span>
        <span class="fm-file-size">${formatBytes(r.size_bytes)}</span>
      </div>`;
    }).join('');

    treeEl.querySelectorAll('.fm-search-result').forEach(el => {
      el.addEventListener('click', () => openFMFile(el.dataset.path));
    });
  } catch (e) {
    treeEl.innerHTML = `<span class="fm-error-text">⚠️ ${escapeHtml(e.message)}</span>`;
  }
}

async function loadFMStats() {
  const el = document.getElementById('fm-stats');
  if (!el) return;
  el.textContent = '…';

  try {
    const res = await fetch('/api/files/statistics');
    if (!res.ok) return;
    const data = await res.json();
    const sources = data.sources || {};
    const src = sources[fmCurrentSource];
    if (src && src.available) {
      el.textContent = `📄 ${src.total_files} files · ${((src.total_size_bytes || 0) / (1024 * 1024)).toFixed(1)} MB`;
    } else {
      el.textContent = '⚠️ Source not available';
    }
  } catch {
    el.textContent = '—';
  }
}

async function loadFMTree() {
  const treeEl = document.getElementById('fm-tree');
  if (!treeEl) return;
  treeEl.innerHTML = '<span class="fm-loading">Loading directory tree…</span>';

  try {
    const res = await fetch(`/api/files/tree?source=${encodeURIComponent(fmCurrentSource)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const tree = await res.json();

    if (!tree.available) {
      treeEl.innerHTML = `<span class="fm-error-text">⚠️ ${escapeHtml(tree.error || 'Source not available')}</span>`;
      return;
    }

    treeEl.innerHTML = '';
    renderFMTree(tree, treeEl, 0);
  } catch (e) {
    treeEl.innerHTML = `<span class="fm-error-text">⚠️ ${escapeHtml(e.message)}</span>`;
  }
}

function renderFMTree(node, container, depth) {
  if (!node.children || node.children.length === 0) {
    if (depth === 0) {
      container.innerHTML = '<div class="fm-empty">(empty)</div>';
    }
    return;
  }

  // Keep the general tree alphabetical, but order experiment directories by manifest time.
  const sorted = [...node.children].sort((a, b) => {
    if (node.path === 'experiments' && a.type === 'directory' && b.type === 'directory') {
      const aTime = Date.parse(a.created_at || '');
      const bTime = Date.parse(b.created_at || '');
      const aHasTime = !Number.isNaN(aTime);
      const bHasTime = !Number.isNaN(bTime);
      if (aHasTime && bHasTime && aTime !== bTime) {
        return fmExperimentSort === 'oldest' ? aTime - bTime : bTime - aTime;
      }
      if (aHasTime !== bHasTime) return aHasTime ? -1 : 1;
    }
    if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
    return a.name.localeCompare(b.name);
  });

  const ul = document.createElement('ul');
  ul.className = 'fm-tree-list';

  sorted.forEach(child => {
    const li = document.createElement('li');
    li.className = 'fm-tree-item';

    if (child.type === 'directory') {
      li.className += ' fm-tree-dir';
      li.style.cursor = 'pointer';

      const label = document.createElement('span');
      label.className = 'fm-dir-label';
      label.textContent = '📁 ' + child.name;

      li.appendChild(label);

      const childContainer = document.createElement('div');
      childContainer.className = 'fm-dir-children is-hidden';

      li.onclick = (event) => {
        if (event.target.closest('.fm-tree-file, .fm-dir-children')) return;
        const expanded = childContainer.classList.contains('is-hidden');
        childContainer.classList.toggle('is-hidden', !expanded);
        li.classList.toggle('fm-dir-expanded', expanded);
        if (!childContainer.dataset.loaded) {
          renderFMTree(child, childContainer, depth + 1);
          childContainer.dataset.loaded = 'true';
        }
      };

      li.appendChild(childContainer);
    } else {
      li.className += ' fm-tree-file';
      li.style.cursor = 'pointer';
      const icon = child.is_image ? '🖼️' :
                   child.is_video ? '🎬' :
                   child.is_audio ? '🎵' :
                   child.is_spreadsheet ? '📊' :
                   child.is_document ? '📘' :
                   child.is_binary ? '📦' : '📄';
      li.innerHTML = `${icon} ${escapeHtml(child.name)} <span class="fm-file-size">${formatBytes(child.size_bytes)}</span>`;
      li.addEventListener('click', (event) => {
        event.stopPropagation();
        openFMFile(child.path);
      });
    }

    ul.appendChild(li);
  });

  container.appendChild(ul);
}

function ensureFMViewerDialog() {
  let dialog = document.getElementById('fm-viewer-dialog');
  if (dialog) return dialog;
  dialog = document.createElement('dialog');
  dialog.id = 'fm-viewer-dialog';
  dialog.className = 'fm-viewer-dialog';
  dialog.innerHTML = '<div class="fm-viewer-dialog-frame"><div class="fm-viewer-dialog-main"><header><h2>Datei-Vorschau</h2><button type="button" id="fm-dialog-back" class="icon-btn" title="Zurück" aria-label="Zurück">←</button><button type="button" id="fm-dialog-close" class="icon-btn" title="Schließen" aria-label="Schließen">×</button></header><div id="fm-dialog-viewer" class="fm-viewer-content"></div></div></div>';
  document.body.appendChild(dialog);
  dialog.querySelector('#fm-dialog-close').addEventListener('click', () => closeFMViewer());
  dialog.querySelector('#fm-dialog-back').addEventListener('click', () => goBackFMViewer());
  dialog.addEventListener('click', (event) => { if (event.target === dialog) closeFMViewer(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && dialog.open) closeFMViewer(); });
  return dialog;
}

export async function openFMFile(path, { recordHistory = true } = {}) {
  // Use popup or tab viewer based on checkbox
  const usePopup = fmUsePopup;
  let viewer;
  if (usePopup) {
    const dialog = ensureFMViewerDialog();
    dialog.showModal();
    viewer = document.getElementById('fm-dialog-viewer');
  } else {
    viewer = document.getElementById('fm-viewer');
    if (viewer) {
      viewer.classList.remove('fm-viewer-hidden');
      document.body.classList.remove('fm-viewer-open');
    }
  }
  if (!viewer) return;
  path = String(path || '').replaceAll('\\', '/');
  const source = fmCurrentSource;
  if (recordHistory && fmCurrentPath && (fmCurrentPath !== path || fmCurrentFileSource !== source)) {
    fmViewerHistory.push({ source: fmCurrentFileSource || source, path: fmCurrentPath });
  }
  fmCurrentPath = path;
  fmCurrentFileSource = source;
  document.body.classList.add('fm-viewer-open');
  addFMRecent(path, path.split('/').pop() || path, source);
  await renderFile(viewer, { source, path }, {
    onClose: closeFMViewer,
    onBack: goBackFMViewer,
    onChange: refreshFileManager,
    onOpen: (reference) => { fmCurrentSource = reference.source; updateFMBreadcrumb(); openFMFile(reference.path); },
    onReady: (data, { actions }) => {
      for (const [label, loader] of [['History', loadFMHistory], ['Analyse', loadFMAnalyze], ['Notizen', loadFMMeta]]) {
        if (label === 'Notizen' && data.read_only) continue;
        const panel = document.createElement('div'); panel.classList.add('is-hidden'); viewer.append(panel);
        actions.append(iconButton(label, () => loader(path, source, panel)));
      }
      const aiPanel = document.createElement('div'); aiPanel.classList.add('is-hidden'); viewer.append(aiPanel);
      actions.append(iconButton('KI-Analyse', () => loadFMAIAnalysis(path, source, aiPanel, data)));
      const exportBtn = iconButton('Export', () => {
        const format = window.prompt('Export: html, docx oder md', 'html');
        if (['html', 'docx', 'md'].includes(format)) window.open(`/api/files/export/${encodeURIComponent(path)}?source=${encodeURIComponent(source)}&format=${format}`, '_blank', 'noopener');
      });
      if (!data.truncated && ['text', 'markdown', 'json', 'table', 'formula'].includes(data.kind)) actions.append(exportBtn);
    }
  });
}

async function closeFMViewer() {
  const dialog = document.getElementById('fm-viewer-dialog');
  if (dialog?.open) dialog.close();
  document.body.classList.remove('fm-viewer-open');
}

async function goBackFMViewer() {
  const previous = fmViewerHistory.pop();
  if (!previous) { closeFMViewer(); return; }
  fmCurrentSource = previous.source;
  document.querySelectorAll('.fm-source-btn').forEach((button) => {
    button.classList.toggle('active', button.dataset.source === fmCurrentSource);
  });
  updateFMBreadcrumb();
  await openFMFile(previous.path, { recordHistory: false });
}

async function loadFMHistory(path, source, container) {
  container.classList.toggle('is-hidden');
  if (container.classList.contains('is-hidden') || container.dataset.loaded) return;

  container.innerHTML = '<div class="fm-history-loading">Loading history…</div>';
  try {
    const encodedPath = encodeURIComponent(path);
    const res = await fetch(`/api/files/history/${encodedPath}?source=${encodeURIComponent(source)}`);
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);

    if (!data.history || data.history.length === 0) {
      container.innerHTML = '<div class="fm-history-empty">No Git history found for this file.</div>';
      container.dataset.loaded = 'true';
      return;
    }

    let html = '<div class="fm-history-list">';
    data.history.forEach(commit => {
      const shortHash = commit.hash.substring(0, 8);
      html += `
        <div class="fm-history-item">
          <div class="fm-history-meta">
            <code class="fm-history-hash">${escapeHtml(shortHash)}</code>
            <span class="fm-history-date">${escapeHtml(commit.date)}</span>
            <span class="fm-history-author">${escapeHtml(commit.author)}</span>
          </div>
          <div class="fm-history-message">${escapeHtml(commit.message)}</div>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;
    container.dataset.loaded = 'true';
  } catch (e) {
    container.innerHTML = `<div class="fm-history-empty">⚠️ ${escapeHtml(e.message)}</div>`;
  }
}

async function loadFMAnalyze(path, source, container) {
  container.classList.toggle('is-hidden');
  if (container.classList.contains('is-hidden') || container.dataset.loaded) return;

  container.innerHTML = '<div class="fm-analyze-loading">Analyzing…</div>';
  try {
    const encodedPath = encodeURIComponent(path);
    const res = await fetch(`/api/files/analyze/${encodedPath}?source=${encodeURIComponent(source)}`);
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);

    const stats = data.stats || {};
    const readability = data.readability || {};
    const keywords = data.keywords || [];
    const sentiment = data.sentiment || {};
    const summary = data.summary || '';
    const language = data.language || 'unknown';

    const keywordHtml = keywords.length
      ? `<div class="fm-analyze-keywords">${keywords.map(k => `<span class="fm-analyze-keyword">${escapeHtml(k.word)} (${k.count})</span>`).join('')}</div>`
      : '<div class="fm-analyze-empty">No keywords extracted.</div>';

    container.innerHTML = `
      <div class="fm-analyze-header">
        <span class="fm-analyze-title">🤖 Document analysis</span>
        <span class="fm-analyze-lang">Language: ${escapeHtml(language)}</span>
      </div>
      <div class="fm-analyze-grid">
        <div class="fm-analyze-stat"><strong>${stats.words || 0}</strong> words</div>
        <div class="fm-analyze-stat"><strong>${stats.lines || 0}</strong> lines</div>
        <div class="fm-analyze-stat"><strong>${stats.sentences || 0}</strong> sentences</div>
        <div class="fm-analyze-stat"><strong>${stats.chars || 0}</strong> chars</div>
      </div>
      <div class="fm-analyze-row">
        <div class="fm-analyze-block">
          <h4>Readability</h4>
          <div class="fm-analyze-readability">${escapeHtml(readability.label || 'n/a')}: <strong>${readability.score !== undefined ? readability.score : 'n/a'}</strong></div>
        </div>
        <div class="fm-analyze-block">
          <h4>Sentiment</h4>
          <div class="fm-analyze-sentiment fm-analyze-sentiment-${escapeHtml(sentiment.label || 'neutral')}">${escapeHtml(sentiment.label || 'neutral')} (${sentiment.score || 0})</div>
        </div>
      </div>
      <div class="fm-analyze-block">
        <h4>Keywords</h4>
        ${keywordHtml}
      </div>
      <div class="fm-analyze-block">
        <h4>Summary</h4>
        <p class="fm-analyze-summary">${escapeHtml(summary)}</p>
      </div>
    `;
    container.dataset.loaded = 'true';
  } catch (e) {
    container.innerHTML = `<div class="fm-analyze-loading">⚠️ ${escapeHtml(e.message)}</div>`;
  }
}

async function loadFMAIAnalysis(path, source, container, data) {
  container.classList.toggle('is-hidden');
  if (container.classList.contains('is-hidden') || container.dataset.loaded) return;
  container.replaceChildren(document.createElement('p'));
  container.firstChild.textContent = 'Zentrale KI analysiert das Dokument ...';
  const content = String(data?.raw_content ?? data?.content ?? '').slice(0, 16000);
  try {
    const response = await fetch('/api/research/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `Analysiere die Datei ${source}/${path}. Fuehre keinen Code aus. Trenne Beobachtung, technische Einordnung, Risiken, offene Fragen und naechste menschliche Pruefung. Zitiere den exakten Dateipfad.`,
        response_mode: 'scientific',
        conversation_context: `GEZIELTE DATEI FUER DIE ANALYSE:\n[${source}/${path}]\n${content}`,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    container.replaceChildren();
    renderMessage(container, payload.answer || 'Keine Analyse erhalten.', []);
    container.dataset.loaded = 'true';
  } catch (error) {
    const errorNode = document.createElement('p');
    errorNode.className = 'fm-analyze-empty';
    errorNode.textContent = `KI-Analyse nicht verfuegbar: ${error.message}`;
    container.replaceChildren(errorNode);
  }
}

async function loadFMMeta(path, source, container) {
  container.classList.toggle('is-hidden');
  if (container.classList.contains('is-hidden') || container.dataset.loaded) return;

  container.innerHTML = '<div class="fm-meta-loading">Loading notes…</div>';
  try {
    const encodedPath = encodeURIComponent(path);
    const res = await fetch(`/api/files/meta/${encodedPath}?source=${encodeURIComponent(source)}`);
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);

    const initialContent = data.content || `# File notes for ${path}\nstatus: draft\ntags: []\n`;
    container.innerHTML = `
      <div class="fm-meta-header">
        <span class="fm-meta-title">📝 File notes</span>
        <span class="fm-meta-path">${escapeHtml(data.meta_path || path + '.meta.yaml')}</span>
        <button class="fm-meta-save-btn" id="fm-meta-save">💾 Save</button>
      </div>
      <textarea class="fm-meta-textarea" id="fm-meta-textarea">${escapeHtml(initialContent)}</textarea>
      <div class="fm-meta-status" id="fm-meta-status"></div>
    `;
    container.dataset.loaded = 'true';

    const saveBtn = document.getElementById('fm-meta-save');
    const textarea = document.getElementById('fm-meta-textarea');
    const status = document.getElementById('fm-meta-status');

    async function saveMeta() {
      saveBtn.disabled = true;
      status.textContent = 'Saving…';
      try {
        const putRes = await fetch(`/api/files/meta/${encodedPath}?source=${encodeURIComponent(source)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: textarea.value, backup: true }),
        });
        const putData = await putRes.json();
        if (!putRes.ok || putData.error) throw new Error(putData.error || `HTTP ${putRes.status}`);
        status.textContent = `Saved ${new Date().toLocaleTimeString()} — ${formatBytes(putData.size_bytes || 0)}`;
        status.classList.remove('fm-meta-error');
      } catch (e) {
        status.textContent = `Error: ${e.message}`;
        status.classList.add('fm-meta-error');
      } finally {
        saveBtn.disabled = false;
      }
    }

    saveBtn.addEventListener('click', saveMeta);
    textarea.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        saveMeta();
      }
    });
  } catch (e) {
    container.innerHTML = `<div class="fm-meta-loading">⚠️ ${escapeHtml(e.message)}</div>`;
  }
}

// ── Unknown-State Icons ────────────────────────────────────────
// Four distinct states: measured empty, not present, not loaded (lazy), stale
function unknownStateIcon(state) {
  switch (state) {
    case 'empty': return '<span class="fm-state-empty" title="Vorhanden, aber kein Inhalt">◇</span>';
    case 'absent': return '<span class="fm-state-absent" title="Nicht vorhanden / fehlt">○</span>';
    case 'stale': return '<span class="fm-state-stale" title="Veraltet – nicht mehr aktuell">◌</span>';
    default: return '<span class="fm-state-loading" title="Nicht geladen (Lazy)">…</span>';
  }
}

// ── DATA/EVID visual separation ────────────────────────────────
function sourceBadge(source) {
  if (source === 'research') return '<span class="fm-source-badge fm-source-data">DATA</span>';
  if (source === 'docs') return '<span class="fm-source-badge fm-source-docs">DOCS</span>';
  return '';
}

// ── Provenance Side-Panel ──────────────────────────────────────
function ensureProvenancePanel() {
  let panel = document.getElementById('fm-provenance-panel');
  if (panel) return panel;
  panel = document.createElement('aside');
  panel.id = 'fm-provenance-panel';
  panel.className = 'fm-provenance-panel is-hidden';
  panel.innerHTML = '<header><span class="workspace-kicker">PROVENIENZ</span><h3>Artefakt-Metadaten</h3><button type="button" class="icon-btn" id="fm-provenance-close" title="Schließen">×</button></header><div id="fm-provenance-body"></div>';
  document.getElementById('fm-viewer-dialog')?.querySelector('.fm-viewer-dialog-frame')?.append(panel);
  panel.querySelector('#fm-provenance-close')?.addEventListener('click', () => panel.classList.add('is-hidden'));
  return panel;
}

async function loadProvenance(path, source) {
  const panel = ensureProvenancePanel();
  const body = document.getElementById('fm-provenance-body');
  if (!body) return;
  panel.classList.remove('is-hidden');
  body.innerHTML = '<div class="fm-meta-loading">Lade Provenienz …</div>';
  try {
    const res = await fetch(`/api/files/provenance/${encodeURIComponent(path)}?source=${encodeURIComponent(source)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    body.innerHTML = `<dl class="fm-prov-dl">
      <dt>Pfad</dt><dd><code>${escapeHtml(data.path || path)}</code><button class="fm-copy-btn" data-copy="${escapeHtml(data.path || path)}" title="Pfad kopieren">📋</button></dd>
      <dt>Größe</dt><dd>${formatBytes(data.size_bytes)}</dd>
      <dt>Geändert</dt><dd>${escapeHtml(data.mtime || '—')}</dd>
      <dt>Erstellt</dt><dd>${escapeHtml(data.ctime || '—')}</dd>
      <dt>Hash (SHA256)</dt><dd><code>${escapeHtml((data.hash || '').slice(0, 16))}…</code><button class="fm-copy-btn" data-copy="${escapeHtml(data.hash || '')}" title="Hash kopieren">📋</button></dd>
      <dt>Experiment-ID</dt><dd>${data.experiment_id ? `<code>${escapeHtml(data.experiment_id)}</code><button class="fm-copy-btn" data-copy="${escapeHtml(data.experiment_id)}" title="ID kopieren">📋</button>` : '<span class="fm-state-absent">—</span>'}</dd>
      <dt>Git-Commit</dt><dd><code>${escapeHtml((data.git_commit || '').slice(0, 12))}…</code></dd>
      <dt>Source</dt><dd>${sourceBadge(source)}</dd>
      <dt>Status</dt><dd>${data.available === false ? unknownStateIcon('absent') + ' nicht verfügbar' : data.size_bytes === 0 ? unknownStateIcon('empty') + ' leer' : unknownStateIcon('loaded') + ' verfügbar'}</dd>
    </dl>`;
    body.querySelectorAll('.fm-copy-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(btn.dataset.copy); btn.textContent = '✓'; setTimeout(() => btn.textContent = '📋', 1500); }
        catch { btn.textContent = '✗'; }
      });
    });
  } catch (e) {
    body.innerHTML = `<span class="fm-error-text">⚠️ ${escapeHtml(e.message)}</span>`;
  }
}

// ── Keyboard navigation & multi-select ─────────────────────────
let fmSelectedIndices = new Set();
let fmLastSelectedIndex = -1;

function setupFMKeyboardNav() {
  document.addEventListener('keydown', (event) => {
    const tree = document.getElementById('fm-tree');
    if (!tree || !tree.isConnected) return;
    const items = [...tree.querySelectorAll('.fm-tree-file, .fm-tree-dir')];
    if (!items.length) return;
    const target = event.target;
    if (!tree.contains(target) && target.tagName !== 'BODY') return;

    // Only handle if no input is focused
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) return;

    let focused = items.indexOf(document.querySelector('.fm-tree-focused'));
    if (focused === -1) focused = 0;

    switch (event.key) {
      case 'j': case 'ArrowDown':
        event.preventDefault();
        focused = Math.min(focused + 1, items.length - 1);
        break;
      case 'k': case 'ArrowUp':
        event.preventDefault();
        focused = Math.max(focused - 1, 0);
        break;
      case 'Enter': case ' ':
        event.preventDefault();
        const item = items[focused];
        if (item.classList.contains('fm-tree-file')) {
          const path = item.dataset.path || item.querySelector('[data-path]')?.dataset.path || '';
          if (path) openFMFile(path);
        } else if (item.classList.contains('fm-tree-dir')) {
          item.click();
        }
        return;
      case '/':
        if (event.key === '/') {
          event.preventDefault();
          const searchInput = document.getElementById('fm-search');
          if (searchInput) searchInput.focus();
        }
        return;
      default: return;
    }

    items.forEach(el => el.classList.remove('fm-tree-focused'));
    items[focused].classList.add('fm-tree-focused');
    items[focused].scrollIntoView({ block: 'nearest' });
  });
}

// ── Expose provenance on file click ────────────────────────────
function patchFMOpenWithProvenance() {
  const origOpen = openFMFile;
  const patchedOpen = async (path, opts) => {
    const result = await origOpen(path, opts);
    loadProvenance(path, fmCurrentSource);
    return result;
  };
  window.__fmOpenPatched = true;
  // We override the export by patching the module's reference
  // Since we can't easily do that, we add a click listener on the tree
  document.addEventListener('click', (event) => {
    const fileEl = event.target.closest('.fm-tree-file');
    if (fileEl) {
      const path = fileEl.dataset.path || '';
      if (path) setTimeout(() => loadProvenance(path, fmCurrentSource), 100);
    }
  });
}

// ── Init extensions ────────────────────────────────────────────
function initFMAdvanced() {
  setupFMKeyboardNav();
  patchFMOpenWithProvenance();
}

// Patch initFileManager to include advanced features
const origInit = initFileManager;
initFileManager = function() {
  if (!origInit()) return false;
  initFMAdvanced();
  return true;
};

function initResearchBrowser() { initFileManager(); }
function initDocumentationBrowser() { initFileManager(); }

export function openDocumentationFile(path) {
  initFileManager();
  fmCurrentSource = 'docs';
  document.querySelectorAll('.fm-source-btn').forEach((button) => {
    button.classList.toggle('active', button.dataset.source === 'docs');
  });
  updateFMBreadcrumb();
  return openFMFile(path);
}

export function openBrain5DFile(source, path) {
  if (!['docs', 'research'].includes(source) || typeof path !== 'string') return Promise.resolve(null);
  initFileManager();
  fmCurrentSource = source;
  document.querySelectorAll('.fm-source-btn').forEach((button) => {
    button.classList.toggle('active', button.dataset.source === source);
  });
  updateFMBreadcrumb();
  return openFMFile(path);
}

window.openBrain5DFile = openBrain5DFile;
document.addEventListener('brain5d:open-file', (event) => {
  const detail = event.detail || {};
  openBrain5DFile(detail.source, detail.path);
});

// ================================================================
// Markdown / CSV rendering helpers
// ================================================================

export { initFileManager, initResearchBrowser, initDocumentationBrowser, refreshFileManager };
