/* MHRN Neural Symbiosis + MSBA view.
 * Status is read-only; lifecycle controls are limited to registered experiments.
 */

const SYMBIOSIS_POLL_MS = 2000;
const NETWORK_AREAS = [
  ["CNN", "Vision / Audio", "sensorische Merkmalsextraktion"],
  ["Vision Transformer", "Vision", "globale visuelle Aufmerksamkeit"],
  ["Transformer", "Language / Audio / Multimodal", "Sequenz- und Kontextprojektion"],
  ["LSTM / GRU / RNN", "Temporal", "rekurrente Sequenzen"],
  ["GNN", "Graph", "relationale Strukturen"],
  ["Modern Hopfield", "Memory", "assoziativer Abruf"],
  ["Echo State Network", "Reservoir", "Reservoir-Dynamik"],
  ["MLP", "Control / Projection", "Dekodierung und Projektion"],
  ["VAE / GAN / Diffusion", "Generative", "generative Repräsentationen"],
  ["Peripheral SNN", "Event", "ereignisbasierte Vorverarbeitung"],
  ["Custom", "Open set", "beliebiger NetworkAreaAdapter"],
];

const PIPELINES = [
  { id: "camera.vision", label: "Camera → CNN / ViT → Gateway → 5D-SNN", source: "sensor.camera", kind: "afferent" },
  { id: "microphone.audio", label: "Microphone → Audio CNN / Transformer → Gateway → 5D-SNN", source: "sensor.microphone", kind: "afferent" },
  { id: "web.language", label: "Web / API → Language Transformer → Gateway → 5D-SNN", source: "data.web_api", kind: "afferent" },
  { id: "database.knowledge", label: "Database → Knowledge / GNN → Gateway → 5D-SNN", source: "data.database", kind: "cognitive" },
  { id: "logic.cognitive", label: "Logic Engine → Neuro-symbolic Projector → Gateway → 5D-SNN", source: "virtual.logic", kind: "cognitive" },
  { id: "core.audio", label: "5D-SNN → Gateway → Speech → Audio output", sink: "actuator.audio", kind: "efferent" },
  { id: "core.display", label: "5D-SNN → Gateway → Decoder → Display", sink: "actuator.display", kind: "efferent" },
  { id: "core.robotics", label: "5D-SNN → Gateway → Control → Robotics", sink: "actuator.robotics", kind: "efferent" },
];

const MSBA = [
  ["Audio", "Temporal coherence", "band · phase/envelope · channel · lag · feature", "t-STDP candidate", "bands / update rate / delay taps"],
  ["Vision", "Spatial multiplex", "x · y · feature · scale · frame", "s-STDP + growth candidate", "FPS / resolution / ROI / feature channels"],
  ["Digital", "Quantized high fidelity", "symbol · sequence · source · context · route", "meta-gating candidate", "admission / batching / symbol rate"],
];

let timer = null;
let lastConnections = [];
let lastSymbiosis = null;
let lastExperimentMode = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}
function connectionArray(payload) { return payload && Array.isArray(payload.connections) ? payload.connections : []; }
function availableConnectionIds(connections) {
  return connections.filter((item) => item && item.available === true).map((item) => String(item.connection_id || "")).filter(Boolean);
}
function endpointReachable(endpoint, available) {
  if (!endpoint || endpoint.startsWith("virtual.")) return true;
  return available.some((item) => item === endpoint || item.startsWith(`${endpoint}.`));
}
function pipelineReachable(pipeline, available) {
  return endpointReachable(pipeline.source, available) && endpointReachable(pipeline.sink, available);
}

