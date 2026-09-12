"use strict";

const STORAGE_KEY = "mhrn-workspace-router-v1";
const ROUTED_CLASS = "mhrn-routed-local-tabs";

const AREAS = Object.freeze({
  dashboard: {
    number: "01", label: "Dashboard", subtitle: "System & Betrieb", owner: "overview",
    purpose: "Kompakte Betriebsübersicht ohne doppelte Detailansichten.",
    howto: ["Health und Integration prüfen.", "Passenden Untertab wählen.", "Für Detailanalysen in Wissenschaft, Runtime oder Control wechseln."],
    contracts: ["/api/status", "/api/integration/status", "/api/snapshot-info"],
    routes: [
      ["overview", "Übersicht", "overview"], ["vitals", "Vitals", "overview", "overview", "vitals"],
      ["organs", "Organe", "overview", "overview", "organs"], ["memory", "Gedächtnis", "overview", "overview", "memory"],
      ["structure", "Struktur", "overview", "overview", "structure"], ["snapshot", "Snapshot", "overview", "overview", "snapshot"],
      ["sysinfo", "System Info", "overview", "overview", "sysinfo"],
    ],
  },
  science: {
    number: "02", label: "Wissenschaft", subtitle: "Evidenz & Analyse", owner: "research",
    purpose: "Messung, Experiment, Analyse, Registry und Dateien mit expliziter Evidenzgrenze.",
    howto: ["Observatory für Messwerte und UNKNOWN-Zustände nutzen.", "Kausale Aussagen nur aus registrierten kontrollierten Läufen ableiten.", "Dateien immer im zentralen File Viewer öffnen."],
    contracts: ["/api/science/metrics", "/api/research", "/api/research/analysis-jobs"],
    routes: [
      ["overview", "Übersicht", "research"], ["observatory", "Observatory", "research", "focus", "#mhrn-scientific-metrics"],
      ["experiments", "Experimente", "research", "research", "experiments"], ["network", "Netzwerk", "network", "view", "visual"],
      ["dynamics", "Dynamik", "network", "view", "dynamics"], ["inspect", "Inspektor", "network", "view", "inspect"],
      ["data", "Daten", "network", "view", "data"], ["files", "Dateien", "research", "research", "files"],
      ["registry", "Registry", "research", "research", "registry"],
    ],
  },
  wesen: {
    number: "03", label: "Runtime & Wesen", subtitle: "Körper & Verhalten", owner: "embodiment",
    purpose: "Runtime, Körpergrenze, Sensorik, Aktorik, Kognition und technische Identität in einer Arbeitsfläche.",
    howto: ["Körpergrenze und Verbindungen prüfen.", "Pipeline und Clock nur über autorisierte Verträge steuern.", "Kognition, Profil und Symbiosis als technische Zustände interpretieren."],
    contracts: ["/api/embodiment/state", "/api/cognition/state", "/api/embodiment/gateways"],
    routes: [
      ["overview", "Übersicht", "embodiment"], ["live", "Wesen Live", "wesen"], ["anatomy", "Anatomie", "embodiment", "embodiment", "anatomy"],
      ["connections", "Verbindungen", "embodiment", "embodiment", "connections"], ["pipeline", "Pipeline", "embodiment", "embodiment", "pipeline"],
      ["clock", "Runtime-Clock", "embodiment", "embodiment", "clock"], ["self", "Selbstbild", "embodiment", "embodiment", "self"],
      ["cognition", "Kognition", "wesen", "focus", "#mhrn-cognition"], ["profile", "Profil", "wesen", "focus", "#wesen-profile-identity"],
      ["symbiosis", "Neural Symbiosis", "wesen", "focus", "#wesen-neural-symbiosis"], ["gateways", "Gateways", "embodiment", "focus", "#mhrn-gateway-monitor"],
    ],
  },
  control: {
    number: "04", label: "Control", subtitle: "Steuerung & Parameter", owner: "control",
    purpose: "Alle zustandsverändernden Operatorfunktionen, Experimentsteuerung, strukturelle Freigaben und wissenschaftliche Parameter.",
    howto: ["Runtime- und Experimentmodus prüfen.", "Parameter als Pending Change vorbereiten und Provenienz kontrollieren.", "Lernen und Struktur nur über Approval-Grenzen freigeben."],
    contracts: ["/api/control", "/api/parameters", "/api/structural/status"],
    routes: [
      ["overview", "Übersicht", "control"], ["runtime", "Runtime", "control", "focusOnly", "#control-causal-flow,#runtime-control-card"],
      ["console", "Konsole", "control", "focusOnly", "#operator-console"], ["experiments", "Experiment Mode", "control", "focusOnly", "#experiment-panel"],
      ["structural", "Struktur & Lernen", "control", "focusOnly", "#structural-live-strip,#mhrn-learning-prep,#mhrn-structural-inspector"],
      ["parameters", "Parameter", "settings"],
    ],
  },
  release: {
    number: "05", label: "Release", subtitle: "Gate & Reife", owner: "gate",
    purpose: "Engineering-Reife, CI, Scientific Gate, Roadmap und veröffentlichte Releases getrennt bewerten.",
    howto: ["Gate und Blocker zuerst prüfen.", "Engineering-Reife nicht mit wissenschaftlicher Evidenz gleichsetzen.", "Release nur aus einem verifizierten Source-Freeze ableiten."],
    contracts: ["/api/gate/status", "/api/releases", "/api/releases/current"],
    routes: [
      ["overview", "Übersicht", "gate"], ["gate", "Gate", "gate", "release", "gate"], ["releases", "Releases", "gate", "release", "releases"],
      ["preview", "Vorschau", "gate", "release", "preview"], ["timeline", "Timeline", "gate", "release", "timeline"],
      ["development", "Entwicklung", "gate", "release", "development"], ["documents", "Roadmap", "gate", "release", "documents"],
    ],
  },
  settings: {
    number: "06", label: "Settings", subtitle: "App & Integrationen", owner: "appsettings",
    purpose: "Nicht-wissenschaftliche Oberfläche, Chat-/AI-Provider und Integrationen. Modellparameter bleiben unter Control.",
    howto: ["Oberfläche und Accessibility hier konfigurieren.", "AI-Provider über den vorhandenen Chat-Settings-Vertrag verwalten.", "Runtime-/Modellparameter ausschließlich unter Control → Parameter ändern."],
    contracts: ["/api/research/chat/settings", "/api/research/chat/providers", "/api/integration/status"],
    routes: [["overview", "Übersicht", "appsettings"], ["appearance", "Oberfläche", "appsettings", "generated", "appearance"], ["ai", "AI & Chat", "appsettings", "generated", "ai"], ["integrations", "Integrationen", "appsettings", "generated", "integrations"], ["boundaries", "Grenzen", "appsettings", "generated", "boundaries"]],
  },
  review: {
    number: "07", label: "Review", subtitle: "Human Review & Prüfer", owner: "review",
    purpose: "Human Review, AIRR-Interpretationen, externe Prüfermetadaten und Prüferportal ohne automatische EVID-Promotion.",
    howto: ["Offene Review-Items im Inbox-Untertab prüfen.", "AI-Interpretationen nur als Interpretation akzeptieren oder ablehnen.", "Probandenantworten bleiben außerhalb des Research-AI-Kontexts."],
    contracts: ["/api/research/reviews", "/api/research/external-review", "/api/research/ai-reports"],
    routes: [["overview", "Übersicht", "review"], ["inbox", "Review Inbox", "review", "generated", "inbox"], ["ai", "AI Reports", "review", "generated", "ai"], ["external", "External Review", "review", "generated", "external"], ["portal", "Prüferportal", "review", "generated", "portal"], ["method", "Methoden & Ethik", "review", "generated", "method"]],
  },
});

