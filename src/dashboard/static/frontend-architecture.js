/* MHRN three-area frontend architecture.
 *
 * Primary navigation is deliberately limited to:
 *   1. Dashboard
 *   2. Wissenschaft
 *   3. Runtime & Wesen
 *
 * Existing workspaces remain intact and are routed as contextual tools so no
 * operator or research capability is lost. Maturity labels are explicit:
 * planned capabilities are never rendered as if they were already live.
 */
"use strict";

const AREA_BY_WORKSPACE = {
  overview: "dashboard",
  control: "dashboard",
  network: "science",
  research: "science",
  settings: "science",
  embodiment: "wesen",
  wesen: "wesen",
};

function byId(id) { return document.getElementById(id); }
function legacyButton(name) { return document.querySelector(`.tab-nav .tab-btn[data-tab="${name}"]`); }

function injectStyles() {
  if (byId("brain5d-three-area-styles")) return;
  const style = document.createElement("style");
  style.id = "brain5d-three-area-styles";
  style.textContent = `
    .tab-nav { display:none !important; }
    .brain5d-primary-nav { position:sticky; top:0; z-index:30; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.55rem; padding:.7rem clamp(.8rem,2vw,1.6rem); border-bottom:1px solid var(--line,rgba(127,127,127,.2)); background:color-mix(in srgb,var(--bg,#08131c) 92%,transparent); backdrop-filter:blur(14px); }
    .brain5d-primary-nav button { min-height:48px; display:flex; align-items:center; justify-content:center; gap:.55rem; border:1px solid var(--line,rgba(127,127,127,.22)); border-radius:11px; background:rgba(127,127,127,.035); color:inherit; cursor:pointer; font:600 .82rem/1.2 inherit; letter-spacing:.025em; }
    .brain5d-primary-nav button span { opacity:.6; font-size:.68rem; text-transform:uppercase; }
    .brain5d-primary-nav button.active { border-color:color-mix(in srgb,currentColor 38%,transparent); background:rgba(127,127,127,.12); box-shadow:inset 0 -2px 0 currentColor; }
    .science-context-nav { display:flex; flex-wrap:wrap; gap:.45rem; margin:.7rem 0 1rem; padding:.55rem; border:1px solid var(--line,rgba(127,127,127,.2)); border-radius:11px; background:rgba(127,127,127,.035); }
    .science-context-nav button { border:1px solid transparent; border-radius:8px; background:transparent; color:inherit; padding:.55rem .75rem; cursor:pointer; font:inherit; opacity:.72; }
    .science-context-nav button.active { opacity:1; border-color:var(--line,rgba(127,127,127,.25)); background:rgba(127,127,127,.1); }
    .architecture-maturity-panel { margin:1rem 0 1.25rem; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.7rem; }
    .architecture-capability { padding:.85rem .9rem; border:1px solid var(--line,rgba(127,127,127,.2)); border-radius:11px; background:rgba(127,127,127,.035); }
    .architecture-capability header { display:flex; align-items:flex-start; justify-content:space-between; gap:.6rem; }
    .architecture-capability h3 { margin:0; font-size:.9rem; }
    .architecture-capability p { margin:.45rem 0 0; opacity:.68; font-size:.78rem; line-height:1.45; }
    .embedding-analysis-capability { grid-column:1/-1; }
    .embedding-analysis-form { display:flex; flex-wrap:wrap; gap:.5rem; align-items:end; margin-top:.7rem; }
    .embedding-analysis-form label { display:grid; gap:.22rem; color:var(--muted,#9ca3af); font-size:.68rem; }
    .embedding-analysis-form input,.embedding-analysis-form select { min-width:7rem; padding:.42rem .5rem; border:1px solid var(--line,rgba(127,127,127,.25)); border-radius:6px; background:rgba(0,0,0,.16); color:inherit; font:inherit; }
    .embedding-analysis-form button { padding:.48rem .7rem; border:1px solid var(--line,rgba(127,127,127,.25)); border-radius:7px; background:rgba(127,127,127,.1); color:inherit; cursor:pointer; font:600 .72rem/1.2 inherit; }
    .embedding-analysis-status { margin:.6rem 0 0; font-size:.72rem; color:var(--muted,#9ca3af); white-space:pre-wrap; }
    .embedding-analysis-status[data-state="completed"] { color:#51d6ad; }
    .embedding-analysis-status[data-state="error"] { color:#ef8b8b; }
    .maturity-state { flex:0 0 auto; display:inline-flex; padding:.22rem .45rem; border:1px solid currentColor; border-radius:999px; font-size:.62rem; letter-spacing:.05em; text-transform:uppercase; }
    .maturity-state.implemented { color:#51d6ad; }
    .maturity-state.pending { color:#efb45e; }
    .runtime-capability-board { margin:1rem 0 1.3rem; }
    .runtime-capability-board > header { display:flex; justify-content:space-between; gap:1rem; align-items:flex-end; margin-bottom:.7rem; }
    .runtime-capability-board > header h2 { margin:.1rem 0 0; font-size:1.05rem; }
    .runtime-capability-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; }
    .runtime-capability-card { border:1px solid var(--line,rgba(127,127,127,.2)); border-radius:11px; padding:.85rem .9rem; background:rgba(127,127,127,.035); }
    .runtime-capability-card header { display:flex; justify-content:space-between; gap:.7rem; align-items:flex-start; }
    .runtime-capability-card h3 { margin:0; font-size:.9rem; }
    .runtime-capability-card ul { margin:.65rem 0 0; padding-left:1.1rem; font-size:.76rem; line-height:1.55; opacity:.8; }
    .runtime-capability-card li + li { margin-top:.2rem; }
    .not-implemented-yet { color:#efb45e; font-weight:650; }
    .architecture-route-note { margin:.55rem 0 0; font-size:.72rem; opacity:.65; }
    @media(max-width:900px){.architecture-maturity-panel,.runtime-capability-grid{grid-template-columns:1fr}.brain5d-primary-nav button{flex-direction:column;gap:.15rem}}
    @media(max-width:620px){.brain5d-primary-nav{grid-template-columns:1fr 1fr 1fr;padding:.5rem}.brain5d-primary-nav button{min-height:54px;font-size:.7rem}.brain5d-primary-nav button span{display:none}}
  `;
  document.head.appendChild(style);
}