function ensurePanel() {
  const workspace = document.getElementById("tab-wesen");
  if (!workspace) return null;
  let panel = document.getElementById("wesen-neural-symbiosis");
  if (panel) return panel;
  panel = document.createElement("section");
  panel.id = "wesen-neural-symbiosis";
  panel.className = "wesen-symbiosis-card";
  panel.innerHTML = `
    <header class="wesen-symbiosis-header">
      <div><span>EMBODIED MULTI-NETWORK INTERFACE</span><h3>Neural Symbiosis · MSBA</h3>
      <p>Kontrollierte Vermittlungsschicht mit modalitätsspezifischen Audio-, Vision- und Digitalbahnen sowie expliziter Ressourcenökonomie.</p></div>
      <div class="wesen-symbiosis-state"><strong id="wesen-symbiosis-state">DISABLED</strong><small id="wesen-symbiosis-maturity">Maturity 0 · Contract only</small></div>
    </header>
    <div class="wesen-symbiosis-boundary"><strong>Scientific boundary / EXPERIMENT CONTROL</strong>
      <span>Experimental activation only · Productive Gateway: LOCKED · keine Core-Mutation · Gateway-Aktivität ist kein Lernnachweis.</span>
    </div>
    <div class="wesen-symbiosis-grid">
      <article><header><strong>Gateway status</strong><span id="wesen-symbiosis-condition">EXPERIMENT ONLY</span></header><div id="wesen-symbiosis-status" class="wesen-symbiosis-gateway"></div></article>
      <article><header><strong>Topology</strong><span id="wesen-symbiosis-topology-count">0 edges</span></header><div id="wesen-symbiosis-topology" class="wesen-symbiosis-topology"></div></article>
      <article><header><strong>Network areas</strong><span id="wesen-symbiosis-area-count">0</span></header><div id="wesen-symbiosis-areas" class="wesen-symbiosis-list"></div></article>
      <article><header><strong>Pipelines</strong><span id="wesen-symbiosis-pipeline-count">0</span></header><div id="wesen-symbiosis-pipelines" class="wesen-symbiosis-list"></div></article>
      <article><header><strong>MSBA pathways</strong><span>3 MODALITIES</span></header><div id="wesen-msba-pathways" class="wesen-symbiosis-list"></div></article>
      <article><header><strong>Energy homeostasis</strong><span>FAIL-CLOSED</span></header><div class="wesen-symbiosis-gateway">
        <div><span>Accounting</span><strong>energy units / estimated / measured</strong></div>
        <div><span>Soft allocation</span><strong>disabled by default</strong></div>
        <div><span>Structural growth</span><strong>disabled by default</strong></div>
        <div><span>Hard safety</span><strong>fan / thermal / persistence override</strong></div>
        <p>NORMAL → CONSERVE → CRITICAL → SURVIVAL. Zuerst Plastizität und redundante Auflösung reduzieren; erlernte Struktur wird nicht als Energiesparmaßnahme gelöscht.</p>
      </div></article>
      <article><header><strong>Digital integrity</strong><span>EXACT PAYLOAD</span></header><div class="wesen-symbiosis-gateway">
        <div><span>Payload</span><strong>immutable outside SNN</strong></div>
        <div><span>Population code</span><strong>deterministic</strong></div>
        <div><span>Learnable component</span><strong>routing / gain / admission only</strong></div>
        <p>Bitwerte, Prüfsumme und Original-Payload werden nicht durch SNN-Plastizität verändert.</p>
      </div></article>
      <article><header><strong>Experimental Plasticity</strong><span>AVAILABLE IN CONTROLLED EXPERIMENTS</span></header><div class="wesen-symbiosis-gateway">
        <div><span>Synaptic STDP</span><strong>experiment-only</strong></div>
        <div><span>Phase-weighted t-STDP</span><strong>candidate</strong></div>
        <div><span>Productive Gateway</span><strong>LOCKED</strong></div>
        <p>Plasticity erfordert die vorhandenen Backend-Gates: Experiment Mode, Preregistration, Seed und Resource Limits.</p>
      </div></article>
      <article><header><strong>Gateway experiment control</strong><span id="wesen-gateway-mode">OPERATOR MODE</span></header><div class="wesen-gateway-controls">
        <label>Experiment ID<input id="wesen-gateway-experiment-id" type="text" placeholder="EXP-GW-…"></label>
        <label>Condition<select id="wesen-gateway-condition"><option value="frozen">Frozen</option><option value="random">Random</option><option value="shuffle">Shuffle</option><option value="plastic">Plastic</option></select></label>
        <label>Seed<input id="wesen-gateway-seed" type="number" value="42"></label>
        <label>Preregistration / Protocol<textarea id="wesen-gateway-preregistration" rows="2" placeholder='{"protocol_id":"…"}'></textarea></label>
        <div class="wesen-gateway-actions"><button type="button" data-gateway-action="activate">Activate</button><button type="button" data-gateway-action="pause">Pause</button><button type="button" data-gateway-action="resume">Resume</button><button type="button" data-gateway-action="stop">Stop</button></div>
        <small id="wesen-gateway-message">Nur Experiment Mode kann diese Controls freischalten.</small>
      </div></article>
    </div>`;
  const stage = workspace.querySelector(".wesen-stage-card");
  if (stage) stage.insertAdjacentElement("afterend", panel); else workspace.appendChild(panel);
  renderPanel();
  return panel;
}

