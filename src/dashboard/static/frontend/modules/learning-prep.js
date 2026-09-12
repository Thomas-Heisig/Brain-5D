"use strict";

import { apiGet, apiPost } from "../core/api.js";

let refreshTimer = null;

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value === null || value === undefined ? "" : String(value);
  return span.innerHTML;
}

function planIdDefault() {
  const stamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  return `LP-${stamp}`;
}

function ensurePanel() {
  let panel = document.getElementById("mhrn-learning-prep");
  if (panel) return panel;
  const workspace = document.getElementById("tab-control");
  if (!workspace) return null;
  panel = document.createElement("section");
  panel.id = "mhrn-learning-prep";
  panel.className = "mhrn-learning-prep card";
  panel.dataset.panelInfo = "Nicht-ausführende Lernvorbereitung. Create und Approve erzeugen Proposal-/Approval-Artefakte; sie setzen weder Gewichte noch Rewards oder Spikes.";
  panel.innerHTML = `
    <header><div><span class="workspace-kicker">LEARNING PREPARATION · GUARDED</span><h2>Lern-Vorbereitung</h2><p>Planen und freigeben, ohne Lernen auszuführen. Die produktive Ausführungsgrenze bleibt separat.</p></div><span id="learning-prep-badge" class="maturity-state pending">lade …</span></header>
    <div class="learning-prep-boundary"><strong>Grenze</strong><span>Dieser Bereich erzeugt ausschließlich Proposals und Approval-Metadaten. Keine direkte Gewichts-, Spike-, Current- oder Reward-Manipulation.</span></div>
    <div class="learning-prep-grid">
      <section class="learning-prep-section"><h3>Vorhandene Pläne</h3><div id="learning-prep-detail" class="learning-prep-detail">lade …</div></section>
      <section class="learning-prep-section"><h3>Proposal erstellen</h3><form id="learning-prep-create-form" class="learning-prep-form">
        <label>Plan-ID<input id="learning-plan-id" required value="${planIdDefault()}"></label><label>Objective-ID<input id="learning-objective-id" required value="OBJ-001"></label>
        <label class="learning-prep-wide">Zielbeschreibung<textarea id="learning-objective-description" required rows="2" placeholder="Kontrolliert prüfbares Lernziel"></textarea></label>
        <label>Success Metric<input id="learning-success-metric" required placeholder="holdout success"></label><label>Evaluation Question<input id="learning-evaluation-question" required placeholder="Does performance improve?"></label>
        <label>Source-ID<input id="learning-source-id" required value="SRC-001"></label><label>Source Digest<input id="learning-source-digest" required placeholder="sha256 / provenance digest"></label>
        <label>Origin<input id="learning-source-origin" required value="environment"></label><label>Partition<input id="learning-source-partition" required value="train"></label>
        <label>Baseline Protocol<input id="learning-baseline-protocol" required value="baseline"></label><label>Exposure Protocol<input id="learning-exposure-protocol" required value="exposure"></label>
        <label>Evaluation Protocol<input id="learning-evaluation-protocol" required value="holdout"></label><label>Stopping Rule<input id="learning-stopping-rule" required value="fixed episodes"></label>
        <label class="learning-prep-wide">Controls<input id="learning-controls" required value="learning_off" placeholder="learning_off, shuffled"></label><button type="submit" class="btn-primary">Proposal speichern</button>
      </form><div id="learning-prep-create-result" class="learning-prep-result" aria-live="polite"></div></section>
      <section class="learning-prep-section"><h3>Human Approval</h3><form id="learning-prep-approve-form" class="learning-prep-form learning-prep-approve-form"><label>Plan-ID<input id="learning-approve-plan-id" required placeholder="LP-..."></label><label>Freigegeben durch<input id="learning-approved-by" required placeholder="Operator / Reviewer"></label><button type="submit" class="btn-success">Plan freigeben</button></form><div id="learning-prep-approve-result" class="learning-prep-result" aria-live="polite"></div></section>
    </div>`;
  const anchor = workspace.querySelector(":scope > header");
  if (anchor) anchor.insertAdjacentElement("afterend", panel); else workspace.prepend(panel);
  panel.querySelector("#learning-prep-create-form")?.addEventListener("submit", createProposal);
  panel.querySelector("#learning-prep-approve-form")?.addEventListener("submit", approveProposal);
  return panel;
}

