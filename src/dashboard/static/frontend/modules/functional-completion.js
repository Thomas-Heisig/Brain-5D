"use strict";

const VIEWER_PROFILE_KEY = "mhrn.neuron-model-viewer.profile.v1";
const RATE_REFRESH_MS = 5000;
const EMBODIMENT_REFRESH_MS = 3000;

let initialized = false;
let viewerTimer = null;
let embodimentTimer = null;
let rootObserver = null;
let profileRestored = false;

const byId = (id) => document.getElementById(id);

async function readJson(url) {
  const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function finite(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
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

function setProfileStatus(text, title = "") {
  const node = byId("nmv-profile-status");
  if (!node) return;
  if (node.textContent !== text) node.textContent = text;
  node.title = title || "Lokales presentation-only Ansichtsprofil; keine Runtime- oder Evidenzdaten.";
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

function restoreViewerProfile() {
  if (profileRestored || !byId("neuron-model-viewer")) return;
  profileRestored = true;
  let profile = null;
  try { profile = JSON.parse(localStorage.getItem(VIEWER_PROFILE_KEY) || "null"); } catch (_) {}
  if (!profile || typeof profile !== "object") {
    setProfileStatus("bereit · lokal", "Noch kein Ansichtsprofil gespeichert. Änderungen werden automatisch lokal gespeichert.");
    return;
  }

  const assign = (id, value, emit = true) => {
    const control = byId(id);
    if (!control || ![...control.options].some((option) => option.value === String(value))) return;
    control.value = String(value);
    if (emit) control.dispatchEvent(new Event("change", { bubbles: true }));
  };
  // Method is restored without firing change: nonlinear backend jobs must never
  // start merely because the page was opened.
  assign("nmv-method", profile.method || "pca", false);
  assign("nmv-dim", profile.dimensions || "2");
  assign("nmv-sample", profile.sample || "500");
  assign("nmv-interval", profile.interval || "0");
  const view = document.querySelector(`#neuron-model-viewer [data-nmv-view="${CSS.escape(String(profile.view || "projection"))}"]`);
  view?.click();
  setProfileStatus("wiederhergestellt · lokal", "Presentation-only Ansichtsprofil aus localStorage wiederhergestellt.");
}

function bindViewerProfile(viewer) {
  if (viewer.dataset.functionalCompletionBound === "true") return;
  viewer.dataset.functionalCompletionBound = "true";
  ["nmv-method", "nmv-dim", "nmv-sample", "nmv-interval"].forEach((id) => {
    byId(id)?.addEventListener("change", () => {
      saveViewerProfile();
      if (id === "nmv-sample") void refreshNeuronRates();
    });
  });
  viewer.querySelector(".nmv-view-tabs")?.addEventListener("click", (event) => {
    if (event.target.closest("[data-nmv-view]")) queueMicrotask(saveViewerProfile);
  });
}

function ensureViewerCompletion() {
  const viewer = byId("neuron-model-viewer");
  if (!viewer) return false;
  if (viewer.dataset.functionalCompletionReady === "true") return true;

  const rateStat = findViewerStat("Per-neuron Hz");
  if (rateStat) {
    const label = rateStat.querySelector("span");
    const value = rateStat.querySelector("strong");
    if (label) {
      label.textContent = "Per-neuron Hz · kumulativ";
      label.title = "Kumulative Feuerrate seit Runtime-Start; keine Instantanrate.";
    }
    if (value) {
      value.id = "nmv-rate-summary";
      value.classList.remove("nmv-pending");
      value.textContent = "Messfenster wird geladen …";
    }
  }

  const profileStat = findViewerStat("Profil-Cache");
  if (profileStat) {
    const label = profileStat.querySelector("span");
    const value = profileStat.querySelector("strong");
    if (label) {
      label.textContent = "Ansichtsprofil";
      label.title = "Presentation-only Zustand des Viewers; keine wissenschaftlichen Daten.";
    }
    if (value) {
      value.id = "nmv-profile-status";
      value.classList.remove("nmv-pending");
      value.textContent = "lokal · presentation-only";
    }
  }

  const legend = viewer.querySelector(".nmv-legend");
  if (legend) {
    const marker = legend.querySelector("i");
    legend.replaceChildren(document.createTextNode("Feuerrate · kumulativ "));
    if (marker) legend.append(marker);
    legend.title = "Bei festem Beobachtungsfenster ist die Spike-Counter-Farbskala monoton äquivalent zur kumulativen Feuerrate.";
  }

  bindViewerProfile(viewer);
  restoreViewerProfile();
  viewer.dataset.functionalCompletionReady = "true";
  return true;
}

async function refreshNeuronRates() {
  if (!ensureViewerCompletion()) return;
  const output = byId("nmv-rate-summary");
  if (!output) return;
  const requested = Math.max(1, Math.min(2000, Number(byId("nmv-sample")?.value || 500)));

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
    output.textContent = `μ ${formatRate(mean)} · ${formatRate(Math.min(...rates))}–${formatRate(Math.max(...rates))} · n=${rates.length}`;
    output.title = `Kumulative Feuerrate über ${tick.toLocaleString("de-DE")} Ticks (${durationSeconds.toFixed(3)} s). Quelle: Live-Runtime. Kein EVIDENCE-Claim.`;
  } catch (error) {
    output.textContent = `nicht verfügbar · ${error.message}`;
    output.title = "Live-Raten konnten nicht aus den Runtime-Endpunkten berechnet werden.";
  }
}

function feedbackStatus(pipeline, state) {
  if (state?.last_observation_state) return ["observation received", `Rückkopplung gemessen: ${state.last_observation_state}`];
  const stage = pipeline?.stages?.feedback;
  if (!stage) return ["state unknown", "Der Pipeline-Vertrag hat keinen Feedback-Status geliefert."];
  if (stage.implemented === false) return ["adapter feedback unavailable", "Die aktuelle Adapter-/Runtime-Konfiguration veröffentlicht keinen implementierten Feedback-Pfad."];
  if (stage.enabled) return ["enabled · waiting for observation", "Feedback-Pipeline ist freigegeben; noch keine EnvironmentObservation empfangen."];
  return ["ready · disabled", "Feedback-Pipeline ist implementiert, aktuell aber deaktiviert."];
}

async function refreshEmbodimentFeedback() {
  const node = byId("embodiment-feedback-state");
  if (!node) return;
  try {
    const [pipeline, state] = await Promise.all([
      readJson("/api/embodiment/pipeline"),
      readJson("/api/embodiment/state"),
    ]);
    const [text, title] = feedbackStatus(pipeline, state);
    if (node.textContent !== text) node.textContent = text;
    node.title = title;
    node.dataset.functionalState = text.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
  } catch (error) {
    if (node.textContent !== "state unavailable") node.textContent = "state unavailable";
    node.title = `Embodiment-Status nicht erreichbar: ${error.message}`;
  }
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

function scanDynamicSurfaces() {
  ensureViewerCompletion();
  annotateGuardedDisabledControls();
}

export function initFunctionalCompletion() {
  if (initialized) {
    scanDynamicSurfaces();
    void refreshNeuronRates();
    void refreshEmbodimentFeedback();
    return;
  }
  initialized = true;
  scanDynamicSurfaces();
  void refreshNeuronRates();
  void refreshEmbodimentFeedback();

  rootObserver = new MutationObserver(() => {
    if (!byId("neuron-model-viewer")?.dataset.functionalCompletionReady) scanDynamicSurfaces();
  });
  rootObserver.observe(document.querySelector("main") || document.body, { childList: true, subtree: true });

  viewerTimer = window.setInterval(refreshNeuronRates, RATE_REFRESH_MS);
  embodimentTimer = window.setInterval(refreshEmbodimentFeedback, EMBODIMENT_REFRESH_MS);
  window.addEventListener("beforeunload", () => {
    if (viewerTimer) clearInterval(viewerTimer);
    if (embodimentTimer) clearInterval(embodimentTimer);
    rootObserver?.disconnect();
  }, { once: true });

  window.MHRNFunctionalCompletion = {
    refresh: () => {
      scanDynamicSurfaces();
      void refreshNeuronRates();
      void refreshEmbodimentFeedback();
    },
    viewerProfileKey: VIEWER_PROFILE_KEY,
  };
}
