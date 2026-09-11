"use strict";
import { apiGet, apiPost } from "../core/api.js";

let refreshTimer = null;
function ensurePanel() {
  let panel = document.getElementById("mhrn-runtime-io");
  if (panel) return panel;
  const workspace = document.getElementById("tab-wesen"); if (!workspace) return null;
  panel = document.createElement("section"); panel.id = "mhrn-runtime-io"; panel.className = "mhrn-runtime-io card";
  panel.innerHTML = `<header><div><span class="workspace-kicker">RUNTIME INPUT / OUTPUT</span><h2>Manuelle Operator-Injektion</h2><p>Nur registrierte Input-Neuronen · Experimentmodus ist fail-closed · scientific_evidence=false.</p></div><span id="runtime-io-mode" class="maturity-state pending">unknown</span></header>
  <form id="runtime-io-form"><label>Input-Neuron<select id="runtime-io-neuron"></select></label><label>Strom<input id="runtime-io-current" type="number" step="0.1" min="-1000" max="1000" value="10"></label><label>Ticks<input id="runtime-io-ticks" type="number" min="1" max="10000" value="1"></label><button type="submit">Strom injizieren</button></form>
  <div class="runtime-io-readout"><strong id="runtime-io-status">lade …</strong><pre id="runtime-io-output">Noch kein manueller Eingriff.</pre></div>`;
  const anchor = workspace.querySelector(":scope > header"); if (anchor) anchor.insertAdjacentElement("afterend", panel); else workspace.prepend(panel);
  panel.querySelector("#runtime-io-form").addEventListener("submit", inject);
  return panel;
}
function render(payload) {
  const panel = ensurePanel(); if (!panel) return;
  const select = panel.querySelector("#runtime-io-neuron");
  const selected = select.value;
  select.innerHTML = (payload.input_neurons || []).map((n) => `<option value="${n.neuron_id}">${n.neuron_id} · v=${Number(n.v).toFixed(2)} · u=${Number(n.u).toFixed(2)}</option>`).join("");
  if ([...select.options].some((opt) => opt.value === selected)) select.value = selected;
  panel.querySelector("#runtime-io-mode").textContent = `${payload.mode || "unknown"} · tick ${payload.tick ?? "unknown"}`;
  const submit = panel.querySelector('button[type="submit"]'); submit.disabled = !payload.manual_injection_allowed || !payload.input_neurons?.length;
  panel.querySelector("#runtime-io-status").textContent = payload.manual_injection_allowed ? `bereit · ${payload.counts?.input_neurons ?? 0} Inputs / ${payload.counts?.output_neurons ?? 0} Outputs` : `gesperrt · ${payload.mode || payload.controller_state || "unknown"}`;
}
async function refresh() {
  try { render(await apiGet("/api/runtime/io")); } catch (error) { const panel = ensurePanel(); if (panel) panel.querySelector("#runtime-io-status").textContent = `nicht verfügbar · ${error.message}`; }
}
async function inject(event) {
  event.preventDefault(); const panel = ensurePanel(); if (!panel) return;
  const body = { neuron_id: Number(panel.querySelector("#runtime-io-neuron").value), current: Number(panel.querySelector("#runtime-io-current").value), ticks: Number(panel.querySelector("#runtime-io-ticks").value) };
  try {
    const result = await apiPost("/api/runtime/io/inject", body);
    panel.querySelector("#runtime-io-output").textContent = JSON.stringify({ operator_intervention: result.operator_intervention, scientific_evidence: result.scientific_evidence, request: result.request, delta: result.delta, output_neurons: result.after?.outputs }, null, 2);
    await refresh();
  } catch (error) {
    panel.querySelector("#runtime-io-output").textContent = `Injektion abgelehnt: ${error.message}`;
    await refresh();
  }
}
export function initRuntimeIO() { ensurePanel(); refresh(); if (refreshTimer) clearInterval(refreshTimer); refreshTimer = setInterval(refresh, 3000); }
