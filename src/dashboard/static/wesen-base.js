/* Brain-5D Wesen workspace
 * Read-only, machine-native body visualization.
 * Observed state only: no learning, language output or actuator writes.
 */
const WESEN_POLL_MS = 750;
const NS = "http://www.w3.org/2000/svg";

const WESEN_BASE = [
  { id: "kern", label: "SNN-Kern", kind: "core", hue: "gold", icon: "◆" },
  { id: "innenzustand", label: "Interozeption", kind: "internal", hue: "rose", icon: "♥" },
  { id: "rueckkopplung", label: "Rückkopplung", kind: "feedback", hue: "violet", icon: "↻" },
  { id: "struktur", label: "Körpergrenze", kind: "structure", hue: "green", icon: "⌬" },
];

const state = {
  status: null,
  embodiment: null,
  connections: null,
  selected: "kern",
  history: [],
  recurrence: [],
  morphologyHistory: [],
  previousSignature: "",
  paused: false,
  zoom: 1,
  filter: "all",
  timer: null,
  controller: null,
};

function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}
function pick(source, paths) {
  for (const path of paths) {
    let value = source;
    for (const part of path.split(".")) value = value && typeof value === "object" ? value[part] : undefined;
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return null;
}
function text(source, paths, fallback = "unbekannt") {
  const value = pick(source, paths);
  return value === null ? fallback : String(value);
}
function metric(source, paths) { return num(pick(source, paths)); }
function fmt(value, suffix = "", digits = 1) {
  const n = num(value);
  return n === null ? "—" : `${n.toFixed(digits)}${suffix}`;
}
function clamp(value, min = 0, max = 1) { return Math.max(min, Math.min(max, value)); }
function esc(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
async function wesenReadJson(url, signal) {
  const response = await fetch(url, { cache: "no-store", signal });
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.json();
}
function wesenConnectionArray() {
  const payload = state.connections;
  if (!payload) return [];
  for (const candidate of [payload.connections, payload.items, payload.devices, payload.available_connections, payload]) {
    if (Array.isArray(candidate)) return candidate;
  }
  return [];
}
function connectionLabel(item, index) {
  return text(item, ["label", "name", "id", "connection_id", "device_id"], `Verbindung ${index + 1}`);
}
function connectionKind(item) {
  return text(item, ["kind", "type", "category", "direction", "capability"], "connection").toLowerCase();
}
function classifyConnection(item) {
  const raw = `${connectionLabel(item, 0)} ${connectionKind(item)} ${JSON.stringify(item)}`.toLowerCase();
  if (/actuator|output|printer|display|speaker|robot|motor|arm|write|send/.test(raw)) return "actuator";
  if (/camera|micro|audio|sensor|weather|input|network|vision|temperature/.test(raw)) return "sensor";
  return "connection";
}
function statusClass(value) {
  const raw = String(value ?? "unknown").toLowerCase();
  if (/critical|error|failed|offline|unsafe|lost/.test(raw)) return "critical";
  if (/warn|degraded|pressure|partial|stale|paused/.test(raw)) return "warn";
  if (/ok|healthy|active|running|stable|ready|connected|true|nominal/.test(raw)) return "ok";
  return "unknown";
}
function runtimeMetrics() {
  const s = state.status || {};
  const e = state.embodiment || {};
  return {
    tick: pick(s, ["tick", "runtime.tick", "metrics.tick"]),
    firing: metric(s, ["firing_rate_hz", "metrics.firing_rate_hz", "network.firing_rate_hz"]),
    targetHz: metric(s, ["runtime_clock.target_hz", "target_hz", "runtime.target_hz"]),
    achievedHz: metric(s, ["runtime_clock.achieved_hz", "achieved_hz", "runtime.achieved_hz"]),
    energy: metric(e, ["energy", "metrics.energy", "homeostasis.energy"]),
    cpu: metric(e, ["host.cpu_percent", "interoception.cpu_percent", "metrics.cpu_percent"]),
    memory: metric(e, ["host.memory_percent", "interoception.memory_percent", "metrics.memory_percent"]),
    temp: metric(e, ["host.temperature_c", "interoception.temperature_c", "metrics.temperature_c"]),
    fan: metric(e, ["host.fan_rpm", "interoception.fan_rpm", "metrics.fan_rpm"]),
    disk: metric(e, ["host.disk_percent", "interoception.disk_percent", "metrics.disk_percent"]),
    recurrence: metric(e, ["recurrence", "metrics.recurrence", "loopback.recurrence", "feedback.recurrence"]),
    latency: metric(e, ["loopback_latency_ms", "metrics.loopback_latency_ms", "loopback.latency_ms", "feedback.latency_ms"]),
    regulation: text(e, ["regulatory_state", "homeostasis.state", "homeostasis_status"], "unbekannt"),
    environment: text(e, ["environment.name", "environment_status", "environment.state"], "nicht beobachtet"),
  };
}

function dynamicNodes() {
  const nodes = [...WESEN_BASE];
  const connections = wesenConnectionArray();
  connections.forEach((item, index) => {
    const type = classifyConnection(item);
    const id = `conn-${index}`;
    nodes.push({
      id,
      label: connectionLabel(item, index),
      kind: type,
      hue: type === "sensor" ? "cyan" : type === "actuator" ? "amber" : "blue",
      icon: type === "sensor" ? "◉" : type === "actuator" ? "▶" : "•",
      source: item,
    });
  });
  if (!connections.some((item) => classifyConnection(item) === "sensor")) {
    nodes.push({ id: "sensor-placeholder", label: "Sensorik", kind: "sensor", hue: "cyan", icon: "◉", placeholder: true });
  }
  if (!connections.some((item) => classifyConnection(item) === "actuator")) {
    nodes.push({ id: "actuator-placeholder", label: "Aktorik", kind: "actuator", hue: "amber", icon: "▶", placeholder: true });
  }
  return nodes;
}
function morphologySignature(nodes) {
  return nodes.filter((n) => !n.placeholder).map((n) => `${n.kind}:${n.label}`).sort().join("|");
}
function recordMorphology(nodes) {
  const signature = morphologySignature(nodes);
  if (!state.previousSignature) state.previousSignature = signature;
  if (signature === state.previousSignature) return;
  state.previousSignature = signature;
  const entry = { time: new Date().toLocaleTimeString("de-DE", { hour12: false }), signature, count: nodes.length };
  state.morphologyHistory.unshift(entry);
  if (state.morphologyHistory.length > 12) state.morphologyHistory.length = 12;
  pushEvent("structure", "Körpergrenze verändert", `${nodes.filter((n) => !n.placeholder).length} beobachtete Körperknoten`);
}

function layoutNodes(nodes) {
  const center = { x: 450, y: 350 };
  const groups = { sensor: [], actuator: [], internal: [], feedback: [], structure: [], connection: [] };
  nodes.forEach((n) => { if (n.kind !== "core") (groups[n.kind] || groups.connection).push(n); });
  const positions = { kern: center };
  const placeArc = (items, cx, cy, rx, ry, start, end) => {
    items.forEach((item, i) => {
      const t = items.length === 1 ? 0.5 : i / (items.length - 1);
      const angle = start + (end - start) * t;
      positions[item.id] = { x: cx + Math.cos(angle) * rx, y: cy + Math.sin(angle) * ry };
    });
  };
  placeArc(groups.sensor, 430, 340, 300, 235, Math.PI * 1.05, Math.PI * 1.55);
  placeArc(groups.actuator, 465, 365, 310, 235, Math.PI * 0.15, Math.PI * 0.65);
  placeArc(groups.connection, 450, 350, 325, 210, Math.PI * 0.72, Math.PI * 0.98);
  positions.innenzustand = { x: 340, y: 435 };
  positions.rueckkopplung = { x: 555, y: 445 };
  positions.struktur = { x: 450, y: 565 };
  return positions;
}

function adaptiveProfile() {
  const m = runtimeMetrics();
  const e = state.embodiment || {};
  const sensorNodes = dynamicNodes().filter((n) => n.kind === "sensor" && !n.placeholder);
  const actuatorNodes = dynamicNodes().filter((n) => n.kind === "actuator" && !n.placeholder);
  const sensorLost = pick(e, ["sensor_loss", "degraded_sensor", "metrics.sensor_loss"]);
  const actuatorFault = pick(e, ["actuator_fault", "actuator_error", "metrics.actuator_fault"]);
  const network = text(e, ["host.network_state", "network_state", "interoception.network_state"], "unknown");
  const pressure = Math.max(
    m.cpu === null ? 0 : m.cpu / 100,
    m.memory === null ? 0 : m.memory / 100,
    m.disk === null ? 0 : m.disk / 100,
    m.temp === null ? 0 : clamp((m.temp - 45) / 45)
  );
  let label = "Stabil beobachtet", level = "ok", scale = 1, tension = 0;
  if (sensorLost === true || /lost|offline|degraded/.test(String(sensorLost).toLowerCase())) {
    label = "Sensorverlust"; level = "warn"; scale = 0.97; tension = 0.45;
  }
  if (actuatorFault === true || /failed|error|offline/.test(String(actuatorFault).toLowerCase())) {
    label = "Aktorfehler"; level = "warn"; scale = 0.96; tension = 0.5;
  }
  if (/offline|isolated|down/.test(network.toLowerCase())) {
    label = "Netzwerkisolation"; level = "warn"; scale = 0.95; tension = 0.6;
  }
  if (pressure > 0.82) {
    label = m.temp !== null && m.temp > 80 ? "Thermische Belastung" : "Ressourcendruck";
    level = "critical"; scale = 0.91; tension = 1;
  } else if (pressure > 0.65 && level === "ok") {
    label = "Erhöhte Belastung"; level = "warn"; scale = 0.96; tension = 0.5;
  }
  return {
    label, level, scale, tension, pressure,
    notes: [
      `Sensoren: ${sensorNodes.length || "unbekannt"}`,
      `Aktoren: ${actuatorNodes.length || "unbekannt"}`,
      `Regulation: ${m.regulation}`,
      `Netzwerk: ${network}`,
    ],
  };
}

function ensureWorkspace() {
  if (document.getElementById("tab-wesen")) return;
  const main = document.querySelector("main") || document.querySelector(".dashboard-main") || document.body;
  const section = document.createElement("section");
  section.id = "tab-wesen";
  section.className = "tab-content dashboard-workspace wesen-workspace";
  section.hidden = true;
  section.innerHTML = `
    <header class="dashboard-generated-header wesen-header"><div><span class="dashboard-workspace-kicker">LIVE BODY</span><h2>Wesen</h2><p>Maschinen-native Echtzeitansicht aus beobachteten Sensoren, Interozeption, SNN, Aktoren und Rückkopplung.</p></div><div class="wesen-live-state"><span class="wesen-live-dot"></span><strong id="wesen-live-label">verbinde …</strong></div></header>
    <div class="wesen-layout">
      <aside class="wesen-sidebar">
        <section class="wesen-card"><header><span>KÖRPER-ZUSTAND</span><small>beobachtet</small></header><div id="wesen-vitals" class="wesen-metrics"></div><div class="wesen-spark-wrap"><div><span>Recurrence</span><strong id="wesen-recurrence-value">—</strong></div><svg id="wesen-recurrence-chart" viewBox="0 0 240 56" preserveAspectRatio="none"></svg></div></section>
        <section class="wesen-card"><header><span>ANSICHT</span><small>interaktiv</small></header><div class="wesen-view-controls"><button class="active" data-wesen-view="signals">Signale</button><button data-wesen-view="causality">Kausalpfade</button><button class="active" data-wesen-view="connections">Verbindungen</button><button class="active" data-wesen-view="environment">Umwelt</button></div><p class="wesen-hint">Klick: Fokus · Mausrad: Zoom · Doppelklick: Gesamtansicht</p></section>
        <section class="wesen-card"><header><span>AUTOMATISCHE ANPASSUNG</span><small>read-only</small></header><div id="wesen-adaptation" class="wesen-adaptation"></div></section>
      </aside>
      <section class="wesen-stage-card">
        <div class="wesen-stage-toolbar"><div><strong>Adaptive Körperkarte</strong><span id="wesen-stage-subtitle">Körperform entsteht aus real verfügbaren Verbindungen.</span></div><div class="wesen-stage-actions"><button data-wesen-action="reset-view">⌂ Gesamt</button><button data-wesen-action="pause-visual">Ⅱ Visualisierung</button></div></div>
        <div class="wesen-stage" id="wesen-stage"><svg id="wesen-svg" viewBox="0 0 900 700"><defs><filter id="wesen-glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><g id="wesen-camera"><path id="wesen-membrane" class="wesen-membrane"/><g id="wesen-environment-layer"></g><g id="wesen-connection-layer"></g><g id="wesen-signal-layer"></g><g id="wesen-organ-layer"></g><g id="wesen-pin-layer"></g></g></svg><div class="wesen-environment-caption"><span>UMWELT</span><strong id="wesen-environment-label">nicht beobachtet</strong></div><div class="wesen-adaptive-caption"><span>REAKTION</span><strong id="wesen-reaction-label">warte auf Telemetrie</strong></div></div>
        <div class="wesen-console"><div class="wesen-console-head"><strong>Ereignisse & Kausalität</strong><div id="wesen-event-filters"><button class="active" data-wesen-filter="all">Alle</button><button data-wesen-filter="sensor">Sensorik</button><button data-wesen-filter="actuator">Aktorik</button><button data-wesen-filter="feedback">Loop</button><button data-wesen-filter="structure">Morphologie</button><button data-wesen-filter="system">System</button></div></div><div id="wesen-events" class="wesen-events"></div></div>
      </section>
      <aside class="wesen-sidebar">
        <section class="wesen-card wesen-inspector"><header><span>INSPEKTION</span><small id="wesen-inspector-status">—</small></header><div id="wesen-inspector"></div></section>
        <section class="wesen-card"><header><span>KÖRPERGRENZE</span><small>live</small></header><div id="wesen-connections" class="wesen-connection-list"></div></section>
        <section class="wesen-card"><header><span>SELBST-MODELL</span><small>zeitversetzt</small></header><svg id="wesen-self-svg" viewBox="0 0 300 180"></svg><div id="wesen-self-metrics" class="wesen-self-metrics"></div></section>
        <section class="wesen-card"><header><span>MORPHOLOGIE-HISTORIE</span><small>Session</small></header><div id="wesen-morphology-history" class="wesen-history"></div></section>
      </aside>
    </div>`;
  main.appendChild(section);
  bindInteractions();
}
function ensureNav() {
  if (document.querySelector('.tab-btn[data-tab="wesen"]')) return;
  const nav = document.querySelector(".tab-nav") || document.querySelector("nav");
  if (!nav) return;
  const button = document.createElement("button");
  button.type = "button"; button.className = "tab-btn"; button.dataset.tab = "wesen"; button.textContent = "◉ WESEN";
  const ref = nav.querySelector('.tab-btn[data-tab="embodiment"]');
  if (ref) ref.before(button); else nav.appendChild(button);
  button.addEventListener("click", activate);
}
function activate() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach((b) => b.classList.toggle("active", b.dataset.tab === "wesen"));
  document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => { const on = tab.id === "tab-wesen"; tab.hidden = !on; tab.classList.toggle("active", on); });
  document.body.dataset.currentTab = "wesen";
  document.body.dataset.experienceWorkspace = "wesen";
}