function activateWorkspace(name) {
  const button = legacyButton(name);
  if (button) {
    button.click();
    queueMicrotask(syncNavigation);
    return true;
  }
  return false;
}

function ensurePrimaryNavigation() {
  if (document.querySelector(".brain5d-primary-nav")) return;
  const topbar = document.querySelector(".topbar");
  if (!topbar) return;
  const nav = document.createElement("nav");
  nav.className = "brain5d-primary-nav";
  nav.setAttribute("aria-label", "MHRN Hauptbereiche");
  nav.innerHTML = `
    <button type="button" class="active" data-primary-area="dashboard"><strong>📊 Dashboard</strong><span>Operator</span></button>
    <button type="button" data-primary-area="science"><strong>🔬 Wissenschaft</strong><span>Research & Analysis</span></button>
    <button type="button" data-primary-area="wesen"><strong>🧠 Runtime & Wesen</strong><span>Living System</span></button>`;
  topbar.insertAdjacentElement("afterend", nav);
  const mhrnStickyInsets = () => {
    const headerHeight = Math.ceil(topbar.getBoundingClientRect().height);
    const navHeight = Math.ceil(nav.getBoundingClientRect().height);
    document.documentElement.style.setProperty('--dashboard-topbar-height', `${headerHeight}px`);
    document.documentElement.style.setProperty('--mhrn-sticky-offset', `${headerHeight + navHeight + 12}px`);
  };
  mhrnStickyInsets();
  if (typeof ResizeObserver === 'function') {
    const observer = new ResizeObserver(mhrnStickyInsets);
    observer.observe(topbar);
    observer.observe(nav);
  } else {
    window.addEventListener('resize', mhrnStickyInsets);
  }

  nav.addEventListener("click", (event) => {
    const button = event.target.closest("[data-primary-area]");
    if (!button) return;
    const area = button.dataset.primaryArea;
    if (area === "dashboard") activateWorkspace("overview");
    if (area === "science") activateWorkspace("research");
    if (area === "wesen") {
      if (!activateWorkspace("wesen")) {
        window.Brain5DWesenIntegration?.refresh?.();
        setTimeout(() => activateWorkspace("wesen"), 0);
      }
    }
  });
}

