/**
 * Brain-5D Operator Dashboard – Unified File Manager Module
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

import { initBibTeXViewer, wireBibTeXEvents } from './bibtex-viewer.js';

// ================================================================
// Local helpers (mirrored from app.js to keep this module standalone)
// ================================================================

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
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

const FM_EDITABLE_EXTS = new Set([
  '.md', '.markdown', '.txt', '.text', '.py', '.js', '.ts', '.mjs',
  '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
  '.bib', '.patch', '.diff', '.tex', '.rst', '.dockerfile', '.sh', '.bat', '.ps1',
  '.xml', '.html', '.css', '.c', '.cpp', '.h', '.hpp', '.rs', '.go', '.java', '.kt',
]);

function isFMEditable(ext) {
  if (!ext) return false;
  const lower = ext.toLowerCase();
  return FM_EDITABLE_EXTS.has(lower);
}

function fmLangFromExt(ext) {
  const map = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.mjs': 'javascript',
    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.toml': 'ini', '.ini': 'ini',
    '.cfg': 'ini', '.conf': 'ini', '.config': 'ini', '.md': 'markdown',
    '.markdown': 'markdown', '.tex': 'latex', '.sh': 'shell', '.ps1': 'powershell',
    '.bat': 'bat', '.xml': 'xml', '.html': 'html', '.css': 'css',
    '.c': 'cpp', '.cpp': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
    '.rs': 'rust', '.go': 'go', '.java': 'java', '.kt': 'kotlin',
  };
  return map[ext.toLowerCase()] || 'plaintext';
}

// ================================================================
// Module state
// ================================================================

let fmInitialized = false;
let fmCurrentSource = 'research';
let fmActiveFilter = 'all';
let fmExperimentSort = 'newest';
let fmRecentFiles = [];
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
    list.innerHTML = '<div class="fm-empty" style="padding:12px;">(no recent files)</div>';
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
  if (select) select.disabled = fmCurrentSource !== 'research';
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
    items.forEach(el => el.style.display = '');
    return;
  }
  const exts = fmActiveFilter.split(',');
  items.forEach(el => {
    const label = el.querySelector('.fm-file-label');
    if (!label) return;
    const name = label.textContent || '';
    const ext = '.' + name.split('.').pop().split(' ')[0].toLowerCase();
    const match = exts.some(e => name.toLowerCase().endsWith(e) || ext === e);
    el.style.display = match ? '' : 'none';
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
    const visible = panel.style.display !== 'none';
    panel.style.display = visible ? 'none' : 'block';
    btn.style.opacity = visible ? '' : '1';
    btn.style.color = visible ? '' : '#7aabff';
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
    treeEl.innerHTML = `<span style="color:#f06070;">⚠️ ${escapeHtml(e.message)}</span>`;
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
      treeEl.innerHTML = `<span style="color:#f06070;">⚠️ ${escapeHtml(tree.error || 'Source not available')}</span>`;
      return;
    }

    treeEl.innerHTML = '';
    renderFMTree(tree, treeEl, 0);
  } catch (e) {
    treeEl.innerHTML = `<span style="color:#f06070;">⚠️ ${escapeHtml(e.message)}</span>`;
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
      const toggle = document.createElement('span');
      toggle.className = 'fm-dir-toggle';
      toggle.textContent = '▶';
      toggle.style.display = 'inline-block';
      toggle.style.transition = 'transform 0.15s';

      const label = document.createElement('span');
      label.className = 'fm-dir-label';
      label.textContent = '📁 ' + child.name;

      li.appendChild(toggle);
      li.appendChild(label);

      const childContainer = document.createElement('div');
      childContainer.className = 'fm-dir-children';
      childContainer.style.display = 'none';

      toggle.onclick = () => {
        const expanded = childContainer.style.display !== 'none';
        childContainer.style.display = expanded ? 'none' : 'block';
        toggle.style.transform = expanded ? 'rotate(0deg)' : 'rotate(90deg)';
        // Load children lazily on first expand
        if (!childContainer.dataset.loaded) {
          renderFMTree(child, childContainer, depth + 1);
          childContainer.dataset.loaded = 'true';
        }
      };

      li.appendChild(childContainer);
    } else {
      li.className += ' fm-tree-file';
      const icon = child.is_image ? '🖼️' :
                   child.is_video ? '🎬' :
                   child.is_audio ? '🎵' :
                   child.is_spreadsheet ? '📊' :
                   child.is_document ? '📘' :
                   child.is_binary ? '📦' : '📄';
      const label = document.createElement('span');
      label.className = 'fm-file-label';
      label.innerHTML = `${icon} ${escapeHtml(child.name)} <span class="fm-file-size">${formatBytes(child.size_bytes)}</span>`;
      label.addEventListener('click', () => openFMFile(child.path));

      li.appendChild(label);
    }

    ul.appendChild(li);
  });

  container.appendChild(ul);
}

async function openFMFile(path) {
  const viewer = document.getElementById('fm-viewer');
  if (!viewer) return;
  // Show viewer (it may be hidden in overlay mode)
  viewer.classList.remove('fm-viewer-hidden');
  viewer.innerHTML = '<div class="fm-loading">📂 Loading file…</div>';

  // Extract name from path for recent files
  const fileName = path.split('/').pop() || path;
  addFMRecent(path, fileName, fmCurrentSource);

  try {
    const res = await fetch(`/api/files/content/${encodeURIComponent(path)}?source=${encodeURIComponent(fmCurrentSource)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
      viewer.innerHTML = `<div class="fm-error">⚠️ ${escapeHtml(err.error || 'Failed to load file')}</div>`;
      return;
    }

    const contentType = res.headers.get('Content-Type') || '';
    if (contentType.startsWith('image/')) {
      // Image file: render inline
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      viewer.innerHTML = `
        <div class="fm-file-header">
          <span>${escapeHtml(path)}</span>
          <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
        </div>
        <div class="fm-image-container">
          <img src="${url}" alt="${escapeHtml(path)}" class="fm-image" />
        </div>
      `;
      document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
        viewer.classList.add('fm-viewer-hidden');
      });
    } else if (contentType.startsWith('video/')) {
      // Video file: render with video player
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      viewer.innerHTML = `
        <div class="fm-file-header">
          <span>${escapeHtml(path)}</span>
          <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
        </div>
        <div class="fm-video-container">
          <video controls class="fm-video">
            <source src="${url}" type="${escapeHtml(contentType)}">
            Your browser does not support video playback.
          </video>
        </div>
      `;
      document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
        viewer.classList.add('fm-viewer-hidden');
      });
    } else if (contentType.startsWith('audio/')) {
      // Audio file: render with audio player
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      viewer.innerHTML = `
        <div class="fm-file-header">
          <span>${escapeHtml(path)}</span>
          <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
        </div>
        <div class="fm-audio-container">
          <audio controls class="fm-audio">
            <source src="${url}" type="${escapeHtml(contentType)}">
            Your browser does not support audio playback.
          </audio>
        </div>
      `;
      document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
        viewer.classList.add('fm-viewer-hidden');
      });
    } else if (contentType === 'application/pdf') {
      // PDF file: render inline with iframe
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      viewer.innerHTML = `
        <div class="fm-file-header">
          <span>${escapeHtml(path)}</span>
          <div class="fm-file-header-actions">
            <a href="${url}" download="${escapeHtml(path.split('/').pop() || 'document.pdf')}" class="fm-file-copy-btn">⬇️ Download</a>
            <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
          </div>
        </div>
        <div class="fm-pdf-container">
          <iframe class="fm-pdf-frame" src="${url}" title="${escapeHtml(path)}"></iframe>
        </div>
      `;
      document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
        viewer.classList.add('fm-viewer-hidden');
      });
    } else if (/\.(xlsx|xls|xlsm|ods)$/i.test(path)) {
      // Spreadsheet: parse with SheetJS and render first sheet as table
      const blob = await res.blob();
      const arrayBuffer = await blob.arrayBuffer();
      await renderSpreadsheet(path, arrayBuffer, viewer);
      return;
    } else if (/\.(docx|doc)$/i.test(path)) {
      // Word document: convert to HTML with mammoth.js
      const blob = await res.blob();
      const arrayBuffer = await blob.arrayBuffer();
      await renderDocx(path, arrayBuffer, viewer);
      return;
    } else if (/\.(ipynb)$/i.test(path)) {
      // Jupyter notebook: render structured cells
      const data = await res.json();
      renderIPythonNotebook(path, data.content || '', viewer);
      return;
    } else if (/\.(log)$/i.test(path)) {
      // Log file: render with level highlighting
      const data = await res.json();
      renderLogFile(path, data.content || '', viewer);
      return;
    } else if (/\.(dot)$/i.test(path)) {
      // Graphviz DOT file
      const data = await res.json();
      renderGraphviz(path, data.content || '', viewer);
      return;
    } else if (/\.(puml|plantuml)$/i.test(path)) {
      // PlantUML file
      const data = await res.json();
      renderPlantUML(path, data.content || '', viewer);
      return;
    } else if (path.toLowerCase().endsWith('.bib')) {
      // BibTeX file: use dedicated structured viewer
      const data = await res.json();
      const content = data.content || '';
      const ext = (data.ext || '').toLowerCase();

      viewer.innerHTML = `
        <div class="fm-file-header">
          <h3>${escapeHtml(data.name || path)}</h3>
          <div class="fm-file-header-actions">
            <span class="fm-file-meta">${formatBytes(data.size_bytes || 0)}</span>
            <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
          </div>
        </div>
        <div class="fm-content">${initBibTeXViewer(content, data.name || path, path, source)}</div>
      `;

      // Wire up the close button
      const closeBtn = document.getElementById('fm-close-viewer');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          viewer.classList.add('fm-viewer-hidden');
        });
      }

      // Wire up BibTeX-specific event handlers
      wireBibTeXEvents();
    } else {
      // Text file: render as JSON
      const data = await res.json();
      const content = data.content || '';
      const ext = (data.ext || '').toLowerCase();

      const editable = isFMEditable(ext);
      viewer.innerHTML = `
        <div class="fm-file-header">
          <h3>${escapeHtml(data.name || path)}</h3>
          <div class="fm-file-header-actions">
            <span class="fm-file-meta">${formatBytes(data.size_bytes || 0)}</span>
            <button class="fm-file-action-btn" id="fm-file-search" title="Find in document (Ctrl+F)">🔍 Search</button>
            <button class="fm-file-action-btn" id="fm-file-history" title="Git history">🕰️ History</button>
            <button class="fm-file-action-btn" id="fm-file-notes" title="File notes / metadata">📝 Notes</button>
            <button class="fm-file-action-btn" id="fm-file-analyze" title="Analyze document">🤖 Analyze</button>
            <button class="fm-file-action-btn" id="fm-file-export" title="Export document">⬇️ Export</button>
            <button class="fm-file-action-btn" id="fm-file-fullscreen" title="Toggle fullscreen">🖥️ Full</button>
            ${editable ? `<button class="fm-file-edit-btn" id="fm-file-edit" title="Edit file">✏️ Edit</button>` : ''}
            <button class="fm-file-copy-btn" id="fm-file-copy-all" data-content="${escapeHtml(content)}">📋 Copy all</button>
            <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
          </div>
        </div>
        <div class="fm-content" id="fm-content">${renderFMContent(content, ext, path)}</div>
        <div class="fm-history-panel" id="fm-history-panel" style="display:none;"></div>
        <div class="fm-meta-panel" id="fm-meta-panel" style="display:none;"></div>
        <div class="fm-analyze-panel" id="fm-analyze-panel" style="display:none;"></div>
      `;

      viewer.querySelectorAll('.fm-md-link[data-fm-path]').forEach(link => {
        link.addEventListener('click', (event) => {
          event.preventDefault();
          openFMFile(link.dataset.fmPath);
        });
      });

      // Wire up the close button
      const closeBtn = document.getElementById('fm-close-viewer');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          viewer.classList.add('fm-viewer-hidden');
        });
      }

      // Wire up the "Copy all" button
      const copyBtn = document.getElementById('fm-file-copy-all');
      if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(content);
            copyBtn.textContent = '✅ Copied!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
              copyBtn.textContent = '📋 Copy all';
              copyBtn.classList.remove('copied');
            }, 2000);
          } catch {
            copyBtn.textContent = '❌ Failed';
          }
        });
      }

      // Wire up the "Edit" button
      const editBtn = document.getElementById('fm-file-edit');
      if (editBtn) {
        editBtn.addEventListener('click', () => {
          activateFMEditor({
            path,
            name: data.name || path,
            content,
            ext,
            source: fmCurrentSource,
            viewer,
          });
        });
      }

      // Wire up search, history, notes, analyze, export and fullscreen buttons
      const searchBtn = document.getElementById('fm-file-search');
      const historyBtn = document.getElementById('fm-file-history');
      const notesBtn = document.getElementById('fm-file-notes');
      const analyzeBtn = document.getElementById('fm-file-analyze');
      const exportBtn = document.getElementById('fm-file-export');
      const fullscreenBtn = document.getElementById('fm-file-fullscreen');
      const contentContainer = document.getElementById('fm-content');
      const historyPanel = document.getElementById('fm-history-panel');
      const metaPanel = document.getElementById('fm-meta-panel');
      const analyzePanel = document.getElementById('fm-analyze-panel');

      if (searchBtn && contentContainer) {
        searchBtn.addEventListener('click', () => createFMSearchBox(contentContainer, () => content));
      }
      if (historyBtn && historyPanel) {
        historyBtn.addEventListener('click', () => loadFMHistory(path, source, historyPanel));
      }
      if (notesBtn && metaPanel) {
        notesBtn.addEventListener('click', () => loadFMMeta(path, source, metaPanel));
      }
      if (analyzeBtn && analyzePanel) {
        analyzeBtn.addEventListener('click', () => loadFMAnalyze(path, source, analyzePanel));
      }
      if (exportBtn) {
        exportBtn.addEventListener('click', () => {
          const fmt = prompt('Export format: html, docx, or md', 'html');
          if (!fmt) return;
          const encodedPath = encodeURIComponent(path);
          window.open(`/api/files/export/${encodedPath}?source=${encodeURIComponent(source)}&format=${encodeURIComponent(fmt)}`, '_blank');
        });
      }
      if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => toggleFMFullscreen(viewer));
      }
      // Global Ctrl+F shortcut when viewer is active
      viewer.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'f') {
          e.preventDefault();
          if (contentContainer) createFMSearchBox(contentContainer, () => content);
        }
      });
    }
  } catch (e) {
    viewer.innerHTML = `<div class="fm-error">⚠️ ${escapeHtml(e.message)}</div>`;
  }
}

async function loadFMHistory(path, source, container) {
  container.style.display = container.style.display === 'none' ? 'block' : 'none';
  if (container.style.display === 'none' || container.dataset.loaded) return;

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
  container.style.display = container.style.display === 'none' ? 'block' : 'none';
  if (container.style.display === 'none' || container.dataset.loaded) return;

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

async function loadFMMeta(path, source, container) {
  container.style.display = container.style.display === 'none' ? 'block' : 'none';
  if (container.style.display === 'none' || container.dataset.loaded) return;

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

function renderFMContent(content, ext, path = '') {
  if (!content) return '<div class="fm-empty">(empty file)</div>';

  // Markdown rendering
  if (ext === '.md' || ext === '.markdown') {
    return renderFMMarkdown(content, path);
  }

  // JSON rendering: also catch .schema.json, .ipynb etc.
  if (ext.endsWith('.json')) {
    try {
      const parsed = JSON.parse(content);
      const formatted = JSON.stringify(parsed, null, 2);
      return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(formatted)}">📋 Copy</button><pre class="fm-code">${escapeHtml(formatted)}</pre></div>`;
    } catch {
      return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(content)}">📋 Copy</button><pre class="fm-code">${escapeHtml(content)}</pre></div>`;
    }
  }

  // Research registry YAML: structured card view
  if ((ext === '.yaml' || ext === '.yml') && path.includes('/registry/')) {
    return renderFMRegistry(content);
  }

  // YAML rendering with syntax highlighting
  if (ext === '.yaml' || ext === '.yml') {
    return renderFMYaml(content);
  }

  // Code/text files with syntax highlighting
  if (['.py', '.js', '.ts', '.css', '.html', '.toml', '.xml', '.cfg', '.conf', '.ini', '.env', '.gitignore', '.log', '.bib', '.patch', '.rst', '.tex', '.sh', '.bat', '.ps1', '.dockerfile', '.cmake', '.makefile', '.txt'].includes(ext)) {
    return renderFMCode(content, ext);
  }

  // CSV rendering as table
  if (ext === '.csv') {
    return renderFMCSV(content);
  }

  // Default: plain text
  return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(content)}">📋 Copy</button><pre class="fm-text">${escapeHtml(content)}</pre></div>`;
}

// ================================================================
// Research registry card renderer
// ================================================================

function renderFMRegistry(content) {
  let items = [];
  try {
    items = parseFMYamlList(content);
  } catch (e) {
    return `<div class="fm-error">⚠️ Could not parse registry YAML: ${escapeHtml(e.message)}</div>`;
  }

  if (!items.length) {
    return '<div class="fm-empty">No registry entries found.</div>';
  }

  let html = '<div class="fm-registry-grid">';
  items.forEach(item => {
    const status = (item.status || 'unknown').toString().toLowerCase();
    const id = item.id || item.ID || '—';
    const title = item.question || item.claim || item.title || item.hypothesis || item.name || item.description || 'Untitled';
    const type = inferRegistryType(item, id);
    const badgeClass = `fm-registry-badge fm-registry-badge-${status}`;
    const confidence = item.answer && item.answer.confidence ? item.answer.confidence : (item.confidence || '—');

    html += `
      <div class="fm-registry-card">
        <div class="fm-registry-card-header">
          <code class="fm-registry-id">${escapeHtml(id)}</code>
          <span class="${badgeClass}">${escapeHtml(status)}</span>
        </div>
        <div class="fm-registry-type">${escapeHtml(type)}</div>
        <div class="fm-registry-title">${escapeHtml(title)}</div>
        ${item.domain ? `<div class="fm-registry-domain">Domain: ${escapeHtml(item.domain)}</div>` : ''}
        ${item.relevance ? `<div class="fm-registry-relevance">${escapeHtml(item.relevance)}</div>` : ''}
        ${renderRegistryLinks(item.literature, 'Literature')}
        ${renderRegistryLinks(item.hypotheses, 'Hypotheses')}
        ${renderRegistryLinks(item.evidence, 'Evidence')}
        ${renderRegistryLinks(item.methods, 'Methods')}
        ${confidence !== '—' ? `<div class="fm-registry-confidence">Confidence: ${escapeHtml(confidence)}</div>` : ''}
        ${item.created ? `<div class="fm-registry-dates">Created ${escapeHtml(item.created)}${item.updated && item.updated !== item.created ? ` · Updated ${escapeHtml(item.updated)}` : ''}</div>` : ''}
      </div>
    `;
  });
  html += '</div>';
  return html;
}

function inferRegistryType(item, id) {
  if (id && id.startsWith('RQ-')) return 'Research Question';
  if (id && id.startsWith('H-')) return 'Hypothesis';
  if (id && id.startsWith('CLAIM-')) return 'Claim';
  if (id && id.startsWith('SRC-')) return 'Source';
  if (id && id.startsWith('EXP-')) return 'Experiment';
  if (id && id.startsWith('METH-')) return 'Method';
  if (item.hypothesis) return 'Hypothesis';
  if (item.question) return 'Research Question';
  if (item.claim) return 'Claim';
  if (item.source) return 'Source';
  return 'Entry';
}

function renderRegistryLinks(list, label) {
  if (!Array.isArray(list) || list.length === 0) return '';
  const links = list.map(ref => `<span class="fm-registry-link">${escapeHtml(ref)}</span>`).join('');
  return `<div class="fm-registry-links"><span class="fm-registry-link-label">${escapeHtml(label)}:</span>${links}</div>`;
}

function parseFMYamlList(text) {
  if (typeof jsyaml !== 'undefined') {
    const parsed = jsyaml.load(text);
    return Array.isArray(parsed) ? parsed : [];
  }
  // Fallback: minimal parser
  const items = [];
  let current = null;
  let inList = null;
  const lines = text.split('\n');
  for (let raw of lines) {
    const line = raw.replace(/\r$/, '');
    if (!line.trim() || line.trim().startsWith('#')) continue;

    const matchTop = line.match(/^(\s*)- id:\s*(.+)$/);
    if (matchTop) {
      if (current) items.push(current);
      current = { id: matchTop[2].trim() };
      inList = null;
      continue;
    }

    const matchListItem = line.match(/^(\s*)-\s+(.+)$/);
    if (matchListItem && current && inList) {
      current[inList].push(matchListItem[2].trim());
      continue;
    }

    const matchKey = line.match(/^(\s*)(\w+):\s*(.*)$/);
    if (matchKey && current) {
      const key = matchKey[2];
      const value = matchKey[3].trim();
      if (value === '') {
        current[key] = [];
        inList = key;
      } else {
        current[key] = value.replace(/^["'](.*)["']$/, '$1');
        inList = null;
      }
    }
  }
  if (current) items.push(current);
  return items;
}

// ================================================================
// (Research browser functions migrated to Unified File Manager)
// ================================================================

function initResearchBrowser() { initFileManager(); }
function initDocumentationBrowser() { initFileManager(); }

// ================================================================
// Markdown / CSV rendering helpers
// ================================================================

function renderFMMarkdown(content, currentPath = '') {
  let html = content;

  // Code blocks (```...```) with language label
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const langLabel = lang ? `<span class="fm-code-lang">${escapeHtml(lang)}</span>` : '';
    return `<div class="fm-code-wrapper">${langLabel}<button class="fm-copy-btn" data-content="${escapeHtml(code.trim())}">📋 Copy</button><pre class="fm-code fm-code-block"><code>${escapeHtml(code.trim())}</code></pre></div>`;
  });

  // Inline code (`...`)
  html = html.replace(/`([^`]+)`/g, '<code class="fm-inline-code">$1</code>');

  // Images: ![alt](url)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
    let imgSrc = src;
    if (!src.startsWith('http://') && !src.startsWith('https://') && !src.startsWith('data:')) {
      imgSrc = `/api/files/content/${encodeURIComponent(src)}?source=${encodeURIComponent(fmCurrentSource)}`;
    }
    return `<img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(alt)}" class="fm-md-image" loading="lazy" />`;
  });

  // Links: keep internal research links inside the unified viewer.
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, target) => {
    if (/^(https?:|mailto:|#)/i.test(target)) {
      return `<a href="${escapeHtml(target)}" target="_blank" rel="noopener" class="fm-md-link">${label}</a>`;
    }
    const base = currentPath.split('/').slice(0, -1);
    target.split('/').forEach(part => {
      if (!part || part === '.') return;
      if (part === '..') base.pop();
      else base.push(part);
    });
    return `<a href="#" data-fm-path="${escapeHtml(base.join('/'))}" class="fm-md-link">${label}</a>`;
  });

  // Headings (### → h4, ## → h3, # → h2)
  html = html.replace(/^### (.+)$/gm, '<h4 class="fm-md-h3">$1</h4>');
  html = html.replace(/^## (.+)$/gm, '<h3 class="fm-md-h2">$1</h3>');
  html = html.replace(/^# (.+)$/gm, '<h2 class="fm-md-h1">$1</h2>');

  // Bold and italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr class="fm-md-hr" />');

  // Blockquotes with optional nested paragraphs
  html = html.replace(/^> (.+)$/gm, '<blockquote class="fm-md-quote"><p>$1</p></blockquote>');

  // Unordered lists
  html = html.replace(/^[\s]*[-*] (.+)$/gm, '<li class="fm-md-li">$1</li>');
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, '<ul class="fm-md-ul">$&</ul>');

  // Ordered lists
  html = html.replace(/^[\s]*\d+\.\s(.+)$/gm, '<li class="fm-md-li">$1</li>');
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, (match) => {
    if (!match.startsWith('<ul')) return '<ol class="fm-md-ol">' + match + '</ol>';
    return match;
  });

  // Tables: | col1 | col2 | (simple pipe tables)
  html = html.replace(/^\|(.+)\|$/gm, (line) => {
    const cells = line.split('|').filter(c => c.trim()).map(c => c.trim());
    // Detect header separator row (|---|)
    if (cells.length > 0 && cells[0].match(/^[-:\s]+$/)) return '';
    return cells.map(c => `<td>${c}</td>`).join('');
  });
  // Wrap consecutive <td> rows in <table>/<tr>
  html = html.replace(/((?:<td>.*<\/td>\n?)+)/g, '<tr>$1</tr>');
  html = html.replace(/((?:<tr>.*<\/tr>\n?)+)/g, '<table class="fm-md-table"><tbody>$1</tbody></table>');

  // Paragraphs: wrap remaining text lines
  html = html.split('\n\n').map(block => {
    const t = block.trim();
    if (!t) return '';
    // Skip blocks that are already HTML
    if (t.startsWith('<')) return t;
    return `<p class="fm-md-p">${t.replace(/\n/g, '<br/>')}</p>`;
  }).join('\n');

  return `<div class="fm-markdown">${html}</div>`;
}

function renderFMCSV(content) {
  const lines = content.split('\n').filter(l => l.trim());
  if (lines.length === 0) return '<div class="fm-empty">(empty CSV)</div>';

  const rows = lines.map(l => {
    // Simple CSV parsing (handles quoted fields)
    const fields = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < l.length; i++) {
      const ch = l[i];
      if (ch === '"') { inQuotes = !inQuotes; continue; }
      if (ch === ',' && !inQuotes) { fields.push(current); current = ''; continue; }
      current += ch;
    }
    fields.push(current);
    return fields;
  });

  const header = rows[0];
  const body = rows.slice(1);

  let html = '<table class="fm-csv-table"><thead><tr>';
  header.forEach(h => { html += `<th>${escapeHtml(h)}</th>`; });
  html += '</tr></thead><tbody>';
  body.slice(0, 500).forEach(row => {
    html += '<tr>';
    for (let i = 0; i < Math.max(row.length, header.length); i++) {
      html += `<td>${escapeHtml(row[i] || '')}</td>`;
    }
    html += '</tr>';
  });
  if (body.length > 500) html += '<tr><td colspan="' + header.length + '" class="fm-csv-truncated">... (truncated, ' + body.length + ' rows total)</td></tr>';
  html += '</tbody></table>';
  return html;
}

// ================================================================
// Spreadsheet renderer (XLSX / XLS / ODS)
// ================================================================

async function renderSpreadsheet(path, arrayBuffer, viewer) {
  if (typeof XLSX === 'undefined') {
    viewer.innerHTML = `<div class="fm-error">⚠️ SheetJS library not loaded.</div>`;
    return;
  }

  try {
    const workbook = XLSX.read(new Uint8Array(arrayBuffer), { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const json = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

    if (!json || json.length === 0) {
      viewer.innerHTML = `<div class="fm-empty">(empty spreadsheet)</div>`;
      return;
    }

    const header = json[0];
    const body = json.slice(1);
    const maxCols = Math.max(header.length, ...body.map(r => r.length));

    const sheetTabs = workbook.SheetNames.map((name, idx) =>
      `<button class="fm-sheet-tab${idx === 0 ? ' active' : ''}" data-sheet="${escapeHtml(name)}">${escapeHtml(name)}</button>`
    ).join('');

    let html = `
      <div class="fm-file-header">
        <span>${escapeHtml(path)}</span>
        <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
      </div>
      <div class="fm-sheet-tabs">${sheetTabs}</div>
      <div class="fm-sheet-viewer">
        <table class="fm-spreadsheet-table"><thead><tr>`;
    for (let i = 0; i < maxCols; i++) {
      html += `<th>${escapeHtml(String(header[i] || `Col ${i + 1}`))}</th>`;
    }
    html += '</tr></thead><tbody>';
    body.slice(0, 500).forEach(row => {
      html += '<tr>';
      for (let i = 0; i < maxCols; i++) {
        html += `<td>${escapeHtml(String(row[i] ?? ''))}</td>`;
      }
      html += '</tr>';
    });
    if (body.length > 500) {
      html += `<tr><td colspan="${maxCols}" class="fm-csv-truncated">... (truncated, ${body.length} rows total)</td></tr>`;
    }
    html += '</tbody></table></div>';

    viewer.innerHTML = html;

    document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
      viewer.classList.add('fm-viewer-hidden');
    });

    viewer.querySelectorAll('.fm-sheet-tab').forEach(tab => {
      tab.addEventListener('click', async () => {
        viewer.querySelectorAll('.fm-sheet-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const name = tab.dataset.sheet;
        const ws = workbook.Sheets[name];
        const data = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
        const h = data[0] || [];
        const b = data.slice(1);
        const cols = Math.max(h.length, ...b.map(r => r.length));
        let t = '<table class="fm-spreadsheet-table"><thead><tr>';
        for (let i = 0; i < cols; i++) {
          t += `<th>${escapeHtml(String(h[i] || `Col ${i + 1}`))}</th>`;
        }
        t += '</tr></thead><tbody>';
        b.slice(0, 500).forEach(row => {
          t += '<tr>';
          for (let i = 0; i < cols; i++) {
            t += `<td>${escapeHtml(String(row[i] ?? ''))}</td>`;
          }
          t += '</tr>';
        });
        if (b.length > 500) {
          t += `<tr><td colspan="${cols}" class="fm-csv-truncated">... (truncated, ${b.length} rows total)</td></tr>`;
        }
        t += '</tbody></table>';
        viewer.querySelector('.fm-sheet-viewer').innerHTML = t;
      });
    });
  } catch (e) {
    viewer.innerHTML = `<div class="fm-error">⚠️ Could not render spreadsheet: ${escapeHtml(e.message)}</div>`;
  }
}

// ================================================================
// Word document renderer (DOCX / DOC)
// ================================================================

async function renderDocx(path, arrayBuffer, viewer) {
  if (typeof mammoth === 'undefined') {
    viewer.innerHTML = `<div class="fm-error">⚠️ mammoth.js library not loaded.</div>`;
    return;
  }

  try {
    const result = await mammoth.convertToHtml({ arrayBuffer }, {
      styleMap: [
        "p[style-name='Heading 1'] => h1:fresh",
        "p[style-name='Heading 2'] => h2:fresh",
        "p[style-name='Heading 3'] => h3:fresh",
      ],
    });

    viewer.innerHTML = `
      <div class="fm-file-header">
        <span>${escapeHtml(path)}</span>
        <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
      </div>
      <div class="fm-docx-viewer">
        <div class="fm-docx-content">${result.value}</div>
        ${result.messages.length ? `<div class="fm-docx-messages">${escapeHtml(result.messages.map(m => m.message).join('; '))}</div>` : ''}
      </div>
    `;

    document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
      viewer.classList.add('fm-viewer-hidden');
    });
  } catch (e) {
    viewer.innerHTML = `<div class="fm-error">⚠️ Could not render Word document: ${escapeHtml(e.message)}</div>`;
  }
}

// ================================================================
// Multi-language code syntax highlighting renderer
// ================================================================

/**
 * Language-specific keyword sets and highlighting rules.
 * Uses VS Code Dark+ color palette for visual consistency.
 */
