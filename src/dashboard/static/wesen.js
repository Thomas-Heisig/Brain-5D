/* Brain-5D Wesen integration shell.
 * The existing adaptive Wesen implementation remains in wesen-base.js.
 * This shell merges the technical Embodiment surface into Wesen and keeps
 * Settings/Release as footer utilities instead of primary workspaces.
 */
import "./wesen-base.js";

function byId(id) {
  return document.getElementById(id);
}

function injectIntegrationStyles() {
  if (byId("wesen-integration-styles")) return;
  const style = document.createElement("style");
  style.id = "wesen-integration-styles";
  style.textContent = `
    .tab-nav .wesen-utility-hidden { display: none !important; }
    .wesen-technical-body { margin: 1.25rem 0 2rem; border: 1px solid var(--line, #1c4155); border-radius: 14px; overflow: clip; background: rgba(127,127,127,.035); }
    .wesen-technical-body > summary { cursor: pointer; padding: 1rem 1.15rem; display: flex; justify-content: space-between; gap: 1rem; align-items: center; list-style: none; }
    .wesen-technical-body > summary::-webkit-details-marker { display: none; }
    .wesen-technical-body > summary div { display: grid; gap: .2rem; }
    .wesen-technical-body > summary small { opacity: .68; }
    .wesen-technical-body-content { padding: 0 1rem 1rem; }
    .wesen-technical-body-content > .workspace-header { margin-top: .25rem; }
    .footer-tools { display: flex; gap: .45rem; align-items: center; }
    .footer-nav-btn { border: 1px solid var(--line, #1c4155); background: transparent; color: inherit; border-radius: 8px; padding: .45rem .7rem; cursor: pointer; font: inherit; }
    .footer-nav-btn:hover, .footer-nav-btn:focus-visible { background: rgba(127,127,127,.12); outline: none; }
    @media (max-width: 900px) { .footer-tools { width: 100%; justify-content: flex-end; } .wesen-technical-body > summary { align-items: flex-start; flex-direction: column; } }
  `;
  document.head.appendChild(style);
}

function mergeEmbodimentIntoWesen() {
  const wesen = byId("tab-wesen");
  const embodiment = byId("tab-embodiment");
  if (!wesen || !embodiment || embodiment.closest("#tab-wesen")) return;

  const details = document.createElement("details");
  details.className = "wesen-technical-body";
  details.innerHTML = `
    <summary>
      <div><span class="workspace-kicker">TECHNISCHE KÖRPERGRENZE</span><strong>Sensoren, Aktoren, Adapter & Runtime</strong></div>
      <small>einklappbar · Basis für kommende Embodiment-Generationen</small>
    </summary>`;

  embodiment.classList.remove("tab-content", "active");
  embodiment.classList.add("wesen-technical-body-content");
  embodiment.hidden = false;
  embodiment.removeAttribute("aria-hidden");
  details.appendChild(embodiment);
  wesen.appendChild(details);
}

function configurePrimaryNavigation() {
  const nav = document.querySelector(".tab-nav");
  if (!nav) return;

  const embodimentButton = nav.querySelector('.tab-btn[data-tab="embodiment"]');
  embodimentButton?.remove();

  for (const name of ["network", "settings", "gate"]) {
    const button = nav.querySelector(`.tab-btn[data-tab="${name}"]`);
    if (!button) continue;
    button.classList.add("wesen-utility-hidden");
    button.setAttribute("aria-hidden", "true");
    button.tabIndex = -1;
  }

  const bodyShortcut = document.querySelector('[data-overview-tab="embodiment"]');
  if (bodyShortcut) {
    bodyShortcut.dataset.overviewTab = "wesen";
    bodyShortcut.textContent = "◉ Wesen öffnen";
  }
}

function activateUtilityTab(name) {
  const hiddenButton = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  if (hiddenButton) hiddenButton.click();
}

function ensureFooterTools() {
  const footer = document.querySelector(".site-footer");
  if (!footer || footer.querySelector(".footer-tools")) return;
  const tools = document.createElement("div");
  tools.className = "footer-tools";
  tools.setAttribute("aria-label", "Systembereiche");
  tools.innerHTML = `
    <button type="button" class="footer-nav-btn" data-footer-tab="settings">⚙ Settings</button>
    <button type="button" class="footer-nav-btn" data-footer-tab="gate">🚀 Release</button>`;
  const health = byId("footer-status");
  if (health) health.insertBefore(tools, health.firstChild);
  else footer.appendChild(tools);
  tools.addEventListener("click", (event) => {
    const button = event.target.closest("[data-footer-tab]");
    if (button) activateUtilityTab(button.dataset.footerTab);
  });
}

function integrateShell() {
  injectIntegrationStyles();
  configurePrimaryNavigation();
  mergeEmbodimentIntoWesen();
  ensureFooterTools();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", integrateShell, { once: true });
} else {
  integrateShell();
}

window.Brain5DWesenIntegration = { refresh: integrateShell };
