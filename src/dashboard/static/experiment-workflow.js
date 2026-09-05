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
  constructor({ onCompleted = null } = {}) {
    this.onCompleted = onCompleted;
    this.questions = [];
    this.hypotheses = [];
    this.nextExperimentId = "";
    this.activePreset = null;
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
      status: byId("workflow-status"),
      result: byId("workflow-result"),
    };
    this.elements.question?.addEventListener("change", () => this._renderHypotheses());
    this.elements.protocol?.addEventListener("change", () => this._applyProtocol());
    this.elements.conditionProfile?.addEventListener("change", () => this._applyConditionProfile());
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
      this._applyProtocol();
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
      seeds: this.elements.seeds?.value.trim() || "",
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
      const runResult = result.result;
      if (runResult && typeof runResult === "object") {
        if (runResult.start && runResult.end) {
          lines.push(`Tick: ${runResult.start.tick} -> ${runResult.end.tick}`);
        } else if (typeof runResult.run_count === "number") {
          const duration = typeof runResult.duration_seconds === "number"
            ? `; Dauer: ${runResult.duration_seconds.toFixed(3)} s`
            : "";
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
      if (this.onCompleted) await this.onCompleted();
    } catch (error) {
      this._setStatus(`Ausfuehrung abgebrochen: ${error.message}`, "error");
    } finally {
      this.elements.run.disabled = false;
    }
  }

  _applyProtocol() {
    const protocol = this.elements.protocol?.value;
    const presets = {
      science_suite_v1: {
        question: "RQ-PING-001",
        hypothesis: "H-PING-001-A",
        title: "Network impulse response",
        conditions: "Seeds 42,43,44; identischer Anfangszustand je Seed; Impulsstrom 100.0; Rekurrenz als kontrollierte Behandlung.",
        ticks: "8",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; identischer Anfangszustand je Seed; Impulsstrom 100.0; Rekurrenz als kontrollierte Behandlung.",
          replication: "Seeds 42,43,44; zwei identische Replikate je Behandlung; Response-Signatur und Zustands-Digest vergleichen.",
          sensitivity: "Seeds 42,43,44; nur die Rekurrenzbehandlung variieren; alle übrigen Parameter konstant halten.",
        },
      },
      science_time_v1: {
        question: "RQ-TIME-001",
        hypothesis: "H-TIME-001-A",
        title: "Learning timescale calibration",
        conditions: "Seeds 42,43,44; Tick-Leiter bis 1.000.000; Laufzeit pro Stufe messen.",
        ticks: "1000000",
        seeds: "42,43,44",
        profiles: {
          standard: "Seeds 42,43,44; Tick-Leiter bis 1.000.000; Laufzeit pro Stufe messen.",
          short: "Seeds 42,43,44; Tick-Leiter bis 10.000; schneller Kalibrierungslauf vor dem Langzeittest.",
        },
      },
      science_5d_v1: {
        question: "RQ-5D-001",
        hypothesis: "H-5D-001-A",
        title: "Dimensional ablation",
        conditions: "Seeds 0-29; 1D, 2D, 3D, 5D und Random-Graph; nur Dimension bzw. Topologie variieren.",
        ticks: "8",
        seeds: "0-29",
        profiles: {
          standard: "Seeds 0-29; 1D, 2D, 3D, 5D und Random-Graph; nur Dimension bzw. Topologie variieren.",
          pilot: "Seeds 0-2; alle Dimensionen und Topologien als kostenguenstiger Pilotlauf.",
        },
      },
      stdp_pair_timing_v1: {
        question: "RQ-STDP-001",
        hypothesis: "H-STDP-001-A",
        title: "Pair-Timing STDP",
        conditions: "Registriertes Protokoll: isolierte STDPSynapse; Startgewicht 0.5; Delta-t -50 bis +50 ms; 10 Replikationen je Delta-t.",
        ticks: "11",
        seeds: "42",
        profiles: { standard: "Registriertes Protokoll; Eingaben werden durch protocol.json festgelegt." },
      },
      runtime_ticks_v1: {
        question: "",
        hypothesis: "",
        title: "Kontrollierter Runtime-Lauf",
        conditions: "Seed, Konfiguration, Replikate und Abbruchkriterien explizit dokumentieren.",
        ticks: "100",
        seeds: "42",
        profiles: { standard: "Seed, Konfiguration, Replikate und Abbruchkriterien explizit dokumentieren." },
      },
    };
    const preset = presets[protocol];
    if (!preset) return;
    this.activePreset = preset;
    const question = this.elements.question;
    const hypothesis = this.elements.hypothesis;
    if (question && preset.question) question.value = preset.question;
    this._renderHypotheses();
    if (hypothesis && preset.hypothesis) hypothesis.value = preset.hypothesis;
    if (this.elements.title) this.elements.title.value = preset.title;
    if (this.elements.ticks) this.elements.ticks.value = preset.ticks;
    if (this.elements.seeds) this.elements.seeds.value = preset.seeds;
    if (this.elements.conditionProfile) this.elements.conditionProfile.value = "standard";
    this._applyConditionProfile(preset);

    const fixedProtocol = protocol === "stdp_pair_timing_v1";
    [this.elements.question, this.elements.hypothesis, this.elements.title, this.elements.conditions, this.elements.seeds, this.elements.ticks, this.elements.conditionProfile].forEach((element) => {
      if (element) element.disabled = fixedProtocol;
    });
  }

  _applyConditionProfile(preset = this.activePreset) {
    const profiles = preset?.profiles || {
      standard: this.elements.conditions?.value || "",
    };
    const profile = this.elements.conditionProfile?.value || "standard";
    const condition = profiles[profile] || profiles.standard || "";
    if (this.elements.conditions && condition) this.elements.conditions.value = condition;
  }

  _setStatus(message, state) {
    if (!this.elements.status) return;
    this.elements.status.textContent = message;
    this.elements.status.dataset.state = state;
  }
}
