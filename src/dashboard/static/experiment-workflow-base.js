"use strict";

import { openFMFile } from "./file-viewer.js";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  if (value == null) return "";
  const div = document.createElement("div");
  div.textContent = String(value);
  return div.innerHTML;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...(options.headers || {}) },
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

const RESEARCH_HELP = Object.freeze({
  seeds: "Seeds initialisieren die deterministischen Zufallsprozesse. Derselbe Seed-Satz über Kontroll- und Treatmentbedingungen ermöglicht gepaarte Vergleiche; mehrere unabhängige Seeds prüfen Robustheit.",
  ticks: "Ticks sind simulierte Zeitschritte. Mehr Ticks bedeuten nicht automatisch stärkere Evidenz; das registrierte Protokoll definiert das notwendige Beobachtungsfenster.",
  preregistration: "Eine eingefrorene Preregistrierung bindet Forschungsfrage, Hypothese, primäre Outcomes, Kontrollen, Seed-Strategie und Auswertungsgrenzen vor einem bestätigenden Lauf.",
  humanReview: "Human Review dokumentiert die menschliche Prüfung von Artefakten und Interpretation. REVIEWED/READY bedeutet nicht automatisch, dass eine Hypothese bestätigt ist.",
  eligibility: "Confirmatory Eligibility erfordert die Einhaltung des eingefrorenen Research Contracts. Unzureichende Seeds oder Vertragsabweichungen stufen den Lauf auf explorativ herunter bzw. blockieren ihn serverseitig.",
  proposal: "Neue Forschungsfragen werden zunächst als PROPOSED im Experimentartefakt gespeichert. Erst nach menschlicher Prüfung dürfen sie in den kanonischen Registry-Zyklus übernommen werden.",
});

function parseSeedExpression(expression) {
  const values = [];
  for (const token of String(expression || "").split(",")) {
    const part = token.trim();
    if (!part) continue;
    const range = part.match(/^(-?\d+)\s*-\s*(-?\d+)$/);
    if (range) {
      const start = Number(range[1]);
      const end = Number(range[2]);
      const step = start <= end ? 1 : -1;
      for (let value = start; value !== end + step; value += step) values.push(value);
    } else if (/^-?\d+$/.test(part)) {
      values.push(Number(part));
    }
  }
  return [...new Set(values)];
}

function seedSuggestion(minimum) {
  const count = Number(minimum || 1);
  if (count <= 1) return "101";
  return `101-${100 + count}`;
}

