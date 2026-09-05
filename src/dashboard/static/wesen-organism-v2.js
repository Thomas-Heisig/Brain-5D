/* Brain-5D adaptive organism v2. Presentation-only and read-only. */
const NS = "http://www.w3.org/2000/svg";
const FRAME_LIMIT = 240;
const SNAP_LIMIT = 180;
const ICON_DOCK_ID = "wesen-icon-dock";

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
const number = (v) => { const x = Number(v); return Number.isFinite(x) ? x : null; };
const escapeText = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function deviceType(label, kind) {
  const raw = String(label || "").toLowerCase();
  if (kind === "core") return "core";
  if (kind === "internal") return "internal";
  if (kind === "feedback") return "feedback";
  if (kind === "structure") return "structure";
  if (/camera|kamera|webcam|vision/.test(raw)) return "camera";
  if (/micro|mikro|audio input|capture/.test(raw)) return "microphone";
  if (/speaker|lautsprecher|audio output|headphone|kopfhörer/.test(raw)) return "speaker";
  if (/printer|drucker|print/.test(raw)) return "printer";
  if (/display|monitor|screen|samsung|hdmi/.test(raw)) return "display";
  if (/nvidia|radeon|gpu|graphics|geforce/.test(raw)) return "gpu";
  if (/network|internet|ethernet|wifi|wlan|wan|lan|adapter/.test(raw)) return "network";
  if (/usb|serial|com port/.test(raw)) return "usb";
  if (/disk|storage|ssd|nvme|drive|filesystem|file/.test(raw)) return "storage";
  if (/robot|motor|arm|servo/.test(raw)) return "robot";
  if (/weather|wetter|climate/.test(raw)) return "weather";
  if (/temperature|thermal|fan|cpu|memory|ram/.test(raw)) return "system";
  return kind === "sensor" ? "sensor" : kind === "actuator" ? "actuator" : "connection";
}

function iconFor(type) {
  return ({
    core: "◆", internal: "◈", feedback: "↻", structure: "⬡",
    camera: "◉", microphone: "◒", speaker: "◖", printer: "▤",
    display: "▣", gpu: "◇", network: "⌁", usb: "⊣", storage: "▱",
    robot: "✣", weather: "☁", system: "◎", sensor: "○", actuator: "▷", connection: "·",
  })[type] || "·";
}

function nodes() {
  return qa("#wesen-organ-layer .wesen-organ").map((el, index) => {
    const kindClass = [...el.classList].find((c) => c.startsWith("kind-"));
    const kind = kindClass ? kindClass.slice(5) : "connection";
    const labelNode = q(".wesen-organ-label", el);
    const valueNode = q(".wesen-organ-value", el);
    const originalLabel = el.dataset.wesenLabel || labelNode?.textContent?.trim() || `Knoten ${index + 1}`;
    const originalValue = valueNode?.textContent?.trim() || "—";
    el.dataset.wesenLabel = originalLabel;
    return { id: el.dataset.node || `node-${index}`, kind, label: originalLabel, value: originalValue, type: deviceType(originalLabel, kind), el };
  });
}

function decorateNodes(list) {
  list.forEach((node) => {
    const icon = iconFor(node.type);
    node.el.dataset.deviceType = node.type;
    node.el.setAttribute("aria-label", `${node.label}: ${node.value}`);
    node.el.setAttribute("tabindex", "0");
    const iconNode = q(".wesen-organ-icon", node.el);
    const labelNode = q(".wesen-organ-label", node.el);
    const valueNode = q(".wesen-organ-value", node.el);
    if (iconNode) iconNode.textContent = icon;
    if (labelNode) labelNode.textContent = "";
    if (valueNode) valueNode.textContent = "";
    let title = q("title", node.el);
    if (!title) { title = document.createElementNS(NS, "title"); node.el.prepend(title); }
    title.textContent = `${node.label} — ${node.value}`;
  });
  qa("#wesen-pin-layer .wesen-data-pin").forEach((pin, index) => {
    const node = list[index];
    if (node) { pin.dataset.node = node.id; pin.dataset.deviceType = node.type; }
  });
}

