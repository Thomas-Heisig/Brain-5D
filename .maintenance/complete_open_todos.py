from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:60]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker in text:
        return
    target.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


replace(
    "src/dashboard/file_rendering.py",
    "import secrets\nimport shutil\nimport tempfile",
    "import secrets\nimport shutil\nimport struct\nimport subprocess\nimport tempfile",
)
replace(
    "src/dashboard/file_rendering.py",
    "ARCHIVE_BYTES = 32 * 1024 * 1024\nARCHIVE_EXTENSIONS",
    "ARCHIVE_BYTES = 32 * 1024 * 1024\nMEDIA_PROBE_BYTES = 64 * 1024\nPDF_TEXT_BYTES = 128 * 1024\nDIAGRAM_OUTPUT_BYTES = 2 * 1024 * 1024\nARCHIVE_EXTENSIONS",
)
helpers = r'''

def _image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read dimensions from bounded image headers without decoding pixels."""
    with path.open("rb") as stream:
        header = stream.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
            return cast(tuple[int, int], struct.unpack(">II", header[16:24]))
        if header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
            return cast(tuple[int, int], struct.unpack("<HH", header[6:10]))
    return None


def _ffprobe_metadata(path: Path) -> dict[str, Any]:
    executable = shutil.which("ffprobe")
    if not executable:
        return {}
    try:
        completed = subprocess.run(
            [executable, "-v", "error", "-probesize", str(MEDIA_PROBE_BYTES), "-analyzeduration", "1000000", "-show_entries", "format=duration,format_name:stream=codec_name,codec_type,width,height", "-of", "json", str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=4,
        )
        payload = json.loads(completed.stdout[:PDF_TEXT_BYTES])
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        return {}
    result: dict[str, Any] = {}
    format_info = payload.get("format") if isinstance(payload, dict) else None
    if isinstance(format_info, dict):
        if format_info.get("duration") is not None:
            try:
                result["duration_seconds"] = round(float(format_info["duration"]), 3)
            except (TypeError, ValueError):
                pass
        if format_info.get("format_name"):
            result["container"] = str(format_info["format_name"])
    streams = payload.get("streams") if isinstance(payload, dict) else None
    if isinstance(streams, list):
        codecs = sorted({str(item.get("codec_name")) for item in streams if isinstance(item, dict) and item.get("codec_name")})
        if codecs:
            result["codecs"] = codecs
        for item in streams:
            if isinstance(item, dict) and item.get("codec_type") == "video":
                if item.get("width") is not None:
                    result["width"] = int(item["width"])
                if item.get("height") is not None:
                    result["height"] = int(item["height"])
                break
    return result


def _media_metadata(path: Path, mime: str) -> dict[str, Any]:
    result: dict[str, Any] = {"mime_type": mime}
    if mime.startswith("image/"):
        dimensions = _image_dimensions(path)
        if dimensions:
            result["width"], result["height"] = dimensions
        result["metadata_probe"] = "header"
    elif mime.startswith(("audio/", "video/")):
        result.update(_ffprobe_metadata(path))
        result["metadata_probe"] = "ffprobe-bounded"
    return result


def _pdf_metadata(path: Path) -> tuple[dict[str, Any], str]:
    size = path.stat().st_size
    with path.open("rb") as stream:
        head = stream.read(MEDIA_PROBE_BYTES)
        tail = b""
        if size > MEDIA_PROBE_BYTES:
            stream.seek(max(0, size - MEDIA_PROBE_BYTES))
            tail = stream.read(MEDIA_PROBE_BYTES)
    sample = head + tail
    version = "unknown"
    match = re.match(rb"%PDF-([0-9.]+)", head)
    if match:
        version = match.group(1).decode("ascii", errors="replace")
    page_estimate = len(re.findall(rb"/Type\s*/Page(?!s)\b", sample))
    metadata: dict[str, Any] = {
        "pdf_version": version,
        "page_count": page_estimate or None,
        "page_count_source": "bounded-structure-estimate" if page_estimate else "unavailable",
    }
    text_preview = ""
    pdftotext = shutil.which("pdftotext")
    if pdftotext and size <= DIGEST_BYTES:
        try:
            completed = subprocess.run(
                [pdftotext, "-f", "1", "-l", "5", "-nopgbrk", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            text_preview = completed.stdout[:PDF_TEXT_BYTES]
            metadata["text_preview_pages"] = 5
            metadata["text_preview_source"] = "pdftotext"
        except (OSError, subprocess.SubprocessError):
            metadata["text_preview_source"] = "unavailable"
    else:
        metadata["text_preview_source"] = "unavailable"
    return metadata, text_preview


def _sanitize_local_svg(svg: str) -> str:
    if not svg or len(svg.encode("utf-8")) > DIAGRAM_OUTPUT_BYTES or not re.search(r"<svg\b", svg, re.IGNORECASE):
        return ""
    if re.search(r"<(?:script|foreignObject|iframe|object|embed)\b", svg, re.IGNORECASE):
        return ""
    svg = re.sub(r"\son[a-z]+\s*=\s*(['\"]).*?\1", "", svg, flags=re.IGNORECASE | re.DOTALL)
    svg = re.sub(r"\s(?:xlink:)?href\s*=\s*(['\"])(?!#).*?\1", "", svg, flags=re.IGNORECASE | re.DOTALL)
    return svg


def _local_diagram_svg(diagram_format: str, source: str) -> tuple[str, str]:
    if diagram_format == "graphviz":
        executable = shutil.which("dot")
        if not executable:
            return "", "unavailable"
        command = [executable, "-Tsvg"]
    elif diagram_format == "plantuml":
        executable = shutil.which("plantuml")
        if not executable:
            return "", "unavailable"
        command = [executable, "-tsvg", "-pipe"]
    else:
        return "", "unsupported"
    try:
        completed = subprocess.run(command, input=source[:PREVIEW_BYTES], check=True, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return "", "failed"
    safe = _sanitize_local_svg(completed.stdout)
    return (safe, "local") if safe else ("", "rejected")
'''
replace("src/dashboard/file_rendering.py", "\ndef file_is_read_only(source: str, path: str) -> bool:", helpers + "\n\ndef file_is_read_only(source: str, path: str) -> bool:")
replace(
    "src/dashboard/file_rendering.py",
    '''        if mime.startswith(("image/", "audio/", "video/")) and ext not in {
            ".svg",
            ".html",
        }:
            result["kind"] = mime.split("/", 1)[0]
        elif ext == ".pdf":
            result["kind"] = "pdf"
''',
    '''        if mime.startswith(("image/", "audio/", "video/")) and ext not in {
            ".svg",
            ".html",
        }:
            result["kind"] = mime.split("/", 1)[0]
            result["media_metadata"] = _media_metadata(candidate, mime)
        elif ext == ".pdf":
            result["kind"] = "pdf"
            pdf_metadata, pdf_text = _pdf_metadata(candidate)
            result["pdf_metadata"] = pdf_metadata
            result["content"] = pdf_text
            result["truncated"] = len(pdf_text) >= PDF_TEXT_BYTES
''',
)
replace(
    "src/dashboard/file_rendering.py",
    '''                    if ext in DIAGRAM_FORMATS:
                        result["diagram_format"] = DIAGRAM_FORMATS[ext]
''',
    '''                    if ext in DIAGRAM_FORMATS:
                        result["diagram_format"] = DIAGRAM_FORMATS[ext]
                        diagram_svg, renderer = _local_diagram_svg(DIAGRAM_FORMATS[ext], content)
                        result["diagram_renderer"] = renderer
                        if diagram_svg:
                            result["diagram_svg"] = diagram_svg
''',
)

