"use strict";

const BOX_STATE_KEY = "brain5d.box-controls.v1";
const BOX_SELECTOR = [
  ".card",
  ".panel",
  ".control-card",
  ".overview-surface",
  ".snapshot-info-card",
  ".settings-section",
  ".parameter-inspector-card",
  ".structural-live-card",
  ".wesen-card",
  ".wesen-stage-card",
  ".wesen-console",
  ".wesen-technical-body",
  ".embodiment-loop",
  ".anatomy-inner",
  ".organ-panel",
  ".release-summary-panel",
  ".project-timeline",
  ".release-tree",
  ".gate-section",
  ".settings-guardrail-grid",
  ".settings-mode-selector",
  ".settings-domain-filter",
  ".settings-note",
  ".release-summary-status",
  ".release-summary-metrics",
  ".gate-overall-grid",
].join(",");

let boxState = { minimized: {}, maximized: null };
let boxSequence = 0;

function loadState() {
  try {
    const stored = JSON.parse(localStorage.getItem(BOX_STATE_KEY) || "{}");
    if (stored && typeof stored === "object") {
      boxState = {
        minimized: stored.minimized && typeof stored.minimized === "object" ? stored.minimized : {},
        maximized: typeof stored.maximized === "string" ? stored.maximized : null,
      };
    }
  } catch (_) {
    boxState = { minimized: {}, maximized: null };
  }
}

function saveState() {
  try {
    localStorage.setItem(BOX_STATE_KEY, JSON.stringify(boxState));
  } catch (_) {
    // Local persistence is optional; the controls still work for the session.
  }
}

function stableKey(box) {
  if (box.dataset.boxControlId) return box.dataset.boxControlId;
  const explicit = box.id || box.dataset.wesenPanel || box.dataset.releasePanel;
  if (explicit) {
    box.dataset.boxControlId = `box:${explicit}`;
    return box.dataset.boxControlId;
  }
  boxSequence += 1;
  box.dataset.boxControlId = `box:auto-${boxSequence}`;
  return box.dataset.boxControlId;
}

function updateButtons(box) {
  const minimized = box.classList.contains("b5d-box-minimized");
  const maximized = box.classList.contains("b5d-box-maximized");
  const minimizeButton = box.querySelector("[data-box-action='minimize']");
  const maximizeButton = box.querySelector("[data-box-action='maximize']");
  if (minimizeButton) {
    minimizeButton.textContent = minimized ? "+" : "−";
    minimizeButton.title = minimized ? "Box wiederherstellen" : "Box minimieren";
    minimizeButton.setAttribute("aria-label", minimizeButton.title);
  }
  if (maximizeButton) {
    maximizeButton.textContent = maximized ? "↙" : "↗";
    maximizeButton.title = maximized ? "Box wieder verkleinern" : "Box maximieren";
    maximizeButton.setAttribute("aria-label", maximizeButton.title);
  }
  box.setAttribute("aria-expanded", String(!minimized));
}

function setMaximized(box, value) {
  const key = stableKey(box);
  if (value) {
    document.querySelectorAll(".b5d-box-maximized").forEach((other) => {
      if (other !== box) {
        other.classList.remove("b5d-box-maximized");
        updateButtons(other);
      }
    });
    box.classList.add("b5d-box-maximized");
    boxState.maximized = key;
  } else {
    box.classList.remove("b5d-box-maximized");
    if (boxState.maximized === key) boxState.maximized = null;
  }
  saveState();
  updateButtons(box);
}

function toggleMinimized(box) {
  const key = stableKey(box);
  const minimized = box.classList.toggle("b5d-box-minimized");
  boxState.minimized[key] = minimized;
  if (minimized && box.classList.contains("b5d-box-maximized")) setMaximized(box, false);
  saveState();
  updateButtons(box);
}

function attachBox(box) {
  if (!(box instanceof HTMLElement) || box.dataset.boxControls === "true") return;
  if (box.closest("dialog")?.classList.contains("gate-detail-dialog")) return;
  const key = stableKey(box);
  box.dataset.boxControls = "true";
  box.classList.add("b5d-box-controlled");
  const controls = document.createElement("div");
  controls.className = "b5d-box-controls";
  controls.innerHTML = `
    <button type="button" data-box-action="minimize" title="Box minimieren" aria-label="Box minimieren">−</button>
    <button type="button" data-box-action="maximize" title="Box maximieren" aria-label="Box maximieren">↗</button>`;
  controls.addEventListener("click", (event) => {
    const action = event.target.closest("[data-box-action]")?.dataset.boxAction;
    if (action === "minimize") toggleMinimized(box);
    if (action === "maximize") setMaximized(box, !box.classList.contains("b5d-box-maximized"));
  });
  box.prepend(controls);
  if (boxState.minimized[key]) box.classList.add("b5d-box-minimized");
  if (boxState.maximized === key) box.classList.add("b5d-box-maximized");
  updateButtons(box);
}

function scanBoxes(root = document) {
  root.querySelectorAll(BOX_SELECTOR).forEach(attachBox);
}

function initBoxControls() {
  loadState();
  scanBoxes();
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => mutation.addedNodes.forEach((node) => {
      if (node instanceof HTMLElement) {
        if (node.matches(BOX_SELECTOR)) attachBox(node);
        scanBoxes(node);
      }
    }));
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

export { initBoxControls };
