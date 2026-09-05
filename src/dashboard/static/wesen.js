/* Brain-5D Wesen workspace
 *
 * Read-only adaptive organism visualization. This module visualizes observed
 * runtime, embodiment and connection state; it does not fabricate scientific
 * evidence, run learning, or issue actuator/language output.
 */

const WESEN_POLL_MS = 750;
const WESEN_ORGANS = [
  { id: "sensorik", label: "Sensorik", icon: "◉", hue: "cyan", role: "Umwelt erfassen" },
  { id: "innenzustand", label: "Innenzustand", icon: "♥", hue: "rose", role: "Homöostase und Belastung" },
  { id: "rueckkopplung", label: "Rückkopplung", icon: "↻", hue: "violet", role: "Eigenwirkung beobachten" },
  { id: "struktur", label: "Struktur", icon: "⌬", hue: "green", role: "Körpergrenze und Plastizität" },
  { id: "ressourcen", label: "Ressourcen", icon: "▤", hue: "amber", role: "Host und Laufzeit" },
  { id: "umwelt", label: "Umwelt", icon: "◎", hue: "blue", role: "Externe Situation" },
  { id: "kern", label: "SNN-Kern", icon: "◆", hue: "gold", role: "Neuronale Dynamik" },
];

const wesenState = {
  selected: "sensorik",
  status: null,
  embodiment: null,
  connections: null,
  recurrenceHistory: [],
  eventHistory: [],
  lastSnapshot: null,
  controller: null,
  timer: null,
  paused: false,
};

function wesenNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function wesenPick(source, paths) {
  for (const path of paths) {
    const parts = path.split(".");
    let value = source;
    for (const part of parts) value = value && typeof value === "object" ? value[part] : undefined;
    if (value !== undefined && value !== null) return value;
  }
  return null;
}

function wesenMetric(source, paths) {
  return wesenNumber(wesenPick(source, paths));
}