function membranePath(nodes, positions, profile) {
  const pts = nodes.filter((n) => !n.placeholder && positions[n.id]).map((n) => positions[n.id]);
  if (!pts.length) return "M450 80 C720 80 820 220 820 350 C820 570 650 640 450 640 C250 640 80 570 80 350 C80 180 220 80 450 80Z";
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const minX = Math.max(35, Math.min(...xs) - 95), maxX = Math.min(865, Math.max(...xs) + 95);
  const minY = Math.max(45, Math.min(...ys) - 90), maxY = Math.min(655, Math.max(...ys) + 90);
  const inset = profile.tension * 18;
  return `M${(minX + maxX) / 2} ${minY + inset} C${maxX - inset} ${minY} ${maxX} ${(minY + maxY) / 2} ${(maxX - inset)} ${maxY - inset} C${(minX + maxX) / 2} ${maxY} ${minX + inset} ${maxY - inset} ${minX} ${(minY + maxY) / 2} C${minX + inset} ${minY} ${(minX + maxX) / 2} ${minY + inset} ${(minX + maxX) / 2} ${minY + inset}Z`;
}
function nodeValue(node) {
  const m = runtimeMetrics();
  if (node.id === "kern") return m.firing === null ? "—" : `${m.firing.toFixed(1)} Hz`;
  if (node.id === "innenzustand") return m.regulation;
  if (node.id === "rueckkopplung") return m.recurrence === null ? "—" : m.recurrence.toFixed(2);
  if (node.id === "struktur") return `${wesenConnectionArray().length} Ports`;
  if (node.placeholder) return "nicht verfügbar";
  return text(node.source, ["status", "state", "available", "connected"], "beobachtet");
}
function renderBody() {
  const nodes = dynamicNodes();
  recordMorphology(nodes);
  const positions = layoutNodes(nodes);
  const profile = adaptiveProfile();
  const organLayer = document.getElementById("wesen-organ-layer");
  const connectionLayer = document.getElementById("wesen-connection-layer");
  const pinLayer = document.getElementById("wesen-pin-layer");
  const envLayer = document.getElementById("wesen-environment-layer");
  if (!organLayer || !connectionLayer || !pinLayer || !envLayer) return;
  organLayer.innerHTML = ""; connectionLayer.innerHTML = ""; pinLayer.innerHTML = ""; envLayer.innerHTML = "";

  const core = positions.kern;
  nodes.filter((n) => n.id !== "kern").forEach((node) => {
    const p = positions[node.id]; if (!p) return;
    const path = document.createElementNS(NS, "path");
    path.setAttribute("d", `M ${core.x} ${core.y} Q ${(core.x + p.x) / 2} ${(core.y + p.y) / 2 - 18} ${p.x} ${p.y}`);
    path.setAttribute("class", `wesen-nerve kind-${node.kind}`);
    path.dataset.node = node.id;
    connectionLayer.appendChild(path);
  });

  nodes.forEach((node) => {
    const p = positions[node.id]; if (!p) return;
    const g = document.createElementNS(NS, "g");
    g.setAttribute("transform", `translate(${p.x} ${p.y})`);
    g.setAttribute("class", `wesen-organ wesen-hue-${node.hue} kind-${node.kind}${state.selected === node.id ? " selected" : ""}${node.placeholder ? " unknown" : ""}`);
    g.dataset.node = node.id; g.tabIndex = 0; g.setAttribute("role", "button");
    const r = node.kind === "core" ? 70 : node.kind === "sensor" || node.kind === "actuator" ? 38 : 48;
    g.innerHTML = `<circle class="wesen-organ-halo" r="${r + 16}"/><circle class="wesen-organ-body" r="${r}"/><circle class="wesen-organ-status" cx="${r - 7}" cy="-${r - 7}" r="6"/><text class="wesen-organ-icon" y="-7">${esc(node.icon)}</text><text class="wesen-organ-label" y="15">${esc(node.label).slice(0, 22)}</text><text class="wesen-organ-value" y="33">${esc(nodeValue(node))}</text>`;
    organLayer.appendChild(g);

    if (!node.placeholder) {
      const pin = document.createElementNS(NS, "g");
      pin.setAttribute("transform", `translate(${p.x + r + 12} ${p.y - r - 8})`);
      pin.setAttribute("class", "wesen-data-pin");
      pin.innerHTML = `<rect x="0" y="-16" rx="5" width="92" height="23"/><text x="7" y="0">${esc(nodeValue(node)).slice(0, 18)}</text>`;
      pinLayer.appendChild(pin);
    }
  });

  const membrane = document.getElementById("wesen-membrane");
  membrane.setAttribute("d", membranePath(nodes, positions, profile));
  membrane.dataset.state = profile.level;
  const camera = document.getElementById("wesen-camera");
  camera.style.setProperty("--wesen-adaptive-scale", String(profile.scale * state.zoom));
  renderSignals(nodes, positions);
  renderEnvironment(profile);
  renderEcho(nodes, positions);
  renderInspector(nodes);
  renderConnections();
  renderHistory();
}

