"use strict";

import { ExperimentWorkflowPanel as BaseExperimentWorkflowPanel } from "./experiment-workflow-base.js";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}

const PROFILE_LABELS = Object.freeze({
  standard: "Registrierter Gesamtplan",
  controls: "Nur Kontrollen",
  treatments: "Nur Treatments",
  replication: "Replikation",
  sensitivity: "Sensitivität",
  pilot: "Pilot",
  short: "Kurzlauf",
});

export class ExperimentWorkflowPanel extends BaseExperimentWorkflowPanel {
  _ensureResearchUX() {
    super._ensureResearchUX();
    const question = this.elements.question;
    if (!question || byId("workflow-research-catalog")) return;

    const host = question.closest("label")?.parentElement;
    if (!host) return;
    const catalog = document.createElement("section");
    catalog.id = "workflow-research-catalog";
    catalog.className = "research-catalog-selector";
    catalog.innerHTML = `
      <div class="panel-title">
        <div>
          <h3>Research Catalog</h3>
          <p>Durchsuchbare Auswahl statt langer Pulldown-Liste. Operational = frozen/preregistered; Exploratory = protokollierter Lauf ohne Evidenz-Promotion.</p>
        </div>
        <span id="workflow-research-count" class="gate-badge pending">0 RQs</span>
      </div>
      <div class="research-catalog-controls">
        <input id="workflow-research-search" type="search" placeholder="RQ, Hypothese oder Begriff suchen …" autocomplete="off">
        <label class="research-catalog-check"><input id="workflow-research-operational" type="checkbox"> nur operational</label>
      </div>
      <div id="workflow-research-results" class="research-catalog-results" role="listbox" aria-label="Forschungsfragen"></div>
      <section id="workflow-review-inbox" class="research-review-inbox" aria-label="Offene Human Reviews">
        <div class="research-review-head"><strong>Review Inbox</strong><span id="workflow-review-count" class="gate-badge pending">lädt …</span></div>
        <p>Offene Human Reviews können hier nachvollziehbar abgeschlossen werden. Reviewer, Entscheidung und Kommentar sind Pflicht; ein Review erzeugt niemals automatisch wissenschaftliche Evidenz.</p>
        <div class="research-review-controls">
          <input id="workflow-review-reviewer" type="text" placeholder="Reviewer / Verantwortlicher" autocomplete="name">
          <button id="workflow-review-refresh" type="button">Reviews aktualisieren</button>
        </div>
        <div id="workflow-review-list" class="research-review-list"></div>
      </section>
      <div class="research-dimension-control">
        <label>MSBA Projektions-Dimensionen
          <input id="workflow-projection-dimensions" type="number" min="1" max="32" value="5">
        </label>
        <small>1–32 Dimensionen für externe/MSBA-Projektionsräume. Der persistierte produktive SNN-Core bleibt aus Kompatibilitätsgründen derzeit 5D.</small>
      </div>
      <section class="research-gateway-experiment" aria-label="Gateway Experiment">
        <div class="research-review-head"><strong>Gateway Experiment</strong><span class="gate-badge pending">EXPERIMENTAL</span></div>
        <div class="research-gateway-controls">
          <label>Experiment ID<input id="workflow-gateway-experiment-id" type="text" placeholder="EXP-GW-..." autocomplete="off"></label>
          <label>Condition<select id="workflow-gateway-condition"><option value="frozen">Frozen</option><option value="random">Random</option><option value="shuffle">Shuffle</option><option value="plastic">Plastic</option></select></label>
          <label>Seed<input id="workflow-gateway-seed" type="number" value="101"></label>
          <button id="workflow-gateway-activate" type="button">Gateway aktivieren</button>
        </div>
        <small id="workflow-gateway-message">Plastic erfordert eine registrierte, eingefrorene Preregistration; produktive Gateway-Plastizität bleibt gesperrt.</small>
      </section>`;
    host.insertAdjacentElement("beforebegin", catalog);
    for (const [field, label] of Object.entries({domain: "Domain", status: "Status", evidence_status: "Evidenzpruefung", experiment_progress: "Versuchsfortschritt"})) {
      const wrapper = document.createElement("label");
      wrapper.textContent = label;
      const select = document.createElement("select");
      select.dataset.catalogFacet = field;
      select.setAttribute("aria-label", label);
      select.add(new Option("Alle", ""));
      select.addEventListener("change", () => this._renderResearchCatalog());
      wrapper.appendChild(select);
      catalog.querySelector(".research-catalog-controls").appendChild(wrapper);
    }

    const style = document.createElement("style");
    style.dataset.researchCatalogStyle = "true";
    style.textContent = `
      .research-catalog-selector{grid-column:1/-1;border:1px solid var(--border-color,#30363d);border-radius:12px;padding:14px;margin-bottom:10px}
      .research-catalog-controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0}
      .research-catalog-controls input[type=search]{flex:1 1 320px;min-width:220px}
      .research-catalog-check{display:flex!important;gap:7px;align-items:center!important;white-space:nowrap}
      .research-catalog-results{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:8px;max-height:330px;overflow:auto;padding:2px}
      .research-rq-card{appearance:none;text-align:left;border:1px solid var(--border-color,#30363d);border-radius:9px;padding:10px;background:transparent;color:inherit;cursor:pointer}
      .research-rq-card:hover,.research-rq-card.is-selected{border-color:var(--accent,#58a6ff);background:rgba(88,166,255,.08)}
      .research-rq-head{display:flex;gap:8px;justify-content:space-between;align-items:center;margin-bottom:6px}
      .research-rq-card p{margin:0;font-size:.88rem;line-height:1.35}
      .research-rq-badge{font-size:.72rem;padding:2px 6px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}
      .research-rq-badge.operational{color:#3fb950}.research-rq-badge.exploratory{color:#d29922}
      .research-dimension-control{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin-top:12px;padding-top:10px;border-top:1px solid var(--border-color,#30363d)}
      .research-dimension-control label{max-width:220px}.research-dimension-control small{max-width:680px;opacity:.8}
      .research-review-inbox{margin-top:14px;padding-top:12px;border-top:1px solid var(--border-color,#30363d)}
      .research-review-head,.research-review-controls,.research-review-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
      .research-review-head{justify-content:space-between}.research-review-controls{margin:8px 0}
      .research-review-controls input{min-width:240px;flex:1}.research-review-list{display:grid;gap:8px}
      .research-review-card{border:1px solid var(--border-color,#30363d);border-radius:9px;padding:10px}
      .research-review-card textarea{width:100%;min-height:72px;margin:8px 0;resize:vertical}
      .research-review-meta{font-size:.78rem;opacity:.75}.research-review-empty{opacity:.75;font-style:italic}
      .research-gateway-experiment{margin-top:14px;padding-top:12px;border-top:1px solid var(--border-color,#30363d)}
      .research-gateway-controls{display:flex;gap:10px;align-items:end;flex-wrap:wrap;margin:8px 0}
      .research-gateway-controls label{display:grid;gap:4px;min-width:140px}.research-gateway-controls input,.research-gateway-controls select{min-width:120px}
      .research-gateway-controls button{cursor:pointer}.research-gateway-experiment small{display:block;opacity:.78}
    `;
    document.head.appendChild(style);

    byId("workflow-research-search")?.addEventListener("input", () => this._renderResearchCatalog());
    byId("workflow-research-operational")?.addEventListener("change", () => this._renderResearchCatalog());
    byId("workflow-review-refresh")?.addEventListener("click", () => this._loadReviewInbox());
    byId("workflow-review-list")?.addEventListener("click", (event) => this._handleReviewAction(event));
    byId("workflow-gateway-activate")?.addEventListener("click", () => this._activateGateway());
    this._loadReviewInbox();
    byId("workflow-projection-dimensions")?.addEventListener("change", (event) => {
      const value = Math.max(1, Math.min(32, Number(event.target.value) || 5));
      event.target.value = String(value);
      this._syncProjectionDimensions(value);
    });
  }