function wesenText(source, paths, fallback = "unbekannt") {
  const value = wesenPick(source, paths);
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function wesenFormat(value, suffix = "", digits = 1) {
  const number = wesenNumber(value);
  return number === null ? "—" : `${number.toFixed(digits)}${suffix}`;
}

function wesenClamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function wesenStatusClass(value) {
  if (value === null || value === undefined) return "unknown";
  if (typeof value === "boolean") return value ? "ok" : "warn";
  const text = String(value).toLowerCase();
  if (["ok", "healthy", "active", "running", "stable", "ready", "nominal", "connected"].some((token) => text.includes(token))) return "ok";
  if (["critical", "error", "failed", "offline", "unsafe"].some((token) => text.includes(token))) return "critical";
  if (["warn", "degraded", "pressure", "partial", "paused"].some((token) => text.includes(token))) return "warn";
  return "unknown";
}

async function wesenReadJson(url, signal) {
  const response = await fetch(url, { cache: "no-store", signal });
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.json();
}

function wesenEnsureWorkspace() {
  if (document.getElementById("tab-wesen")) return;
  const main = document.querySelector("main") || document.querySelector(".dashboard-main") || document.body;
  const section = document.createElement("section");
  section.id = "tab-wesen";
  section.className = "tab-content dashboard-workspace wesen-workspace";
  section.hidden = true;
  section.innerHTML = `
    <header class="dashboard-generated-header wesen-header">
      <div>
        <span class="dashboard-workspace-kicker">LIVE BODY</span>
        <h2>Wesen</h2>
        <p>Interaktive Echtzeitansicht der beobachtbaren Körperzustände. Keine Lern- oder Sprachausgabe.</p>
      </div>
      <div class="wesen-live-state"><span class="wesen-live-dot"></span><strong id="wesen-live-label">verbinde …</strong></div>
    </header>
    <div class="wesen-layout">
      <aside class="wesen-sidebar wesen-sidebar-left">
        <section class="wesen-card">
          <header><span>ΚÖRPER-ZUSTAND</span><small>live</small></header>
          <div class="wesen-metrics" id="wesen-vitals"></div>
          <div class="wesen-spark-wrap">
            <div><span>Rückkopplung</span><strong id="wesen-recurrence-value">—</strong></div>
            <svg id="wesen-recurrence-chart" viewBox="0 0 240 56" preserveAspectRatio="none" aria-label="Rückkopplungstrend"></svg>
          </div>
        </section>
        <section class="wesen-card">
          <header><span>INTERAKTION</span><small>Ansicht</small></header>
          <div class="wesen-view-controls">
            <button type="button" data-wesen-view="signals" class="active">Signale</button>
            <button type="button" data-wesen-view="causality">Kausalpfade</button>
            <button type="button" data-wesen-view="connections">Verbindungen</button>
            <button type="button" data-wesen-view="environment">Umweltwirkung</button>
          </div>
          <p class="wesen-hint">Organ anklicken: Fokus und Diagnose rechts. Mausrad: Detaildichte. Doppelklick: Gesamtansicht.</p>
        </section>
        <section class="wesen-card">
          <header><span>AUTOMATISCHE ANPASSUNG</span><small>beobachtet</small></header>
          <div class="wesen-adaptation" id="wesen-adaptation"></div>
        </section>
      </aside>

      <section class="wesen-stage-card">
        <div class="wesen-stage-toolbar">
          <div><strong>Das Brain-5D Wesen</strong><span id="wesen-stage-subtitle">Körperform folgt realen Verbindungen und Zuständen.</span></div>
          <div class="wesen-stage-actions">
            <button type="button" data-wesen-action="reset-view">⌂ Gesamt</button>
            <button type="button" data-wesen-action="pause-visual">Ⅱ Visualisierung</button>
          </div>
        </div>
        <div class="wesen-stage" id="wesen-stage">
          <svg id="wesen-svg" viewBox="0 0 900 720" role="img" aria-label="Interaktive Brain-5D Wesen-Darstellung">
            <defs>
              <filter id="wesen-glow"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
              <radialGradient id="wesen-core-gradient"><stop offset="0" stop-color="#fff3b0"/><stop offset="0.28" stop-color="#ffca57"/><stop offset="1" stop-color="#4a2b02"/></radialGradient>
              <linearGradient id="wesen-membrane-gradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#37d9ff" stop-opacity=".22"/><stop offset=".48" stop-color="#7c5cff" stop-opacity=".1"/><stop offset="1" stop-color="#2af598" stop-opacity=".16"/></linearGradient>
            </defs>
            <g id="wesen-camera">
              <path id="wesen-membrane" class="wesen-membrane" d="M450 72 C640 66 790 178 822 352 C854 528 704 662 472 674 C252 684 88 568 86 365 C84 173 248 79 450 72Z"/>
              <g id="wesen-connection-layer"></g>
              <g id="wesen-signal-layer"></g>
              <g id="wesen-organ-layer"></g>
              <g id="wesen-echo-layer" class="wesen-echo-layer"></g>
            </g>
          </svg>
          <div class="wesen-environment-caption"><span>UMWELT</span><strong id="wesen-environment-label">nicht beobachtet</strong></div>
          <div class="wesen-adaptive-caption"><span>REAKTION</span><strong id="wesen-reaction-label">warte auf Telemetrie</strong></div>
        </div>
        <div class="wesen-console">
          <div class="wesen-console-head"><strong>Ereignisse</strong><div id="wesen-event-filters"><button class="active" data-wesen-filter="all">Alle</button><button data-wesen-filter="sensorik">Sensorik</button><button data-wesen-filter="innenzustand">Innen</button><button data-wesen-filter="rueckkopplung">Loop</button><button data-wesen-filter="struktur">Struktur</button><button data-wesen-filter="system">System</button></div></div>
          <div id="wesen-events" class="wesen-events"></div>
        </div>
      </section>

      <aside class="wesen-sidebar wesen-sidebar-right">
        <section class="wesen-card wesen-inspector">
          <header><span>ORGAN-INSPEKTION</span><small id="wesen-inspector-status">—</small></header>
          <div id="wesen-inspector"></div>
        </section>
        <section class="wesen-card">
          <header><span>KÖRPERGRENZE</span><small>Verbindungen</small></header>
          <div id="wesen-connections" class="wesen-connection-list"></div>
        </section>
        <section class="wesen-card">
          <header><span>SELBST-MODELL</span><small>zeitversetzt</small></header>
          <div class="wesen-self-model">
            <svg id="wesen-self-svg" viewBox="0 0 260 140" aria-label="Zeitverzögertes Selbstmodell"></svg>
            <div class="wesen-self-metrics" id="wesen-self-metrics"></div>
          </div>
        </section>
      </aside>
    </div>`;
  main.appendChild(section);
  wesenRenderOrganism();
  wesenBindInteractions();
}

function wesenEnsureNavButton() {
  if (document.querySelector('.tab-btn[data-tab="wesen"]')) return;
  const nav = document.querySelector(".tab-nav") || document.querySelector("nav");
  if (!nav) return;
  const reference = nav.querySelector('.tab-btn[data-tab="embodiment"]') || nav.querySelector('.tab-btn[data-tab="control"]');
  const button = document.createElement("button");
  button.type = "button";
  button.className = "tab-btn";
  button.dataset.tab = "wesen";
  button.innerHTML = "◉ WESEN";
  if (reference) reference.insertAdjacentElement("beforebegin", button);
  else nav.appendChild(button);
  button.addEventListener("click", () => wesenActivate());
}

function wesenActivate() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach((button) => button.classList.toggle("active", button.dataset.tab === "wesen"));
  document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => {
    const active = tab.id === "tab-wesen";
    tab.classList.toggle("active", active);
    tab.hidden = !active;
  });
  document.body.dataset.currentTab = "wesen";
  document.body.dataset.experienceWorkspace = "wesen";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function wesenOrganPosition(id) {
  const positions = {
    sensorik: [450, 150],
    innenzustand: [650, 245],
    struktur: [690, 438],
    rueckkopplung: [565, 575],
    ressourcen: [335, 574],
    umwelt: [215, 420],
    kern: [450, 365],
  };
  return positions[id] || [450, 365];
}

