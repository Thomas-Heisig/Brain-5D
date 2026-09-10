"use strict";

// This panel reads public metadata only; participant answers stay in the isolated collector.
export function initExternalReview() {
  const workspace = document.getElementById("tab-research");
  if (!workspace || document.getElementById("external-review-status")) return;
  const panel = document.createElement("section");
  panel.id = "external-review-status";
  panel.className = "research-review-inbox";
  panel.innerHTML = `
    <h3>Externe Begutachtung</h3>
    <p>Der Fragebogen ist ein Screening. Antworten ersetzen weder eine Fachpruefung noch eine institutionelle Ethikfreigabe oder wissenschaftliche Evidenz.</p>
    <p id="external-review-summary" role="status">Status wird geprueft.</p>
    <a href="/review/index.html" target="_blank" rel="noopener noreferrer">Fragenkatalog oeffnen</a>
    <button type="button" id="external-review-refresh">Status pruefen</button>
    <button type="button" id="external-review-method">Pruefverfahren im File Viewer</button>
    <div id="external-review-stages"></div>
    <p>Private Antworten und Prueferidentitaeten werden hier weder geladen noch an eine KI uebergeben. Ausstehende Beurteilungen bleiben offen.</p>`;
  workspace.appendChild(panel);
  document.getElementById("external-review-method").addEventListener("click", () => {
    document.dispatchEvent(new CustomEvent("brain5d:open-file", {
      detail: { source: "research", path: "external_review/INTEGRATION.md" },
    }));
  });
  async function refresh() {
    const summary = document.getElementById("external-review-summary");
    const stages = document.getElementById("external-review-stages");
    stages.replaceChildren();
    summary.textContent = "Status wird geprueft.";
    try {
      const response = await fetch("/api/research/external-review", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (data.available !== true) throw new Error(data.reason || "Keine geprueften Metadaten verfuegbar");
      summary.textContent = `${data.base_questions + data.specialist_questions} Fragen | Version ${data.instrument_version} | Beurteilung ausstehend | Ethikfreigabe nicht behauptet`;
      const list = document.createElement("dl");
      for (const item of data.stages || []) {
        const name = document.createElement("dt");
        name.textContent = `${item.label}: ${item.status}`;
        const description = document.createElement("dd");
        description.textContent = item.requirement;
        list.append(name, description);
      }
      stages.append(list);
    } catch (error) {
      summary.textContent = `Nicht verfuegbar: ${error.message || error}. Keine Freigabe abgeleitet.`;
    }
  }
  document.getElementById("external-review-refresh").addEventListener("click", refresh);
  void refresh();
}
