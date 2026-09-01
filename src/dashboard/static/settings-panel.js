/**
 * Scientific Settings tab coordinator.
 * Reuses the canonical ParameterInspector and its pending-change workflow.
 */

"use strict";

import { ExperimentAPI } from "./experiment-mode.js";

export class SettingsPanel {
  constructor(parameterInspector) {
    this.parameterInspector = parameterInspector;
    this.filterRoot = document.getElementById("settings-domain-filter");
    this.search = document.getElementById("parameter-search");
    this._bindFilters();
    this._bindModes();
  }

  _bindModes() {
    const selector = document.getElementById("settings-mode-selector");
    selector?.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-settings-mode]");
      if (!button) return;
      const mode = button.dataset.settingsMode;
      if (!mode) return;
      try {
        await ExperimentAPI.setMode(mode);
        document.getElementById("settings-mode").textContent = mode;
        selector.querySelectorAll("[data-settings-mode]").forEach((item) => {
          item.classList.toggle("active", item === button);
        });
        document.querySelectorAll("#experiment-mode-switcher .mode-btn").forEach((item) => {
          item.classList.toggle("active", item.dataset.mode === mode);
        });
      } catch (error) {
        console.error("Failed to set experiment mode:", error);
      }
    });
  }

  _bindFilters() {
    this.filterRoot?.addEventListener("click", (event) => {
      const button = event.target.closest("[data-settings-filter]");
      if (!button || !this.search) return;
      this.filterRoot.querySelectorAll("[data-settings-filter]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      this.search.value = button.dataset.settingsFilter || "";
      this.search.dispatchEvent(new Event("input", { bubbles: true }));
    });
  }

  refresh() {
    return this.parameterInspector.refresh();
  }
}