function renderPanel() {
  if (!ensurePanel()) return;
  const areas = document.getElementById("wesen-symbiosis-areas");
  const pipelines = document.getElementById("wesen-symbiosis-pipelines");
  const msba = document.getElementById("wesen-msba-pathways");
  const areaCount = document.getElementById("wesen-symbiosis-area-count");
  const pipelineCount = document.getElementById("wesen-symbiosis-pipeline-count");
  const gatewayState = document.getElementById("wesen-symbiosis-state");
  const maturity = document.getElementById("wesen-symbiosis-maturity");
  const condition = document.getElementById("wesen-symbiosis-condition");
  const status = document.getElementById("wesen-symbiosis-status");
  const topology = document.getElementById("wesen-symbiosis-topology");
  const topologyCount = document.getElementById("wesen-symbiosis-topology-count");
  if (!areas || !pipelines || !msba || !areaCount || !pipelineCount) return;
  const gateway = lastSymbiosis?.gateway || {};
  const experimentMode = lastExperimentMode?.current_mode === "experiment";
  const modeLabel = document.getElementById("wesen-gateway-mode");
  if (modeLabel) modeLabel.textContent = experimentMode ? "EXPERIMENT MODE" : String(lastExperimentMode?.current_mode || "operator").toUpperCase();
  document.querySelectorAll("[data-gateway-action]").forEach((button) => {
    const action = button.dataset.gatewayAction;
    button.disabled = !experimentMode || (action === "activate" ? !document.getElementById("wesen-gateway-experiment-id")?.value.trim() : !gateway.state || gateway.state === "disabled");
  });
  const catalog = lastSymbiosis?.catalog || {};
  const catalogAreas = Array.isArray(catalog.areas) ? catalog.areas : [];
  const areaRows = catalogAreas.length ? catalogAreas.map((item) => [item.name, item.architecture, item.implementation_status]) : NETWORK_AREAS;
  areaCount.textContent = `${areaRows.length} + open set`;
  areas.innerHTML = areaRows.map(([name, family, purpose]) => `<div class="wesen-symbiosis-item"><span class="wesen-symbiosis-dot"></span><div><strong>${escapeHtml(name)}</strong><small>${escapeHtml(family)} · ${escapeHtml(purpose)}</small></div></div>`).join("");
  if (gatewayState) gatewayState.textContent = String(gateway.state || "disabled").replaceAll("_", " ").toUpperCase();
  if (condition) condition.textContent = gateway.condition ? String(gateway.condition).toUpperCase() : "EXPERIMENT ONLY";
  if (maturity) maturity.textContent = `Maturity ${Number(lastSymbiosis?.maturity_level || 0)} · ${gateway.productive_gateway?.available ? "candidate" : "Productive locked"}`;
  if (status) status.innerHTML = [
    ["Plasticity", gateway.gateway_plasticity_allowed ? "experimental" : "disabled"],
    ["Resource mode", gateway.resource_mode || "unknown"],
    ["Experiment", gateway.experiment_id || "none"],
    ["Productive", "LOCKED"],
  ].map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
  const topologyData = gateway.topology || {};
  if (topologyCount) topologyCount.textContent = `${Number(topologyData.edges || 0)} edges`;
  if (topology) topology.innerHTML = `<div class="wesen-symbiosis-topology-node"><strong>${escapeHtml(topologyData.source_area || "source")}</strong><span>${escapeHtml(topologyData.modality || "unknown")}</span></div><div class="wesen-symbiosis-topology-edge"><span>GW</span><strong>${escapeHtml(gateway.state || "disabled")}</strong></div><div class="wesen-symbiosis-topology-node"><strong>${escapeHtml(topologyData.target_area || "target")}</strong><span>${Number(topologyData.edges || 0)} aggregated edges</span></div>`;
  const available = availableConnectionIds(lastConnections);
  const reachable = PIPELINES.filter((item) => pipelineReachable(item, available)).length;
  pipelineCount.textContent = `${reachable}/${PIPELINES.length} reachable`;
  pipelines.innerHTML = PIPELINES.map((pipeline) => {
    const ok = pipelineReachable(pipeline, available);
    return `<div class="wesen-symbiosis-item ${ok ? "reachable" : "unreachable"}"><span class="wesen-symbiosis-dot"></span><div><strong>${escapeHtml(pipeline.label)}</strong><small>${escapeHtml(pipeline.kind)} · ${ok ? "endpoint reachable" : "endpoint unavailable"} · disabled</small></div></div>`;
  }).join("");
  msba.innerHTML = MSBA.map(([name, path, coords, plasticity, throttle]) => `<div class="wesen-symbiosis-item"><span class="wesen-symbiosis-dot"></span><div><strong>${escapeHtml(name)} · ${escapeHtml(path)}</strong><small>${escapeHtml(coords)} · ${escapeHtml(plasticity)} · throttle: ${escapeHtml(throttle)}</small></div></div>`).join("");
}

