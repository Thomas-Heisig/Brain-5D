"use strict";

import { initStatusBar } from "./components/status-bar.js";
import { initNotificationCenter } from "./components/notification-center.js";
import { initPanelHelp } from "./components/help.js";
import { initRuntimeIO } from "./modules/runtime-io.js";
import { initScienceTransparency } from "./modules/science-transparency.js";
import { initScientificMetrics } from "./modules/scientific-metrics.js";
import { startDataStyleObserver } from "./modules/data-styles.js";
import { initCognition } from "./modules/cognition.js";
import { initGatewayMonitor } from "./modules/gateway-monitor.js";
import { initDocsBrowser } from "./modules/docs-browser.js";
import { initResearchDocs } from "./modules/research-docs.js";
import { initAIReportTools } from "./modules/ai-report-tools.js";
import { initLearningPrep } from "./modules/learning-prep.js";
import { initStructuralInspector } from "./modules/structural-inspector.js";
import { initSystemInfo } from "./modules/system-info.js";
import { initSnapshotHistory } from "./modules/snapshot-history.js";
import { initReviewLink } from "./modules/review-link.js";
import { initOverviewSubtabs } from "./modules/overview-subtabs.js";
import { initResearchSubtabs } from "./modules/research-subtabs.js";
import { initWorkspaceRouter } from "./workspace-router.js";

function init() {
  initWorkspaceRouter();
  initStatusBar();
  initNotificationCenter();
  initPanelHelp();
  initRuntimeIO();
  initScienceTransparency();
  initScientificMetrics();
  startDataStyleObserver();
  initCognition();
  initGatewayMonitor();
  initDocsBrowser();
  initResearchDocs();
  initAIReportTools();
  initLearningPrep();
  initStructuralInspector();
  initSystemInfo();
  initSnapshotHistory();
  initReviewLink();
  initOverviewSubtabs();
  initResearchSubtabs();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => setTimeout(init, 0), { once: true });
} else {
  setTimeout(init, 0);
}

window.MHRNFrontend = { refresh: init };