function wesenRenderOrganism() {
  const organLayer = document.getElementById("wesen-organ-layer");
  const connectionLayer = document.getElementById("wesen-connection-layer");
  if (!organLayer || !connectionLayer) return;
  organLayer.innerHTML = "";
  connectionLayer.innerHTML = "";

  WESEN_ORGANS.filter((organ) => organ.id !== "kern").forEach((organ) => {
    const [x, y] = wesenOrganPosition(organ.id);
    const [cx, cy] = wesenOrganPosition("kern");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const mx = (x + cx) / 2 + (y - cy) * 0.08;
    const my = (y + cy) / 2 - (x - cx) * 0.08;
    path.setAttribute("d", `M ${cx} ${cy} Q ${mx} ${my} ${x} ${y}`);
    path.setAttribute("class", `wesen-nerve wesen-hue-${organ.hue}`);
    path.dataset.organ = organ.id;
    connectionLayer.appendChild(path);
  });

  WESEN_ORGANS.forEach((organ) => {
    const [x, y] = wesenOrganPosition(organ.id);
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", `wesen-organ wesen-hue-${organ.hue}${organ.id === "kern" ? " wesen-core" : ""}`);
    group.setAttribute("transform", `translate(${x} ${y})`);
    group.dataset.organ = organ.id;
    group.tabIndex = 0;
    group.setAttribute("role", "button");
    group.setAttribute("aria-label", organ.label);
    group.innerHTML = `
      <circle class="wesen-organ-halo" r="${organ.id === "kern" ? 108 : 74}"/>
      <circle class="wesen-organ-body" r="${organ.id === "kern" ? 82 : 56}"/>
      <circle class="wesen-organ-status" cx="${organ.id === "kern" ? 56 : 40}" cy="${organ.id === "kern" ? -56 : -40}" r="7"/>
      <text class="wesen-organ-icon" y="-13">${organ.icon}</text>
      <text class="wesen-organ-label" y="16">${organ.label}</text>
      <text class="wesen-organ-value" y="38" data-wesen-organ-value="${organ.id}">—</text>`;
    organLayer.appendChild(group);
  });
}

function wesenConnectionArray() {
  const payload = wesenState.connections;
  if (!payload) return [];
  const candidates = [payload.connections, payload.items, payload.devices, payload.available_connections, payload];
  for (const candidate of candidates) if (Array.isArray(candidate)) return candidate;
  return [];
}

function wesenVitals() {
  const s = wesenState.status || {};
  const e = wesenState.embodiment || {};
  return [
    ["Tick", wesenText(s, ["tick", "runtime.tick", "metrics.tick"], "—"), "tick"],
    ["Feuerrate", wesenFormat(wesenPick(s, ["firing_rate_hz", "metrics.firing_rate_hz", "network.firing_rate_hz"]), " Hz", 1), "rate"],
    ["Energie", wesenFormat(wesenPick(e, ["energy", "metrics.energy", "homeostasis.energy"]), "", 3), "energy"],
    ["Homöostase", wesenText(e, ["homeostasis.state", "homeostasis_status", "regulatory_state"], "—"), "homeostasis"],
    ["CPU", wesenFormat(wesenPick(e, ["host.cpu_percent", "interoception.cpu_percent", "metrics.cpu_percent"]), " %", 0), "cpu"],
    ["Temperatur", wesenFormat(wesenPick(e, ["host.temperature_c", "interoception.temperature_c", "metrics.temperature_c"]), " °C", 1), "temperature"],
  ];
}