replace("src/dashboard/static/file-renderer.js", "import { parseBibTeX } from './bibtex-viewer.js';", "import { parseBibTeX, formatCitationStyle, formatRis } from './bibtex-viewer.js';")
replace(
    "src/dashboard/static/file-renderer.js",
    "    const result = await window.mammoth.convertToHtml({ arrayBuffer: await response.arrayBuffer() });",
    '''    const result = await window.mammoth.convertToHtml({
      arrayBuffer: await response.arrayBuffer(),
      styleMap: [
        "p[style-name='Page Break'] => hr.fm-docx-page-break:fresh",
        "p[style-name='Section Break'] => hr.fm-docx-section-break:fresh",
      ],
    });''',
)
replace(
    "src/dashboard/static/file-renderer.js",
    "  container.append(table);\n}\n\nfunction renderHighlightedCode",
    '''  container.append(table);
  const controls = node('div', '', 'file-renderer-bib-controls');
  const style = document.createElement('select');
  style.className = 'file-renderer-citation-style';
  style.setAttribute('aria-label', 'Zitierstil');
  for (const [value, label] of [['short', 'Kurz'], ['apa', 'APA'], ['ieee', 'IEEE']]) {
    const option = document.createElement('option'); option.value = value; option.textContent = label; style.append(option);
  }
  controls.append(style);
  controls.append(button('Zitate kopieren', async () => {
    const citations = entries.map((entry, index) => formatCitationStyle(entry, style.value, index + 1)).join('\\n');
    try { await navigator.clipboard.writeText(citations); } catch { /* optional */ }
  }));
  controls.append(button('RIS exportieren', () => {
    const blob = new Blob([formatRis(entries)], { type: 'application/x-research-info-systems;charset=utf-8' });
    const url = URL.createObjectURL(blob); const anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'references.ris'; document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
  }));
  container.append(controls);
}

function renderHighlightedCode''',
)
replace(
    "src/dashboard/static/file-renderer.js",
    '''async function renderDiagram(container, data) {
  const format = data.diagram_format || 'unknown';
  const pre = node('pre');
  const source = node('code', data.content || '', `language-${format}`);
  pre.append(source);
  container.append(pre);
  if (format === 'mermaid') {
    await renderMermaidBlocks(container);
    return;
  }
  container.append(node('p', `${format === 'graphviz' ? 'Graphviz' : 'PlantUML'}-Quellen werden sicher als Text angezeigt. Eine lokale SVG-Konvertierung ist nicht aktiviert.`, 'file-renderer-notice'));
}
''',
    '''async function renderDiagram(container, data) {
  const format = data.diagram_format || 'unknown';
  const pre = node('pre');
  const source = node('code', data.content || '', `language-${format}`);
  pre.append(source);
  container.append(pre);
  if (format === 'mermaid') { await renderMermaidBlocks(container); return; }
  if (data.diagram_svg) {
    const figure = node('figure', '', 'file-renderer-diagram fm-local-diagram');
    figure.append(safeDocumentFragment(data.diagram_svg));
    container.prepend(figure);
    container.append(node('p', `${format} wurde lokal in eine bereinigte SVG-Vorschau konvertiert.`, 'file-renderer-notice'));
    return;
  }
  container.append(node('p', `Lokale ${format}-Konvertierung: ${data.diagram_renderer || 'nicht verfuegbar'}. Die Quelle bleibt sichtbar.`, 'file-renderer-notice'));
}
''',
)
replace(
    "src/dashboard/static/file-renderer.js",
    '''for (const kind of ['image', 'audio', 'video', 'pdf']) {
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
''',
    '''for (const kind of ['image', 'audio', 'video', 'pdf']) {
  registerFileRenderer(kind, (container, data) => {
    const metadata = kind === 'pdf' ? data.pdf_metadata : data.media_metadata;
    if (metadata && Object.keys(metadata).length) renderTable(container, { rows: [['Metadatum', 'Wert'], ...Object.entries(metadata).map(([key, value]) => [key, Array.isArray(value) ? value.join(', ') : String(value ?? '')])] });
    if (kind === 'pdf' && data.content) {
      const details = node('details', '', 'file-renderer-pdf-text');
      details.append(node('summary', 'Begrenzte PDF-Textvorschau'), node('pre', data.content));
      container.append(details);
    }
    const media = node(kind === 'image' ? 'img' : kind === 'pdf' ? 'iframe' : kind);
    media.src = data.safeRawUrl; media.className = 'file-renderer-media';
    if (kind === 'image') { media.alt = data.name; media.loading = 'lazy'; }
    if (kind === 'audio' || kind === 'video') { media.controls = true; media.preload = 'metadata'; }
    if (kind === 'pdf') { media.title = data.name; media.setAttribute('sandbox', 'allow-same-origin allow-downloads'); }
    container.append(media);
  });
}
''',
)
split_helpers = r'''

function lineDiff(localText, remoteText) {
  const local = String(localText || '').split('\n');
  const remote = String(remoteText || '').split('\n');
  const rows = [['Zeile', 'Lokal', 'Aktuell']];
  const count = Math.min(Math.max(local.length, remote.length), 500);
  for (let index = 0; index < count; index += 1) if ((local[index] || '') !== (remote[index] || '')) rows.push([String(index + 1), local[index] || '', remote[index] || '']);
  return rows;
}

function renderConflictDiff(container, localText, remoteText) {
  container.replaceChildren(node('h4', 'Speicherkonflikt'));
  container.append(node('p', 'Die Datei wurde zwischenzeitlich geaendert. Lokal und aktueller Stand werden verglichen.', 'file-renderer-error'));
  renderTable(container, { rows: lineDiff(localText, remoteText) });
}

async function renderEditorPreview(container, data, value, options) {
  const preview = { ...data, content: value, raw_content: value };
  if (preview.ext === '.json') {
    try { preview.content = JSON.stringify(JSON.parse(value), null, 2); preview.kind = 'json'; } catch { preview.kind = 'text'; }
  } else if (['.md', '.markdown'].includes(preview.ext)) preview.kind = 'markdown';
  else preview.kind = 'text';
  container.replaceChildren();
  await (renderers.get(preview.kind) || renderers.get('text'))(container, preview, options);
}
'''
replace("src/dashboard/static/file-renderer.js", "\nasync function mutate(reference, action) {", split_helpers + "\n\nasync function mutate(reference, action) {")
replace(
    "src/dashboard/static/file-renderer.js",
    '''    if (data.editable && options.manage !== false) {
      actions.append(button('Bearbeiten', () => {
        const editor = node('textarea', '', 'file-renderer-editor'); editor.value = data.raw_content ?? data.content;
        editor.setAttribute('aria-label', 'Dateiinhalt bearbeiten');
        body.replaceChildren(editor, button('Speichern', () => operation({ action: 'write', content: editor.value })), button('Abbrechen', () => renderFile(container, { source, path }, options)));
      }));
    }
''',
    '''    if (data.editable && options.manage !== false) {
      actions.append(button('Bearbeiten', () => {
        const split = node('div', '', 'file-renderer-editor-split');
        const sourcePane = node('section', '', 'file-renderer-editor-source');
        const previewPane = node('section', '', 'file-renderer-editor-preview');
        const editor = node('textarea', '', 'file-renderer-editor'); editor.value = data.raw_content ?? data.content;
        editor.setAttribute('aria-label', 'Dateiinhalt bearbeiten');
        const controls = node('div', '', 'file-renderer-editor-controls');
        controls.append(button('Speichern', () => operation({ action: 'write', content: editor.value })), button('Abbrechen', () => renderFile(container, { source, path }, options)));
        sourcePane.append(node('h4', 'Quelle'), editor, controls); previewPane.append(node('h4', 'Vorschau'));
        split.append(sourcePane, previewPane); body.replaceChildren(split);
        let timer = null;
        const refresh = () => renderEditorPreview(previewPane, data, editor.value, renderOptions);
        editor.addEventListener('input', () => { window.clearTimeout(timer); timer = window.setTimeout(refresh, 120); });
        refresh();
      }));
    }
''',
)
replace(
    "src/dashboard/static/file-renderer.js",
    "      } catch (error) { notice.textContent = error.message; notice.setAttribute('role', 'alert'); }\n    };",
    '''      } catch (error) {
        notice.textContent = error.message; notice.setAttribute('role', 'alert');
        if (action.action === 'write' && /version|conflict|changed/i.test(error.message || '')) {
          try {
            const latestResponse = await fetch(`/api/files/preview/${encodeURIComponent(path)}?source=${encodeURIComponent(source)}`);
            const latest = await latestResponse.json();
            if (latestResponse.ok) renderConflictDiff(body, action.content, latest.raw_content ?? latest.content ?? '');
          } catch { /* retain original error */ }
        }
      }
    };''',
)

