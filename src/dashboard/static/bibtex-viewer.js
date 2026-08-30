/**
 * Brain-5D Operator Dashboard – BibTeX Viewer Module
 *
 * Self-contained ES module for parsing, displaying, and exporting
 * BibTeX bibliographic entries. Provides:
 *   - Structured table view (sortable, filterable)
 *   - Syntax-highlighted raw code view
 *   - Citation copy (e.g. "(Heisig, 2026)")
 *   - Entry copy as BibTeX snippet
 *   - Full BibTeX export / download
 *   - Validation & quality checks
 *   - DOI link resolution
 *
 * @module bibtex-viewer
 * @requires No external dependencies.
 */

"use strict";

// ================================================================
// BibTeX Parser
// ================================================================

/**
 * Parse raw BibTeX text into an array of entry objects.
 * @param {string} content - Raw BibTeX file content
 * @returns {Array<{type:string, key:string, fields:Object, raw:string}>}
 */
function parseBibTeX(content) {
  const entries = [];
  // Remove comments (% lines) first
  const cleaned = content.replace(/^[ \t]*%.*$/gm, '');
  // Match each @type{key, ... }
  const entryRegex = /@(\w+)\s*\{\s*([^,\s]+)\s*,([\s\S]*?)\}\s*(?=@|\s*$)/gi;
  let match;

  while ((match = entryRegex.exec(cleaned)) !== null) {
    const type = match[1].toLowerCase();
    const key = match[2].trim();
    const body = match[3];

    const fields = {};
    // Match field = {value} or field = "value"
    const fieldRegex = /(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)")/gi;
    let fm;
    while ((fm = fieldRegex.exec(body)) !== null) {
      const fieldName = fm[1].toLowerCase();
      const fieldValue = (fm[2] !== undefined ? fm[2] : fm[3] || '').trim();
      fields[fieldName] = fieldValue;
    }

    entries.push({
      type,
      key,
      fields,
      raw: match[0].trim()
    });
  }

  return entries;
}

// ================================================================
// Entry validation
// ================================================================

const REQUIRED_FIELDS = {
  article: ['author', 'title', 'journal', 'year'],
  book: ['author', 'title', 'publisher', 'year'],
  inproceedings: ['author', 'title', 'booktitle', 'year'],
  incollection: ['author', 'title', 'booktitle', 'publisher', 'year'],
  phdthesis: ['author', 'title', 'school', 'year'],
  mastersthesis: ['author', 'title', 'school', 'year'],
  misc: ['title', 'year'],
  techreport: ['author', 'title', 'institution', 'year'],
  unpublished: ['author', 'title', 'note'],
};

function getRequiredFields(type) {
  return REQUIRED_FIELDS[type] || ['author', 'title', 'year'];
}

