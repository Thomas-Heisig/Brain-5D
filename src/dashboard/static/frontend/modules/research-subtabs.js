/**
 * MHRN Dashboard — Research Sub-Tabs
 *
 * Switches between Experiments / Files / Registry
 * panels inside the Research tab.
 */

"use strict";

export function initResearchSubtabs() {
  const subtabBar = document.querySelector(".research-subtabs");
  if (!subtabBar || subtabBar.dataset.initialised === "true") return;
  subtabBar.dataset.initialised = "true";

  const tabs = Array.from(subtabBar.querySelectorAll(".research-subtab"));
  const panels = Array.from(document.querySelectorAll("#tab-research .research-subpanel"));

  subtabBar.addEventListener("click", (event) => {
    const tab = event.target.closest(".research-subtab");
    if (!tab) return;

    const target = tab.dataset.subtab;

    tabs.forEach((t) => {
      const active = t === tab;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", String(active));
    });

    panels.forEach((p) => {
      const active = p.dataset.subpanel === target;
      p.classList.toggle("active", active);
      p.hidden = !active;
    });
  });
}
