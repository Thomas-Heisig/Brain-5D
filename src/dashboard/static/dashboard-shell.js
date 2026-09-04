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
  if (document.querySelector('link[data-dashboard-shell="true"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/dashboard-shell.css";
  link.dataset.dashboardShell = "true";
  document.head.appendChild(link);
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
  Object.entries(TAB_META).forEach(([tabName, meta]) => {
    const tab = document.getElementById(`tab-${tabName}`);
    if (!tab) return;
    tab.classList.add("dashboard-workspace");
    if (tab.querySelector(":scope > .workspace-header, :scope > .overview-command-bar, :scope > .dashboard-generated-header")) return;

    const header = document.createElement("header");
    header.className = "dashboard-generated-header";
    header.dataset.workspace = tabName;
    header.innerHTML = `
      <div>
        <span class="dashboard-workspace-kicker">${meta.kicker}</span>
        <h2>${meta.title}</h2>
        <p>${meta.context}</p>
      </div>`;
    tab.prepend(header);
  });
}

function addUtilityBars() {
  Object.keys(TAB_META).forEach((tabName) => {
    const tab = document.getElementById(`tab-${tabName}`);
    if (!tab || tab.querySelector(":scope > .dashboard-utility-bar")) return;

    const header = tab.querySelector(":scope > .workspace-header, :scope > .overview-command-bar, :scope > .dashboard-generated-header");
    if (!header) return;

    const bar = document.createElement("div");
    bar.className = "dashboard-utility-bar";
    bar.innerHTML = `
      <span class="dashboard-utility-context" data-dashboard-context>${TAB_META[tabName].context}</span>
      <div class="dashboard-utility-actions">
        <button type="button" class="dashboard-utility-button" data-dashboard-action="refresh">↻ Refresh</button>
        <button type="button" class="dashboard-utility-button" data-dashboard-action="density">Compact</button>
        <button type="button" class="dashboard-utility-button" data-dashboard-action="top">↑ Top</button>
      </div>`;
    header.insertAdjacentElement("afterend", bar);
  });
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