const FM_LANG = {
  py: {
    keywords: /\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b/g,
    builtins: /\b(print|len|range|int|float|str|list|dict|tuple|set|bool|type|isinstance|hasattr|getattr|setattr|open|super|self|cls|__init__|__call__|__str__|__repr__|__len__|__getitem__|__setitem__|__enter__|__exit__|enumerate|zip|map|filter|sorted|reversed|any|all|sum|min|max|abs|round|input|format|property|staticmethod|classmethod|object|ValueError|TypeError|KeyError|IndexError|RuntimeError|Exception|BaseException)\b/g,
    decorator: /^([ \t]*)(@[\w.]+)/gm,
    fstring: /\{[^{}]*\}/g,
    string: /"""[\s\S]*?"""|'''[\s\S]*?'''|"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    comment: /(^|\s)(#[^\n]*)/gm,
    number: /\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?[jJ]?)\b/g,
  },
  js: {
    keywords: /\b(async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|let|new|of|return|static|super|switch|this|throw|try|typeof|var|void|while|with|yield)\b/g,
    builtins: /\b(console|document|window|Array|Object|String|Number|Boolean|Map|Set|Promise|JSON|Math|Date|RegExp|Error|parseInt|parseFloat|isNaN|fetch|setTimeout|setInterval|null|undefined|true|false)\b/g,
    string: /`([^`\\]|\\.)*`|"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    comment: /\/\/[^\n]*|\/\*[\s\S]*?\*\//g,
    number: /\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g,
  },
  ts: {
    keywords: /\b(abstract|as|async|await|break|case|catch|class|const|continue|debugger|declare|default|delete|do|else|enum|export|extends|finally|for|function|if|implements|import|in|infer|instanceof|interface|is|keyof|let|module|namespace|new|of|readonly|return|static|super|switch|this|throw|try|typeof|var|void|while|with|yield)\b/g,
    builtins: /\b(console|document|window|Array|Object|String|Number|Boolean|Map|Set|Promise|JSON|Math|Date|RegExp|Error|parseInt|parseFloat|isNaN|fetch|setTimeout|setInterval|null|undefined|true|false|Record|Partial|Pick|Omit|Required|Readonly|Exclude|Extract|NonNullable|ReturnType|InstanceType|Parameters)\b/g,
    types: /\b(string|number|boolean|symbol|bigint|any|unknown|never|void|null|undefined|object)\b/g,
    string: /`([^`\\]|\\.)*`|"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    comment: /\/\/[^\n]*|\/\*[\s\S]*?\*\//g,
    number: /\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g,
  },
  html: {
    tag: /(&lt;\/?)([\w-]+)/g,
    attr: /\b([\w-]+)(=)("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g,
    comment: /&lt;!--[\s\S]*?--&gt;/g,
    entity: /(&amp;|&lt;|&gt;|&quot;|&#?\w+;)/g,
  },
  css: {
    selector: /^([ \t]*)([.#]?[\w-]+(?:[ >+~][.#]?[\w-]+)*)\s*\{/gm,
    property: /([\w-]+)\s*:/g,
    value: /:\s*(.+?);/g,
    comment: /\/\*[\s\S]*?\*\//g,
    number: /\b(-?\d+\.?\d*)(px|em|rem|%|vh|vw|s|ms)?\b/g,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    important: /(!important)/g,
  },
  sh: {
    keyword: /\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|exit|export|local|source|\.)\b/g,
    builtin: /\b(echo|cd|ls|cat|grep|sed|awk|rm|mv|cp|mkdir|rmdir|chmod|chown|find|xargs|sort|uniq|wc|head|tail|cut|tr|tee|read|printf|eval|exec|shift|wait|kill|trap)\b/g,
    variable: /\$[a-zA-Z_][\w]*|\$\{[^}]+\}/g,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    comment: /(^|\s)(#[^\n]*)/gm,
    number: /\b(-?\d+)\b/g,
  },
  bat: {
    keyword: /\b(@echo|if|else|for|do|goto|call|exit|set|setlocal|endlocal|pause|rem|shift|choice|errorlevel|defined|exist|not|cmdextversion)\b/gi,
    variable: /%[a-zA-Z_][\w]*|%[0-9]|%\*|![\w]+!/g,
    comment: /^([ \t]*)rem\b.*$/gmi,
    label: /^:[a-zA-Z_][\w]*/gm,
    string: /"([^"\\]|\\.)*"/g,
  },
  ps1: {
    keyword: /\b(function|param|begin|process|end|if|else|elseif|for|foreach|while|switch|break|continue|return|exit|throw|try|catch|finally|filter|in|not|and|or|eq|ne|gt|lt|ge|le|match|notmatch|contains|notcontains|replace|split|join|begin|process|end|dynamicparam)\b/g,
    builtin: /\b(Write-Host|Write-Output|Write-Error|Write-Warning|Write-Verbose|Get-ChildItem|Get-Content|Set-Content|Add-Content|Select-Object|Where-Object|ForEach-Object|New-Object|New-Item|Remove-Item|Test-Path|Join-Path|Split-Path|Resolve-Path|ConvertTo-Json|ConvertFrom-Json|Invoke-WebRequest|Invoke-RestMethod|Start-Process|Start-Sleep|Get-Command|Get-Member|Get-Help|Out-String|Format-Table|Format-List|Export-Csv|Import-Csv)\b/g,
    variable: /\$[a-zA-Z_][\w]*|\$\{[^}]+\}/g,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    comment: /(^|\s)(#[^\n]*)/gm,
    number: /\b(-?\d+\.?\d*)\b/g,
  },
  toml: {
    table: /^\[([\w.-]+)\]\s*$/gm,
    key: /^([ \t]*)([\w.-]+)(\s*=)/gm,
    comment: /(^|\s)(#[^\n]*)/gm,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    number: /\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g,
    bool: /\b(true|false)\b/gi,
    date: /\b\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?\b/g,
  },
  xml: {
    tag: /(&lt;\/?)([\w:-]+)/g,
    attr: /\b([\w:-]+)(=)("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g,
    comment: /&lt;!--[\s\S]*?--&gt;/g,
    cdata: /&lt;!\[CDATA\[[\s\S]*?\]\]&gt;/g,
    entity: /(&amp;|&lt;|&gt;|&quot;|&#?\w+;)/g,
  },
  config: {
    section: /^\[([^\]]+)\]\s*$/gm,
    key: /^([ \t]*)([\w.-]+)(\s*[=:])/gm,
    comment: /(^|\s)([;#][^\n]*)/gm,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
    number: /\b(-?\d+\.?\d*)\b/g,
    bool: /\b(true|false|yes|no|on|off)\b/gi,
  },
  bib: {
    entry: /^(@[\w]+)\s*\{/gm,
    field: /([\w-]+)\s*=/g,
    string: /"([^"\\]|\\.)*"|\{([^{}]|\{[^{}]*\})*\}/g,
    comment: /(^|\s)(#[^\n]*)/gm,
    number: /\b(-?\d+)\b/g,
    crossref: /\bcrossref\s*=\s*"([^"]*)"/g,
  },
  patch: {
    diff: /^(---|\+\+\+)\s/gm,
    header: /^@@\s.+@@\s*$/gm,
    add: /^\+[^+]/gm,
    del: /^-[^-]/gm,
    hunk: /^@@/gm,
  },
  tex: {
    command: /\\([\w]+)/g,
    comment: /(^|\s)(%[^\n]*)/gm,
    math: /\$[^$]*\$|\$\$[\s\S]*?\$\$/g,
    beginend: /\\(begin|end)\s*\{[\w*]+\}/g,
    label: /\\(label|ref|cite)\s*\{[^}]+\}/g,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
  },
  rst: {
    section: /^[=\-~^]+$/gm,
    directive: /^\.\.\s+[\w-]+::/gm,
    role: /:[\w-]+:`[^`]+`/g,
    comment: /^\.\.\s[^\n]*$/gm,
    literal: /``[^`]+``/g,
    link: /`[^<]+<[^>]+>`__/g,
  },
  dockerfile: {
    instruction: /^(FROM|RUN|CMD|ENTRYPOINT|COPY|ADD|WORKDIR|ENV|ARG|EXPOSE|LABEL|MAINTAINER|VOLUME|USER|SHELL|HEALTHCHECK|ONBUILD|STOPSIGNAL)\b/gim,
    comment: /(^|\s)(#[^\n]*)/gm,
    variable: /\$\{?[a-zA-Z_][\w]*\}?/g,
    string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
  },
};

/** Shared patterns used across languages */
const FM_CODE_SHARED = {
  number: /\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g,
  string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
  commentSingle: /(^|\s)(\/\/[^\n]*)/gm,
  commentBlock: /\/\*[\s\S]*?\*\//g,
};

/**
 * Map file extensions to language configuration keys.
 */
const FM_EXT_TO_LANG = {
  '.py': 'py',
  '.js': 'js',
  '.ts': 'ts',
  '.css': 'css',
  '.html': 'html',
  '.toml': 'toml',
  '.xml': 'xml',
  '.cfg': 'config',
  '.conf': 'config',
  '.ini': 'config',
  '.bib': 'bib',
  '.patch': 'patch',
  '.tex': 'tex',
  '.rst': 'rst',
  '.sh': 'sh',
  '.bat': 'bat',
  '.ps1': 'ps1',
  '.dockerfile': 'dockerfile',
};

/** Fallback for unknown code file types — basic highlighting only */
const FM_CODE_FALLBACK = {
  comment: /(^|\s)([;#][^\n]*)/gm,
  string: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'/g,
  number: /\b(-?\d+\.?\d*)\b/g,
};

function renderFMCode(content, ext) {
  let html = escapeHtml(content);
  const langKey = FM_EXT_TO_LANG[ext];
  const rules = langKey ? FM_LANG[langKey] : FM_CODE_FALLBACK;

  if (!rules) {
    // No rules at all — plain text fallback
    return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(content)}">📋 Copy</button><pre class="fm-code">${html}</pre></div>`;
  }

  // Apply rules in order: comments first (to avoid re-tagging inside), then specific tokens
  const langClass = langKey ? `fm-code-${langKey}` : 'fm-code-fallback';

  // Comments
  if (rules.comment) {
    html = html.replace(rules.comment, (match, ...args) => {
      if (args.length >= 2) {
        const prefix = args[0] || '';
        const comment = args[1];
        return prefix + `<span class="fm-tk-comment">${comment}</span>`;
      }
      return `<span class="fm-tk-comment">${match}</span>`;
    });
  }

  // Strings (must come before numbers to avoid tagging numbers inside strings)
  if (rules.string) {
    html = html.replace(rules.string, '<span class="fm-tk-string">$&</span>');
  }

  // Numbers
  if (rules.number) {
    html = html.replace(rules.number, '<span class="fm-tk-number">$&</span>');
  }

  // Language-specific rules
  for (const [key, pattern] of Object.entries(rules)) {
    if (key === 'comment' || key === 'string' || key === 'number') continue;

    if (key === 'keyword' || key === 'keywords') {
      html = html.replace(pattern, '<span class="fm-tk-keyword">$&</span>');
    } else if (key === 'builtin' || key === 'builtins') {
      html = html.replace(pattern, '<span class="fm-tk-builtin">$&</span>');
    } else if (key === 'types') {
      html = html.replace(pattern, '<span class="fm-tk-type">$&</span>');
    } else if (key === 'decorator') {
      html = html.replace(pattern, (match, ws, dec) => ws + `<span class="fm-tk-decorator">${dec}</span>`);
    } else if (key === 'fstring') {
      html = html.replace(pattern, '<span class="fm-tk-fstring">$&</span>');
    } else if (key === 'tag') {
      html = html.replace(pattern, (match, bracket, name) => `${bracket}<span class="fm-tk-tag">${name}</span>`);
    } else if (key === 'attr') {
      html = html.replace(pattern, (match, name, eq, val) =>
        `<span class="fm-tk-attr">${name}</span>${eq}<span class="fm-tk-string">${val}</span>`);
    } else if (key === 'entity') {
      html = html.replace(pattern, '<span class="fm-tk-entity">$&</span>');
    } else if (key === 'selector') {
      html = html.replace(pattern, (match, ws, sel) => ws + `<span class="fm-tk-selector">${sel}</span> {`);
    } else if (key === 'property') {
      html = html.replace(pattern, '<span class="fm-tk-property">$&</span>');
    } else if (key === 'value') {
      html = html.replace(pattern, ': <span class="fm-tk-value">$1</span>;');
    } else if (key === 'important') {
      html = html.replace(pattern, '<span class="fm-tk-important">$&</span>');
    } else if (key === 'variable') {
      html = html.replace(pattern, '<span class="fm-tk-variable">$&</span>');
    } else if (key === 'section' || key === 'table') {
      html = html.replace(pattern, '<span class="fm-tk-section">$&</span>');
    } else if (key === 'entry') {
      html = html.replace(pattern, '<span class="fm-tk-entry">$&</span>');
    } else if (key === 'field') {
      html = html.replace(pattern, '<span class="fm-tk-field">$&</span>');
    } else if (key === 'diff' || key === 'add' || key === 'del') {
      html = html.replace(pattern, '<span class="fm-tk-diff">$&</span>');
    } else if (key === 'hunk' || key === 'header') {
      html = html.replace(pattern, '<span class="fm-tk-hunk">$&</span>');
    } else if (key === 'label') {
      html = html.replace(pattern, '<span class="fm-tk-label">$&</span>');
    } else if (key === 'command' || key === 'instruction') {
      html = html.replace(pattern, '<span class="fm-tk-keyword">$&</span>');
    } else if (key === 'math') {
      html = html.replace(pattern, '<span class="fm-tk-string">$&</span>');
    } else if (key === 'beginend') {
      html = html.replace(pattern, '<span class="fm-tk-keyword">$&</span>');
    } else if (key === 'directive') {
      html = html.replace(pattern, '<span class="fm-tk-keyword">$&</span>');
    } else if (key === 'role') {
      html = html.replace(pattern, '<span class="fm-tk-builtin">$&</span>');
    } else if (key === 'literal' || key === 'link') {
      html = html.replace(pattern, '<span class="fm-tk-string">$&</span>');
    } else if (key === 'cdata') {
      html = html.replace(pattern, '<span class="fm-tk-string">$&</span>');
    } else if (key === 'bool') {
      html = html.replace(pattern, '<span class="fm-tk-keyword">$&</span>');
    } else if (key === 'date') {
      html = html.replace(pattern, '<span class="fm-tk-number">$&</span>');
    } else if (key === 'crossref') {
      html = html.replace(pattern, '<span class="fm-tk-field">$&</span>');
    }
  }

  return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(content)}">📋 Copy</button><pre class="fm-code fm-code-hl ${langClass}">${html}</pre></div>`;
}

// ================================================================
// YAML syntax highlighting renderer
// ================================================================

function renderFMYaml(content) {
  // Escape HTML first, then apply syntax highlighting via regex
  let html = escapeHtml(content);

  // Highlight YAML comments (# ...)
  html = html.replace(/(^|\s)(#.*)$/gm, '$1<span class="fm-yaml-comment">$2</span>');

  // Highlight keys (word before colon at start of line, possibly indented)
  html = html.replace(/^([ \t]*)([\w.-]+)(\s*:)/gm, '$1<span class="fm-yaml-key">$2</span>$3');

  // Highlight boolean values (true/false/yes/no/on/off)
  html = html.replace(/\b(true|false|yes|no|on|off)\b/gi, '<span class="fm-yaml-bool">$1</span>');

  // Highlight numeric values (integers, floats, scientific notation)
  html = html.replace(/\b(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\b/g, '<span class="fm-yaml-number">$1</span>');

  // Highlight quoted strings ("..." or '...')
  html = html.replace(/(["'])(?:(?!\1|\\).|\\.)*\1/g, '<span class="fm-yaml-string">$&</span>');

  // Highlight null/none/~ values
  html = html.replace(/\b(null|~|none|nil)\b/gi, '<span class="fm-yaml-null">$1</span>');

  // Highlight list markers (- )
  html = html.replace(/^([ \t]*)(- )/gm, '$1<span class="fm-yaml-list-marker">$2</span>');

  // Highlight anchor (*) and alias (&) references
  html = html.replace(/(\*[\w.-]+)/g, '<span class="fm-yaml-anchor">$1</span>');
  html = html.replace(/(&[\w.-]+)/g, '<span class="fm-yaml-alias">$1</span>');

  // Highlight document separators (---, ...)
  html = html.replace(/^(---|\.\.\.)$/gm, '<span class="fm-yaml-doc-sep">$1</span>');

  // Highlight pipe (|) and greater-than (>) block scalars
  html = html.replace(/(\s[|>]\s*)$/gm, '<span class="fm-yaml-block-scalar">$1</span>');

  return `<div class="fm-code-wrapper"><button class="fm-copy-btn" data-content="${escapeHtml(content)}">📋 Copy</button><pre class="fm-code fm-yaml">${html}</pre></div>`;
}

// ================================================================
// Global delegated click handler for copy buttons
// ================================================================

document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.fm-copy-btn');
  if (!btn) return;
  const content = btn.dataset.content;
  if (!content) return;
  try {
    await navigator.clipboard.writeText(content);
    btn.textContent = '✅ Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = '📋 Copy';
      btn.classList.remove('copied');
    }, 2000);
  } catch {
    btn.textContent = '❌ Failed';
  }
});

// ================================================================
// In-browser text/code editor
// ================================================================

function computeFMDiff(oldText, newText) {
  const oldLines = oldText.split('\n');
  const newLines = newText.split('\n');
  const changes = [];
  let oi = 0, ni = 0;
  while (oi < oldLines.length || ni < newLines.length) {
    if (oi >= oldLines.length) {
      changes.push({ type: 'add', line: newLines[ni], oldLine: ni + 1 });
      ni++;
    } else if (ni >= newLines.length) {
      changes.push({ type: 'del', line: oldLines[oi], oldLine: oi + 1 });
      oi++;
    } else if (oldLines[oi] === newLines[ni]) {
      changes.push({ type: 'ctx', line: oldLines[oi], oldLine: oi + 1 });
      oi++; ni++;
    } else {
      // Simple heuristic: if next new line matches current old line -> deletion
      // if next old line matches current new line -> addition
      // otherwise replace
      const nextNewMatchesOld = ni + 1 < newLines.length && newLines[ni + 1] === oldLines[oi];
      const nextOldMatchesNew = oi + 1 < oldLines.length && oldLines[oi + 1] === newLines[ni];
      if (nextNewMatchesOld && !nextOldMatchesNew) {
        changes.push({ type: 'add', line: newLines[ni], oldLine: ni + 1 });
        ni++;
      } else if (nextOldMatchesNew && !nextNewMatchesOld) {
        changes.push({ type: 'del', line: oldLines[oi], oldLine: oi + 1 });
        oi++;
      } else {
        changes.push({ type: 'del', line: oldLines[oi], oldLine: oi + 1 });
        changes.push({ type: 'add', line: newLines[ni], oldLine: ni + 1 });
        oi++; ni++;
      }
    }
  }
  return changes;
}

function renderFMDiff(changes) {
  if (changes.length === 0) return '<div class="fm-diff-empty">No changes</div>';
  let html = '<div class="fm-diff"><table class="fm-diff-table"><tbody>';
  changes.forEach(c => {
    const cls = c.type === 'add' ? 'fm-diff-add' : c.type === 'del' ? 'fm-diff-del' : 'fm-diff-ctx';
    const sign = c.type === 'add' ? '+' : c.type === 'del' ? '-' : ' ';
    html += `<tr class="${cls}"><td class="fm-diff-sign">${sign}</td><td class="fm-diff-line">${escapeHtml(c.line)}</td></tr>`;
  });
  html += '</tbody></table></div>';
  return html;
}

function activateFMEditor({ path, name, content, ext, source, viewer }) {
  const lang = fmLangFromExt(ext);
  const isMarkdown = ext === '.md' || ext === '.markdown';
  const originalContent = content;
  let autoSaveTimer = null;
  const AUTO_SAVE_INTERVAL_MS = 30000; // 30 seconds

  function renderEditorUI() {
    viewer.innerHTML = `
      <div class="fm-file-header">
        <h3>✏️ ${escapeHtml(name)}</h3>
        <div class="fm-file-header-actions">
          <span class="fm-file-meta" id="fm-editor-changed" style="display:none;">● unsaved</span>
          <span class="fm-file-meta">${escapeHtml(lang)}</span>
          <button class="fm-file-action-btn" id="fm-file-diff" title="Show diff">🆚 Diff</button>
          <button class="fm-file-action-btn" id="fm-file-restore" title="Restore from backup">↩️ Restore</button>
          <button class="fm-file-save-btn" id="fm-file-save" title="Save changes (Ctrl+S)">💾 Save</button>
          <button class="fm-file-cancel-btn" id="fm-file-cancel" title="Cancel editing (Esc)">❌ Cancel</button>
        </div>
      </div>
      <div class="fm-editor-wrapper">
        ${isMarkdown ? `
          <div class="fm-editor-split">
            <div class="fm-editor-pane">
              <textarea id="fm-editor-textarea" class="fm-editor-textarea" spellcheck="false">${escapeHtml(originalContent)}</textarea>
            </div>
            <div class="fm-editor-preview fm-markdown" id="fm-editor-preview"></div>
          </div>
        ` : `
          <textarea id="fm-editor-textarea" class="fm-editor-textarea" spellcheck="false">${escapeHtml(originalContent)}</textarea>
        `}
      </div>
      <div class="fm-editor-diff" id="fm-editor-diff" style="display:none;"></div>
      <div class="fm-editor-status" id="fm-editor-status"></div>
    `;
  }

  renderEditorUI();

  const textarea = document.getElementById('fm-editor-textarea');
  const statusEl = document.getElementById('fm-editor-status');
  const saveBtn = document.getElementById('fm-file-save');
  const cancelBtn = document.getElementById('fm-file-cancel');
  const diffBtn = document.getElementById('fm-file-diff');
  const restoreBtn = document.getElementById('fm-file-restore');
  const changedIndicator = document.getElementById('fm-editor-changed');
  const diffContainer = document.getElementById('fm-editor-diff');

  if (!textarea || !saveBtn || !cancelBtn) return;

  function markChanged() {
    if (changedIndicator) changedIndicator.style.display = 'inline';
  }

  function clearChanged() {
    if (changedIndicator) changedIndicator.style.display = 'none';
  }

  function resizeTextarea() {
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.max(300, textarea.scrollHeight + 16)}px`;
  }
  resizeTextarea();
  textarea.addEventListener('input', () => {
    resizeTextarea();
    markChanged();
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => performSave(true), AUTO_SAVE_INTERVAL_MS);
  });

  if (isMarkdown) {
    const preview = document.getElementById('fm-editor-preview');
    const updatePreview = () => {
      if (preview) preview.innerHTML = renderFMMarkdown(textarea.value);
    };
    textarea.addEventListener('input', updatePreview);
    updatePreview();
  }

  async function performSave(isAuto = false) {
    const newContent = textarea.value;
    if (!isAuto) {
      saveBtn.disabled = true;
      saveBtn.textContent = '⏳ Saving...';
    }
    statusEl.textContent = '';
    statusEl.className = 'fm-editor-status';

    try {
      const encodedPath = encodeURIComponent(path);
      const res = await fetch(`/api/files/save/${encodedPath}?source=${encodeURIComponent(source)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newContent, backup: true }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      clearChanged();
      const label = isAuto ? 'Auto-saved' : 'Saved';
      statusEl.textContent = `✅ ${label} (${formatBytes(data.size_bytes || 0)})`;
      statusEl.classList.add('success');
      if (!isAuto) {
        setTimeout(() => {
          openFMFile(path, source);
        }, 600);
      }
    } catch (e) {
      statusEl.textContent = `❌ Save failed: ${escapeHtml(e.message)}`;
      statusEl.classList.add('error');
      if (!isAuto) {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save';
      }
    } finally {
      if (!isAuto && saveBtn) {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save';
      }
    }
  }

  saveBtn.addEventListener('click', () => performSave(false));

  cancelBtn.addEventListener('click', () => {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    openFMFile(path, source);
  });

  diffBtn?.addEventListener('click', () => {
    if (!diffContainer) return;
    const isHidden = diffContainer.style.display === 'none';
    if (isHidden) {
      const changes = computeFMDiff(originalContent, textarea.value);
      diffContainer.innerHTML = renderFMDiff(changes);
      diffContainer.style.display = 'block';
      if (diffBtn) diffBtn.textContent = '🆚 Hide diff';
    } else {
      diffContainer.style.display = 'none';
      if (diffBtn) diffBtn.textContent = '🆚 Diff';
    }
  });

  restoreBtn?.addEventListener('click', async () => {
    if (!confirm('Restore content from the latest backup? Unsaved changes will be lost.')) return;
    try {
      const encodedPath = encodeURIComponent(path);
      const backupPath = path + (path.includes('.') ? '.bak' : '.bak');
      const res = await fetch(`/api/files/content/${encodeURIComponent(backupPath)}?source=${encodeURIComponent(source)}`);
      if (!res.ok) throw new Error('No backup found');
      const data = await res.json();
      textarea.value = data.content || '';
      resizeTextarea();
      markChanged();
      statusEl.textContent = '↩️ Restored from backup';
      statusEl.classList.add('success');
    } catch (e) {
      statusEl.textContent = `❌ Restore failed: ${escapeHtml(e.message)}`;
      statusEl.classList.add('error');
    }
  });

  // Keyboard shortcuts
  textarea.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      performSave(false);
    }
    if (e.key === 'Escape') {
      e.preventDefault();
      cancelBtn.click();
    }
  });
}

