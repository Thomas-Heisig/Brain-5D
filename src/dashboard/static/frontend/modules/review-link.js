"use strict";
function ensureReviewLink() {
  const workspace = document.getElementById("tab-research"); if (!workspace || document.getElementById("mhrn-review-share")) return;
  const panel = document.createElement("section"); panel.id = "mhrn-review-share"; panel.className = "mhrn-review-share card"; panel.dataset.mhrnRoute = "review:portal"; panel.dataset.generatedPanel = "portal"; panel.hidden = true;
  panel.style.display = "none";
  const link = new URL("/review", window.location.href).href;
  panel.innerHTML = `<div><span class="workspace-kicker">EXTERNAL REVIEW</span><strong>Probanden- und Prüferansicht</strong><small>Direkter Link; private Antwortdaten und Prüferidentitäten bleiben außerhalb des Research-AI-Kontexts.</small></div><code id="mhrn-review-url"></code><button type="button">Link kopieren</button><a href="/review" target="_blank" rel="noopener">/review öffnen</a>`;
  panel.querySelector("#mhrn-review-url").textContent = link;
  panel.querySelector("button").addEventListener("click", async () => { try { await navigator.clipboard.writeText(link); panel.querySelector("button").textContent = "Kopiert"; } catch (_) { panel.querySelector("button").textContent = "Kopieren fehlgeschlagen"; } });
  const host = document.getElementById("tab-review") || document.querySelector("main") || document.body; host.appendChild(panel);
}
export function initReviewLink() { ensureReviewLink(); }
