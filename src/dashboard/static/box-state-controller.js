/* Responsive box states and Research workspace organization. */
"use strict";

const STORAGE_KEY = "brain5d-box-states";
const RESEARCH_VIEW_KEY = "mhrn-research-workspace-view";
const BOX_SELECTOR = [
  ".card",
  ".panel",
  ".control-card",
  ".overview-surface",
  ".snapshot-info-card",
  ".workspace-tile",
  ".wesen-card",
  ".wesen-stage-card",
  ".wesen-console",
  ".wesen-symbiosis-card",
  ".experiment-workflow",
  ".release-board",
  ".connection-manager",
  ".embodiment-system-strip",
  ".embodiment-loop",
  ".research-workspace-panel",
  ".research-focus-rail",
  ".research-catalog-selector",
  ".research-contract-card",
  ".experiment-library-card",
  ".human-review-card",
  ".rq-proposal-card",
  ".research-review-inbox",
].join(",");

const NESTED_RESEARCH_BOX_SELECTOR = [
  ".experiment-workflow",
  ".research-focus-rail",
  ".research-catalog-selector",
  ".research-contract-card",
  ".experiment-library-card",
  ".human-review-card",
  ".rq-proposal-card",
  ".research-review-inbox",
].join(",");

const EXCLUDED_SELECTOR = [
  ".site-footer",
  ".workspace-header",
  ".overview-command-bar",
  ".dashboard-generated-header",
  ".dashboard-utility-bar",
  ".experience-ribbon",
  ".experience-welcome",
  ".research-chat-modal",
  "dialog",
].join(",");

const HEADER_SELECTOR = [
  ":scope > .panel-title",
  ":scope > .overview-surface-title",
  ":scope > .control-card__header",
  ":scope > .console-header",
  ":scope > .experiment-workflow-header",
  ":scope > .gate-header",
  ":scope > .release-header",
  ":scope > .research-workspace-panel-header",
  ":scope > header",
].join(",");

let states = {};
let scanQueued = false;
let researchWorkspaceReady = false;

function loadStates() {
  try {
    states = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch (_) {
    states = {};
  }
}

function saveStates() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(states));
  } catch (_) {
    // Preferences are optional.
  }
}

function boxKey(box, index) {
  if (box.id) return box.id;
  const workspace = box.closest(".tab-content")?.id || "dashboard";
  return `${workspace}:${box.className}:${index}`;
}

function isNestedBox(box) {
  return Boolean(box.parentElement?.closest(BOX_SELECTOR));
}

function findHeader(box) {
  return box.querySelector(HEADER_SELECTOR);
}

function ensureHeader(box) {
  const existing = findHeader(box);
  if (existing) return existing;
  const heading = box.querySelector(":scope > h2, :scope > h3, :scope > h4");
  const label = box.getAttribute("aria-label") || heading?.textContent?.trim() || "Panel";
  const header = document.createElement("div");
  header.className = "box-state-generated-header";
  const title = document.createElement("strong");
  title.textContent = label;
  header.appendChild(title);
  box.prepend(header);
  return header;
}

function markContent(box, header) {
  [...box.children].forEach((child) => {
    if (child === header || child.classList.contains("box-state-tools")) return;
    child.classList.add("box-state-content");
  });
}

function makeButton(label, icon, state) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "box-state-button";
  button.dataset.boxState = state;
  button.setAttribute("aria-label", label);
  button.title = label;
  button.textContent = icon;
  return button;
}

function setState(box, key, state, persist = true) {
  const next = state === "minimized" || state === "maximized" ? state : "standard";
  box.dataset.boxState = next;
  box.classList.toggle("box-state-minimized", next === "minimized");
  box.classList.toggle("box-state-maximized", next === "maximized");
  if (next === "maximized") document.body.classList.add("box-state-lock");
  if (persist && next !== "maximized") {
    states[key] = next;
    saveStates();
  }
  box.querySelectorAll(".box-state-button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.boxState === next));
  });
}