function wesenRecurrence() {
  const e = wesenState.embodiment || {};
  return wesenMetric(e, ["recurrence", "metrics.recurrence", "loopback.recurrence", "feedback.recurrence"]);
}

function wesenLoopLatency() {
  const e = wesenState.embodiment || {};
  return wesenMetric(e, ["loopback_latency_ms", "metrics.loopback_latency_ms", "loopback.latency_ms", "feedback.latency_ms"]);
}

function wesenCoreRate() {
  const s = wesenState.status || {};
  return wesenMetric(s, ["firing_rate_hz", "metrics.firing_rate_hz", "network.firing_rate_hz"]);
}

function wesenSensorRate() {
  const e = wesenState.embodiment || {};
  return wesenMetric(e, ["sensor_rate_hz", "metrics.sensor_rate_hz", "input_rate_hz", "metrics.input_rate_hz"]);
}

function wesenHostPressure() {
  const e = wesenState.embodiment || {};
  const cpu = wesenMetric(e, ["host.cpu_percent", "interoception.cpu_percent", "metrics.cpu_percent"]);
  const temperature = wesenMetric(e, ["host.temperature_c", "interoception.temperature_c", "metrics.temperature_c"]);
  if (cpu === null && temperature === null) return null;
  const cpuPart = cpu === null ? 0 : wesenClamp(cpu / 100);
  const tempPart = temperature === null ? 0 : wesenClamp((temperature - 35) / 60);
  return Math.max(cpuPart, tempPart);
}

function wesenOrganValue(id) {
  const e = wesenState.embodiment || {};
  if (id === "kern") return wesenCoreRate() === null ? "—" : `${wesenCoreRate().toFixed(1)} Hz`;
  if (id === "sensorik") return wesenSensorRate() === null ? "—" : `${wesenSensorRate().toFixed(1)} Hz`;
  if (id === "rueckkopplung") {
    const recurrence = wesenRecurrence();
    return recurrence === null ? "—" : recurrence.toFixed(2);
  }
  if (id === "ressourcen") {
    const cpu = wesenMetric(e, ["host.cpu_percent", "interoception.cpu_percent", "metrics.cpu_percent"]);
    return cpu === null ? "—" : `CPU ${cpu.toFixed(0)}%`;
  }
  if (id === "struktur") return String(wesenConnectionArray().length || "—");
  if (id === "innenzustand") return wesenText(e, ["regulatory_state", "homeostasis.state", "homeostasis_status"], "—");
  if (id === "umwelt") return wesenText(e, ["environment.name", "environment_status", "environment.state"], "—");
  return "—";
}

function wesenAdaptiveProfile() {
  const e = wesenState.embodiment || {};
  const pressure = wesenHostPressure();
  const recurrence = wesenRecurrence();
  const sensorRate = wesenSensorRate();
  const available = wesenPick(e, ["available"]);
  const profile = { label: "Beobachtung", className: "unknown", scale: 1, membrane: 1, notes: [] };

  if (available === false) {
    profile.label = "Embodiment nicht verfügbar";
    profile.className = "warn";
    profile.scale = 0.94;
    profile.membrane = 0.45;
    profile.notes.push("Körperdaten fehlen; keine Reaktion wird simuliert.");
    return profile;
  }
  if (pressure !== null && pressure > 0.85) {
    profile.label = "Ressourcendruck";
    profile.className = "critical";
    profile.scale = 0.93;
    profile.membrane = 0.72;
    profile.notes.push("Hostbelastung ist hoch; Darstellung zieht die Körpergrenze zusammen.");
  } else if (pressure !== null && pressure > 0.65) {
    profile.label = "Erhöhte Belastung";
    profile.className = "warn";
    profile.scale = 0.97;
    profile.membrane = 0.84;
    profile.notes.push("Erhöhte Hostbelastung wird als kompakter Körper visualisiert.");
  } else {
    profile.label = "Stabil beobachtet";
    profile.className = "ok";
    profile.notes.push("Keine kritische Hostbelastung aus verfügbaren Messwerten erkannt.");
  }
  if (sensorRate !== null && sensorRate > 0) profile.notes.push(`Sensoraktivität: ${sensorRate.toFixed(1)} Hz.`);
  if (recurrence !== null) profile.notes.push(`Rückkopplung: ${recurrence.toFixed(2)}.`);
  profile.notes.push(`${wesenConnectionArray().length} reale Verbindung(en) beobachtet.`);
  return profile;
}

