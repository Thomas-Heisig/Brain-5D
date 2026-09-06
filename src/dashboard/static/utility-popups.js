"use strict";

const UTILITY_POPUPS = {
  gate: { kicker: "VERIFY", title: "Release" },
  settings: { kicker: "CONFIGURE", title: "Scientific Settings" },
};

const popupState = new Map();

function restoreTab(name) {
  const button = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (button) button.click();
}

function closePopup(name) {
  const state = popupState.get(name);
  if (!state || !state.dialog.open) return;
  state.dialog.close();
}

function openPopup(name) {
  const state = popupState.get(name);
  if (!state || state.dialog.open) return;
  state.restoreTab = document.body.dataset.currentTab || "overview";
  restoreTab(name);
  state.dialog.showModal();
}

function setReleaseView(section, view) {
  section.querySelectorAll("[data-utility-release-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.utilityReleaseView === view);
  });
  section.querySelectorAll("[data-release-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.releasePanel !== view;
  });
}

function createPopup(name, metadata) {
  const section = document.getElementById(`tab-${name}`);
  if (!section || !section.parentElement) return;

  const dialog = document.createElement("dialog");
  dialog.id = `${name}-utility-popup`;
  dialog.className = "utility-popup";
  dialog.setAttribute("aria-labelledby", `${name}-utility-popup-title`);
  dialog.innerHTML = `
    <div class="utility-popup-frame">
      <header class="utility-popup-header">
        <div><span class="workspace-kicker">${metadata.kicker}</span><h2 id="${name}-utility-popup-title">${metadata.title}</h2></div>
        <button type="button" class="modal-close" data-utility-popup-close aria-label="${metadata.title} schliessen">&times;</button>
      </header>
    </div>`;

  const frame = dialog.querySelector(".utility-popup-frame");
  section.classList.add("utility-popup-content");
  frame.appendChild(section);
  document.body.appendChild(dialog);

  const state = { dialog, restoreTab: "overview" };
  popupState.set(name, state);
  const releaseViews = section.querySelector("[data-utility-release-views]");
  releaseViews?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-utility-release-view]");
    if (button) setReleaseView(section, button.dataset.utilityReleaseView);
  });
  dialog.querySelector("[data-utility-popup-close]").addEventListener("click", () => closePopup(name));
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closePopup(name);
  });
  dialog.addEventListener("close", () => {
    section.hidden = true;
    section.classList.remove("active");
    if (state.restoreTab && state.restoreTab !== name) restoreTab(state.restoreTab);
  });
}

function initUtilityPopups() {
  Object.entries(UTILITY_POPUPS).forEach(([name, metadata]) => createPopup(name, metadata));
  window.Brain5DUtilityPopups = { open: openPopup, close: closePopup };
}

export { initUtilityPopups, openPopup };