function scienceNavigationMarkup(active) {
  return `
    <button type="button" data-science-route="network" class="${active === "network" ? "active" : ""}">Neuronales Netzwerk</button>
    <button type="button" data-science-route="research" class="${active === "research" ? "active" : ""}">Experimente & Nachweise</button>
    <button type="button" data-science-route="settings" class="${active === "settings" ? "active" : ""}">Parameter</button>`;
}

function ensureScienceNavigation() {
  for (const name of ["network", "research", "settings"]) {
    const workspace = byId(`tab-${name}`);
    if (!workspace || workspace.querySelector(":scope > .science-context-nav")) continue;
    const nav = document.createElement("nav");
    nav.className = "science-context-nav";
    nav.setAttribute("aria-label", "Wissenschaftliche Arbeitsbereiche");
    nav.innerHTML = scienceNavigationMarkup(name);
    const header = workspace.querySelector(":scope > .workspace-header");
    if (header) header.insertAdjacentElement("afterend", nav); else workspace.prepend(nav);
    nav.addEventListener("click", (event) => {
      const button = event.target.closest("[data-science-route]");
      if (button) activateWorkspace(button.dataset.scienceRoute);
    });
  }
}

function ensureScienceMaturityPanel() {
  const research = byId("tab-research");
  if (!research || byId("science-maturity-panel")) return;
  const panel = document.createElement("section");
  panel.id = "science-maturity-panel";
  panel.className = "architecture-maturity-panel";
  panel.setAttribute("aria-label", "Scientific capability maturity");
  panel.innerHTML = `
    <article class="architecture-capability"><header><h3>Netzwerk-Workbench</h3><span class="maturity-state implemented">implemented</span></header><p>Live-Dynamik, Topologie, Raster/Histogramm und der neue PCA-basierte Neuron Model Viewer verwenden reale Runtime-Daten.</p></article>
    <article class="architecture-capability"><header><h3>Experiment-Workflow</h3><span class="maturity-state implemented">implemented</span></header><p>Registrierte Forschungsfragen, kontrollierte Runner, DATA/EVID-Trennung und reproduzierbare Nachweise bleiben erhalten.</p></article>
    <article class="architecture-capability embedding-analysis-capability"><header><h3>t-SNE / UMAP / Clusterexport</h3><span class="maturity-state implemented">backend job</span></header><p>Reproduzierbare Live-Netzwerkanalyse mit gebundenen Parametern, Bibliotheksversionen, Input-Digest und Source-Provenienz. Ergebnisdaten sind technische Analyse, keine automatische Evidenz.</p><form class="embedding-analysis-form" id="embedding-analysis-form"><label>Methode<select id="embedding-analysis-method"><option value="tsne">t-SNE</option><option value="umap">UMAP</option><option value="cluster_export">Clusterexport</option></select></label><label>Seed<input id="embedding-analysis-seed" type="number" min="0" value="42"></label><label>Punkte<input id="embedding-analysis-points" type="number" min="2" max="2000" value="500"></label><label>Cluster<input id="embedding-analysis-clusters" type="number" min="2" max="64" value="5"></label><button type="submit">Analyse starten</button></form><div id="embedding-analysis-status" class="embedding-analysis-status" data-state="idle">Bereit für einen Live-Netzwerkjob.</div><div id="embedding-analysis-history" class="embedding-analysis-history"></div></article>`;
  const anchor = research.querySelector(":scope > .research-lanes") || research.querySelector(":scope > .workspace-header");
  anchor?.insertAdjacentElement("afterend", panel);
  const form = panel.querySelector("#embedding-analysis-form");
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = panel.querySelector("#embedding-analysis-status");
    const method = panel.querySelector("#embedding-analysis-method")?.value || "tsne";
    const body = {
      method,
      random_state: Number(panel.querySelector("#embedding-analysis-seed")?.value || 42),
      max_points: Number(panel.querySelector("#embedding-analysis-points")?.value || 500),
      n_clusters: Number(panel.querySelector("#embedding-analysis-clusters")?.value || 5),
    };
    if (status) { status.dataset.state = "running"; status.textContent = "Analyse läuft …"; }
    try {
      const response = await fetch("/api/research/analysis-jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      const job = payload.job || {};
      if (status) { status.dataset.state = "completed"; status.textContent = `${job.method} abgeschlossen: ${job.input?.neuron_count || 0} Punkte. JSON: ${job.artifacts?.json || "—"} · CSV: ${job.artifacts?.csv || "—"}\nSource-Digest: ${job.provenance?.source_tree_digest || "—"}`; }
      await loadEmbeddingHistory(panel);
    } catch (error) {
      if (status) { status.dataset.state = "error"; status.textContent = `Analyse fehlgeschlagen: ${error.message || error}`; }
    }
  });
  loadEmbeddingHistory(panel);
}

