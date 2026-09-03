"use strict";

let currentState = {};

const byId = (id) => document.getElementById(id);
const setText = (id, value) => {
  const node = byId(id);
  if (node) node.textContent = String(value ?? "—");
};

function createLearningTabButton() {
  const nav = document.querySelector(".tab-nav");
  if (!nav || nav.querySelector('[data-tab="learning"]')) return;
  const button = document.createElement("button");
  button.className = "tab-btn";
  button.dataset.tab = "learning";
  button.type = "button";
  button.textContent = "🧭 LEARNING";

  const control = nav.querySelector('[data-tab="control"]');
  if (control?.nextSibling) nav.insertBefore(button, control.nextSibling);
  else nav.append(button);
}

function createLearningWorkspace() {
  if (byId("tab-learning")) return;
  const main = document.querySelector("main");
  if (!main) return;

  const section = document.createElement("section");
  section.className = "tab-content";
  section.id = "tab-learning";
  section.innerHTML = `
    <header class="workspace-header" data-workspace="learning">
      <div>
        <span class="workspace-kicker">PREPARE · OBSERVE · COMPARE</span>
        <h2>Learning Preparation Studio</h2>
        <p>KI darf Lernbedingungen vorbereiten. Muster, Gewichte, Ströme und Rewardwerte bleiben außerhalb ihrer Autorität.</p>
      </div>
      <div class="workspace-status-strip">
        <span>Engine<strong id="learning-studio-engine">unknown</strong></span>
        <span>STDP<strong id="learning-studio-stdp">unknown</strong></span>
        <span>Reward<strong id="learning-studio-reward">unknown</strong></span>
        <span>Session<strong id="learning-studio-session">none</strong></span>
      </div>
    </header>

    <section class="control-causal-map" aria-label="Learning workflow">
      <div><span>1</span><strong>Lernziel</strong><small>Messbare Aufgabe statt gewünschtes Neuronenmuster</small></div>
      <i>→</i><div><span>2</span><strong>Baseline</strong><small>Verhalten und optionale Impulsantwort vor Lernen</small></div>
      <i>→</i><div><span>3</span><strong>Vorbereitung</strong><small>Quellen, Partitionen, Kontrollen, Stop-Regel</small></div>
      <i>→</i><div><span>4</span><strong>Experience</strong><small>Environment → SNN → LearningEngine</small></div>
      <i>→</i><div><span>5</span><strong>Vergleich</strong><small>Post-Evaluation, Holdout und Evidence</small></div>
    </section>

    <section class="overview-operations-grid">
      <article class="overview-surface">
        <div class="overview-surface-title"><div><span>LIVE</span><h3>Aktueller Lernzustand</h3></div><strong id="learning-studio-learning-ms">—</strong></div>
        <div class="overview-dynamics-grid">
          <div><span>STDP Updates</span><strong id="learning-studio-stdp-updates">—</strong></div>
          <div><span>Reward Updates</span><strong id="learning-studio-reward-updates">—</strong></div>
          <div><span>Rewards</span><strong id="learning-studio-rewards">—</strong></div>
          <div><span>Pending</span><strong id="learning-studio-pending">—</strong></div>
          <div><span>Knowledge Items</span><strong id="learning-studio-knowledge">—</strong></div>
          <div><span>Mode</span><strong id="learning-studio-mode">operator</strong></div>
        </div>
      </article>

      <article class="overview-surface">
        <div class="overview-surface-title"><div><span>BOUNDARY</span><h3>KI-Autorität</h3></div><strong>PROPOSAL ONLY</strong></div>
        <p>Erlaubt: Lernziel strukturieren, Quellen/Partitionen prüfen, Baseline, Kontrollen, Evaluation und Stop-Kriterien vorschlagen.</p>
        <p><strong>Nicht erlaubt:</strong> Synapsengewichte, Spikefolgen, Strominjektionen, Eligibility-Zustände, Plasticity-Updates oder Rewardwerte vorgeben.</p>
      </article>
    </section>

    <section class="overview-operations-grid">
      <article class="overview-surface">
        <div class="overview-surface-title"><div><span>1–3</span><h3>Lernen vorbereiten</h3></div><strong>nicht ausführend</strong></div>
        <label class="input-label" for="learning-goal">Lernziel
          <textarea id="learning-goal" rows="4" placeholder="Beispiel: Lerne, ob eine eigene Aktion den erwarteten Umwelteffekt ausgelöst hat."></textarea>
        </label>
        <label class="input-label" for="learning-success-metric">Erfolgskriterium
          <input id="learning-success-metric" type="text" placeholder="z. B. Holdout task success / attribution accuracy" />
        </label>
        <label class="input-label" for="learning-source-notes">Quellen / Environment / Provenienz
          <textarea id="learning-source-notes" rows="4" placeholder="Welche kontrollierten Sensor-, Environment- oder Knowledge-Quellen sollen verwendet werden?"></textarea>
        </label>
        <label class="input-label" for="learning-constraints">Randbedingungen / Kontrollen
          <textarea id="learning-constraints" rows="3" placeholder="z. B. gleicher Seed, learning-off control, getrenntes Holdout, feste Episodenzahl"></textarea>
        </label>
        <label class="input-label" for="learning-context-length">KI-Kontextlänge
          <select id="learning-context-length"><option value="8000">8.000 Zeichen</option><option value="16000">16.000 Zeichen</option><option value="24000" selected>24.000 Zeichen</option><option value="48000">48.000 Zeichen</option></select>
        </label>
        <div class="overview-actions">
          <button id="learning-ai-prepare" class="overview-action" type="button">✦ KI-Vorbereitung erstellen</button>
          <button id="learning-run" class="overview-action" type="button">Lernlauf starten</button>
          <button id="learning-clear-proposal" class="overview-action" type="button">Zurücksetzen</button>
        </div>
        <small>Die Schaltfläche ruft den bestehenden read-only Research Assistant auf. Sie startet keinen Lauf und ändert keine Lernparameter.</small>
      </article>

      <article class="overview-surface">
        <div class="overview-surface-title"><div><span>AI PROPOSAL</span><h3>Vorbereitungsentwurf</h3></div><strong id="learning-ai-status">not requested</strong></div>
        <pre id="learning-ai-proposal" style="white-space:pre-wrap;overflow-wrap:anywhere;min-height:18rem;">Noch kein KI-Vorschlag erstellt.</pre>
      </article>
    </section>

    <section class="overview-operations-grid">
      <article class="overview-surface">
        <div class="overview-surface-title"><div><span>DIAGNOSTIK</span><h3>Pre / Post Learning</h3></div><strong>secondary measures</strong></div>
        <div class="overview-dynamics-grid">
          <div><span>Pre Task Baseline</span><strong>required</strong></div>
          <div><span>Pre Impulse Probe</span><strong>optional</strong></div>
          <div><span>Temporal Reference</span><strong>optional</strong></div>
          <div><span>Post Task Evaluation</span><strong>required</strong></div>
          <div><span>Post Impulse Probe</span><strong>optional</strong></div>
          <div><span>Holdout / Generalization</span><strong>required for claim</strong></div>
        </div>
        <p>Eine veränderte NetworkResponseSignature oder TemporalDiscrepancy ist allein noch kein Lernerfolg. Primär zählt die preregistrierte Aufgabenleistung gegenüber Kontrollen.</p>
      </article>
    </section>
  `;

  const research = byId("tab-research");
  if (research) main.insertBefore(section, research);
  else main.append(section);

  byId("learning-ai-prepare")?.addEventListener("click", prepareWithAI);
  byId("learning-run")?.addEventListener("click", runLearning);
  byId("learning-clear-proposal")?.addEventListener("click", () => {
    ["learning-goal", "learning-success-metric", "learning-source-notes", "learning-constraints"].forEach((id) => {
      const field = byId(id);
      if (field) field.value = "";
    });
    setText("learning-ai-status", "not requested");
    setText("learning-ai-proposal", "Noch kein KI-Vorschlag erstellt.");
  });
}

