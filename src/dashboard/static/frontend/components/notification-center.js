"use strict";
import { apiGet } from "../core/api.js";

let statusDetail = null;
let events = [];
let paused = false;

function escapeHtml(value) { const div = document.createElement("div"); div.textContent = String(value ?? ""); return div.innerHTML; }

function normalizedProblems() {
  const result = [];
  for (const failure of statusDetail?.failures || []) result.push({ kind: "error", label: "API", text: failure });
  for (const item of statusDetail?.integration?.items || []) {
    if (["failed", "stale"].includes(item?.status)) result.push({ kind: "warning", label: "Integration", text: `${item.name}: ${item.message || item.status}` });
  }
  for (const item of statusDetail?.gate?.criteria || statusDetail?.gate?.items || []) {
    if (["failed", "blocked", "stale"].includes(item?.status)) result.push({ kind: "warning", label: "Gate", text: `${item.label || item.id}: ${item.message || item.status}` });
  }
  for (const event of events) result.push({ kind: "error", label: "Runtime", text: event?.message || event?.error || JSON.stringify(event) });
  return result;
}

function renderTicker() {
  const ticker = document.getElementById("mhrn-ticker");
  if (!ticker) return;
  const problems = normalizedProblems();
  const count = document.getElementById("mhrn-notification-count");
  if (count) count.textContent = String(problems.length);

  if (!problems.length) {
    ticker.innerHTML = `<span class="mhrn-ticker-empty">Bereit · keine Ereignisse</span>`;
    return;
  }

  const items = problems.map((p) =>
    `<span class="mhrn-ticker-item" data-kind="${p.kind}"><b>${escapeHtml(p.label)}</b><span>${escapeHtml(p.text)}</span></span>`
  );
  // Duplicate items for seamless infinite scroll
  ticker.innerHTML = `<span class="mhrn-ticker-track">${items.join("")}${items.join("")}</span>`;
  if (paused) ticker.querySelector(".mhrn-ticker-track")?.style.setProperty("animation-play-state", "paused");
}

async function refreshErrors() {
  try { const payload = await apiGet("/api/errors?limit=50"); events = Array.isArray(payload.events) ? payload.events : []; } catch (_) { events = []; }
  renderTicker();
}

export function initNotificationCenter() {
  renderTicker();
  window.addEventListener("mhrn:global-status", (event) => { statusDetail = event.detail; renderTicker(); });
  document.addEventListener("click", (event) => {
    if (event.target.closest("#mhrn-notification-toggle")) {
      event.stopPropagation();
      paused = !paused;
      const track = document.querySelector(".mhrn-ticker-track");
      if (track) track.style.setProperty("animation-play-state", paused ? "paused" : "running");
      const btn = document.getElementById("mhrn-notification-toggle");
      if (btn) btn.style.opacity = paused ? "1" : "";
      if (paused) refreshErrors();
    }
  });
  refreshErrors();
  // Refresh errors every 15 seconds
  setInterval(refreshErrors, 15000);
}
