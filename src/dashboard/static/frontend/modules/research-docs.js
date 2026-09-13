"use strict";
import { apiGet } from "../core/api.js";
let refreshTimer=null;
let _viewMode=localStorage.getItem("mhrn-registry-view")||"grid";
let _sortMode=localStorage.getItem("mhrn-registry-sort")||"name-asc";
function esc(v){const d=document.createElement("div");d.textContent=v==null?"":String(v);return d.innerHTML;}
function open(path){if(!path)return;document.dispatchEvent(new CustomEvent("brain5d:open-file",{detail:{source:"research",path}}));window.MHRNWorkspaceArchitecture?.selectRoute?.("files","browse");}
function sortItems(items,mode){const s=[].concat(items);const fn=(a,b)=>{const aN=(a.name||a.title||a.path||a.report_id||"").toLowerCase();const bN=(b.name||b.title||b.path||b.report_id||"").toLowerCase();const aD=a.created_at||a.timestamp||"";const bD=b.created_at||b.timestamp||"";const aT=a.kind||a.category||"";const bT=b.kind||b.category||"";switch(mode){case"name-desc":return bN.localeCompare(aN);case"date-asc":return aD<bD?-1:aD>bD?1:0;case"date-desc":return aD>bD?-1:aD<bD?1:0;case"type":return aT.localeCompare(bT)||aN.localeCompare(bN);default:return aN.localeCompare(bN);}};s.sort(fn);return s;}
function ensure(){let p=document.getElementById("mhrn-research-docs");if(p)return p;const root=document.getElementById("tab-research");if(!root)return null;p=document.createElement("section");p.id="mhrn-research-docs";p.className="mhrn-research-docs card";p.dataset.panelInfo="Registry-Index für Research-Artefakte. Inhalte rendert ausschließlich der zentrale File Viewer.";p.innerHTML=`<header><div><span class="workspace-kicker">REGISTRY · REPORTS · AIRR</span><h2>Research-Dokumente & Berichte</h2><p>Index und Provenienz; keine parallele Dateiansicht.</p></div><span id="research-docs-badge">lade …</span></header>
<div class="registry-view-toolbar">
  <div class="exp-view-toggle">
    <button type="button" class="exp-view-btn" data-reg-view="grid" title="Grid-Ansicht" aria-label="Grid-Ansicht">▦</button>
    <button type="button" class="exp-view-btn" data-reg-view="list" title="Listen-Ansicht" aria-label="Listen-Ansicht">☰</button>
  </div>
  <label class="exp-sort-label">Sortieren<select id="registry-sort" class="exp-sort-select">
    <option value="name-asc">A–Z</option>
    <option value="name-desc">Z–A</option>
    <option value="date-desc">Neueste zuerst</option>
    <option value="date-asc">Älteste zuerst</option>
    <option value="type">Nach Typ</option>
  </select></label>
</div>
<div class="research-docs-grid"><section class="research-docs-section"><h3>Research-Dokumente</h3><div id="research-documents-list" class="registry-list" data-reg-view="${_viewMode}">lade …</div></section><section class="research-docs-section"><h3>Generierte Berichte</h3><div id="research-reports-list" class="registry-list" data-reg-view="${_viewMode}">lade …</div></section><section class="research-docs-section"><h3>AI Research Reports</h3><div id="research-ai-reports-list" class="registry-list" data-reg-view="${_viewMode}">lade …</div></section></div>`;const target=root.querySelector('.research-subpanel[data-subpanel="registry"]')||root;target.querySelector("#research-registry-placeholder")?.remove();target.append(p);
p.querySelectorAll("[data-reg-view]").forEach(btn=>{btn.classList.toggle("active",btn.dataset.regView===_viewMode);btn.addEventListener("click",()=>{_viewMode=btn.dataset.regView;localStorage.setItem("mhrn-registry-view",_viewMode);p.querySelectorAll("[data-reg-view]").forEach(b=>b.classList.toggle("active",b.dataset.regView===_viewMode));document.querySelectorAll(".registry-list").forEach(el=>el.dataset.regView=_viewMode);});});
const sortSel=p.querySelector("#registry-sort");if(sortSel){sortSel.value=_sortMode;sortSel.addEventListener("change",()=>{_sortMode=sortSel.value;localStorage.setItem("mhrn-registry-sort",_sortMode);refresh();});}
p.onclick=e=>{const b=e.target.closest("[data-research-path]");if(b)open(b.dataset.researchPath);};return p;}
function row(item,extra=""){const title=item.name||item.title||item.path||item.report_id||"—";const meta=[item.kind||item.category,item.experiment_id,item.size_bytes!=null?`${item.size_bytes} B`:""].filter(Boolean).join(" · ");const path=item.path||item.json_path||item.markdown_path;return `<article class="research-item"><div><strong>${esc(title)}</strong><small>${esc(meta)}</small>${extra}</div><button type="button" data-research-path="${esc(path||"")}" ${path?"":"disabled"}>Im File Viewer öffnen</button></article>`;}
function renderList(id,items,extraFn){const el=document.getElementById(id);if(!el)return;const sorted=sortItems(items,_sortMode);el.innerHTML=sorted.length?sorted.map(x=>row(x,extraFn?extraFn(x):"")).join(""):"<p>Keine Einträge.</p>";return sorted.length;}
function docs(payload){const a=Array.isArray(payload?.documents)?payload.documents:[];return renderList("research-documents-list",a);}
function reports(payload){const a=Array.isArray(payload?.reports)?payload.reports:[];return renderList("research-reports-list",a);}
function airr(payload){const a=Array.isArray(payload?.reports)?payload.reports:[];return renderList("research-ai-reports-list",a,x=>{const path=x.json_path||x.markdown_path;return x.markdown_path&&x.markdown_path!==path?`<button type="button" data-research-path="${esc(x.markdown_path)}">Markdown</button>`:"";});}
async function refresh(){const p=ensure();if(!p||p.hidden)return;const [d,r,a]=await Promise.allSettled([apiGet("/api/research/documents"),apiGet("/api/research/reports"),apiGet("/api/research/ai-reports")]);let total=0;if(d.status==="fulfilled")total+=docs(d.value);else document.getElementById("research-documents-list").textContent=`Nicht verfügbar: ${d.reason.message}`;if(r.status==="fulfilled")total+=reports(r.value);else document.getElementById("research-reports-list").textContent=`Nicht verfügbar: ${r.reason.message}`;if(a.status==="fulfilled")total+=airr(a.value);else document.getElementById("research-ai-reports-list").textContent=`Nicht verfügbar: ${a.reason.message}`;document.getElementById("research-docs-badge").textContent=`${total} artifact(s)`;}
export function initResearchDocs(){ensure();refresh();if(refreshTimer)clearInterval(refreshTimer);refreshTimer=setInterval(refresh,30000);}