function ringRadius(kind, index, count) {
  const base = ({ core: 0, internal: 112, feedback: 148, structure: 184, connection: 226, sensor: 260, actuator: 284 })[kind] ?? 230;
  if (!/sensor|actuator/.test(kind) || count < 8) return base;
  const ring = index % 2;
  return base + ring * 76;
}
function initial(node, index, count) {
  const base = node.kind === "sensor" ? Math.PI : node.kind === "actuator" ? 0 : Math.PI / 2;
  const spread = /sensor|actuator/.test(node.kind) ? Math.PI * .92 : Math.PI * 1.55;
  const slot = count > 1 ? index / (count - 1) : .5;
  const angle = base - spread / 2 + spread * slot;
  const r = ringRadius(node.kind, index, count);
  return { x: 450 + Math.cos(angle) * r, y: 350 + Math.sin(angle) * r, vx: 0, vy: 0 };
}
function desiredRadius(node, index, count) { return ringRadius(node.kind, index, count); }
function layout(list) {
  const groups = new Map();
  list.forEach((node) => { if (!groups.has(node.kind)) groups.set(node.kind, []); groups.get(node.kind).push(node); });
  list.forEach((node) => {
    if (!model.positions.has(node.id)) {
      const group = groups.get(node.kind) || [node];
      model.positions.set(node.id, initial(node, group.indexOf(node), group.length));
    }
  });
  [...model.positions.keys()].forEach((id) => { if (!list.some((node) => node.id === id)) model.positions.delete(id); });

  for (let step = 0; step < 38; step += 1) {
    list.forEach((a, ai) => {
      const pa = model.positions.get(a.id); if (!pa) return;
      if (a.kind === "core") { pa.x += (450 - pa.x) * .5; pa.y += (350 - pa.y) * .5; return; }
      const group = groups.get(a.kind) || [a];
      const desired = desiredRadius(a, group.indexOf(a), group.length);
      const dx = pa.x - 450, dy = pa.y - 350, d = Math.max(1, Math.hypot(dx, dy));
      const spring = (desired - d) * .026;
      pa.vx -= dx / d * spring; pa.vy -= dy / d * spring;
      list.slice(ai + 1).forEach((b) => {
        const pb = model.positions.get(b.id); if (!pb) return;
        let rx = pa.x - pb.x, ry = pa.y - pb.y;
        const minDistance = a.kind === b.kind ? 72 : 58;
        const d2 = Math.max(minDistance * minDistance, rx * rx + ry * ry);
        const dd = Math.sqrt(d2); rx /= dd; ry /= dd;
        const force = (a.kind === b.kind ? 7200 : 4200) / d2;
        pa.vx += rx * force; pa.vy += ry * force; pb.vx -= rx * force; pb.vy -= ry * force;
      });
    });
    list.forEach((node) => {
      const p = model.positions.get(node.id); if (!p) return;
      p.vx *= .66; p.vy *= .66;
      p.x = clamp(p.x + p.vx, 52, 848); p.y = clamp(p.y + p.vy, 52, 648);
    });
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
  const expanded = points.map((p) => { const dx = p.x - cx, dy = p.y - cy, d = Math.max(1, Math.hypot(dx, dy)); return { x: p.x + dx / d * 48, y: p.y + dy / d * 48 }; });
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
  if (env && !/nicht beobachtet|unbekannt|—/i.test(env)) result.push({ label: env, type: "weather" });
  list.filter((node) => node.kind === "sensor" && /network|internet|weather|wetter|wifi|camera|kamera|micro|audio/i.test(node.label)).forEach((node) => result.push({ label: node.label, target: node.id, type: node.type }));
  return result.slice(0, 8);
}
function satellites(list, pos) {
  const layer = q("#wesen-environment-layer"); if (!layer) return; layer.replaceChildren();
  externalSources(list).forEach((source, i, all) => {
    const angle = -Math.PI * .86 + i / Math.max(1, all.length - 1) * Math.PI * 1.72;
    const x = 450 + Math.cos(angle) * 408, y = 350 + Math.sin(angle) * 305;
    if (source.target && pos.get(source.target)) {
      const p = pos.get(source.target), line = document.createElementNS(NS, "line");
      line.setAttribute("class", "wesen-satellite-link"); line.setAttribute("x1", x); line.setAttribute("y1", y); line.setAttribute("x2", p.x); line.setAttribute("y2", p.y); layer.appendChild(line);
    }
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", `wesen-satellite device-${source.type || "connection"}`);
    g.setAttribute("transform", `translate(${x} ${y})`);
    g.setAttribute("aria-label", source.label);
    g.innerHTML = `<title>${escapeText(source.label)}</title><circle r="22"/><text y="6">${iconFor(source.type || "connection")}</text>`;
    layer.appendChild(g);
  });
}

function ensureIconDock(list) {
  const stage = q("#wesen-stage"); if (!stage) return;
  let dock = q(`#${ICON_DOCK_ID}`);
  if (!dock) {
    dock = document.createElement("div"); dock.id = ICON_DOCK_ID; dock.className = "wesen-icon-dock"; dock.setAttribute("aria-label", "Körperknoten Schnellzugriff"); stage.appendChild(dock);
    dock.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-node]"); if (!button) return;
      const node = q(`#wesen-organ-layer .wesen-organ[data-node="${CSS.escape(button.dataset.node)}"]`);
      node?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
      node?.focus();
    });
  }
  dock.innerHTML = list.map((node) => `<button type="button" data-node="${escapeText(node.id)}" data-kind="${escapeText(node.kind)}" data-device-type="${escapeText(node.type)}" title="${escapeText(node.label)} — ${escapeText(node.value)}" aria-label="${escapeText(node.label)}"><span>${iconFor(node.type)}</span></button>`).join("");
}

