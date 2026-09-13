"use strict";
import { apiGet } from "../core/api.js";

let refreshTimer = null;

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function ensurePanel() {
  let panel = document.getElementById("mhrn-snapshot-history");
  if (panel) return panel;
  const snapshotPanel = document.querySelector('.overview-subpanel[data-subpanel="snapshot"]');
  if (!snapshotPanel) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-snapshot-history";
  panel.className = "mhrn-snapshot-history card";
  panel.innerHTML = `
    <header>
      <div>
        <span class="workspace-kicker">SNAPSHOT-ARCHIV</span>
        <h2>Snapshot-Historie</h2>
        <p>Gespeicherte Snapshots auswählen, laden und vergleichen.</p>
      </div>
      <span id="snapshot-history-count" class="maturity-state pending">lade …</span>
    </header>
    <div class="snapshot-history-toolbar">
      <button type="button" id="snapshot-history-refresh" class="btn-small">🔄 Aktualisieren</button>
      <span id="snapshot-history-status" class="snapshot-history-status">—</span>
    </div>
    <div id="snapshot-history-table-wrap" class="snapshot-history-table-wrap">
      <table class="snapshots-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tick</th>
            <th>Erstellt</th>
            <th>Größe</th>
            <th>Aktion</th>
          </tr>
        </thead>
        <tbody id="snapshot-history-body">
          <tr><td colspan="5">Lade Snapshots …</td></tr>
        </tbody>
      </table>
    </div>
    <div id="snapshot-history-detail" class="snapshot-history-detail" hidden>
      <h3>Snapshot-Details</h3>
      <div id="snapshot-history-detail-body"></div>
    </div>`;
  snapshotPanel.append(panel);
  panel.querySelector("#snapshot-history-refresh")?.addEventListener("click", () => refresh());
  return panel;
}

function renderSnapshots(data) {
  const el = document.getElementById("snapshot-history-body");
  const count = document.getElementById("snapshot-history-count");
  const status = document.getElementById("snapshot-history-status");
  if (!el) return;
  const snapshots = Array.isArray(data) ? data : (data?.snapshots || []);
  if (!snapshots.length) {
    el.innerHTML = '<tr><td colspan="5">Keine Snapshots vorhanden.</td></tr>';
    if (count) count.textContent = "0";
    if (status) status.textContent = "Keine Snapshots";
    return;
  }
  if (count) count.textContent = `${snapshots.length} Snapshot(s)`;
  if (status) status.textContent = `${snapshots.length} Einträge`;
  el.innerHTML = snapshots.map((s, index) => {
    const id = s.id || s.snapshot_id || `#${index + 1}`;
    const tick = s.tick ?? "—";
    const created = s.created_at || s.date || "—";
    const size = s.size || "—";
    return `<tr>
      <td><code>${escapeHtml(id)}</code></td>
      <td>${tick}</td>
      <td>${escapeHtml(created)}</td>
      <td>${escapeHtml(size)}</td>
      <td><button type="button" class="btn-small" data-snapshot-id="${escapeHtml(id)}" title="Snapshot ${escapeHtml(id)} auswählen">Auswählen</button></td>
    </tr>`;
  }).join("");
  // Click handler for selection
  el.querySelectorAll("[data-snapshot-id]").forEach((btn) => {
    btn.addEventListener("click", () => selectSnapshot(btn.dataset.snapshotId, snapshots));
  });
}

function selectSnapshot(id, allSnapshots) {
  const detail = document.getElementById("snapshot-history-detail");
  const body = document.getElementById("snapshot-history-detail-body");
  const status = document.getElementById("snapshot-history-status");
  if (!detail || !body) return;
  const snapshot = allSnapshots.find((s) => (s.id || s.snapshot_id) === id);
  if (!snapshot) {
    body.innerHTML = "<p>Snapshot nicht gefunden.</p>";
    detail.hidden = false;
    return;
  }
  if (status) status.textContent = `Ausgewählt: ${id}`;
  // Mark selected row
  document.querySelectorAll("#snapshot-history-body tr").forEach((row) => row.classList.remove("selected"));
  const btn = document.querySelector(`[data-snapshot-id="${CSS.escape(id)}"]`);
  if (btn) btn.closest("tr")?.classList.add("selected");
  // Show details
  body.innerHTML = `<dl class="snapshot-detail-grid">
    ${Object.entries(snapshot).filter(([, v]) => v !== null && v !== undefined).map(([k, v]) => {
      const val = typeof v === "object" ? JSON.stringify(v, null, 2) : String(v);
      return `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(val)}</dd>`;
    }).join("")}
  </dl>`;
  detail.hidden = false;
}

async function refresh() {
  const panel = ensurePanel();
  if (!panel) return;
  try {
    const data = await apiGet("/api/snapshots");
    renderSnapshots(data);
  } catch (error) {
    const el = document.getElementById("snapshot-history-body");
    if (el) el.innerHTML = `<tr><td colspan="5">Fehler: ${escapeHtml(error.message)}</td></tr>`;
  }
}

export function initSnapshotHistory() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 10000);
}