async function loadEmbeddingHistory(panel) {
  const history = panel.querySelector("#embedding-analysis-history");
  if (!history) return;
  try {
    const response = await fetch("/api/research/analysis-jobs", { headers: { "Cache-Control": "no-store" } });
    const payload = await response.json();
    const jobs = Array.isArray(payload.jobs) ? payload.jobs.slice(0, 5) : [];
    history.innerHTML = jobs.length ? `<small>Letzte Jobs: ${jobs.map((job) => `${job.method} · ${job.created_at || ""} · ${job.status}`).join(" | ")}</small>` : "";
  } catch (_) {
    history.textContent = "Jobhistorie nicht verfügbar.";
  }
}

function ensureRuntimeCapabilityBoard() {
  const workspace = byId("tab-wesen");
  if (!workspace || byId("runtime-capability-board")) return;
  const board = document.createElement("section");
  board.id = "runtime-capability-board";
  board.className = "runtime-capability-board";
  board.innerHTML = `
    <header><div><span class="workspace-kicker">RUNTIME CAPABILITIES</span><h2>Sinne, Gateway, Profile & Persönlichkeit</h2><p class="architecture-route-note">Reifegrad folgt dem kanonischen TODO/ROADMAP-Stand; geplante Funktionen bleiben sichtbar, aber nicht bedienbar.</p></div></header>
    <div class="runtime-capability-grid">
      <article class="runtime-capability-card"><header><h3>Sinne & Peripherie</h3><span class="maturity-state implemented">read-only implemented</span></header><ul><li>Dynamische Connection-Inventur und Körpermorphologie: implementiert.</li><li>Host-Interozeption und technische Körpergrenze: implementiert.</li><li><span class="not-implemented-yet">Einzelne Sinne aktivieren/deaktivieren: Not implemented yet.</span></li><li>Keine erfundene Kamera-/Audio-/Geräteverbindung bei fehlendem Adapter.</li></ul></article>
      <article class="runtime-capability-card"><header><h3>Neural Symbiosis / Gateway</h3><span class="maturity-state pending">Not implemented yet</span></header><ul><li>Verträge und MSBA-Forschungsprogramm: vorhanden.</li><li><span class="not-implemented-yet">Produktive Gateway-Aktivierung und Gateway-Plastizität: Not implemented yet.</span></li><li>Gemäß Roadmap zunächst nur experiment-only mit Frozen/Random/Shuffle-Kontrollen.</li></ul></article>
      <article class="runtime-capability-card"><header><h3>Profile & Identität</h3><span class="maturity-state pending">partial</span></header><ul><li>Snapshot/Persistenz des kanonischen SNN-Zustands: implementiert.</li><li><span class="not-implemented-yet">Ganzheitliches Wesen-Profil mit Sinnen, Lernparametern, Morphologie und Aktoren: Not implemented yet.</span></li><li><span class="not-implemented-yet">Profil laden/speichern/exportieren/löschen: Not implemented yet.</span></li></ul></article>
      <article class="runtime-capability-card"><header><h3>Persönlichkeit / Weltmodell</h3><span class="maturity-state pending">Not implemented yet</span></header><ul><li><span class="not-implemented-yet">Persönlichkeitsprofile: Not implemented yet.</span></li><li><span class="not-implemented-yet">Memory-/World-Model-Layer: Not implemented yet.</span></li><li>Eine spätere Implementierung benötigt explizite Zustandsverträge und Memory-on/off-Kontrollen.</li></ul></article>
    </div>`;
  const header = workspace.querySelector(":scope > header");
  if (header) header.insertAdjacentElement("afterend", board); else workspace.prepend(board);
}

