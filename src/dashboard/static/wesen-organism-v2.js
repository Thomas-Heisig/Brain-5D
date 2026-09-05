/* Brain-5D adaptive organism v2. Presentation-only and read-only. */
const NS = "http://www.w3.org/2000/svg";
const FRAME_LIMIT = 240;
const SNAP_LIMIT = 180;

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

const model = {
  positions: new Map(), frames: [], snapshots: [], signature: "", selected: null,
  camera: { x: 0, y: 0, scale: 1 }, dragging: false, pointer: null, timer: null, observer: null,
};
const q = (s, r = document) => r.querySelector(s);
const qa = (s, r = document) => [...r.querySelectorAll(s)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const number = (v) => { const n = Number(v); return Number.isFinite(n) ? n : null; };

function nodes() {
  return qa("#wesen-organ-layer .wesen-organ").map((el, index) => {
    const kindClass = [...el.classList].find((c) => c.startsWith("kind-"));
    return {
      id: el.dataset.node || `node-${index}`,
      kind: kindClass ? kindClass.slice(5) : "connection",
      label: q(".wesen-organ-label", el)?.textContent?.trim() || `Knoten ${index + 1}`,
      value: q(".wesen-organ-value", el)?.textContent?.trim() || "—",
      el,
    };
  });
}
function radius(kind) {
  return ({ core: 0, internal: 118, feedback: 155, structure: 190, connection: 225, sensor: 275, actuator: 305 })[kind] ?? 230;
}
function initial(node, index, count) {
  const base = node.kind === "sensor" ? Math.PI : node.kind === "actuator" ? 0 : Math.PI / 2;
  const spread = /sensor|actuator/.test(node.kind) ? Math.PI * 0.8 : Math.PI * 1.5;
  const t = count < 2 ? 0.5 : index / (count - 1);
  const angle = base - spread / 2 + spread * t, r = radius(node.kind);
  return { x: 450 + Math.cos(angle) * r, y: 350 + Math.sin(angle) * r, vx: 0, vy: 0 };
}
function layout(list) {
  const groups = new Map();
  list.forEach((node) => { if (!groups.has(node.kind)) groups.set(node.kind, []); groups.get(node.kind).push(node); });
  list.forEach((node) => {
    if (!model.positions.has(node.id)) {
      const group = groups.get(node.kind); model.positions.set(node.id, initial(node, group.indexOf(node), group.length));
    }
  });
  [...model.positions.keys()].forEach((id) => { if (!list.some((node) => node.id === id)) model.positions.delete(id); });
  for (let step = 0; step < 24; step += 1) {
    list.forEach((a, ai) => {
      const pa = model.positions.get(a.id); if (!pa) return;
      if (a.kind === "core") { pa.x += (450 - pa.x) * .45; pa.y += (350 - pa.y) * .45; return; }
      const dx = pa.x - 450, dy = pa.y - 350, d = Math.max(1, Math.hypot(dx, dy));
      const spring = (radius(a.kind) - d) * .02; pa.vx -= dx / d * spring; pa.vy -= dy / d * spring;
      list.slice(ai + 1).forEach((b) => {
        const pb = model.positions.get(b.id); if (!pb) return;
        let rx = pa.x - pb.x, ry = pa.y - pb.y; const d2 = Math.max(1000, rx * rx + ry * ry); const dd = Math.sqrt(d2); rx /= dd; ry /= dd;
        const force = 1900 / d2; pa.vx += rx * force; pa.vy += ry * force; pb.vx -= rx * force; pb.vy -= ry * force;
      });
    });
    list.forEach((node) => { const p = model.positions.get(node.id); if (!p) return; p.vx *= .72; p.vy *= .72; p.x = clamp(p.x + p.vx, 75, 825); p.y = clamp(p.y + p.vy, 70, 625); });
  }
  return model.positions;
}
function cross(o, a, b) { return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x); }
function hull(points) {
  const p = [...points].sort((a, b) => a.x - b.x || a.y - b.y); if (p.length < 3) return p;
  const lower = [], upper = [];
  p.forEach((x) => { while (lower.length > 1 && cross(lower.at(-2), lower.at(-1), x) <= 0) lower.pop(); lower.push(x); });
  [...p].reverse().forEach((x) => { while (upper.length > 1 && cross(upper.at(-2), upper.at(-1), x) <= 0) upper.pop(); upper.push(x); });
  lower.pop(); upper.pop(); return lower.concat(upper);
}
function hullPath(points) {
  if (points.length < 3) return "";
  const cx = points.reduce((s, p) => s + p.x, 0) / points.length, cy = points.reduce((s, p) => s + p.y, 0) / points.length;
  const expanded = points.map((p) => { const dx = p.x - cx, dy = p.y - cy, d = Math.max(1, Math.hypot(dx, dy)); return { x: p.x + dx / d * 62, y: p.y + dy / d * 62 }; });
  return expanded.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ") + " Z";
}
function syncEdges(list, pos) {
  const core = list.find((node) => node.kind === "core") || list[0], cp = core && pos.get(core.id); if (!cp) return;
  qa("#wesen-connection-layer .wesen-nerve").forEach((edge) => {
    const p = pos.get(edge.dataset.node); if (!p) return;
    const node = list.find((item) => item.id === edge.dataset.node), bend = node?.kind === "actuator" ? 30 : -24;
    edge.setAttribute("d", `M ${cp.x} ${cp.y} Q ${(cp.x + p.x) / 2} ${(cp.y + p.y) / 2 + bend} ${p.x} ${p.y}`);
  });
}
function externalSources(list) {
  const result = [], env = q("#wesen-environment-label")?.textContent?.trim();
  if (env && !/nicht beobachtet|unbekannt|—/i.test(env)) result.push({ label: env });
  list.filter((node) => node.kind === "sensor" && /network|internet|weather|wetter|wifi|camera|kamera|micro|audio/i.test(node.label)).forEach((node) => result.push({ label: node.label, target: node.id }));
  return result.slice(0, 8);
}
function satellites(list, pos) {
  const layer = q("#wesen-environment-layer"); if (!layer) return; layer.replaceChildren();
  externalSources(list).forEach((source, i, all) => {
    const angle = -Math.PI * .82 + i / Math.max(1, all.length - 1) * Math.PI * 1.64, x = 450 + Math.cos(angle) * 400, y = 350 + Math.sin(angle) * 300;
    if (source.target && pos.get(source.target)) { const p = pos.get(source.target), line = document.createElementNS(NS, "line"); line.setAttribute("class", "wesen-satellite-link"); line.setAttribute("x1", x); line.setAttribute("y1", y); line.setAttribute("x2", p.x); line.setAttribute("y2", p.y); layer.appendChild(line); }
    const g = document.createElementNS(NS, "g"); g.setAttribute("class", "wesen-satellite"); g.setAttribute("transform", `translate(${x} ${y})`); g.innerHTML = `<circle r="23"/><text y="4">EXT</text><text class="wesen-satellite-label" x="30" y="4">${source.label.slice(0, 20)}</text>`; layer.appendChild(g);
  });
}
function capture(list, pos, membrane) {
  const frame = { at: Date.now(), membrane, nodes: list.map((node) => ({ id: node.id, kind: node.kind, label: node.label, value: node.value, ...pos.get(node.id) })) };
  model.frames.push(frame); if (model.frames.length > FRAME_LIMIT) model.frames.shift();
  const signature = frame.nodes.map((x) => `${x.kind}:${x.label}`).sort().join("|");
  if (signature !== model.signature) { model.signature = signature; model.snapshots.push({ ...frame, signature }); if (model.snapshots.length > SNAP_LIMIT) model.snapshots.shift(); saveSnapshots(); timeline(); }
  delayedClone();
}
function latency() {
  const row = qa("#wesen-self-metrics > div").find((el) => /Loop-Latenz/i.test(el.textContent || ""));
  const raw = row?.querySelector("strong")?.textContent?.replace(/[^0-9.,-]/g, "")?.replace(",", "."); return number(raw);
}
function delayed() {
  if (model.selected) return model.selected; const ms = latency(); if (ms === null) return model.frames.at(-1) || null;
  const target = Date.now() - ms; let result = model.frames[0] || null; for (const frame of model.frames) { if (frame.at <= target) result = frame; else break; } return result;
}
function delayedClone() {
  const svg = q("#wesen-self-svg"), frame = delayed(); if (!svg || !frame?.nodes.length) return;
  const core = frame.nodes.find((x) => x.kind === "core") || frame.nodes[0], sx = .31, sy = .235;
  const edges = frame.nodes.filter((x) => x.id !== core.id).map((x) => `<line x1="${18 + core.x * sx}" y1="${9 + core.y * sy}" x2="${18 + x.x * sx}" y2="${9 + x.y * sy}"/>`).join("");
  const dots = frame.nodes.map((x) => `<circle class="kind-${x.kind}" cx="${18 + x.x * sx}" cy="${9 + x.y * sy}" r="${x.kind === "core" ? 8 : 3.8}"/>`).join("");
  svg.innerHTML = `<g class="wesen-self-body wesen-delayed-clone">${edges}${dots}</g><text x="150" y="170" text-anchor="middle">${model.selected ? "Historischer Morphologie-Snapshot" : `Echo ${latency() === null ? "ohne gemessene Latenz" : `${latency().toFixed(1)} ms`}`}</text>`;
}
function loadSnapshots() { try { const raw = localStorage.getItem("brain5d.wesen.morphology.v2"); if (raw) model.snapshots = JSON.parse(raw).slice(-SNAP_LIMIT); } catch (_) { model.snapshots = []; } }
function saveSnapshots() { try { localStorage.setItem("brain5d.wesen.morphology.v2", JSON.stringify(model.snapshots)); } catch (_) { /* optional client history */ } }
function ensureTimeline() {
  const history = q("#wesen-morphology-history"); if (!history || q("#wesen-timeline")) return;
  const wrap = document.createElement("div"); wrap.id = "wesen-timeline"; wrap.className = "wesen-timeline"; wrap.innerHTML = '<input type="range" min="0" max="0" value="0" step="1" aria-label="Morphologie-Zeitreise"><div><span>älter</span><strong>Live</strong><span>jetzt</span></div><button type="button">Live</button>'; history.before(wrap);
  const input = q("input", wrap), label = q("strong", wrap); input.addEventListener("input", () => { model.selected = model.snapshots[Number(input.value)] || null; label.textContent = model.selected ? new Date(model.selected.at).toLocaleString("de-DE") : "Live"; delayedClone(); });
  q("button", wrap).addEventListener("click", () => { model.selected = null; input.value = input.max; label.textContent = "Live"; delayedClone(); });
}
function timeline() { ensureTimeline(); const input = q("#wesen-timeline input"); if (!input) return; input.max = String(Math.max(0, model.snapshots.length - 1)); if (!model.selected) input.value = input.max; }
function visualState() {
  const t = q("#wesen-reaction-label")?.textContent?.toLowerCase() || "";
  if (/thermal|thermisch/.test(t)) return "thermal"; if (/sensorverlust/.test(t)) return "sensor-loss"; if (/netzwerk/.test(t)) return "network-isolation"; if (/aktorfehler/.test(t)) return "actuator-fault"; if (/recovery|erholung/.test(t)) return "recovery"; if (/unbekannt|nicht verfügbar/.test(t)) return "unknown"; if (/ressource|belastung/.test(t)) return "pressure"; return "stable";
}
function camera() {
  const el = q("#wesen-camera"); if (!el) return; el.style.setProperty("--wesen-camera-x", `${model.camera.x}px`); el.style.setProperty("--wesen-camera-y", `${model.camera.y}px`); el.style.setProperty("--wesen-camera-scale", String(model.camera.scale));
}
function bindCamera() {
  const stage = q("#wesen-stage"); if (!stage || stage.dataset.organismCamera) return; stage.dataset.organismCamera = "1";
  stage.addEventListener("wheel", (event) => { event.preventDefault(); event.stopImmediatePropagation(); const rect = stage.getBoundingClientRect(), mx = event.clientX - rect.left, my = event.clientY - rect.top, old = model.camera.scale, next = clamp(old * (event.deltaY < 0 ? 1.12 : .89), .55, 2.5); model.camera.x = mx - (mx - model.camera.x) * next / old; model.camera.y = my - (my - model.camera.y) * next / old; model.camera.scale = next; camera(); }, { passive: false, capture: true });
  stage.addEventListener("pointerdown", (event) => { if (event.button !== 0) return; model.dragging = true; model.pointer = { x: event.clientX, y: event.clientY }; });
  stage.addEventListener("pointermove", (event) => { if (!model.dragging || !model.pointer) return; model.camera.x += event.clientX - model.pointer.x; model.camera.y += event.clientY - model.pointer.y; model.pointer = { x: event.clientX, y: event.clientY }; camera(); });
  stage.addEventListener("pointerup", () => { model.dragging = false; model.pointer = null; });
  stage.addEventListener("pointerleave", () => { model.dragging = false; model.pointer = null; });
  stage.addEventListener("dblclick", () => { model.camera = { x: 0, y: 0, scale: 1 }; camera(); });
}
function focus() { const all = qa("#wesen-organ-layer .wesen-organ"), selected = all.find((x) => x.classList.contains("selected")); all.forEach((x) => x.classList.toggle("wesen-defocused", Boolean(selected && x !== selected))); }
function tracer() {
  const events = q("#wesen-events"); if (!events || events.dataset.tracer) return; events.dataset.tracer = "1";
  events.addEventListener("click", (event) => { const row = event.target.closest(".wesen-event-row"), token = row?.textContent?.match(/(?:event|decision|action|receipt)[-_:# ]*[a-z0-9-]+/i)?.[0]; if (!token) return; const subtitle = q("#wesen-stage-subtitle"); if (subtitle) subtitle.textContent = `Kausal-Tracer: ${token}`; q("#wesen-svg")?.classList.add("show-causality", "wesen-tracer-active"); });
}
function enhance() {
  const list = nodes(); if (!list.length) return; const pos = layout(list); list.forEach((node) => { const p = pos.get(node.id); node.el.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`); });
  const membrane = q("#wesen-membrane"), path = hullPath(hull(list.map((node) => pos.get(node.id)).filter(Boolean))); if (membrane && path) membrane.setAttribute("d", path); syncEdges(list, pos); satellites(list, pos); capture(list, pos, path); const workspace = q("#tab-wesen"); if (workspace) workspace.dataset.organismState = visualState(); focus(); timeline(); bindCamera(); tracer();
}
export function initWesenOrganismV2() {
  loadSnapshots(); const start = () => { enhance(); const layer = q("#wesen-organ-layer"); if (layer && !model.observer) { model.observer = new MutationObserver(() => setTimeout(enhance, 0)); model.observer.observe(layer, { childList: true }); } clearInterval(model.timer); model.timer = setInterval(enhance, 1500); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
}
initWesenOrganismV2();
