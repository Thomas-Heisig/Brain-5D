/* Technical Wesen identity profile view. Configuration identity is not consciousness. */

const PROFILE_POLL_MS = 3000;
let profileTimer = null;
let profilePayload = { profiles: [], active_profile_id: null };

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
    </div>`;
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
      ["Snapshot", profile.snapshot_binding ? "compatible reference" : "not bound"], ["Mutation", "LOCKED"],
    ].map(([key, value]) => `<div><span>${profileEscape(key)}</span><strong>${profileEscape(value)}</strong></div>`).join("");
    if (config) config.innerHTML = [
      ["Neural core", profile.neural_core?.neuron_model || "declared"], ["Senses", profile.senses?.items?.length || 0], ["Actuators", profile.actuators?.items?.length || 0],
      ["Morphology", profile.morphology?.type || "graph"], ["Gateway", profile.gateway?.productive_gateway_lock ? "Productive locked" : "invalid"], ["Memory", "declared / planned"],
    ].map(([key, value]) => `<div><span>${profileEscape(key)}</span><strong>${profileEscape(value)}</strong></div>`).join("");
    if (revision) revision.textContent = `rev ${profile.revision}`;
    const history = await profileRequest(`/api/profiles/${encodeURIComponent(profileId)}/history`);
    const historyNode = document.getElementById("wesen-profile-history");
    if (historyNode) historyNode.innerHTML = `<div class="wesen-profile-lineage"><strong>${profileEscape(profile.profile_id)}</strong>${profile.parent_profile_id ? `<span>← ${profileEscape(profile.parent_profile_id)}</span>` : ""}</div>${history.revisions.map((item) => `<div><span>rev ${item.revision}</span><small>${profileEscape(item.digest.slice(0, 16))}</small></div>`).join("")}`;
    document.getElementById("wesen-profile-save")?.setAttribute("data-profile-id", profileId);
    document.getElementById("wesen-profile-save-as")?.setAttribute("data-profile-id", profileId);
    ["wesen-profile-load", "wesen-profile-load-state", "wesen-profile-export", "wesen-profile-archive"].forEach((id) => document.getElementById(id)?.setAttribute("data-profile-id", profileId));
    setProfileMessage(`${profile.profile_id} ausgewählt · Änderungen überschreiben das Profil nicht automatisch.`);
  } catch (error) {
    setProfileMessage(`Profil nicht verfügbar: ${error.message || error}`);
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
}

function startProfiles() {
  profilePanel();
  refreshProfiles();
  if (profileTimer) clearInterval(profileTimer);
  profileTimer = setInterval(refreshProfiles, PROFILE_POLL_MS);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => requestAnimationFrame(startProfiles), { once: true });
else requestAnimationFrame(startProfiles);