// ================================================================
// Jupyter Notebook renderer
// ================================================================

function renderIPythonNotebook(path, content, viewer) {
  let notebook;
  try {
    notebook = JSON.parse(content);
  } catch (e) {
    viewer.innerHTML = `<div class="fm-error">⚠️ Invalid notebook JSON: ${escapeHtml(e.message)}</div>`;
    return;
  }

  const cells = notebook.cells || [];
  let html = `
    <div class="fm-file-header">
      <span>${escapeHtml(path)}</span>
      <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
    </div>
    <div class="fm-notebook">
  `;

  cells.forEach((cell, idx) => {
    const cellType = cell.cell_type || 'code';
    const source = Array.isArray(cell.source) ? cell.source.join('') : (cell.source || '');
    html += `<div class="fm-notebook-cell fm-notebook-${cellType}">`;
    html += `<div class="fm-notebook-cell-label">${cellType} [${idx + 1}]</div>`;

    if (cellType === 'markdown') {
      html += `<div class="fm-notebook-source fm-markdown">${renderFMMarkdown(source)}</div>`;
    } else if (cellType === 'code') {
      html += `<pre class="fm-notebook-source fm-code"><code>${escapeHtml(source)}</code></pre>`;
      if (cell.outputs && cell.outputs.length > 0) {
        html += '<div class="fm-notebook-outputs">';
        cell.outputs.forEach(out => {
          const outType = out.output_type || 'unknown';
          html += `<div class="fm-notebook-output fm-notebook-output-${outType}">`;
          if (out.text) {
            const text = Array.isArray(out.text) ? out.text.join('') : out.text;
            html += `<pre>${escapeHtml(text)}</pre>`;
          }
          if (out.data) {
            if (out.data['text/html']) {
              const htmlOut = Array.isArray(out.data['text/html']) ? out.data['text/html'].join('') : out.data['text/html'];
              html += `<div class="fm-notebook-output-html">${htmlOut}</div>`;
            } else if (out.data['image/png']) {
              html += `<img src="data:image/png;base64,${out.data['image/png']}" class="fm-notebook-output-image" alt="output">`;
            } else if (out.data['image/jpeg']) {
              html += `<img src="data:image/jpeg;base64,${out.data['image/jpeg']}" class="fm-notebook-output-image" alt="output">`;
            } else if (out.data['text/plain']) {
              const text = Array.isArray(out.data['text/plain']) ? out.data['text/plain'].join('') : out.data['text/plain'];
              html += `<pre>${escapeHtml(text)}</pre>`;
            }
          }
          if (out.ename) {
            html += `<div class="fm-notebook-output-error"><strong>${escapeHtml(out.ename)}</strong>: ${escapeHtml(out.evalue || '')}</div>`;
          }
          html += '</div>';
        });
        html += '</div>';
      }
    } else {
      html += `<pre class="fm-notebook-source fm-code"><code>${escapeHtml(source)}</code></pre>`;
    }
    html += '</div>';
  });

  html += '</div>';
  viewer.innerHTML = html;
  document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
    viewer.classList.add('fm-viewer-hidden');
  });
}