function enhanceBox(box, index) {
  const nestedResearchBox =
    isNestedBox(box) && box.matches(NESTED_RESEARCH_BOX_SELECTOR);
  if (
    box.classList.contains("box-state-ready") ||
    box.matches(EXCLUDED_SELECTOR) ||
    (isNestedBox(box) && !nestedResearchBox)
  ) {
    return;
  }
  const header = ensureHeader(box);
  const key = boxKey(box, index);
  const tools = document.createElement("div");
  tools.className = "box-state-tools";
  tools.setAttribute("aria-label", "Boxgröße");
  tools.append(
    makeButton("Minimieren", "−", "minimized"),
    makeButton("Standardgröße", "□", "standard"),
    makeButton("Maximieren", "⛶", "maximized"),
  );
  tools.addEventListener("click", (event) => {
    const button = event.target.closest(".box-state-button");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    setState(box, key, button.dataset.boxState);
  });
  header.classList.add("box-state-header");
  header.appendChild(tools);
  markContent(box, header);
  box.dataset.boxKey = key;
  box.classList.add("box-state-ready");
  setState(box, key, states[key] || "standard", false);
}

function installResearchWorkspaceStyle() {
  if (document.querySelector("style[data-research-workspace-style]")) return;
  const style = document.createElement("style");
  style.dataset.researchWorkspaceStyle = "true";
  style.textContent = `
    .research-workspace-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0;padding:6px;border:1px solid var(--line);border-radius:12px;background:var(--surface-1,rgba(255,255,255,.025))}
    .research-workspace-tabs button{border:1px solid transparent;border-radius:9px;padding:8px 12px;background:transparent;color:var(--muted);font-weight:650;cursor:pointer}
    .research-workspace-tabs button:hover,.research-workspace-tabs button.active{color:var(--text);border-color:var(--line);background:var(--surface-2,rgba(255,255,255,.06))}
    .research-workspace-shell{display:grid;gap:12px;min-width:0}
    .research-workspace-panel{display:grid;gap:12px;min-width:0;border:1px solid var(--line);border-radius:14px;padding:12px;background:var(--surface-1,rgba(255,255,255,.02))}
    .research-workspace-panel[hidden]{display:none!important}
    .research-workspace-panel-header{display:flex;justify-content:space-between;gap:12px;align-items:center}
    .research-workspace-panel-header h3{margin:0}.research-workspace-panel-header p{margin:3px 0 0;color:var(--muted);font-size:.78rem}
    .research-workspace-panel>.experiment-workflow,.research-workspace-panel>.research-focus-rail,.research-workspace-panel>.experiment-library-card,.research-workspace-panel>.human-review-card,.research-workspace-panel>.rq-proposal-card,.research-workspace-panel>.research-review-inbox{margin:0}
    .research-file-surface{display:grid;gap:8px;min-width:0}
    .research-workspace-note{font-size:.76rem;color:var(--muted);margin:0}
    @media(max-width:760px){.research-workspace-tabs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.research-workspace-tabs button{width:100%}}
  `;
  document.head.appendChild(style);
}

function panelHeader(title, description) {
  const header = document.createElement("header");
  header.className = "research-workspace-panel-header";
  header.innerHTML = `<div><h3>${title}</h3><p>${description}</p></div>`;
  return header;
}

function moveIfPresent(selector, target) {
  const element = document.querySelector(selector);
  if (element && element.parentElement !== target && !target.contains(element)) {
    target.appendChild(element);
  }
}