async function refreshConnections() {
  try {
    const [connectionsResponse, symbiosisResponse, modeResponse] = await Promise.all([
      fetch("/api/embodiment/connections", { cache: "no-store" }),
      fetch("/api/embodiment/neural-symbiosis", { cache: "no-store" }),
      fetch("/api/experiment/mode", { cache: "no-store" }),
    ]);
    if (connectionsResponse.ok) lastConnections = connectionArray(await connectionsResponse.json());
    if (symbiosisResponse.ok) lastSymbiosis = await symbiosisResponse.json();
    if (modeResponse.ok) lastExperimentMode = await modeResponse.json();
    renderPanel();
  } catch (_) { /* unavailable telemetry remains unavailable */ }
}

async function gatewayAction(action) {
  const message = document.getElementById("wesen-gateway-message");
  const experimentId = document.getElementById("wesen-gateway-experiment-id")?.value.trim();
  const condition = document.getElementById("wesen-gateway-condition")?.value || "frozen";
  const seed = Number(document.getElementById("wesen-gateway-seed")?.value || 42);
  if (action === "activate" && !experimentId) return;
  let preregistration = undefined;
  if (action === "activate") {
    try { preregistration = JSON.parse(document.getElementById("wesen-gateway-preregistration")?.value || "{}"); } catch (_) { if (message) message.textContent = "Preregistration muss gültiges JSON sein."; return; }
  }
  try {
    const response = await fetch(`/api/experiments/${encodeURIComponent(experimentId || "current")}/gateway/${action}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ condition, seed, preregistration, experiment_mode: lastExperimentMode?.current_mode === "experiment" }) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    if (message) message.textContent = `Gateway ${action}: ${payload.gateway?.state || "updated"}. Productive: LOCKED.`;
    await refreshConnections();
  } catch (error) { if (message) message.textContent = `Gateway ${action} abgewiesen: ${error.message || error}`; }
}
function start() {
  ensurePanel();
  document.querySelectorAll("[data-gateway-action]").forEach((button) => button.addEventListener("click", () => gatewayAction(button.dataset.gatewayAction)));
  refreshConnections(); if (timer) clearInterval(timer); timer = setInterval(refreshConnections, SYMBIOSIS_POLL_MS);
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { requestAnimationFrame(start); setTimeout(ensurePanel, 500); }, { once: true });
else { requestAnimationFrame(start); setTimeout(ensurePanel, 500); }
