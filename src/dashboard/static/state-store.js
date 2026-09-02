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
      gate: {},
      research: {},
      experiment_state: {},
      embodiment: {},
      embodiment_detail: {},
      embodiment_history: {},
      embodiment_connections: {},
      components: {},
      parameters: {},
      pending_changes: {},
      change_history: [],
      system: {},
      structural_errors: { errors: [] },
      status: "idle",
      version: "unknown",
    };
    this.subscribers = [];
    this.pollTimer = null;
    this.lastError = null;
    this.fetching = false;
    this.lastSupplementalFetch = 0;
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
        ...(payload.runtime || {}),
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
      gate: this.state.gate || {},
      research: this.state.research || {},
      experiment_state: payload.experiment_state || this.state.experiment_state || {},
      embodiment: payload.embodiment || {},
      embodiment_detail: this.state.embodiment_detail || {},
      embodiment_history: this.state.embodiment_history || {},
      embodiment_connections: this.state.embodiment_connections || {},
      components: payload.components || {},
      parameters: payload.parameters || {},
      pending_changes: payload.pending_changes || {},
      change_history: payload.change_history || [],
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

      if (Date.now() - this.lastSupplementalFetch >= 15000) {
        const [gateResult, modeResult, researchResult, embodimentResult, embodimentHistoryResult, connectionResult, pipelineResult] = await Promise.allSettled([
          fetch("/api/gate/status", { cache: "no-store" }),
          fetch("/api/experiment/mode", { cache: "no-store" }),
          fetch("/api/research", { cache: "no-store" }),
          fetch("/api/embodiment/state", { cache: "no-store" }),
          fetch("/api/embodiment/history?limit=100", { cache: "no-store" }),
          fetch("/api/embodiment/connections", { cache: "no-store" }),
          fetch("/api/embodiment/pipeline", { cache: "no-store" }),
        ]);
        if (gateResult.status === "fulfilled" && gateResult.value.ok) {
          this.state.gate = await gateResult.value.json();
        }
        if (modeResult.status === "fulfilled" && modeResult.value.ok) {
          const modeData = await modeResult.value.json();
          this.state.experiment_state = {
            ...this.state.experiment_state,
            ...modeData,
          };
        }
        if (researchResult.status === "fulfilled" && researchResult.value.ok) {
          this.state.research = await researchResult.value.json();
        }
        if (embodimentResult.status === "fulfilled" && embodimentResult.value.ok) {
          this.state.embodiment_detail = await embodimentResult.value.json();
        }
        if (embodimentHistoryResult.status === "fulfilled" && embodimentHistoryResult.value.ok) {
          this.state.embodiment_history = await embodimentHistoryResult.value.json();
        }
        if (connectionResult.status === "fulfilled" && connectionResult.value.ok) {
          this.state.embodiment_connections = await connectionResult.value.json();
        }
        if (pipelineResult.status === "fulfilled" && pipelineResult.value.ok) {
          this.state.embodiment_detail = {
            ...this.state.embodiment_detail,
            pipeline: await pipelineResult.value.json(),
          };
        }
        this.lastSupplementalFetch = Date.now();
      }

      // Fetch runtime structural errors for health drawer visibility
      try {
        const errorsRes = await fetch("/api/structural/errors", { cache: "no-store" });
        if (errorsRes.ok) {
          const errorsData = await errorsRes.json();
          this.state.structural_errors = { errors: errorsData.errors || [] };
        }
      } catch (e) {
        // ignore — errors endpoint is optional
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