function selectResearchView(view) {
  const shell = document.querySelector(".research-workspace-shell");
  const tabs = document.querySelector(".research-workspace-tabs");
  if (!shell || !tabs) return;
  const valid = [
    ...shell.querySelectorAll(":scope > [data-research-workspace-panel]"),
  ].map((panel) => panel.dataset.researchWorkspacePanel);
  const next = valid.includes(view) ? view : "plan";
  tabs.querySelectorAll("[data-research-workspace-view]").forEach((button) => {
    const active = button.dataset.researchWorkspaceView === next;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  shell
    .querySelectorAll(":scope > [data-research-workspace-panel]")
    .forEach((panel) => {
      panel.hidden = panel.dataset.researchWorkspacePanel !== next;
    });
  try {
    localStorage.setItem(RESEARCH_VIEW_KEY, next);
  } catch (_) {
    // Preference persistence is optional.
  }
}

function routeResearchElements() {
  const plan = document.querySelector('[data-research-workspace-panel="plan"]');
  const runs = document.querySelector('[data-research-workspace-panel="runs"]');
  const review = document.querySelector(
    '[data-research-workspace-panel="review"]',
  );
  const files = document.querySelector(
    '[data-research-workspace-panel="files"] .research-file-surface',
  );
  if (!plan || !runs || !review || !files) return;

  moveIfPresent("#tab-research > .research-focus-rail", plan);
  moveIfPresent("#tab-research > #experiment-workflow", plan);
  moveIfPresent("#workflow-experiment-library", runs);
  moveIfPresent("#workflow-result-actions", runs);
  moveIfPresent("#workflow-review-inbox", review);
  moveIfPresent("#workflow-human-review", review);
  moveIfPresent("#workflow-rq-proposal", review);

  for (const selector of [
    "#tab-research > #research-lanes",
    "#tab-research > .research-lanes",
    "#tab-research > .fm-toolbar",
    "#tab-research > .fm-breadcrumb",
    "#tab-research > .fm-filters",
    "#tab-research > .fm-layout",
  ]) {
    moveIfPresent(selector, files);
  }
}

function initResearchWorkspace() {
  if (researchWorkspaceReady) {
    routeResearchElements();
    return;
  }
  const root = document.getElementById("tab-research");
  const header = root?.querySelector(":scope > .workspace-header");
  if (!root || !header) return;
  installResearchWorkspaceStyle();

  const tabs = document.createElement("nav");
  tabs.className = "research-workspace-tabs";
  tabs.setAttribute("role", "tablist");
  tabs.setAttribute("aria-label", "Research Arbeitsbereiche");
  const definitions = [
    ["plan", "Planen & Ausführen"],
    ["runs", "Läufe & Reihen"],
    ["review", "Reviews"],
    ["files", "Dateien & Analyse"],
  ];
  for (const [key, label] of definitions) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.researchWorkspaceView = key;
    button.setAttribute("role", "tab");
    button.textContent = label;
    tabs.appendChild(button);
  }

  const shell = document.createElement("div");
  shell.className = "research-workspace-shell";
  const panels = {
    plan: [
      "Planen & Ausführen",
      "Forschungsfrage, Vertrag, Bedingungen und kontrollierter Experimentstart.",
    ],
    runs: [
      "Läufe & Reihen",
      "Aktive und ausgeblendete Experimente, Serienstatus und aktuelle Resultate.",
    ],
    review: [
      "Reviews",
      "Human Review, offene Interpretation und neue Forschungsfragen getrennt von Evidenz-Promotion.",
    ],
    files: [
      "Dateien & Analyse",
      "Kanonischer File Viewer, Evidenz, AIRR, Matrizen, Dokumentation und technische Analyse.",
    ],
  };
  for (const [key, [title, description]] of Object.entries(panels)) {
    const panel = document.createElement("section");
    panel.className = "research-workspace-panel";
    panel.dataset.researchWorkspacePanel = key;
    panel.setAttribute("role", "tabpanel");
    panel.appendChild(panelHeader(title, description));
    if (key === "files") {
      const surface = document.createElement("div");
      surface.className = "research-file-surface";
      panel.appendChild(surface);
    }
    shell.appendChild(panel);
  }
  header.insertAdjacentElement("afterend", tabs);
  tabs.insertAdjacentElement("afterend", shell);
  tabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-research-workspace-view]");
    if (button) selectResearchView(button.dataset.researchWorkspaceView);
  });
  researchWorkspaceReady = true;
  routeResearchElements();
  let initial = "plan";
  try {
    initial = localStorage.getItem(RESEARCH_VIEW_KEY) || initial;
  } catch (_) {
    // Preference persistence is optional.
  }
  selectResearchView(initial);
}

function scan() {
  scanQueued = false;
  initResearchWorkspace();
  routeResearchElements();
  let index = 0;
  document
    .querySelectorAll(`.tab-content ${BOX_SELECTOR}`)
    .forEach((box) => enhanceBox(box, index++));
}

function queueScan() {
  if (scanQueued) return;
  scanQueued = true;
  requestAnimationFrame(scan);
}

function restoreStandard() {
  const expanded = document.querySelector(".box-state-maximized");
  if (!expanded) return;
  const key = expanded.dataset.boxKey;
  setState(expanded, key, "standard");
  document.body.classList.remove("box-state-lock");
}

export function initBoxStates() {
  loadStates();
  scan();
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") restoreStandard();
  });
  const observer = new MutationObserver(queueScan);
  observer.observe(document.querySelector("main") || document.body, {
    childList: true,
    subtree: true,
  });
}
