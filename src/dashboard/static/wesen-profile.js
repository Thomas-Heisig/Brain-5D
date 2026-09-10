/* Technical Wesen identity profile view. Configuration identity is not consciousness. */
import { openFMFile } from "./file-viewer.js";

const PROFILE_POLL_MS = 3000;
let profileTimer = null;
let profilePayload = { profiles: [], active_profile_id: null };
let cognitionPayload = { available: false };

function profileEscape(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function profilePanel() {
  const workspace = document.getElementById("tab-wesen");
  if (!workspace) return null;
  let panel = document.getElementById("wesen-profile-identity");
  if (panel) return panel;
  panel = document.createElement("section");
  panel.id = "wesen-profile-identity";
  panel.className = "wesen-profile-panel";
  panel.innerHTML = `
    <header class="wesen-profile-header">
      <div><span class="workspace-kicker">TECHNICAL IDENTITY</span><h2>Profile & Identität</h2><p>Versionierte Konfiguration, Snapshot-Bindung und nachvollziehbare Lineage.</p></div>
      <div class="wesen-profile-health"><strong id="wesen-profile-health">NO PROFILE</strong><small id="wesen-profile-boundary">Technical identity only</small></div>
    </header>
    <div class="wesen-profile-boundary"><strong>Scientific boundary</strong><span>Ein Profil beschreibt eine persistente technische Systemidentität. Es ist kein Nachweis von Persönlichkeit, subjektiver Kontinuität oder Bewusstsein.</span></div>
    <div class="wesen-profile-toolbar">
      <input id="wesen-profile-name" type="text" placeholder="Neuer Profilname" aria-label="Neuer Profilname">
      <button type="button" id="wesen-profile-new">New</button>
      <button type="button" id="wesen-profile-save-current">Save Current</button>
      <button type="button" id="wesen-profile-load">Load</button>
      <button type="button" id="wesen-profile-load-state">Load + State</button>
      <button type="button" id="wesen-profile-bind-snapshot">Bind Current Snapshot</button>
      <button type="button" id="wesen-profile-save">Save Revision</button>
      <button type="button" id="wesen-profile-save-as">Save As</button>
      <button type="button" id="wesen-profile-export">Export</button>
      <button type="button" id="wesen-profile-archive">Archive</button>
      <button type="button" id="wesen-profile-import">Import</button>
      <input id="wesen-profile-import-file" type="file" accept=".zip,.mhrn-profile.zip" hidden>
      <span id="wesen-profile-message" role="status">Profile werden geladen …</span>
    </div>
    <div class="wesen-profile-grid">
      <article><header><strong>Current Identity</strong><span id="wesen-profile-current-id">—</span></header><div id="wesen-profile-current" class="wesen-profile-kv"></div></article>
      <article><header><strong>Profile Registry</strong><span id="wesen-profile-count">0</span></header><div id="wesen-profile-list" class="wesen-profile-list"></div></article>
      <article><header><strong>Configuration</strong><span>VERSIONED</span></header><div id="wesen-profile-config" class="wesen-profile-kv"></div></article>
      <article><header><strong>History / Lineage</strong><span id="wesen-profile-revision">—</span></header><div id="wesen-profile-history" class="wesen-profile-history"></div></article>
    </div>
    <section class="wesen-cognition-zone" aria-label="Cognition and memory">
      <header class="wesen-profile-header"><div><span class="workspace-kicker">COGNITION / MEMORY</span><h3>Bounded operational state</h3><p>Working memory, episodic records, prediction telemetry and operational disposition. This is an engineering view, not a claim about human-like memory or personality.</p></div><div class="wesen-profile-health"><strong id="wesen-cognition-status">UNAVAILABLE</strong><small id="wesen-cognition-run">Run —</small></div></header>
      <div class="wesen-profile-grid">
        <article><header><strong>Memory controls</strong><span id="wesen-memory-integrity">—</span></header><div class="wesen-profile-kv"><label><input id="wesen-memory-read" type="checkbox"> Memory Read</label><label><input id="wesen-memory-write" type="checkbox"> Memory Write</label><div><span>Episodes</span><strong id="wesen-memory-counts">—</strong></div><div><span>Retention</span><strong id="wesen-memory-retention">—</strong></div><div><span>Last write tick</span><strong id="wesen-memory-last-write">—</strong></div></div></article>
        <article><header><strong>Working / episodic memory</strong><span id="wesen-episode-count">0</span></header><div id="wesen-cognition-episodes" class="wesen-profile-history"></div></article>
        <article><header><strong>World prediction</strong><span id="wesen-prediction-count">0</span></header><div id="wesen-cognition-predictions" class="wesen-profile-history"></div></article>
        <article><header><strong>Behavior Profile</strong><span id="wesen-behavior-status">—</span></header><div id="wesen-cognition-behavior" class="wesen-profile-kv"></div></article>
      </div>
    </section>`;
  const board = document.getElementById("runtime-capability-board");
  if (board) board.insertAdjacentElement("afterend", panel); else workspace.appendChild(panel);
  bindProfileActions(panel);
  return panel;
}

function setProfileMessage(text) {
  const node = document.getElementById("wesen-profile-message");
  if (node) node.textContent = text;
}

async function profileRequest(path, options = {}) {
  const response = await fetch(path, { cache: "no-store", ...options });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.blob();
  if (!response.ok) throw new Error(payload?.error || `HTTP ${response.status}`);
  return payload;
}

function renderProfiles() {
  profilePanel();
  const list = document.getElementById("wesen-profile-list");
  const count = document.getElementById("wesen-profile-count");
  if (!list || !count) return;
  count.textContent = String(profilePayload.profiles.length);
  if (!profilePayload.profiles.length) {
    list.innerHTML = '<span class="wesen-profile-empty">Noch kein technisches Profil gespeichert.</span>';
    return;
  }
  list.innerHTML = profilePayload.profiles.map((profile) => `
    <button type="button" class="wesen-profile-card ${profile.profile_id === profilePayload.active_profile_id ? "active" : ""}" data-profile-id="${profileEscape(profile.profile_id)}">
      <strong>${profileEscape(profile.name)}</strong><small>${profileEscape(profile.profile_id)} · rev ${profileEscape(profile.version)} · ${profileEscape(profile.status)}</small>
    </button>`).join("");
  list.querySelectorAll("[data-profile-id]").forEach((button) => button.addEventListener("click", () => selectProfile(button.dataset.profileId)));
}

async function selectProfile(profileId) {
  try {
    const profile = await profileRequest(`/api/profiles/${encodeURIComponent(profileId)}`);
    const currentId = document.getElementById("wesen-profile-current-id");
    const current = document.getElementById("wesen-profile-current");
    const config = document.getElementById("wesen-profile-config");
    const revision = document.getElementById("wesen-profile-revision");
    if (currentId) currentId.textContent = profile.profile_id;
    if (current) current.innerHTML = [
      ["Name", profile.name], ["Status", profile.status], ["Revision", profile.revision], ["Digest", String(profile.provenance?.profile_digest || "").slice(0, 16)],
      ["Bound Snapshot", profile.snapshot_binding ? "compatible reference" : "not bound"], ["Snapshot Digest", String(profile.snapshot_binding?.digest || "").slice(0, 16) || "—"], ["Snapshot Tick", profile.snapshot_binding?.tick ?? "not embedded"], ["Compatibility", profile.snapshot_binding ? "BOUND" : "UNBOUND"], ["Mutation", "LOCKED"],
    ].map(([key, value]) => `<div><span>${profileEscape(key)}</span><strong>${profileEscape(value)}</strong></div>`).join("") + (profile.snapshot_binding?.path ? `<button type="button" data-open-snapshot="${profileEscape(profile.snapshot_binding.path)}">Open in File Viewer</button>` : "");
    if (config) config.innerHTML = [
      ["Neural core", profile.neural_core?.neuron_model || "declared"], ["Senses", profile.senses?.items?.length || 0], ["Actuators", profile.actuators?.items?.length || 0],
      ["Morphology", profile.morphology?.type || "graph"], ["Gateway", profile.gateway?.productive_gateway_lock ? "Productive locked" : "invalid"], ["Memory", cognitionPayload.memory ? `${cognitionPayload.memory.episode_count} episodes · ${cognitionPayload.memory.working_count} working` : "not available"], ["Behavior Profile", cognitionPayload.behavior_profile ? "implemented / experimental" : "not available"],
    ].map(([key, value]) => `<div><span>${profileEscape(key)}</span><strong>${profileEscape(value)}</strong></div>`).join("");
    if (revision) revision.textContent = `rev ${profile.revision}`;
    const history = await profileRequest(`/api/profiles/${encodeURIComponent(profileId)}/history`);
    const historyNode = document.getElementById("wesen-profile-history");
    if (historyNode) historyNode.innerHTML = `<div class="wesen-profile-lineage"><strong>${profileEscape(profile.profile_id)}</strong>${profile.parent_profile_id ? `<span>← ${profileEscape(profile.parent_profile_id)}</span>` : ""}</div>${history.revisions.map((item) => `<div><span>rev ${item.revision}</span><small>${profileEscape(item.digest.slice(0, 16))}</small></div>`).join("")}`;
    document.getElementById("wesen-profile-save")?.setAttribute("data-profile-id", profileId);
    document.getElementById("wesen-profile-save-as")?.setAttribute("data-profile-id", profileId);
    ["wesen-profile-load", "wesen-profile-load-state", "wesen-profile-bind-snapshot", "wesen-profile-export", "wesen-profile-archive"].forEach((id) => document.getElementById(id)?.setAttribute("data-profile-id", profileId));
    document.getElementById("wesen-profile-bind-snapshot")?.setAttribute("data-snapshot-path", profile.snapshot_binding?.path || "artifacts/latest.b5d");
    setProfileMessage(`${profile.profile_id} ausgewählt · Änderungen überschreiben das Profil nicht automatisch.`);
  } catch (error) {
    setProfileMessage(`Profil nicht verfügbar: ${error.message || error}`);
  }
}

function renderCognition() {
  const status = document.getElementById("wesen-cognition-status");
  const run = document.getElementById("wesen-cognition-run");
  const memory = cognitionPayload.memory;
  const controls = memory?.controls || {};
  const read = document.getElementById("wesen-memory-read");
  const write = document.getElementById("wesen-memory-write");
  if (status) status.textContent = cognitionPayload.available ? String(cognitionPayload.status || "OBSERVING").toUpperCase() : "UNAVAILABLE";
  if (run) run.textContent = `Run ${memory?.run_id || "—"}`;
  if (read) { read.checked = controls.read_enabled === true; read.disabled = !memory; }
  if (write) { write.checked = controls.write_enabled === true; write.disabled = !memory; }
  const integrity = document.getElementById("wesen-memory-integrity");
  if (integrity) integrity.textContent = memory?.integrity_digest ? `SHA-256 ${String(memory.integrity_digest).slice(0, 12)}` : "—";
  const counts = document.getElementById("wesen-memory-counts");
  if (counts) counts.textContent = memory ? `${memory.episode_count} / ${memory.episode_capacity} · ${memory.working_count} / ${memory.working_capacity}` : "—";
  const retention = document.getElementById("wesen-memory-retention");
  if (retention) retention.textContent = memory ? `${memory.retention_ticks} ticks` : "—";
  const lastWrite = document.getElementById("wesen-memory-last-write");
  if (lastWrite) lastWrite.textContent = memory?.last_write_tick ?? "—";
  const episodes = document.getElementById("wesen-cognition-episodes");
  const episodeItems = Array.isArray(cognitionPayload.episodes) ? cognitionPayload.episodes : [];
  if (episodes) episodes.innerHTML = episodeItems.length ? episodeItems.slice(0, 6).map((item) => `<div><span>tick ${profileEscape(item.tick)}</span><small>${profileEscape(item.observation?.modality || "observation")} · ${profileEscape(item.episode_id || "episode")}</small></div>`).join("") : "<span>Keine lesbaren Episoden.</span>";
  const predictions = document.getElementById("wesen-cognition-predictions");
  const predictionItems = Array.isArray(cognitionPayload.predictions) ? cognitionPayload.predictions : [];
  if (predictions) predictions.innerHTML = predictionItems.length ? predictionItems.slice(-6).reverse().map((item) => `<div><span>tick ${profileEscape(item.tick)} → ${profileEscape(item.target_tick)}</span><small>Error ${profileEscape(item.error ?? "—")} · uncertainty ${profileEscape(item.uncertainty ?? "—")}</small></div>`).join("") : "<span>Keine Prediction Records.</span>";
  const behavior = document.getElementById("wesen-cognition-behavior");
  const behaviorState = cognitionPayload.behavior_profile;
  const disposition = behaviorState?.disposition || {};
  const lastUpdate = Array.isArray(behaviorState?.update_log) && behaviorState.update_log.length ? behaviorState.update_log[behaviorState.update_log.length - 1] : null;
  const behaviorStatus = document.getElementById("wesen-behavior-status");
  if (behaviorStatus) behaviorStatus.textContent = behaviorState ? "IMPLEMENTED / EXPERIMENTAL" : "NOT AVAILABLE";
  if (behavior) behavior.innerHTML = behaviorState ? Object.entries(disposition).map(([key, value]) => `<div><span>${profileEscape(key)}</span><strong>${Number(value).toFixed(3)}</strong></div>`).join("") + `<div><span>Last update</span><strong>${profileEscape(lastUpdate?.tick ?? "—")}</strong></div>` : "<span>Kein operatives Profil verbunden.</span>";
}

async function refreshCognition() {
  try {
    const [status, episodes, predictions, behavior] = await Promise.all([
      profileRequest("/api/cognition/status"),
      profileRequest("/api/cognition/memory/episodes?limit=8"),
      profileRequest("/api/cognition/predictions?limit=8"),
      profileRequest("/api/cognition/behavior-profile"),
    ]);
    cognitionPayload = { ...status, episodes: episodes.episodes || [], predictions: predictions.predictions || [], behavior_profile: behavior.profile || null };
    renderCognition();
  } catch (error) {
    cognitionPayload = { available: false };
    renderCognition();
    setProfileMessage(`Cognition nicht verfügbar: ${error.message || error}`);
  }
}

async function setMemoryControl(name, value) {
  const controls = cognitionPayload.memory?.controls || {};
  try {
    await profileRequest("/api/cognition/memory/controls", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ read_enabled: name === "read_enabled" ? value : controls.read_enabled === true, write_enabled: name === "write_enabled" ? value : controls.write_enabled === true }) });
    await refreshCognition();
    setProfileMessage(`Memory ${name === "read_enabled" ? "Read" : "Write"} bestätigt.`);
  } catch (error) {
    await refreshCognition();
    setProfileMessage(`Memory-Control abgewiesen: ${error.message || error}`);
  }
}