let currentArea = "dashboard";
let currentRoute = "overview";
let refreshTimer = null;

const byId = (id) => document.getElementById(id);
const rootFor = (workspace) => byId(`tab-${workspace}`);

function activateLegacy(workspace) {
  const button = document.querySelector(`.tab-nav .tab-btn[data-tab="${workspace}"]`);
  if (!button) return false;
  button.click();
  requestAnimationFrame(() => {
    document.querySelectorAll(".tab-content[id^='tab-']").forEach((node) => {
      const active = node.id === `tab-${workspace}`;
      node.classList.toggle("active", active);
      node.hidden = !active;
    });
    document.querySelectorAll(".tab-btn[data-tab]").forEach((node) => node.classList.toggle("active", node === button));
    document.body.dataset.currentTab = workspace;
  });
  return true;
}

function createGeneratedWorkspace(id, label, kicker) {
  if (rootFor(id)) return rootFor(id);
  const main = document.querySelector("main");
  const section = document.createElement("section");
  section.className = "tab-content mhrn-generated-workspace";
  section.id = `tab-${id}`;
  section.hidden = true;
  section.innerHTML = `<header class="workspace-header"><div><span class="workspace-kicker">${kicker}</span><h2>${label}</h2><p>Strukturierte Arbeitsfläche des MHRN Dashboard.</p></div></header>`;
  main?.append(section);
  const tabs = document.querySelector(".tab-nav");
  if (tabs && !tabs.querySelector(`[data-tab="${id}"]`)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "tab-btn mhrn-generated-tab";
    button.dataset.tab = id;
    button.hidden = true;
    button.textContent = label;
    tabs.append(button);
  }
  return section;
}

