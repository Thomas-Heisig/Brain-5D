/* Brain-5D adaptive organism enhancement layer.
 * Presentation-only: consumes the existing read-only Wesen DOM and telemetry.
 * It never issues runtime, learning, actuator, or evidence mutations.
 */

const SVG_NS = "http://www.w3.org/2000/svg";
const FRAME_LIMIT = 240;
const SNAPSHOT_LIMIT = 180;

export const WESEN_TERMS = Object.freeze({
  workspace: "Wesen",
  instance: "Instance",
  core: "SNN-Kern",
  adaptive: "Adaptive Regelstruktur",
  sensor: "Sensor-Endpunkt",
  actuator: "Aktor-Endpunkt",
  interoception: "Interozeption",
  environment: "Umweltquelle",
  feedback: "Rückkopplung",
  unknown: "unbekannt",
});

const organism = {
  frames: [],
  snapshots: [],
  positions: new Map(),
  camera: { x: 0, y: 0, scale: 1 },
  dragging: false,
  lastPointer: null,
  selectedSnapshot: null,
  lastSignature: "",
  lastState: "unknown",
  observer: null,
  timer: null,
};

function q(selector, root = document) { return root.querySelector(selector); }
function qa(selector, root = document) { return [...root.querySelectorAll(selector)]; }
function n(value) { const x = Number(value); return Number.isFinite(x) ? x : null; }
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
function safeText(value) { return value == null || value === "" ? WESEN_TERMS.unknown : String(value); }
function nowMs() { return performance.timeOrigin + performance.now(); }

function parseVisibleNodes() {
  return qa("#wesen-organ-layer .wesen-organ").map((el, index) => {
    const label = q(".wesen-organ-label", el)?.textContent?.trim() || `Knoten ${index + 1}`;
    const value = q(".wesen-organ-value", el)?.textContent?.trim() || "—";
    const id = el.dataset.node || `node-${index}`;
    const classes = [...el.classList];
    const kindClass = classes.find((c) => c.startsWith("kind-"));
    const kind = kindClass ? kindClass.slice(5) : "connection";
    return { id, label, value, kind, el };
  });
}

function desiredRadius(kind) {
  if (kind === "core") return 0;
  if (kind === "internal") return 120;
  if (kind === "feedback") return 155;
  if (kind === "structure") return 185;
  if (kind === "sensor") return 270;
  if (kind === "actuator") return 300;
  return 235;
}

function seedPosition(node, index, total) {
  const angleBias = node.kind === "sensor" ? Math.PI : node.kind === "actuator" ? 0 : Math.PI / 2;
  const spread = node.kind === "sensor" || node.kind === "actuator" ? Math.PI * 0.78 : Math.PI * 1.6;
  const t = total <= 1 ? 0.5 : index / (total - 1);
  const angle = angleBias - spread / 2 + spread * t;
  const r = desiredRadius(node.kind);
  return { x: 450 + Math.cos(angle) * r, y: 350 + Math.sin(angle) * r, vx: 0, vy: 0 };
}

function forceLayout(nodes) {
  const grouped = new Map();
  nodes.forEach((node) => {
    if (!grouped.has(node.kind)) grouped.set(node.kind, []);
    grouped.get(node.kind).push(node);
  });
  nodes.forEach((node) => {
    if (!organism.positions.has(node.id)) {
      const group = grouped.get(node.kind) || [node];
      organism.positions.set(node.id, seedPosition(node, group.indexOf(node), group.length));
    }
  });
  for (const id of [...organism.positions.keys()]) if (!nodes.some((node) => node.id === id)) organism.positions.delete(id);

  for (let step = 0; step < 26; step += 1) {
    nodes.forEach((a, i) => {
      const pa = organism.positions.get(a.id);
      if (!pa) return;
      if (a.kind === "core") { pa.x += (450 - pa.x) * 0.4; pa.y += (350 - pa.y) * 0.4; return; }
      const dx = pa.x - 450, dy = pa.y - 350;
      const dist = Math.max(1, Math.hypot(dx, dy));
      const target = desiredRadius(a.kind);
      const spring = (target - dist) * 0.018;
      pa.vx -= (dx / dist) * spring;
      pa.vy -= (dy / dist) * spring;

      nodes.slice(i + 1).forEach((b) => {
        const pb = organism.positions.get(b.id); if (!pb) return;
        let rx = pa.x - pb.x, ry = pa.y - pb.y;
        const d2 = Math.max(900, rx * rx + ry * ry);
        const f = 1550 / d2;
        const d = Math.sqrt(d2); rx /= d; ry /= d;
        pa.vx += rx * f; pa.vy += ry * f; pb.vx -= rx * f; pb.vy -= ry * f;
      });
    });
    nodes.forEach((node) => {
      const p = organism.positions.get(node.id); if (!p) return;
      p.vx *= 0.72; p.vy *= 0.72;
      p.x = clamp(p.x + p.vx, 75, 825); p.y = clamp(p.y + p.vy, 70, 630);
    });
  }
  return organism.positions;
}