function wesenUpdateVitals() {
  const root = document.getElementById("wesen-vitals");
  if (!root) return;
  root.innerHTML = wesenVitals().map(([label, value, key]) => `<div class="wesen-metric"><span>${label}</span><strong data-vital="${key}">${value}</strong></div>`).join("");
  const recurrence = wesenRecurrence();
  document.getElementById("wesen-recurrence-value").textContent = recurrence === null ? "—" : recurrence.toFixed(2);
  if (recurrence !== null) {
    wesenState.recurrenceHistory.push(recurrence);
    if (wesenState.recurrenceHistory.length > 100) wesenState.recurrenceHistory.shift();
  }
  wesenDrawRecurrence();
}

function wesenDrawRecurrence() {
  const svg = document.getElementById("wesen-recurrence-chart");
  if (!svg) return;
  const values = wesenState.recurrenceHistory;
  if (!values.length) {
    svg.innerHTML = '<text x="120" y="31" text-anchor="middle" class="wesen-chart-empty">keine Messwerte</text>';
    return;
  }
  const width = 240, height = 56;
  const min = Math.min(0, ...values), max = Math.max(1, ...values);
  const range = Math.max(0.001, max - min);
  const points = values.map((value, index) => `${(index / Math.max(1, values.length - 1)) * width},${height - ((value - min) / range) * (height - 8) - 4}`).join(" ");
  const last = points.split(" ").at(-1).split(",");
  svg.innerHTML = `<polyline class="wesen-chart-line" points="${points}"/><circle class="wesen-chart-point" cx="${last[0]}" cy="${last[1]}" r="3"/>`;
}

function wesenUpdateOrganism() {
  document.querySelectorAll("[data-wesen-organ-value]").forEach((node) => { node.textContent = wesenOrganValue(node.dataset.wesenOrganValue); });
  const profile = wesenAdaptiveProfile();
  const camera = document.getElementById("wesen-camera");
  const membrane = document.getElementById("wesen-membrane");
  if (camera) camera.style.setProperty("--wesen-adaptive-scale", String(profile.scale));
  if (membrane) membrane.style.opacity = String(profile.membrane);
  const reaction = document.getElementById("wesen-reaction-label");
  if (reaction) {
    reaction.textContent = profile.label;
    reaction.dataset.state = profile.className;
  }

  const environment = document.getElementById("wesen-environment-label");
  if (environment) environment.textContent = wesenOrganValue("umwelt");

  const adaptation = document.getElementById("wesen-adaptation");
  if (adaptation) adaptation.innerHTML = `<div class="wesen-adaptation-state ${profile.className}"><span></span><strong>${profile.label}</strong></div>${profile.notes.map((note) => `<p>${note}</p>`).join("")}`;

  document.querySelectorAll(".wesen-organ").forEach((node) => {
    node.classList.toggle("selected", node.dataset.organ === wesenState.selected);
    const value = wesenOrganValue(node.dataset.organ);
    node.classList.toggle("unknown", value === "—" || value === "unbekannt");
  });

  wesenDrawSignals();
  wesenDrawEcho();
}

function wesenDrawSignals() {
  if (wesenState.paused) return;
  const layer = document.getElementById("wesen-signal-layer");
  if (!layer) return;
  layer.innerHTML = "";
  const active = ["sensorik", "innenzustand", "rueckkopplung", "struktur", "ressourcen", "umwelt"];
  const core = wesenOrganPosition("kern");
  active.forEach((id, index) => {
    const value = wesenOrganValue(id);
    if (value === "—" || value === "unbekannt") return;
    const pos = wesenOrganPosition(id);
    const line = document.querySelector(`.wesen-nerve[data-organ="${id}"]`);
    if (!line) return;
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("r", id === "sensorik" ? "4.5" : "3.5");
    dot.setAttribute("class", `wesen-signal-dot wesen-signal-${id}`);
    dot.innerHTML = `<animateMotion dur="${1.1 + index * 0.13}s" repeatCount="indefinite" path="${line.getAttribute("d")}"/>`;
    layer.appendChild(dot);
    if (id === "rueckkopplung") {
      const echo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      echo.setAttribute("r", "3.5");
      echo.setAttribute("class", "wesen-signal-dot wesen-signal-echo");
      const reversePath = `M ${pos[0]} ${pos[1]} Q ${(pos[0] + core[0]) / 2} ${(pos[1] + core[1]) / 2} ${core[0]} ${core[1]}`;
      echo.innerHTML = `<animateMotion begin=".35s" dur="1.5s" repeatCount="indefinite" path="${reversePath}"/>`;
      layer.appendChild(echo);
    }
  });
}