function learningPrompt() {
  const goal = byId("learning-goal")?.value?.trim() || "";
  const metric = byId("learning-success-metric")?.value?.trim() || "not specified";
  const sources = byId("learning-source-notes")?.value?.trim() || "not specified";
  const controls = byId("learning-constraints")?.value?.trim() || "not specified";
  const contextLength = Number(byId("learning-context-length")?.value || 24000);
  const learning = currentState.learning || {};
  const mode = currentState.experiment_state?.current_mode || currentState.experiment_state?.mode || "operator";

  return `You are preparing a Brain-5D learning experiment. Produce a proposal only; do not execute anything.\n\nLearning goal: ${goal}\nSuccess metric: ${metric}\nSources/environment/provenance: ${sources}\nControls/constraints: ${controls}\nRequested context length: ${contextLength} characters\nCurrent mode: ${mode}\nCurrent learning status: STDP enabled=${Boolean(learning.stdp_enabled)}, eligibility enabled=${Boolean(learning.eligibility_enabled)}, reward enabled=${Boolean(learning.reward_enabled)}.\n\nReturn a concise preparation proposal with exactly these sections: Objective, Source and partition plan, Pre-learning baseline, Exposure plan at task/environment level, Controls, Evaluation and holdout, Stopping rule, Confounds and safety, Required human decisions.\n\nHard boundary: never provide synaptic weights, a weight matrix, target spike trains/patterns, injected-current values/arrays, eligibility traces, direct plasticity updates, or reward values. Do not propose that the LLM writes a neural representation. The SNN must form its own representation through the registered environment and LearningEngine. Label the result AI PROPOSAL — NOT APPLIED.`;
}