function cross(o, a, b) { return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x); }
function convexHull(points) {
  const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y);
  if (sorted.length <= 2) return sorted;
  const lower = [];
  for (const p of sorted) { while (lower.length >= 2 && cross(lower.at(-2), lower.at(-1), p) <= 0) lower.pop(); lower.push(p); }
  const upper = [];
  for (const p of [...sorted].reverse()) { while (upper.length >= 2 && cross(upper.at(-2), upper.at(-1), p) <= 0) upper.pop(); upper.push(p); }
  lower.pop(); upper.pop(); return lower.concat(upper);
}

function hullPath(hull, padding = 62) {
  if (hull.length < 3) return "";
  const cx = hull.reduce((s, p) => s + p.x, 0) / hull.length;
  const cy = hull.reduce((s, p) => s + p.y, 0) / hull.length;
  const expanded = hull.map((p) => {
    const dx = p.x - cx, dy = p.y - cy, d = Math.max(1, Math.hypot(dx, dy));
    return { x: p.x + dx / d * padding, y: p.y + dy / d * padding };
  });
  return `${expanded.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ")} Z`;
}

function applyMorphology() {
  const nodes = parseVisibleNodes();
  if (!nodes.length) return;
  const positions = forceLayout(nodes);
  nodes.forEach((node) => {
    const p = positions.get(node.id); if (!p) return;
    node.el.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
  });
  const membrane = q("#wesen-membrane");
  const bodyPoints = nodes.filter((node) => node.kind !== "environment").map((node) => positions.get(node.id)).filter(Boolean);
  const hull = convexHull(bodyPoints);
  const path = hullPath(hull);
  if (membrane && path) membrane.setAttribute("d", path);
  syncNerves(nodes, positions);
  renderSatellites(nodes, positions);
  captureFrame(nodes, positions, path);
}

function syncNerves(nodes, positions) {
  const core = nodes.find((node) => node.kind === "core") || nodes[0];
  const cp = positions.get(core.id); if (!cp) return;
  qa("#wesen-connection-layer .wesen-nerve").forEach((path) => {
    const id = path.dataset.node;
    const p = positions.get(id); if (!p) return;
    const bend = id?.includes("actuator") ? 28 : -28;
    path.setAttribute("d", `M ${cp.x} ${cp.y} Q ${(cp.x + p.x) / 2} ${(cp.y + p.y) / 2 + bend} ${p.x} ${p.y}`);
  });
}

function satelliteSources(nodes) {
  const sources = [];
  const env = q("#wesen-environment-label")?.textContent?.trim();
  if (env && !/nicht beobachtet|unbekannt|—/.test(env)) sources.push({ id: "env", label: env, kind: "environment" });
  nodes.filter((node) => node.kind === "sensor").forEach((node) => {
    const raw = node.label.toLowerCase();
    if (/network|internet|weather|wetter|wifi|camera|kamera|micro|audio/.test(raw)) sources.push({ id: `sat-${node.id}`, label: node.label, kind: "environment", target: node.id });
  });
  return sources.slice(0, 8);
}

function renderSatellites(nodes, positions) {
  const layer = q("#wesen-environment-layer"); if (!layer) return;
  const sources = satelliteSources(nodes);
  layer.innerHTML = "";
  sources.forEach((source, index) => {
    const angle = -Math.PI * 0.82 + (index / Math.max(1, sources.length - 1)) * Math.PI * 1.64;
    const x = 450 + Math.cos(angle) * 395, y = 350 + Math.sin(angle) * 300;
    const g = document.createElementNS(SVG_NS, "g"); g.setAttribute("class", "wesen-satellite"); g.setAttribute("transform", `translate(${x} ${y})`);
    g.innerHTML = `<circle r="24"/><text y="4">EXT</text><text class="wesen-satellite-label" x="31" y="4">${source.label.slice(0, 22)}</text>`;
    layer.appendChild(g);
    if (source.target && positions.get(source.target)) {
      const p = positions.get(source.target); const line = document.createElementNS(SVG_NS, "line");
      line.setAttribute("class", "wesen-satellite-link"); line.setAttribute("x1", x); line.setAttribute("y1", y); line.setAttribute("x2", p.x); line.setAttribute("y2", p.y); layer.prepend(line);
    }
  });
}