function wesenDrawEcho() {
  const svg = document.getElementById("wesen-self-svg");
  if (!svg) return;
  const latency = wesenLoopLatency();
  const recurrence = wesenRecurrence();
  const delayText = latency === null ? "Latenz unbekannt" : `${latency.toFixed(1)} ms Echo`;
  const opacity = recurrence === null ? 0.25 : 0.25 + wesenClamp(recurrence) * 0.65;
  svg.innerHTML = `
    <g class="wesen-self-primary" transform="translate(67 70)">
      <circle r="43"/><circle cx="0" cy="-23" r="8"/><circle cx="22" cy="9" r="8"/><circle cx="-22" cy="9" r="8"/><circle cx="0" cy="25" r="8"/>
    </g>
    <path class="wesen-self-arrow" d="M116 70 H143"/>
    <g class="wesen-self-echo" transform="translate(194 70)" style="opacity:${opacity}">
      <circle r="43"/><circle cx="0" cy="-23" r="8"/><circle cx="22" cy="9" r="8"/><circle cx="-22" cy="9" r="8"/><circle cx="0" cy="25" r="8"/>
    </g>
    <text x="130" y="130" text-anchor="middle">${delayText}</text>`;
  const metrics = document.getElementById("wesen-self-metrics");
  if (metrics) metrics.innerHTML = `<div><span>Recurrence</span><strong>${recurrence === null ? "—" : recurrence.toFixed(2)}</strong></div><div><span>Loop-Latenz</span><strong>${latency === null ? "—" : `${latency.toFixed(1)} ms`}</strong></div>`;
}

function wesenInspectorData(id) {
  const organ = WESEN_ORGANS.find((item) => item.id === id) || WESEN_ORGANS[0];
  const e = wesenState.embodiment || {};
  const rows = [];
  if (id === "sensorik") {
    rows.push(["Input-Rate", wesenOrganValue(id)], ["Verbindungen", String(wesenConnectionArray().filter((item) => /sensor|camera|audio|micro|weather|input/i.test(JSON.stringify(item))).length)], ["Letzter Input", wesenText(e, ["last_text_input", "last_input", "metrics.last_input"], "—")]);
  } else if (id === "innenzustand") {
    rows.push(["Regulation", wesenOrganValue(id)], ["Energie", wesenFormat(wesenPick(e, ["energy", "metrics.energy", "homeostasis.energy"]), "", 3)], ["Temperatur", wesenFormat(wesenPick(e, ["host.temperature_c", "interoception.temperature_c", "metrics.temperature_c"]), " °C", 1)]);
  } else if (id === "rueckkopplung") {
    rows.push(["Recurrence", wesenOrganValue(id)], ["Latenz", wesenFormat(wesenLoopLatency(), " ms", 1)], ["Messpunkte", String(wesenState.recurrenceHistory.length)]);
  } else if (id === "struktur") {
    rows.push(["Körperverbindungen", String(wesenConnectionArray().length)], ["Körpergrenze", wesenConnectionArray().length ? "dynamisch" : "unbekannt"], ["Modus", "beobachtend"]);
  } else if (id === "ressourcen") {
    rows.push(["CPU", wesenOrganValue(id)], ["RAM", wesenFormat(wesenPick(e, ["host.memory_percent", "interoception.memory_percent", "metrics.memory_percent"]), " %", 0)], ["Host", wesenText(e, ["host.hostname", "interoception.hostname"], "—")]);
  } else if (id === "umwelt") {
    rows.push(["Umgebung", wesenOrganValue(id)], ["Episode", wesenText(e, ["episode", "episode_id", "metrics.episode"], "—")], ["Verfügbarkeit", wesenText(e, ["available"], "—")]);
  } else {
    rows.push(["Feuerrate", wesenOrganValue(id)], ["Tick", wesenText(wesenState.status || {}, ["tick", "runtime.tick"], "—")], ["Runtime", wesenText(wesenState.status || {}, ["state", "runtime.state", "status"], "—")]);
  }
  return { organ, rows };
}