function ensureGeneratedWorkspaces() {
  const settings = createGeneratedWorkspace("appsettings", "Settings", "APPLICATION");
  if (settings && !byId("appsettings-content")) settings.insertAdjacentHTML("beforeend", `
    <div id="appsettings-content" class="mhrn-generated-panels">
      <section data-generated-panel="appearance"><h3>Oberfläche & Accessibility</h3><p>Theme, Kontrast, Reader Mode, Accessibility und Hilfe bleiben UI-Einstellungen und verändern keine wissenschaftlichen Parameter.</p><div class="mhrn-action-row"><button type="button" data-proxy="#theme-toggle">Theme wechseln</button><button type="button" data-proxy="#contrast-toggle">Kontrast</button><button type="button" data-proxy="#reader-toggle">Reader Mode</button><button type="button" data-proxy="#accessibility-toggle">Accessibility</button></div></section>
      <section data-generated-panel="ai"><h3>AI & Research Chat</h3><p>Provider, Modell, Kontext und Health über den kanonischen Research-Chat-Vertrag.</p><div id="appsettings-ai-detail" class="mhrn-kv-list">lade …</div><button type="button" id="appsettings-open-chat">Chat Settings öffnen</button></section>
      <section data-generated-panel="integrations"><h3>Integrationen</h3><p>Backend-/Frontend-Integration und verfügbare Komponenten.</p><div id="appsettings-integration-detail" class="mhrn-kv-list">lade …</div></section>
      <section data-generated-panel="boundaries"><h3>Konfigurationsgrenzen</h3><p>App-Settings steuern Darstellung und Integrationen. Wissenschaftlich sensitive Modell- und Runtime-Parameter gehören ausschließlich zu <strong>Control → Parameter</strong>.</p><button type="button" data-route-jump="control:parameters">Parameter öffnen</button></section>
    </div>`);
  const review = createGeneratedWorkspace("review", "Review", "HUMAN REVIEW");
  if (review && !byId("review-content")) review.insertAdjacentHTML("beforeend", `
    <div id="review-content" class="mhrn-generated-panels">
      <section data-generated-panel="inbox"><header><h3>Review Inbox</h3><div><span>offen <strong id="review-open-count">—</strong></span><span>abgeschlossen <strong id="review-completed-count">—</strong></span></div></header><div id="review-inbox-list">lade …</div></section>
      <section data-generated-panel="ai"><div id="review-ai-tools-mount"></div></section>
      <section data-generated-panel="external"><div id="review-external-mount"></div></section>
      <section data-generated-panel="portal"><h3>Prüfer- und Probandenportal</h3><p>Die separate Ansicht lädt keine privaten Antworten in den Dashboard-/AI-Kontext.</p><div class="mhrn-action-row"><a class="button-like" href="/review" target="_blank" rel="noopener">/review öffnen</a><button type="button" id="review-copy-link">Link kopieren</button></div></section>
      <section data-generated-panel="method"><h3>Methoden & Ethik</h3><p>Standardisierte Fragen, Einwilligung, Anonymität, Rücktritt, Auswertungsplan und Trennung von AI-Interpretation und wissenschaftlicher Evidenz.</p><button type="button" data-review-file="external_review/INTEGRATION.md">Methodik im File Viewer</button></section>
    </div>`);
}

