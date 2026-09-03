"use strict";

function byId(id) {
  return document.getElementById(id);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

export class ExperimentWorkflowPanel {
  constructor() {
    this.questions = [];
    this.hypotheses = [];
    this.nextExperimentId = "";
    this.elements = {
      question: byId("workflow-question"),
      hypothesis: byId("workflow-hypothesis"),
      experimentId: byId("workflow-experiment-id"),
      title: byId("workflow-title"),
      conditions: byId("workflow-conditions"),
      protocol: byId("workflow-protocol"),
      ticks: byId("workflow-ticks"),
      notes: byId("workflow-notes"),
      run: byId("workflow-run"),
      status: byId("workflow-status"),
      result: byId("workflow-result"),
    };
    this.elements.question?.addEventListener("change", () => this._renderHypotheses());
    this.elements.protocol?.addEventListener("change", () => this._applyProtocol());
    this.elements.run?.addEventListener("click", () => this._run());
  }

  async refresh() {
    try {
      const catalog = await fetchJson("/api/experiment/workflow/catalog");
      this.questions = catalog.questions || [];
      this.hypotheses = catalog.hypotheses || [];
      this.nextExperimentId = catalog.next_experiment_id || "";
      if (this.elements.experimentId && !this.elements.experimentId.value) {
        this.elements.experimentId.placeholder = this.nextExperimentId || "automatisch";
      }
      this._renderQuestions();
      this._setStatus("Bereit", "ready");
    } catch (error) {
      this._setStatus(`Nicht verfuegbar: ${error.message}`, "error");
    }
  }

  _renderQuestions() {
    const select = this.elements.question;
    if (!select) return;
    select.replaceChildren(new Option("Forschungsfrage waehlen", ""));
    for (const question of this.questions) {
      select.add(new Option(`${question.id} - ${question.label}`, question.id));
    }
    this._renderHypotheses();
  }

  _renderHypotheses() {
    const select = this.elements.hypothesis;
    if (!select) return;
    const questionId = this.elements.question?.value;
    select.replaceChildren(new Option("Hypothese waehlen", ""));
    for (const hypothesis of this.hypotheses) {
      if (hypothesis.question_id === questionId) {
        select.add(new Option(`${hypothesis.id} - ${hypothesis.label}`, hypothesis.id));
      }
    }
  }

  async _run() {
    const payload = {
      question_id: this.elements.question?.value || "",
      hypothesis_id: this.elements.hypothesis?.value || "",
      experiment_id: this.elements.experimentId?.value.trim() || this.nextExperimentId,
      title: this.elements.title?.value.trim() || "",
      conditions: this.elements.conditions?.value.trim() || "",
      ticks: Number(this.elements.ticks?.value),
      notes: this.elements.notes?.value.trim() || "",
      protocol: this.elements.protocol?.value || "runtime_ticks_v1",
    };
    this.elements.run.disabled = true;
    this._setStatus("Ausfuehrung laeuft", "running");
    this.elements.result.textContent = "";
    try {
      const result = await fetchJson("/api/experiment/workflow/run", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      this._setStatus("Bericht eingetragen", "completed");
      const lines = [
        `Experiment: ${result.experiment_id}`,
        `Manifest: research/${result.manifest}`,
        `Bericht: research/${result.report}`,
      ];
      if (result.evidence_id) lines.push(`Evidenz: ${result.evidence_id}`);
      if (result.data_id) lines.push(`Daten: ${result.data_id}`);
      if (result.result) lines.push(`Tick: ${result.result.start.tick} -> ${result.result.end.tick}`);
      if (result.ai_report) {
        lines.push(`KI-Bericht: ${result.ai_report.status}`);
        if (result.ai_report.json) lines.push(`KI JSON: research/${result.ai_report.json}`);
        if (result.ai_report.markdown) lines.push(`KI Markdown: research/${result.ai_report.markdown}`);
        if (result.ai_report.reason) lines.push(`KI Hinweis: ${result.ai_report.reason}`);
        if (result.ai_report.message) lines.push(`KI Fehler: ${result.ai_report.message}`);
      }
      this.elements.result.textContent = lines.join("\n");
    } catch (error) {
      this._setStatus(`Ausfuehrung abgebrochen: ${error.message}`, "error");
    } finally {
      this.elements.run.disabled = false;
    }
  }

  _applyProtocol() {
    const protocol = this.elements.protocol?.value;
    const presets = {
      science_suite_v1: ["RQ-PING-001", "H-PING-001-A", "EXP-PING-0001", "Network impulse response", "Identischer Zustand, Seed und Input-Spike; Rekurrenz kontrolliert.", "8"],
      science_time_v1: ["RQ-TIME-001", "H-TIME-001-A", "EXP-TIME-0001", "Learning timescale calibration", "Unabhängige Seeds; Tick-Leiter 100 bis 1.000.000; keine automatische Wiederholung.", "1000000"],
      science_5d_v1: ["RQ-5D-001", "H-5D-001-A", "EXP-5D-0001", "Dimensional ablation", "1D, 2D, 3D, 5D und Random-Graph; 30 Seeds je Bedingung.", "8"],
      stdp_pair_timing_v1: ["RQ-STDP-001", "H-STDP-001-A", "EXP-STDP-0001", "Pair-Timing STDP", "Isolierte STDPSynapse; Seed 42; Startgewicht 0.5; Δt -50 bis +50 ms; 10 Replikationen pro Δt.", "11"],
    };
    const preset = presets[protocol];
    if (!preset) return;
    const question = this.elements.question;
    const hypothesis = this.elements.hypothesis;
    if (question) question.value = preset[0];
    this._renderHypotheses();
    if (hypothesis) hypothesis.value = preset[1];
    if (this.elements.experimentId) this.elements.experimentId.value = preset[2];
    if (this.elements.title) this.elements.title.value = preset[3];
    if (this.elements.conditions) this.elements.conditions.value = preset[4];
    if (this.elements.ticks) this.elements.ticks.value = preset[5];
  }

  _setStatus(message, state) {
    if (!this.elements.status) return;
    this.elements.status.textContent = message;
    this.elements.status.dataset.state = state;
  }
}
