"use strict";

async function brain5dJson(url, options = undefined) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

async function sendControl(command, ticks = null) {
  const body = { command };
  if (ticks !== null) body.ticks = ticks;
  return brain5dJson("/api/control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

async function applyProposal(proposalId) {
  return brain5dJson("/api/self-organization/apply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proposal_id: proposalId, approved: true }),
  });
}

async function undoStructuralChange() {
  return brain5dJson("/api/self-organization/undo", { method: "POST" });
}

function bindOperatorConsole() {
  const byId = (id) => document.getElementById(id);
  byId("b5d-step")?.addEventListener("click", () => sendControl("step"));
  byId("b5d-start")?.addEventListener("click", () => sendControl("start"));
  byId("b5d-pause")?.addEventListener("click", () => sendControl("pause"));
  byId("b5d-resume")?.addEventListener("click", () => sendControl("resume"));
  byId("b5d-stop")?.addEventListener("click", () => sendControl("stop"));
  byId("b5d-snapshot")?.addEventListener("click", () => sendControl("snapshot"));
  byId("b5d-run-ticks")?.addEventListener("click", () => {
    const count = Number.parseInt(byId("b5d-tick-count")?.value || "1", 10);
    if (Number.isFinite(count) && count > 0) sendControl("run_ticks", count);
  });
  byId("b5d-undo")?.addEventListener("click", () => undoStructuralChange());
}

document.addEventListener("DOMContentLoaded", bindOperatorConsole);