function overviewMarkup(areaId, area) {
  const routes = area.routes.filter(([id]) => id !== "overview");
  return `<section class="mhrn-area-overview" data-area-overview="${areaId}">
    <header class="mhrn-area-overview-hero"><div><span class="workspace-kicker">${area.number} / ${area.subtitle}</span><h2>${area.label}</h2><p>${area.purpose}</p></div><strong>${routes.length} Unterbereiche</strong></header>
    <div class="mhrn-area-overview-grid"><article><h3>How to</h3><ol>${area.howto.map((item) => `<li>${item}</li>`).join("")}</ol></article><article><h3>Backend-Verträge</h3><div class="mhrn-contract-list">${area.contracts.map((endpoint) => `<div data-contract="${endpoint}"><code>${endpoint}</code><span>prüfe …</span></div>`).join("")}</div></article></div>
    <div class="mhrn-area-route-grid">${routes.map(([id,label], index) => `<button type="button" data-route-card="${id}" title="${label} öffnen"><span>${String(index + 1).padStart(2,"0")}</span><strong>${label}</strong></button>`).join("")}</div>
  </section>`;
}

function ensureOverview(areaId) {
  const area = AREAS[areaId];
  const root = rootFor(area.owner);
  if (!root || root.querySelector(`[data-area-overview="${areaId}"]`)) return;
  const header = root.querySelector(":scope > .workspace-header, :scope > .overview-command-bar, :scope > header");
  const holder = document.createElement("div");
  holder.innerHTML = overviewMarkup(areaId, area);
  const overview = holder.firstElementChild;
  header?.insertAdjacentElement("afterend", overview) || root.prepend(overview);
  overview.querySelectorAll("[data-route-card]").forEach((button) => button.addEventListener("click", () => selectRoute(areaId, button.dataset.routeCard)));
}

function ensureNavigation() {
  let nav = document.querySelector(".brain5d-primary-nav");
  if (!nav) {
    nav = document.createElement("nav"); nav.className = "brain5d-primary-nav";
    document.body.prepend(nav);
  }
  if (nav.dataset.router === "v1") return;
  nav.dataset.router = "v1";
  nav.setAttribute("aria-label", "MHRN Hauptnavigation");
  nav.innerHTML = Object.entries(AREAS).map(([id, area]) => `<button type="button" data-mhrn-area="${id}" title="${area.label}: ${area.purpose}"><span class="mhrn-nav-number">${area.number}</span><span class="mhrn-nav-icon">${area.label.slice(0,1)}</span><span class="mhrn-nav-copy"><strong>${area.label}</strong><span>${area.subtitle}</span></span></button>`).join("");
  nav.addEventListener("click", (event) => { const button = event.target.closest("[data-mhrn-area]"); if (button) selectRoute(button.dataset.mhrnArea, "overview"); });
}

