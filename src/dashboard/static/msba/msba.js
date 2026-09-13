"use strict";

const REFRESH_MS = 5000;
let timer = null;

const byId = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "—").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[char]);

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function text(id, value) {
  const node = byId(id);
  if (node) node.textContent = String(value ?? "—");
}

function displayValue(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "ja" : "nein";
  if (typeof value === "number") return Number.isInteger(value) ? value.toLocaleString("de-DE") : value.toLocaleString("de-DE", { maximumFractionDigits: 4 });
  return String(value).replaceAll("_", " ");
}

function kvMarkup(entries) {
  return entries.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(displayValue(value))}</strong></div>`).join("");
}

function availableConnectionIds(connectionPayload) {
  const rows = Array.isArray(connectionPayload?.connections) ? connectionPayload.connections : [];
  return new Set(rows.filter((item) => item?.available && item?.connection_id).map((item) => String(item.connection_id)));
}

function endpointReachable(endpoint, available) {
  if (!endpoint || String(endpoint).startsWith("virtual.")) return true;
  return [...available].some((item) => item === endpoint || item.startsWith(`${endpoint}.`));
}

function renderPipelines(catalog, connectionPayload) {
  const root = byId("pipeline-list");
  if (!root) return;
  const pipelines = Array.isArray(catalog?.pipelines) ? catalog.pipelines : [];
  const available = availableConnectionIds(connectionPayload);
  const states = pipelines.map((pipeline) => ({
    pipeline,
    reachable: endpointReachable(pipeline.source_connection, available) && endpointReachable(pipeline.sink_connection, available),
  }));
  text("pipeline-reachable", states.filter((item) => item.reachable).length);
  if (!pipelines.length) {
    root.innerHTML = '<p class="loading">Keine Pipeline-Deskriptoren publiziert.</p>';
    return;
  }
  root.innerHTML = states.map(({ pipeline, reachable }) => {
    const stages = Array.isArray(pipeline.stages) ? pipeline.stages.join(" → ") : "—";
    const endpoint = [pipeline.source_connection, pipeline.sink_connection].filter(Boolean).join(" → ") || "virtuell / intern";
    const source = pipeline.reachable === reachable ? "catalog + live inventory" : "live inventory override";
    return `<article class="pipeline-row">
      <div><strong>${escapeHtml(pipeline.name || pipeline.pipeline_id)}</strong><small>${escapeHtml(pipeline.direction || "unknown")} · ${escapeHtml(endpoint)} · ${escapeHtml(source)}</small></div>
      <div class="pipeline-stages">${escapeHtml(stages)}</div>
      <span class="state ${reachable ? "reachable" : "unreachable"}">${reachable ? "ERREICHBAR" : "NICHT ERREICHBAR"}</span>
    </article>`;
  }).join("");
}

function renderAreas(catalog) {
  const root = byId("area-list");
  if (!root) return;
  const areas = Array.isArray(catalog?.areas) ? catalog.areas : [];
  if (!areas.length) {
    root.innerHTML = '<p class="loading">Keine Netzbereiche publiziert.</p>';
    return;
  }
  root.innerHTML = areas.map((area) => {
    const modalities = [...(area.input_modalities || []), ...(area.output_modalities || [])];
    const unique = [...new Set(modalities)].slice(0, 8);
    return `<article class="area-card">
      <header><h3>${escapeHtml(area.name || area.area_id)}</h3><span class="kind">${escapeHtml(area.kind || "area")}</span></header>
      <p>${escapeHtml(area.architecture || "unknown architecture")} · ${escapeHtml(area.implementation_status || "unknown")}</p>
      <p>${escapeHtml((area.roles || []).join(" · ") || "keine Rollen publiziert")}</p>
      <div class="tokens">${unique.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>
    </article>`;
  }).join("");
}

function renderGateway(gateway, productiveGateway) {
  const topology = gateway?.topology || {};
  const stateRoot = byId("gateway-state");
  if (stateRoot) stateRoot.innerHTML = kvMarkup([
    ["Gateway ID", gateway?.gateway_id],
    ["Zustand", gateway?.state],
    ["Bedingung", gateway?.condition || "keine"],
    ["Experiment", gateway?.experiment_id || "keines"],
    ["Seed", gateway?.seed],
    ["Ressourcenmodus", gateway?.resource_mode],
    ["Modalität", topology.modality],
    ["Topologie", topology.source_area && topology.target_area ? `${topology.source_area} → ${topology.target_area}` : "—"],
    ["Kanäle", topology.source_channels && topology.target_channels ? `${topology.source_channels} → ${topology.target_channels}` : "—"],
    ["Kanten", topology.edges],
    ["Plastizitätsregel", topology.plasticity_rule],
    ["Gateway-Plastizität", gateway?.gateway_plasticity_allowed ? "aktiv" : "nicht aktiv"],
  ]);

  const metricsRoot = byId("gateway-metrics");
  const metrics = gateway?.metrics || {};
  if (metricsRoot) metricsRoot.innerHTML = kvMarkup([
    ["Gateway Events", metrics.gateway_events],
    ["Spikes", metrics.spikes],
    ["Synaptic Ops", metrics.synaptic_operations],
    ["Queue Depth", metrics.queue_depth],
    ["CPU Time ms", metrics.cpu_time_ms],
    ["Estimated Energy", metrics.estimated_energy],
    ["Measured Energy", metrics.measured_energy],
    ["Latency ms", metrics.latency_ms],
    ["Dropped Events", metrics.dropped_events],
    ["Throttled Ticks", metrics.throttled_ticks],
    ["Plasticity Updates", metrics.plasticity_updates],
    ["Structural Changes", metrics.structural_changes],
  ]);

  const limitsRoot = byId("gateway-limits");
  const limits = gateway?.limits || {};
  if (limitsRoot) limitsRoot.innerHTML = kvMarkup([
    ["Events / Tick", limits.max_events_per_tick],
    ["Spikes / Tick", limits.max_spikes_per_tick],
    ["Kanten", limits.max_edges],
    ["Struktur / Fenster", limits.max_structural_changes_window],
    ["Gewichtsdelta / Fenster", limits.max_weight_delta_window],
    ["Queue Depth", limits.max_queue_depth],
    ["Latenz ms", limits.max_latency_ms],
    ["Speicher Bytes", limits.max_memory_bytes],
  ]);

  const productive = productiveGateway || gateway?.productive_gateway || {};
  const productiveNode = byId("productive-gateway");
  if (productiveNode) {
    productiveNode.textContent = productive.available
      ? "Produktiver Gateway-Pfad als verfügbar gemeldet."
      : `Produktiver Gateway gesperrt · ${String(productive.reason || "validation incomplete").replaceAll("_", " ")}`;
    productiveNode.style.borderLeftColor = productive.available ? "var(--accent)" : "var(--danger)";
  }
}

function renderConnections(payload) {
  text("connection-count", payload?.count ?? 0);
  text("connection-available", payload?.available ?? 0);
  text("connection-authorized", payload?.authorized ?? 0);
  text("connection-active", payload?.active ?? 0);
}

function setUnavailable(message) {
  text("status-system", "nicht verfügbar");
  text("status-maturity", "unbekannt");
  text("status-gateway", "unbekannt");
  for (const id of ["pipeline-list", "area-list", "gateway-state", "gateway-metrics", "gateway-limits"]) {
    const node = byId(id);
    if (node) node.innerHTML = `<p class="loading error">${escapeHtml(message)}</p>`;
  }
}

async function refresh() {
  try {
    const [symbiosis, connections] = await Promise.all([
      getJson("/api/embodiment/neural-symbiosis"),
      getJson("/api/embodiment/connections"),
    ]);
    text("status-system", symbiosis.status || "unknown");
    text("status-maturity", symbiosis.maturity_level || "unknown");
    text("status-gateway", symbiosis.gateway?.state || "unknown");
    renderConnections(connections);
    renderPipelines(symbiosis.catalog || {}, connections);
    renderAreas(symbiosis.catalog || {});
    renderGateway(symbiosis.gateway || {}, symbiosis.productive_gateway || {});
    text("last-refresh", `aktualisiert ${new Date().toLocaleString("de-DE")}`);
  } catch (error) {
    setUnavailable(`Live-Verträge nicht erreichbar: ${error.message}`);
    text("last-refresh", `Fehler ${new Date().toLocaleTimeString("de-DE")}`);
  }
}

refresh();
timer = window.setInterval(refresh, REFRESH_MS);
window.addEventListener("beforeunload", () => timer && clearInterval(timer), { once: true });
