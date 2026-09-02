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
    this.elements = {
      question: byId("workflow-question"),
      hypothesis: byId("workflow-hypothesis"),
      experimentId: byId("workflow-experiment-id"),
      title: byId("workflow-title"),
      conditions: byId("workflow-conditions"),
      ticks: byId("workflow-ticks"),
      notes: byId("workflow-notes"),
      run: byId("workflow-run"),
      status: byId("workflow-status"),
      result: byId("workflow-result"),
    };
    this.elements.question?.addEventListener("change", () => this._renderHypotheses());
    this.elements.run?.addEventListener("click", () => this._run());
  }

  async refresh() {
    try {
      const catalog = await fetchJson("/api/experiment/workflow/catalog");
      this.questions = catalog.questions || [];
      this.hypotheses = catalog.hypotheses || [];
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
      experiment_id: this.elements.experimentId?.value.trim() || "",
      title: this.elements.title?.value.trim() || "",
      conditions: this.elements.conditions?.value.trim() || "",
      ticks: Number(this.elements.ticks?.value),
      notes: this.elements.notes?.value.trim() || "",
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
      this.elements.result.textContent = [
        `Experiment: ${result.experiment_id}`,
        `Manifest: research/${result.manifest}`,
        `Bericht: research/${result.report}`,
        `Tick: ${result.result.start.tick} -> ${result.result.end.tick}`,
      ].join("\n");
    } catch (error) {
      this._setStatus(`Ausfuehrung abgebrochen: ${error.message}`, "error");
    } finally {
      this.elements.run.disabled = false;
    }
  }

  _setStatus(message, state) {
    if (!this.elements.status) return;
    this.elements.status.textContent = message;
    this.elements.status.dataset.state = state;
  }
}