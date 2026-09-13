"use strict";

const LAB_STORAGE_KEY = "mhrn-science-experiment-lab-stage-v1";

const LAB_STAGES = Object.freeze([
  { id: "overview", number: "00", label: "Labor", title: "Experiment-Labor", description: "Vom Forschungsziel bis zur überprüften Evidenz – ohne vermischte Arbeitsflächen." },
  { id: "question", number: "01", label: "Frage & Hypothese", title: "Forschungsfrage & Hypothese", description: "Wähle die Forschungsfrage, die dazugehörige Hypothese und den wissenschaftlichen Kontext." },
  { id: "plan", number: "02", label: "Versuchsplan", title: "Versuchsplan & Research Contract", description: "Definiere Protokoll, Seeds, Ticks, Bedingungen, Titel und reproduzierbare Randbedingungen." },
  { id: "run", number: "03", label: "Ausführen", title: "Kontrollierte Ausführung", description: "Starte Einzel- oder Batchläufe und beobachte ausschließlich den aktuellen Ausführungszustand." },
  { id: "series", number: "04", label: "Läufe & Reihen", title: "Läufe, Reihen & Archiv", description: "Ordne aktive Experimente, Experimentreihen und archivierte Versuche in zeitlicher Reihenfolge." },
  { id: "results", number: "05", label: "Ergebnisse", title: "Ergebnisse & Artefakte", description: "Öffne Bericht, Summary, Statistik und Rohdaten des zuletzt abgeschlossenen Laufs." },
  { id: "evidence", number: "06", label: "Review & Evidenz", title: "Review, Interpretation & Evidenzgrenze", description: "Human Review, neue Forschungsfragen und Evidenzgrenzen bleiben von Rohdaten und AI-Interpretation getrennt." },
]);

let activeStage = restoreStage();
let observer = null;
let scheduled = false;
let initialized = false;

const byId = (id) => document.getElementById(id);

function restoreStage() {
  try {
    const value = localStorage.getItem(LAB_STORAGE_KEY);
    if (LAB_STAGES.some((stage) => stage.id === value)) return value;
  } catch (_) {}
  return "overview";
}

function persistStage(stageId) {
  try { localStorage.setItem(LAB_STORAGE_KEY, stageId); } catch (_) {}
}

function setVisibility(node, visible) {
  if (!node) return;
  node.hidden = !visible;
  node.setAttribute("aria-hidden", String(!visible));
  node.classList.toggle("experiment-lab-hidden", !visible);
  node.inert = !visible;
}

function stageMarkup(stage) {
  const extra = stage.id === "overview"
    ? `<div class="experiment-lab-stage-map" aria-label="Experimentablauf">
        ${LAB_STAGES.filter((item) => item.id !== "overview").map((item) => `<button type="button" data-lab-jump="${item.id}"><span>${item.number}</span><strong>${item.label}</strong><small>${item.description}</small></button>`).join("")}
      </div>
      <div class="experiment-lab-boundary"><strong>Wissenschaftliche Grenze</strong><span>DATA → Analyse → Human Review → EVIDENCE. AI-Ausgaben bleiben Interpretation und werden nicht automatisch zu Evidenz.</span></div>`
    : `<div class="experiment-lab-mount" data-lab-mount="${stage.id}"></div>`;
  return `<section class="card experiment-lab-panel" data-lab-stage="${stage.id}" aria-labelledby="experiment-lab-title-${stage.id}"${stage.id === "overview" ? "" : " hidden"}>
    <header class="experiment-lab-panel-title"><div><span class="workspace-kicker">${stage.number} / EXPERIMENT LAB</span><h3 id="experiment-lab-title-${stage.id}">${stage.title}</h3><p>${stage.description}</p></div></header>
    ${extra}
  </section>`;
}

function ensureLabShell() {
  const host = byId("research-panel-experiments");
  if (!host) return null;

  host.querySelectorAll(".research-lanes, .research-focus-rail").forEach((node) => {
    node.dataset.labLegacy = "true";
    setVisibility(node, false);
  });

  let lab = byId("mhrn-experiment-lab");
  if (!lab) {
    lab = document.createElement("section");
    lab.id = "mhrn-experiment-lab";
    lab.className = "experiment-lab";
    lab.innerHTML = `
      <header class="experiment-lab-header">
        <div><span class="workspace-kicker">02 · WISSENSCHAFT / EXPERIMENTE</span><h2>Experiment-Labor</h2><p>Die zentrale Arbeitsfläche für registrierte, reproduzierbare Experimente – in der tatsächlichen Reihenfolge des wissenschaftlichen Ablaufs.</p></div>
        <div class="experiment-lab-header-state"><span>Quelle<strong>Registry + Runtime</strong></span><span>Grenze<strong>Human Review</strong></span></div>
      </header>
      <nav class="experiment-lab-nav" role="tablist" aria-label="Experiment-Labor Schritte">
        ${LAB_STAGES.map((stage) => `<button type="button" role="tab" data-lab-stage-button="${stage.id}" aria-controls="experiment-lab-${stage.id}" aria-selected="${String(stage.id === activeStage)}"><span>${stage.number}</span>${stage.label}</button>`).join("")}
      </nav>
      <div class="experiment-lab-panels">${LAB_STAGES.map(stageMarkup).join("")}</div>`;

    const source = byId("experiment-workflow");
    if (source) source.insertAdjacentElement("beforebegin", lab);
    else host.prepend(lab);

    lab.addEventListener("click", (event) => {
      const target = event.target.closest("[data-lab-stage-button], [data-lab-jump]");
      if (!target) return;
      selectExperimentLabStage(target.dataset.labStageButton || target.dataset.labJump, { scroll: Boolean(target.dataset.labJump) });
    });
  }
  return lab;
}

