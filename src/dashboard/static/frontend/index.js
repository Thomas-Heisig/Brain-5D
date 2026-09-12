"use strict";
import { initStatusBar } from "./components/status-bar.js";
import { initNotificationCenter } from "./components/notification-center.js";
import { initPanelHelp } from "./components/help.js";
import { initRuntimeIO } from "./modules/runtime-io.js";
import { initScienceTransparency } from "./modules/science-transparency.js";
import { initScientificMetrics } from "./modules/scientific-metrics.js";
import { initReviewLink } from "./modules/review-link.js";
import { startDataStyleObserver } from "./modules/data-styles.js";
import { initCognition } from "./modules/cognition.js";
import { initGatewayMonitor } from "./modules/gateway-monitor.js";
import { initDocsBrowser } from "./modules/docs-browser.js";
import { initResearchDocs } from "./modules/research-docs.js";
import { initAIReportTools } from "./modules/ai-report-tools.js";
import { initLearningPrep } from "./modules/learning-prep.js";
import { initStructuralInspector } from "./modules/structural-inspector.js";
import { initSystemInfo } from "./modules/system-info.js";
import { initOverviewSubtabs } from "./modules/overview-subtabs.js";
import { initResearchSubtabs } from "./modules/research-subtabs.js";

const AREA_COPY = {
  dashboard: { icon: "📊", title: "Dashboard", subtitle: "Operator · Systemzustand & Steuerung" },
  science: { icon: "🔬", title: "Wissenschaft", subtitle: "Research · Analyse & Evidenz" },
  wesen: { icon: "🧠", title: "Runtime & Wesen", subtitle: "Living System · Körper & Verhalten" },
};

function activateLegacyWorkspace(name) {
  const button = document.querySelector(`.tab-nav .tab-btn[data-tab="${name}"]`);
  if (!button) return false;
  // Directly switch the tab without relying on click() event delegation
  document.querySelectorAll(".tab-btn[data-tab]").forEach((item) => {
    item.classList.toggle("active", item === button);
  });
  document.querySelectorAll(".tab-content[id^='tab-']").forEach((tab) => {
    const selected = tab.id === `tab-${name}`;
    tab.classList.toggle("active", selected);
    tab.hidden = !selected;
  });
  document.body.dataset.currentTab = name;
  // Trigger lazy init via click, but after we've already set the correct state
  button.click();
  // Re-assert in the next frame to override any competing handlers
  requestAnimationFrame(() => {
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
  return true;
}

function decoratePrimaryNavigation() {
  const nav = document.querySelector(".brain5d-primary-nav");
  if (!nav || nav.dataset.visualShell === "v2") return;
  nav.dataset.visualShell = "v2";

  const areaButtons = Array.from(nav.querySelectorAll("button[data-primary-area]"));
  const areaTabs = document.createElement("div");
  areaTabs.className = "mhrn-area-tabs";
  for (const button of areaButtons) {
    const area = button.dataset.primaryArea;
    const copy = AREA_COPY[area];
    if (copy) {
      button.innerHTML = `
        <span class="mhrn-nav-icon" aria-hidden="true">${copy.icon}</span>
        <span class="mhrn-nav-copy"><strong>${copy.title}</strong><span>${copy.subtitle}</span></span>`;
    }
    areaTabs.appendChild(button);
  }

  const GLOBAL_ACTIONS = [
    { ws: "control", icon: "🎮", title: "Control", subtitle: "Runtime · Pacing · Experiment", label: "Control Workbench öffnen" },
    { ws: "gate", icon: "🚀", title: "Release", subtitle: "Gate & CI", label: "Release öffnen" },
    { ws: "settings", icon: "⚙", title: "Settings", subtitle: "Konfiguration", label: "Settings öffnen" },
    { ws: "parameter", icon: "🎛", title: "Parameter", subtitle: "Runtime-Parameter", label: "Parameter öffnen" },
    { ws: "review", icon: "↗", title: "Review", subtitle: "Prüferportal", label: "Review Portal öffnen" },
  ];

  const actions = document.createElement("div");
  actions.className = "mhrn-global-actions";
  actions.setAttribute("aria-label", "Globale Arbeitsbereiche");
  actions.innerHTML = GLOBAL_ACTIONS.map((a) =>
    `<button type="button" class="mhrn-global-route" data-global-workspace="${a.ws}" aria-label="${a.label}"><span class="mhrn-nav-icon" aria-hidden="true">${a.icon}</span><span class="mhrn-nav-copy"><strong>${a.title}</strong><span>${a.subtitle}</span></span></button>`
  ).join("");

  nav.replaceChildren(areaTabs, actions);
  actions.addEventListener("click", (event) => {
    const button = event.target.closest("[data-global-workspace]");
    if (!button) return;
    const ws = button.dataset.globalWorkspace;
    if (ws === "review") {
      window.open("/review", "_blank", "noopener,noreferrer");
      return;
    }
    if (ws === "parameter") {
      activateLegacyWorkspace("settings");
      document.body.dataset.globalWorkspace = "parameter";
      requestAnimationFrame(() => {
        const card = document.getElementById("parameter-inspector-card");
        if (card) {
          card.scrollIntoView({ behavior: "smooth", block: "start" });
          card.classList.add("parameter-highlight");
          setTimeout(() => card.classList.remove("parameter-highlight"), 2000);
        }
      });
      return;
    }
    delete document.body.dataset.globalWorkspace;
    activateLegacyWorkspace(ws);
  });
}

function syncGlobalNavigation() {
  const active = document.querySelector(".tab-content.active[id^='tab-']");
  const currentTab = active?.id?.replace("tab-", "") || "overview";
  const workspace = currentTab === "settings" && document.body.dataset.globalWorkspace === "parameter"
    ? "parameter"
    : currentTab;
  document.querySelectorAll("[data-global-workspace]").forEach((button) => {
    button.classList.toggle("active", button.dataset.globalWorkspace === workspace);
  });
}

function initVisualShell() {
  document.body.classList.add("mhrn-visual-shell-v2");
  decoratePrimaryNavigation();
  syncGlobalNavigation();

  document.addEventListener("click", (event) => {
    const globalButton = event.target.closest("[data-global-workspace]");
    if (!globalButton || globalButton.dataset.globalWorkspace !== "parameter") {
      delete document.body.dataset.globalWorkspace;
    }
    if (event.target.closest(".tab-btn[data-tab], [data-primary-area], [data-global-workspace], [data-science-route]")) {
      requestAnimationFrame(syncGlobalNavigation);
    }
  });
}

function init() {
  initVisualShell();
  initStatusBar();
  initNotificationCenter();
  initPanelHelp();
  initRuntimeIO();
  initScienceTransparency();
  initScientificMetrics();
  initReviewLink();
  startDataStyleObserver();
  initCognition();
  initGatewayMonitor();
  initDocsBrowser();
  initResearchDocs();
  initAIReportTools();
  initLearningPrep();
  initStructuralInspector();
  initSystemInfo();
  initOverviewSubtabs();
  initResearchSubtabs();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => setTimeout(init, 0), { once: true }); else setTimeout(init, 0);
window.MHRNFrontend = { refresh: init };
