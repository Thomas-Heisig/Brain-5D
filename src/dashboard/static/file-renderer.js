/** Canonical, container-scoped output renderer for File Manager and Research Chat.
 * Untrusted content is built with text nodes, never executable HTML. File paths
 * remain explicit research/docs references. Preview and mutation are separate.
 */
import { parseBibTeX } from './bibtex-viewer.js';

const requests = new WeakMap();
const renderers = new Map();
const TEXT_LIMIT = 262144;

function node(tag, text = '', className = '') {
  const element = document.createElement(tag);
  if (text !== '') element.textContent = String(text);
  if (className) element.className = className;
  return element;
}

function button(label, action) {
  const control = node('button', label, 'file-renderer-action');
  control.type = 'button';
  control.addEventListener('click', action);
  return control;
}

/** Resolve a link without allowing references outside the configured sources. */
export function fileReference(value, context = { source: 'research', path: '' }) {
  if (typeof value !== 'string' || !value || /[\\\u0000]/.test(value)) return null;
  let path;
  try { path = decodeURIComponent(value.split('#')[0]); } catch { return null; }
  if (/^[a-z][a-z\d+.-]*:/i.test(path) || path.startsWith('//')) return null;
  if (path.startsWith('/api/files/')) {
    const url = new URL(path, window.location.origin);
    const match = url.pathname.match(/^\/api\/files\/(?:content|preview|raw)\/(.+)$/);
    return match ? fileReference(`${url.searchParams.get('source') || 'research'}/${match[1]}`) : null;
  }
  let source = context.source;
  let parts;
  const rooted = path.match(/^\/?(research|docs)\/(.+)$/);
  if (rooted) { source = rooted[1]; parts = rooted[2].split('/'); }
  else {
    if (path.startsWith('/') || !['docs', 'research'].includes(source)) return null;
    parts = [...String(context.path || '').split('/').slice(0, -1), ...path.split('/')];
  }
  const normalized = [];
  for (const part of parts) {
    if (!part || part === '.') continue;
    if (part === '..') { if (!normalized.length) return null; normalized.pop(); }
    else if (part.startsWith('.') || part.includes(':')) return null;
    else normalized.push(part);
  }
  if (!normalized.length || !['docs', 'research'].includes(source)) return null;
  return { source, path: normalized.join('/') };
}

function inline(parent, text, context, onOpen, depth = 0) {
  if (depth > 4) { parent.append(document.createTextNode(text)); return; }
  const pattern = /(`[^`\n]+`|\*\*[^*\n]+\*\*|\[[^\]\n]+\]\([^)\n]+\))/g;
  let offset = 0;
  for (const match of text.matchAll(pattern)) {
    parent.append(document.createTextNode(text.slice(offset, match.index)));
    const token = match[0];
    if (token.startsWith('`')) parent.append(node('code', token.slice(1, -1)));
    else if (token.startsWith('**')) {
      const strong = node('strong'); inline(strong, token.slice(2, -2), context, onOpen, depth + 1); parent.append(strong);
    } else {
      const link = token.match(/^\[([^\]]+)\]\((.+)\)$/);
      const reference = fileReference(link[2], context);
      if (reference) {
        const control = button(link[1], () => onOpen?.(reference));
        control.classList.add('fm-md-link');
        control.dataset.filePath = reference.path; control.dataset.fileSource = reference.source;
        parent.append(control);
      } else if (/^https?:\/\//i.test(link[2])) {
        const anchor = node('a', link[1]); anchor.href = link[2]; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; parent.append(anchor);
      } else parent.append(document.createTextNode(token));
    }
    offset = match.index + token.length;
  }
  parent.append(document.createTextNode(text.slice(offset)));
}

/** Safe Markdown subset. Source code, equations and unsupported syntax survive. */
export function renderText(container, value, context = {}, onOpen = null) {
  container.replaceChildren();
  const text = String(value ?? '').slice(0, TEXT_LIMIT);
  const lines = text.split('\n');
  let code = null;
  let list = null;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.startsWith('```')) {
      if (code) code = null;
      else { const pre = node('pre'); code = node('code'); pre.append(code); container.append(pre); }
      list = null; continue;
    }
    if (code) { code.append(document.createTextNode(`${line}\n`)); continue; }
    if (!line.trim()) { list = null; continue; }
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    const bullet = line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)$/);
    if (line.includes('|') && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1])) {
      const rows = [line]; index += 1;
      while (index + 1 < lines.length && lines[index + 1].includes('|')) rows.push(lines[++index]);
      const table = node('table'); table.className = 'file-renderer-table';
      for (const [rowIndex, rowText] of rows.slice(0, 500).entries()) {
        const row = node('tr');
        for (const cell of rowText.replace(/^\s*\||\|\s*$/g, '').split('|').slice(0, 64)) {
          const element = node(rowIndex ? 'td' : 'th'); inline(element, cell.trim(), context, onOpen); row.append(element);
        }
        table.append(row);
      }
      container.append(table); list = null; continue;
    }
    if (bullet) {
      if (!list) { list = node('ul'); container.append(list); }
      const item = node('li'); inline(item, bullet[1], context, onOpen); list.append(item); continue;
    }
    list = null;
    const element = heading ? node(`h${Math.min(heading[1].length + 1, 6)}`) : node(line.startsWith('> ') ? 'blockquote' : 'p');
    inline(element, heading ? heading[2] : line.replace(/^> /, ''), context, onOpen);
    container.append(element);
  }
  if (String(value ?? '').length > TEXT_LIMIT) container.append(node('p', 'Anzeige begrenzt. Originaltext bleibt erhalten.', 'file-renderer-notice'));
}

