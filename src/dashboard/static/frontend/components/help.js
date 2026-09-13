"use strict";
import { openDocumentationFile } from "../../file-viewer.js";

const HELP = {
  "science-maturity-panel": { title: "Wissenschaftliche Reifegrade", source: "06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md", basis: "Engineering-Reife und wissenschaftliche Evidenz werden getrennt behandelt." },
  "runtime-capability-board": { title: "Runtime & Wesen", source: "02-architecture/EMBODIMENT_FOUNDATION.md", basis: "Embodiment, Sensoren und Aktoren folgen expliziten Adapter- und Kausalitätsgrenzen." },
  "mhrn-runtime-io": { title: "Runtime Input/Output", source: "02-architecture/EMBODIMENT_FOUNDATION.md", basis: "Manuelle Injektionen sind Operator-/Debug-Eingriffe und niemals automatische Evidenz." },
  "neuron-model-viewer": { title: "Neuron Model Viewer", source: "03-dashboard/DASHBOARD.md", basis: "Projektionen sind Analyseartefakte auf realen Runtime-Samples; sie beweisen keine Hypothese." },
};
function ensureDialog() {
  let dialog = document.getElementById("mhrn-panel-help");
  if (dialog) return dialog;
  dialog = document.createElement("dialog");
  dialog.id = "mhrn-panel-help";
  dialog.className = "mhrn-panel-help";
  dialog.innerHTML = `<header><strong id="mhrn-panel-help-title">Hilfe</strong><button type="button" data-panel-help-close>×</button></header><p id="mhrn-panel-help-basis"></p><button type="button" class="panel-help-source" id="mhrn-panel-help-source">Quelle öffnen</button>`;
  document.body.appendChild(dialog);
  dialog.addEventListener("click", (event) => { if (event.target.closest("[data-panel-help-close]")) dialog.close(); });
  return dialog;
}
function attach() {
  for (const [id, help] of Object.entries(HELP)) {
    const panel = document.getElementById(id);
    if (!panel || panel.querySelector(":scope > .panel-help-button")) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "panel-help-button";
    button.textContent = "?";
    button.title = `Erklärung, Datenquelle und wissenschaftliche Grundlage: ${help.title}`;
    button.dataset.helpPanel = id;
    panel.prepend(button);
  }
}
export function initPanelHelp() {
  ensureDialog(); attach();
  const observer = new MutationObserver(attach); observer.observe(document.body, { childList: true, subtree: true });
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-help-panel]"); if (!button) return;
    const help = HELP[button.dataset.helpPanel]; if (!help) return;
    const dialog = ensureDialog();
    dialog.querySelector("#mhrn-panel-help-title").textContent = help.title;
    dialog.querySelector("#mhrn-panel-help-basis").textContent = `${help.basis} Datenquelle: docs/${help.source}`;
    const source = dialog.querySelector("#mhrn-panel-help-source");
    source.onclick = () => { dialog.close(); openDocumentationFile(help.source); };
    dialog.showModal();
  });
}
