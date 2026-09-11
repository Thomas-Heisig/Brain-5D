"use strict";
import { initStatusBar } from "./components/status-bar.js";
import { initNotificationCenter } from "./components/notification-center.js";
import { initPanelHelp } from "./components/help.js";
import { initRuntimeIO } from "./modules/runtime-io.js";
import { initScienceTransparency } from "./modules/science-transparency.js";
import { initReviewLink } from "./modules/review-link.js";

function init() {
  initStatusBar();
  initNotificationCenter();
  initPanelHelp();
  initRuntimeIO();
  initScienceTransparency();
  initReviewLink();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => setTimeout(init, 0), { once: true }); else setTimeout(init, 0);
window.MHRNFrontend = { refresh: init };