replace(
    "src/dashboard/static/bibtex-viewer.js",
    '''function formatCitation(entry) {
  const author = formatAuthorShort(entry.fields.author);
  const year = entry.fields.year || 'o.J.';
  return `(${author}, ${year})`;
}
''',
    '''function formatCitation(entry) {
  const author = formatAuthorShort(entry.fields.author);
  const year = entry.fields.year || 'o.J.';
  return `(${author}, ${year})`;
}

function formatCitationStyle(entry, style = 'short', index = 1) {
  const author = entry.fields.author || 'Anonym';
  const year = entry.fields.year || 'o.J.';
  const title = entry.fields.title || entry.key;
  const venue = entry.fields.journal || entry.fields.booktitle || entry.fields.publisher || '';
  if (style === 'apa') return `${author} (${year}). ${title}.${venue ? ` ${venue}.` : ''}`;
  if (style === 'ieee') return `[${index}] ${author}, “${title},”${venue ? ` ${venue},` : ''} ${year}.`;
  return formatCitation(entry);
}

function formatRis(entries) {
  const typeMap = { article: 'JOUR', book: 'BOOK', inproceedings: 'CPAPER', phdthesis: 'THES', mastersthesis: 'THES', techreport: 'RPRT' };
  return entries.map((entry) => {
    const lines = [`TY  - ${typeMap[entry.type] || 'GEN'}`, `ID  - ${entry.key}`];
    for (const author of String(entry.fields.author || '').split(' and ').filter(Boolean)) lines.push(`AU  - ${author}`);
    if (entry.fields.title) lines.push(`TI  - ${entry.fields.title}`);
    if (entry.fields.journal) lines.push(`JO  - ${entry.fields.journal}`);
    if (entry.fields.booktitle) lines.push(`T2  - ${entry.fields.booktitle}`);
    if (entry.fields.year) lines.push(`PY  - ${entry.fields.year}`);
    if (entry.fields.doi) lines.push(`DO  - ${entry.fields.doi}`);
    if (entry.fields.url) lines.push(`UR  - ${entry.fields.url}`);
    lines.push('ER  - ');
    return lines.join('\\r\\n');
  }).join('\\r\\n\\r\\n');
}
''',
)
replace("src/dashboard/static/bibtex-viewer.js", "      const citation = formatCitation(entry);", "      const style = document.querySelector('.bibtex-citation-style')?.value || 'short';\n      const citation = formatCitationStyle(entry, style, idx + 1);")
replace(
    "src/dashboard/static/bibtex-viewer.js",
    '''      <button class="bibtex-copy-all-btn" title="Copy all as BibTeX">📋 Copy all</button>
      <button class="bibtex-export-btn" title="Download .bib file">💾 Download</button>''',
    '''      <select class="bibtex-citation-style" title="Citation style" aria-label="Citation style"><option value="short">Short</option><option value="apa">APA</option><option value="ieee">IEEE</option></select>
      <button class="bibtex-copy-all-btn" title="Copy all as BibTeX">📋 Copy all</button>
      <button class="bibtex-export-ris-btn" title="Download RIS file">⬇ RIS</button>
      <button class="bibtex-export-btn" title="Download .bib file">💾 Download</button>''',
)
replace(
    "src/dashboard/static/bibtex-viewer.js",
    "  // Export / Download\n  const exportBtn = document.querySelector('.bibtex-export-btn');",
    '''  // RIS export
  const risBtn = document.querySelector('.bibtex-export-ris-btn');
  if (risBtn) {
    risBtn.addEventListener('click', () => {
      const blob = new Blob([formatRis(bibtexEntries)], { type: 'application/x-research-info-systems;charset=utf-8' });
      const url = URL.createObjectURL(blob); const a = document.createElement('a');
      a.href = url; a.download = (bibtexFileName || 'references.bib').replace(/\\.bib$/i, '.ris');
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    });
  }

  // Export / Download
  const exportBtn = document.querySelector('.bibtex-export-btn');''',
)
replace("src/dashboard/static/bibtex-viewer.js", "export { initBibTeXViewer, wireBibTeXEvents, parseBibTeX, formatCitation, formatBibTeXSnippet, formatBibTeXFull, validateEntry };", "export { initBibTeXViewer, wireBibTeXEvents, parseBibTeX, formatCitation, formatCitationStyle, formatRis, formatBibTeXSnippet, formatBibTeXFull, validateEntry };")