function ensureContextNav(areaId) {
  const area = AREAS[areaId];
  for (const workspace of new Set(area.routes.map((route) => route[2]))) {
    const root = rootFor(workspace); if (!root) continue;
    let nav = root.querySelector(`:scope > .mhrn-context-nav[data-area="${areaId}"]`);
    if (nav) continue;
    nav = document.createElement("nav"); nav.className = "mhrn-context-nav"; nav.dataset.area = areaId; nav.setAttribute("role", "tablist");
    nav.innerHTML = area.routes.map(([id,label]) => `<button type="button" role="tab" data-area-route="${id}" title="${label}">${label}</button>`).join("");
    const anchor = root.querySelector(":scope > .workspace-header, :scope > .overview-command-bar, :scope > header");
    anchor?.insertAdjacentElement("afterend", nav) || root.prepend(nav);
    nav.addEventListener("click", (event) => { const button = event.target.closest("[data-area-route]"); if (button) selectRoute(areaId, button.dataset.areaRoute); });
  }
}

function hideLocalTabs() {
  ["#tab-overview > .overview-subtabs", "#tab-research > .research-subtabs", "#tab-network > .workspace-view-tabs", "#tab-gate > .workspace-view-tabs", "#tab-embodiment > .embodiment-subtabs", ".science-context-nav", ".research-workspace-tabs"].forEach((selector) => document.querySelectorAll(selector).forEach((node) => node.classList.add(ROUTED_CLASS)));
}

function clickMatch(selector, dataName, value) {
  const button = [...document.querySelectorAll(selector)].find((node) => node.dataset[dataName] === value);
  button?.click();
}

function clearFocused(workspace) {
  rootFor(workspace)?.querySelectorAll(".mhrn-route-focus-hidden").forEach((node) => node.classList.remove("mhrn-route-focus-hidden"));
}

function applyRoute(areaId, route) {
  const [id,,workspace,action,arg] = route;
  activateLegacy(workspace);
  requestAnimationFrame(() => {
    clearFocused(workspace);
    if (action === "overview") clickMatch(".overview-subtab", "subtab", arg);
    if (action === "research") clickMatch(".research-subtab", "subtab", arg);
    if (action === "embodiment") clickMatch(".embodiment-subtab", "subtab", arg);
    if (action === "view") {
      const name = workspace === "gate" ? "release" : "network";
      clickMatch(`[data-workspace-views="${name}"] [data-workspace-view]`, "workspaceView", arg);
    }
    if (action === "focus" && arg) document.querySelector(arg)?.scrollIntoView({ block: "start" });
    if (action === "focusOnly") {
      const root = rootFor(workspace); const keep = new Set(String(arg).split(",").map((s) => s.trim()));
      root?.querySelectorAll(":scope > section, :scope > article, :scope > .card, :scope > .panel, :scope > .operator-console, :scope > .experiment-panel").forEach((node) => { if (![...keep].some((sel) => node.matches(sel))) node.classList.add("mhrn-route-focus-hidden"); });
    }
    if (workspace === "settings") {
      const h2 = rootFor("settings")?.querySelector(".workspace-header h2"); if (h2) h2.textContent = "Parameter & Provenienz";
    }
    if (action === "generated") showGenerated(workspace, arg);
    setOverview(areaId, id === "overview");
    syncNav();
  });
}

function showGenerated(workspace, id) {
  rootFor(workspace)?.querySelectorAll("[data-generated-panel]").forEach((node) => { node.hidden = node.dataset.generatedPanel !== id; });
}