export function registerFileRenderer(kind, renderer) {
  if (typeof kind !== 'string' || typeof renderer !== 'function') throw new TypeError('Invalid renderer');
  renderers.set(kind, renderer);
}

function renderTable(container, data) {
  const table = node('table', '', 'file-renderer-table');
  for (const [index, values] of (data.rows || []).slice(0, 500).entries()) {
    const row = node('tr');
    for (const value of values.slice(0, 64)) row.append(node(index ? 'td' : 'th', value));
    table.append(row);
  }
  container.append(table);
}

function renderSource(container, data) {
  if (data.ext === '.bib') {
    const entries = parseBibTeX(data.content || '');
    if (entries.length) renderTable(container, { rows: [['Key', 'Autor', 'Jahr', 'Titel'], ...entries.map(entry => [entry.key, entry.fields.author || '', entry.fields.year || '', entry.fields.title || ''])] });
  }
  if (data.ext === '.ipynb') {
    try {
      const notebook = JSON.parse(data.content);
      if (Array.isArray(notebook.cells)) {
        for (const [index, cell] of notebook.cells.slice(0, 100).entries()) {
          container.append(node('h4', `Zelle ${index + 1} (${cell.cell_type || 'unknown'})`));
          container.append(node('pre', Array.isArray(cell.source) ? cell.source.join('') : String(cell.source || '')));
          for (const output of (cell.outputs || []).slice(0, 20)) {
            const text = output.text || output.data?.['text/plain'];
            if (text) container.append(node('pre', (Array.isArray(text) ? text.join('') : String(text)).slice(0, 20000)));
          }
        }
        return;
      }
    } catch { /* Malformed notebooks remain visible as source; never execute. */ }
  }
  container.append(node('pre', data.content || '', 'file-renderer-source'));
}

registerFileRenderer('text', renderSource);
registerFileRenderer('json', renderSource);
registerFileRenderer('markdown', (container, data, options) => renderText(container, data.content, data, options.onOpen));
registerFileRenderer('table', renderTable);
for (const kind of ['image', 'audio', 'video', 'pdf']) {
  registerFileRenderer(kind, (container, data) => {
    const media = node(kind === 'image' ? 'img' : kind === 'pdf' ? 'iframe' : kind);
    media.src = data.safeRawUrl;
    media.className = 'file-renderer-media';
    if (kind === 'image') { media.alt = data.name; media.loading = 'lazy'; }
    if (kind === 'audio' || kind === 'video') { media.controls = true; media.preload = 'metadata'; }
    if (kind === 'pdf') { media.title = data.name; media.setAttribute('sandbox', 'allow-same-origin allow-downloads'); }
    container.append(media);
  });
}
registerFileRenderer('binary', (container) => container.append(node('p', 'Fuer dieses Format ist keine sichere Vorschau verfuegbar. Das unveraenderte Original kann heruntergeladen werden.')));