function bindKeyboard() {
  const layer = q("#wesen-organ-layer"); if (!layer || layer.dataset.keyboardBound) return;
  layer.dataset.keyboardBound = "1";
  layer.addEventListener("keydown", (event) => {
    const node = event.target.closest(".wesen-organ"); if (!node || !["Enter", " "].includes(event.key)) return;
    event.preventDefault(); node.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  });
}

function capture(list, pos, membrane) {
  const frame = { at: Date.now(), membrane, nodes: list.map((node) => ({ id: node.id, kind: node.kind, type: node.type, label: node.label, value: node.value, ...pos.get(node.id) })) };
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
  svg.innerHTML = `<g class="wesen-self-body wesen-delayed-clone">${edges}${dots}</g><text x="150" y="170" text-anchor="middle">${model.selected ? "Historischer Snapshot" : `Echo ${latency() === null ? "—" : `${latency().toFixed(1)} ms`}`}</text>`;
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
  stage.addEventListener("pointerdown", (event) => { if (event.button !== 0 || event.target.closest?.("button")) return; model.dragging = true; model.pointer = { x: event.clientX, y: event.clientY }; });
  stage.addEventListener("pointermove", (event) => { if (!model.dragging || !model.pointer) return; model.camera.x += event.clientX - model.pointer.x; model.camera.y += event.clientY - model.pointer.y; model.pointer = { x: event.clientX, y: event.clientY }; camera(); });
  stage.addEventListener("pointerup", () => { model.dragging = false; model.pointer = null; });
  stage.addEventListener("pointerleave", () => { model.dragging = false; model.pointer = null; });
  stage.addEventListener("dblclick", (event) => { if (event.target.closest?.("button")) return; model.camera = { x: 0, y: 0, scale: 1 }; camera(); });
}
function focus() { const all = qa("#wesen-organ-layer .wesen-organ"), selected = all.find((x) => x.classList.contains("selected")); all.forEach((x) => x.classList.toggle("wesen-defocused", Boolean(selected && x !== selected))); }
function tracer() {
  const events = q("#wesen-events"); if (!events || events.dataset.tracer) return; events.dataset.tracer = "1";
  events.addEventListener("click", (event) => { const row = event.target.closest(".wesen-event-row"), token = row?.textContent?.match(/(?:event|decision|action|receipt)[-_:# ]*[a-z0-9-]+/i)?.[0]; if (!token) return; const subtitle = q("#wesen-stage-subtitle"); if (subtitle) subtitle.textContent = `Kausal-Tracer: ${token}`; q("#wesen-svg")?.classList.add("show-causality", "wesen-tracer-active"); });
}
function enhance() {
  const list = nodes(); if (!list.length) return;
  decorateNodes(list);
  const pos = layout(list);
  list.forEach((node) => { const p = pos.get(node.id); node.el.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`); });
  const membrane = q("#wesen-membrane"), path = hullPath(hull(list.map((node) => pos.get(node.id)).filter(Boolean))); if (membrane && path) membrane.setAttribute("d", path);
  syncEdges(list, pos); satellites(list, pos); ensureIconDock(list); capture(list, pos, path);
  const workspace = q("#tab-wesen"); if (workspace) workspace.dataset.organismState = visualState();
  focus(); timeline(); bindCamera(); bindKeyboard(); tracer();
}
export function initWesenOrganismV2() {
  loadSnapshots();
  const start = () => {
    enhance();
    const layer = q("#wesen-organ-layer");
    if (layer && !model.observer) { model.observer = new MutationObserver(() => setTimeout(enhance, 0)); model.observer.observe(layer, { childList: true }); }
    clearInterval(model.timer); model.timer = setInterval(enhance, 1500);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
}
initWesenOrganismV2();
