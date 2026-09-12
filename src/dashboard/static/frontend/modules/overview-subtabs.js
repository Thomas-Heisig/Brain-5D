/**
 * MHRN Dashboard — Overview Sub-Tabs
 *
 * Switches between Vitals / Organe / Gedächtnis / Struktur / Snapshot
 * panels inside the Overview tab.
 */

"use strict";

export function initOverviewSubtabs() {
  const subtabBar = document.querySelector(".overview-subtabs");
  if (!subtabBar || subtabBar.dataset.initialised === "true") return;
  subtabBar.dataset.initialised = "true";

  const tabs = Array.from(subtabBar.querySelectorAll(".overview-subtab"));
  const panels = Array.from(document.querySelectorAll(".overview-subpanel"));

  subtabBar.addEventListener("click", (event) => {
    const tab = event.target.closest(".overview-subtab");
    if (!tab) return;

    const target = tab.dataset.subtab;

    tabs.forEach((t) => {
      const active = t === tab;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", String(active));
    });

    panels.forEach((p) => {
      p.classList.toggle("active", p.dataset.subpanel === target);
    });
  });
}
