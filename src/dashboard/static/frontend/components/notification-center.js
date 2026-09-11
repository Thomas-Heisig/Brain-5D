"use strict";
import { apiGet } from "../core/api.js";

let statusDetail = null;
let events = [];
function ensureCenter() {
  let center = document.getElementById("mhrn-notification-center");
  if (center) return center;
  center = document.createElement("aside");
  center.id = "mhrn-notification-center";
  center.className = "mhrn-notification-center";
  center.hidden = true;
  center.innerHTML = `<header><strong>Systemmeldungen</strong><button type="button" data-notification-close>×</button></header><div id="mhrn-notification-list"></div>`;
  document.body.appendChild(center);
  center.addEventListener("click", (event) => { if (event.target.closest("[data-notification-close]")) center.hidden = true; });
  return center;
}
function normalizedProblems() {
  const result = [];
  for (const failure of statusDetail?.failures || []) result.push({ kind: "API", text: failure });
  for (const item of statusDetail?.integration?.items || []) {
    if (["failed", "stale"].includes(item?.status)) result.push({ kind: "Integration", text: `${item.name}: ${item.message || item.status}` });
  }
  for (const item of statusDetail?.gate?.criteria || statusDetail?.gate?.items || []) {
    if (["failed", "blocked", "stale"].includes(item?.status)) result.push({ kind: "Gate", text: `${item.label || item.id}: ${item.message || item.status}` });
  }
  for (const event of events) result.push({ kind: "Runtime", text: event?.message || event?.error || JSON.stringify(event) });
  return result;
}
function render() {
  const center = ensureCenter();
  const list = center.querySelector("#mhrn-notification-list");
  const problems = normalizedProblems();
  list.innerHTML = problems.length ? problems.slice(0, 50).map((problem) => `<article><small>${problem.kind}</small><p>${escapeHtml(problem.text)}</p></article>`).join("") : `<p class="notification-empty">Keine aktuell gemeldeten Fehler. Unknown/Pending werden nicht als Erfolg umgedeutet.</p>`;
  const count = document.getElementById("mhrn-notification-count");
  if (count) count.textContent = String(problems.length);
}
function escapeHtml(value) { const div = document.createElement("div"); div.textContent = String(value ?? ""); return div.innerHTML; }
async function refreshErrors() {
  try { const payload = await apiGet("/api/errors?limit=50"); events = Array.isArray(payload.events) ? payload.events : []; } catch (_) { events = []; }
  render();
}
export function initNotificationCenter() {
  ensureCenter();
  window.addEventListener("mhrn:global-status", (event) => { statusDetail = event.detail; render(); });
  document.addEventListener("click", (event) => {
    if (event.target.closest("#mhrn-notification-toggle")) { const center = ensureCenter(); center.hidden = !center.hidden; if (!center.hidden) refreshErrors(); }
  });
  refreshErrors();
}
