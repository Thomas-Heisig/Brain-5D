from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected snippet not found in {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# 1) Keep RQ-SNN-001 executable without pretending PING is primary evidence.
replace_once(
    "src/dashboard/experiment_workflow.py",
    '''        if question_id == "RQ-SNN-001":\n            raise WorkflowValidationError(\n                "RQ-SNN-001 requires a dedicated long-term stability protocol with sustained activity; "\n                "run_ping is not valid primary evidence for this research question."\n            )\n''',
    '''        if question_id == "RQ-SNN-001":\n            # Keep the UI workflow executable, but never relabel an impulse-response\n            # PING run as primary evidence for long-term stability. The complete\n            # suite is diagnostic only; _semantic_status deliberately keeps this RQ\n            # at MISMATCH until a dedicated sustained-activity protocol exists.\n            return "run_all"\n''',
)

# Echo effective seeds in the result so the UI can display what really executed.
replace_once(
    "src/dashboard/experiment_workflow.py",
    '''            "result": {\n                "run_count": len(runs),\n                "duration_seconds": duration,\n                "runner": runner_name,\n                "ticks_requested": workflow.ticks,\n                "tick_validation": tick_validation,\n            },\n''',
    '''            "result": {\n                "run_count": len(runs),\n                "duration_seconds": duration,\n                "runner": runner_name,\n                "ticks_requested": workflow.ticks,\n                "seeds_executed": list(effective_seeds),\n                "tick_validation": tick_validation,\n            },\n''',
)

# 2) RQ-SNN-002 recurrence experiments are semantically classifiable.
replace_once(
    "src/research/experiment_summary.py",
    '''    if question_id == "RQ-SNN-001":\n        return (\n            "MISMATCH",\n            "RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. Ein einzelner Impuls bzw. science_all_v1 mit langer stiller Nachlaufphase ist dafuer keine ausreichende Primaerpruefung.",\n        )\n''',
    '''    if question_id == "RQ-SNN-002":\n        return classify(\n            {"recurrence_off", "recurrence_on"}.issubset(plain),\n            "RQ-SNN-002 erwartet einen kontrollierten Impulsantwort-Vergleich mit recurrence_off und recurrence_on.",\n        )\n    if question_id == "RQ-SNN-001":\n        return (\n            "MISMATCH",\n            "RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. science_suite_v1/science_all_v1 bleiben dafuer diagnostisch; eine Primaerpruefung erfordert weiterhin ein dediziertes Sustained-Activity-Protokoll.",\n        )\n''',
)

# 3) The unified viewer is the one presentation surface for all experiment files.
replace_once(
    "src/dashboard/static/file-viewer.js",
    "async function openFMFile(path) {\n",
    "export async function openFMFile(path) {\n",
)
replace_once(
    "src/dashboard/static/file-viewer.js",
    '''  viewer.classList.remove('fm-viewer-hidden');\n  viewer.innerHTML = '<div class="fm-loading">📂 Loading file…</div>';\n''',
    '''  viewer.classList.remove('fm-viewer-hidden');\n  viewer.classList.add('fm-viewer-modal');\n  document.body.classList.add('fm-viewer-open');\n  viewer.innerHTML = '<div class="fm-loading">📂 Loading file…</div>';\n''',
)
# All viewer close buttons use the same helper behavior via delegated listener.
replace_once(
    "src/dashboard/static/file-viewer.js",
    '''function renderFMContent(content, ext, path = '') {\n''',
    '''function closeFMViewer() {\n  const viewer = document.getElementById('fm-viewer');\n  if (!viewer) return;\n  viewer.classList.add('fm-viewer-hidden');\n  viewer.classList.remove('fm-viewer-modal');\n  document.body.classList.remove('fm-viewer-open');\n}\n\ndocument.addEventListener('click', event => {\n  if (event.target.closest?.('#fm-close-viewer')) closeFMViewer();\n});\n\ndocument.addEventListener('keydown', event => {\n  if (event.key === 'Escape' && document.body.classList.contains('fm-viewer-open')) closeFMViewer();\n});\n\nfunction renderFMContent(content, ext, path = '') {\n''',
)
# Mermaid blocks need their language class preserved.
replace_once(
    "src/dashboard/static/file-viewer.js",
    '''    return `<div class="fm-code-wrapper">${langLabel}<button class="fm-copy-btn" data-content="${escapeHtml(code.trim())}">📋 Copy</button><pre class="fm-code fm-code-block"><code>${escapeHtml(code.trim())}</code></pre></div>`;\n''',
    '''    const languageClass = lang ? ` language-${escapeHtml(lang.toLowerCase())}` : '';\n    return `<div class="fm-code-wrapper">${langLabel}<button class="fm-copy-btn" data-content="${escapeHtml(code.trim())}">📋 Copy</button><pre class="fm-code fm-code-block"><code class="${languageClass.trim()}">${escapeHtml(code.trim())}</code></pre></div>`;\n''',
)
# Resolve escaped underscores and reject upward traversal for Markdown links.
replace_once(
    "src/dashboard/static/file-viewer.js",
    '''  html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, (_, label, target) => {\n    if (/^(https?:|mailto:|#)/i.test(target)) {\n      return `<a href="${escapeHtml(target)}" target="_blank" rel="noopener" class="fm-md-link">${label}</a>`;\n    }\n    const base = currentPath.split('/').slice(0, -1);\n    target.split('/').forEach(part => {\n      if (!part || part === '.') return;\n      if (part === '..') base.pop();\n      else base.push(part);\n    });\n    return `<a href="#" data-fm-path="${escapeHtml(base.join('/'))}" class="fm-md-link">${label}</a>`;\n  });\n''',
    '''  html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, (_, label, target) => {\n    if (/^(https?:|mailto:|#)/i.test(target)) {\n      return `<a href="${escapeHtml(target)}" target="_blank" rel="noopener" class="fm-md-link">${label}</a>`;\n    }\n    const normalizedTarget = target.replace(/\\\\_/g, '_').split('#')[0].split('?')[0];\n    const base = currentPath.split('/').slice(0, -1);\n    let safe = true;\n    normalizedTarget.split('/').forEach(part => {\n      if (!part || part === '.') return;\n      if (part === '..') {\n        if (!base.length) safe = false;\n        else base.pop();\n      } else base.push(part);\n    });\n    if (!safe) return `<span class="fm-link-invalid" title="Blocked unsafe relative path">${label}</span>`;\n    return `<a href="#" data-fm-path="${escapeHtml(base.join('/'))}" class="fm-md-link">${label}</a>`;\n  });\n''',
)
# Render inline scientific formula markup legibly without depending on an SVG math engine.
replace_once(
    "src/dashboard/static/file-viewer.js",
    '''  // Headings (### → h4, ## → h3, # → h2)\n''',
    '''  // Scientific inline formulas. Keep a readable textual representation in\n  // the document DOM/copy buffer instead of an opaque SVG-only accessibility node.\n  html = html.replace(/\\$([^$\\n]+)\\$/g, (_, formula) =>\n    `<span class="fm-math" role="math" aria-label="${escapeHtml(formula)}">${escapeHtml(formula)}</span>`\n  );\n\n  // Headings (### → h4, ## → h3, # → h2)\n''',
)

# 4) Experiment workflow uses the unified popup viewer and visible effective parameters.
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''"use strict";\n\n''',
    '''"use strict";\n\nimport { openFMFile } from "./file-viewer.js";\n\n''',
)
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''    this.elements.question?.addEventListener("change", () => {\n      this._renderHypotheses();\n      this._renderContract();\n    });\n''',
    '''    this.elements.question?.addEventListener("change", () => {\n      this._renderHypotheses();\n      this._alignProtocolWithQuestion();\n      this._renderContract();\n    });\n''',
)
# Canonical PING preset should default to the registered SNN impulse-response RQ.
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''      science_suite_v1: {\n        question: "RQ-PING-001",\n        hypothesis: "H-PING-001-A",\n''',
    '''      science_suite_v1: {\n        question: "RQ-SNN-002",\n        hypothesis: "H-SNN-002-A",\n''',
)
# Preserve user-selected seed/tick values on question alignment while choosing a compatible protocol.
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''  _applyProtocol() {\n''',
    '''  _alignProtocolWithQuestion() {\n    const questionId = this.elements.question?.value || "";\n    if (!questionId || !this.elements.protocol) return;\n    const operational = this.protocols.find(item => item.research_question === questionId && item.preregistration);\n    if (operational) {\n      const currentSeeds = this.elements.seeds?.value;\n      const currentTicks = this.elements.ticks?.value;\n      this.elements.protocol.value = operational.id;\n      this._applyProtocol();\n      if (this.elements.seeds && currentSeeds) this.elements.seeds.value = currentSeeds;\n      if (this.elements.ticks && currentTicks) this.elements.ticks.value = currentTicks;\n      this._renderContract();\n      return;\n    }\n    if (questionId === "RQ-SNN-001" && this.elements.protocol.value === "science_suite_v1") {\n      // Long-term stability has no dedicated primary protocol yet. Use the complete\n      // suite as an executable diagnostic rather than aborting, while preserving\n      // the selected RQ/H and retaining MISMATCH evidence semantics server-side.\n      this.elements.protocol.value = "science_all_v1";\n      this.activePreset = null;\n      this._renderContract();\n    }\n  }\n\n  _applyProtocol() {\n''',
)
# Display actual seeds returned by backend.
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''        if (typeof runResult.ticks_requested === "number") lines.push(`Ticks angefordert: ${runResult.ticks_requested}`);\n''',
    '''        if (typeof runResult.ticks_requested === "number") lines.push(`Ticks angefordert: ${runResult.ticks_requested}`);\n        if (Array.isArray(runResult.seeds_executed)) lines.push(`Seeds ausgeführt: ${runResult.seeds_executed.join(", ")}`);\n''',
)
# Remove bulky inline report area from the normal page.
replace_once(
    "src/dashboard/static/experiment-workflow.js",
    '''        </div>\n        <div id="workflow-inline-report" class="workflow-inline-report" hidden></div>`;\n''',
    '''        </div>`;\n''',
)
# All experiment artefacts go through the complete file viewer.
start = '''  async _openArtifact(path) {\n    if (!path) return;\n    const inline = byId("workflow-inline-report");\n    if (!inline) return;\n    inline.hidden = false;\n    inline.innerHTML = `<div class="fm-loading">Loading ${escapeHtml(path)}…</div>`;\n    try {\n      const file = await this._readResearchFile(path);\n      if (file.is_binary) {\n        inline.innerHTML = `<p>Binary artefact: <a target="_blank" rel="noopener" href="/api/files/content/${encodeURIComponent(path)}?source=research">${escapeHtml(path)}</a></p>`;\n        return;\n      }\n      const content = file.content || "";\n      if (/\\.json$/i.test(path)) {\n        let formatted = content;\n        try { formatted = JSON.stringify(JSON.parse(content), null, 2); } catch { /* keep source */ }\n        inline.innerHTML = `<div class="inline-report-header"><strong>${escapeHtml(path)}</strong></div><pre>${escapeHtml(formatted)}</pre>`;\n      } else {\n        inline.innerHTML = `<div class="inline-report-header"><strong>${escapeHtml(path)}</strong></div><pre class="inline-markdown-source">${escapeHtml(content)}</pre>`;\n      }\n      this.currentViewerPath = path;\n    } catch (error) {\n      inline.innerHTML = `<div class="workflow-warning">⚠ ${escapeHtml(error.message)}</div>`;\n    }\n  }\n'''
end = '''  async _openArtifact(path) {\n    if (!path) return;\n    this.currentViewerPath = path;\n    await openFMFile(path);\n    this._installExperimentPopupActions(path);\n  }\n\n  _installExperimentPopupActions(path) {\n    const viewer = byId("fm-viewer");\n    const header = viewer?.querySelector(".fm-file-header-actions");\n    if (!viewer || !header || header.querySelector("[data-experiment-popup-actions]")) return;\n    const group = document.createElement("span");\n    group.dataset.experimentPopupActions = "true";\n    group.className = "workflow-popup-actions";\n    group.innerHTML = `\n      <button type="button" class="fm-file-action-btn" data-popup-artifact="report">Report</button>\n      <button type="button" class="fm-file-action-btn" data-popup-artifact="summary">Summary</button>\n      <button type="button" class="fm-file-action-btn" data-popup-artifact="statistics">Statistics</button>\n      <button type="button" class="fm-file-action-btn" data-popup-artifact="raw">Raw Index</button>`;\n    header.prepend(group);\n    group.querySelectorAll("[data-popup-artifact]").forEach(button => {\n      button.addEventListener("click", () => {\n        const kind = button.dataset.popupArtifact;\n        const target = kind === "raw" ? this._experimentArtifact("DATA/runs_index.json") : this.lastResult?.[kind];\n        if (target && target !== path) this._openArtifact(target);\n      });\n    });\n  }\n'''
replace_once("src/dashboard/static/experiment-workflow.js", start, end)

# 5) Make the unified viewer a real system-level popup, not another output area.
p = Path("src/dashboard/static/styles.css")
css = p.read_text(encoding="utf-8")
marker = "/* Brain-5D unified file viewer modal */"
if marker not in css:
    css += '''\n\n/* Brain-5D unified file viewer modal */\nbody.fm-viewer-open { overflow: hidden; }\n.fm-viewer.fm-viewer-modal:not(.fm-viewer-hidden) {\n  position: fixed !important;\n  inset: 3vh 3vw !important;\n  z-index: 20000 !important;\n  display: flex !important;\n  flex-direction: column;\n  width: auto !important;\n  max-width: none !important;\n  height: 94vh !important;\n  max-height: 94vh !important;\n  background: var(--panel-bg, #10151f);\n  border: 1px solid var(--border, #334155);\n  border-radius: 14px;\n  box-shadow: 0 0 0 100vmax rgba(0, 0, 0, 0.68), 0 24px 80px rgba(0, 0, 0, 0.55);\n  overflow: hidden !important;\n}\n.fm-viewer.fm-viewer-modal .fm-content,\n.fm-viewer.fm-viewer-modal .fm-docx-viewer,\n.fm-viewer.fm-viewer-modal .fm-sheet-viewer,\n.fm-viewer.fm-viewer-modal .fm-pdf-container {\n  flex: 1 1 auto;\n  min-height: 0;\n  overflow: auto;\n}\n.fm-viewer.fm-viewer-modal .fm-file-header {\n  position: sticky;\n  top: 0;\n  z-index: 3;\n}\n.fm-math {\n  display: inline-block;\n  padding: 0.08rem 0.28rem;\n  border-radius: 4px;\n  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;\n  background: rgba(127, 127, 127, 0.12);\n  white-space: nowrap;\n}\n.workflow-popup-actions { display: inline-flex; gap: 0.3rem; align-items: center; }\n'''
    p.write_text(css, encoding="utf-8")

# 6) Tests: RQ-SNN-001 now runs diagnostic suite; SNN-002 is a direct semantic match.
p = Path("tests/test_scientific_execution_contract.py")
t = p.read_text(encoding="utf-8")
t = t.replace(
    '''def test_snn_001_rejects_ping_as_primary_evidence() -> None:\n    with pytest.raises(\n        WorkflowValidationError, match="dedicated long-term stability protocol"\n    ):\n        ExperimentWorkflowService._science_runner(  # pyright: ignore[reportPrivateUsage]\n            {"protocol": "science_suite_v1"}, _workflow("RQ-SNN-001")\n        )\n''',
    '''def test_snn_001_uses_diagnostic_suite_without_promoting_ping_evidence() -> None:\n    assert (\n        ExperimentWorkflowService._science_runner(  # pyright: ignore[reportPrivateUsage]\n            {"protocol": "science_suite_v1"}, _workflow("RQ-SNN-001")\n        )\n        == "run_all"\n    )\n''',
)
if 'test_snn_002_recurrence_is_direct_semantic_match' not in t:
    t += '''\n\ndef test_snn_002_recurrence_is_direct_semantic_match() -> None:\n    from src.research.experiment_summary import _semantic_status\n\n    status, _ = _semantic_status(\n        "RQ-SNN-002", "science_suite_v1", {"recurrence_off", "recurrence_on"}\n    )\n    assert status == "DIRECT_MATCH"\n'''
p.write_text(t, encoding="utf-8")

print("Research execution/viewer fixes applied.")