function syncNavigation() {
  const current = document.body.dataset.currentTab || "overview";
  const area = AREA_BY_WORKSPACE[current] || document.body.dataset.primaryArea || "dashboard";
  document.body.dataset.primaryArea = area;
  document.querySelectorAll(".brain5d-primary-nav [data-primary-area]").forEach((button) => {
    button.classList.toggle("active", button.dataset.primaryArea === area);
  });
  document.querySelectorAll(".science-context-nav [data-science-route]").forEach((button) => {
    button.classList.toggle("active", button.dataset.scienceRoute === current);
  });
  const context = byId("header-context");
  if (context && current !== "gate") {
    context.textContent = area === "dashboard" ? "Dashboard" : area === "science" ? "Wissenschaft" : "Runtime & Wesen";
  }
}

function observeWorkspaceChanges() {
  const observer = new MutationObserver((mutations) => {
    if (mutations.some((mutation) => mutation.type === "attributes" && mutation.attributeName === "data-current-tab")) syncNavigation();
    ensureScienceNavigation();
    ensureScienceMaturityPanel();
    ensureRuntimeCapabilityBoard();
  });
  observer.observe(document.body, { attributes:true, childList:true, subtree:true, attributeFilter:["data-current-tab"] });
}

function syncFixedChrome() {
  const topbar = document.querySelector(".topbar");
  const primaryNav = document.querySelector(".brain5d-primary-nav");
  if (!topbar || !primaryNav) return;
  const headerHeight = Math.ceil(topbar.getBoundingClientRect().height);
  const navHeight = Math.ceil(primaryNav.getBoundingClientRect().height);
  document.body.style.setProperty("--dashboard-header-height", `${headerHeight}px`);
  document.body.style.setProperty("--dashboard-primary-nav-height", `${navHeight}px`);
}

function init() {
  injectStyles();
  ensurePrimaryNavigation();
  ensureScienceNavigation();
  ensureScienceMaturityPanel();
  ensureRuntimeCapabilityBoard();
  observeWorkspaceChanges();
  syncNavigation();
  const refreshChrome = () => requestAnimationFrame(syncFixedChrome);
  refreshChrome();
  window.addEventListener("resize", refreshChrome, { passive: true });
  if (typeof ResizeObserver !== "undefined") {
    const observer = new ResizeObserver(refreshChrome);
    const topbar = document.querySelector(".topbar");
    const primaryNav = document.querySelector(".brain5d-primary-nav");
    if (topbar) observer.observe(topbar);
    if (primaryNav) observer.observe(primaryNav);
  }
  setTimeout(() => { ensureRuntimeCapabilityBoard(); syncNavigation(); refreshChrome(); }, 0);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once:true }); else init();

window.Brain5DFrontendArchitecture = { activateWorkspace, refresh:init };