async function mutate(reference, action) {
  const response = await fetch(`/api/files/document/${encodeURIComponent(reference.path)}?source=${encodeURIComponent(reference.source)}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(action),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  document.dispatchEvent(new CustomEvent('brain5d:files-changed', { detail: reference }));
  return data;
}

export async function createTextFile(reference, content = '') {
  return mutate(reference, { action: 'create', content });
}

/** The same asynchronous renderer is used in the modal and in each chat card. */
export async function renderFile(container, reference, options = {}) {
  requests.get(container)?.abort();
  const controller = new AbortController(); requests.set(container, controller);
  container.replaceChildren(node('p', 'Datei wird geladen ...', 'file-renderer-loading'));
  container.classList.add('file-renderer'); container.dataset.renderState = 'loading';
  const source = reference?.source;
  const path = reference?.path;
  try {
    if (!['docs', 'research'].includes(source) || typeof path !== 'string') throw new Error('Ungueltige Dateireferenz');
    const response = await fetch(`/api/files/preview/${encodeURIComponent(path)}?source=${encodeURIComponent(source)}`, { signal: controller.signal });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    if (controller.signal.aborted) return null;
    const raw = `/api/files/raw/${encodeURIComponent(path)}?source=${encodeURIComponent(source)}`;
    data.safeRawUrl = raw;
    const header = node('header', '', 'fm-file-header file-renderer-header');
    header.append(node('strong', `${source}/${path}`));
    const actions = node('div', '', 'file-renderer-actions'); header.append(actions);
    const download = node('a', 'Original herunterladen'); download.href = `${raw}&download=1`; download.download = data.name; actions.append(download);
    const body = node('div', '', 'file-renderer-body');
    const notice = node('p', '', 'file-renderer-notice'); notice.setAttribute('role', 'status');
    container.replaceChildren(header, notice, body);
    container.dataset.renderState = 'ready'; container.dataset.fileKind = data.kind;
    notice.textContent = [data.read_only ? 'Schreibgeschuetztes Forschungsartefakt.' : '', data.truncated ? 'Begrenzte Vorschau; Original ist vollstaendig.' : '', data.notice || ''].filter(Boolean).join(' ');
    const renderOptions = { ...options, onOpen: options.onOpen || (ref => renderFile(container, ref, options)) };
    (renderers.get(data.kind) || renderers.get('binary'))(body, data, renderOptions);
    if (options.onClose) actions.append(button('Schliessen', options.onClose));
    if (options.chat !== true) actions.append(button('Im Chat anzeigen', () => {
      document.dispatchEvent(new CustomEvent('brain5d:chat-file', { detail: { source, path } }));
      options.onClose?.();
    }));
    const operation = async (action) => {
      try {
        const result = await mutate({ source, path }, { expected_sha256: data.sha256, ...action });
        options.onChange?.();
        if (action.action === 'trash') { container.replaceChildren(node('p', 'Datei in den lokalen Papierkorb verschoben.')); return; }
        await renderFile(container, { source, path: result.file.path }, options);
      } catch (error) { notice.textContent = error.message; notice.setAttribute('role', 'alert'); }
    };
    if (data.editable && options.manage !== false) {
      actions.append(button('Bearbeiten', () => {
        const editor = node('textarea', '', 'file-renderer-editor'); editor.value = data.raw_content ?? data.content;
        editor.setAttribute('aria-label', 'Dateiinhalt bearbeiten');
        body.replaceChildren(editor, button('Speichern', () => operation({ action: 'write', content: editor.value })), button('Abbrechen', () => renderFile(container, { source, path }, options)));
      }));
    }
    if (!data.read_only && data.sha256 && options.manage !== false) {
      actions.append(button('Umbenennen', () => { const destination = window.prompt('Neuer relativer Dateipfad', path); if (destination && destination !== path) operation({ action: 'rename', destination }); }));
      actions.append(button('In Papierkorb', () => { if (window.confirm(`${source}/${path} in den Papierkorb verschieben?`)) operation({ action: 'trash' }); }));
    }
    if (typeof data.content === 'string') actions.append(button('Text kopieren', async () => {
      try { await navigator.clipboard.writeText(data.raw_content ?? data.content); notice.textContent = 'Text kopiert.'; }
      catch { notice.textContent = 'Zwischenablage nicht verfuegbar.'; }
    }));
    options.onReady?.(data, { body, actions, notice });
    return data;
  } catch (error) {
    if (controller.signal.aborted) return null;
    container.dataset.renderState = 'error';
    const errorNode = node('p', error.message, 'file-renderer-error'); errorNode.setAttribute('role', 'alert');
    container.replaceChildren(errorNode, button('Erneut laden', () => renderFile(container, reference, options)));
    if (options.onClose) container.append(button('Schliessen', options.onClose));
    return null;
  }
}

/** Render chat text plus validated, lazy file cards without a second renderer. */
export function renderMessage(container, text, attachments = []) {
  const content = node('div', '', 'chat-markdown');
  const cards = node('div', '', 'chat-file-cards');
  const known = new Set();
  const add = (reference, expanded = false) => {
    const safe = fileReference(`${reference.source}/${reference.path}`);
    if (!safe) return;
    const key = `${safe.source}/${safe.path}`;
    const existing = [...cards.children].find(card => card.dataset.fileKey === key);
    if (existing) { if (expanded) existing.open = true; return; }
    if (known.size >= 8) return;
    known.add(key);
    const details = node('details', '', 'chat-file-card'); details.dataset.fileKey = key;
    const summary = node('summary', key); const preview = node('div');
    details.append(summary, preview); cards.append(details);
    let loaded = false;
    const load = () => { if (!loaded && details.open) { loaded = true; renderFile(preview, safe, { chat: true, manage: false, onOpen: ref => add(ref, true) }); } };
    details.addEventListener('toggle', load);
    details.open = expanded; load();
  };
  renderText(content, text, { source: 'research', path: '' }, ref => add(ref, true));
  container.replaceChildren(content, cards);
  for (const reference of Array.isArray(attachments) ? attachments : []) {
    if (reference && typeof reference.path === 'string') add(reference, true);
  }
}