// ================================================================
// Log file renderer
// ================================================================

function renderLogFile(path, content, viewer) {
  const lines = content.split('\n');
  let html = `
    <div class="fm-file-header">
      <span>${escapeHtml(path)}</span>
      <div class="fm-file-header-actions">
        <button class="fm-file-action-btn" id="fm-log-filter-info" title="Toggle INFO">ℹ️ INFO</button>
        <button class="fm-file-action-btn" id="fm-log-filter-warn" title="Toggle WARNING">⚠️ WARN</button>
        <button class="fm-file-action-btn" id="fm-log-filter-error" title="Toggle ERROR">🔴 ERROR</button>
        <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
      </div>
    </div>
    <div class="fm-log-viewer">
  `;

  lines.forEach((line, idx) => {
    const levelMatch = line.match(/\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b/);
    const level = levelMatch ? levelMatch[1].toLowerCase() : 'default';
    const displayLevel = level === 'warn' ? 'warning' : level;
    html += `<div class="fm-log-line fm-log-level-${displayLevel}" data-level="${displayLevel}" data-line="${idx + 1}"><span class="fm-log-line-num">${idx + 1}</span><span class="fm-log-line-text">${escapeHtml(line)}</span></div>`;
  });

  html += '</div>';
  viewer.innerHTML = html;

  document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
    viewer.classList.add('fm-viewer-hidden');
  });

  ['info', 'warning', 'error'].forEach(level => {
    const btn = document.getElementById(`fm-log-filter-${level}`);
    if (!btn) return;
    btn.addEventListener('click', () => {
      const active = btn.classList.toggle('active');
      viewer.querySelectorAll(`.fm-log-line[data-level="${level}"]`).forEach(el => {
        el.style.display = active ? 'none' : '';
      });
    });
  });
}

