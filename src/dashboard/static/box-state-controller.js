/* Responsive box states for the dashboard presentation layer. */
"use strict";

const STORAGE_KEY = "brain5d-box-states";
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
  ".experiment-workflow",
  ".release-board",
  ".connection-manager",
  ".embodiment-system-strip",
  ".embodiment-loop",
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
  ":scope > header",
].join(",");

let states = {};
let scanQueued = false;

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
  if (box.classList.contains("box-state-ready") || box.matches(EXCLUDED_SELECTOR) || isNestedBox(box)) return;
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

function scan() {
  scanQueued = false;
  let index = 0;
  document.querySelectorAll(`.tab-content ${BOX_SELECTOR}`).forEach((box) => enhanceBox(box, index++));
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
  observer.observe(document.querySelector("main") || document.body, { childList: true, subtree: true });
}
