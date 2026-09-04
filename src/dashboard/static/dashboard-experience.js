/* Brain-5D Operator Experience
 *
 * Presentation and navigation only. This module never issues runtime control
 * commands and never fabricates scientific state. Values shown in the chrome
 * are copied from already-rendered dashboard state or explicitly marked as UI.
 */

const WORKSPACES = {
  overview: { icon: "◫", label: "Overview", group: "System", hint: "Live body, health and readiness" },
  network: { icon: "⌬", label: "Network", group: "Observe", hint: "Dynamics, topology and populations" },
  control: { icon: "▶", label: "Control", group: "Operate", hint: "Runtime, pacing and approvals" },
  research: { icon: "⌕", label: "Research", group: "Evidence", hint: "Experiments, provenance and files" },
  gate: { icon: "✓", label: "Release", group: "Verify", hint: "Scientific gate and release readiness" },
  settings: { icon: "⚙", label: "Settings", group: "Configure", hint: "Runtime-visible configuration" },
  embodiment: { icon: "◈", label: "Embodiment", group: "Embody", hint: "Body, devices and interoception" },
};

const STORAGE = {
  welcome: "brain5d-experience-welcome-dismissed",
  focus: "brain5d-experience-focus",
};

function ensureStylesheet() {
  if (document.querySelector('link[data-dashboard-experience="true"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/dashboard-experience.css";
  link.dataset.dashboardExperience = "true";
  document.head.appendChild(link);
}

function activeWorkspaceName() {
  const section = document.querySelector(".tab-content.active[id^='tab-']");
  return section?.id?.replace("tab-", "") || "overview";
}

function repairWorkspaceActivation(button) {
  const name = button?.dataset.tab;
  if (!name) return;
  requestAnimationFrame(() => {
    const active = document.querySelector(".tab-content.active[id^='tab-']");
    if (active?.id === `tab-${name}`) return;
    document.querySelectorAll(".tab-btn[data-tab]").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => {
      const selected = tab.id === `tab-${name}`;
      tab.classList.toggle("active", selected);
      tab.hidden = !selected;
    });
    document.body.dataset.currentTab = name;
  });
}

function activateWorkspace(name) {
  const button = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (!button) return;
  button.click();
  repairWorkspaceActivation(button);
}

function safeText(selector, fallback = "unknown") {
  const value = document.querySelector(selector)?.textContent?.trim();
  return value || fallback;
}

function makeButton(label, action, title = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "experience-icon-button";
  button.dataset.experienceAction = action;
  button.textContent = label;
  if (title) button.title = title;
  return button;
}

function enhanceTopbar() {
  const topbar = document.querySelector(".topbar");
  if (!topbar || topbar.querySelector(".experience-status-cluster")) return;

  const cluster = document.createElement("div");
  cluster.className = "experience-status-cluster";
  cluster.setAttribute("aria-label", "Operator context");
  cluster.innerHTML = `
    <span class="experience-live-dot" aria-hidden="true"></span>
    <span class="experience-status-copy"><small>WORKSPACE</small><strong data-experience-workspace>Overview</strong></span>
    <span class="experience-status-copy"><small>RUNTIME</small><strong data-experience-runtime>unknown</strong></span>
    <span class="experience-status-copy"><small>TICK</small><strong data-experience-tick>—</strong></span>`;

  const right = topbar.querySelector(".topbar-right");
  topbar.insertBefore(cluster, right || null);

  if (right) {
    right.prepend(makeButton("⌘K", "palette", "Command palette (Ctrl/Cmd+K)"));
    right.prepend(makeButton("◎", "focus", "Focus mode (F)"));
  }
}

function enhanceNavigation() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach((button) => {
    const name = button.dataset.tab;
    const meta = WORKSPACES[name];
    if (!meta || button.dataset.experienceEnhanced === "true") return;
    button.dataset.experienceEnhanced = "true";
    button.innerHTML = `<span class="experience-tab-icon" aria-hidden="true">${meta.icon}</span><span class="experience-tab-copy"><strong>${meta.label}</strong><small>${meta.group}</small></span>`;
    button.title = meta.hint;
  });
}