// ================================================================
// Graphviz DOT renderer
// ================================================================

function renderGraphviz(path, content, viewer) {
  if (typeof d3 === 'undefined' || typeof d3.graphviz === 'undefined') {
    viewer.innerHTML = `<div class="fm-error">⚠️ d3-graphviz library not loaded.</div>`;
    return;
  }

  const id = 'fm-graphviz-' + Math.random().toString(36).slice(2);
  viewer.innerHTML = `
    <div class="fm-file-header">
      <span>${escapeHtml(path)}</span>
      <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
    </div>
    <div class="fm-diagram-viewer">
      <div id="${id}" class="fm-diagram-container"></div>
    </div>
  `;

  try {
    d3.select(`#${id}`).graphviz().renderDot(content);
  } catch (e) {
    document.getElementById(id).innerHTML = `<div class="fm-error">⚠️ Graphviz render error: ${escapeHtml(e.message)}</div>`;
  }

  document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
    viewer.classList.add('fm-viewer-hidden');
  });
}

// ================================================================
// PlantUML renderer
// ================================================================

function renderPlantUML(path, content, viewer) {
  if (typeof plantumlEncoder === 'undefined') {
    viewer.innerHTML = `<div class="fm-error">⚠️ plantuml-encoder library not loaded.</div>`;
    return;
  }

  try {
    const encoded = plantumlEncoder.encode(content);
    const url = `https://www.plantuml.com/plantuml/svg/${encoded}`;
    viewer.innerHTML = `
      <div class="fm-file-header">
        <span>${escapeHtml(path)}</span>
        <a href="${url}" target="_blank" class="fm-file-copy-btn">Open source</a>
        <button class="fm-close-viewer-btn" id="fm-close-viewer" title="Close viewer">✕</button>
      </div>
      <div class="fm-diagram-viewer">
        <img src="${url}" alt="PlantUML diagram" class="fm-diagram-image">
      </div>
    `;
    document.getElementById('fm-close-viewer')?.addEventListener('click', () => {
      viewer.classList.add('fm-viewer-hidden');
    });
  } catch (e) {
    viewer.innerHTML = `<div class="fm-error">⚠️ PlantUML encode error: ${escapeHtml(e.message)}</div>`;
  }
}

// ================================================================
// EXPORTS
// ================================================================

export { initFileManager, initResearchBrowser, initDocumentationBrowser, refreshFileManager };
