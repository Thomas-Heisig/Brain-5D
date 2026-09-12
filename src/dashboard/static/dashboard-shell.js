const TAB_META = {
  overview: { kicker: "SYSTEM", title: "Overview", context: "Live system state, health and scientific status" },
  network: { kicker: "OBSERVE", title: "Network", context: "Neural dynamics, topology and data inspection" },
  control: { kicker: "OPERATE", title: "Control", context: "Runtime, pacing, experiments and approvals" },
  research: { kicker: "EVIDENCE", title: "Research", context: "Experiments, provenance, files and scientific evidence" },
  gate: { kicker: "VERIFY", title: "Release", context: "Scientific gate, CI evidence and release readiness" },
  settings: { kicker: "CONFIGURE", title: "Settings", context: "Runtime-visible configuration and operator preferences" },
  embodiment: { kicker: "EMBODY", title: "Embodiment", context: "Observed body, devices, interoception and feedback" },
};

function ensureStylesheet() {
  // The canonical stylesheet imports the shell layer once.
}

function currentTab() {
  const active = document.querySelector(".tab-content.active[id^='tab-']");
  return active?.id?.replace("tab-", "") || "overview";
}

function fitCanvas(canvas) {
  if (!(canvas instanceof HTMLCanvasElement)) return;
  const ratio = canvas.height / Math.max(canvas.width, 1);
  canvas.style.width = "100%";
  canvas.style.height = `${Math.max(160, canvas.clientWidth * ratio)}px`;
}

function fitVisibleCanvases(root = document) {
  root.querySelectorAll("canvas").forEach(fitCanvas);
}

function ensureWorkspaceHeaders() {
  // Workspace headers removed — sidebar provides all navigation context.
}

function addUtilityBars() {
  // Utility bars removed — sidebar provides all navigation and context.
}

function refreshReadOnlyData() {
  window.dispatchEvent(new CustomEvent("brain5d:dashboard-refresh", { detail: { tab: currentTab() } }));
  document.querySelector(`.tab-btn[data-tab="${currentTab()}"]`)?.click();
}

function bindUtilityActions() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-dashboard-action]");
    if (!button) return;
    const action = button.dataset.dashboardAction;
    if (action === "top") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    if (action === "density") {
      const compact = document.body.dataset.dashboardDensity === "compact";
      document.body.dataset.dashboardDensity = compact ? "comfortable" : "compact";
      document.querySelectorAll('[data-dashboard-action="density"]').forEach((item) => {
        item.textContent = compact ? "Compact" : "Comfortable";
      });
      localStorage.setItem("brain5d-dashboard-density", document.body.dataset.dashboardDensity);
      fitVisibleCanvases(document.querySelector(".tab-content.active") || document);
      return;
    }
    if (action === "refresh") refreshReadOnlyData();
  });
}

function bindTabResponsiveness() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      requestAnimationFrame(() => {
        const tab = document.getElementById(`tab-${button.dataset.tab}`);
        if (tab) fitVisibleCanvases(tab);
      });
    });
  });

  let resizeTimer = null;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => fitVisibleCanvases(document.querySelector(".tab-content.active") || document), 80);
  });
}

function restorePreferences() {
  document.body.dataset.dashboardDensity = localStorage.getItem("brain5d-dashboard-density") || "comfortable";
}

function init() {
  ensureStylesheet();
  restorePreferences();
  ensureWorkspaceHeaders();
  addUtilityBars();
  bindUtilityActions();
  bindTabResponsiveness();
  fitVisibleCanvases(document.querySelector(".tab-content.active") || document);
}

ensureStylesheet();
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}
