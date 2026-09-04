"use strict";

const POLL_MS = 2000;
let lastConnections = null;
let lastStatus = null;
let selectedConnectionId = null;

function byId(id) {
  return document.getElementById(id);
}

function addStylesheet() {
  if (document.querySelector('link[href="/embodiment-self-model.css"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/embodiment-self-model.css";
  document.head.append(link);
}

function text(value, fallback = "—") {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

function number(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function bytes(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  const amount = Number(value);
  const units = ["B", "KiB", "MiB", "GiB", "TiB"];
  let index = 0;
  let current = amount;
  while (Math.abs(current) >= 1024 && index < units.length - 1) {
    current /= 1024;
    index += 1;
  }
  return `${current.toFixed(index < 2 ? 0 : 1)} ${units[index]}`;
}

function iconFor(connection) {
  const id = connection.connection_id || "";
  if (id.includes("camera")) return "◉";
  if (id.includes("microphone")) return "◖";
  if (id.includes("display")) return "▣";
  if (id.includes("audio")) return "◁";
  if (id.includes("printer")) return "▤";
  if (id.includes("robot")) return "⌁";
  if (id.includes("internet")) return "◎";
  if (id.includes("network")) return "⌘";
  if (id.includes("storage")) return "◇";
  if (id.includes("compute")) return "◆";
  if (connection.kind === "sensor") return "○";
  if (connection.kind === "actuator") return "↗";
  if (connection.kind === "service") return "⇄";
  if (connection.kind === "data") return "≋";
  return "·";
}

function createShell() {
  const tab = byId("tab-embodiment");
  const oldMap = byId("embodiment-living-map");
  if (!tab || !oldMap || byId("real-body-shell")) return;

  const shell = document.createElement("section");
  shell.id = "real-body-shell";
  shell.className = "real-body-shell";
  shell.innerHTML = `
    <header class="real-body-heading">
      <div>
        <span class="workspace-kicker">REAL BODY · OBSERVED ONLY</span>
        <h3>Selbstbild des aktuellen Systems</h3>
        <p>Die Form entsteht ausschließlich aus aktuell erkannten Verbindungen und gemessenen Hostwerten. Nicht erkannte Hardware wird nicht als Organ dargestellt.</p>
      </div>
      <div class="real-body-summary">
        <span>Organe<strong id="real-body-organ-count">0</strong></span>
        <span>aktiv<strong id="real-body-active-count">0</strong></span>
        <span>autorisiert<strong id="real-body-authorized-count">0</strong></span>
        <span>Sample<strong id="real-body-sample">—</strong></span>
      </div>
    </header>

    <div class="real-body-stage" id="real-body-stage">
      <svg class="real-body-links" id="real-body-links" aria-hidden="true"></svg>
      <div class="real-body-organs" id="real-body-organs" role="list" aria-label="Aktuell erkannte Körperorgane"></div>
      <article class="real-body-core" id="real-body-core">
        <div class="core-aura" aria-hidden="true"></div>
        <img src="/assets/brain5d-being.svg" alt="" class="real-body-being">
        <span class="real-body-kicker">BRAIN-5D</span>
        <strong id="real-body-runtime-state">IDLE</strong>
        <small id="real-body-hostname">host unknown</small>
        <div class="real-body-vitals">
          <span><b id="real-body-cpu">—</b><small>CPU</small></span>
          <span><b id="real-body-memory">—</b><small>RAM</small></span>
          <span><b id="real-body-temperature">—</b><small>TEMP</small></span>
          <span><b id="real-body-disk">—</b><small>DISK FREE</small></span>
          <span><b id="real-body-network">—</b><small>NETWORK</small></span>
          <span><b id="real-body-processes">—</b><small>PROCESSES</small></span>
        </div>
      </article>
    </div>

    <div class="real-body-lower">
      <section class="real-body-detail" id="real-body-detail" aria-live="polite">
        <span class="workspace-kicker">SELECTED ORGAN</span>
        <h4 id="real-body-detail-name">Systemkern</h4>
        <p id="real-body-detail-message">Wähle ein erkanntes Organ, um Herkunft, Fähigkeiten, Berechtigungen und Zustand zu sehen.</p>
        <dl id="real-body-detail-fields"></dl>
      </section>
      <section class="real-body-telemetry">
        <span class="workspace-kicker">INNERE MESSWERTE</span>
        <div id="real-body-telemetry-grid" class="real-body-telemetry-grid"></div>
      </section>
      <details class="real-body-boundary">
        <summary>Nicht zum aktuellen Körper gehörende Katalogeinträge <strong id="real-body-unavailable-count">0</strong></summary>
        <div id="real-body-unavailable"></div>
      </details>
    </div>
  `;

  oldMap.before(shell);
  oldMap.classList.add("legacy-embodiment-details");
}

function telemetryItems(host) {
  return [
    ["CPU Kerne", `${text(host.cpu_physical_count)} phys · ${text(host.cpu_logical_count)} log`],
    ["CPU Frequenz", host.cpu_frequency_mhz == null ? "unbekannt" : `${number(host.cpu_frequency_mhz, 0)} MHz`],
    ["RAM verfügbar", bytes(host.memory_available_bytes)],
    ["RAM gesamt", bytes(host.memory_total_bytes)],
    ["Swap", host.swap_total_bytes == null ? "unbekannt" : `${bytes(host.swap_used_bytes)} / ${bytes(host.swap_total_bytes)}`],
    ["Disk I/O", `${bytes(host.disk_read_bytes)} read · ${bytes(host.disk_write_bytes)} write`],
    ["Netz I/O", `${bytes(host.network_bytes_received)} in · ${bytes(host.network_bytes_sent)} out`],
    ["Netzfehler", `${text(host.network_errors_in)} in · ${text(host.network_errors_out)} out`],
    ["Akku", host.battery_percent == null ? "nicht geliefert" : `${number(host.battery_percent, 0)}%${host.battery_plugged ? " · Netz" : ""}`],
    ["Lüfter", host.fan_rpm == null ? "nicht geliefert" : `${number(host.fan_rpm, 0)} rpm`],
    ["System", `${text(host.platform)} ${text(host.platform_release, "")}`.trim()],
    ["Architektur", text(host.machine)],
  ];
}

function renderHost(host = {}) {
  byId("real-body-hostname").textContent = text(host.hostname, "host unknown");
  byId("real-body-cpu").textContent = host.cpu_percent == null ? "—" : `${number(host.cpu_percent, 1)}%`;
  byId("real-body-memory").textContent = host.memory_percent == null ? "—" : `${number(host.memory_percent, 1)}%`;
  byId("real-body-temperature").textContent = host.temperature_c == null ? "UNKNOWN" : `${number(host.temperature_c, 1)}°C`;
  byId("real-body-disk").textContent = bytes(host.disk_free_bytes);
  byId("real-body-network").textContent = host.network_up === true ? "UP" : host.network_up === false ? "DOWN" : "UNKNOWN";
  byId("real-body-processes").textContent = number(host.process_count, 0);
  byId("real-body-sample").textContent = host.unix_time ? new Date(Number(host.unix_time) * 1000).toLocaleTimeString() : "—";

  const grid = byId("real-body-telemetry-grid");
  if (!grid) return;
  grid.replaceChildren();
  for (const [label, value] of telemetryItems(host)) {
    const item = document.createElement("div");
    const term = document.createElement("span");
    const result = document.createElement("strong");
    term.textContent = label;
    result.textContent = value;
    item.append(term, result);
    grid.append(item);
  }
}

function renderStatus(status = {}) {
  const raw = status.status || status.runtime?.state || "idle";
  byId("real-body-runtime-state").textContent = String(raw).toUpperCase();
  byId("real-body-core").dataset.state = String(raw).toLowerCase();
}

function detailRows(connection) {
  return [
    ["ID", connection.connection_id],
    ["Typ", connection.kind],
    ["Beziehung", connection.relationship],
    ["Status", connection.status],
    ["Verfügbar", connection.available ? "ja" : "nein"],
    ["Autorisiert", connection.authorized ? "ja" : "nein"],
    ["Aktiv", connection.active ? "ja" : "nein"],
    ["Modalitäten", (connection.modalities || []).join(" · ") || "keine gemeldet"],
    ["Fähigkeiten", (connection.capabilities || []).join(" · ") || "keine gemeldet"],
    ["Berechtigungen", (connection.permissions || []).join(" · ") || "keine erteilt"],
    ["Latenz", connection.latency_ms == null ? "nicht gemessen" : `${number(connection.latency_ms, 1)} ms`],
    ["Gefahrenstufe", connection.hazard_level],
    ["Quelle", connection.source],
  ];
}

function showDetail(connection) {
  selectedConnectionId = connection.connection_id;
  byId("real-body-detail-name").textContent = connection.name || connection.connection_id;
  byId("real-body-detail-message").textContent = connection.message || "Kein zusätzlicher Status geliefert.";
  const list = byId("real-body-detail-fields");
  list.replaceChildren();
  for (const [label, value] of detailRows(connection)) {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = text(value);
    list.append(dt, dd);
  }
  document.querySelectorAll(".real-body-organ[data-selected]").forEach((node) => delete node.dataset.selected);
  const selected = document.querySelector(`.real-body-organ[data-connection-id="${CSS.escape(connection.connection_id)}"]`);
  if (selected) selected.dataset.selected = "true";
}

function layoutOrgans(connections) {
  const organRoot = byId("real-body-organs");
  if (!organRoot) return;
  organRoot.replaceChildren();

  const available = connections.filter((item) => item.available);
  const unavailable = connections.filter((item) => !item.available);
  byId("real-body-organ-count").textContent = String(available.length);
  byId("real-body-active-count").textContent = String(available.filter((item) => item.active).length);
  byId("real-body-authorized-count").textContent = String(available.filter((item) => item.authorized).length);
  byId("real-body-unavailable-count").textContent = String(unavailable.length);

  available.forEach((connection) => {
    const node = document.createElement("button");
    node.type = "button";
    node.className = "real-body-organ";
    node.dataset.kind = connection.kind || "resource";
    node.dataset.status = connection.status || "available";
    node.dataset.active = String(Boolean(connection.active));
    node.dataset.authorized = String(Boolean(connection.authorized));
    node.dataset.connectionId = connection.connection_id;
    node.innerHTML = `<i aria-hidden="true">${iconFor(connection)}</i><span>${text(connection.name, connection.connection_id)}</span><small>${text(connection.relationship)}</small>`;
    node.title = connection.message || connection.connection_id;
    node.setAttribute("role", "listitem");
    node.addEventListener("click", () => showDetail(connection));
    organRoot.append(node);
  });

  const unavailableRoot = byId("real-body-unavailable");
  unavailableRoot.replaceChildren();
  for (const connection of unavailable) {
    const item = document.createElement("span");
    item.textContent = connection.name || connection.connection_id;
    item.title = connection.message || "Nicht erkannt";
    unavailableRoot.append(item);
  }

  if (selectedConnectionId) {
    const stillPresent = available.find((item) => item.connection_id === selectedConnectionId);
    if (stillPresent) showDetail(stillPresent);
    else selectedConnectionId = null;
  }
  requestAnimationFrame(drawLinks);
}

function drawLinks() {
  const stage = byId("real-body-stage");
  const svg = byId("real-body-links");
  const core = byId("real-body-core");
  if (!stage || !svg || !core) return;
  const stageBox = stage.getBoundingClientRect();
  const coreBox = core.getBoundingClientRect();
  svg.setAttribute("viewBox", `0 0 ${stageBox.width} ${stageBox.height}`);
  svg.replaceChildren();
  const x1 = coreBox.left - stageBox.left + coreBox.width / 2;
  const y1 = coreBox.top - stageBox.top + coreBox.height / 2;
  for (const organ of stage.querySelectorAll(".real-body-organ")) {
    const box = organ.getBoundingClientRect();
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", String(x1));
    line.setAttribute("y1", String(y1));
    line.setAttribute("x2", String(box.left - stageBox.left + box.width / 2));
    line.setAttribute("y2", String(box.top - stageBox.top + box.height / 2));
    line.dataset.kind = organ.dataset.kind || "resource";
    line.dataset.active = organ.dataset.active || "false";
    svg.append(line);
  }
}

function renderConnections(payload = {}) {
  lastConnections = payload;
  renderHost(payload.host || {});
  layoutOrgans(Array.isArray(payload.connections) ? payload.connections : []);
}

async function readJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

async function refresh() {
  if (!byId("real-body-shell")) return;
  const results = await Promise.allSettled([
    readJson("/api/embodiment/connections"),
    readJson("/api/status"),
  ]);
  if (results[0].status === "fulfilled") renderConnections(results[0].value);
  if (results[1].status === "fulfilled") {
    lastStatus = results[1].value;
    renderStatus(lastStatus);
  }
  if (results.some((result) => result.status === "rejected")) {
    byId("real-body-shell").dataset.telemetry = "degraded";
  } else {
    byId("real-body-shell").dataset.telemetry = "live";
  }
}

function init() {
  addStylesheet();
  createShell();
  if (!byId("real-body-shell")) return;
  refresh();
  window.setInterval(refresh, POLL_MS);
  window.addEventListener("resize", drawLinks, { passive: true });
  new MutationObserver(drawLinks).observe(document.body, {
    attributes: true,
    attributeFilter: ["data-theme", "class"],
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}

export { drawLinks, refresh };