function setOverview(areaId, visible) {
  const area = AREAS[areaId]; const root = rootFor(area.owner); if (!root) return;
  const overview = root.querySelector(`[data-area-overview="${areaId}"]`); if (overview) overview.hidden = !visible;
  [...root.children].forEach((node) => {
    if (node === overview || node.classList?.contains("mhrn-context-nav") || node.classList?.contains("workspace-header") || node.classList?.contains("overview-command-bar")) return;
    if (visible) node.classList.add("mhrn-overview-content-hidden"); else node.classList.remove("mhrn-overview-content-hidden");
  });
}

function syncNav() {
  document.body.dataset.currentArea = currentArea; document.body.dataset.currentRoute = currentRoute;
  document.querySelectorAll("[data-mhrn-area]").forEach((node) => node.classList.toggle("active", node.dataset.mhrnArea === currentArea));
  document.querySelectorAll(".mhrn-context-nav").forEach((nav) => {
    nav.hidden = nav.dataset.area !== currentArea;
    nav.querySelectorAll("[data-area-route]").forEach((node) => { const active = nav.dataset.area === currentArea && node.dataset.areaRoute === currentRoute; node.classList.toggle("active", active); node.setAttribute("aria-selected", String(active)); });
  });
}

async function probeContracts(areaId) {
  const area = AREAS[areaId]; const overview = rootFor(area.owner)?.querySelector(`[data-area-overview="${areaId}"]`); if (!overview) return;
  await Promise.all(area.contracts.map(async (endpoint) => {
    const row = [...overview.querySelectorAll("[data-contract]")].find((node) => node.dataset.contract === endpoint); if (!row) return;
    try { const response = await fetch(endpoint, { cache: "no-store", headers: { Accept: "application/json" } }); row.dataset.state = response.ok ? "ok" : "failed"; row.querySelector("span").textContent = `HTTP ${response.status}`; }
    catch (_) { row.dataset.state = "offline"; row.querySelector("span").textContent = "offline"; }
  }));
}

