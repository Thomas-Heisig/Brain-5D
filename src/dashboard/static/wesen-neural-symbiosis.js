/* Brain-5D Neural Symbiosis view
 * Read-only embodiment presentation for peripheral neural/virtual pipelines.
 * This module never writes runtime, learning, research or actuator state.
 */

const SYMBIOSIS_POLL_MS = 2000;

const NETWORK_AREAS = [
  ["CNN", "Vision / Audio", "sensorische Merkmalsextraktion"],
  ["Vision Transformer", "Vision", "globale visuelle Aufmerksamkeit"],
  ["Transformer", "Language / Audio / Multimodal", "Sequenz- und Kontextprojektion"],
  ["LSTM", "Temporal", "zeitliche Kontexte"],
  ["GRU", "Temporal", "kompakte rekurrente Sequenzen"],
  ["RNN", "Temporal", "rekurrente Dynamik"],
  ["GNN", "Graph", "relationale Strukturen"],
  ["Modern Hopfield", "Memory", "assoziativer Abruf"],
  ["Echo State Network", "Reservoir", "Reservoir-Dynamik"],
  ["MLP", "Control / Projection", "Dekodierung und Projektion"],
  ["VAE", "Generative", "Repräsentation und Imagination"],
  ["GAN", "Generative", "generative Bild-/Merkmalsräume"],
  ["Diffusion", "Generative", "generative multimodale Räume"],
  ["Autoencoder", "Representation", "Kompression / Repräsentation"],
  ["Peripheral SNN", "Event", "ereignisbasierte Vorverarbeitung"],
  ["Custom", "Open set", "beliebiger NetworkAreaAdapter"],
];

const PIPELINES = [
  { id: "camera.vision", label: "Camera → CNN / ViT → Gateway → 5D-SNN", source: "sensor.camera", kind: "afferent" },
  { id: "microphone.audio", label: "Microphone → Audio CNN / Transformer → Gateway → 5D-SNN", source: "sensor.microphone", kind: "afferent" },
  { id: "microphone.speech", label: "Microphone → Speech / Language Transformer → Gateway → 5D-SNN", source: "sensor.microphone", kind: "afferent" },
  { id: "web.language", label: "Web / API → Language Transformer → Gateway → 5D-SNN", source: "data.web_api", kind: "afferent" },
  { id: "database.knowledge", label: "Database → Knowledge / GNN → Gateway → 5D-SNN", source: "data.database", kind: "cognitive" },
  { id: "logic.cognitive", label: "Logic Engine → Neuro-symbolic Projector → Gateway → 5D-SNN", source: "virtual.logic", kind: "cognitive" },
  { id: "memory.cognitive", label: "Associative Memory ↔ Cognitive Gateway ↔ 5D-SNN", source: "virtual.memory", kind: "cognitive" },
  { id: "core.audio", label: "5D-SNN → Gateway → Language / Speech → Audio output", sink: "actuator.audio", kind: "efferent" },
  { id: "core.display", label: "5D-SNN → Gateway → Multimodal Decoder → Display", sink: "actuator.display", kind: "efferent" },
  { id: "core.printer", label: "5D-SNN → Gateway → Document Projection → Printer", sink: "actuator.printer", kind: "efferent" },
  { id: "core.robotics", label: "5D-SNN → Gateway → GRU / Control MLP → Robotics", sink: "actuator.robotics", kind: "efferent" },
];

let timer = null;
let lastConnections = [];

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function connectionArray(payload) {
  if (!payload) return [];
  if (Array.isArray(payload.connections)) return payload.connections;
  return [];
}