function addWorkspaceRibbons() {
  Object.entries(WORKSPACES).forEach(([name, meta]) => {
    const tab = document.getElementById(`tab-${name}`);
    if (!tab || tab.querySelector(":scope > .experience-ribbon")) return;
    const utility = tab.querySelector(":scope > .dashboard-utility-bar");
    const ribbon = document.createElement("aside");
    ribbon.className = "experience-ribbon";
    ribbon.setAttribute("aria-label", `${meta.label} workspace context`);
    ribbon.innerHTML = `
      <div class="experience-ribbon-copy">
        <span>${meta.group.toUpperCase()} / ${meta.label.toUpperCase()}</span>
        <strong>${meta.hint}</strong>
      </div>
      <div class="experience-ribbon-actions">
        <button type="button" data-experience-action="palette">⌘ Command</button>
        <button type="button" data-experience-action="shortcuts">? Shortcuts</button>
        <button type="button" data-experience-action="focus">◎ Focus</button>
      </div>`;
    if (utility) utility.insertAdjacentElement("afterend", ribbon);
    else tab.prepend(ribbon);
  });
}

function buildWelcome() {
  if (localStorage.getItem(STORAGE.welcome) === "true") return;
  const overview = document.getElementById("tab-overview");
  if (!overview || overview.querySelector(".experience-welcome")) return;

  const panel = document.createElement("section");
  panel.className = "experience-welcome";
  panel.innerHTML = `
    <div class="experience-welcome-copy">
      <span class="experience-eyebrow">OPERATOR ORIENTATION</span>
      <h2>Vom Systemzustand zur belastbaren Evidenz</h2>
      <p>Brain-5D trennt Beobachtung, Eingriff, Experiment und Freigabe. Diese Oberfläche führt entlang derselben Kausalitätskette; sie erzeugt keine Messwerte und ersetzt keine wissenschaftlichen Nachweise.</p>
    </div>
    <div class="experience-welcome-steps">
      <button type="button" data-jump-workspace="overview"><b>01</b><span><strong>Zustand lesen</strong><small>Health, Aktivität, Speicher</small></span></button>
      <button type="button" data-jump-workspace="network"><b>02</b><span><strong>Dynamik prüfen</strong><small>Spikes, Populationen, Topologie</small></span></button>
      <button type="button" data-jump-workspace="control"><b>03</b><span><strong>Gezielt eingreifen</strong><small>Operator-bestätigte Controls</small></span></button>
      <button type="button" data-jump-workspace="research"><b>04</b><span><strong>Evidenz erzeugen</strong><small>Experiment und Provenienz</small></span></button>
      <button type="button" data-jump-workspace="gate"><b>05</b><span><strong>Freigabe prüfen</strong><small>Gate, CI, Reproduzierbarkeit</small></span></button>
    </div>
    <button type="button" class="experience-dismiss" data-experience-action="dismiss-welcome" aria-label="Einführung schließen">×</button>`;

  const header = overview.querySelector(":scope > .overview-command-bar");
  const anchor = overview.querySelector(":scope > .experience-ribbon") || header;
  anchor?.insertAdjacentElement("afterend", panel);
}

function buildPalette() {
  if (document.getElementById("experience-command-palette")) return;
  const dialog = document.createElement("dialog");
  dialog.id = "experience-command-palette";
  dialog.className = "experience-dialog experience-command-palette";
  dialog.innerHTML = `
    <form method="dialog" class="experience-dialog-frame">
      <header><div><span class="experience-eyebrow">COMMAND PALETTE</span><h2>Navigate Brain-5D</h2></div><button value="cancel" aria-label="Close">×</button></header>
      <label class="experience-command-search"><span>⌕</span><input type="search" autocomplete="off" placeholder="Workspace oder Funktion suchen …" data-experience-search></label>
      <div class="experience-command-results" data-experience-results></div>
      <footer><span><kbd>↑</kbd><kbd>↓</kbd> wählen</span><span><kbd>Enter</kbd> öffnen</span><span><kbd>Esc</kbd> schließen</span></footer>
    </form>`;
  document.body.appendChild(dialog);

  const input = dialog.querySelector("[data-experience-search]");
  input.addEventListener("input", () => renderPaletteResults(input.value));
  dialog.addEventListener("keydown", handlePaletteKeys);
  dialog.addEventListener("close", () => { input.value = ""; renderPaletteResults(""); });
  renderPaletteResults("");
}

