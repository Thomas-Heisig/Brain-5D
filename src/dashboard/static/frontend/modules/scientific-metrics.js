"use strict";

import { apiGet } from "../core/api.js";

let baseline = null;
let refreshTimer = null;

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = value === null || value === undefined ? "" : String(value);
  return element.innerHTML;
}

function valueAt(root, path) {
  return path.reduce((value, key) => value && value[key], root);
}

function formatValue(value, unit = "") {
  if (value === null || value === undefined || value === "") return "UNKNOWN";
  if (typeof value === "object") {
    if (value.available === false || value.value === null || value.value === undefined) return "UNKNOWN";
    value = value.value;
  }
  if (typeof value === "number") return `${Number.isInteger(value) ? value.toLocaleString("de-DE") : value.toFixed(3)}${unit ? ` ${unit}` : ""}`;
  return escapeHtml(value);
}

function metric(id, label) {
  return `<div class="science-metric"><span>${label}</span><strong id="${id}">UNKNOWN</strong></div>`;
}

function ensurePanel() {
  let panel = document.getElementById("mhrn-scientific-metrics");
  if (panel) return panel;
  const workspace = document.getElementById("tab-research");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-scientific-metrics";
  panel.className = "mhrn-scientific-metrics card";
  panel.innerHTML = `<header class="science-metrics-header"><div><span class="workspace-kicker">SCIENTIFIC INSTRUMENT</span><h2>Dynamics, causality, statistics and falsification</h2><p>Measured values are separated from unavailable analyses. No null is treated as zero.</p></div><div class="science-metrics-actions"><span id="science-metrics-status" class="science-state unknown">UNKNOWN</span><button type="button" data-science-action="refresh">Refresh</button><button type="button" data-science-action="auto">Auto: off</button></div></header>
  <div class="science-metrics-toolbar"><span id="science-metrics-source">source: unknown</span><span id="science-metrics-tick">tick: unknown</span><span id="science-metrics-unknowns">unknown fields: 0</span><button type="button" data-science-action="capture">Capture comparison baseline</button><button type="button" data-science-action="compare">Compare current</button><button type="button" data-science-action="network">Open network drill-down</button><button type="button" data-science-action="runtime">Open runtime manipulator</button></div>
  <div class="science-metrics-grid">
    <article class="science-metrics-card"><header><span>01 / SPIKE TRAINS</span><h3>Population dynamics</h3></header><div class="science-metric-list">${metric("science-window", "Telemetry window")}${metric("science-isi", "ISI")}${metric("science-cv-isi", "CV(ISI)")}${metric("science-fano", "Fano factor")}${metric("science-vp", "Victor-Purpura")}${metric("science-van-rossum", "van Rossum")}${metric("science-entropy", "Population entropy")}${metric("science-bursts", "Burst trains")}</div></article>
    <article class="science-metrics-card"><header><span>02 / TOPOLOGY</span><h3>Connectivity and 5D geometry</h3></header><div class="science-metric-list">${metric("science-density", "Synaptic density")}${metric("science-fan-in", "Mean fan-in")}${metric("science-fan-out", "Mean fan-out")}${metric("science-weight", "Weight mean")}${metric("science-clustering", "Clustering coefficient")}${metric("science-path", "Mean path length")}${metric("science-five-d", "5D synapse distance")}${metric("science-modularity", "Modularity / small-world / motifs")}</div></article>
    <article class="science-metrics-card"><header><span>03 / CRITICALITY</span><h3>Regime and network dynamics</h3></header><div class="science-metric-list">${metric("science-avalanche", "Avalanches")}${metric("science-branching", "Branching parameter")}${metric("science-regime", "Regime")}${metric("science-lyapunov", "Lyapunov exponent")}${metric("science-attractor", "Attractor landscape")}${metric("science-dimensionality", "Dynamic dimensionality")}${metric("science-synchrony", "Synchrony")}${metric("science-burst-index", "Burst index")}</div></article>
    <article class="science-metrics-card"><header><span>04 / LEARNING</span><h3>Plasticity and credit assignment</h3></header><div class="science-metric-list">${metric("science-stdp", "STDP updates")}${metric("science-rewards", "Rewards applied")}${metric("science-eligibility", "Eligibility")}${metric("science-ltp-ltd", "LTP / LTD ratio")}${metric("science-rpe", "Reward prediction error")}${metric("science-trace-decay", "Eligibility decay")}${metric("science-credit", "Credit assignment")}${metric("science-learning-ci", "Learning CI")}</div></article>
    <article class="science-metrics-card"><header><span>05 / HOMEOSTASIS</span><h3>Energy and hardware cost</h3></header><div class="science-metric-list">${metric("science-target-rate", "Target rate")}${metric("science-actual-rate", "Actual rate")}${metric("science-rate-error", "Rate error")}${metric("science-threshold", "Threshold adaptation")}${metric("science-energy", "Mean energy")}${metric("science-energy-spike", "Energy per spike")}${metric("science-synops", "SynOps")}${metric("science-latency", "Closed-loop latency")}</div></article>
    <article class="science-metrics-card"><header><span>06 / STATISTICS</span><h3>Replication and inference</h3></header><div class="science-metric-list">${metric("science-seeds", "Multi-seed variance")}${metric("science-ci", "Confidence intervals")}${metric("science-effect", "Effect sizes")}${metric("science-power", "Power")}${metric("science-null", "Null models")}${metric("science-surrogate", "Surrogate data")}${metric("science-contradictions", "Contradictions")}${metric("science-falsification", "Falsification status")}</div></article>
  </div>
  <section class="science-evidence-strip"><div><span>UNKNOWN-STATE / PROVENANCE</span><strong id="science-telemetry">Telemetry: UNKNOWN</strong><p id="science-provenance-note">No scientific claim is made for unavailable values.</p></div><div><span>FALSIFICATION NOTE</span><label for="science-falsification-note">What observation would disconfirm the current hypothesis?</label><textarea id="science-falsification-note" rows="2" placeholder="Record a falsifiable prediction or null result."></textarea><button type="button" data-science-action="save-note">Save local annotation</button><small id="science-note-status">Not part of scientific evidence until exported with an experiment.</small></div><pre id="science-comparison" class="science-comparison" hidden></pre></section>`;
  const host = document.getElementById("research-panel-experiments") || workspace;
  host.append(panel);
  upgradePanelToWorkbench(panel);
  panel.addEventListener("click", handleAction);
  const note = panel.querySelector("#science-falsification-note");
  if (note) note.value = localStorage.getItem("mhrn.science.falsification-note") || "";
  return panel;
}