  async _activateGateway() {
    const message = byId("workflow-gateway-message");
    const experimentId = (byId("workflow-gateway-experiment-id")?.value || "").trim();
    const condition = byId("workflow-gateway-condition")?.value || "frozen";
    const seed = Number(byId("workflow-gateway-seed")?.value || 101);
    if (!experimentId || !Number.isInteger(seed)) {
      if (message) message.textContent = "Experiment ID und ganzzahliger Seed sind erforderlich.";
      return;
    }
    try {
      const response = await fetch(`/api/experiments/${encodeURIComponent(experimentId)}/gateway/activate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ condition, seed, experiment_mode: true }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      if (message) message.textContent = `Gateway ${condition} aktiv: ${payload.gateway.state}. Productive: LOCKED.`;
      document.dispatchEvent(new CustomEvent("mhrn:gateway-status-updated", { detail: payload }));
    } catch (error) {
      if (message) message.textContent = `Gateway-Start blockiert: ${error.message || error}`;
    }
  }

  async _loadReviewInbox() {
    const list = byId("workflow-review-list");
    const count = byId("workflow-review-count");
    if (!list) return;
    try {
      const response = await fetch("/api/research/reviews", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`Review inbox HTTP ${response.status}`);
      const payload = await response.json();
      this.reviewInbox = Array.isArray(payload.items) ? payload.items : [];
      if (count) {
        count.textContent = `${Number(payload.open || 0)} offen`;
        count.className = `gate-badge ${Number(payload.open || 0) ? "pending" : "success"}`;
      }
      if (!this.reviewInbox.length) {
        list.innerHTML = '<p class="research-review-empty">Keine offenen Human Reviews.</p>';
        return;
      }
      list.innerHTML = this.reviewInbox.map((item, index) => `
        <article class="research-review-card" data-review-index="${index}">
          <strong>${escapeHtml(item.title || item.artifact_path)}</strong>
          <div class="research-review-meta">${escapeHtml(item.research_question_id || item.kind || "review")} · ${escapeHtml(item.artifact_path || "")}</div>
          <p>${escapeHtml(item.summary || "Human Review erforderlich.")}</p>
          <textarea aria-label="Review-Kommentar" placeholder="Begründung / Review-Kommentar"></textarea>
          <div class="research-review-actions">
            <button type="button" data-review-decision="accepted_as_interpretation">Als Interpretation akzeptieren</button>
            <button type="button" data-review-decision="rejected">Ablehnen</button>
          </div>
        </article>`).join("");
    } catch (error) {
      list.innerHTML = `<p class="research-review-empty">Review Inbox nicht verfügbar: ${escapeHtml(error.message || error)}</p>`;
      if (count) count.textContent = "Fehler";
    }
  }

  async _handleReviewAction(event) {
    const button = event.target.closest?.("[data-review-decision]");
    if (!button) return;
    const card = button.closest("[data-review-index]");
    const item = this.reviewInbox?.[Number(card?.dataset.reviewIndex)];
    if (!item) return;
    const reviewer = (byId("workflow-review-reviewer")?.value || "").trim();
    const comments = (card.querySelector("textarea")?.value || "").trim();
    if (!reviewer || !comments) {
      window.alert("Reviewer und Review-Kommentar sind Pflicht.");
      return;
    }
    const review_status = button.dataset.reviewDecision;
    const body = item.kind === "artifact"
      ? { artifact_path: item.artifact_path, reviewer, comments, review_status }
      : { reviewer, comments, review_status };
    button.disabled = true;
    try {
      const response = await fetch(item.review_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || payload.message || `HTTP ${response.status}`);
      await this._loadReviewInbox();
      document.dispatchEvent(new CustomEvent("mhrn:research-review-completed", { detail: payload }));
    } catch (error) {
      window.alert(`Review konnte nicht gespeichert werden: ${error.message || error}`);
    } finally {
      button.disabled = false;
    }
  }

  _configureConditionProfiles(preset = this.activePreset) {
    const select = this.elements.conditionProfile;
    if (!select) return;
    const profiles = preset?.profiles || { standard: preset?.conditions || "" };
    select.replaceChildren();
    for (const [key, value] of Object.entries(profiles)) {
      if (!value) continue;
      select.add(new Option(PROFILE_LABELS[key] || key, key));
    }
    if (!select.options.length) select.add(new Option("Standard", "standard"));
    select.value = "standard";
  }

  _renderQuestions() {
    super._renderQuestions();
    this._renderResearchCatalog();
  }

  _isOperational(questionId) {
    return this.protocols.some(
      (item) => item.research_question === questionId && item.preregistration,
    );
  }

  _matchingHypotheses(questionId) {
    return this.hypotheses.filter((item) => item.question_id === questionId);
  }

  _renderResearchCatalog() {
    const results = byId("workflow-research-results");
    const count = byId("workflow-research-count");
    if (!results) return;
    const search = (byId("workflow-research-search")?.value || "").trim().toLowerCase();
    const operationalOnly = Boolean(byId("workflow-research-operational")?.checked);
    const selected = this.elements.question?.value || "";
    const facets = [...document.querySelectorAll("[data-catalog-facet]")];
    for (const select of facets) {
      const value = select.value;
      const field = select.dataset.catalogFacet;
      const configured = this.facets?.[field];
      const options = Array.isArray(configured)
        ? configured
        : [...new Set(this.questions.map((item) => item[field]).filter(Boolean))].sort();
      select.replaceChildren(new Option("Alle", ""), ...options.map((item) => new Option(item, item)));
      select.value = options.includes(value) ? value : "";
    }
    const visible = this.questions.filter((question) => {
      const hypotheses = this._matchingHypotheses(question.id);
      const haystack = [question.id, question.label, ...hypotheses.map((item) => `${item.id} ${item.label}`)]
        .join(" ")
        .toLowerCase();
      if (facets.some((select) => select.value && question[select.dataset.catalogFacet] !== select.value)) return false;
      if (search && !haystack.includes(search)) return false;
      if (operationalOnly && !this._isOperational(question.id)) return false;
      return true;
    });
    if (count) count.textContent = `${visible.length} / ${this.questions.length} RQs`;
    results.innerHTML = visible
      .map((question) => {
        const operational = this._isOperational(question.id);
        const hypotheses = this._matchingHypotheses(question.id);
        return `<button type="button" class="research-rq-card ${selected === question.id ? "is-selected" : ""}" data-rq-id="${escapeHtml(question.id)}" role="option" aria-selected="${selected === question.id}">
          <div class="research-rq-head"><strong>${escapeHtml(question.id)}</strong><span class="research-rq-badge ${operational ? "operational" : "exploratory"}">${operational ? "OPERATIONAL" : "EXPLORATORY"}</span></div>
          <p>${escapeHtml(question.label)}</p>
          <small>${hypotheses.length} Hypothese${hypotheses.length === 1 ? "" : "n"}</small>
        </button>`;
      })
      .join("");
    results.querySelectorAll("[data-rq-id]").forEach((button) => {
      button.addEventListener("click", () => this._selectResearchQuestion(button.dataset.rqId));
    });
  }

  _selectResearchQuestion(questionId) {
    if (!questionId || !this.elements.question) return;
    this.elements.question.value = questionId;
    this._renderHypotheses();
    this._alignProtocolWithQuestion();
    if (!this._isOperational(questionId) && this.elements.protocol) {
      this.elements.protocol.value = "runtime_ticks_v1";
      this._applyProtocol();
    }
    this._renderContract();
    this._renderResearchCatalog();
  }

  _syncProjectionDimensions(value) {
    const marker = `MSBA projection_dimensions=${value}`;
    const notes = this.elements.notes;
    if (notes) {
      const lines = String(notes.value || "")
        .split("\n")
        .filter((line) => !line.startsWith("MSBA projection_dimensions="));
      lines.push(marker);
      notes.value = lines.filter(Boolean).join("\n");
    }
  }

  _applyProtocol() {
    super._applyProtocol();
    const operational = this._protocolContract(this.elements.protocol?.value);
    if (!operational) return;

    const profiles = operational.condition_profiles || {
      standard: (operational.conditions || [])
        .map((item) => `${item.id || item.condition_id || item}${item.role ? ` (${item.role})` : ""}`)
        .join("; "),
    };
    const defaultSeeds = operational.default_seed_expression;
    this.activePreset = {
      ...(this.activePreset || {}),
      question: operational.research_question,
      hypothesis: operational.hypothesis,
      title: operational.label || operational.id,
      ticks: String(operational.default_ticks ?? this.elements.ticks?.value ?? "100"),
      seeds: defaultSeeds || this.activePreset?.seeds || "101",
      conditions: profiles.standard || "",
      profiles,
    };

    if (this.elements.seeds && this.activePreset.seeds) this.elements.seeds.value = this.activePreset.seeds;
    if (this.elements.ticks && this.activePreset.ticks) this.elements.ticks.value = this.activePreset.ticks;
    this._configureConditionProfiles(this.activePreset);
    this._applyConditionProfile(this.activePreset);
    this._renderContract();
    this._renderResearchCatalog();
  }

  _renderContract() {
    super._renderContract();
    if (this.activeContract) return;
    const content = byId("workflow-contract-content");
    if (!content || !this.activePreset) return;
    content.innerHTML = `
      <details class="legacy-diagnostic-details" open>
        <summary><span>Exploratory / diagnostic protocol</span><small>keine automatische Evidenz-Promotion</small></summary>
        <div class="legacy-diagnostic-body">
          <p>${escapeHtml(this.activePreset.conditions || "")}</p>
          <p>Dieser Lauf kann die ausgewählte RQ/H protokolliert explorieren. Er besitzt aber keinen passenden eingefrorenen Research Contract und darf deshalb nicht als bestätigende Evidenz interpretiert werden.</p>
        </div>
      </details>`;
  }
}
