/**
 * Brain-5D Dashboard — Central Frontend State Store
 *
 * Replaces panel-individual fetch calls with a single source of truth.
 * Polls /api/status, /api/components, /api/parameters and /api/health
 * and notifies subscribers.  Domain modules subscribe to this store instead
 * of calling fetch themselves.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

const POLL_INTERVAL_MS = 1000;

/**
 * Deep-merge two objects (shallow merge for arrays).
 * @param {object} target
 * @param {object} source
 */
function merge(target, source) {
  for (const key of Object.keys(source)) {
    const val = source[key];
    if (val && typeof val === "object" && !Array.isArray(val)) {
      target[key] = merge(target[key] || {}, val);
    } else {
      target[key] = val;
    }
  }
  return target;
}

/**
 * Central dashboard state store.
 */
export class DashboardStateStore {
  constructor() {
    this.state = {
      runtime: {},
      network: {},
      learning: {},
      homeostasis: {},
      structural: {},
      storage: {},
      telemetry: {},
      health: {},
      verification: {},
      components: {},
      parameters: {},
      system: {},
      status: "idle",
      version: "unknown",
    };
    this.subscribers = [];
    this.pollTimer = null;
    this.lastError = null;
    this.fetching = false;
  }

  /**
   * Subscribe to state changes.
   * @param {(state: object) => void} callback
   * @returns {() => void} unsubscribe function
   */
  subscribe(callback) {
    this.subscribers.push(callback);
    callback(this.state);
    return () => {
      const idx = this.subscribers.indexOf(callback);
      if (idx >= 0) this.subscribers.splice(idx, 1);
    };
  }

  /**
   * Notify all subscribers.
   * @private
   */
  _notify() {
    for (const fn of this.subscribers) {
      try {
        fn(this.state);
      } catch (e) {
        console.error("State subscriber failed:", e);
      }
    }
  }

  /**
   * Update state from a status payload.
   * @param {object} payload
   * @private
   */
  _updateFromStatus(payload) {
    const next = {
      status: payload.status || this.state.status,
      version: payload.version || this.state.version,
      system: payload.system || {},
      runtime: {
        tick: payload.system?.tick ?? this.state.runtime.tick,
        neurons: payload.system?.neurons ?? this.state.runtime.neurons,
        synapses: payload.system?.synapses ?? this.state.runtime.synapses,
        status: payload.status ?? this.state.runtime.status,
      },
      network: payload.network || {},
      learning: payload.learning || {},
      homeostasis: payload.homeostasis || {},
      structural: payload.structural || {},
      storage: payload.storage || {},
      telemetry: {
        tick: payload.system?.tick ?? this.state.telemetry.tick,
        core_step_ms: payload.system?.core_step_ms ?? this.state.telemetry.core_step_ms,
      },
      health: payload.health || {},
      verification: payload.verification || {},
      components: payload.components || {},
      parameters: payload.parameters || {},
    };
    this.state = next;
  }

  /**
   * Fetch fresh state from all backend endpoints.
   * @private
   */
  async _fetch() {
    if (this.fetching) return;
    this.fetching = true;
    try {
      const statusRes = await fetch("/api/status", { cache: "no-store" });
      if (!statusRes.ok) throw new Error(`HTTP ${statusRes.status}`);
      const status = await statusRes.json();
      this._updateFromStatus(status);

      // Health and components may already be embedded; if not, fetch them.
      if (!this.state.health || !this.state.health.problems) {
        try {
          const healthRes = await fetch("/api/health", { cache: "no-store" });
          if (healthRes.ok) {
            this.state.health = await healthRes.json();
          }
        } catch (e) {
          // ignore — status already has best-effort health
        }
      }
      if (!this.state.components || Object.keys(this.state.components).length === 0) {
        try {
          const compRes = await fetch("/api/components", { cache: "no-store" });
          if (compRes.ok) {
            const compData = await compRes.json();
            this.state.components = compData.components || {};
          }
        } catch (e) {
          // ignore
        }
      }
      if (!this.state.parameters || Object.keys(this.state.parameters).length === 0) {
        try {
          const paramRes = await fetch("/api/parameters", { cache: "no-store" });
          if (paramRes.ok) {
            const paramData = await paramRes.json();
            this.state.parameters = paramData.parameters || {};
          }
        } catch (e) {
          // ignore
        }
      }

      this.lastError = null;
      this._notify();
    } catch (error) {
      this.lastError = String(error);
      this._notify();
    } finally {
      this.fetching = false;
    }
  }

  /**
   * Start polling the backend.
   */
  start() {
    if (this.pollTimer) return;
    this._fetch();
    this.pollTimer = setInterval(() => this._fetch(), POLL_INTERVAL_MS);
  }

  /**
   * Stop polling the backend.
   */
  stop() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  /**
   * Force an immediate refresh.
   */
  refresh() {
    return this._fetch();
  }
}

/**
 * Shared singleton store instance.
 */
export const dashboardStore = new DashboardStateStore();