function upgradePanelToWorkbench(panel) {
  if (panel.dataset.workbenchReady === "true") return;
  const grid = panel.querySelector(".science-metrics-grid");
  if (!grid) return;
  const cards = Array.from(grid.children);
  const evidence = panel.querySelector(".science-evidence-strip");
  const definitions = [
    { id: "observatory", label: "Observatory", content: `<div class="science-observatory"><span class="science-section-label">LIVE RESEARCH STATE</span><h3>One instrument, many evidence layers</h3><p>Inspect measurements, trace unavailable values, and move from a network overview to a controlled experiment.</p><div class="science-action-row"><button type="button" data-science-action="network">Network drill-down</button><button type="button" data-science-action="runtime">Runtime manipulator</button><button type="button" data-science-action="experiment">Experiment runner</button></div><div class="science-observatory-grid">${metric("science-observatory-window", "Telemetry events")}${metric("science-observatory-density", "Synaptic density")}${metric("science-observatory-branching", "Branching")}${metric("science-observatory-rate", "Rate error")}${metric("science-observatory-stdp", "STDP updates")}${metric("science-observatory-evidence", "Evidence source")}</div></div>` },
    { id: "spikes", label: "Spike trains", node: cards[0], content: `<aside class="science-side-structure"><h4>Spike train controls</h4><button type="button" data-science-action="raster">Open raster and histogram</button><button type="button" data-science-action="capture">Capture baseline</button><p id="science-spike-window">Window UNKNOWN -> UNKNOWN</p><small>Distances use the retained telemetry window and declared q/tau parameters.</small></aside>` },
    { id: "topology", label: "Topology / 5D", node: cards[1], content: `<aside class="science-side-structure"><h4>Topology controls</h4><button type="button" data-science-action="network">Open neuron and synapse tables</button><button type="button" data-science-action="projection">Open 5D projection</button><p>Modularity, motifs, rich-club and effective connectivity remain UNKNOWN until their analysis contracts are present.</p></aside>` },
    { id: "criticality", label: "Criticality", node: cards[2], content: `<aside class="science-side-structure"><h4>Interpretation boundary</h4><p>A branching value alone does not establish a critical state. Distributional tests, fitted exponents and uncertainty are required.</p><button type="button" data-science-action="experiment">Run controlled criticality experiment</button></aside>` },
    { id: "learning", label: "Learning", node: cards[3], content: `<aside class="science-side-structure"><h4>Learning controls</h4><button type="button" data-science-action="learning">Open Learning Studio</button><button type="button" data-science-action="preparation">Learning preparation</button><p>Direct weight, eligibility and reward injection remain blocked by the experiment boundary.</p></aside>` },
    { id: "energy", label: "Energy / Homeostasis", node: cards[4], content: `<aside class="science-side-structure"><h4>Runtime clock</h4><p id="science-runtime-clock">Target, achieved rate, jitter and phase profile: UNKNOWN</p><button type="button" data-science-action="embodiment">Open Embodiment</button></aside>` },
    { id: "statistics", label: "Statistics", node: cards[5], content: `<aside class="science-side-structure"><h4>Replication workflow</h4><button type="button" data-science-action="experiment">Open Experiment Runner</button><button type="button" data-science-action="registry">Open Evidence Registry</button><p>Confidence intervals, effect sizes and power require seed-level experiment records.</p></aside>` },
    { id: "causality", label: "Causality", content: `<div class="science-tab-layout"><div class="science-contract-list"><div><strong>Mutual information</strong><span>UNKNOWN · no paired source/target event stream</span></div><div><strong>Transfer entropy</strong><span>UNKNOWN · no lagged causal telemetry contract</span></div><div><strong>Effective connectivity</strong><span>UNKNOWN · no intervention receipt</span></div><div><strong>Counterfactual effect</strong><span>UNKNOWN · no controlled twin run</span></div></div><aside class="science-side-structure"><h4>Causal controls</h4><button type="button" data-science-action="experiment">Create controlled run</button><button type="button" data-science-action="compare">Compare current sample</button></aside></div>` },
    { id: "embodiment", label: "Embodiment", content: `<div class="science-tab-layout"><div class="science-metric-list">${metric("science-environment", "Environment")}${metric("science-sensors", "Active sensors")}${metric("science-actuators", "Active actuators")}${metric("science-episode", "Episode")}${metric("science-reward", "Episode reward")}${metric("science-action", "Last action")}${metric("science-closed-loop", "Closed-loop latency")}${metric("science-jitter", "Jitter")}</div><aside class="science-side-structure"><h4>Embodiment controls</h4><button type="button" data-science-action="embodiment">Open sensor and pipeline controls</button><p>Sensorimotor claims require an active, authorized adapter.</p></aside></div>` },
    { id: "provenance", label: "Provenance", content: `<div class="science-tab-layout"><div class="science-provenance-table"><div><span>Telemetry</span><strong id="science-provenance-telemetry">UNKNOWN</strong></div><div><span>Age</span><strong id="science-telemetry-age">UNKNOWN</strong></div><div><span>Source</span><strong id="science-provenance-source">UNKNOWN</strong></div><div><span>Tick</span><strong id="science-provenance-tick">UNKNOWN</strong></div><div><span>Unknown fields</span><strong id="science-provenance-unknowns">UNKNOWN</strong></div></div><aside class="science-side-structure"><h4>Evidence boundary</h4><p>Live observations, DATA artifacts, reviewed EVID and AI interpretation remain separate states.</p><button type="button" data-science-action="transparency">Open Science Transparency</button></aside></div>` },
    { id: "benchmarks", label: "Benchmarks", content: `<div class="science-tab-layout"><div class="science-benchmark-grid"><div><strong>MHRN</strong><span id="science-benchmark-mhrn">live runtime · measured</span></div><div><strong>Brian2</strong><span>negative conformity record · no ranking</span></div><div><strong>NEST</strong><span>planned · no task-matched result</span></div><div><strong>Loihi / Lava</strong><span>planned · hardware data unavailable</span></div><div><strong>SpiNNaker</strong><span>planned · hardware data unavailable</span></div></div><aside class="science-side-structure"><h4>Benchmark contract</h4><p>Identical task, seeds, duration, metrics and hardware conditions are required.</p><button type="button" data-science-action="experiment">Register benchmark run</button></aside></div>` },
    { id: "falsification", label: "Falsification", content: `<div class="science-falsification-layout"><div><h3>What would disconfirm this experiment?</h3><p>Record a prediction, null result, stopping rule or disconfirming observation.</p></div><aside><strong id="science-falsification-state">NOT EVALUATED</strong><p id="science-comparison-summary">No comparison recorded.</p></aside></div>` },
  ];
  const tabBar = document.createElement("nav");
  tabBar.className = "science-tabbar";
  tabBar.setAttribute("role", "tablist");
  tabBar.setAttribute("aria-label", "Scientific research layers");
  const panelRoot = document.createElement("div");
  panelRoot.className = "science-tab-panels";
  definitions.forEach((definition, index) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = `science-tab${index === 0 ? " active" : ""}`;
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-selected", String(index === 0));
    tab.dataset.scienceTab = definition.id;
    tab.textContent = definition.label;
    tabBar.appendChild(tab);
    const tabPanel = document.createElement("section");
    tabPanel.className = `science-tab-panel${index === 0 ? " active" : ""}`;
    tabPanel.id = `science-panel-${definition.id}`;
    tabPanel.dataset.sciencePanel = definition.id;
    tabPanel.hidden = index !== 0;
    if (definition.node) {
      const layout = document.createElement("div");
      layout.className = "science-tab-layout";
      layout.appendChild(definition.node);
      layout.insertAdjacentHTML("beforeend", definition.content);
      tabPanel.appendChild(layout);
    } else {
      tabPanel.innerHTML = definition.content;
    }
    panelRoot.appendChild(tabPanel);
  });
  if (evidence) panelRoot.querySelector('[data-science-panel="falsification"]')?.appendChild(evidence);
  grid.replaceWith(panelRoot);
  panel.insertBefore(tabBar, panelRoot);
  panel.dataset.workbenchReady = "true";
}

