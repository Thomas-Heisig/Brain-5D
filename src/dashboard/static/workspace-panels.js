/**
 * Shared workbench summaries for Network, Control, Research, Release and Settings.
 */

"use strict";

const byId = (id) => document.getElementById(id);

function setText(id, value) {
  const element = byId(id);
  if (element) element.textContent = String(value ?? "—");
}

function formatNumber(value) {
  if (value === null || value === undefined) return "—";
  return Number(value).toLocaleString();
}

function formatFixed(value, digits = 3, suffix = "") {
  if (value === null || value === undefined) return "—";
  return `${Number(value).toFixed(digits)}${suffix}`;
}

function formatBytes(value) {
  if (value === null || value === undefined) return "—";
  const bytes = Number(value);
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MiB`;
}

function detailValue(value) {
  if (value === null || value === undefined || value === "" || value === "not_reported" || value === "unavailable") {
    return "nicht implementiert / nicht geliefert";
  }
  if (Array.isArray(value)) return value.length ? value.join(" · ") : "keine Daten geliefert";
  if (typeof value === "boolean") return value ? "ja" : "nein";
  return String(value);
}

function openEmbodimentDetail(title, summary, fields, source = "aktueller Dashboard-Snapshot") {
  const modal = byId("embodiment-detail-modal");
  const list = byId("embodiment-detail-fields");
  if (!modal || !list) return;
  byId("embodiment-detail-title").textContent = title;
  byId("embodiment-detail-summary").textContent = summary;
  list.replaceChildren();
  for (const [label, value] of fields) {
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = detailValue(value);
    list.append(term, description);
  }
  byId("embodiment-detail-source").textContent = `Quelle: ${source}`;
  modal.hidden = false;
}

function readElement(id) {
  return byId(id)?.textContent || null;
}

function showEmbodimentGroup(key) {
  const groups = {
    senses: ["Sinne / Eingänge", "Nur aktuell publizierte Wahrnehmungsdaten.", [["Verbundene Sinne", readElement("being-sensors")], ["Letztes Signal", readElement("embodiment-last-text")], ["Umgebung", readElement("being-environment")], ["Sensorwerte", readElement("embodiment-sensor-detail")], ["Rückkopplung", readElement("embodiment-feedback-state")], ["Status", readElement("embodiment-sensor-state")]]],
    brain: ["Gehirn / neuronale Datenbank", "Der zentrale neuronale Zustand des aktuellen Snapshots.", [["Tick", readElement("being-tick")], ["Neuronen", readElement("being-neurons")], ["Synapsen", readElement("being-synapses")], ["Aktive Neuronen", readElement("being-active")], ["E/I-Ratio", readElement("being-ei-ratio")], ["Systemstatus", readElement("being-system-status")]]],
    inner: ["Innere Zustände", "Gemessene Dynamik und Regulation; keine psychischen Zustände werden behauptet.", [["Homöostase", readElement("being-homeostasis")], ["Energie", readElement("being-energy")], ["Feuerrate", readElement("being-rate")], ["Synchronität", readElement("being-synchrony")], ["Burst-Index", readElement("being-burst")], ["STDP-Updates", readElement("being-stdp")], ["Rate-Fehler", readElement("being-rate-error")], ["Threshold", readElement("being-threshold")]]],
    actuators: ["Extremitäten / Ausgänge", "Nur tatsächlich publizierte Aktions- und Aktorinformationen.", [["Verbundene Aktoren", readElement("being-actuators")], ["Letzte Aktion", readElement("embodiment-action-detail")], ["Aktorwerte", readElement("embodiment-actuator-detail")], ["Reward", readElement("embodiment-last-reward")], ["Status", readElement("embodiment-actuator-state")]]],
    signal: ["Signal-Brücke", "Interne Signalverarbeitung aus dem aktuellen Snapshot.", [["Frames", readElement("being-signal-frames")], ["Regionen", readElement("being-signal-regions")], ["Rohdaten", null]]],
    language: ["Sprachorgan", "Ein Sprachadapter ist nur vorhanden, wenn sein Status dies meldet.", [["Status", readElement("being-language-state")], ["Modell / Backend", readElement("being-language-model")], ["Ausgabeprotokoll", null]]],
    knowledge: ["Wissensaufnahme", "Publizierte Intake-Metriken ohne nicht belegte Inhalte.", [["Verarbeitete Elemente", readElement("being-knowledge-items")], ["Quellen", readElement("being-knowledge-sources")], ["Inhaltsdetails", null]]],
    structure: ["Struktur", "Gemeldete strukturelle Veränderungen und Budgetwerte.", [["Änderungen", readElement("being-structural-changes")], ["Budget", readElement("being-growth-budget")], ["Vorschlagsdetails", null]]],
    storage: ["Speicher", "Nur der gemeldete Speicherstatus und seine Laufzeitwerte.", [["Status", readElement("being-storage-state")], ["Details", readElement("being-storage-detail")], ["Inhaltliche Daten", null]]],
    history: ["Loop-Evidenz", "Nur aufgezeichnete Verlaufssamples des Embodiment-Vertrags.", [["Status", readElement("embodiment-history-state")], ["Samples", readElement("embodiment-history-count")], ["Letzter Tick", readElement("embodiment-history-tick")]]],
    "adapter-loop": ["Adaptergruppe / geschlossener Loop", "Die Environment-Beobachtung ist die Rückkopplung nach der Aktion; Eigenhören und Eigenbild benötigen noch reale Sensoradapter.", [["Environment", readElement("embodiment-loop-environment")], ["Sensor", readElement("embodiment-loop-sensor")], ["Encoder", readElement("embodiment-loop-encoder")], ["SNN", readElement("embodiment-loop-snn")], ["Decoder", readElement("embodiment-loop-decoder")], ["Actuator", readElement("embodiment-loop-actuator")], ["Vertragsnotiz", readElement("embodiment-contract-note")]]],
  };
  const group = groups[key];
  if (group) openEmbodimentDetail(group[0], group[1], group[2]);
}

export function initEmbodimentDetails() {
  const modal = byId("embodiment-detail-modal");
  if (!modal || modal.dataset.initialized) return;
  modal.dataset.initialized = "true";
  const close = () => { modal.hidden = true; };
  byId("embodiment-detail-close")?.addEventListener("click", close);
  byId("embodiment-detail-close-footer")?.addEventListener("click", close);
  modal.addEventListener("click", (event) => { if (event.target === modal) close(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
  document.querySelectorAll("[data-detail-key]").forEach((element) => {
    element.addEventListener("click", () => showEmbodimentGroup(element.dataset.detailKey));
    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); showEmbodimentGroup(element.dataset.detailKey); }
    });
  });
}

function clamp(value, minimum = 0, maximum = 1) {
  return Math.min(maximum, Math.max(minimum, Number(value) || 0));
}

async function setPipelineStage(stage, enabled, input) {
  try {
    const response = await fetch("/api/embodiment/pipeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stage, enabled }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    input.title = enabled ? "Pipeline-Stufe freigegeben" : "Pipeline-Stufe deaktiviert";
  } catch (error) {
    input.checked = !enabled;
    input.title = `Konfiguration nicht übernommen: ${error.message}`;
  }
}

function renderPipelineToggles(pipeline) {
  for (const input of document.querySelectorAll("[data-pipeline-toggle]")) {
    const stage = input.dataset.pipelineToggle;
    const state = pipeline?.stages?.[stage];
    if (!state) continue;
    input.checked = Boolean(state.enabled);
    input.dataset.implemented = String(Boolean(state.implemented));
    input.title = state.implemented ? "Implementierte Pipeline-Stufe" : "Noch nicht implementiert; Häkchen speichert nur Konfigurationsabsicht";
  }
}

export function initEmbodimentPipelineControls() {
  document.querySelectorAll("[data-pipeline-toggle]").forEach((input) => {
    input.addEventListener("click", (event) => event.stopPropagation());
    input.addEventListener("change", (event) => {
      event.stopPropagation();
      setPipelineStage(input.dataset.pipelineToggle, input.checked, input);
    });
  });
}

function renderConnections(payload) {
  const graph = byId("connection-graph");
  if (!graph) return;
  const connections = Array.isArray(payload.connections) ? payload.connections : [];
  setText("connection-available", payload.available || 0);
  setText("connection-authorized", payload.authorized || 0);
  setText("connection-active", payload.active || 0);
  graph.replaceChildren();
  if (!connections.length) {
    const empty = document.createElement("p");
    empty.className = "connection-empty";
    empty.textContent = "Keine Verbindungsdeskriptoren publiziert.";
    graph.append(empty);
    return;
  }
  for (const connection of connections) {
    const card = document.createElement("article");
    card.className = "connection-node";
    card.dataset.status = connection.status || "unavailable";
    card.dataset.kind = connection.kind || "data";
    card.setAttribute("role", "listitem");

    const heading = document.createElement("div");
    const indicator = document.createElement("i");
    indicator.setAttribute("aria-hidden", "true");
    const name = document.createElement("strong");
    name.textContent = connection.name || connection.connection_id;
    const kind = document.createElement("small");
    kind.textContent = connection.kind || "unknown";
    heading.append(indicator, name, kind);

    const relation = document.createElement("p");
    relation.textContent = `${connection.relationship || "perceivable"} · ${connection.status || "unavailable"}`;
    const capabilities = document.createElement("p");
    capabilities.className = "connection-capabilities";
    capabilities.textContent = Array.isArray(connection.capabilities) && connection.capabilities.length
      ? connection.capabilities.join(" · ")
      : "keine Fähigkeiten publiziert";
    const trust = document.createElement("span");
    trust.className = "connection-trust";
    trust.textContent = connection.authorized
      ? `autorisiert${connection.active ? " · aktiv" : ""}`
      : "nicht autorisiert";
    trust.title = connection.message || "";
    card.append(heading, relation, capabilities, trust);
    card.tabIndex = 0;
    card.setAttribute("aria-label", `Details für ${connection.name || connection.connection_id}`);
    const showConnection = () => openEmbodimentDetail(
      connection.name || connection.connection_id,
      "Echter Verbindungsdeskriptor aus der Adapter-Erkennung.",
      [["ID", connection.connection_id], ["Typ", connection.kind], ["Beziehung", connection.relationship], ["Status", connection.status], ["Fähigkeiten", connection.capabilities], ["Berechtigungen", connection.permissions], ["Modalitäten", connection.modalities], ["Verfügbar", connection.available], ["Autorisiert", connection.authorized], ["Aktiv", connection.active], ["Latenz (ms)", connection.latency_ms], ["Energiebedarf", connection.energy_demand], ["Gefahrenstufe", connection.hazard_level], ["Quelle", connection.source], ["Meldung", connection.message]],
      connection.source || "Embodiment connection API",
    );
    card.addEventListener("click", showConnection);
    card.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); showConnection(); } });
    graph.append(card);
  }
}

export function renderWorkspaceSummaries(state) {
  const system = state.system || {};
  const network = state.network || {};
  const gate = state.gate || {};
  const experiment = state.experiment_state || {};
  const research = state.research?.categories || {};
  const parameters = state.parameters || {};
  const pending = state.pending_changes || {};
  const embodiment = state.embodiment || {};
  const embodimentDetail = state.embodiment_detail || {};
  const embodimentHistory = state.embodiment_history || {};
  const embodimentConnections = state.embodiment_connections || {};
  const learning = state.learning || {};
  const storage = state.storage || {};
  const homeostasis = state.homeostasis || {};
  const structural = state.structural || {};
  const spikes = state.spikes || {};
  const languageOrgan = state.language_organ || {};
  const knowledge = state.knowledge_intake || {};
  const signals = state.signal_metrics || {};

  renderPipelineToggles(embodimentDetail.pipeline);

  setText("network-workspace-source", String(network.source || "live").replaceAll("_", " "));
  setText("network-workspace-tick", formatNumber(network.tick ?? system.tick));
  setText("network-workspace-active", formatNumber(network.active_neurons));
  setText("network-workspace-spikes", formatNumber(system.spikes_total));

  setText("control-workspace-state", state.status || "unknown");
  setText("control-workspace-tick", formatNumber(system.tick));
  setText("control-workspace-mode", experiment.current_mode || experiment.mode || "operator");
  setText("control-workspace-pending", Object.keys(pending).length);
  setText("runtime-tick", formatNumber(system.tick));
  setText("runtime-queued", formatNumber(state.runtime?.queued_ticks ?? state.runtime?.queue_depth ?? 0));
  setText("runtime-last-batch", formatNumber(state.runtime?.last_batch_ticks ?? 0));
  setText("runtime-last-ms", Number(state.runtime?.batch_duration_ms ?? system.core_step_ms ?? 0).toFixed(2));

  const activeSession = experiment.active_session || null;
  const footerExperiment = byId("footer-experiment");
  if (footerExperiment) footerExperiment.dataset.active = String(activeSession !== null);
  setText("footer-experiment-state", activeSession ? "running" : "inactive");
  setText("footer-experiment-id", activeSession?.session_id || "no session");

  setText("research-workspace-registry", formatNumber(research.registry));
  setText("research-workspace-experiments", formatNumber(research.experiments));
  setText("research-workspace-generated", formatNumber(research.generated));
  setText("research-workspace-schemas", formatNumber(research.schemas));

  const scientific = gate.scientific_gate?.overall || gate.overall || "unknown";
  const ci = gate.ci_status?.status || "unknown";
  const readiness = gate.release_readiness || {};
  setText("release-workspace-scientific", scientific);
  setText("release-workspace-ci", ci);
  setText("release-workspace-readiness", readiness.overall || "not_ready");
  setText("release-workspace-blockers", Array.isArray(readiness.blockers) ? readiness.blockers.length : 0);

  const values = Object.values(parameters);
  setText("settings-parameter-count", values.length);
  setText("settings-sensitive-count", values.filter((item) => item.scientific_sensitive).length);
  setText("settings-mutable-count", values.filter((item) => item.runtime_mutable).length);
  setText("settings-pending-count", Object.keys(pending).length);
  setText("settings-mode", experiment.current_mode || experiment.mode || "operator");
  setText("settings-session", activeSession?.session_id || "none");
  setText("settings-restart", Object.values(pending).some((item) => item.requires_restart) ? "yes" : "no");

  const environmentKind = embodiment.environment_kind || "unconfigured";
  const sensors = Number(embodiment.active_sensors || 0);
  const actuators = Number(embodiment.active_actuators || 0);
  setText("embodiment-kind", environmentKind);
  setText("embodiment-sensors", sensors);
  setText("embodiment-actuators", actuators);
  setText("embodiment-episode", embodiment.episode || 0);
  setText("embodiment-episode-reward", Number(embodiment.episode_reward || 0).toFixed(3));
  setText("embodiment-last-reward", Number(embodiment.last_reward || 0).toFixed(3));
  setText("embodiment-last-action", embodiment.last_action || "—");
  setText("embodiment-last-text", embodiment.last_text_input || "—");
  setText("embodiment-action-detail", embodiment.last_action || "—");
  setText("embodiment-sensor-state", sensors > 0 ? `${sensors} active` : "Not connected");
  setText("embodiment-actuator-state", actuators > 0 ? `${actuators} active` : "Not connected");
  setText(
    "embodiment-readiness",
    environmentKind === "unconfigured"
      ? "No environment adapter is configured. The tab exposes the real dashboard contract and will become active when runtime metrics are published."
      : `${environmentKind} environment connected with ${sensors} sensor(s) and ${actuators} actuator(s).`,
  );
  for (const phase of embodimentDetail.loop || []) {
    setText(`embodiment-loop-${phase.id}`, String(phase.status || "unknown").replaceAll("_", " "));
    const node = document.querySelector(`[data-loop-node="${phase.id}"]`);
    if (node) node.dataset.status = phase.status || "unknown";
  }
  setText("embodiment-sensor-detail", embodimentDetail.details?.sensor_values === null ? "not published" : "available");
  setText("embodiment-actuator-detail", embodimentDetail.details?.actuator_values === null ? "not published" : "available");
  setText("embodiment-feedback-state", embodiment.last_observation_state ? "observation received" : "not implemented");
  setText("embodiment-contract-note", embodimentDetail.details?.message || "Adapter detail contract not reported.");
  const history = Array.isArray(embodimentHistory.history) ? embodimentHistory.history : [];
  setText("embodiment-history-count", embodimentHistory.count || 0);
  setText("embodiment-history-state", embodimentHistory.available ? "measured" : "unavailable");
  setText("embodiment-history-tick", history[0]?.tick ?? "—");

  setText("being-tick", formatNumber(system.tick));
  setText("being-neurons", formatNumber(network.neuron_count ?? system.neurons));
  setText("being-synapses", formatNumber(network.synapse_count ?? system.synapses));
  setText("being-active", formatNumber(network.active_neurons ?? spikes.active_neurons));
  setText("being-ei-ratio", formatFixed(network.e_i_ratio, 2));
  setText("being-spikes", formatNumber(spikes.spike_count_last_tick ?? system.spikes_last_tick));
  setText("being-rate", formatFixed(spikes.mean_firing_rate_hz ?? network.mean_firing_rate_hz, 2, " Hz"));
  setText("being-burst", formatFixed(spikes.burst_index ?? network.burst_index));
  setText("being-synchrony", formatFixed(spikes.synchrony ?? network.synchrony));
  setText("being-homeostasis", homeostasis.enabled ? "active" : "disabled");
  setText("being-energy", formatFixed(homeostasis.mean_energy ?? network.mean_energy ?? system.mean_energy));
  setText("being-rate-error", formatFixed(homeostasis.mean_rate_error_hz ?? homeostasis.rate_error_hz, 3, " Hz"));
  setText("being-threshold", formatFixed(homeostasis.mean_threshold_adaptation));

  setText("being-sensors", sensors);
  setText("being-actuators", actuators);
  setText("being-environment", environmentKind);
  setText("being-stdp", formatNumber(learning.stdp_updates));
  setText("being-reward-updates", formatNumber(learning.reward_updates));
  setText("being-pending-rewards", formatNumber(learning.pending_rewards));
  setText("being-signal-frames", `${formatNumber(signals.frames_processed)} frames`);
  setText("being-signal-regions", `${formatNumber(signals.active_regions)} Regionen`);
  setText("being-language-state", !languageOrgan.enabled ? "disabled" : languageOrgan.active ? "active" : "idle");
  setText("being-language-model", languageOrgan.model_name || languageOrgan.backend_type || "kein Modell");
  setText("being-knowledge-items", `${formatNumber(knowledge.items_processed)} verarbeitet`);
  setText("being-knowledge-sources", `${formatNumber(knowledge.active_sources)} Quellen`);
  setText("being-structural-changes", `${formatNumber(structural.structural_changes)} Änderungen`);
  setText("being-growth-budget", `${formatFixed(structural.used_budget, 1)} / ${formatFixed(structural.growth_budget, 1)} Budget`);
  setText("being-storage-state", storage.available ? (storage.worker_failed ? "failed" : "active") : "unavailable");
  setText(
    "being-storage-detail",
    storage.available
      ? `Queue ${formatNumber(storage.queue_depth)} · Journal ${formatBytes(storage.journal_size_bytes)}`
      : "not connected",
  );

  const systemState = String(state.status || "idle").toLowerCase();
  setText("being-core-state", systemState);
  setText("being-system-status", systemState.toUpperCase());
  const components = Object.values(state.components || {});
  const activeComponents = components.filter((component) => ["active", "enabled"].includes(component.status)).length;
  setText("being-vital-caption", `${activeComponents}/${components.length} Komponenten`);
  const livingMap = byId("embodiment-living-map");
  if (livingMap) {
    const spikeActivity = clamp(
      Number(spikes.spike_count_last_tick ?? system.spikes_last_tick) /
        Math.max(Number(network.active_neurons ?? spikes.active_neurons) || 1, 1),
    );
    livingMap.dataset.systemState = systemState;
    livingMap.style.setProperty("--activity", String(spikeActivity));
    livingMap.style.setProperty("--pulse-duration", `${Math.max(0.75, 3.2 - spikeActivity * 2.2).toFixed(2)}s`);
    livingMap.style.setProperty("--energy", String(clamp(homeostasis.mean_energy ?? network.mean_energy ?? system.mean_energy)));
    livingMap.style.setProperty("--synchrony", String(clamp(spikes.synchrony ?? network.synchrony)));
  }
  renderConnections(embodimentConnections);
}