function captureFrame(nodes, positions, membrane) {
  const frame = {
    at: nowMs(),
    membrane,
    nodes: nodes.map((node) => ({ id: node.id, label: node.label, kind: node.kind, value: node.value, ...(positions.get(node.id) || {}) })),
  };
  organism.frames.push(frame); if (organism.frames.length > FRAME_LIMIT) organism.frames.shift();
  const signature = frame.nodes.map((node) => `${node.kind}:${node.label}`).sort().join("|");
  if (signature !== organism.lastSignature) {
    organism.lastSignature = signature;
    organism.snapshots.push({ ...frame, signature });
    if (organism.snapshots.length > SNAPSHOT_LIMIT) organism.snapshots.shift();
    persistSnapshots();
    renderTimeline();
  }
  renderDelayedClone();
}

function loopLatency() {
  const rows = qa("#wesen-self-metrics > div");
  const row = rows.find((r) => /Loop-Latenz/i.test(r.textContent || ""));
  return n(row?.querySelector("strong")?.textContent?.replace(/[^0-9.,-]/g, "")?.replace(",", "."));
}

function delayedFrame() {
  const latency = loopLatency();
  if (latency === null) return organism.frames.at(-1) || null;
  const target = nowMs() - latency;
  let best = organism.frames[0] || null;
  for (const frame of organism.frames) if (frame.at <= target) best = frame; else break;
  return best;
}

function renderDelayedClone() {
  const svg = q("#wesen-self-svg"); if (!svg) return;
  const frame = organism.selectedSnapshot || delayedFrame(); if (!frame) return;
  const sx = 0.31, sy = 0.235;
  const core = frame.nodes.find((node) => node.kind === "core") || frame.nodes[0];
  const edges = frame.nodes.filter((node) => node.id !== core?.id).map((node) => `<line x1="${18 + core.x * sx}" y1="${9 + core.y * sy}" x2="${18 + node.x * sx}" y2="${9 + node.y * sy}"/>`).join("");
  const dots = frame.nodes.map((node) => `<circle class="kind-${node.kind}" cx="${18 + node.x * sx}" cy="${9 + node.y * sy}" r="${node.kind === "core" ? 8 : 3.8}"/>`).join("");
  const path = frame.membrane ? frame.membrane.replace(/(-?\d+(?:\.\d+)?)/g, (match, raw, offset, full) => {
    const before = full.slice(Math.max(0, offset - 1), offset);
    const numeric = Number(match);
    // Coordinates alternate in SVG path; transform by token index below is safer, so leave clone hull implicit.
    return String(numeric);
  }) : "";
  svg.innerHTML = `<g class="wesen-self-body wesen-delayed-clone">${edges}${dots}</g><text x="150" y="170" text-anchor="middle">${organism.selectedSnapshot ? "Historischer Morphologie-Snapshot" : `Echo ${loopLatency() === null ? "ohne gemessene Latenz" : `${loopLatency().toFixed(1)} ms`}`}</text>`;
}

function loadSnapshots() {
  try {
    const raw = localStorage.getItem("brain5d.wesen.morphology.v1");
    if (raw) organism.snapshots = JSON.parse(raw).slice(-SNAPSHOT_LIMIT);
  } catch (_) { organism.snapshots = []; }
}
function persistSnapshots() {
  try { localStorage.setItem("brain5d.wesen.morphology.v1", JSON.stringify(organism.snapshots)); } catch (_) { /* browser storage optional */ }
}
function ensureTimeline() {
  const history = q("#wesen-morphology-history"); if (!history || q("#wesen-timeline")) return;
  const wrap = document.createElement("div"); wrap.id = "wesen-timeline"; wrap.className = "wesen-timeline";
  wrap.innerHTML = `<input type="range" min="0" max="0" value="0" step="1" aria-label="Morphologie-Zeitreise"><div><span>älter</span><strong>Live</strong><span>jetzt</span></div><button type="button">Zurück zu Live</button>`;
  history.before(wrap);
  const input = q("input", wrap); const label = q("strong", wrap); const button = q("button", wrap);
  input.addEventListener("input", () => {
    const index = Number(input.value);
    organism.selectedSnapshot = organism.snapshots[index] || null;
    label.textContent = organism.selectedSnapshot ? new Date(organism.selectedSnapshot.at).toLocaleString("de-DE") : "Live";
    renderDelayedClone();
  });
  button.addEventListener("click", () => { organism.selectedSnapshot = null; input.value = String(Math.max(0, organism.snapshots.length - 1)); label.textContent = "Live"; renderDelayedClone(); });
}
function renderTimeline() {
  ensureTimeline(); const input = q("#wesen-timeline input"); if (!input) return;
  input.max = String(Math.max(0, organism.snapshots.length - 1));
  if (!organism.selectedSnapshot) input.value = input.max;
}