async function refreshProfiles() {
  try {
    profilePayload = await profileRequest("/api/profiles");
    renderProfiles();
    const health = document.getElementById("wesen-profile-health");
    if (health) health.textContent = profilePayload.active_profile_id ? "HEALTHY" : "NO PROFILE";
    if (profilePayload.active_profile_id) await selectProfile(profilePayload.active_profile_id);
  } catch (error) {
    profilePanel();
    setProfileMessage(`Profile Registry nicht verfügbar: ${error.message || error}`);
  }
}

async function createProfile(name) {
  const profile = await profileRequest("/api/profiles", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
  setProfileMessage(`${profile.profile.profile_id} erstellt.`);
  await refreshProfiles();
  await selectProfile(profile.profile.profile_id);
}

async function saveCurrentProfile(name) {
  const profile = await profileRequest("/api/profiles", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, source: "current_runtime" }) });
  setProfileMessage(`${profile.profile.profile_id} aus der aktuellen Runtime gespeichert.`);
  await refreshProfiles();
  await selectProfile(profile.profile.profile_id);
}

async function activateProfile(profileId, withState = false) {
  await profileRequest(`/api/profiles/${encodeURIComponent(profileId)}/load`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ with_state: withState }) });
  setProfileMessage(`${profileId} geladen (${withState ? "Profile + State" : "Profile only"}).`);
  await refreshProfiles();
}

