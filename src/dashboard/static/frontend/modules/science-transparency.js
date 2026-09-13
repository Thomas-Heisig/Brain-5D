"use strict";
import { apiGet } from "../core/api.js";
import { openFMFile, openDocumentationFile } from "../../file-viewer.js";

const EMPIRICAL_ANALYSIS = "experiments/EXP-EMP-20260910/ANALYSIS.md";
const TODO_DOC = "08-roadmap/TODO.md";
let snapshotA = null;

function ensurePanel() {
  let panel = document.getElementById("mhrn-science-transparency"); if (panel) return panel;
  const workspace = document.getElementById("tab-research"); if (!workspace) return null;
  panel = document.createElement("section"); panel.id = "mhrn-science-transparency"; panel.className = "mhrn-science-transparency"; panel.dataset.mhrnRoute = "science:observatory"; panel.hidden = true;
  panel.innerHTML = `<header><div><span class="workspace-kicker">SCIENCE TRANSPARENCY</span><h2>Nachweise, Baselines, Provenienz & Diff</h2><p>Unknown, planned, stale und negative Befunde bleiben eigenständige Zustände.</p></div></header>
  <div class="science-transparency-grid">
    <article><h3>DATA / EVID Chronologie</h3><div id="science-chronology">lade …</div></article>
    <article><h3>Baseline Comparator</h3><p><b data-state="failed">Brian2:</b> gespeicherter negativer Konformitätsbefund; kein Framework-Ranking.</p><p><b data-state="pending">NEST / Lava:</b> planned · keine task-matched Messdaten im aktuellen Programm.</p><button data-open-research="${EMPIRICAL_ANALYSIS}">Messbericht öffnen</button><button data-open-doc="${TODO_DOC}">Roadmap öffnen</button></article>
    <article><h3>Dimensionsablation</h3><p><b>2D/3D/4D/5D/6D/8D:</b> Die vorab deklarierten 5D-Kontraste belegen keinen robusten 5D-Vorteil. Das ist ein negativer/neutraler Befund, kein Nachweis der Gleichwertigkeit.</p><button data-open-research="${EMPIRICAL_ANALYSIS}">Analyse öffnen</button></article>
    <article><h3>Ethics Gate</h3><p id="science-ethics"><b data-state="pending">unknown / human review required</b><br>Eine technische Gate-Ampel wird nicht als institutionelle Ethikfreigabe ausgegeben.</p><button data-open-doc="06-research/CONSCIOUSNESS_AND_WELFARE.md">Welfare Policy öffnen</button></article>
    <article><h3>Provenance Viewer</h3><div id="science-provenance">Noch kein Analysis-Job geladen.</div></article>
    <article><h3>Export Center</h3><div id="science-export">JSON-/CSV-Artefakte erscheinen nach einem Analysis-Job.</div></article>
    <article><h3>Runtime Snapshot Diff</h3><p>Vergleicht zwei bewusst erfasste Live-Samples im Browser; scientific_evidence=false.</p><div class="snapshot-diff-actions"><button data-snapshot="a">Snapshot A</button><button data-snapshot="b">Snapshot B + Diff</button></div><pre id="science-snapshot-diff">Noch kein Vergleich.</pre></article>
  </div>`;
  const anchor = workspace.querySelector(":scope > .mhrn-context-nav, :scope > .mhrn-breadcrumb-bar, :scope > .workspace-header") || workspace.firstElementChild; anchor?.insertAdjacentElement("afterend", panel);
  panel.addEventListener("click", handleClick); return panel;
}
async function refresh() {
  const panel = ensurePanel(); if (!panel) return;
  const [experiments, jobs, gate] = await Promise.allSettled([apiGet("/api/research/experiments"), apiGet("/api/research/analysis-jobs"), apiGet("/api/gate/status")]);
  const expPayload = experiments.status === "fulfilled" ? experiments.value : {};
  const expList = expPayload.experiments || expPayload.items || [];
  panel.querySelector("#science-chronology").innerHTML = Array.isArray(expList) && expList.length ? expList.slice(0, 6).map((entry) => `<p><b>${entry.experiment_id || entry.id || "DATA"}</b> · ${entry.status || "unknown"} · ${entry.updated_at || entry.created_at || "date unknown"}</p>`).join("") : `<p>Keine Chronologie über API verfügbar · unknown.</p>`;
  const jobList = jobs.status === "fulfilled" && Array.isArray(jobs.value.jobs) ? jobs.value.jobs : [];
  const job = jobList[0];
  panel.querySelector("#science-provenance").textContent = job ? `${job.job_id} · ${job.method} · tick ${job.input?.network_tick ?? "unknown"} · input ${job.input?.input_digest || "unknown"} · commit ${job.provenance?.git_commit || "unknown"} · source ${job.provenance?.source_tree_digest || "unknown"}` : "Keine persistierten Analysis-Jobs · unknown.";
  const exportRoot = panel.querySelector("#science-export");
  exportRoot.innerHTML = job ? `<button data-open-research="${job.artifacts?.json || ""}">JSON</button> <button data-open-research="${job.artifacts?.csv || ""}">CSV</button><p>scientific_evidence=${job.provenance?.scientific_evidence === true ? "true" : "false"}</p>` : "JSON-/CSV-Artefakte erscheinen nach einem Analysis-Job.";
  const gateText = panel.querySelector("#science-ethics");
  if (gate.status === "fulfilled") gateText.dataset.releaseGate = gate.value.overall || gate.value.status || "unknown";
}
async function captureSnapshot() {
  const projection = await apiGet("/api/network/projection?limit=500&mode=activity");
  return { tick: projection.tick ?? projection.network_tick ?? "unknown", points: (projection.points || []).map((p) => ({ id: p.neuron_id, v: p.v ?? null, u: p.u ?? null, activity: p.value ?? null, spikes: p.spike_counter ?? null })) };
}
function diffSnapshots(a, b) {
  const left = new Map(a.points.map((p) => [String(p.id), p])); let changed = 0; let compared = 0;
  for (const point of b.points) { const old = left.get(String(point.id)); if (!old) continue; compared += 1; if (JSON.stringify(old) !== JSON.stringify(point)) changed += 1; }
  return { scientific_evidence: false, snapshot_a_tick: a.tick, snapshot_b_tick: b.tick, compared_neurons: compared, changed_neurons: changed, sample_a: a.points.length, sample_b: b.points.length };
}
async function handleClick(event) {
  const research = event.target.closest("[data-open-research]"); if (research && research.dataset.openResearch) { openFMFile(research.dataset.openResearch); return; }
  const docs = event.target.closest("[data-open-doc]"); if (docs && docs.dataset.openDoc) { openDocumentationFile(docs.dataset.openDoc); return; }
  const snap = event.target.closest("[data-snapshot]"); if (!snap) return;
  const output = document.getElementById("science-snapshot-diff");
  try { const current = await captureSnapshot(); if (snap.dataset.snapshot === "a") { snapshotA = current; output.textContent = `Snapshot A erfasst · tick ${current.tick} · ${current.points.length} Neuronen`; } else if (!snapshotA) output.textContent = "Zuerst Snapshot A erfassen."; else output.textContent = JSON.stringify(diffSnapshots(snapshotA, current), null, 2); } catch (error) { output.textContent = `Diff nicht verfügbar: ${error.message}`; }
}
export function initScienceTransparency() { ensurePanel(); refresh(); }
