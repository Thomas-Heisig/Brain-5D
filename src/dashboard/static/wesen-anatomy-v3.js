/* Brain-5D Wesen anatomy v3.
 * Read-only presentation layer. It does not mutate runtime, learning,
 * actuator, evidence, or authorization state.
 */
const NS = "http://www.w3.org/2000/svg";
const POLL_MS = 1200;

const anatomy = {
  metrics: null,
  history: null,
  pipeline: null,
  ioFlow: null,
  population: null,
  timer: null,
  controller: null,
};

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const finite = (v) => { const n = Number(v); return Number.isFinite(n) ? n : null; };
const clamp = (v, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const safe = (v) => v === undefined || v === null || v === "" ? "—" : String(v);

async function readJson(url, signal) {
  const r = await fetch(url, { cache: "no-store", signal });
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

function firstNumber(source, keys) {
  if (!source || typeof source !== "object") return null;
  for (const key of keys) {
    const parts = key.split(".");
    let value = source;
    for (const part of parts) value = value && typeof value === "object" ? value[part] : undefined;
    const n = finite(value);
    if (n !== null) return n;
  }
  return null;
}

function firstValue(source, keys) {
  if (!source || typeof source !== "object") return null;
  for (const key of keys) {
    const parts = key.split(".");
    let value = source;
    for (const part of parts) value = value && typeof value === "object" ? value[part] : undefined;
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return null;
}

function normalizePercent(v) {
  const n = finite(v);
  if (n === null) return null;
  return n > 1 ? clamp(n / 100) : clamp(n);
}

function nodes() {
  return $$("#wesen-organ-layer .wesen-organ").map((el, index) => ({
    el,
    id: el.dataset.node || `node-${index}`,
    kind: [...el.classList].find((c) => c.startsWith("kind-"))?.slice(5) || "connection",
    type: el.dataset.deviceType || "connection",
    label: el.dataset.wesenLabel || $("title", el)?.textContent?.split(" — ")[0] || `Knoten ${index + 1}`,
  }));
}

function bodyAnchor(node, index, groupCount) {
  const side = index % 2 === 0 ? -1 : 1;
  const row = Math.floor(index / 2);
  if (node.kind === "core") return { x: 450, y: 285 };
  if (node.kind === "internal") return { x: 450, y: 385 };
  if (node.kind === "feedback") return { x: 450, y: 475 };
  if (node.kind === "structure") return { x: 450, y: 555 };
  if (node.kind === "sensor") {
    const cols = Math.max(1, Math.ceil(groupCount / 2));
    const spread = Math.min(210, 54 * cols);
    const x = 450 + side * (82 + (row % cols) * (spread / Math.max(1, cols - 1)));
    const y = 122 + (row % 2) * 58;
    return { x: clamp(x, 95, 805), y };
  }
  if (node.kind === "actuator") {
    const upper = row < 5;
    if (upper) return { x: 450 + side * (178 + row * 34), y: 330 + row * 42 };
    const legRow = row - 5;
    return { x: 450 + side * (95 + legRow * 24), y: 535 + legRow * 36 };
  }
  return { x: 450 + side * (245 + row * 15), y: 255 + row * 48 };
}

function positionNodes() {
  const list = nodes();
  if (!list.length) return;
  const groups = new Map();
  list.forEach((n) => { if (!groups.has(n.kind)) groups.set(n.kind, []); groups.get(n.kind).push(n); });
  list.forEach((node) => {
    const group = groups.get(node.kind) || [node];
    const index = group.indexOf(node);
    const p = bodyAnchor(node, index, group.length);
    node.el.setAttribute("transform", `translate(${p.x} ${p.y})`);
    node.el.dataset.anatomyZone = node.kind === "sensor" ? "head" : node.kind === "actuator" ? (p.y < 520 ? "arm" : "leg") : node.kind === "internal" ? "torso" : node.kind;
  });
  redrawNerves(list);
  drawBodyScaffold();
}

function redrawNerves(list) {
  const core = list.find((n) => n.kind === "core")?.el;
  const coreT = core?.getAttribute("transform")?.match(/translate\(([-0-9.]+) ([-0-9.]+)\)/);
  if (!coreT) return;
  const cx = Number(coreT[1]), cy = Number(coreT[2]);
  $$("#wesen-connection-layer .wesen-nerve").forEach((path) => {
    const target = list.find((n) => n.id === path.dataset.node)?.el;
    const m = target?.getAttribute("transform")?.match(/translate\(([-0-9.]+) ([-0-9.]+)\)/);
    if (!m) return;
    const tx = Number(m[1]), ty = Number(m[2]);
    const bend = tx < cx ? -34 : 34;
    path.setAttribute("d", `M ${cx} ${cy} C ${cx + bend} ${(cy + ty) / 2} ${tx - bend} ${(cy + ty) / 2} ${tx} ${ty}`);
  });
}

function ensureBodyLayer() {
  const camera = $("#wesen-camera");
  if (!camera) return null;
  let layer = $("#wesen-anatomy-layer");
  if (!layer) {
    layer = document.createElementNS(NS, "g");
    layer.id = "wesen-anatomy-layer";
    const membrane = $("#wesen-membrane");
    membrane?.insertAdjacentElement("afterend", layer);
  }
  return layer;
}

function drawBodyScaffold() {
  const layer = ensureBodyLayer();
  if (!layer) return;
  layer.innerHTML = `
    <g class="wesen-body-silhouette" aria-hidden="true">
      <ellipse class="wesen-body-head" cx="450" cy="155" rx="120" ry="105"/>
      <path class="wesen-body-neck" d="M420 235 C420 260 405 272 392 286 L508 286 C495 272 480 260 480 235 Z"/>
      <path class="wesen-body-torso" d="M385 275 C330 300 320 370 345 465 C365 525 405 548 450 555 C495 548 535 525 555 465 C580 370 570 300 515 275 C492 295 475 305 450 305 C425 305 408 295 385 275 Z"/>
      <path class="wesen-body-spine" d="M450 300 C440 355 460 408 450 470 C442 510 448 535 450 560"/>
      <path class="wesen-body-limb left" d="M375 310 C310 330 265 370 225 430 C205 458 180 480 145 500"/>
      <path class="wesen-body-limb right" d="M525 310 C590 330 635 370 675 430 C695 458 720 480 755 500"/>
      <path class="wesen-body-limb left-leg" d="M420 520 C392 575 372 615 350 660"/>
      <path class="wesen-body-limb right-leg" d="M480 520 C508 575 528 615 550 660"/>
      <ellipse class="wesen-body-core-ring" cx="450" cy="285" rx="84" ry="58"/>
      <ellipse class="wesen-body-interoception-ring" cx="450" cy="392" rx="112" ry="88"/>
    </g>`;
}

function ensureEmpiricalPanel() {
  const sidebar = $("#tab-wesen .wesen-sidebar:last-of-type");
  if (!sidebar || $("#wesen-empirical-card")) return;
  const section = document.createElement("section");
  section.id = "wesen-empirical-card";
  section.className = "wesen-card wesen-empirical-card";
  section.innerHTML = `
    <header><span>EMPIRISCHE DATEN</span><small>LIVE_RUNTIME</small></header>
    <div id="wesen-empirical-grid" class="wesen-empirical-grid"></div>
    <div id="wesen-pipeline-body" class="wesen-pipeline-body" aria-label="Embodiment pipeline"></div>`;
  sidebar.prepend(section);
}

function empiricalRows() {
  const m = anatomy.metrics || {};
  const io = anatomy.ioFlow || {};
  const pop = anatomy.population || {};
  const hist = anatomy.history || {};
  const rows = [
    ["Neural", firstNumber(pop, ["active_fraction", "activity.active_fraction", "mean_activity", "population.active_fraction"]), "ratio"],
    ["Spike", firstNumber(pop, ["spike_count", "spikes", "total_spikes", "population.spike_count"]), "count"],
    ["Input", firstNumber(io, ["input_rate", "input_spikes", "inputs", "flow.input"]), "count"],
    ["Output", firstNumber(io, ["output_rate", "output_spikes", "outputs", "flow.output"]), "count"],
    ["Quality", firstNumber(m, ["quality", "signal_quality", "metrics.quality", "sensor_quality"]), "ratio"],
    ["Integrity", firstNumber(m, ["sensory_integrity", "metrics.sensory_integrity", "functional.sensory_integrity"]), "ratio"],
    ["Pressure", firstNumber(m, ["resource_pressure", "metrics.resource_pressure", "regulation.resource_pressure"]), "ratio"],
    ["Continuity", firstNumber(m, ["continuity_risk", "metrics.continuity_risk", "regulation.continuity_risk"]), "ratio"],
    ["History", Array.isArray(hist) ? hist.length : firstNumber(hist, ["count", "total", "history_count"]), "count"],
  ];
  return rows;
}

function formatMetric(value, mode) {
  if (value === null || value === undefined) return "—";
  if (mode === "ratio") return `${(normalizePercent(value) * 100).toFixed(0)}%`;
  return Number(value).toLocaleString("de-DE", { maximumFractionDigits: 1 });
}

function renderEmpirical() {
  ensureEmpiricalPanel();
  const grid = $("#wesen-empirical-grid");
  if (!grid) return;
  grid.innerHTML = empiricalRows().map(([label, value, mode]) => {
    const ratio = mode === "ratio" && value !== null ? normalizePercent(value) : null;
    const style = ratio === null ? "" : ` style="--empirical-fill:${(ratio * 100).toFixed(1)}%"`;
    return `<div class="wesen-empirical-row"${style}><span>${label}</span><strong>${formatMetric(value, mode)}</strong><i></i></div>`;
  }).join("");
  renderPipeline();
  applyEmpiricalBodyState();
}

function pipelineObject() {
  const p = anatomy.pipeline;
  if (!p || typeof p !== "object") return {};
  return p.pipeline && typeof p.pipeline === "object" ? p.pipeline : p;
}

function renderPipeline() {
  const root = $("#wesen-pipeline-body"); if (!root) return;
  const p = pipelineObject();
  const stages = ["sensor", "encoder", "snn", "decoder", "actuator", "feedback"];
  root.innerHTML = stages.map((name) => {
    const raw = firstValue(p, [name, `${name}.enabled`, `${name}.status`]);
    const active = raw === true || /active|ready|enabled|ok|connected/i.test(String(raw));
    const unknown = raw === null;
    return `<span class="${active ? "active" : unknown ? "unknown" : "inactive"}" title="${name}: ${safe(raw)}">${name === "sensor" ? "◉" : name === "encoder" ? "◇" : name === "snn" ? "◆" : name === "decoder" ? "◈" : name === "actuator" ? "▷" : "↻"}</span>`;
  }).join('<b aria-hidden="true">→</b>');
}

function applyEmpiricalBodyState() {
  const workspace = $("#tab-wesen"); if (!workspace) return;
  const m = anatomy.metrics || {};
  const pressure = normalizePercent(firstNumber(m, ["resource_pressure", "metrics.resource_pressure", "regulation.resource_pressure"]));
  const integrity = normalizePercent(firstNumber(m, ["sensory_integrity", "metrics.sensory_integrity", "functional.sensory_integrity"]));
  const continuity = normalizePercent(firstNumber(m, ["continuity_risk", "metrics.continuity_risk", "regulation.continuity_risk"]));
  if (pressure !== null) workspace.style.setProperty("--wesen-pressure", String(pressure));
  if (integrity !== null) workspace.style.setProperty("--wesen-integrity", String(integrity));
  if (continuity !== null) workspace.style.setProperty("--wesen-continuity", String(continuity));
}

async function pollEmpirical() {
  anatomy.controller?.abort();
  anatomy.controller = new AbortController();
  const signal = anatomy.controller.signal;
  const calls = [
    ["metrics", "/api/embodiment/metrics"],
    ["history", "/api/embodiment/history?limit=24"],
    ["pipeline", "/api/embodiment/pipeline"],
    ["ioFlow", "/api/live/io-flow"],
    ["population", "/api/live/population"],
  ];
  const results = await Promise.allSettled(calls.map(([, url]) => readJson(url, signal)));
  results.forEach((result, index) => {
    if (result.status === "fulfilled") anatomy[calls[index][0]] = result.value;
  });
  renderEmpirical();
  positionNodes();
  clearTimeout(anatomy.timer);
  anatomy.timer = setTimeout(pollEmpirical, POLL_MS);
}

function init() {
  const start = () => {
    ensureEmpiricalPanel();
    drawBodyScaffold();
    positionNodes();
    pollEmpirical();
    const layer = $("#wesen-organ-layer");
    if (layer) new MutationObserver(() => setTimeout(positionNodes, 20)).observe(layer, { childList: true });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
}

window.Brain5DWesenAnatomyV3 = { init, refresh: pollEmpirical };
init();