function wesenUpdateInspector() {
  const root = document.getElementById("wesen-inspector");
  if (!root) return;
  const { organ, rows } = wesenInspectorData(wesenState.selected);
  const value = wesenOrganValue(organ.id);
  const unknown = value === "—" || value === "unbekannt";
  const status = document.getElementById("wesen-inspector-status");
  if (status) {
    status.textContent = unknown ? "unbekannt" : "beobachtet";
    status.className = unknown ? "unknown" : "ok";
  }
  root.innerHTML = `
    <div class="wesen-inspector-title wesen-hue-${organ.hue}"><span>${organ.icon}</span><div><strong>${organ.label}</strong><small>${organ.role}</small></div></div>
    <div class="wesen-inspector-rows">${rows.map(([label, item]) => `<div><span>${label}</span><strong>${item}</strong></div>`).join("")}</div>
    <p class="wesen-integrity-note">Diese Ansicht zeigt beobachtete Telemetrie. Fehlende Felder bleiben unbekannt; es werden keine Ersatzwerte simuliert.</p>`;
}

function wesenUpdateConnections() {
  const root = document.getElementById("wesen-connections");
  if (!root) return;
  const connections = wesenConnectionArray();
  if (!connections.length) {
    root.innerHTML = '<p class="wesen-empty">Keine realen Verbindungen gemeldet.</p>';
    return;
  }
  root.innerHTML = connections.slice(0, 10).map((item, index) => {
    const label = wesenText(item, ["label", "name", "id", "connection_id", "device_id"], `Verbindung ${index + 1}`);
    const kind = wesenText(item, ["kind", "type", "category", "direction"], "Verbindung");
    const state = wesenText(item, ["status", "state", "available", "connected"], "beobachtet");
    return `<button type="button" class="wesen-connection-row" data-wesen-connection="${index}"><span class="wesen-connection-led ${wesenStatusClass(state)}"></span><span><strong>${label}</strong><small>${kind}</small></span><em>${state}</em></button>`;
  }).join("");
}

function wesenSnapshot() {
  return {
    sensorRate: wesenSensorRate(),
    recurrence: wesenRecurrence(),
    latency: wesenLoopLatency(),
    pressure: wesenHostPressure(),
    connections: wesenConnectionArray().length,
    regulation: wesenOrganValue("innenzustand"),
  };
}

function wesenRecordEvents() {
  const next = wesenSnapshot();
  const previous = wesenState.lastSnapshot;
  wesenState.lastSnapshot = next;
  if (!previous) return;
  const now = new Date().toLocaleTimeString("de-DE", { hour12: false });
  const events = [];
  const changed = (a, b, threshold = 0.001) => a !== null && b !== null && Math.abs(a - b) > threshold;
  if (changed(next.sensorRate, previous.sensorRate, 0.1)) events.push(["sensorik", "Sensoraktivität verändert", `${previous.sensorRate?.toFixed(1)} → ${next.sensorRate?.toFixed(1)} Hz`]);
  if (changed(next.recurrence, previous.recurrence, 0.01)) events.push(["rueckkopplung", "Rückkopplung verändert", `${previous.recurrence?.toFixed(2)} → ${next.recurrence?.toFixed(2)}`]);
  if (changed(next.latency, previous.latency, 0.5)) events.push(["rueckkopplung", "Loop-Latenz verändert", `${previous.latency?.toFixed(1)} → ${next.latency?.toFixed(1)} ms`]);
  if (next.connections !== previous.connections) events.push(["struktur", "Körpergrenze verändert", `${previous.connections} → ${next.connections} Verbindungen`]);
  if (next.regulation !== previous.regulation) events.push(["innenzustand", "Regulationszustand verändert", `${previous.regulation} → ${next.regulation}`]);
  if (changed(next.pressure, previous.pressure, 0.05)) events.push(["system", "Hostbelastung verändert", `${Math.round((previous.pressure || 0) * 100)} → ${Math.round((next.pressure || 0) * 100)} %`]);
  events.forEach(([type, label, detail]) => wesenState.eventHistory.unshift({ time: now, type, label, detail }));
  if (wesenState.eventHistory.length > 40) wesenState.eventHistory.length = 40;
  wesenUpdateEvents();
}

function wesenUpdateEvents() {
  const root = document.getElementById("wesen-events");
  if (!root) return;
  const active = document.querySelector("#wesen-event-filters .active")?.dataset.wesenFilter || "all";
  const events = wesenState.eventHistory.filter((event) => active === "all" || event.type === active).slice(0, 20);
  if (!events.length) {
    root.innerHTML = '<p class="wesen-empty">Noch keine Zustandsänderung im aktuellen Beobachtungsfenster.</p>';
    return;
  }
  root.innerHTML = events.map((event) => `<button type="button" class="wesen-event-row" data-wesen-event-organ="${event.type}"><time>${event.time}</time><span class="wesen-event-kind ${event.type}"></span><strong>${event.label}</strong><em>${event.detail}</em></button>`).join("");
}

