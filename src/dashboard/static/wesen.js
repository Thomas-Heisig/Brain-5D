/* MHRN Wesen integration shell.
 * The existing adaptive Wesen implementation remains in wesen-base.js.
 * This shell keeps technical Embodiment as a sibling workspace of Wesen and keeps
 * Settings/Release as footer utilities instead of primary workspaces.
 */
import "./wesen-base.js";

let sensorRefreshTimer = null;

function byId(id) {
  return document.getElementById(id);
}

function injectIntegrationStyles() {
  if (byId("wesen-integration-styles")) return;
  const style = document.createElement("style");
  style.id = "wesen-integration-styles";
  style.textContent = `
    .tab-nav .wesen-utility-hidden { display: none !important; }
    .wesen-technical-body { margin: 1.25rem 0 2rem; border: 1px solid var(--line, #1c4155); border-radius: 14px; overflow: clip; background: rgba(127,127,127,.035); }
    .wesen-technical-body > summary { cursor: pointer; padding: 1rem 1.15rem; display: flex; justify-content: space-between; gap: 1rem; align-items: center; list-style: none; }
    .wesen-technical-body > summary::-webkit-details-marker { display: none; }
    .wesen-technical-body > summary div { display: grid; gap: .2rem; }
    .wesen-technical-body > summary small { opacity: .68; }
    .wesen-technical-body-content { padding: 0 1rem 1rem; }
    .wesen-technical-body-content > .workspace-header { margin-top: .25rem; }
    .wesen-subnav { display:flex; flex-wrap:wrap; gap:.45rem; margin:.7rem 0 1rem; }
    .wesen-subnav button { border:1px solid var(--line,#1c4155); background:transparent; color:inherit; border-radius:8px; padding:.5rem .75rem; cursor:pointer; }
    .wesen-subnav button.active { background:rgba(127,127,127,.12); box-shadow:inset 0 -2px 0 currentColor; }
    .footer-tools { display: flex; gap: .45rem; align-items: center; flex-wrap:wrap; }
    .footer-nav-btn { border: 1px solid var(--line, #1c4155); background: transparent; color: inherit; border-radius: 8px; padding: .45rem .7rem; cursor: pointer; font: inherit; }
    .footer-nav-btn:hover, .footer-nav-btn:focus-visible { background: rgba(127,127,127,.12); outline: none; }
    .wesen-sensor-controls { margin-top: 1rem; border: 1px solid var(--line, #1c4155); border-radius: 10px; padding: 1rem; background: rgba(127,127,127,.035); }
    .wesen-sensor-controls header { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; margin-bottom: .75rem; }
    .wesen-sensor-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: .75rem; align-items: center; border-top: 1px solid rgba(127,127,127,.15); padding: .7rem 0; }
    .wesen-sensor-row:first-child { border-top: 0; }
    .wesen-sensor-meta { display: grid; gap: .15rem; }
    .wesen-sensor-meta small { opacity: .7; }
    .wesen-sensor-switch { display: inline-flex; gap: .45rem; align-items: center; white-space: nowrap; }
    .wesen-sensor-switch input { accent-color: var(--accent, #56c8d8); }
    @media (max-width: 900px) { .footer-tools { width: 100%; justify-content: flex-end; } .wesen-technical-body > summary { align-items: flex-start; flex-direction: column; } }
  `;
  document.head.appendChild(style);
}

function mergeEmbodimentIntoWesen() {
  const wesen = byId("tab-wesen");
  const embodiment = byId("tab-embodiment");
  if (!wesen || !embodiment) return;

  for (const [workspace, current] of [[wesen, "wesen"], [embodiment, "embodiment"]]) {
    if (workspace.querySelector(":scope > .wesen-subnav")) continue;
    const nav = document.createElement("nav");
    nav.className = "wesen-subnav";
    nav.setAttribute("aria-label", "Runtime und Wesen Unterbereiche");
    nav.innerHTML = `
      <button type="button" data-wesen-tab="wesen" ${current === "wesen" ? 'class="active"' : ''}>🧠 Wesen</button>
      <button type="button" data-wesen-tab="embodiment" ${current === "embodiment" ? 'class="active"' : ''}>◈ Embodiment</button>`;
    const header = workspace.querySelector(":scope > .workspace-header, :scope > header");
    if (header) header.insertAdjacentElement("afterend", nav); else workspace.prepend(nav);
    nav.addEventListener("click", (event) => {
      const button = event.target.closest("[data-wesen-tab]");
      if (button) activateUtilityTab(button.dataset.wesenTab);
    });
  }
}