function renderSignals(nodes, positions) {
  const layer = document.getElementById("wesen-signal-layer"); if (!layer) return;
  layer.innerHTML = ""; if (state.paused) return;
  const core = positions.kern;
  nodes.filter((n) => !n.placeholder && n.id !== "kern").forEach((node, index) => {
    const p = positions[node.id]; if (!p) return;
    const path = document.querySelector(`.wesen-nerve[data-node="${CSS.escape(node.id)}"]`); if (!path) return;
    const dot = document.createElementNS(NS, "circle"); dot.setAttribute("r", "3.5"); dot.setAttribute("class", `wesen-signal-dot kind-${node.kind}`);
    dot.innerHTML = `<animateMotion dur="${1 + (index % 5) * 0.17}s" repeatCount="indefinite" path="${path.getAttribute("d")}"/>`;
    layer.appendChild(dot);
    if (node.kind === "feedback" || node.kind === "sensor") {
      const echo = document.createElementNS(NS, "circle"); echo.setAttribute("r", "3"); echo.setAttribute("class", "wesen-signal-dot feedback-echo");
      echo.innerHTML = `<animateMotion begin=".22s" dur="1.35s" repeatCount="indefinite" path="M ${p.x} ${p.y} Q ${(p.x + core.x) / 2} ${(p.y + core.y) / 2 + 18} ${core.x} ${core.y}"/>`;
      layer.appendChild(echo);
    }
  });
}
function renderEnvironment(profile) {
  const m = runtimeMetrics();
  document.getElementById("wesen-environment-label").textContent = m.environment;
  const reaction = document.getElementById("wesen-reaction-label"); reaction.textContent = profile.label; reaction.dataset.state = profile.level;
  const layer = document.getElementById("wesen-environment-layer");
  if (layer) layer.innerHTML = `<g class="wesen-env-node" transform="translate(72 100)"><circle r="28"/><text y="4">ENV</text></g><text class="wesen-env-label" x="110" y="104">${esc(m.environment)}</text>`;
  const root = document.getElementById("wesen-adaptation");
  root.innerHTML = `<div class="wesen-adaptation-state ${profile.level}"><span></span><strong>${esc(profile.label)}</strong></div>${profile.notes.map((n) => `<p>${esc(n)}</p>`).join("")}`;
}
function renderEcho(nodes, positions) {
  const svg = document.getElementById("wesen-self-svg"); if (!svg) return;
  const m = runtimeMetrics(); const delay = m.latency === null ? "Latenz unbekannt" : `${m.latency.toFixed(1)} ms`;
  const opacity = m.recurrence === null ? 0.25 : 0.25 + clamp(m.recurrence) * 0.65;
  const scaleX = 0.29, scaleY = 0.23;
  const dots = nodes.filter((n) => positions[n.id]).map((n) => {
    const p = positions[n.id]; const x = 18 + p.x * scaleX, y = 12 + p.y * scaleY;
    return `<circle cx="${x}" cy="${y}" r="${n.kind === "core" ? 9 : 4}" class="kind-${n.kind}"/>`;
  }).join("");
  const lines = nodes.filter((n) => n.id !== "kern" && positions[n.id]).map((n) => {
    const p = positions[n.id], c = positions.kern;
    return `<line x1="${18 + c.x * scaleX}" y1="${12 + c.y * scaleY}" x2="${18 + p.x * scaleX}" y2="${12 + p.y * scaleY}"/>`;
  }).join("");
  svg.innerHTML = `<g class="wesen-self-body" style="opacity:${opacity}">${lines}${dots}</g><text x="150" y="172" text-anchor="middle">Echo ${esc(delay)}</text>`;
  document.getElementById("wesen-self-metrics").innerHTML = `<div><span>Recurrence</span><strong>${m.recurrence === null ? "—" : m.recurrence.toFixed(2)}</strong></div><div><span>Loop-Latenz</span><strong>${esc(delay)}</strong></div>`;
}

