"use strict";
import { initStatusBar } from "./components/status-bar.js";
import { initNotificationCenter } from "./components/notification-center.js";
import { initPanelHelp } from "./components/help.js";
import { initRuntimeIO } from "./modules/runtime-io.js";
import { initScienceTransparency } from "./modules/science-transparency.js";
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

const AREA_COPY = {
  dashboard: { icon: "📊", title: "Dashboard", subtitle: "Operator · Systemzustand & Steuerung" },
  science: { icon: "🔬", title: "Wissenschaft", subtitle: "Research · Analyse & Evidenz" },
  wesen: { icon: "🧠", title: "Runtime & Wesen", subtitle: "Living System · Körper & Verhalten" },
};

function activateLegacyWorkspace(name) {
  const button = document.querySelector(`.tab-nav .tab-btn[data-tab="${name}"]`);
  if (button) button.click();
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

  const actions = document.createElement("div");
  actions.className = "mhrn-global-actions";
  actions.setAttribute("aria-label", "Globale Arbeitsbereiche");
  actions.innerHTML = `
    <button type="button" class="mhrn-global-route" data-global-workspace="gate" aria-label="Release öffnen"><strong>🚀 Release</strong><span>Gate & CI</span></button>
    <button type="button" class="mhrn-global-route" data-global-workspace="settings" aria-label="Settings öffnen"><strong>⚙ Settings</strong><span>Parameter</span></button>
    <a class="mhrn-review-route" href="/review" target="_blank" rel="noopener noreferrer" aria-label="Externes Review öffnen"><strong>↗ Review</strong><span>Prüferportal</span></a>`;

  nav.replaceChildren(areaTabs, actions);
  actions.addEventListener("click", (event) => {
    const button = event.target.closest("[data-global-workspace]");
    if (button) activateLegacyWorkspace(button.dataset.globalWorkspace);
  });
}

function syncGlobalNavigation() {
  const active = document.querySelector(".tab-content.active[id^='tab-']");
  const workspace = active?.id?.replace("tab-", "") || "overview";
  document.querySelectorAll("[data-global-workspace]").forEach((button) => {
    button.classList.toggle("active", button.dataset.globalWorkspace === workspace);
  });
}

function initVisualShell() {
  document.body.classList.add("mhrn-visual-shell-v2");
  decoratePrimaryNavigation();
  syncGlobalNavigation();

  document.addEventListener("click", (event) => {
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
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => setTimeout(init, 0), { once: true }); else setTimeout(init, 0);
window.MHRNFrontend = { refresh: init };