function sensorEscape(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function sensorReason(sensor) {
  if (sensor.active) return "ACTIVE";
  if (!sensor.available) return sensor.last_error || "UNAVAILABLE: no detected adapter";
  if (!sensor.configured || !sensor.adapter_id) return "ADAPTER_UNAVAILABLE: no configured adapter";
  if (!sensor.authorized) return "AUTHORIZATION_REQUIRED";
  return "READY";
}

function ensureSensorControls() {
  const content = byId("tab-embodiment");
  if (!content || document.getElementById("wesen-sensor-controls")) return;
  const panel = document.createElement("section");
  panel.id = "wesen-sensor-controls";
  panel.className = "wesen-sensor-controls";
  panel.innerHTML = `<header><div><span class="workspace-kicker">SENSOR LIFECYCLE</span><strong>Einzelne Sinne</strong></div><small>Discovery ≠ authorization ≠ active</small></header><div id="wesen-sensor-list"><span>Sensoren werden geladen …</span></div><small>Der globale Pipeline-Schalter erlaubt nur Sensorverarbeitung; er aktiviert keine Hardware.</small>`;
  content.appendChild(panel);
}

function renderSensors(payload) {
  ensureSensorControls();
  const root = byId("wesen-sensor-list");
  if (!root) return;
  const sensors = Array.isArray(payload?.sensors) ? payload.sensors : [];
  root.innerHTML = sensors.length ? sensors.map((sensor) => {
    const id = sensorEscape(sensor.connection_id);
    const disabled = !sensor.available || !sensor.configured || !sensor.adapter_id || !sensor.authorized;
    const state = sensor.active ? "ON" : "OFF";
    return `<div class="wesen-sensor-row"><div class="wesen-sensor-meta"><strong>${sensorEscape(sensor.name || sensor.connection_id)}</strong><small>${sensorEscape(sensor.modality || (sensor.modalities || []).join(", ") || "sensor")} · ${sensorEscape(sensor.health || sensor.status || "UNKNOWN")} · ${sensorEscape(sensorReason(sensor))}</small></div><label class="wesen-sensor-switch"><span>${state}</span><input type="checkbox" data-sensor-id="${id}" ${sensor.active ? "checked" : ""} ${disabled ? "disabled" : ""} title="${sensorEscape(sensorReason(sensor))}"></label></div>`;
  }).join("") : "<span>Keine Sensoren publiziert.</span>";
  root.querySelectorAll("[data-sensor-id]").forEach((input) => input.addEventListener("change", async (event) => {
    const control = event.currentTarget;
    const sensorId = control.dataset.sensorId;
    try {
      const response = await fetch(`/api/embodiment/sensors/${encodeURIComponent(sensorId)}/${control.checked ? "enable" : "disable"}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ operator_source: "wesen", tick: 0 }) });
      if (!response.ok) throw new Error((await response.json()).error || `HTTP ${response.status}`);
    } catch (error) {
      control.checked = !control.checked;
    }
    refreshSensors();
  }));
}

async function refreshSensors() {
  try {
    const response = await fetch("/api/embodiment/sensors", { cache: "no-store" });
    if (response.ok) renderSensors(await response.json());
  } catch (_) { /* unavailable sensor state remains visible */ }
}

function configurePrimaryNavigation() {
  const nav = document.querySelector(".tab-nav");
  if (!nav) return;

  const embodimentButton = nav.querySelector('.tab-btn[data-tab="embodiment"]');
  if (embodimentButton) {
    embodimentButton.classList.add("wesen-utility-hidden");
    embodimentButton.setAttribute("aria-hidden", "true");
    embodimentButton.tabIndex = -1;
  }

  for (const name of ["network", "settings", "gate"]) {
    const button = nav.querySelector(`.tab-btn[data-tab="${name}"]`);
    if (!button) continue;
    button.classList.add("wesen-utility-hidden");
    button.setAttribute("aria-hidden", "true");
    button.tabIndex = -1;
  }

  const bodyShortcut = document.querySelector('[data-overview-tab="embodiment"]');
  if (bodyShortcut) {
    bodyShortcut.dataset.overviewTab = "wesen";
    bodyShortcut.textContent = "◉ Wesen öffnen";
  }
}

function activateUtilityTab(name) {
  const hiddenButton = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (hiddenButton) hiddenButton.click();
}

function ensureFooterTools() {
  const footer = document.querySelector(".site-footer");
  if (!footer || footer.querySelector(".footer-tools")) return;
  const tools = document.createElement("div");
  tools.className = "footer-tools";
  tools.setAttribute("aria-label", "Systembereiche");
  tools.innerHTML = `
    <button type="button" class="footer-nav-btn" data-footer-tab="overview">📊 Dashboard</button>
    <button type="button" class="footer-nav-btn" data-footer-tab="research">🔬 Wissenschaft</button>
    <button type="button" class="footer-nav-btn" data-footer-tab="wesen">🧠 Runtime & Wesen</button>
    <button type="button" class="footer-nav-btn" data-footer-tab="settings">⚙ Settings</button>`;
  const health = byId("footer-status");
  if (health) health.insertBefore(tools, health.firstChild);
  else footer.appendChild(tools);
  tools.addEventListener("click", (event) => {
    const button = event.target.closest("[data-footer-tab]");
    if (button) activateUtilityTab(button.dataset.footerTab);
  });
}

function integrateShell() {
  injectIntegrationStyles();
  configurePrimaryNavigation();
  mergeEmbodimentIntoWesen();
  ensureSensorControls();
  ensureFooterTools();
  refreshSensors();
  if (sensorRefreshTimer) clearInterval(sensorRefreshTimer);
  sensorRefreshTimer = setInterval(refreshSensors, 3000);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", integrateShell, { once: true });
} else {
  integrateShell();
}

window.Brain5DWesenIntegration = { refresh: integrateShell };
