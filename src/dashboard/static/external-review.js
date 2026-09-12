"use strict";

export function initExternalReview() {
  const mount = document.getElementById("review-external-mount") || document.getElementById("tab-review") || document.getElementById("tab-research");
  if (!mount) return;
  let panel = document.getElementById("external-review-status");
  if (panel) { if (panel.parentElement !== mount) mount.appendChild(panel); return; }
  panel = document.createElement("section");
  panel.id = "external-review-status";
  panel.className = "research-review-inbox card";
  panel.dataset.panelInfo = "Zeigt nur öffentliche Instrument-Metadaten. Private Antworten, Prüferidentitäten und Rohdaten werden hier nicht geladen.";
  panel.innerHTML = `<header><div><span class="workspace-kicker">EXTERNAL REVIEW</span><h2>Externe Begutachtung</h2><p>Screening, Fachprüfung und institutionelle Ethikfreigabe bleiben getrennte Ebenen.</p></div><button type="button" id="external-review-refresh">Status prüfen</button></header><div class="mhrn-review-summary"><p id="external-review-summary" role="status">Status wird geprüft.</p><div class="mhrn-action-row"><a class="button-like" href="/review" target="_blank" rel="noopener noreferrer">Fragenkatalog öffnen</a><button type="button" id="external-review-method">Prüfverfahren im File Viewer</button></div></div><div id="external-review-stages"></div><p class="mhrn-epistemic-note">Private Antworten und Prüferidentitäten werden weder hier geladen noch an eine KI übergeben. Ausstehende Beurteilungen bleiben offen.</p>`;
  mount.appendChild(panel);
  panel.querySelector("#external-review-method").addEventListener("click",()=>{document.dispatchEvent(new CustomEvent("brain5d:open-file",{detail:{source:"research",path:"external_review/INTEGRATION.md"}}));window.MHRNWorkspaceArchitecture?.selectRoute?.("science","files");});
  async function refresh(){const summary=panel.querySelector("#external-review-summary"),stages=panel.querySelector("#external-review-stages");stages.replaceChildren();summary.textContent="Status wird geprüft.";try{const response=await fetch("/api/research/external-review",{cache:"no-store"});if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();if(data.available!==true)throw new Error(data.reason||"Keine geprüften Metadaten verfügbar");summary.textContent=`${data.base_questions+data.specialist_questions} Fragen · Version ${data.instrument_version} · Beurteilung ausstehend · Ethikfreigabe nicht behauptet`;const list=document.createElement("dl");for(const item of data.stages||[]){const dt=document.createElement("dt");dt.textContent=`${item.label}: ${item.status}`;const dd=document.createElement("dd");dd.textContent=item.requirement;list.append(dt,dd);}stages.append(list);}catch(error){summary.textContent=`Nicht verfügbar: ${error.message||error}. Keine Freigabe abgeleitet.`;}}
  panel.querySelector("#external-review-refresh").addEventListener("click",refresh);void refresh();
}