async function exportProfile(profileId) {
  const response = await fetch(`/api/profiles/${encodeURIComponent(profileId)}/export`, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const blob = await response.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${profileId}.mhrn-profile.zip`;
  link.click();
  URL.revokeObjectURL(link.href);
}

async function bindCurrentSnapshot(profileId, existingPath) {
  if (existingPath && !window.confirm("Snapshot-Bindung ersetzen?")) return;
  const result = await profileRequest(`/api/profiles/${encodeURIComponent(profileId)}/save-state`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ snapshot_path: "artifacts/latest.b5d" }) });
  setProfileMessage(`${profileId}: Snapshot gebunden (${String(result.profile.snapshot_binding?.digest || "").slice(0, 16)}).`);
  await refreshProfiles();
  await selectProfile(profileId);
}

function bindProfileActions(panel) {
  panel.querySelector("#wesen-profile-new")?.addEventListener("click", async () => {
    try { await createProfile((document.getElementById("wesen-profile-name")?.value || "MHRN Wesen").trim()); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-save-current")?.addEventListener("click", async () => {
    try { await saveCurrentProfile((document.getElementById("wesen-profile-name")?.value || "MHRN Wesen Current").trim()); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-load")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await activateProfile(id); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-load-state")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await activateProfile(id, true); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-bind-snapshot")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await bindCurrentSnapshot(id, event.currentTarget.dataset.snapshotPath); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-current")?.addEventListener("click", (event) => {
    if (!event.target.closest("[data-open-snapshot]")) return;
    const path = event.target.closest("[data-open-snapshot]").dataset.openSnapshot;
    if (path) openFMFile(path);
  });
  panel.querySelector("#wesen-profile-save")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await profileRequest(`/api/profiles/${encodeURIComponent(id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason: "dashboard_save_revision" }) }); setProfileMessage(`${id}: Revision gespeichert.`); await refreshProfiles(); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-save-as")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { const result = await profileRequest(`/api/profiles/${encodeURIComponent(id)}/clone`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: `${id} clone` }) }); setProfileMessage(`${result.profile_id} als Clone gespeichert.`); await refreshProfiles(); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-export")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await exportProfile(id); setProfileMessage(`${id} exportiert.`); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-archive")?.addEventListener("click", async (event) => {
    const id = event.currentTarget.dataset.profileId;
    if (!id) return;
    try { await profileRequest(`/api/profiles/${encodeURIComponent(id)}/archive`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }); setProfileMessage(`${id} archiviert.`); await refreshProfiles(); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-profile-import")?.addEventListener("click", () => panel.querySelector("#wesen-profile-import-file")?.click());
  panel.querySelector("#wesen-profile-import-file")?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try { const buffer = await file.arrayBuffer(); const bytes = new Uint8Array(buffer); let binary = ""; bytes.forEach((value) => { binary += String.fromCharCode(value); }); const result = await profileRequest("/api/profiles/import", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ archive_base64: btoa(binary) }) }); setProfileMessage(`${result.profile.profile_id} importiert.`); await refreshProfiles(); } catch (error) { setProfileMessage(error.message || error); }
  });
  panel.querySelector("#wesen-memory-read")?.addEventListener("change", (event) => setMemoryControl("read_enabled", event.currentTarget.checked));
  panel.querySelector("#wesen-memory-write")?.addEventListener("change", (event) => setMemoryControl("write_enabled", event.currentTarget.checked));
}

function startProfiles() {
  profilePanel();
  refreshProfiles();
  refreshCognition();
  if (profileTimer) clearInterval(profileTimer);
  profileTimer = setInterval(() => { refreshProfiles(); refreshCognition(); }, PROFILE_POLL_MS);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => requestAnimationFrame(startProfiles), { once: true });
else requestAnimationFrame(startProfiles);