function setMetric(panel, id, value, unit = "") {
  const element = panel.querySelector(`#${id}`);
  if (!element) return;
  const text = formatValue(value, unit);
  element.textContent = text;
  element.classList.toggle("is-unknown", text === "UNKNOWN");
}

function selectScienceTab(panel, target) {
  panel.querySelectorAll("[data-science-tab]").forEach((tab) => {
    const active = tab.dataset.scienceTab === target;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  panel.querySelectorAll("[data-science-panel]").forEach((tabPanel) => {
    const active = tabPanel.dataset.sciencePanel === target;
    tabPanel.classList.toggle("active", active);
    tabPanel.hidden = !active;
  });
}

function regime(branching) {
  if (typeof branching !== "number") return null;
  if (branching < 0.95) return "subcritical";
  if (branching <= 1.05) return "near-critical";
  return "supercritical";
}

function render(panel, payload, embodiment) {
  const spikes = payload.spike_trains || {};
  const topology = payload.topology || {};
  const criticality = payload.criticality || {};
  const learning = payload.learning || {};
  const homeostasis = payload.homeostasis || {};
  const statistics = payload.statistics || {};
  const embodimentMetrics = embodiment?.metrics || {};
  const network = payload.network || {};
  const fano = spikes.fano_factor;
  const branching = criticality.branching_parameter;
  const unknowns = [
    spikes.isi_ticks, spikes.cv_isi, spikes.fano_factor, spikes.victor_purpura, spikes.van_rossum,
    topology.modularity, topology.small_worldness, topology.motif_count, criticality.lyapunov_exponent,
    criticality.dimensionality, learning.ltp_ltd_ratio, statistics.confidence_intervals,
  ].filter((value) => value === null || value?.available === false).length;
  const telemetry = payload.provenance?.telemetry || {};
  panel.querySelector("#science-metrics-status").textContent = telemetry.status || "UNKNOWN";
  panel.querySelector("#science-metrics-status").className = `science-state ${telemetry.status || "unknown"}`;
  panel.querySelector("#science-metrics-source").textContent = `source: ${payload.source || "unknown"}`;
  panel.querySelector("#science-metrics-tick").textContent = `tick: ${payload.tick ?? "unknown"}`;
  panel.querySelector("#science-metrics-unknowns").textContent = `unknown fields: ${unknowns}`;
  panel.querySelector("#science-telemetry").textContent = `Telemetry: ${telemetry.status || "UNKNOWN"} · age ${telemetry.frame_age_ticks ?? "unknown"} ticks`;
  panel.querySelector("#science-provenance-note").textContent = `Window ${spikes.window?.start_tick ?? "unknown"} -> ${spikes.window?.end_tick ?? "unknown"}; ${payload.provenance?.unknown_policy || "Unavailable values remain unknown."}`;
  setMetric(panel, "science-window", spikes.window?.events, "events");
  setMetric(panel, "science-window-ticks", spikes.window?.ticks);
  setMetric(panel, "science-observatory-window", spikes.window?.events, "events");
  setMetric(panel, "science-isi", spikes.isi_ticks, "ticks");
  setMetric(panel, "science-cv-isi", spikes.cv_isi);
  setMetric(panel, "science-fano", fano);
  setMetric(panel, "science-vp", spikes.victor_purpura);
  setMetric(panel, "science-van-rossum", spikes.van_rossum);
  setMetric(panel, "science-entropy", spikes.population_entropy_bits, "bits");
  setMetric(panel, "science-bursts", spikes.burst_train_count);
  setMetric(panel, "science-density", topology.synaptic_density);
  setMetric(panel, "science-observatory-density", topology.synaptic_density);
  setMetric(panel, "science-fan-in", topology.mean_fan_in);
  setMetric(panel, "science-fan-out", topology.mean_fan_out);
  setMetric(panel, "science-weight", topology.weight);
  setMetric(panel, "science-clustering", topology.clustering_coefficient);
  setMetric(panel, "science-path", topology.mean_path_length);
  setMetric(panel, "science-five-d", topology.five_d?.mean_manhattan_synapse_distance);
  setMetric(panel, "science-modularity", topology.modularity);
  setMetric(panel, "science-small-world", topology.small_worldness);
  setMetric(panel, "science-motifs", topology.motif_count);
  setMetric(panel, "science-rich-club", topology.rich_club);
  setMetric(panel, "science-avalanche", criticality.avalanche?.mean_size);
  setMetric(panel, "science-avalanche-count", criticality.avalanche?.count);
  setMetric(panel, "science-branching", branching);
  setMetric(panel, "science-branching-criticality", branching);
  setMetric(panel, "science-observatory-branching", branching);
  setMetric(panel, "science-regime", regime(branching?.value));
  setMetric(panel, "science-lyapunov", criticality.lyapunov_exponent);
  setMetric(panel, "science-attractor", criticality.attractor_landscape);
  setMetric(panel, "science-dimensionality", criticality.dimensionality);
  setMetric(panel, "science-synchrony", network.synchrony);
  setMetric(panel, "science-burst-index", network.burst_index);
  setMetric(panel, "science-stdp", learning.stdp_updates);
  setMetric(panel, "science-observatory-stdp", learning.stdp_updates);
  setMetric(panel, "science-stdp-learning", learning.stdp_updates);
  setMetric(panel, "science-rewards", learning.rewards_applied);
  setMetric(panel, "science-rewards-learning", learning.rewards_applied);
  setMetric(panel, "science-eligibility", learning.eligibility_enabled ? "enabled" : learning.eligibility_enabled === false ? "disabled" : null);
  setMetric(panel, "science-eligibility-learning", learning.eligibility_enabled ? "enabled" : learning.eligibility_enabled === false ? "disabled" : null);
  setMetric(panel, "science-ltp-ltd", learning.ltp_ltd_ratio);
  setMetric(panel, "science-rpe", learning.reward_prediction_error);
  setMetric(panel, "science-trace-decay", learning.eligibility_trace_decay);
  setMetric(panel, "science-credit", learning.credit_assignment);
  setMetric(panel, "science-learning-ci", learning.confidence_interval);
  setMetric(panel, "science-target-rate", homeostasis.target_rate_hz, "Hz");
  setMetric(panel, "science-actual-rate", homeostasis.mean_rate_hz, "Hz");
  setMetric(panel, "science-rate-error", homeostasis.mean_rate_error_hz, "Hz");
  setMetric(panel, "science-observatory-rate", homeostasis.mean_rate_error_hz, "Hz");
  setMetric(panel, "science-threshold", homeostasis.mean_threshold_adaptation);
  setMetric(panel, "science-energy", homeostasis.mean_energy);
  setMetric(panel, "science-energy-spike", homeostasis.energy_per_spike);
  setMetric(panel, "science-synops", homeostasis.synops);
  setMetric(panel, "science-latency", embodimentMetrics.closed_loop_latency_ms, "ms");
  setMetric(panel, "science-environment", embodimentMetrics.environment_kind);
  setMetric(panel, "science-sensors", embodimentMetrics.active_sensors);
  setMetric(panel, "science-actuators", embodimentMetrics.active_actuators);
  setMetric(panel, "science-episode", embodimentMetrics.episode);
  setMetric(panel, "science-reward", embodimentMetrics.episode_reward);
  setMetric(panel, "science-action", embodimentMetrics.last_action);
  setMetric(panel, "science-closed-loop", embodimentMetrics.closed_loop_latency_ms, "ms");
  setMetric(panel, "science-jitter", embodimentMetrics.jitter_ms, "ms");
  const windowNode = panel.querySelector("#science-spike-window");
  if (windowNode) windowNode.textContent = `Window ${spikes.window?.start_tick ?? "UNKNOWN"} -> ${spikes.window?.end_tick ?? "UNKNOWN"}`;
  const ageNode = panel.querySelector("#science-telemetry-age");
  if (ageNode) ageNode.textContent = `${telemetry.frame_age_ticks ?? "unknown"} ticks`;
  const provenanceTelemetry = panel.querySelector("#science-provenance-telemetry");
  if (provenanceTelemetry) provenanceTelemetry.textContent = telemetry.status || "UNKNOWN";
  const provenanceSource = panel.querySelector("#science-provenance-source");
  if (provenanceSource) provenanceSource.textContent = payload.source || "UNKNOWN";
  const provenanceTick = panel.querySelector("#science-provenance-tick");
  if (provenanceTick) provenanceTick.textContent = String(payload.tick ?? "UNKNOWN");
  const provenanceUnknowns = panel.querySelector("#science-provenance-unknowns");
  if (provenanceUnknowns) provenanceUnknowns.textContent = String(unknowns);
  const falsificationState = panel.querySelector("#science-falsification-state");
  if (falsificationState) falsificationState.textContent = "NOT EVALUATED";
  setMetric(panel, "science-seeds", statistics.multi_seed);
  setMetric(panel, "science-ci", statistics.confidence_intervals);
  setMetric(panel, "science-effect", statistics.effect_sizes);
  setMetric(panel, "science-power", statistics.power);
  setMetric(panel, "science-null", statistics.null_models);
  setMetric(panel, "science-surrogate", statistics.surrogate_data);
  setMetric(panel, "science-contradictions", payload.experiment?.contradiction_detections);
  setMetric(panel, "science-falsification", "not evaluated");
  panel._sciencePayload = payload;
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel || panel.hidden) return;
  try {
    const [metrics, embodiment] = await Promise.all([apiGet("/api/science/metrics"), apiGet("/api/embodiment/metrics").catch(() => ({}))]);
    render(panel, metrics, embodiment);
  } catch (error) {
    const status = panel.querySelector("#science-metrics-status");
    status.textContent = "UNAVAILABLE";
    status.className = "science-state unavailable";
    panel.querySelector("#science-provenance-note").textContent = `Scientific metrics unavailable: ${error.message}`;
  }
}

function compareCurrent() {
  const panel = ensurePanel();
  const output = panel?.querySelector("#science-comparison");
  if (!output) return;
  if (!baseline) {
    output.hidden = false;
    output.textContent = "No comparison baseline. Capture one first.";
    return;
  }
  const current = panel._sciencePayload;
  if (!current) return;
  const fields = ["tick", "spike_trains.window.events", "spike_trains.fano_factor.value", "criticality.branching_parameter.value", "topology.synaptic_density"];
  const changes = fields.map((path) => {
    const keys = path.split(".");
    return { metric: path, baseline: valueAt(baseline, keys), current: valueAt(current, keys) };
  }).filter((item) => JSON.stringify(item.baseline) !== JSON.stringify(item.current));
  output.hidden = false;
  output.textContent = JSON.stringify({ scientific_evidence: false, changes }, null, 2);
}

function handleAction(event) {
  const scienceTab = event.target.closest("[data-science-tab]");
  if (scienceTab) {
    selectScienceTab(ensurePanel(), scienceTab.dataset.scienceTab);
    return;
  }
  const action = event.target.closest("[data-science-action]")?.dataset.scienceAction;
  if (!action) return;
  const panel = ensurePanel();
  if (action === "refresh") refresh();
  if (action === "auto") {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
      event.target.textContent = "Auto: off";
    } else {
      refreshTimer = setInterval(refresh, 10000);
      event.target.textContent = "Auto: on";
    }
  }
  if (action === "capture") baseline = panel?._sciencePayload || null;
  if (action === "compare") compareCurrent();
  if (["experiment", "learning", "preparation", "registry", "transparency", "embodiment", "raster", "projection"].includes(action)) {
    const routes = { experiment: "control", learning: "control", preparation: "control", registry: "research", transparency: "research", embodiment: "embodiment", raster: "network", projection: "network" };
    document.querySelector(`.tab-btn[data-tab="${routes[action]}"]`)?.click();
  }
  if (action === "save-note") {
    const note = panel?.querySelector("#science-falsification-note")?.value || "";
    localStorage.setItem("mhrn.science.falsification-note", note);
    panel.querySelector("#science-note-status").textContent = "Saved locally; not scientific evidence until exported.";
  }
  if (action === "network") document.querySelector('.tab-btn[data-tab="network"]')?.click();
  if (action === "runtime") document.getElementById("mhrn-runtime-io")?.scrollIntoView({ behavior: "smooth", block: "center" });
}

export function initScientificMetrics() {
  ensurePanel();
  refresh();
}