function wesenUpdateLiveState(error = null) {
  const label = document.getElementById("wesen-live-label");
  const dot = document.querySelector(".wesen-live-dot");
  if (!label || !dot) return;
  if (error) {
    label.textContent = "Telemetrie nicht erreichbar";
    dot.dataset.state = "critical";
    return;
  }
  const runtime = wesenText(wesenState.status || {}, ["state", "runtime.state", "status"], "verbunden");
  label.textContent = runtime;
  dot.dataset.state = wesenStatusClass(runtime);
}

function wesenUpdateAll() {
  wesenUpdateVitals();
  wesenUpdateOrganism();
  wesenUpdateInspector();
  wesenUpdateConnections();
  wesenRecordEvents();
  wesenUpdateLiveState();
}

async function wesenPoll() {
  if (wesenState.controller) wesenState.controller.abort();
  wesenState.controller = new AbortController();
  try {
    const [status, embodiment, connections] = await Promise.allSettled([
      wesenReadJson("/api/status", wesenState.controller.signal),
      wesenReadJson("/api/embodiment/state", wesenState.controller.signal),
      wesenReadJson("/api/embodiment/connections", wesenState.controller.signal),
    ]);
    if (status.status === "fulfilled") wesenState.status = status.value;
    if (embodiment.status === "fulfilled") wesenState.embodiment = embodiment.value;
    if (connections.status === "fulfilled") wesenState.connections = connections.value;
    if ([status, embodiment, connections].every((item) => item.status === "rejected")) throw new Error("Keine Telemetriequelle erreichbar");
    wesenUpdateAll();
  } catch (error) {
    if (error.name !== "AbortError") wesenUpdateLiveState(error);
  } finally {
    clearTimeout(wesenState.timer);
    wesenState.timer = setTimeout(wesenPoll, WESEN_POLL_MS);
  }
}

function wesenSelectOrgan(id) {
  if (!WESEN_ORGANS.some((item) => item.id === id)) return;
  wesenState.selected = id;
  wesenUpdateOrganism();
  wesenUpdateInspector();
}

function wesenBindInteractions() {
  const workspace = document.getElementById("tab-wesen");
  if (!workspace || workspace.dataset.bound === "true") return;
  workspace.dataset.bound = "true";
  workspace.addEventListener("click", (event) => {
    const organ = event.target.closest(".wesen-organ");
    if (organ) wesenSelectOrgan(organ.dataset.organ);

    const eventRow = event.target.closest("[data-wesen-event-organ]");
    if (eventRow && WESEN_ORGANS.some((item) => item.id === eventRow.dataset.wesenEventOrgan)) wesenSelectOrgan(eventRow.dataset.wesenEventOrgan);

    const filter = event.target.closest("[data-wesen-filter]");
    if (filter) {
      document.querySelectorAll("#wesen-event-filters [data-wesen-filter]").forEach((item) => item.classList.toggle("active", item === filter));
      wesenUpdateEvents();
    }

    const view = event.target.closest("[data-wesen-view]");
    if (view) {
      view.classList.toggle("active");
      document.getElementById("wesen-svg")?.classList.toggle(`show-${view.dataset.wesenView}`, view.classList.contains("active"));
    }

    const action = event.target.closest("[data-wesen-action]")?.dataset.wesenAction;
    if (action === "reset-view") wesenSelectOrgan("sensorik");
    if (action === "pause-visual") {
      wesenState.paused = !wesenState.paused;
      event.target.classList.toggle("active", wesenState.paused);
      event.target.textContent = wesenState.paused ? "▶ Visualisierung" : "Ⅱ Visualisierung";
      if (!wesenState.paused) wesenDrawSignals();
      else document.getElementById("wesen-signal-layer").innerHTML = "";
    }
  });

  workspace.addEventListener("keydown", (event) => {
    const organ = event.target.closest(".wesen-organ");
    if (organ && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      wesenSelectOrgan(organ.dataset.organ);
    }
  });

  document.getElementById("wesen-stage")?.addEventListener("dblclick", () => wesenSelectOrgan("sensorik"));
}

function initWesenWorkspace() {
  wesenEnsureWorkspace();
  wesenEnsureNavButton();
  if (!wesenState.timer) wesenPoll();
}

window.Brain5DWesen = { init: initWesenWorkspace, activate: wesenActivate, refresh: wesenPoll };

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initWesenWorkspace, { once: true });
else initWesenWorkspace();