function value(id) { return document.getElementById(id)?.value?.trim() || ""; }

function renderPlans(payload) {
  const target = document.getElementById("learning-prep-detail");
  if (!target) return;
  const plans = Array.isArray(payload?.plans) ? payload.plans : [];
  const badge = document.getElementById("learning-prep-badge");
  if (badge) badge.textContent = `${plans.length} artifact(s)`;
  if (!plans.length) { target.innerHTML = "<p>Keine gespeicherten Lernvorbereitungen.</p>"; return; }
  target.innerHTML = plans.map((plan) => {
    const id = plan.plan_id || plan.id || "—";
    const status = plan.status || (plan.approved_by ? "approved" : "proposal");
    const objective = plan.objective?.description || plan.objective || "—";
    const digest = plan.digest || plan.content_digest || "—";
    return `<article class="learning-plan-row"><header><strong>${escapeHtml(id)}</strong><span>${escapeHtml(status)}</span></header><p>${escapeHtml(typeof objective === "object" ? JSON.stringify(objective) : objective)}</p><small>Digest: ${escapeHtml(digest)}</small><button type="button" data-approve-plan="${escapeHtml(id)}">Für Approval übernehmen</button></article>`;
  }).join("");
  target.querySelectorAll("[data-approve-plan]").forEach((button) => button.addEventListener("click", () => { const input = document.getElementById("learning-approve-plan-id"); if (input) input.value = button.dataset.approvePlan || ""; }));
}

async function refresh() {
  if (!ensurePanel()) return;
  try { renderPlans(await apiGet("/api/learning/preparation")); }
  catch (error) { const target = document.getElementById("learning-prep-detail"); if (target) target.textContent = `Nicht verfügbar: ${error.message}`; const badge = document.getElementById("learning-prep-badge"); if (badge) badge.textContent = "unavailable"; }
}

async function createProposal(event) {
  event.preventDefault();
  const result = document.getElementById("learning-prep-create-result");
  const payload = {
    action: "create", plan_id: value("learning-plan-id"),
    objective: { objective_id: value("learning-objective-id"), description: value("learning-objective-description"), success_metric: value("learning-success-metric"), evaluation_question: value("learning-evaluation-question") },
    sources: [{ source_id: value("learning-source-id"), digest: value("learning-source-digest"), origin: value("learning-source-origin"), partition: value("learning-source-partition") }],
    baseline_protocol: value("learning-baseline-protocol"), exposure_protocol: value("learning-exposure-protocol"), evaluation_protocol: value("learning-evaluation-protocol"), stopping_rule: value("learning-stopping-rule"), controls: value("learning-controls").split(",").map((item) => item.trim()).filter(Boolean),
  };
  if (result) result.textContent = "Proposal wird gespeichert …";
  try { const response = await apiPost("/api/learning/preparation", payload); if (result) result.textContent = `Gespeichert: ${response.status || "created"}. Keine Lern-Ausführung wurde gestartet.`; const approve = document.getElementById("learning-approve-plan-id"); if (approve) approve.value = payload.plan_id; await refresh(); }
  catch (error) { if (result) result.textContent = `Fehler: ${error.message}`; }
}

async function approveProposal(event) {
  event.preventDefault();
  const result = document.getElementById("learning-prep-approve-result");
  const payload = { action: "approve", plan_id: value("learning-approve-plan-id"), approved_by: value("learning-approved-by") };
  if (result) result.textContent = "Approval wird append-only gespeichert …";
  try { const response = await apiPost("/api/learning/preparation", payload); if (result) result.textContent = `Freigabe gespeichert: ${response.status || "approved"}. Der Plan bleibt nicht-ausführend.`; await refresh(); }
  catch (error) { if (result) result.textContent = `Fehler: ${error.message}`; }
}

export function initLearningPrep() {
  ensurePanel();
  refresh();
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = window.setInterval(refresh, 15000);
}
