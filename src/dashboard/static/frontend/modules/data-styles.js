"use strict";

/**
 * Data-attribute → CSS property bridge.
 *
 * After refactoring inline styles out of HTML/JS templates, some elements
 * carry their dynamic values in data-* attributes instead. This module
 * translates them into CSS custom properties so stylesheets can consume
 * them without any inline style= attribute.
 *
 * Call applyDataStyles(root) after any innerHTML replacement.
 */

const MAP = [
  { attr: "data-left",            prop: "left",             unit: "%",   selector: ".development-scale-tick, .development-scale-marker" },
  { attr: "data-marker-position", prop: "--marker-position", unit: "%", selector: ".development-marker" },
  { attr: "data-conf",            prop: "--conf",            unit: "%", selector: ".proposal-conf" },
  { attr: "data-empirical-fill",  prop: "--empirical-fill",  unit: "%", selector: ".wesen-empirical-row" },
  { attr: "data-opacity",         prop: "opacity",           unit: "",   selector: ".wesen-self-body" },
  { attr: "data-width",           prop: "width",             unit: "%",  selector: ".population-bar-fill" },
  { attr: "data-color",           prop: "background",        unit: "",   selector: ".population-bar-fill" },
];

export function applyDataStyles(root = document) {
  for (const { attr, prop, unit, selector } of MAP) {
    root.querySelectorAll(`${selector}[${attr}]`).forEach((el) => {
      const value = el.getAttribute(attr);
      if (value !== null) el.style.setProperty(prop, value + unit);
    });
  }
}

/** MutationObserver that auto-applies data styles on DOM changes. */
let observer = null;

export function startDataStyleObserver() {
  if (observer) return;
  observer = new MutationObserver(() => applyDataStyles());
  observer.observe(document.body, { childList: true, subtree: true });
  // Initial pass
  applyDataStyles();
}

export function stopDataStyleObserver() {
  if (observer) { observer.disconnect(); observer = null; }
}
