/* MHRN Neural Symbiosis + MSBA view.
 * Read-only presentation only: no control, learning or actuator writes.
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
      <p>Framework-neutrale Pipeline-Schicht mit modalitätsspezifischen Audio-, Vision- und Digitalbahnen sowie expliziter Ressourcenökonomie.</p></div>
      <div class="wesen-symbiosis-state"><strong>READ-ONLY</strong><small>Embodiment boundary</small></div>
    </header>
    <div class="wesen-symbiosis-boundary"><strong>Scientific boundary</strong>
      <span>Keine Core-Mutation · keine automatische Gateway-Plastizität · Reachability ≠ learned use · geschätzte Energie ≠ gemessene Joule.</span>
    </div>
    <div class="wesen-symbiosis-grid">
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
      <article><header><strong>Plastic gateways</strong><span>INERT</span></header><div class="wesen-symbiosis-gateway">
        <div><span>Synaptic STDP</span><strong>disabled</strong></div>
        <div><span>Phase-weighted t-STDP</span><strong>candidate only</strong></div>
        <div><span>s-STDP / Structural Growth</span><strong>candidate only</strong></div>
        <div><span>Digital meta-gating</span><strong>candidate only</strong></div>
        <p>Aktivierung ausschließlich in einem expliziten preregistrierten Experiment mit RNG/Seed, Parametern, Controls, DATA und EVID.</p>
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
  if (!areas || !pipelines || !msba || !areaCount || !pipelineCount) return;
  areaCount.textContent = `${NETWORK_AREAS.length} + open set`;
  areas.innerHTML = NETWORK_AREAS.map(([name, family, purpose]) => `<div class="wesen-symbiosis-item"><span class="wesen-symbiosis-dot"></span><div><strong>${escapeHtml(name)}</strong><small>${escapeHtml(family)} · ${escapeHtml(purpose)}</small></div></div>`).join("");
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
    const response = await fetch("/api/embodiment/connections", { cache: "no-store" });
    if (!response.ok) return;
    lastConnections = connectionArray(await response.json());
    renderPanel();
  } catch (_) { /* unavailable telemetry remains unavailable */ }
}
function start() {
  ensurePanel(); refreshConnections(); if (timer) clearInterval(timer); timer = setInterval(refreshConnections, SYMBIOSIS_POLL_MS);
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { requestAnimationFrame(start); setTimeout(ensurePanel, 500); }, { once: true });
else { requestAnimationFrame(start); setTimeout(ensurePanel, 500); }