async function readJson(url) { const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } }); const payload = await response.json(); if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`); return payload; }
function kv(data, limit=16) { return Object.entries(data || {}).filter(([,v]) => v !== null && v !== undefined).slice(0,limit).map(([k,v]) => `<div><span>${k}</span><strong>${typeof v === "object" ? JSON.stringify(v).slice(0,180) : String(v).slice(0,180)}</strong></div>`).join("") || "<p>Keine Daten.</p>"; }

async function refreshSettings() {
  if (currentArea !== "settings") return;
  try { const [settings,providers,health] = await Promise.all([readJson("/api/research/chat/settings"),readJson("/api/research/chat/providers"),readJson("/api/research/chat/health")]); byId("appsettings-ai-detail").innerHTML = kv({ provider:settings.provider, model:settings.model, endpoint:settings.endpoint, vision:settings.vision_enabled, tools:settings.tools_enabled, models:providers.models?.length ?? 0, health:health.ok ? "online" : "offline" }); } catch (error) { if (byId("appsettings-ai-detail")) byId("appsettings-ai-detail").textContent = `Nicht verfügbar: ${error.message}`; }
  try { byId("appsettings-integration-detail").innerHTML = kv(await readJson("/api/integration/status"),24); } catch (error) { if (byId("appsettings-integration-detail")) byId("appsettings-integration-detail").textContent = `Nicht verfügbar: ${error.message}`; }
}

function reviewItem(item) { const path = item.artifact_path || ""; return `<article class="mhrn-review-item"><header><strong>${item.title || item.report_id || path || "Review"}</strong><span>${[item.kind,item.experiment_id,item.research_question_id].filter(Boolean).join(" · ")}</span></header><p>${item.summary || "Human review erforderlich."}</p>${path ? `<button type="button" data-review-path="${path}">Im File Viewer öffnen</button>` : ""}</article>`; }
async function refreshReview() {
  if (currentArea !== "review") return;
  try { const inbox = await readJson("/api/research/reviews"); byId("review-open-count").textContent = String(inbox.open ?? 0); byId("review-completed-count").textContent = String(inbox.completed ?? 0); const list = byId("review-inbox-list"); const items = Array.isArray(inbox.items) ? inbox.items : []; list.innerHTML = items.length ? items.map(reviewItem).join("") : "<p>Keine offenen Review-Items.</p>"; list.querySelectorAll("[data-review-path]").forEach((button) => button.addEventListener("click", () => { document.dispatchEvent(new CustomEvent("brain5d:open-file", { detail: { source: "research", path: button.dataset.reviewPath } })); selectRoute("science","files"); })); } catch (error) { if (byId("review-inbox-list")) byId("review-inbox-list").textContent = `Nicht verfügbar: ${error.message}`; }
}

function bindGeneratedActions() {
  document.addEventListener("click", (event) => {
    const proxy = event.target.closest("[data-proxy]"); if (proxy) document.querySelector(proxy.dataset.proxy)?.click();
    const jump = event.target.closest("[data-route-jump]"); if (jump) { const [a,r] = jump.dataset.routeJump.split(":"); selectRoute(a,r); }
    const file = event.target.closest("[data-review-file]"); if (file) { document.dispatchEvent(new CustomEvent("brain5d:open-file", { detail: { source: "research", path: file.dataset.reviewFile } })); selectRoute("science","files"); }
  });
  byId("appsettings-open-chat")?.addEventListener("click", () => { byId("chat-toggle")?.click(); requestAnimationFrame(() => byId("chat-settings-toggle")?.click()); });
  byId("review-copy-link")?.addEventListener("click", async (event) => { try { await navigator.clipboard.writeText(new URL("/review", location.href).href); event.currentTarget.textContent = "Kopiert"; } catch (_) { event.currentTarget.textContent = "Kopieren fehlgeschlagen"; } });
}

function addHoverInfo() { document.querySelectorAll("button,a,summary,input,select,textarea,[role='button'],[role='tab']").forEach((node) => { if (!node.title) { const text = (node.getAttribute("aria-label") || node.textContent || node.placeholder || "").trim().replace(/\s+/g," "); if (text) node.title = text.slice(0,220); } }); }

export function selectRoute(areaId, routeId="overview") {
  const area = AREAS[areaId] || AREAS.dashboard; const route = area.routes.find(([id]) => id === routeId) || area.routes[0];
  currentArea = AREAS[areaId] ? areaId : "dashboard"; currentRoute = route[0];
  ensureContextNav(currentArea); applyRoute(currentArea, route); probeContracts(currentArea);
  if (currentArea === "settings") refreshSettings(); if (currentArea === "review") refreshReview();
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ area:currentArea, route:currentRoute })); } catch (_) {}
}

function restore() { try { const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null"); if (saved && AREAS[saved.area] && AREAS[saved.area].routes.some(([id]) => id === saved.route)) return saved; } catch (_) {} return { area:"dashboard", route:"overview" }; }

export function initWorkspaceRouter() {
  ensureGeneratedWorkspaces(); ensureNavigation(); Object.keys(AREAS).forEach((id) => { ensureOverview(id); ensureContextNav(id); }); hideLocalTabs(); bindGeneratedActions(); addHoverInfo();
  const saved = restore(); selectRoute(saved.area,saved.route);
  const observer = new MutationObserver(() => { hideLocalTabs(); addHoverInfo(); Object.keys(AREAS).forEach(ensureContextNav); }); observer.observe(document.querySelector("main") || document.body,{childList:true,subtree:true});
  refreshTimer = window.setInterval(() => { probeContracts(currentArea); if (currentArea === "settings") refreshSettings(); if (currentArea === "review") refreshReview(); },30000);
  window.addEventListener("beforeunload", () => refreshTimer && clearInterval(refreshTimer), { once:true });
  window.MHRNWorkspaceArchitecture = { selectRoute, areas:AREAS, refreshContracts:probeContracts };
}