function validateEntry(entry) {
  const errors = [];
  const required = getRequiredFields(entry.type);
  for (const field of required) {
    if (!entry.fields[field] || !entry.fields[field].trim()) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  // Validate year format
  if (entry.fields.year && !/^\d{4}$/.test(entry.fields.year.trim())) {
    errors.push('Year must be 4 digits');
  }
  // Validate DOI format
  if (entry.fields.doi && !/^10\.\d{4,9}\/.*/.test(entry.fields.doi.trim())) {
    errors.push('Invalid DOI format');
  }
  return errors;
}

// ================================================================
// Citation formatting
// ================================================================

function formatAuthorShort(authorStr) {
  if (!authorStr) return 'Anonym';
  const first = authorStr.split(' and ')[0].trim();
  // Handle "Last, First" format
  if (first.includes(',')) {
    return first.split(',')[0].trim();
  }
  // Handle "First Last" format
  const parts = first.split(' ');
  return parts[parts.length - 1].replace(/[{}]/g, '');
}

function formatCitation(entry) {
  const author = formatAuthorShort(entry.fields.author);
  const year = entry.fields.year || 'o.J.';
  return `(${author}, ${year})`;
}

function formatBibTeXSnippet(entry) {
  const fields = Object.entries(entry.fields)
    .map(([k, v]) => `  ${k} = {${v}}`)
    .join(',\n');
  return `@${entry.type}{${entry.key},\n${fields}\n}\n`;
}

function formatBibTeXFull(entries) {
  return entries.map(e => formatBibTeXSnippet(e)).join('\n');
}

// ================================================================
// Renderers
// ================================================================

/**
 * Render the BibTeX viewer panel for a given .bib file content.
 * @param {string} content - Raw BibTeX content
 * @param {string} fileName - File name for display
 * @param {string} filePath - Path for context
 * @returns {string} HTML string
 */
function renderBibTeXViewer(content, fileName, filePath) {
  const entries = parseBibTeX(content);
  const total = entries.length;
  const invalid = entries.filter(e => validateEntry(e).length > 0).length;

  return `
<div class="bibtex-viewer">
  <div class="bibtex-toolbar">
    <div class="bibtex-toolbar-left">
      <span class="bibtex-title">📚 ${escapeHtml(fileName)}</span>
      <span class="bibtex-count">${total} entries</span>
      ${invalid > 0 ? `<span class="bibtex-warning">⚠️ ${invalid} incomplete</span>` : '<span class="bibtex-ok">✅ All complete</span>'}
    </div>
    <div class="bibtex-toolbar-right">
      <button class="bibtex-view-btn active" data-view="table" title="Table view">📋 Table</button>
      <button class="bibtex-view-btn" data-view="code" title="Code view">💻 Code</button>
      <button class="bibtex-copy-all-btn" title="Copy all as BibTeX">📋 Copy all</button>
      <button class="bibtex-export-btn" title="Download .bib file">💾 Download</button>
    </div>
  </div>

  <div class="bibtex-validation-bar">
    ${invalid > 0
      ? `<span class="bibtex-validation-msg warning">⚠️ ${invalid} of ${total} entries have issues. <a href="#" class="bibtex-show-issues">Show issues</a></span>`
      : `<span class="bibtex-validation-msg ok">✅ All ${total} entries validated</span>`
    }
  </div>

  <div class="bibtex-table-container">
    <table class="bibtex-table">
      <thead>
        <tr>
          <th data-sort="key" class="bibtex-sortable">Key <span class="bibtex-sort-icon">↕</span></th>
          <th data-sort="author" class="bibtex-sortable">Author <span class="bibtex-sort-icon">↕</span></th>
          <th data-sort="title" class="bibtex-sortable">Title <span class="bibtex-sort-icon">↕</span></th>
          <th data-sort="year" class="bibtex-sortable">Year <span class="bibtex-sort-icon">↕</span></th>
          <th data-sort="type" class="bibtex-sortable">Type <span class="bibtex-sort-icon">↕</span></th>
          <th data-sort="status">Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="bibtex-table-body">
        ${entries.map((entry, idx) => renderBibTeXRow(entry, idx)).join('')}
      </tbody>
    </table>
  </div>

  <div class="bibtex-code-container" style="display:none;">
    <pre class="bibtex-code">${escapeHtml(content)}</pre>
  </div>

  <div class="bibtex-footer">
    <div class="bibtex-footer-stats">
      <span>📊 <strong>${total}</strong> entries</span>
      <span>📋 <strong>${entries.filter(e => e.type === 'article').length}</strong> articles</span>
      <span>📚 <strong>${entries.filter(e => e.type === 'book').length}</strong> books</span>
      <span>📄 <strong>${entries.filter(e => e.type === 'inproceedings').length}</strong> inproceedings</span>
      <span>🔗 <strong>${entries.filter(e => e.fields.doi).length}</strong> with DOI</span>
    </div>
  </div>
</div>`;
}

function renderBibTeXRow(entry, idx) {
  const errors = validateEntry(entry);
  const statusClass = errors.length === 0 ? 'bibtex-status-ok' : 'bibtex-status-warn';
  const statusIcon = errors.length === 0 ? '✅' : '⚠️';
  const statusTitle = errors.length === 0 ? 'Valid' : errors.join('; ');

  const typeLabels = {
    article: 'art.',
    book: 'book',
    inproceedings: 'proc.',
    phdthesis: 'phd',
    mastersthesis: 'msc',
    misc: 'misc',
    techreport: 'rep.',
    unpublished: 'unpub.',
  };

  const author = entry.fields.author || '';
  const title = entry.fields.title || '';
  const year = entry.fields.year || '';
  const doi = entry.fields.doi || '';

  return `<tr class="bibtex-row ${errors.length > 0 ? 'bibtex-row-warn' : ''}" data-idx="${idx}">
    <td class="bibtex-cell-key"><code>${escapeHtml(entry.key)}</code></td>
    <td class="bibtex-cell-author">${escapeHtml(truncateText(author, 50))}</td>
    <td class="bibtex-cell-title">${escapeHtml(truncateText(title, 60))}</td>
    <td class="bibtex-cell-year">${escapeHtml(year)}</td>
    <td class="bibtex-cell-type"><span class="bibtex-type-badge">${typeLabels[entry.type] || entry.type}</span></td>
    <td class="bibtex-cell-status"><span class="${statusClass}" title="${escapeHtml(statusTitle)}">${statusIcon}</span></td>
    <td class="bibtex-cell-actions">
      <button class="bibtex-action-btn" data-action="cite" data-idx="${idx}" title="Copy citation">📋 Cite</button>
      <button class="bibtex-action-btn" data-action="copy" data-idx="${idx}" title="Copy BibTeX entry">📄 Bib</button>
      ${doi ? `<button class="bibtex-action-btn" data-action="doi" data-doi="${escapeHtml(doi)}" title="Open DOI">🔗 DOI</button>` : ''}
    </td>
  </tr>`;
}

// ================================================================
// Utility functions
// ================================================================

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function truncateText(str, maxLen) {
  if (!str || str.length <= maxLen) return str || '';
  return str.substring(0, maxLen) + '…';
}

// ================================================================
// Sorting
// ================================================================

let bibtexSortField = 'key';
let bibtexSortAsc = true;

function sortBibTeXTable(entries, field, asc) {
  const sorted = [...entries];
  sorted.sort((a, b) => {
    let va, vb;
    switch (field) {
      case 'key': va = a.key.toLowerCase(); vb = b.key.toLowerCase(); break;
      case 'author': va = (a.fields.author || '').toLowerCase(); vb = (b.fields.author || '').toLowerCase(); break;
      case 'title': va = (a.fields.title || '').toLowerCase(); vb = (b.fields.title || '').toLowerCase(); break;
      case 'year': va = parseInt(a.fields.year) || 0; vb = parseInt(b.fields.year) || 0; break;
      case 'type': va = a.type; vb = b.type; break;
      default: return 0;
    }
    if (va < vb) return asc ? -1 : 1;
    if (va > vb) return asc ? 1 : -1;
    return 0;
  });
  return sorted;
}

// ================================================================
// Module state
// ================================================================

let bibtexEntries = [];
let bibtexContent = '';
let bibtexFileName = '';

// ================================================================
// Initialization
// ================================================================

/**
 * Initialize the BibTeX viewer with content.
 * @param {string} content - Raw BibTeX text content
 * @param {string} fileName - Display name
 * @param {string} filePath - File path
 */
function initBibTeXViewer(content, fileName, filePath) {
  bibtexContent = content;
  bibtexFileName = fileName;
  bibtexEntries = parseBibTeX(content);

  // Return the HTML
  return renderBibTeXViewer(content, fileName, filePath);
}

/**
 * Wire up event handlers for the BibTeX viewer.
 * Must be called after the HTML is inserted into the DOM.
 */
function wireBibTeXEvents() {
  // View toggle (table / code)
  const viewBtns = document.querySelectorAll('.bibtex-view-btn');
  viewBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      viewBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const view = btn.dataset.view;
      const tableContainer = document.querySelector('.bibtex-table-container');
      const codeContainer = document.querySelector('.bibtex-code-container');
      if (tableContainer) tableContainer.style.display = view === 'table' ? 'block' : 'none';
      if (codeContainer) codeContainer.style.display = view === 'code' ? 'block' : 'none';
    });
  });

  // Sortable columns
  const sortHeaders = document.querySelectorAll('.bibtex-sortable');
  sortHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const field = header.dataset.sort;
      if (bibtexSortField === field) {
        bibtexSortAsc = !bibtexSortAsc;
      } else {
        bibtexSortField = field;
        bibtexSortAsc = true;
      }
      // Update sort icons
      sortHeaders.forEach(h => {
        const icon = h.querySelector('.bibtex-sort-icon');
        if (icon) icon.textContent = '↕';
      });
      const icon = header.querySelector('.bibtex-sort-icon');
      if (icon) icon.textContent = bibtexSortAsc ? '▲' : '▼';

      const sorted = sortBibTeXTable(bibtexEntries, field, bibtexSortAsc);
      const tbody = document.getElementById('bibtex-table-body');
      if (tbody) {
        tbody.innerHTML = sorted.map((entry, idx) => renderBibTeXRow(entry, idx)).join('');
        // Re-wire action buttons
        wireBibTeXActions();
      }
    });
  });

  // Action buttons
  wireBibTeXActions();

  // Copy all
  const copyAllBtn = document.querySelector('.bibtex-copy-all-btn');
  if (copyAllBtn) {
    copyAllBtn.addEventListener('click', async () => {
      const content = formatBibTeXFull(bibtexEntries);
      try {
        await navigator.clipboard.writeText(content);
        copyAllBtn.textContent = '✅ Copied!';
        setTimeout(() => { copyAllBtn.textContent = '📋 Copy all'; }, 2000);
      } catch {
        copyAllBtn.textContent = '❌ Failed';
      }
    });
  }

  // Export / Download
  const exportBtn = document.querySelector('.bibtex-export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const content = formatBibTeXFull(bibtexEntries);
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = bibtexFileName || 'references.bib';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // Show issues toggle
  const showIssuesLink = document.querySelector('.bibtex-show-issues');
  if (showIssuesLink) {
    showIssuesLink.addEventListener('click', (e) => {
      e.preventDefault();
      // Toggle highlight on warning rows
      const warnRows = document.querySelectorAll('.bibtex-row-warn');
      warnRows.forEach(row => {
        row.style.outline = row.style.outline ? '' : '2px solid var(--color-warning, #e6aa28)';
        row.style.outlineOffset = row.style.outline ? '' : '-1px';
      });
    });
  }
}