function renderVitals() {
  const m = runtimeMetrics();
  const rows = [
    ["Tick", m.tick ?? "—"], ["Feuerrate", fmt(m.firing, " Hz", 1)], ["Target Hz", fmt(m.targetHz, " Hz", 0)], ["Achieved Hz", fmt(m.achievedHz, " Hz", 1)],
    ["Energie", fmt(m.energy, "", 3)], ["CPU", fmt(m.cpu, " %", 0)], ["RAM", fmt(m.memory, " %", 0)], ["Temperatur", fmt(m.temp, " °C", 1)], ["Fan", fmt(m.fan, " rpm", 0)], ["Disk", fmt(m.disk, " %", 0)],
  ];
  document.getElementById("wesen-vitals").innerHTML = rows.map(([a,b]) => `<div class="wesen-metric"><span>${a}</span><strong>${esc(b)}</strong></div>`).join("");
  document.getElementById("wesen-recurrence-value").textContent = m.recurrence === null ? "—" : m.recurrence.toFixed(2);
  if (m.recurrence !== null) { state.recurrence.push(m.recurrence); if (state.recurrence.length > 100) state.recurrence.shift(); }
  drawRecurrence();
}
function drawRecurrence() {
  const svg = document.getElementById("wesen-recurrence-chart"); const values = state.recurrence;
  if (!values.length) { svg.innerHTML = '<text x="120" y="31" text-anchor="middle" class="wesen-chart-empty">keine Messwerte</text>'; return; }
  const pts = values.map((v,i) => `${i / Math.max(1, values.length - 1) * 240},${52 - clamp(v) * 46}`).join(" ");
  const [x,y] = pts.split(" ").at(-1).split(",");
  svg.innerHTML = `<polyline class="wesen-chart-line" points="${pts}"/><circle class="wesen-chart-point" cx="${x}" cy="${y}" r="3"/>`;
}
function selectedNode(nodes) { return nodes.find((n) => n.id === state.selected) || nodes[0]; }
function renderInspector(nodes) {
  const node = selectedNode(nodes); state.selected = node.id;
  const m = runtimeMetrics(); const root = document.getElementById("wesen-inspector");
  const rows = node.source ? Object.entries(node.source).filter(([,v]) => ["string","number","boolean"].includes(typeof v)).slice(0,7) : [];
  const generic = node.id === "kern" ? [["Feuerrate", fmt(m.firing," Hz",1)],["Tick",m.tick??"—"]] : node.id === "innenzustand" ? [["Regulation",m.regulation],["CPU",fmt(m.cpu," %",0)],["Temperatur",fmt(m.temp," °C",1)]] : node.id === "rueckkopplung" ? [["Recurrence",m.recurrence===null?"—":m.recurrence.toFixed(2)],["Latenz",fmt(m.latency," ms",1)]] : [["Status",nodeValue(node)],["Typ",node.kind]];
  const data = rows.length ? rows : generic;
  document.getElementById("wesen-inspector-status").textContent = node.placeholder ? "unbekannt" : "beobachtet";
  root.innerHTML = `<div class="wesen-inspector-title wesen-hue-${node.hue}"><span>${esc(node.icon)}</span><div><strong>${esc(node.label)}</strong><small>${esc(node.kind)}</small></div></div><div class="wesen-inspector-rows">${data.map(([a,b]) => `<div><span>${esc(a)}</span><strong>${esc(b)}</strong></div>`).join("")}</div><p class="wesen-integrity-note">OBSERVED/UNKNOWN: keine erfundenen Ersatzwerte. Darstellung ist Visualisierung, keine Bewusstseinsmessung.</p>`;
}
function renderConnections() {
  const root = document.getElementById("wesen-connections"); const items = wesenConnectionArray();
  if (!items.length) { root.innerHTML = '<p class="wesen-empty">Keine realen Verbindungen gemeldet.</p>'; return; }
  root.innerHTML = items.slice(0,14).map((item,index) => {
    const status = text(item,["status","state","available","connected"],"beobachtet");
    const kind = classifyConnection(item);
    return `<button class="wesen-connection-row" data-node="conn-${index}"><span class="wesen-connection-led ${statusClass(status)}"></span><span><strong>${esc(connectionLabel(item,index))}</strong><small>${esc(kind)}</small></span><em>${esc(status)}</em></button>`;
  }).join("");
}
function renderHistory() {
  const root = document.getElementById("wesen-morphology-history");
  root.innerHTML = state.morphologyHistory.length ? state.morphologyHistory.map((h) => `<div><time>${h.time}</time><span>${h.count} Knoten</span></div>`).join("") : '<p class="wesen-empty">Noch keine Änderung der Körpergrenze.</p>';
}
function pushEvent(type,label,detail) {
  state.history.unshift({ time:new Date().toLocaleTimeString("de-DE",{hour12:false}), type, label, detail });
  if (state.history.length > 40) state.history.length = 40;
}
function snapshot() {
  const m = runtimeMetrics();
  return { recurrence:m.recurrence, latency:m.latency, cpu:m.cpu, temp:m.temp, regulation:m.regulation, connections:wesenConnectionArray().length };
}
function recordEvents() {
  const next = snapshot(), prev = state.lastSnapshot; state.lastSnapshot = next; if (!prev) return;
  const changed = (a,b,t=0.01) => a!==null && b!==null && Math.abs(a-b)>t;
  if (changed(next.recurrence,prev.recurrence)) pushEvent("feedback","Rückkopplung verändert",`${prev.recurrence?.toFixed(2)} → ${next.recurrence?.toFixed(2)}`);
  if (changed(next.latency,prev.latency,0.5)) pushEvent("feedback","Loop-Latenz verändert",`${prev.latency?.toFixed(1)} → ${next.latency?.toFixed(1)} ms`);
  if (changed(next.cpu,prev.cpu,3)) pushEvent("system","CPU-Belastung verändert",`${prev.cpu?.toFixed(0)} → ${next.cpu?.toFixed(0)} %`);
  if (changed(next.temp,prev.temp,1)) pushEvent("system","Temperatur verändert",`${prev.temp?.toFixed(1)} → ${next.temp?.toFixed(1)} °C`);
  if (next.connections!==prev.connections) pushEvent("structure","Körpergrenze verändert",`${prev.connections} → ${next.connections} Verbindungen`);
  if (next.regulation!==prev.regulation) pushEvent("system","Regulation verändert",`${prev.regulation} → ${next.regulation}`);
  renderEvents();
}
function renderEvents() {
  const root = document.getElementById("wesen-events");
  const events = state.history.filter((e) => state.filter === "all" || e.type === state.filter).slice(0,20);
  root.innerHTML = events.length ? events.map((e) => `<button class="wesen-event-row"><time>${e.time}</time><span class="wesen-event-kind ${e.type}"></span><strong>${esc(e.label)}</strong><em>${esc(e.detail)}</em></button>`).join("") : '<p class="wesen-empty">Noch keine Zustandsänderung im Beobachtungsfenster.</p>';
}
function updateLive(error=null) {
  const label=document.getElementById("wesen-live-label"), dot=document.querySelector(".wesen-live-dot");
  if (error) { label.textContent="Telemetrie nicht erreichbar"; dot.dataset.state="critical"; return; }
  const runtime=text(state.status||{},["state","runtime.state","status"],"verbunden"); label.textContent=runtime; dot.dataset.state=statusClass(runtime);
}
function renderAll() { renderVitals(); renderBody(); recordEvents(); updateLive(); }

