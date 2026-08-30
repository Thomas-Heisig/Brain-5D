/**
 * Brain-5D Dashboard — Health / Problems Drawer
 *
 * Renders a persistent health bar and an expandable drawer with
 * errors, warnings, unavailable and stale component statuses.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = String(str);
  return div.innerHTML;
}

function statusClass(status) {
  switch (status) {
    case "error": return "health-error";
    case "degraded": return "health-warning";
    case "stale": return "health-stale";
    case "unavailable": return "health-unavailable";
    case "disabled": return "health-disabled";
    case "active":
    case "enabled":
      return "health-ok";
    default:
      return "health-unknown";
  }
}

/**
 * Health drawer UI controller.
 */
export class HealthDrawer {
  constructor(store) {
    this.store = store;
    this.drawer = byId("health-drawer");
    this.bar = byId("health-bar");
    this.toggleBtn = byId("health-toggle");
    this.problemList = byId("health-problem-list");
    this.componentList = byId("health-component-list");
    this.open = false;
    this.unsubscribe = null;

    this._initElements();
    this._bindEvents();
  }

  _initElements() {
    // Render health bar into the footer status container
    const footerStatus = byId("footer-status");
    if (!this.bar && footerStatus) {
      const bar = document.createElement("div");
      bar.id = "health-bar";
      bar.className = "health-bar";
      bar.innerHTML = `
        <span class="health-indicator" id="health-indicator"></span>
        <span class="health-summary" id="health-summary">—</span>
        <button class="health-toggle" id="health-toggle" aria-expanded="false">Problems</button>
      `;
      footerStatus.appendChild(bar);
      this.bar = bar;
      this.toggleBtn = byId("health-toggle");
    }

    if (!this.drawer) {
      const drawer = document.createElement("aside");
      drawer.id = "health-drawer";
      drawer.className = "health-drawer";
      drawer.innerHTML = `
        <div class="health-drawer__header">
          <h3>Health &amp; Problems</h3>
          <button class="health-drawer__close" id="health-drawer-close" aria-label="Close">&times;</button>
        </div>
        <div class="health-drawer__counts" id="health-counts"></div>
        <div class="health-drawer__section">
          <h4>Problems</h4>
          <div class="health-problem-list" id="health-problem-list"></div>
        </div>
        <div class="health-drawer__section">
          <h4>Runtime Errors</h4>
          <div class="health-runtime-list" id="health-runtime-list"></div>
        </div>
        <div class="health-drawer__section">
          <h4>Components</h4>
          <div class="health-component-list" id="health-component-list"></div>
        </div>
      `;
      document.body.appendChild(drawer);
      this.drawer = drawer;
      this.problemList = byId("health-problem-list");
      this.componentList = byId("health-component-list");
      this.runtimeList = byId("health-runtime-list");
    }

    const closeBtn = byId("health-drawer-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.closeDrawer());
    }
  }

  _bindEvents() {
    this.toggleBtn?.addEventListener("click", () => this.toggleDrawer());
    this.unsubscribe = this.store.subscribe((state) => this.render(state));
  }

  toggleDrawer() {
    this.open = !this.open;
    this.drawer?.classList.toggle("open", this.open);
    this.toggleBtn?.setAttribute("aria-expanded", String(this.open));
  }

  closeDrawer() {
    this.open = false;
    this.drawer?.classList.remove("open");
    this.toggleBtn?.setAttribute("aria-expanded", "false");
  }

  /**
   * Render health bar and drawer contents.
   * @param {object} state
   */
  render(state) {
    const health = state.health || {};
    const components = state.components || {};
    const overall = health.overall || "unknown";
    const problems = health.problems || [];
    const errors = health.errors || 0;
    const warnings = health.warnings || 0;
    const stale = health.stale || 0;
    const unavailable = health.unavailable || 0;
    const runtimeErrors = (state.structural_errors?.errors) || [];
    const runtimeErrorCount = runtimeErrors.length;

    // Update bar
    const indicator = byId("health-indicator");
    const summary = byId("health-summary");
    if (indicator) indicator.className = `health-indicator ${statusClass(overall)}`;
    if (summary) {
      const parts = [];
      if (errors) parts.push(`${errors} error${errors === 1 ? "" : "s"}`);
      if (warnings) parts.push(`${warnings} warning${warnings === 1 ? "" : "s"}`);
      if (stale) parts.push(`${stale} stale`);
      if (unavailable) parts.push(`${unavailable} unavailable`);
      if (runtimeErrorCount) parts.push(`${runtimeErrorCount} runtime error${runtimeErrorCount === 1 ? "" : "s"}`);
      summary.textContent = parts.length ? parts.join(" · ") : "Healthy";
    }

    // Update counts
    const counts = byId("health-counts");
    if (counts) {
      counts.innerHTML = `
        <span class="health-count health-count--error">${errors}</span>
        <span class="health-count health-count--warning">${warnings}</span>
        <span class="health-count health-count--stale">${stale}</span>
        <span class="health-count health-count--unavailable">${unavailable}</span>
      `;
    }

    // Update problem list
    if (this.problemList) {
      if (!problems.length) {
        this.problemList.innerHTML = `<div class="health-empty">No problems detected.</div>`;
      } else {
        this.problemList.innerHTML = problems.map((p) => `
          <div class="health-problem health-problem--${statusClass(p.status)}">
            <div class="health-problem__component">${escapeHtml(p.component)}</div>
            <div class="health-problem__status">${escapeHtml(p.status)}</div>
            <div class="health-problem__reason">${escapeHtml(p.reason)}</div>
            ${p.last_error ? `<div class="health-problem__error">${escapeHtml(p.last_error)}</div>` : ""}
          </div>
        `).join("");
      }
    }

    // Update runtime error list
    if (this.runtimeList) {
      if (!runtimeErrorCount) {
        this.runtimeList.innerHTML = `<div class="health-empty">No runtime errors recorded.</div>`;
      } else {
        this.runtimeList.innerHTML = runtimeErrors.map((e) => `
          <div class="health-problem health-problem--${e.fatal ? 'health-error' : 'health-warning'}">
            <div class="health-problem__component">Tick ${e.tick} · ${escapeHtml(e.phase)}</div>
            <div class="health-problem__status">${escapeHtml(e.exception_type)}</div>
            <div class="health-problem__reason">${escapeHtml(e.message)}</div>
            ${e.traceback_hash ? `<div class="health-problem__error">#${escapeHtml(e.traceback_hash)}</div>` : ""}
          </div>
        `).join("");
      }
    }

    // Update component list
    if (this.componentList) {
      const comps = Object.values(components).sort((a, b) => a.component.localeCompare(b.component));
      this.componentList.innerHTML = comps.map((c) => `
        <div class="health-component health-component--${statusClass(c.status)}">
          <span class="health-component__name">${escapeHtml(c.component)}</span>
          <span class="health-component__status">${escapeHtml(c.status)}</span>
          <span class="health-component__maturity">${escapeHtml(c.maturity)}</span>
        </div>
      `).join("");
    }
  }

  /**
   * Clean up subscriptions and DOM elements.
   */
  destroy() {
    this.unsubscribe?.();
  }
}

/**
 * Initialize the health drawer.
 * @param {DashboardStateStore} store
 */
export function initHealthDrawer(store) {
  return new HealthDrawer(store);
}
