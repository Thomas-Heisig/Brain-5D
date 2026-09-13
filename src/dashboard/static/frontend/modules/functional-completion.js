"use strict";

const VIEWER_PROFILE_KEY = "mhrn.neuron-model-viewer.profile.v1";
const RATE_REFRESH_MS = 5000;
const EMBODIMENT_REFRESH_MS = 3000;

let initialized = false;
let viewerTimer = null;
let embodimentTimer = null;
let rootObserver = null;
let feedbackObserver = null;
let cachedEmbodimentState = null;
let cachedPipelineState = null;
let viewerProfileRestored = false;

const byId = (id) => document.getElementById(id);

async function readJson(url) {
  const response = await fetch(url, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function finite(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatRate(value) {
  if (!Number.isFinite(value)) return "—";
  if (value >= 100) return `${value.toFixed(1)} Hz`;
  if (value >= 10) return `${value.toFixed(2)} Hz`;
  return `${value.toFixed(3)} Hz`;
}

function findViewerStat(label) {
  return [...document.querySelectorAll("#neuron-model-viewer .nmv-stat")]
    .find((node) => node.querySelector("span")?.textContent?.trim() === label) || null;
}

function ensureViewerCompletionSurfaces() {
  const viewer = byId("neuron-model-viewer");
  if (!viewer) return false;

  const rateStat = findViewerStat("Per-neuron Hz");
  if (rateStat) {
    const strong = rateStat.querySelector("strong");
    if (strong) {
      strong.id = "nmv-rate-summary";
      strong.classList.remove("nmv-pending");
      if (!strong.dataset.completed) {
        strong.textContent = "Messfenster wird geladen …";
        strong.dataset.completed = "true";
      }
    }
    const label = rateStat.querySelector("span");
    if (label) {
      label.textContent = "Per-neuron Hz · kumulativ";
      label.title = "Kumulative Feuerrate seit Runtime-Start. Berechnet aus realem Spike-Counter und 1-ms Referenz-Ticks; keine Instantanrate.";
    }
  }

  const profileStat = findViewerStat("Profil-Cache");
  if (profileStat) {
    const label = profileStat.querySelector("span");
    const strong = profileStat.querySelector("strong");
    if (label) {
      label.textContent = "Ansichtsprofil";
      label.title = "Lokaler presentation-only Zustand des Viewers. Keine wissenschaftlichen Daten und keine Evidenz.";
    }
    if (strong) {
      strong.id = "nmv-profile-status";
      strong.classList.remove("nmv-pending");
      if (!strong.dataset.completed) {
        strong.textContent = "lokal · presentation-only";
        strong.dataset.completed = "true";
      }
    }
  }

  const legend = viewer.querySelector(".nmv-legend");
  if (legend && !legend.dataset.rateCompleted) {
    legend.dataset.rateCompleted = "true";
    legend.childNodes[0].textContent = "Feuerrate · kumulativ ";
    legend.title = "Die bestehende Activity-Farbskala ist bei festem Beobachtungsfenster monoton äquivalent zur kumulativen Feuerrate.";
  }

  bindViewerProfile();
  restoreViewerProfile();
  return true;
}

async function refreshNeuronRates() {
  if (!ensureViewerCompletionSurfaces()) return;
  const output = byId("nmv-rate-summary");
  if (!output) return;

  const sampleControl = byId("nmv-sample");
  const requested = Math.max(1, Math.min(2000, Number(sampleControl?.value || 500)));

  try {
    const [summary, projection] = await Promise.all([
      readJson("/api/network/summary"),
      readJson(`/api/network/projection?limit=${requested}&mode=activity`),
    ]);
    const tick = finite(summary.current_tick);
    const dtMs = 1.0; // Reference core invariant: SimulationConfig enforces dt_ms == 1.0.
    if (tick === null || tick <= 0) {
      output.textContent = "noch kein Messfenster · Tick 0";
      output.title = "Eine Feuerrate benötigt ein positives Beobachtungsfenster.";
      return;
    }

    const durationSeconds = tick * dtMs / 1000;
    const rates = (projection.points || [])
      .map((point) => finite(point.value))
      .filter((value) => value !== null)
      .map((spikeCount) => spikeCount / durationSeconds);

    if (!rates.length) {
      output.textContent = "keine Neuronendaten";
      return;
    }

    const mean = rates.reduce((sum, value) => sum + value, 0) / rates.length;
    const minimum = Math.min(...rates);
    const maximum = Math.max(...rates);
    output.textContent = `μ ${formatRate(mean)} · ${formatRate(minimum)}–${formatRate(maximum)} · n=${rates.length}`;
    output.title = `Kumulative Feuerrate über ${tick.toLocaleString("de-DE")} Ticks (${durationSeconds.toFixed(3)} s). Quelle: /api/network/summary + deterministische /api/network/projection Stichprobe. Kein EVIDENCE-Claim.`;
  } catch (error) {
    output.textContent = `nicht verfügbar · ${error.message}`;
    output.title = "Live-Raten konnten nicht aus den Runtime-Endpunkten berechnet werden.";
  }
}

function readViewerProfile() {
  try {
    const value = JSON.parse(localStorage.getItem(VIEWER_PROFILE_KEY) || "null");
    return value && typeof value === "object" ? value : null;
  } catch (_) {
    return null;
  }
}

function currentViewerProfile() {
  return {
    version: 1,
    method: byId("nmv-method")?.value || "pca",
    dimensions: byId("nmv-dim")?.value || "2",
    sample: byId("nmv-sample")?.value || "500",
    interval: byId("nmv-interval")?.value || "0",
    view: document.querySelector("#neuron-model-viewer [data-nmv-view].active")?.dataset.nmvView || "projection",
    saved_at: new Date().toISOString(),
    scope: "presentation_only",
  };
}

function setProfileStatus(message, title = "") {
  const node = byId("nmv-profile-status");
  if (!node) return;
  node.textContent = message;
  node.title = title || "Lokales Ansichtsprofil; verändert keine Runtime- oder Forschungsdaten.";
}

function saveViewerProfile() {
  if (!byId("neuron-model-viewer")) return;
  try {
    const profile = currentViewerProfile();
    localStorage.setItem(VIEWER_PROFILE_KEY, JSON.stringify(profile));
    setProfileStatus("gespeichert · lokal", `Gespeichert ${new Date(profile.saved_at).toLocaleString("de-DE")} · presentation-only`);
  } catch (error) {
    setProfileStatus("Speicher nicht verfügbar", String(error.message || error));
  }
}

function dispatchChange(control) {
  control?.dispatchEvent(new Event("change", { bubbles: true }));
}

function restoreViewerProfile() {
  if (viewerProfileRestored || !byId("neuron-model-viewer")) return;
  viewerProfileRestored = true;
  const profile = readViewerProfile();
  if (!profile) {
    setProfileStatus("bereit · lokal", "Noch kein Ansichtsprofil gespeichert. Änderungen werden automatisch lokal gespeichert.");
    return;
  }

  const method = byId("nmv-method");
  if (method && [...method.options].some((option) => option.value === profile.method)) {
    method.value = profile.method;
    // Do not auto-run an expensive analysis job on page load. The restored
    // method is used on the next explicit refresh.
  }
  const dimensions = byId("nmv-dim");
  if (dimensions && [...dimensions.options].some((option) => option.value === String(profile.dimensions))) {
    dimensions.value = String(profile.dimensions);
    dispatchChange(dimensions);
  }
  const sample = byId("nmv-sample");
  if (sample && [...sample.options].some((option) => option.value === String(profile.sample))) {
    sample.value = String(profile.sample);
    dispatchChange(sample);
  }
  const interval = byId("nmv-interval");
  if (interval && [...interval.options].some((option) => option.value === String(profile.interval))) {
    interval.value = String(profile.interval);
    dispatchChange(interval);
  }
  const view = document.querySelector(`#neuron-model-viewer [data-nmv-view="${CSS.escape(String(profile.view || "projection"))}"]`);
  view?.click();
  setProfileStatus("wiederhergestellt · lokal", "Presentation-only Ansichtsprofil aus localStorage wiederhergestellt.");
}

function bindViewerProfile() {
  const viewer = byId("neuron-model-viewer");
  if (!viewer || viewer.dataset.profileCompletionBound === "true") return;
  viewer.dataset.profileCompletionBound = "true";
  ["nmv-method", "nmv-dim", "nmv-sample", "nmv-interval"].forEach((id) => {
    byId(id)?.addEventListener("change", () => {
      saveViewerProfile();
      if (id === "nmv-sample") refreshNeuronRates();
    });
  });
  viewer.querySelector(".nmv-view-tabs")?.addEventListener("click", (event) => {
    if (event.target.closest("[data-nmv-view]")) queueMicrotask(saveViewerProfile);
  });
}

function feedbackStatus(pipeline, state) {
  if (state?.last_observation_state) return {
    text: "observation received",
    title: `Rückkopplung gemessen: ${String(state.last_observation_state)}`,
  };

  const stage = pipeline?.stages?.feedback;
  if (!stage) return {
    text: "state unknown",
    title: "Der Pipeline-Vertrag hat keinen Feedback-Status geliefert.",
  };
  if (stage.implemented === false) return {
    text: "adapter feedback unavailable",
    title: "Die aktuelle Adapter-/Runtime-Konfiguration veröffentlicht noch keinen implementierten Feedback-Pfad. Der Zustand wird nicht als funktionierend dargestellt.",
  };
  if (stage.enabled) return {
    text: "enabled · waiting for observation",
    title: "Feedback-Pipeline ist freigegeben; noch keine EnvironmentObservation empfangen.",
  };
  return {
    text: "ready · disabled",
    title: "Feedback-Pipeline ist implementiert, aktuell aber deaktiviert.",
  };
}

function renderEmbodimentFeedback() {
  const node = byId("embodiment-feedback-state");
  if (!node) return;
  const status = feedbackStatus(cachedPipelineState, cachedEmbodimentState);
  if (node.textContent !== status.text) node.textContent = status.text;
  node.title = status.title;
  node.dataset.functionalState = status.text.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
}

async function refreshEmbodimentFeedback() {
  const node = byId("embodiment-feedback-state");
  if (!node) return;
  try {
    const [pipeline, state] = await Promise.all([
      readJson("/api/embodiment/pipeline"),
      readJson("/api/embodiment/state"),
    ]);
    cachedPipelineState = pipeline;
    cachedEmbodimentState = state;
    renderEmbodimentFeedback();
  } catch (error) {
    node.textContent = "state unavailable";
    node.title = `Embodiment-Status nicht erreichbar: ${error.message}`;
  }
}

function bindFeedbackObserver() {
  const node = byId("embodiment-feedback-state");
  if (!node || feedbackObserver) return;
  if (/not implemented/i.test(node.textContent || "")) node.textContent = "state wird geprüft …";
  feedbackObserver = new MutationObserver(() => {
    if (cachedPipelineState || cachedEmbodimentState) renderEmbodimentFeedback();
  });
  feedbackObserver.observe(node, { childList: true, characterData: true, subtree: true });
}

function annotateGuardedDisabledControls() {
  const experimentStop = byId("experiment-stop");
  if (experimentStop?.disabled && !experimentStop.title) {
    experimentStop.title = "Wird automatisch aktiviert, sobald eine Experiment-Session aktiv ist.";
  }

  document.querySelectorAll("button:disabled, input:disabled, select:disabled, option:disabled").forEach((control) => {
    if (!control.title && control.getAttribute("aria-label")) control.title = control.getAttribute("aria-label");
  });
}

function refreshFunctionalSurfaces() {
  ensureViewerCompletionSurfaces();
  bindFeedbackObserver();
  annotateGuardedDisabledControls();
}

export function initFunctionalCompletion() {
  if (initialized) {
    refreshFunctionalSurfaces();
    refreshNeuronRates();
    refreshEmbodimentFeedback();
    return;
  }
  initialized = true;
  refreshFunctionalSurfaces();
  refreshNeuronRates();
  refreshEmbodimentFeedback();

  rootObserver = new MutationObserver(() => refreshFunctionalSurfaces());
  rootObserver.observe(document.querySelector("main") || document.body, { childList: true, subtree: true });

  viewerTimer = window.setInterval(refreshNeuronRates, RATE_REFRESH_MS);
  embodimentTimer = window.setInterval(refreshEmbodimentFeedback, EMBODIMENT_REFRESH_MS);

  window.addEventListener("beforeunload", () => {
    if (viewerTimer) clearInterval(viewerTimer);
    if (embodimentTimer) clearInterval(embodimentTimer);
    rootObserver?.disconnect();
    feedbackObserver?.disconnect();
  }, { once: true });

  window.MHRNFunctionalCompletion = {
    refresh: () => {
      refreshFunctionalSurfaces();
      refreshNeuronRates();
      refreshEmbodimentFeedback();
    },
    viewerProfileKey: VIEWER_PROFILE_KEY,
  };
}