async function prepareWithAI() {
  const goal = byId("learning-goal")?.value?.trim();
  if (!goal) {
    setText("learning-ai-status", "goal required");
    setText("learning-ai-proposal", "Bitte zuerst ein Lernziel formulieren.");
    return;
  }

  const button = byId("learning-ai-prepare");
  if (button) button.disabled = true;
  setText("learning-ai-status", "preparing");
  setText("learning-ai-proposal", "KI erstellt einen proposal-only Vorbereitungsentwurf …");

  try {
    const response = await fetch("/api/research/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "ask",
        message: learningPrompt(),
        response_mode: "scientific",
        web_search: false,
        max_context_chars: Number(byId("learning-context-length")?.value || 24000),
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    setText("learning-ai-status", "AI PROPOSAL · NOT APPLIED");
    setText("learning-ai-proposal", payload.answer || "Keine Antwort geliefert.");
  } catch (error) {
    setText("learning-ai-status", "unavailable");
    setText("learning-ai-proposal", `KI-Vorbereitung nicht verfügbar: ${error.message}`);
  } finally {
    if (button) button.disabled = false;
  }
}

async function runLearning() {
  const goal = byId("learning-goal")?.value?.trim();
  const metric = byId("learning-success-metric")?.value?.trim();
  if (!goal || !metric) {
    setText("learning-ai-status", "goal and metric required");
    setText("learning-ai-proposal", "Lernziel und Erfolgskriterium sind vor dem Lernlauf erforderlich.");
    return;
  }
  const button = byId("learning-run");
  if (button) button.disabled = true;
  setText("learning-ai-status", "running registered learning workflow");
  setText("learning-ai-proposal", "Lernlauf wird ausgeführt; KI-Ausgabe und Freitext werden nicht als Lernparameter verwendet.");
  const suffix = `${Date.now()}`.slice(-10);
  try {
    const response = await fetch("/api/learning/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        operator_confirmed: true,
        experiment_id: `EXP-LEARN-${suffix}`,
        question_id: "RQ-SNN-005",
        hypothesis_id: "H-SNN-005-A",
        title: goal,
        conditions: `success_metric=${metric}; ${byId("learning-constraints")?.value?.trim() || "operator-defined controls"}`,
        ticks: 100,
        notes: `Sources/provenance: ${byId("learning-source-notes")?.value?.trim() || "not specified"}`,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    setText("learning-ai-status", "learning completed · data recorded");
    setText("learning-ai-proposal", JSON.stringify(payload, null, 2));
  } catch (error) {
    setText("learning-ai-status", "learning unavailable");
    setText("learning-ai-proposal", `Lernlauf nicht verfügbar: ${error.message}`);
  } finally {
    if (button) button.disabled = false;
  }
}

export function ensureLearningStudio() {
  createLearningTabButton();
  createLearningWorkspace();
}

export function renderLearningStudio(state) {
  currentState = state || {};
  ensureLearningStudio();

  const learning = state?.learning || {};
  const knowledge = state?.knowledge_intake || {};
  const experiment = state?.experiment_state || {};
  const activeSession = experiment.active_session || null;

  setText("learning-studio-engine", learning.engine_attached ? "ACTIVE" : "UNAVAILABLE");
  setText(
    "learning-studio-stdp",
    learning.stdp_enabled ? (Number(learning.stdp_updates || 0) > 0 ? "ACTIVE" : "ARMED") : "DISABLED",
  );
  setText(
    "learning-studio-reward",
    learning.reward_enabled ? (Number(learning.reward_updates || 0) > 0 ? "ACTIVE" : "ARMED") : "DISABLED",
  );
  setText("learning-studio-session", activeSession?.session_id || "none");
  setText("learning-studio-learning-ms", `${Number(learning.update_ms || 0).toFixed(3)} ms`);
  setText("learning-studio-stdp-updates", Number(learning.stdp_updates || 0).toLocaleString());
  setText("learning-studio-reward-updates", Number(learning.reward_updates || 0).toLocaleString());
  setText(
    "learning-studio-rewards",
    `${Number(learning.rewards_applied || 0).toLocaleString()} / ${Number(learning.rewards_received || 0).toLocaleString()}`,
  );
  setText("learning-studio-pending", Number(learning.pending_rewards || 0).toLocaleString());
  setText("learning-studio-knowledge", Number(knowledge.items_processed || 0).toLocaleString());
  setText("learning-studio-mode", experiment.current_mode || experiment.mode || "operator");
}
