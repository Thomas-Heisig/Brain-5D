"use strict";

import { ExperimentWorkflowPanel as BaseExperimentWorkflowPanel } from "./experiment-workflow-base.js";

function byId(id) {
  return document.getElementById(id);
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
  }

  _renderContract() {
    super._renderContract();
    if (this.activeContract) return;
    const content = byId("workflow-contract-content");
    if (!content || !this.activePreset) return;
    content.innerHTML = `
      <details class="legacy-diagnostic-details">
        <summary><span>Legacy / diagnostic protocol</span><small>nur bei Bedarf öffnen</small></summary>
        <div class="legacy-diagnostic-body">
          <p>${this.activePreset.conditions || ""}</p>
          <p>Dieser Lauf besitzt keinen operationalen eingefrorenen Research Contract und ist deshalb nicht automatisch als bestätigende Evidenz zu interpretieren.</p>
        </div>
      </details>`;
  }
}