function wireBibTeXActions() {
  // Cite button
  document.querySelectorAll('.bibtex-action-btn[data-action="cite"]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const idx = parseInt(btn.dataset.idx);
      const entry = bibtexEntries[idx];
      if (!entry) return;
      const citation = formatCitation(entry);
      try {
        await navigator.clipboard.writeText(citation);
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 2000);
      } catch {
        btn.textContent = '❌';
      }
    });
  });

  // Copy BibTeX entry
  document.querySelectorAll('.bibtex-action-btn[data-action="copy"]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const idx = parseInt(btn.dataset.idx);
      const entry = bibtexEntries[idx];
      if (!entry) return;
      const snippet = formatBibTeXSnippet(entry);
      try {
        await navigator.clipboard.writeText(snippet);
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 2000);
      } catch {
        btn.textContent = '❌';
      }
    });
  });

  // DOI link
  document.querySelectorAll('.bibtex-action-btn[data-action="doi"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const doi = btn.dataset.doi;
      if (doi) {
        window.open(`https://doi.org/${doi}`, '_blank');
      }
    });
  });
}

// ================================================================
// EXPORTS
// ================================================================

export { initBibTeXViewer, wireBibTeXEvents, parseBibTeX, formatCitation, formatBibTeXSnippet, formatBibTeXFull, validateEntry };