async function poll() {
  state.controller?.abort(); state.controller = new AbortController();
  try {
    const results = await Promise.allSettled([
      wesenReadJson("/api/status",state.controller.signal),
      wesenReadJson("/api/embodiment/state",state.controller.signal),
      wesenReadJson("/api/embodiment/connections",state.controller.signal),
    ]);
    if (results[0].status==="fulfilled") state.status=results[0].value;
    if (results[1].status==="fulfilled") state.embodiment=results[1].value;
    if (results[2].status==="fulfilled") state.connections=results[2].value;
    if (results.every((r)=>r.status==="rejected")) throw new Error("Keine Telemetriequelle erreichbar");
    renderAll();
  } catch (error) { if (error.name!=="AbortError") updateLive(error); }
  finally { clearTimeout(state.timer); state.timer=setTimeout(poll,WESEN_POLL_MS); }
}

function selectNode(id) { state.selected=id; renderBody(); }
function bindInteractions() {
  const root=document.getElementById("tab-wesen"); if (!root || root.dataset.bound) return; root.dataset.bound="1";
  root.addEventListener("click",(event)=>{
    const node=event.target.closest("[data-node]"); if (node) selectNode(node.dataset.node);
    const filter=event.target.closest("[data-wesen-filter]"); if (filter) { state.filter=filter.dataset.wesenFilter; document.querySelectorAll("[data-wesen-filter]").forEach((b)=>b.classList.toggle("active",b===filter)); renderEvents(); }
    const view=event.target.closest("[data-wesen-view]"); if (view) { view.classList.toggle("active"); document.getElementById("wesen-svg")?.classList.toggle(`show-${view.dataset.wesenView}`,view.classList.contains("active")); }
    const action=event.target.closest("[data-wesen-action]")?.dataset.wesenAction;
    if (action==="reset-view") { state.zoom=1; state.selected="kern"; renderBody(); }
    if (action==="pause-visual") { state.paused=!state.paused; event.target.textContent=state.paused?"▶ Visualisierung":"Ⅱ Visualisierung"; renderBody(); }
  });
  document.getElementById("wesen-stage")?.addEventListener("wheel",(event)=>{ event.preventDefault(); state.zoom=clamp(state.zoom + (event.deltaY<0?0.08:-0.08),0.72,1.45); renderBody(); },{passive:false});
  document.getElementById("wesen-stage")?.addEventListener("dblclick",()=>{ state.zoom=1; state.selected="kern"; renderBody(); });
}
function initWesenWorkspace() { ensureWorkspace(); ensureNav(); if (!state.timer) poll(); }
window.Brain5DWesen={init:initWesenWorkspace,activate,refresh:poll};
if (document.readyState==="loading") document.addEventListener("DOMContentLoaded",initWesenWorkspace,{once:true}); else initWesenWorkspace();