function currentVisualState() {
  const reaction = q("#wesen-reaction-label")?.textContent?.toLowerCase() || "";
  if (/thermal|thermisch/.test(reaction)) return "thermal";
  if (/sensorverlust|sensor loss/.test(reaction)) return "sensor-loss";
  if (/netzwerk|network/.test(reaction)) return "network-isolation";
  if (/aktorfehler|actuator/.test(reaction)) return "actuator-fault";
  if (/recovery|erholung|wiederher/.test(reaction)) return "recovery";
  if (/unbekannt|unknown|nicht verfügbar/.test(reaction)) return "unknown";
  if (/ressource|belastung|pressure/.test(reaction)) return "pressure";
  return "stable";
}
function applyStateMachine() {
  const workspace = q("#tab-wesen"); if (!workspace) return;
  const next = currentVisualState();
  if (next !== organism.lastState) { workspace.dataset.organismState = next; organism.lastState = next; }
}

function applyCamera() {
  const camera = q("#wesen-camera"); if (!camera) return;
  camera.style.setProperty("--wesen-camera-x", `${organism.camera.x}px`);
  camera.style.setProperty("--wesen-camera-y", `${organism.camera.y}px`);
  camera.style.setProperty("--wesen-camera-scale", String(organism.camera.scale));
}
function bindCamera() {
  const stage = q("#wesen-stage"); if (!stage || stage.dataset.organismCamera) return;
  stage.dataset.organismCamera = "1";
  stage.addEventListener("wheel", (event) => {
    event.preventDefault(); event.stopImmediatePropagation();
    const rect = stage.getBoundingClientRect(); const mx = event.clientX - rect.left, my = event.clientY - rect.top;
    const old = organism.camera.scale; const next = clamp(old * (event.deltaY < 0 ? 1.12 : 0.89), 0.55, 2.5);
    organism.camera.x = mx - (mx - organism.camera.x) * (next / old);
    organism.camera.y = my - (my - organism.camera.y) * (next / old);
    organism.camera.scale = next; applyCamera();
  }, { passive: false, capture: true });
  stage.addEventListener("pointerdown", (event) => { if (event.button !== 0) return; organism.dragging = true; organism.lastPointer = { x: event.clientX, y: event.clientY }; stage.setPointerCapture?.(event.pointerId); });
  stage.addEventListener("pointermove", (event) => { if (!organism.dragging || !organism.lastPointer) return; organism.camera.x += event.clientX - organism.lastPointer.x; organism.camera.y += event.clientY - organism.lastPointer.y; organism.lastPointer = { x: event.clientX, y: event.clientY }; applyCamera(); });
  stage.addEventListener("pointerup", () => { organism.dragging = false; organism.lastPointer = null; });
  stage.addEventListener("dblclick", () => { organism.camera = { x: 0, y: 0, scale: 1 }; applyCamera(); });
}

function focusSelection() {
  const nodes = qa("#wesen-organ-layer .wesen-organ");
  const selected = nodes.find((node) => node.classList.contains("selected"));
  nodes.forEach((node) => node.classList.toggle("wesen-defocused", Boolean(selected && node !== selected)));
}

function addCausalTracerHooks() {
  const events = q("#wesen-events"); if (!events || events.dataset.tracerHooks) return;
  events.dataset.tracerHooks = "1";
  events.addEventListener("click", (event) => {
    const row = event.target.closest(".wesen-event-row"); if (!row) return;
    const token = row.textContent?.match(/(?:event|decision|action|receipt)[-_:# ]*[a-z0-9-]+/i)?.[0];
    if (!token) return;
    q("#wesen-stage-subtitle").textContent = `Kausal-Tracer: ${token}`;
    q("#wesen-svg")?.classList.add("show-causality", "wesen-tracer-active");
  });
}

function enhance() {
  if (!q("#tab-wesen")) return;
  applyMorphology();
  applyStateMachine();
  focusSelection();
  renderTimeline();
  bindCamera();
  addCausalTracerHooks();
}

export function initWesenOrganism() {
  loadSnapshots();
  const start = () => {
    enhance();
    const root = q("#tab-wesen");
    if (root && !organism.observer) {
      organism.observer = new MutationObserver(() => queueMicrotask(enhance));
      organism.observer.observe(root, { childList: true, subtree: true, characterData: true });
    }
    clearInterval(organism.timer); organism.timer = setInterval(enhance, 1200);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
}

initWesenOrganism();