function mount(stageId) {
  return document.querySelector(`[data-lab-mount="${stageId}"]`);
}

function moveNode(node, stageId) {
  const target = mount(stageId);
  if (!node || !target || node.parentElement === target) return false;
  node.dataset.labOwned = stageId;
  target.appendChild(node);
  return true;
}

function moveSelector(selector, stageId) {
  return moveNode(document.querySelector(selector), stageId);
}

function moveFormField(controlId, stageId) {
  const control = byId(controlId);
  const label = control?.closest("label");
  if (label) moveNode(label, stageId);
}

function flattenNestedSurfaces(root) {
  if (!root) return;
  root.querySelectorAll(".research-catalog-selector, .research-contract-card, .experiment-library-card, .workflow-result-actions, .human-review-card, .rq-proposal-card, .research-review-inbox, .research-gateway-experiment, .research-dimension-control").forEach((node) => {
    node.classList.add("experiment-lab-flat-content");
  });
}

function relocateObservatory() {
  const metrics = byId("mhrn-scientific-metrics");
  const research = byId("tab-research");
  if (!metrics || !research) return;
  metrics.dataset.mhrnRoute = "science:observatory";
  if (metrics.parentElement !== research) research.appendChild(metrics);
  const isObservatory = document.body.dataset.currentArea === "science" && document.body.dataset.currentRoute === "observatory";
  if (!isObservatory) setVisibility(metrics, false);
}

function organizeStaticWorkflow() {
  const source = byId("experiment-workflow");
  if (!source) return;

  moveSelector("#experiment-workflow > .experiment-workflow-header", "run");
  moveSelector("#experiment-workflow > .workflow-form-grid", "plan");
  moveSelector("#experiment-workflow > .workflow-progress-row", "run");
  moveSelector("#experiment-workflow > .workflow-actions", "run");
  moveSelector("#workflow-result", "results");

  moveFormField("workflow-question", "question");
  moveFormField("workflow-hypothesis", "question");

  source.querySelectorAll(":scope > .workflow-steps").forEach((node) => setVisibility(node, false));
  source.classList.remove("card");
  source.classList.add("experiment-lab-source");
  setVisibility(source, false);
}

function organizeDynamicWorkflow() {
  moveSelector("#workflow-research-catalog", "question");
  moveSelector("#workflow-research-contract", "plan");
  moveSelector(".research-dimension-control", "plan");
  moveSelector(".research-gateway-experiment", "run");
  moveSelector("#workflow-experiment-library", "series");
  moveSelector("#workflow-result-actions", "results");
  moveSelector("#workflow-human-review", "evidence");
  moveSelector("#workflow-rq-proposal", "evidence");
  moveSelector("#workflow-review-inbox", "evidence");


  const lab = byId("mhrn-experiment-lab");
  flattenNestedSurfaces(lab);
}

function syncRunStatus() {
  const source = byId("workflow-status");
  const lab = byId("mhrn-experiment-lab");
  if (!lab) return;
  const state = source?.dataset.state || "idle";
  lab.dataset.runState = state;
}

function organizeExperimentLab() {
  const lab = ensureLabShell();
  if (!lab) return;
  organizeStaticWorkflow();
  organizeDynamicWorkflow();
  relocateObservatory();
  syncRunStatus();
  selectExperimentLabStage(activeStage, { persist: false });
}

function scheduleOrganize() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    scheduled = false;
    organizeExperimentLab();
  });
}

export function selectExperimentLabStage(stageId, { scroll = false, persist = true } = {}) {
  if (!LAB_STAGES.some((stage) => stage.id === stageId)) stageId = "overview";
  activeStage = stageId;
  if (persist) persistStage(stageId);

  document.querySelectorAll("[data-lab-stage]").forEach((panel) => {
    setVisibility(panel, panel.dataset.labStage === stageId);
  });
  document.querySelectorAll("[data-lab-stage-button]").forEach((button) => {
    const active = button.dataset.labStageButton === stageId;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
  });

  if (scroll) byId("mhrn-experiment-lab")?.scrollIntoView({ block: "start", behavior: "smooth" });
}

export function initExperimentLab() {
  if (initialized) {
    scheduleOrganize();
    return;
  }
  initialized = true;
  organizeExperimentLab();

  const host = byId("research-panel-experiments") || document.querySelector("main") || document.body;
  observer = new MutationObserver(() => scheduleOrganize());
  observer.observe(host, { childList: true, subtree: true });

  const bodyObserver = new MutationObserver(() => {
    relocateObservatory();
    if (document.body.dataset.currentArea === "science" && document.body.dataset.currentRoute === "experiments") {
      selectExperimentLabStage(activeStage, { persist: false });
    }
  });
  bodyObserver.observe(document.body, { attributes: true, attributeFilter: ["data-current-area", "data-current-route"] });

  document.addEventListener("brain5d:experiment-progress", (event) => {
    const detail = event.detail || {};
    if (detail.active) selectExperimentLabStage("run");
    else if (Number(detail.progress || 0) >= 100) selectExperimentLabStage("results");
  });

  document.addEventListener("mhrn:research-review-completed", () => selectExperimentLabStage("evidence"));
  window.MHRNExperimentLab = { selectStage: selectExperimentLabStage, stages: LAB_STAGES };
}