function commandItems() {
  const workspaceItems = Object.entries(WORKSPACES).map(([id, meta]) => ({
    id: `workspace:${id}`,
    icon: meta.icon,
    label: meta.label,
    meta: `${meta.group} · ${meta.hint}`,
    run: () => activateWorkspace(id),
  }));
  return [
    ...workspaceItems,
    { id: "action:refresh", icon: "↻", label: "Refresh active view", meta: "Read-only UI refresh", run: () => document.querySelector(".tab-content.active [data-dashboard-action='refresh']")?.click() },
    { id: "action:focus", icon: "◎", label: "Toggle focus mode", meta: "Hide secondary chrome", run: toggleFocus },
    { id: "action:shortcuts", icon: "?", label: "Keyboard shortcuts", meta: "Show operator navigation keys", run: openShortcuts },
  ];
}

function renderPaletteResults(query) {
  const root = document.querySelector("[data-experience-results]");
  if (!root) return;
  const needle = query.trim().toLowerCase();
  const items = commandItems().filter((item) => `${item.label} ${item.meta}`.toLowerCase().includes(needle));
  root.innerHTML = "";
  items.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "experience-command-item";
    button.dataset.commandId = item.id;
    button.dataset.commandIndex = String(index);
    button.innerHTML = `<span class="experience-command-icon">${item.icon}</span><span><strong>${item.label}</strong><small>${item.meta}</small></span><kbd>↵</kbd>`;
    button.addEventListener("click", () => runCommand(item));
    root.appendChild(button);
  });
  root.querySelector("button")?.classList.add("selected");
}

function runCommand(item) {
  document.getElementById("experience-command-palette")?.close();
  item.run();
}

function handlePaletteKeys(event) {
  if (!["ArrowDown", "ArrowUp", "Enter"].includes(event.key)) return;
  const buttons = [...document.querySelectorAll(".experience-command-item")];
  if (!buttons.length) return;
  const current = Math.max(0, buttons.findIndex((button) => button.classList.contains("selected")));
  event.preventDefault();
  if (event.key === "Enter") {
    buttons[current]?.click();
    return;
  }
  buttons[current]?.classList.remove("selected");
  const delta = event.key === "ArrowDown" ? 1 : -1;
  const next = (current + delta + buttons.length) % buttons.length;
  buttons[next].classList.add("selected");
  buttons[next].scrollIntoView({ block: "nearest" });
}

function buildShortcuts() {
  if (document.getElementById("experience-shortcuts")) return;
  const dialog = document.createElement("dialog");
  dialog.id = "experience-shortcuts";
  dialog.className = "experience-dialog experience-shortcuts";
  dialog.innerHTML = `
    <form method="dialog" class="experience-dialog-frame">
      <header><div><span class="experience-eyebrow">KEYBOARD MAP</span><h2>Operator shortcuts</h2></div><button value="cancel" aria-label="Close">×</button></header>
      <div class="experience-shortcut-grid">
        <div><kbd>Ctrl</kbd><span>+</span><kbd>K</kbd><strong>Command palette</strong></div>
        <div><kbd>?</kbd><strong>Shortcut map</strong></div>
        <div><kbd>F</kbd><strong>Focus mode</strong></div>
        <div><kbd>1</kbd>…<kbd>7</kbd><strong>Workspace wechseln</strong></div>
        <div><kbd>Esc</kbd><strong>Overlay schließen</strong></div>
      </div>
      <p class="experience-integrity-note">Die globalen Shortcuts navigieren ausschließlich in der Oberfläche. Runtime-Aktionen werden nicht automatisch ausgelöst.</p>
    </form>`;
  document.body.appendChild(dialog);
}