append_once(
    "src/dashboard/static/styles.css",
    "/* TODO completion: canonical file viewer advanced surfaces */",
    r'''
/* TODO completion: canonical file viewer advanced surfaces */
.file-renderer-editor-split { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:1rem; min-height:22rem; }
.file-renderer-editor-source,.file-renderer-editor-preview { min-width:0; display:flex; flex-direction:column; gap:.65rem; }
.file-renderer-editor-split .file-renderer-editor { flex:1; min-height:18rem; width:100%; resize:vertical; font-family:var(--font-mono, monospace); }
.file-renderer-editor-controls,.file-renderer-bib-controls { display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; }
.fm-docx-page-break,.fm-docx-section-break { border:0; border-top:1px dashed var(--border-color, #777); margin:1.5rem 0; }
.file-renderer-pdf-text pre { max-height:18rem; overflow:auto; }
.fm-local-diagram svg { max-width:100%; height:auto; }
@media (max-width: 900px) { .file-renderer-editor-split { grid-template-columns:1fr; } }
''',
)

replace("tests/test_file_rendering.py", "import json\nimport zipfile", "import json\nimport struct\nimport zipfile")
append_once(
    "tests/test_file_rendering.py",
    "def test_media_pdf_and_local_diagram_todo_contracts(",
    r'''
def test_media_pdf_and_local_diagram_todo_contracts(
    service: FilePreviewService, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace
    from src.dashboard import file_rendering

    png = service.roots["docs"] / "sample.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 320, 200) + b"\x00" * 8)
    image = service.preview("docs", png.name)
    assert image["media_metadata"]["width"] == 320
    assert image["media_metadata"]["height"] == 200

    pdf = service.roots["docs"] / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.7\n1 0 obj << /Type /Page >> endobj\n%%EOF")
    pdf_preview = service.preview("docs", pdf.name)
    assert pdf_preview["pdf_metadata"]["pdf_version"] == "1.7"
    assert pdf_preview["pdf_metadata"]["page_count"] == 1

    graph = service.roots["docs"] / "flow.dot"
    graph.write_text("digraph G { a -> b; }")
    monkeypatch.setattr(file_rendering.shutil, "which", lambda name: "/usr/bin/dot" if name == "dot" else None)
    monkeypatch.setattr(file_rendering.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'))
    diagram = service.preview("docs", graph.name)
    assert diagram["diagram_renderer"] == "local"
    assert diagram["diagram_svg"].startswith("<svg")


def test_file_viewer_advanced_frontend_contracts_present() -> None:
    root = Path(__file__).resolve().parents[1]
    renderer = (root / "src/dashboard/static/file-renderer.js").read_text(encoding="utf-8")
    bibtex = (root / "src/dashboard/static/bibtex-viewer.js").read_text(encoding="utf-8")
    assert "file-renderer-editor-split" in renderer
    assert "renderConflictDiff" in renderer
    assert "diagram_svg" in renderer
    assert "pdf_metadata" in renderer
    assert "formatRis" in renderer
    assert "bibtex-export-ris-btn" in bibtex
''',
)