function availableConnectionIds(connections) {
  return connections
    .filter((item) => item && item.available === true)
    .map((item) => String(item.connection_id || ""))
    .filter(Boolean);
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
      <div>
        <span>EMBODIED MULTI-NETWORK INTERFACE</span>
        <h3>Neural Symbiosis</h3>
        <p>Offene, framework-neutrale Pipeline-Schicht zwischen 5D-SNN, realen Sensoren/Aktoren und virtuellen kognitiven Systemen.</p>
      </div>
      <div class="wesen-symbiosis-state"><strong>READ-ONLY</strong><small>Embodiment boundary</small></div>
    </header>
    <div class="wesen-symbiosis-boundary">
      <strong>Scientific boundary</strong>
      <span>Keine Änderung am kanonischen SNN-Core · keine automatische Aktivierung · keine wissenschaftliche Evidenz aus bloßer Erreichbarkeit.</span>
    </div>
    <div class="wesen-symbiosis-grid">
      <article><header><strong>Network areas</strong><span id="wesen-symbiosis-area-count">0</span></header><div id="wesen-symbiosis-areas" class="wesen-symbiosis-list"></div></article>
      <article><header><strong>Pipelines</strong><span id="wesen-symbiosis-pipeline-count">0</span></header><div id="wesen-symbiosis-pipelines" class="wesen-symbiosis-list"></div></article>
      <article><header><strong>Plastic gateways</strong><span>INERT</span></header><div class="wesen-symbiosis-gateway">
        <div><span>Synaptic STDP</span><strong>disabled</strong></div>
        <div><span>Homeostatic scaling</span><strong>modelled / not active</strong></div>
        <div><span>Structural plasticity</span><strong>disabled</strong></div>
        <div><span>Efferent R-STDP gating</span><strong>disabled</strong></div>
        <p>Aktivierung gehört ausschließlich in einen expliziten, preregistrierten Experimentpfad. RNG, Parameter, DATA und EVID müssen dort separat protokolliert werden.</p>
      </div></article>
    </div>
  `;

  const stage = workspace.querySelector(".wesen-stage-card");
  if (stage) stage.insertAdjacentElement("afterend", panel);
  else workspace.appendChild(panel);
  renderPanel();
  return panel;
}

function renderPanel() {
  if (!ensurePanel()) return;
  const areas = document.getElementById("wesen-symbiosis-areas");
  const pipelines = document.getElementById("wesen-symbiosis-pipelines");
  const areaCount = document.getElementById("wesen-symbiosis-area-count");
  const pipelineCount = document.getElementById("wesen-symbiosis-pipeline-count");
  if (!areas || !pipelines || !areaCount || !pipelineCount) return;

  areaCount.textContent = `${NETWORK_AREAS.length} + open set`;
  areas.innerHTML = NETWORK_AREAS.map(([name, family, purpose]) => `
    <div class="wesen-symbiosis-item">
      <span class="wesen-symbiosis-dot"></span>
      <div><strong>${escapeHtml(name)}</strong><small>${escapeHtml(family)} · ${escapeHtml(purpose)}</small></div>
    </div>
  `).join("");

  const available = availableConnectionIds(lastConnections);
  const reachable = PIPELINES.filter((item) => pipelineReachable(item, available)).length;
  pipelineCount.textContent = `${reachable}/${PIPELINES.length} reachable`;
  pipelines.innerHTML = PIPELINES.map((pipeline) => {
    const isReachable = pipelineReachable(pipeline, available);
    return `
      <div class="wesen-symbiosis-item ${isReachable ? "reachable" : "unreachable"}">
        <span class="wesen-symbiosis-dot"></span>
        <div><strong>${escapeHtml(pipeline.label)}</strong><small>${escapeHtml(pipeline.kind)} · ${isReachable ? "endpoint reachable" : "endpoint unavailable"} · disabled</small></div>
      </div>
    `;
  }).join("");
}

async function refreshConnections() {
  try {
    const response = await fetch("/api/embodiment/connections", { cache: "no-store" });
    if (!response.ok) return;
    lastConnections = connectionArray(await response.json());
    renderPanel();
  } catch (_) {
    // Read-only presentation: unavailable telemetry remains unavailable.
  }
}

function start() {
  ensurePanel();
  refreshConnections();
  if (timer) clearInterval(timer);
  timer = setInterval(refreshConnections, SYMBIOSIS_POLL_MS);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    requestAnimationFrame(start);
    setTimeout(ensurePanel, 500);
  }, { once: true });
} else {
  requestAnimationFrame(start);
  setTimeout(ensurePanel, 500);
}
