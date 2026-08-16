"use strict";

(() => {
  const byId = (id) => document.getElementById(id);
  const stateBadge = byId("runtime-state");
  if (!stateBadge) return;

  const controls = {
    tick: byId("runtime-tick"),
    queued: byId("runtime-queued"),
    lastBatch: byId("runtime-last-batch"),
    lastMs: byId("runtime-last-ms"),
    stepTicks: byId("step-ticks"),
    loopSize: byId("loop-size"),
    delayMs: byId("delay-ms"),
    step: byId("step-button"),
    run: byId("run-button"),
    pause: byId("pause-button"),
    stop: byId("stop-button"),
    apply: byId("apply-runtime-config"),
    snapshot: byId("snapshot-button"),
    selfOrgEnabled: byId("self-org-enabled"),
    selfOrgDryRun: byId("self-org-dry-run"),
    proposal: byId("self-org-proposal"),
    message: byId("control-message"),
  };

  let commandInFlight = false;

  function numericValue(element, fallback) {
    if (!element) return fallback;
    const value = Number(element.value);
    return Number.isFinite(value) ? value : fallback;
  }

  function setMessage(text, isError = false) {
    if (!controls.message) return;
    controls.message.textContent = text;
    controls.message.dataset.kind = isError ? "error" : "info";
  }

  function renderState(payload) {
    const runtime = payload.runtime || payload;
    if (!runtime) return;
    stateBadge.textContent = runtime.mode || "unknown";
    stateBadge.dataset.mode = runtime.mode || "unknown";
    if (controls.tick) controls.tick.textContent = String(runtime.ticks_executed ?? 0);
    if (controls.queued) controls.queued.textContent = String(runtime.queued_ticks ?? 0);
    if (controls.lastBatch) controls.lastBatch.textContent = String(runtime.last_batch_ticks ?? 0);
    if (controls.lastMs) controls.lastMs.textContent = Number(runtime.last_batch_ms ?? 0).toFixed(2);
    if (controls.snapshot) controls.snapshot.disabled = runtime.can_snapshot === false;

    const selfOrg = payload.self_organization;
    if (selfOrg) {
      if (controls.selfOrgEnabled) controls.selfOrgEnabled.checked = Boolean(selfOrg.enabled);
      if (controls.selfOrgDryRun) controls.selfOrgDryRun.checked = Boolean(selfOrg.dry_run);
      const proposal = selfOrg.last_proposal;
      if (controls.proposal) {
        controls.proposal.textContent = proposal
          ? `${proposal.action} × ${proposal.count} — ${proposal.reason}`
          : "none";
      }
    }
  }

  async function loadState() {
    try {
      const response = await fetch("/api/control", { cache: "no-store" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      renderState(payload);
    } catch (error) {
      setMessage(`Control status unavailable: ${error.message}`, true);
    }
  }

  async function command(payload) {
    if (commandInFlight) return;
    commandInFlight = true;
    try {
      const response = await fetch("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || result.ok === false) {
        throw new Error(result.error || `HTTP ${response.status}`);
      }
      renderState(result);
      setMessage(`Command '${payload.action}' accepted.`);
      await loadState();
    } catch (error) {
      setMessage(error.message, true);
    } finally {
      commandInFlight = false;
    }
  }

  controls.step?.addEventListener("click", () => command({
    action: "step",
    ticks: Math.trunc(numericValue(controls.stepTicks, 1)),
  }));

  controls.run?.addEventListener("click", () => command({
    action: "run",
    loop_size: Math.trunc(numericValue(controls.loopSize, 100)),
  }));

  controls.pause?.addEventListener("click", () => command({ action: "pause" }));
  controls.stop?.addEventListener("click", () => command({ action: "stop" }));
  controls.snapshot?.addEventListener("click", () => command({ action: "snapshot" }));

  controls.apply?.addEventListener("click", () => command({
    action: "configure",
    loop_size: Math.trunc(numericValue(controls.loopSize, 100)),
    delay_ms: numericValue(controls.delayMs, 0),
  }));

  const updateSelfOrganization = () => command({
    action: "self_organization",
    enabled: Boolean(controls.selfOrgEnabled?.checked),
    dry_run: Boolean(controls.selfOrgDryRun?.checked),
  });
  controls.selfOrgEnabled?.addEventListener("change", updateSelfOrganization);
  controls.selfOrgDryRun?.addEventListener("change", updateSelfOrganization);

  loadState();
  window.setInterval(loadState, 500);
})();