function openPalette() {
  const dialog = document.getElementById("experience-command-palette");
  if (!dialog) return;
  dialog.showModal();
  requestAnimationFrame(() => dialog.querySelector("[data-experience-search]")?.focus());
}

function openShortcuts() {
  document.getElementById("experience-shortcuts")?.showModal();
}

function toggleFocus() {
  const enabled = document.body.dataset.experienceFocus !== "true";
  document.body.dataset.experienceFocus = String(enabled);
  localStorage.setItem(STORAGE.focus, String(enabled));
  document.querySelectorAll('[data-experience-action="focus"]').forEach((button) => {
    button.classList.toggle("active", enabled);
  });
}

function syncChrome() {
  const name = activeWorkspaceName();
  const meta = WORKSPACES[name] || WORKSPACES.overview;
  document.querySelectorAll("[data-experience-workspace]").forEach((node) => { node.textContent = meta.label; });
  document.querySelectorAll("[data-experience-runtime]").forEach((node) => { node.textContent = safeText("#overview-runtime-status", safeText("#control-workspace-state")); });
  document.querySelectorAll("[data-experience-tick]").forEach((node) => { node.textContent = safeText("#tick", safeText("#control-workspace-tick", "—")); });
  document.body.dataset.experienceWorkspace = name;
}

function enhanceUnknownStates() {
  const markers = ["—", "unknown", "pending", "Waiting for component state", "Keine Live-Verbindung."];
  document.querySelectorAll(".tab-content strong, .tab-content .overview-empty, .tab-content .heatmap-meta").forEach((node) => {
    const text = node.textContent?.trim();
    if (!markers.includes(text)) return;
    node.classList.add("experience-unknown-state");
    if (!node.title) node.title = "Noch kein beobachteter Wert verfügbar";
  });
}

function bindActions() {
  document.addEventListener("click", (event) => {
    const jump = event.target.closest("[data-jump-workspace]");
    if (jump) activateWorkspace(jump.dataset.jumpWorkspace);

    const action = event.target.closest("[data-experience-action]")?.dataset.experienceAction;
    if (!action) return;
    if (action === "palette") openPalette();
    if (action === "shortcuts") openShortcuts();
    if (action === "focus") toggleFocus();
    if (action === "dismiss-welcome") {
      localStorage.setItem(STORAGE.welcome, "true");
      document.querySelector(".experience-welcome")?.remove();
    }
  });

  document.addEventListener("keydown", (event) => {
    const tag = event.target?.tagName?.toLowerCase();
    const typing = tag === "input" || tag === "textarea" || tag === "select" || event.target?.isContentEditable;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openPalette();
      return;
    }
    if (typing) return;
    if (event.key === "?") openShortcuts();
    if (event.key.toLowerCase() === "f") toggleFocus();
    if (/^[1-7]$/.test(event.key)) activateWorkspace(Object.keys(WORKSPACES)[Number(event.key) - 1]);
  });

  document.querySelectorAll(".tab-btn[data-tab]").forEach((button) => button.addEventListener("click", () => {
    repairWorkspaceActivation(button);
    requestAnimationFrame(syncChrome);
  }));
}

function observeRenderedState() {
  const observer = new MutationObserver(() => {
    syncChrome();
    enhanceUnknownStates();
  });
  ["overview-runtime-status", "tick", "control-workspace-state", "control-workspace-tick"].forEach((id) => {
    const node = document.getElementById(id);
    if (node) observer.observe(node, { childList: true, characterData: true, subtree: true });
  });
}

function restorePreferences() {
  document.body.dataset.experienceFocus = localStorage.getItem(STORAGE.focus) === "true" ? "true" : "false";
}

function init() {
  ensureStylesheet();
  restorePreferences();
  enhanceTopbar();
  enhanceNavigation();
  addWorkspaceRibbons();
  buildWelcome();
  buildPalette();
  buildShortcuts();
  bindActions();
  observeRenderedState();
  syncChrome();
  enhanceUnknownStates();
  document.body.classList.add("experience-ready");
}

ensureStylesheet();
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
else init();