function resolveRelativeResearchPath(currentPath, href) {
  if (!href || /^(?:https?:|mailto:|data:|#|\/)/i.test(href)) return href;
  const raw = href.replace(/\\_/g, "_").split("#")[0].split("?")[0];
  const base = String(currentPath || "").split("/").slice(0, -1);
  const stack = [];
  for (const part of [...base, ...raw.split("/")]) {
    if (!part || part === ".") continue;
    if (part === "..") {
      if (!stack.length) return null;
      stack.pop();
      continue;
    }
    stack.push(part);
  }
  return stack.join("/");
}

function mermaidForContract(contract) {
  if (!contract) return "";
  const rq = contract.research_question || contract.question || "RQ";
  const hyp = contract.hypothesis || "Hypothesis";
  const protocol = contract.id || "Protocol";
  const lines = [
    "```mermaid",
    "graph TD",
    `    RQ[\"${rq}\"] --> H[\"${hyp}\"]`,
    `    H --> P[\"${protocol}\"]`,
  ];
  (contract.controls || []).forEach((item, idx) => lines.push(`    P --> C${idx}[\"Control: ${String(item).replace(/\"/g, "'")}\"]`));
  (contract.treatments || []).forEach((item, idx) => lines.push(`    P --> T${idx}[\"Treatment: ${String(item).replace(/\"/g, "'")}\"]`));
  lines.push("    P --> M[\"Measured outcomes\"]");
  (contract.primary_outcomes || []).forEach((item, idx) => lines.push(`    M --> O${idx}[\"${String(item).replace(/\"/g, "'")}\"]`));
  lines.push("```");
  return lines.join("\n");
}

export class ExperimentWorkflowPanel {
  constructor({ onCompleted = null } = {}) {
    this.onCompleted = onCompleted;
    this.questions = [];
    this.facets = {};
    this.hypotheses = [];
    this.protocols = [];
    this.nextExperimentId = "";
    this.activePreset = null;
    this.activeContract = null;
    this.lastResult = null;
    this.currentViewerPath = "";
    this.elements = {
      question: byId("workflow-question"),
      hypothesis: byId("workflow-hypothesis"),
      experimentId: byId("workflow-experiment-id"),
      title: byId("workflow-title"),
      conditions: byId("workflow-conditions"),
      conditionProfile: byId("workflow-condition-profile"),
      seeds: byId("workflow-seeds"),
      protocol: byId("workflow-protocol"),
      ticks: byId("workflow-ticks"),
      notes: byId("workflow-notes"),
      run: byId("workflow-run"),
      batchOpen: byId("workflow-batch-open"),
      batchDialog: byId("workflow-batch-dialog"),
      batchForm: byId("workflow-batch-form"),
      batchId: byId("workflow-batch-id"),
      batchTicks: byId("workflow-batch-ticks"),
      batchSeeds: byId("workflow-batch-seeds"),
      batchTitlePrefix: byId("workflow-batch-title-prefix"),
      batchProtocols: byId("workflow-batch-protocols"),
      batchStatus: byId("workflow-batch-status"),
      batchResult: byId("workflow-batch-result"),
      batchStart: byId("workflow-batch-start"),
      status: byId("workflow-status"),
      progressBar: byId("workflow-progress-bar"),
      progressLabel: byId("workflow-progress-label"),
      progressValue: byId("workflow-progress-value"),
      result: byId("workflow-result"),
    };
    this._ensureResearchUX();
    this._bindEvents();
    this._bindBatchWorkflow();
    this._installViewerEnhancements();
  }

  _ensureResearchUX() {
    const form = this.elements.protocol?.closest(".workflow-form-grid") || this.elements.run?.closest("section");
    if (!form) return;

    const labels = [...form.querySelectorAll("label")];
    for (const label of labels) {
      const text = (label.textContent || "").toLowerCase();
      if (text.includes("seed")) label.title = RESEARCH_HELP.seeds;
      if (text.includes("tick")) label.title = RESEARCH_HELP.ticks;
      if (text.includes("protokoll")) label.title = RESEARCH_HELP.preregistration;
    }

    if (!byId("workflow-research-contract")) {
      const contract = document.createElement("section");
      contract.id = "workflow-research-contract";
      contract.className = "research-contract-card";
      contract.innerHTML = `
        <div class="panel-title">
          <div><h3>Research Contract <span title="${escapeHtml(RESEARCH_HELP.preregistration)}">ⓘ</span></h3><p>Vorgaben aus Protocol Registry und eingefrorener Preregistrierung vor dem Start.</p></div>
          <span id="workflow-contract-eligibility" class="gate-badge pending" title="${escapeHtml(RESEARCH_HELP.eligibility)}">NOT EVALUATED</span>
        </div>
        <div id="workflow-contract-content" class="research-contract-content">Protokoll auswählen, um Vorgaben anzuzeigen.</div>`;
      form.insertAdjacentElement("afterend", contract);
    }

    if (!byId("workflow-experiment-library")) {
      const library = document.createElement("section");
      library.id = "workflow-experiment-library";
      library.className = "experiment-library-card";
      this._viewMode = localStorage.getItem("mhrn-exp-library-view") || "grid";
      this._sortMode = localStorage.getItem("mhrn-exp-library-sort") || "date-desc";
      library.innerHTML = `
        <div class="panel-title">
          <div><span class="workspace-kicker">RESEARCH ORGANIZER</span><h3>Experimentreihen &amp; Archiv</h3><p>Reihen laufen über den kontrollierten Batch-Workflow. Abgeschlossene Experimente bleiben unverändert und können aus der aktiven Ansicht ins Archiv verschoben werden.</p></div>
          <div class="experiment-library-actions"><button type="button" id="workflow-series-open" class="btn-primary">Neue Reihe</button><button type="button" id="workflow-library-refresh" class="btn-secondary" title="Experimentliste aktualisieren" aria-label="Experimentliste aktualisieren">↻</button></div>
        </div>
        <div class="experiment-library-summary"><span id="workflow-series-count">0 Reihen</span><span id="workflow-active-count">0 aktiv</span><span id="workflow-archived-count">0 archiviert</span></div>
        <div class="experiment-library-view-toolbar">
          <div class="exp-view-toggle">
            <button type="button" class="exp-view-btn" data-exp-view="grid" title="Grid-Ansicht" aria-label="Grid-Ansicht">▦</button>
            <button type="button" class="exp-view-btn" data-exp-view="list" title="Listen-Ansicht" aria-label="Listen-Ansicht">☰</button>
          </div>
          <label class="exp-sort-label">Sortieren<select id="exp-library-sort" class="exp-sort-select">
            <option value="date-desc">Neueste zuerst</option>
            <option value="date-asc">Älteste zuerst</option>
            <option value="name-asc">A–Z</option>
            <option value="name-desc">Z–A</option>
            <option value="status">Status</option>
          </select></label>
        </div>
        <section class="experiment-series-section"><div class="experiment-library-section-head"><h4>Experimentreihen</h4><small>Jede Reihe ist separat technisch bewertbar.</small></div><div id="workflow-experiment-series" class="experiment-series-list"><p class="experiment-library-empty">Lade Reihen …</p></div></section>
        <div class="experiment-library-grid">
          <section><h4>Aktive Experimente</h4><div id="workflow-active-experiments" class="experiment-library-list"><p class="experiment-library-empty">Lade Experimente …</p></div></section>
          <details id="workflow-archive-section" class="experiment-archive-section"><summary><span>Archiv</span><span id="workflow-archive-summary-count">0 archiviert</span></summary><div id="workflow-archived-experiments" class="experiment-library-list"><p class="experiment-library-empty">Archiv ist leer.</p></div></details>
        </div>`;
      form.insertAdjacentElement("afterend", library);
      byId("workflow-series-open")?.addEventListener("click", () => this._openBatchWorkflow());
      byId("workflow-library-refresh")?.addEventListener("click", () => this._loadExperimentCollections());
      library.addEventListener("click", (event) => this._handleExperimentLibraryAction(event));

      // View mode toggle
      library.querySelectorAll("[data-exp-view]").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.expView === this._viewMode);
        btn.addEventListener("click", () => {
          this._viewMode = btn.dataset.expView;
          localStorage.setItem("mhrn-exp-library-view", this._viewMode);
          library.querySelectorAll("[data-exp-view]").forEach((b) => b.classList.toggle("active", b.dataset.expView === this._viewMode));
          const list = byId("workflow-active-experiments");
          if (list) { list.dataset.expView = this._viewMode; }
          const archivedList = byId("workflow-archived-experiments");
          if (archivedList) { archivedList.dataset.expView = this._viewMode; }
        });
      });

      // Sort
      const sortSelect = byId("exp-library-sort");
      if (sortSelect) {
        sortSelect.value = this._sortMode;
        sortSelect.addEventListener("change", () => {
          this._sortMode = sortSelect.value;
          localStorage.setItem("mhrn-exp-library-sort", this._sortMode);
          this._loadExperimentCollections();
        });
      }

      this._loadExperimentCollections();
    }

    if (!byId("workflow-result-actions")) {
      const actions = document.createElement("section");
      actions.id = "workflow-result-actions";
      actions.className = "workflow-result-actions";
      actions.hidden = true;
      actions.innerHTML = `
        <div class="panel-title"><div><h3>Abgeschlossener Lauf</h3><p>Berichte und Rohdaten direkt unter dem aktuellen Lauf öffnen.</p></div></div>
        <div class="button-group">
          <button type="button" id="workflow-open-report" class="btn-primary">Open Scientific Report</button>
          <button type="button" id="workflow-open-summary" class="btn-secondary">Open Summary</button>
          <button type="button" id="workflow-open-statistics" class="btn-secondary">Open Statistics</button>
          <button type="button" id="workflow-open-raw" class="btn-secondary">Raw Data Index</button>
        </div>`;
      this.elements.result?.parentElement?.appendChild(actions);
      byId("workflow-open-report")?.addEventListener("click", () => this._openArtifact(this.lastResult?.report));
      byId("workflow-open-summary")?.addEventListener("click", () => this._openArtifact(this.lastResult?.summary));
      byId("workflow-open-statistics")?.addEventListener("click", () => this._openArtifact(this.lastResult?.statistics));
      byId("workflow-open-raw")?.addEventListener("click", () => this._openArtifact(this._experimentArtifact("DATA/runs_index.json")));
    }

    if (!byId("workflow-human-review")) {
      const review = document.createElement("section");
      review.id = "workflow-human-review";
      review.className = "human-review-card";
      review.hidden = true;
      review.innerHTML = `
        <div class="panel-title"><div><h3>Human Review <span title="${escapeHtml(RESEARCH_HELP.humanReview)}">ⓘ</span></h3><p>Status: <strong id="workflow-human-review-status">PENDING</strong></p></div></div>
        <div class="workflow-form-grid">
          <label>Reviewer<input id="workflow-reviewer" type="text" placeholder="Name"></label>
          <label>Decision<select id="workflow-review-decision"><option value="ACCEPT_FOR_REVIEWED_RECORD">Accept for reviewed record</option><option value="ACCEPT_AS_EXPLORATORY">Accept as exploratory only</option><option value="REQUEST_FOLLOW_UP">Request follow-up</option><option value="REJECT">Reject</option></select></label>
        </div>
        <div class="human-review-checklist">
          <label><input type="checkbox" data-review-check="experiment_contract"> Experiment Contract geprüft</label>
          <label><input type="checkbox" data-review-check="raw_data"> Rohdaten geprüft</label>
          <label><input type="checkbox" data-review-check="statistics"> Statistik geprüft</label>
          <label><input type="checkbox" data-review-check="ai_analysis"> AI-Interpretation geprüft</label>
          <label><input type="checkbox" data-review-check="limitations"> Limitationen akzeptiert</label>
        </div>
        <label>Kommentar<textarea id="workflow-review-notes" rows="3" placeholder="Review-Kommentar"></textarea></label>
        <button type="button" id="workflow-complete-review" class="btn-success">✓ Complete Human Review</button>`;
      this.elements.result?.parentElement?.appendChild(review);
      byId("workflow-complete-review")?.addEventListener("click", () => this._completeHumanReview());
    }

    if (!byId("workflow-rq-proposal")) {
      const proposal = document.createElement("section");
      proposal.id = "workflow-rq-proposal";
      proposal.className = "rq-proposal-card";
      proposal.hidden = true;
      proposal.innerHTML = `
        <div class="panel-title"><div><h3>Neue Forschungsfrage integrieren <span title="${escapeHtml(RESEARCH_HELP.proposal)}">ⓘ</span></h3><p>Neue Fragen werden zunächst als PROPOSED mit Herkunft aus diesem Experiment gespeichert.</p></div></div>
        <label>Research Question Candidate<textarea id="workflow-rq-proposal-text" rows="3" placeholder="Welche neue Forschungsfrage ergibt sich aus diesem Lauf?"></textarea></label>
        <button type="button" id="workflow-save-rq-proposal" class="btn-secondary">Add as PROPOSED</button>
        <div id="workflow-rq-proposal-status" class="heatmap-meta"></div>`;
      this.elements.result?.parentElement?.appendChild(proposal);
      byId("workflow-save-rq-proposal")?.addEventListener("click", () => this._saveResearchQuestionProposal());
    }
  }

  _bindEvents() {
    this.elements.question?.addEventListener("change", () => {
      this._renderHypotheses();
      this._alignProtocolWithQuestion();
      this._renderContract();
    });
    this.elements.hypothesis?.addEventListener("change", () => this._renderContract());
    this.elements.seeds?.addEventListener("input", () => this._renderContract());
    this.elements.ticks?.addEventListener("input", () => this._renderContract());
    this.elements.protocol?.addEventListener("change", () => {
      this._applyProtocol();
      if (this.elements.protocol.value === "batch_workflow_v1") this._openBatchWorkflow();
    });
    this.elements.conditionProfile?.addEventListener("change", () => this._applyConditionProfile());
    this.elements.run?.addEventListener("click", () => this._run());
  }

  _bindBatchWorkflow() {
    this.elements.batchOpen?.addEventListener("click", () => this._openBatchWorkflow());
    this.elements.batchStart?.addEventListener("click", () => this._runBatchWorkflow());
  }

  _openBatchWorkflow() {
    this._renderBatchProtocols();
    if (typeof this.elements.batchDialog?.showModal === "function") {
      this.elements.batchDialog.showModal();
    } else if (this.elements.batchDialog) {
      this.elements.batchDialog.setAttribute("open", "");
    }
  }

  _renderBatchProtocols() {
    const root = this.elements.batchProtocols;
    if (!root) return;
    const operationalByQuestion = new Map(
      this.protocols
        .filter((protocol) => protocol.preregistration && protocol.research_question)
        .map((protocol) => [protocol.research_question, protocol]),
    );
    if (!this.questions.length) {
      root.innerHTML = "<p>Keine Forschungsfragen aus dem Registry-Katalog verfügbar.</p>";
      return;
    }
    const controls = document.createElement("div");
    controls.className = "workflow-batch-selection-tools";
    controls.innerHTML = '<button type="button" class="btn-small" data-batch-select="all">Alle auswählen</button><button type="button" class="btn-small" data-batch-select="none">Keine auswählen</button>';
    controls.addEventListener("click", (event) => {
      const action = event.target.closest("[data-batch-select]")?.dataset.batchSelect;
      if (!action) return;
      root.querySelectorAll("input[type=checkbox]:not(:disabled)").forEach((input) => { input.checked = action === "all"; });
    });
    root.replaceChildren(controls, ...this.questions.map((question) => {
      const protocol = operationalByQuestion.get(question.id);
      const label = document.createElement("label");
      label.className = "workflow-batch-protocol";
      if (protocol) {
        const auditTemplate = protocol.execution_kind === "conceptual_audit";
        label.dataset.executionKind = protocol.execution_kind || "native_experiment";
        label.innerHTML = `<input type="checkbox" value="${escapeHtml(protocol.id)}" ${auditTemplate ? "" : "checked"}><span><strong>${escapeHtml(question.id)} · ${escapeHtml(question.label || "")}</strong><small>${auditTemplate ? "PRUEFVORLAGE / menschliche Bewertung offen: " : ""}${escapeHtml(protocol.label || protocol.id)} · registrierte Vorgaben</small><em><span>Seeds</span><input type="text" data-batch-seeds value="${escapeHtml(protocol.default_seed_expression || "42-44")}"><span>Ticks</span><input type="number" data-batch-ticks min="1" value="${escapeHtml(protocol.default_ticks || 1000)}"></em></span>`;
      } else {
        const hypothesis = this.hypotheses.find((item) => item.question_id === question.id);
        const hypothesisId = hypothesis?.id || "EXPLORATORY-UNSPECIFIED";
        const selection = `exploratory:${question.id}:${hypothesisId}`;
        label.classList.add("workflow-batch-protocol-exploratory");
        const selectable = question.workflow_selectable !== false;
        if (!selectable) label.classList.add("workflow-batch-protocol-blocked");
        const executionLabel = selectable
          ? `EXPLORATORY · Runtime-Ticks${hypothesis ? ` · ${escapeHtml(hypothesis.id)}` : " · ohne registrierte Hypothese"} · automatische Diagnosevorgaben`
          : `BLOCKED · ${escapeHtml(question.execution_status || "native adapter/review required")} · kein Generic-Ticks-Fallback`;
        label.innerHTML = `<input type="checkbox" value="${escapeHtml(selection)}" ${selectable ? "checked" : "disabled"}><span><strong>${escapeHtml(question.id)} · ${escapeHtml(question.label || "")}</strong><small>${executionLabel}</small><em><span>Seeds</span><input type="text" data-batch-seeds value="42-44" readonly><span>Ticks</span><input type="number" data-batch-ticks min="1" value="1000" readonly></em></span>`;
      }
      return label;
    }));
  }

  async _runBatchWorkflow() {
    const selected = [...(this.elements.batchProtocols?.querySelectorAll("input:checked") || [])]
      .map((input) => input.value)
      .filter(Boolean);
    if (!selected.length) {
      if (this.elements.batchStatus) this.elements.batchStatus.textContent = "Mindestens ein Protokoll auswählen.";
      return;
    }
    const payload = {
      batch_id: this.elements.batchId?.value.trim() || undefined,
      ticks: Number(this.elements.batchTicks?.value || 1000),
      seeds: this.elements.batchSeeds?.value.trim() || "42-44",
      title_prefix: this.elements.batchTitlePrefix?.value.trim() || "Experiment workflow",
      protocols: selected,
      protocol_options: Object.fromEntries(selected.map((protocol) => {
        const input = [...(this.elements.batchProtocols?.querySelectorAll("input[type=checkbox]:checked") || [])]
          .find((candidate) => candidate.value === protocol);
        const row = input?.closest(".workflow-batch-protocol");
        return [protocol, {
          seeds: row?.querySelector("[data-batch-seeds]")?.value.trim() || this.elements.batchSeeds?.value.trim() || "42-44",
          ticks: Number(row?.querySelector("[data-batch-ticks]")?.value || this.elements.batchTicks?.value || 1000),
        }];
      })),
    };
    if (this.elements.batchStart) this.elements.batchStart.disabled = true;
    if (this.elements.batchStart) this.elements.batchStart.textContent = "Läuft …";
    if (this.elements.batchStatus) this.elements.batchStatus.textContent = "Workflow läuft …";
    document.dispatchEvent(new CustomEvent("brain5d:experiment-progress", {
      detail: { active: true, progress: 0, label: "Experiment-Workflow läuft", experimentId: payload.batch_id || "Batch" },
    }));
    try {
      const result = await fetchJson("/api/experiment/workflow/batch", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (this.elements.batchStatus) {
        this.elements.batchStatus.textContent = `Abgeschlossen: ${result.completed} erfolgreich, ${result.failed} fehlgeschlagen.`;
      }
      const resultText = [
          `Workflow: ${result.workflow_id}`,
          `Bericht: ${result.report}`,
          `Markdown: ${result.report_markdown}`,
          `Erfolgreich: ${result.completed}`,
          `Fehlgeschlagen: ${result.failed}`,
          ...(result.results || []).map((item) => `${item.protocol}: ${item.status}${item.error ? ` — ${item.error}` : ""}`),
        ].join("\n");
      if (this.elements.batchResult) this.elements.batchResult.textContent = resultText;
      if (this.elements.result) this.elements.result.textContent = resultText;
      this._setStatus("Workflow-Bericht erstellt", "completed");
      await this._loadExperimentCollections();
      document.dispatchEvent(new CustomEvent("brain5d:experiment-progress", {
        detail: { active: false, preserveFooter: true, progress: 100, label: "Experiment-Workflow abgeschlossen", experimentId: result.workflow_id },
      }));
      if (typeof this.onCompleted === "function") await this.onCompleted();
      const dialog = this.elements.batchDialog;
      if (dialog) {
        try { if (dialog.open) dialog.close("completed"); } catch (_) { /* keep result visible */ }
        dialog.removeAttribute("open");
      }
    } catch (error) {
      if (this.elements.batchStatus) this.elements.batchStatus.textContent = `Workflow fehlgeschlagen: ${error.message}`;
      if (this.elements.batchResult) this.elements.batchResult.textContent = `Fehler: ${error.message}`;
      document.dispatchEvent(new CustomEvent("brain5d:experiment-progress", {
        detail: { active: false, preserveFooter: true, progress: 0, label: "Experiment-Workflow fehlgeschlagen", experimentId: payload.batch_id || "Batch" },
      }));
    } finally {
      if (this.elements.batchStart) {
        this.elements.batchStart.disabled = false;
        this.elements.batchStart.textContent = "Auswahl starten";
      }
    }
  }

  async refresh() {
    try {
      const catalog = await fetchJson("/api/experiment/workflow/catalog");
      this.questions = catalog.questions || [];
      this.facets = catalog.facets || {};
      this.hypotheses = catalog.hypotheses || [];
      this.protocols = catalog.protocols || [];
      this.nextExperimentId = catalog.next_experiment_id || "";
      if (this.elements.experimentId && !this.elements.experimentId.value) {
        this.elements.experimentId.placeholder = this.nextExperimentId || "automatisch";
      }
      this._renderProtocolOptions();
      this._renderQuestions();
      this._applyProtocol();
      this._setStatus("Bereit", "ready");
      this._setProgress(0, "Bereit", false);
    } catch (error) {
      this._setStatus(`Nicht verfuegbar: ${error.message}`, "error");
    }
  }

  async _loadExperimentCollections() {
    const active = byId("workflow-active-experiments");
    const archived = byId("workflow-archived-experiments");
    if (!active || !archived) return;
    try {
      const [activePayload, archivedPayload, seriesPayload] = await Promise.all([
        fetchJson("/api/research/experiments"),
        fetchJson("/api/research/experiments/archive"),
        fetchJson("/api/research/experiment-series"),
      ]);
      const activeItems = Array.isArray(activePayload.experiments) ? activePayload.experiments : [];
      const archivedItems = Array.isArray(archivedPayload.experiments) ? archivedPayload.experiments : [];
      const seriesItems = Array.isArray(seriesPayload.series) ? seriesPayload.series : [];
      const seriesCount = byId("workflow-series-count");
      const activeCount = byId("workflow-active-count");
      const archivedCount = byId("workflow-archived-count");
      if (seriesCount) seriesCount.textContent = `${seriesItems.length} Reihen`;
      if (activeCount) activeCount.textContent = `${activeItems.length} aktiv`;
      if (archivedCount) archivedCount.textContent = `${archivedItems.length} archiviert`;
      const archiveSummaryCount = byId("workflow-archive-summary-count");
      if (archiveSummaryCount) archiveSummaryCount.textContent = `${archivedItems.length} archiviert`;
      const series = byId("workflow-experiment-series");
      if (series) series.innerHTML = seriesItems.length ? seriesItems.map((item) => this._experimentSeriesItem(item)).join("") : '<p class="experiment-library-empty">Noch keine Experimentreihe.</p>';

      // Apply sort
      const sortMode = this._sortMode || "date-desc";
      const sortFn = this._sortExperimentItems(sortMode);
      activeItems.sort(sortFn);
      archivedItems.sort(sortFn);

      active.innerHTML = activeItems.length ? activeItems.map((item) => this._experimentLibraryItem(item, false)).join("") : '<p class="experiment-library-empty">Keine aktiven Experimente.</p>';
      archived.innerHTML = archivedItems.length ? archivedItems.map((item) => this._experimentLibraryItem(item, true)).join("") : '<p class="experiment-library-empty">Archiv ist leer.</p>';

      // Apply view mode
      active.dataset.expView = this._viewMode || "grid";
      archived.dataset.expView = this._viewMode || "grid";
    } catch (error) {
      active.innerHTML = `<p class="experiment-library-empty">Experimentliste nicht verfügbar: ${escapeHtml(error.message || error)}</p>`;
      archived.innerHTML = `<p class="experiment-library-empty">Archiv nicht verfügbar: ${escapeHtml(error.message || error)}</p>`;
    }
  }

  _sortExperimentItems(mode) {
    return (a, b) => {
      const aId = a.experiment_id || a.id || "";
      const bId = b.experiment_id || b.id || "";
      const aDate = a.created_at || (a.manifest && a.manifest.created_at) || a.timestamp || "";
      const bDate = b.created_at || (b.manifest && b.manifest.created_at) || b.timestamp || "";
      const aStatus = String(a.manifest?.experiment_status || a.status || "");
      const bStatus = String(b.manifest?.experiment_status || b.status || "");
      switch (mode) {
        case "date-asc": return aDate < bDate ? -1 : aDate > bDate ? 1 : 0;
        case "name-asc": return aId.localeCompare(bId);
        case "name-desc": return bId.localeCompare(aId);
        case "status": return aStatus.localeCompare(bStatus) || (aDate < bDate ? 1 : -1);
        default: return aDate > bDate ? -1 : aDate < bDate ? 1 : 0; // date-desc
      }
    };
  }

  _experimentLibraryItem(item, archived) {
    const manifest = item.manifest && typeof item.manifest === "object" ? item.manifest : {};
    const status = String(manifest.experiment_status || item.status || (archived ? "archived" : "unknown"));
    const question = Array.isArray(manifest.research_questions) ? manifest.research_questions.join(", ") : "Research experiment";
    const created = item.created_at || manifest.created_at || manifest.timestamp || "";
    const meta = [question, created].filter(Boolean).join(" · ");
    const statusClass = status === "completed" ? "exp-status-ok" : status === "running" || status === "active" ? "exp-status-active" : "exp-status-pending";
    const action = archived
      ? `<button type="button" class="btn-small" data-experiment-action="restore" data-experiment-id="${escapeHtml(item.experiment_id)}">↶ Wiederherstellen</button>`
      : `<button type="button" class="btn-small" data-experiment-action="archive" data-experiment-id="${escapeHtml(item.id)}">▣ Archivieren</button>`;
    return `<article class="experiment-library-item ${archived ? "is-archived" : ""}">
      <div class="exp-item-header"><strong>${escapeHtml(item.experiment_id || item.id)}</strong><span class="exp-status-badge ${statusClass}">${escapeHtml(status)}</span></div>
      <small class="exp-item-meta">${escapeHtml(meta)}</small>
      <div class="experiment-library-item-actions">${action}</div>
    </article>`;
  }

  _experimentSeriesItem(item) {
    const results = Array.isArray(item.results) ? item.results : [];
    const resultRows = results.length
      ? results.map((result) => `<li><strong>${escapeHtml(result.protocol || result.experiment_id || "Experiment")}</strong><span>${escapeHtml(result.status || "unknown")}</span></li>`).join("")
      : "<li>Keine Teilresultate</li>";
    const reportButton = item.report
      ? `<button type="button" class="btn-small" data-series-report="${escapeHtml(item.report)}">Reihenbericht</button>`
      : "";
    return `<details class="experiment-series-item"><summary><span><strong>${escapeHtml(item.series_id)}</strong><small>${escapeHtml(item.created_at || "")}</small></span><em class="series-status-${escapeHtml(item.status)}">${escapeHtml(item.status)} · ${escapeHtml(item.assessment_status)}</em></summary><div class="experiment-series-assessment"><div class="experiment-series-kpis"><span><small>Erfolgreich</small><strong>${Number(item.completed || 0)}</strong></span><span><small>Fehlgeschlagen</small><strong>${Number(item.failed || 0)}</strong></span><span><small>Ticks</small><strong>${escapeHtml(item.requested_ticks ?? "—")}</strong></span><span><small>Seeds</small><strong>${escapeHtml(item.seeds ?? "—")}</strong></span></div><p>${escapeHtml(item.assessment_boundary || "Technische Bewertung; Human Review erforderlich.")}</p><ul class="experiment-series-results">${resultRows}</ul>${reportButton}</div></details>`;
  }

  async _handleExperimentLibraryAction(event) {
    const button = event.target.closest?.("[data-experiment-action], [data-series-report]");
    if (!button) return;
    const experimentId = button.dataset.experimentId;
    const action = button.dataset.experimentAction;
    const seriesReport = button.dataset.seriesReport;
    if (seriesReport) {
      await this._openArtifact(seriesReport);
      return;
    }
    if (!experimentId || !action) return;
    const reason = action === "archive" ? (window.prompt("Warum wird dieses Experiment archiviert?", "manuelle Archivierung") || "manuelle Archivierung") : "";
    if (action === "archive" && !window.confirm(`${experimentId} archivieren? Die Artefakte bleiben unverändert.`)) return;
    button.disabled = true;
    try {
      await fetchJson("/api/research/experiments/archive", {
        method: "POST",
        body: JSON.stringify({ experiment_id: experimentId, action, reason }),
      });
      await this._loadExperimentCollections();
    } catch (error) {
      window.alert(`Aktion fehlgeschlagen: ${error.message || error}`);
      button.disabled = false;
    }
  }

  _renderProtocolOptions() {
    const select = this.elements.protocol;
    if (!select) return;
    const current = select.value;
    const labels = new Map(this.protocols.map((item) => [item.id, item.label]));
    for (const item of this.protocols) {
      if (![...select.options].some((option) => option.value === item.id)) {
        select.add(new Option(item.label || item.id, item.id));
      } else if (labels.get(item.id)) {
        const option = [...select.options].find((candidate) => candidate.value === item.id);
        if (option) option.textContent = labels.get(item.id);
      }
    }
    if ([...select.options].some((option) => option.value === current)) select.value = current;
  }

  _renderQuestions() {
    const select = this.elements.question;
    if (!select) return;
    const current = select.value;
    select.replaceChildren(new Option("Forschungsfrage waehlen", ""));
    for (const question of this.questions) {
      select.add(new Option(`${question.id} - ${question.label}`, question.id));
    }
    if ([...select.options].some((option) => option.value === current)) select.value = current;
    this._renderHypotheses();
  }

  _renderHypotheses() {
    const select = this.elements.hypothesis;
    if (!select) return;
    const current = select.value;
    const questionId = this.elements.question?.value;
    select.replaceChildren(new Option("Hypothese waehlen", ""));
    for (const hypothesis of this.hypotheses) {
      if (hypothesis.question_id === questionId) {
        select.add(new Option(`${hypothesis.id} - ${hypothesis.label}`, hypothesis.id));
      }
    }
    if ([...select.options].some((option) => option.value === current)) select.value = current;
  }

  _protocolContract(protocolId = this.elements.protocol?.value) {
    return this.protocols.find((item) => item.id === protocolId && item.preregistration) || null;
  }

  _renderContract() {
    const content = byId("workflow-contract-content");
    const badge = byId("workflow-contract-eligibility");
    if (!content || !badge) return;
    const contract = this._protocolContract();
    this.activeContract = contract;
    if (!contract) {
      const legacy = this.activePreset;
      content.innerHTML = legacy ? `<p><strong>Legacy / diagnostic protocol.</strong> ${escapeHtml(legacy.conditions || "")}</p><p>Dieser Lauf besitzt keinen operationalen eingefrorenen Research Contract und ist deshalb nicht automatisch als bestätigende Evidenz zu interpretieren.</p>` : "Kein registrierter Research Contract verfügbar.";
      badge.textContent = "EXPLORATORY / DIAGNOSTIC";
      badge.className = "gate-badge warning";
      return;
    }

    const seeds = parseSeedExpression(this.elements.seeds?.value);
    const minimum = Number(contract.minimum_independent_seeds || 1);
    const ticks = Number(this.elements.ticks?.value || contract.default_ticks || 0);
    const seedOk = seeds.length >= minimum;
    const tickChanged = contract.default_ticks != null && ticks !== Number(contract.default_ticks);
    const eligible = seedOk && !tickChanged;
    badge.textContent = eligible ? "CONFIRMATORY ELIGIBLE" : "EXPLORATORY ONLY";
    badge.className = `gate-badge ${eligible ? "pass" : "warning"}`;

    const conditions = (contract.conditions || []).map((item) => `<li>${escapeHtml(item.id || item)}${item.role ? ` — <strong>${escapeHtml(item.role)}</strong>` : ""}</li>`).join("");
    const list = (items) => (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>—</li>";
    content.innerHTML = `
      <div class="research-contract-grid">
        <div><span>Forschungsfrage</span><strong>${escapeHtml(contract.research_question)}</strong></div>
        <div><span>Hypothese</span><strong>${escapeHtml(contract.hypothesis)}</strong></div>
        <div><span>Modus</span><strong>${escapeHtml(contract.mode || "—")}</strong></div>
        <div><span>Preregistration</span><strong>${escapeHtml(contract.preregistration)}</strong></div>
        <div><span>Seeds</span><strong>${seeds.length} / min. ${minimum} ${seedOk ? "✓" : "⚠"}</strong><small>${escapeHtml(contract.seed_rule || "")}</small></div>
        <div><span>Ticks</span><strong>${ticks}${contract.default_ticks != null ? ` / default ${contract.default_ticks}` : ""} ${tickChanged ? "⚠" : "✓"}</strong></div>
      </div>
      <details open><summary>Conditions / Roles</summary><ul>${conditions || "<li>—</li>"}</ul></details>
      <details><summary>Controls</summary><ul>${list(contract.controls)}</ul></details>
      <details><summary>Treatments</summary><ul>${list(contract.treatments)}</ul></details>
      <details open><summary>Primary Outcomes</summary><ul>${list(contract.primary_outcomes)}</ul></details>
      <details><summary>Secondary Outcomes</summary><ul>${list(contract.secondary_outcomes)}</ul></details>
      <details><summary>Inclusion Criteria</summary><ul>${list(contract.inclusion_criteria)}</ul></details>
      <details><summary>Exclusion Criteria</summary><ul>${list(contract.exclusion_criteria)}</ul></details>
      <p class="research-inference-policy"><strong>Wissenschaftliche Aussagegrenze:</strong> ${escapeHtml(contract.inference_policy || "Keine zusätzliche Inferenzregel angegeben.")}</p>
      ${!seedOk ? `<p class="workflow-warning">⚠ Seedzahl zu niedrig: ${seeds.length} statt mindestens ${minimum}.</p>` : ""}
      ${tickChanged ? `<p class="workflow-warning">⚠ Tickzahl weicht vom registrierten Default ab. Der Lauf ist damit nicht unverändert confirmatory.</p>` : ""}`;
  }

  async _run() {
    const payload = {
      question_id: this.elements.question?.value || "",
      hypothesis_id: this.elements.hypothesis?.value || "",
      experiment_id: this.elements.experimentId?.value.trim() || this.nextExperimentId,
      title: this.elements.title?.value.trim() || "",
      conditions: this.elements.conditions?.value.trim() || "",
      seeds: this.elements.seeds?.value.trim() || "",
      ticks: Number(this.elements.ticks?.value),
      notes: this.elements.notes?.value.trim() || "",
      protocol: this.elements.protocol?.value || "runtime_ticks_v1",
    };
    this._renderContract();
    this.elements.run.disabled = true;
    this._setStatus("Ausfuehrung laeuft", "running");
    this._setProgress(8, "Testlauf laeuft", true, payload.experiment_id);
    this.elements.result.textContent = "";
    try {
      const result = await fetchJson("/api/experiment/workflow/run", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      this.lastResult = result;
      this._setStatus("Bericht eingetragen", "completed");
      const lines = [
        `Experiment: ${result.experiment_id}`,
        `Manifest: research/${result.manifest}`,
        `Bericht: research/${result.report}`,
      ];
      if (result.evidence_id) lines.push(`Evidenz: ${result.evidence_id}`);
      if (result.data_id) lines.push(`Daten: ${result.data_id}`);
      if (result.workflow) lines.push(`Workflow: research/${result.workflow}`);
      if (result.summary) lines.push(`Zusammenfassung: research/${result.summary}`);
      if (result.statistics) lines.push(`Statistik: research/${result.statistics}`);
      const runResult = result.result;
      if (runResult && typeof runResult === "object") {
        if (runResult.runner) lines.push(`Runner: ${runResult.runner}`);
        if (typeof runResult.ticks_requested === "number") lines.push(`Ticks angefordert: ${runResult.ticks_requested}`);
        if (Array.isArray(runResult.seeds_executed)) lines.push(`Seeds ausgeführt: ${runResult.seeds_executed.join(", ")}`);
        if (runResult.tick_validation?.status) lines.push(`Tick-Vertrag: ${runResult.tick_validation.status}`);
        if (runResult.start && runResult.end) lines.push(`Tick: ${runResult.start.tick} -> ${runResult.end.tick}`);
        else if (typeof runResult.run_count === "number") {
          const duration = typeof runResult.duration_seconds === "number" ? `; Dauer: ${runResult.duration_seconds.toFixed(3)} s` : "";
          lines.push(`Runs: ${runResult.run_count}${duration}`);
        }
      }
      if (result.ai_report) {
        lines.push(`KI-Bericht: ${result.ai_report.status}`);
        if (result.ai_report.json) lines.push(`KI JSON: research/${result.ai_report.json}`);
        if (result.ai_report.markdown) lines.push(`KI Markdown: research/${result.ai_report.markdown}`);
        if (result.ai_report.reason) lines.push(`KI Hinweis: ${result.ai_report.reason}`);
        if (result.ai_report.message) lines.push(`KI Fehler: ${result.ai_report.message}`);
      }
      this.elements.result.textContent = lines.join("\n");
      this._setProgress(100, "Testlauf abgeschlossen", false, result.experiment_id || payload.experiment_id);
      byId("workflow-result-actions").hidden = false;
      byId("workflow-human-review").hidden = false;
      byId("workflow-rq-proposal").hidden = false;
      byId("workflow-human-review-status").textContent = "PENDING";
      await this._appendSchemaToReport();
      if (this.onCompleted) await this.onCompleted();
    } catch (error) {
      this._setStatus(`Ausfuehrung abgebrochen: ${error.message}`, "error");
      this._setProgress(0, "Testlauf fehlgeschlagen", false, payload.experiment_id);
    } finally {
      this.elements.run.disabled = false;
    }
  }

  _experimentArtifact(relativePath) {
    const id = this.lastResult?.experiment_id;
    return id ? `experiments/${id}/${relativePath}` : null;
  }

  async _readResearchFile(path) {
    if (!path) throw new Error("Artefaktpfad fehlt.");
    const response = await fetch(`/api/files/content/${encodeURIComponent(path)}?source=research`, { headers: { "Cache-Control": "no-store" } });
    if (!response.ok) throw new Error(`File not found: ${path}`);
    const type = response.headers.get("content-type") || "";
    if (!type.includes("application/json")) return { is_binary: true, path };
    return response.json();
  }

  async _saveResearchFile(path, content, backup = true) {
    const response = await fetch(`/api/files/save/${encodeURIComponent(path)}?source=research`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, backup }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
  }

  async _appendSchemaToReport() {
    const path = this.lastResult?.report;
    const contract = this.activeContract;
    if (!path || !contract) return;
    try {
      const file = await this._readResearchFile(path);
      if (file.is_binary || typeof file.content !== "string") return;
      if (file.content.includes("## Experimental schema") || file.content.includes("## Experimentelles Schema")) return;
      const block = `\n\n## Experimental schema\n\nThe following diagram is deterministically derived from the registered Research Contract. It is documentation of the design, not AI-generated evidence.\n\n${mermaidForContract(contract)}\n`;
      await this._saveResearchFile(path, file.content.replace(/\s*$/, "") + block + "\n", true);
    } catch (error) {
      console.warn("Could not append experiment schema:", error);
    }
  }

  async _openArtifact(path) {
    if (!path) return;
    const researchButton = document.querySelector('.fm-source-btn[data-source="research"]');
    if (researchButton && !researchButton.classList.contains("active")) researchButton.click();
    this.currentViewerPath = path;
    await openFMFile(path);
    this._installExperimentPopupActions(path);
  }

  _installExperimentPopupActions(path) {
    const viewer = byId("fm-viewer");
    const header = viewer?.querySelector(".fm-file-header-actions");
    if (!viewer || !header || header.querySelector("[data-experiment-popup-actions]")) return;
    const group = document.createElement("span");
    group.dataset.experimentPopupActions = "true";
    group.className = "workflow-popup-actions";
    group.innerHTML = `
      <button type="button" class="fm-file-action-btn" data-popup-artifact="report">Report</button>
      <button type="button" class="fm-file-action-btn" data-popup-artifact="summary">Summary</button>
      <button type="button" class="fm-file-action-btn" data-popup-artifact="statistics">Statistics</button>
      <button type="button" class="fm-file-action-btn" data-popup-artifact="raw">Raw Index</button>`;
    header.prepend(group);
    group.querySelectorAll("[data-popup-artifact]").forEach(button => {
      button.addEventListener("click", () => {
        const kind = button.dataset.popupArtifact;
        const target = kind === "raw" ? this._experimentArtifact("DATA/runs_index.json") : this.lastResult?.[kind];
        if (target && target !== path) this._openArtifact(target);
      });
    });
  }

  async _completeHumanReview() {
    if (!this.lastResult?.workflow) return;
    const reviewer = (byId("workflow-reviewer")?.value || "").trim();
    if (!reviewer) {
      this._setStatus("Human Review: Reviewer fehlt", "error");
      return;
    }
    const decision = byId("workflow-review-decision")?.value || "ACCEPT_FOR_REVIEWED_RECORD";
    const notes = (byId("workflow-review-notes")?.value || "").trim();
    const checklist = {};
    document.querySelectorAll("[data-review-check]").forEach((input) => { checklist[input.dataset.reviewCheck] = Boolean(input.checked); });
    try {
      const file = await this._readResearchFile(this.lastResult.workflow);
      const payload = JSON.parse(file.content || "{}");
      payload.human_review = {
        status: "READY",
        reviewer,
        decision,
        reviewed_at: new Date().toISOString(),
        notes,
        checklist,
        semantics: "Human review completed; this status does not automatically confirm the hypothesis or promote evidence.",
      };
      await this._saveResearchFile(this.lastResult.workflow, JSON.stringify(payload, null, 2) + "\n", true);
      byId("workflow-human-review-status").textContent = "READY";
      this._setStatus("Human Review: READY", "completed");
    } catch (error) {
      this._setStatus(`Human Review fehlgeschlagen: ${error.message}`, "error");
    }
  }

  async _saveResearchQuestionProposal() {
    if (!this.lastResult?.workflow) return;
    const text = (byId("workflow-rq-proposal-text")?.value || "").trim();
    if (!text) return;
    try {
      const file = await this._readResearchFile(this.lastResult.workflow);
      const payload = JSON.parse(file.content || "{}");
      const proposals = Array.isArray(payload.proposed_research_questions) ? payload.proposed_research_questions : [];
      proposals.push({
        status: "PROPOSED",
        question: text,
        origin: {
          type: "experiment_observation",
          experiment_id: this.lastResult.experiment_id,
          report: this.lastResult.report || null,
        },
        proposed_at: new Date().toISOString(),
        promotion_rule: "Requires human review before canonical registry inclusion and preregistration.",
      });
      payload.proposed_research_questions = proposals;
      await this._saveResearchFile(this.lastResult.workflow, JSON.stringify(payload, null, 2) + "\n", true);
      byId("workflow-rq-proposal-status").textContent = "✓ Als PROPOSED im Workflow-Artefakt gespeichert.";
      byId("workflow-rq-proposal-text").value = "";
    } catch (error) {
      byId("workflow-rq-proposal-status").textContent = `⚠ ${error.message}`;
    }
  }

  _alignProtocolWithQuestion() {
    const questionId = this.elements.question?.value || "";
    if (!questionId || !this.elements.protocol) return;
    const operational = this.protocols.find(item => item.research_question === questionId && item.preregistration);
    if (operational) {
      // A newly selected RQ/protocol must load its frozen defaults. Stale values
      // from the previously selected experiment must not silently survive. Users
      // can still edit seeds/ticks explicitly after this contract has been loaded.
      this.elements.protocol.value = operational.id;
      this._applyProtocol();
      this._renderContract();
      return;
    }
    if (questionId === "RQ-SNN-001" && this.elements.protocol.value === "science_suite_v1") {
      // Long-term stability has no dedicated primary protocol yet. Use the complete
      // suite as an executable diagnostic rather than aborting, while preserving
      // the selected RQ/H and retaining MISMATCH evidence semantics server-side.
      this.elements.protocol.value = "science_all_v1";
      this.activePreset = {
        title: "Long-term stability diagnostic suite",
        conditions: "Diagnostic bundle: PING/Recurrence, Temporal, STDP/Learning, TIME, 5D and Regulation. Not primary long-term stability evidence.",
        ticks: "1000",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; complete diagnostic suite; RQ-SNN-001 remains evidence-blocked until a sustained-activity protocol exists.",
        },
      };
      if (this.elements.title) this.elements.title.value = this.activePreset.title;
      if (this.elements.ticks) this.elements.ticks.value = this.activePreset.ticks;
      if (this.elements.seeds) this.elements.seeds.value = this.activePreset.seeds;
      if (this.elements.conditionProfile) this.elements.conditionProfile.value = "standard";
      this._applyConditionProfile(this.activePreset);
      this._renderContract();
    }
  }

  _applyProtocol() {
    const protocol = this.elements.protocol?.value;
    const operational = this._protocolContract(protocol);
    if (operational) {
      this.activePreset = {
        question: operational.research_question,
        hypothesis: operational.hypothesis,
        title: operational.label || operational.id,
        conditions: (operational.conditions || []).map((item) => `${item.id || item}${item.role ? ` (${item.role})` : ""}`).join("; "),
        ticks: String(operational.default_ticks ?? this.elements.ticks?.value ?? "100"),
        seeds: seedSuggestion(operational.minimum_independent_seeds),
        profiles: { standard: (operational.conditions || []).map((item) => `${item.id || item}${item.role ? ` (${item.role})` : ""}`).join("; ") },
      };
      this._applyPreset(this.activePreset, false);
      this._renderContract();
      return;
    }

    const presets = {
      science_all_v1: {
        question: "RQ-SUITE-001",
        hypothesis: "H-SUITE-001-A",
        title: "Complete science suite diagnostic",
        conditions: "Diagnostic bundle: PING/Recurrence, Temporal, STDP/Learning, TIME, 5D and Regulation with shared provenance. This suite is not a substitute for each confirmatory preregistration.",
        ticks: "1000",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; all registered science-suite runners; grouped conditions and common provenance.",
          pilot: "Seed 42; all science-suite runners as a low-cost diagnostic pilot.",
        },
      },
      science_suite_v1: {
        question: "RQ-SNN-002",
        hypothesis: "H-SNN-002-A",
        title: "Network impulse response",
        conditions: "Seeds 42,43,44; identical initial state per seed; impulse current 100.0; recurrence as controlled treatment.",
        ticks: "8",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; identical initial state per seed; impulse current 100.0; recurrence as controlled treatment.",
          replication: "Seeds 42,43,44; two identical replicates per treatment; compare response signature and state digest.",
          sensitivity: "Seeds 42,43,44; vary recurrence treatment only; keep all other parameters fixed.",
        },
      },
      science_time_v1: {
        question: "RQ-TIME-001",
        hypothesis: "H-TIME-001-A",
        title: "Learning timescale calibration",
        conditions: "Seeds 42,43,44; tick ladder up to 1,000,000; measure runtime per stage.",
        ticks: "1000000",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; tick ladder up to 1,000,000; measure runtime per stage.",
          short: "Seeds 42,43,44; tick ladder up to 10,000; fast calibration before long run.",
        },
      },
      science_5d_v1: {
        question: "RQ-5D-001",
        hypothesis: "H-5D-001-A",
        title: "Dimensional ablation",
        conditions: "Seeds 0-29; 1D, 2D, 3D, 5D and random graph; dimension/topology only varies.",
        ticks: "8",
        seeds: "0-29",
        profiles: {
          standard: "Seeds 0-29; 1D, 2D, 3D, 5D and random graph; dimension/topology only varies.",
          pilot: "Seeds 0-2; all dimensions/topologies as low-cost pilot.",
        },
      },
      stdp_pair_timing_v1: {
        question: "RQ-STDP-001",
        hypothesis: "H-STDP-001-A",
        title: "Pair-Timing STDP",
        conditions: "Registered protocol: isolated STDPSynapse; initial weight 0.5; delta-t -50 to +50 ms; 10 replicates per delta-t.",
        ticks: "11",
        seeds: "42",
        profiles: { standard: "Registered protocol; inputs defined by protocol.json." },
      },
      runtime_ticks_v1: {
        question: "",
        hypothesis: "",
        title: "Controlled runtime run",
        conditions: "Explicitly document seed, configuration, replicates and stopping criteria.",
        ticks: "100",
        seeds: "42",
        profiles: { standard: "Explicitly document seed, configuration, replicates and stopping criteria." },
      },
    };
    const preset = presets[protocol];
    if (!preset) return;
    this.activePreset = preset;
    this._applyPreset(preset, protocol === "stdp_pair_timing_v1");
    this._renderContract();
  }

  _applyPreset(preset, fixedProtocol) {
    const question = this.elements.question;
    const hypothesis = this.elements.hypothesis;
    if (question && preset.question) question.value = preset.question;
    this._renderHypotheses();
    if (hypothesis && preset.hypothesis) hypothesis.value = preset.hypothesis;
    if (this.elements.title) this.elements.title.value = preset.title;
    if (this.elements.ticks && preset.ticks) this.elements.ticks.value = preset.ticks;
    if (this.elements.seeds && preset.seeds) this.elements.seeds.value = preset.seeds;
    if (this.elements.conditionProfile) this.elements.conditionProfile.value = "standard";
    this._applyConditionProfile(preset);
    [this.elements.question, this.elements.hypothesis, this.elements.title, this.elements.conditions, this.elements.seeds, this.elements.ticks, this.elements.conditionProfile].forEach((element) => {
      if (element) element.disabled = Boolean(fixedProtocol);
    });
  }

  _applyConditionProfile(preset = this.activePreset) {
    const profiles = preset?.profiles || { standard: this.elements.conditions?.value || "" };
    const profile = this.elements.conditionProfile?.value || "standard";
    const condition = profiles[profile] || profiles.standard || "";
    if (this.elements.conditions && condition) this.elements.conditions.value = condition;
  }

  _setStatus(message, state) {
    if (!this.elements.status) return;
    this.elements.status.textContent = message;
    this.elements.status.dataset.state = state;
  }

  _setProgress(percent, label, active, experimentId = "") {
    const value = Math.max(0, Math.min(100, percent));
    if (this.elements.progressBar) {
      this.elements.progressBar.style.width = `${value}%`;
      this.elements.progressBar.parentElement?.classList.toggle("is-running", active);
      this.elements.progressBar.parentElement?.setAttribute("aria-valuenow", String(value));
    }
    if (this.elements.progressLabel) this.elements.progressLabel.textContent = label;
    if (this.elements.progressValue) this.elements.progressValue.textContent = active ? "laufend" : `${value}%`;
    document.dispatchEvent(new CustomEvent("brain5d:experiment-progress", {
      detail: { active, progress: value, label, experimentId },
    }));
  }

  _installViewerEnhancements() {
    document.addEventListener("click", (event) => {
      const fileNode = event.target.closest?.("[data-path]");
      if (fileNode?.dataset?.path && fileNode.closest("#fm-tree, #fm-recent-list")) this.currentViewerPath = fileNode.dataset.path;
      const anchor = event.target.closest?.("#fm-viewer a[href]");
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (!href || /^(?:https?:|mailto:|data:|#|\/)/i.test(href)) return;
      const resolved = resolveRelativeResearchPath(this.currentViewerPath, href);
      if (!resolved) {
        event.preventDefault();
        anchor.title = "Blocked unsafe relative path";
        return;
      }
      event.preventDefault();
      this.currentViewerPath = resolved;
      this._openResolvedViewerFile(resolved);
    }, true);

  }

  async _openResolvedViewerFile(path) {
    const researchButton = document.querySelector('.fm-source-btn[data-source="research"]');
    if (researchButton && !researchButton.classList.contains("active")) researchButton.click();
    this.currentViewerPath = path;
    await openFMFile(path);
  }

}