for path in ["README.md", "docs/README.md"]:
    append_once(
        path,
        "## Full-stack File Viewer completion — 2026-09-08",
        """
## Full-stack File Viewer completion — 2026-09-08

The repository File Viewer is the canonical renderer for Dashboard, Research and Chat file cards. It now includes bounded media metadata, bounded PDF metadata/text when local tools are available, optional local Graphviz/PlantUML-to-SVG conversion, DOCX page/section markers, RIS export with selectable citation styles, and a responsive split editor with live preview and optimistic-lock conflict diff. Scientific artifacts remain read-only and local converters never upload source material.
""",
    )
append_once("docs/08-roadmap/ROADMAP.md", "### 2026-09-08 — File Viewer backlog completion", """
### 2026-09-08 — File Viewer backlog completion

- Completed the remaining executable File Viewer backlog through the shared Dashboard/Research Chat renderer.
- Added bounded media/PDF metadata and optional local-only Graphviz/PlantUML rendering.
- Added DOCX structural markers, RIS/APA/IEEE citation output and a responsive split editor with live preview/conflict diff.
- Human-review/EVID promotions remain deliberately gated and are never auto-approved by CI or AI tooling.
""")
append_once("docs/07-changelog/CHANGELOG.md", "### 2026-09-08 — Full-stack File Viewer completion", """
### 2026-09-08 — Full-stack File Viewer completion

- Added bounded media/PDF metadata and local-only optional Graphviz/PlantUML SVG previews.
- Added DOCX structural markers, RIS export, short/APA/IEEE citation formatting and split editing with conflict comparison.
""")

todo = ROOT / "docs/08-roadmap/TODO.md"
text = todo.read_text(encoding="utf-8")
for item in [
    "Add optional page-break and section markers when Mammoth exposes them without recreating a nested paper surface.",
    "Add RIS export and richer citation style previews.",
    "Add a richer split-pane editor with language-aware preview and conflict diff.",
    "Add browser media metadata (dimensions, duration and codec) without decoding full files.",
    "Add bounded PDF text/page metadata and optional local Graphviz/PlantUML conversion.",
    "Add an optional local Graphviz/PlantUML to SVG converter without sending research sources to a remote service.",
]:
    text = text.replace(f"- [ ] {item}", f"- [x] {item}")
text = text.replace("**Updated:** 2026-09-07", "**Updated:** 2026-09-08")
todo.write_text(text, encoding="utf-8")
