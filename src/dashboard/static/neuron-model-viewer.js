/* MHRN Neuron Model Viewer
 *
 * Scientific, bounded replacement for the legacy nested 5D projection.
 * Default path: deterministic backend sampling + client-side PCA on N x 5.
 * Heavy non-linear embeddings remain visibly unavailable until a dedicated,
 * provenance-bound backend job contract exists.
 */
"use strict";

const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.179.1/build/three.module.js";
const MAX_DENSITY_SYNAPSES = 5000;
const viewerState = {
  points: [],
  projected: [],
  eigenvalues: [],
  explained: [],
  degree: new Map(),
  densityComplete: false,
  sampleCount: 500,
  targetDimensions: 2,
  view: "projection",
  timer: null,
  screenPoints: [],
  three: null,
};

function byId(id) { return document.getElementById(id); }
function clamp(value, min = 0, max = 1) { return Math.max(min, Math.min(max, value)); }
function number(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function setText(id, text) { const el = byId(id); if (el) el.textContent = String(text); }

function injectStyles() {
  if (byId("neuron-model-viewer-styles")) return;
  const style = document.createElement("style");
  style.id = "neuron-model-viewer-styles";
  style.textContent = `
    .neuron-model-viewer { padding: 0; overflow: clip; }
    .nmv-head { padding: 1rem 1.1rem .8rem; display:flex; gap:1rem; align-items:flex-start; justify-content:space-between; border-bottom:1px solid var(--line,rgba(127,127,127,.2)); }
    .nmv-head h2 { margin:0; font-size:1.08rem; }
    .nmv-head p { margin:.3rem 0 0; opacity:.7; max-width:68ch; }
    .nmv-badge { display:inline-flex; align-items:center; padding:.24rem .5rem; border:1px solid rgba(77,212,172,.36); border-radius:999px; font-size:.7rem; letter-spacing:.05em; text-transform:uppercase; }
    .nmv-toolbar { padding:.8rem 1.1rem; display:grid; grid-template-columns:repeat(5,minmax(130px,1fr)); gap:.7rem; background:rgba(127,127,127,.035); border-bottom:1px solid var(--line,rgba(127,127,127,.2)); }
    .nmv-toolbar label { display:grid; gap:.3rem; font-size:.72rem; opacity:.86; }
    .nmv-toolbar select,.nmv-toolbar button { min-height:36px; border:1px solid var(--line,rgba(127,127,127,.25)); border-radius:8px; background:var(--panel,#0d1822); color:inherit; padding:.35rem .55rem; }
    .nmv-toolbar button { cursor:pointer; align-self:end; }
    .nmv-toolbar button:hover { background:rgba(127,127,127,.12); }
    .nmv-view-tabs { display:flex; gap:.45rem; padding:.72rem 1.1rem 0; }
    .nmv-view-tabs button { border:0; border-bottom:2px solid transparent; background:transparent; color:inherit; padding:.5rem .65rem; cursor:pointer; opacity:.68; }
    .nmv-view-tabs button.active { opacity:1; border-bottom-color:currentColor; }
    .nmv-stage { position:relative; min-height:520px; padding:.6rem 1rem 0; }
    .nmv-stage canvas { width:100%; height:520px; display:block; border-radius:10px; background:rgba(2,7,12,.58); }
    .nmv-three-mount { width:100%; height:520px; border-radius:10px; overflow:hidden; background:rgba(2,7,12,.58); }
    .nmv-three-mount canvas { height:100%; border-radius:0; }
    .nmv-tooltip { position:absolute; z-index:3; pointer-events:none; min-width:210px; max-width:320px; padding:.65rem .75rem; border:1px solid rgba(127,127,127,.32); border-radius:9px; background:rgba(5,13,20,.94); color:#f1f6f8; box-shadow:0 10px 35px rgba(0,0,0,.28); font:12px/1.45 ui-monospace,monospace; }
    .nmv-footer { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.65rem; padding:.85rem 1.1rem 1.1rem; }
    .nmv-stat { padding:.7rem .8rem; border:1px solid var(--line,rgba(127,127,127,.2)); border-radius:9px; background:rgba(127,127,127,.035); }
    .nmv-stat span { display:block; font-size:.66rem; opacity:.62; text-transform:uppercase; letter-spacing:.07em; }
    .nmv-stat strong { display:block; margin-top:.22rem; font-size:.82rem; }
    .nmv-pending { color:#f0b45e; }
    .nmv-legend { position:absolute; right:1.5rem; top:1.1rem; padding:.45rem .55rem; border-radius:8px; background:rgba(5,13,20,.82); color:#d9e5ea; font-size:.7rem; }
    .nmv-legend i { display:inline-block; width:80px; height:7px; margin-left:.35rem; border-radius:9px; background:linear-gradient(90deg,hsl(210,80%,45%),hsl(110,80%,48%),hsl(10,85%,52%)); }
    .nmv-empty { min-height:420px; display:grid; place-items:center; text-align:center; opacity:.72; }
    @media(max-width:1000px){.nmv-toolbar{grid-template-columns:repeat(2,minmax(150px,1fr));}.nmv-footer{grid-template-columns:repeat(2,minmax(0,1fr));}}
    @media(max-width:650px){.nmv-head{flex-direction:column}.nmv-toolbar,.nmv-footer{grid-template-columns:1fr}.nmv-stage{min-height:420px}.nmv-stage canvas,.nmv-three-mount{height:420px}}
  `;
  document.head.appendChild(style);
}

function createViewer() {
  const legacy = byId("network-projection");
  if (!legacy || byId("neuron-model-viewer")) return;
  injectStyles();
  const section = document.createElement("section");
  section.id = "neuron-model-viewer";
  section.className = "card neuron-model-viewer";
  section.dataset.networkView = "visual";
  section.innerHTML = `
    <header class="nmv-head">
      <div><span class="workspace-kicker">NETWORK WORKBENCH · DIMENSIONALITY REDUCTION</span><h2>Neuron Model Viewer</h2><p>Deterministisch gesampelte reale 5D-Neuronen. PCA läuft lokal auf einer 5×5-Kovarianzmatrix; keine verschachtelten Würfel und kein permanentes Re-Rendering.</p></div>
      <span class="nmv-badge">PCA · implemented</span>
    </header>
    <div class="nmv-toolbar">
      <label>Projektionsmodus<select id="nmv-method"><option value="pca">PCA · schnell</option><option value="tsne" disabled>t-SNE · Not implemented yet</option><option value="umap" disabled>UMAP · Not implemented yet</option></select></label>
      <label>Zieldimension<select id="nmv-dim"><option value="2" selected>2D · Canvas</option><option value="3">3D · Three.js</option></select></label>
      <label>Stichprobe<select id="nmv-sample"><option value="200">200 Neuronen</option><option value="500" selected>500 Neuronen</option><option value="2000">2000 Neuronen</option></select></label>
      <label>Aktualisierung<select id="nmv-interval"><option value="0" selected>Manuell</option><option value="5000">Alle 5 s</option><option value="30000">Alle 30 s</option></select></label>
      <button id="nmv-refresh" type="button">↻ Neu berechnen</button>
    </div>
    <nav class="nmv-view-tabs" aria-label="Neuron Model Viewer views">
      <button class="active" data-nmv-view="projection" type="button">PCA-Projektion</button>
      <button data-nmv-view="correlation" type="button">Korrelations-Heatmap</button>
      <button data-nmv-view="parallel" type="button">Parallele Koordinaten</button>
    </nav>
    <div class="nmv-stage">
      <canvas id="nmv-canvas" width="1100" height="520" aria-label="Neuron projection"></canvas>
      <div id="nmv-three" class="nmv-three-mount" hidden></div>
      <div id="nmv-tooltip" class="nmv-tooltip" hidden></div>
      <div class="nmv-legend">Aktivität <i></i></div>
    </div>
    <footer class="nmv-footer">
      <div class="nmv-stat"><span>Erklärte Varianz</span><strong id="nmv-variance">—</strong></div>
      <div class="nmv-stat"><span>Cluster-Kennzahl</span><strong class="nmv-pending">Not implemented yet · keine Clusterlabels</strong></div>
      <div class="nmv-stat"><span>Verbindungsdichte</span><strong id="nmv-density">—</strong></div>
      <div class="nmv-stat"><span>Backend / Status</span><strong id="nmv-status">bereit · manuell</strong></div>
      <div class="nmv-stat"><span>Non-linear embeddings</span><strong class="nmv-pending">t-SNE / UMAP · Not implemented yet</strong></div>
      <div class="nmv-stat"><span>Lasso / Cluster export</span><strong class="nmv-pending">Not implemented yet</strong></div>
      <div class="nmv-stat"><span>Per-neuron Hz</span><strong class="nmv-pending">Not implemented yet · Farbe nutzt Activity-Proxy</strong></div>
      <div class="nmv-stat"><span>Profil-Cache</span><strong class="nmv-pending">Not implemented yet</strong></div>
    </footer>`;
  legacy.parentElement.insertBefore(section, legacy);
  legacy.hidden = true;
  legacy.setAttribute("aria-hidden", "true");
  legacy.dataset.replacedBy = "neuron-model-viewer";
  bindViewer();
  refreshViewer();
}

function bindViewer() {
  byId("nmv-refresh")?.addEventListener("click", refreshViewer);
  byId("nmv-sample")?.addEventListener("change", (event) => {
    viewerState.sampleCount = number(event.target.value, 500);
  });
  byId("nmv-dim")?.addEventListener("change", (event) => {
    viewerState.targetDimensions = number(event.target.value, 2);
    renderCurrentView();
  });
  byId("nmv-interval")?.addEventListener("change", (event) => {
    if (viewerState.timer) clearInterval(viewerState.timer);
    viewerState.timer = null;
    const ms = number(event.target.value, 0);
    if (ms > 0) viewerState.timer = setInterval(refreshViewer, ms);
    setText("nmv-status", ms ? `auto · ${ms / 1000}s` : "bereit · manuell");
  });
  document.querySelector(".nmv-view-tabs")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-nmv-view]");
    if (!button) return;
    viewerState.view = button.dataset.nmvView;
    document.querySelectorAll("[data-nmv-view]").forEach((item) => item.classList.toggle("active", item === button));
    renderCurrentView();
  });
  const canvas = byId("nmv-canvas");
  canvas?.addEventListener("pointermove", handleCanvasHover);
  canvas?.addEventListener("pointerleave", () => hideTooltip());
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

async function refreshViewer() {
  const method = byId("nmv-method")?.value || "pca";
  if (method !== "pca") {
    setText("nmv-status", `${method.toUpperCase()} · Not implemented yet`);
    return;
  }
  setText("nmv-status", "lade reale 5D-Stichprobe …");
  try {
    const limit = viewerState.sampleCount;
    const [projection, synapses] = await Promise.all([
      fetchJson(`/api/network/projection?limit=${limit}&mode=activity`),
      fetchJson(`/api/network/synapses?limit=${MAX_DENSITY_SYNAPSES}&offset=0`).catch(() => null),
    ]);
    viewerState.points = (projection.points || []).map((point) => ({
      id: point.neuron_id,
      coords: [point.x, point.y, point.z, point.d4, point.d5].map((v) => number(v)),
      activity: number(point.value),
      input: Boolean(point.is_input),
      output: Boolean(point.is_output),
      degree: null,
    }));
    applyDensity(synapses);
    const pca = computePca(viewerState.points, 3);
    viewerState.projected = pca.projected;
    viewerState.eigenvalues = pca.eigenvalues;
    viewerState.explained = pca.explained;
    const used = viewerState.targetDimensions === 3 ? 3 : 2;
    const explained = viewerState.explained.slice(0, used).reduce((a, b) => a + b, 0) * 100;
    setText("nmv-variance", viewerState.points.length > 1 ? `PC1–PC${used}: ${explained.toFixed(1)} %` : "—");
    setText("nmv-status", `${projection.source || "live_runtime"} · ${viewerState.points.length}/${projection.total_count ?? viewerState.points.length} · ${projection.sampling_method || "bounded"}`);
    renderCurrentView();
  } catch (error) {
    viewerState.points = [];
    viewerState.projected = [];
    setText("nmv-status", `nicht verfügbar · ${error.message}`);
    renderEmpty(`Neuron Model Viewer kann die Live-Daten nicht lesen: ${error.message}`);
  }
}

function applyDensity(payload) {
  const degree = new Map();
  const rows = payload?.synapses || [];
  for (const synapse of rows) {
    const source = synapse.source_id;
    const target = synapse.target_id;
    if (source != null) degree.set(source, (degree.get(source) || 0) + 1);
    if (target != null) degree.set(target, (degree.get(target) || 0) + 1);
  }
  viewerState.degree = degree;
  viewerState.densityComplete = Boolean(payload && payload.total === payload.returned);
  for (const point of viewerState.points) point.degree = degree.has(point.id) ? degree.get(point.id) : null;
  if (!payload) setText("nmv-density", "nicht verfügbar");
  else if (viewerState.densityComplete) setText("nmv-density", `exakt · ${payload.total} Synapsen`);
  else setText("nmv-density", `begrenzt · ${payload.returned}/${payload.total} Synapsen`);
}

function computePca(points, components = 3) {
  const rows = points.map((point) => point.coords);
  if (rows.length < 2) return { projected: rows.map(() => [0, 0, 0]), eigenvalues: [0,0,0,0,0], explained: [0,0,0,0,0] };
  const dims = 5;
  const means = Array(dims).fill(0);
  rows.forEach((row) => row.forEach((value, d) => { means[d] += value; }));
  for (let d = 0; d < dims; d++) means[d] /= rows.length;
  const centered = rows.map((row) => row.map((value, d) => value - means[d]));
  const covariance = Array.from({ length: dims }, () => Array(dims).fill(0));
  for (const row of centered) {
    for (let i = 0; i < dims; i++) for (let j = i; j < dims; j++) covariance[i][j] += row[i] * row[j];
  }
  for (let i = 0; i < dims; i++) for (let j = i; j < dims; j++) {
    covariance[i][j] /= Math.max(1, rows.length - 1);
    covariance[j][i] = covariance[i][j];
  }
  const { values, vectors } = jacobiEigen(covariance);
  const order = values.map((value, index) => ({ value, index })).sort((a, b) => b.value - a.value);
  const eigenvalues = order.map((entry) => Math.max(0, entry.value));
  const basis = order.slice(0, components).map((entry) => vectors.map((row) => row[entry.index]));
  const projected = centered.map((row) => basis.map((vector) => row.reduce((sum, value, index) => sum + value * vector[index], 0)));
  const total = eigenvalues.reduce((a, b) => a + b, 0) || 1;
  return { projected, eigenvalues, explained: eigenvalues.map((value) => value / total) };
}

function jacobiEigen(matrix) {
  const n = matrix.length;
  const a = matrix.map((row) => row.slice());
  const v = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => i === j ? 1 : 0));
  for (let iteration = 0; iteration < 80; iteration++) {
    let p = 0, q = 1, max = Math.abs(a[p][q]);
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const value = Math.abs(a[i][j]);
      if (value > max) { max = value; p = i; q = j; }
    }
    if (max < 1e-10) break;
    const angle = 0.5 * Math.atan2(2 * a[p][q], a[q][q] - a[p][p]);
    const c = Math.cos(angle), s = Math.sin(angle);
    const app = c*c*a[p][p] - 2*s*c*a[p][q] + s*s*a[q][q];
    const aqq = s*s*a[p][p] + 2*s*c*a[p][q] + c*c*a[q][q];
    for (let k = 0; k < n; k++) {
      if (k === p || k === q) continue;
      const aik = a[k][p], akq = a[k][q];
      a[k][p] = a[p][k] = c*aik - s*akq;
      a[k][q] = a[q][k] = s*aik + c*akq;
    }
    a[p][p] = app; a[q][q] = aqq; a[p][q] = a[q][p] = 0;
    for (let k = 0; k < n; k++) {
      const vip = v[k][p], viq = v[k][q];
      v[k][p] = c*vip - s*viq;
      v[k][q] = s*vip + c*viq;
    }
  }
  return { values: a.map((row, i) => row[i]), vectors: v };
}

function renderCurrentView() {
  if (!viewerState.points.length) return renderEmpty("Keine Neuronendaten verfügbar.");
  destroyThree();
  byId("nmv-canvas").hidden = false;
  byId("nmv-three").hidden = true;
  if (viewerState.view === "correlation") return drawCorrelation();
  if (viewerState.view === "parallel") return drawParallelCoordinates();
  if (viewerState.targetDimensions === 3) return drawThreeProjection();
  return drawTwoDimensionalProjection();
}

function canvasContext() {
  const canvas = byId("nmv-canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  return { canvas, ctx };
}

function activityDomain() {
  const values = viewerState.points.map((point) => point.activity);
  return [Math.min(...values), Math.max(...values)];
}
function activityColor(value, min, max) {
  const t = max > min ? clamp((value - min) / (max - min)) : 0;
  const hue = 210 - 200 * t;
  return `hsl(${hue},82%,${42 + 10*t}%)`;
}
function pointRadius(point) {
  if (point.degree == null) return point.input || point.output ? 4.2 : 2.8;
  return clamp(2.4 + Math.log1p(point.degree) * 1.15, 2.4, 8.5);
}

function drawTwoDimensionalProjection() {
  const { canvas, ctx } = canvasContext();
  const coords = viewerState.projected;
  const xs = coords.map((row) => row[0]), ys = coords.map((row) => row[1]);
  const [xmin, xmax] = [Math.min(...xs), Math.max(...xs)];
  const [ymin, ymax] = [Math.min(...ys), Math.max(...ys)];
  const [amin, amax] = activityDomain();
  const pad = 38;
  viewerState.screenPoints = [];
  ctx.strokeStyle = "rgba(150,170,185,.16)"; ctx.lineWidth = 1;
  ctx.strokeRect(pad, pad, canvas.width - pad*2, canvas.height - pad*2);
  coords.forEach((row, index) => {
    const point = viewerState.points[index];
    const x = pad + ((row[0] - xmin) / Math.max(1e-12, xmax - xmin)) * (canvas.width - pad*2);
    const y = canvas.height - pad - ((row[1] - ymin) / Math.max(1e-12, ymax - ymin)) * (canvas.height - pad*2);
    const radius = pointRadius(point);
    ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI*2); ctx.fillStyle = activityColor(point.activity, amin, amax); ctx.fill();
    if (point.input || point.output) { ctx.strokeStyle = point.input ? "#4cdcb7" : "#efb352"; ctx.lineWidth = 1.3; ctx.stroke(); }
    viewerState.screenPoints.push({ x, y, radius: radius + 5, index });
  });
  ctx.fillStyle = "rgba(205,220,230,.72)"; ctx.font = "12px ui-monospace,monospace";
  ctx.fillText("PC1", canvas.width - 66, canvas.height - 14); ctx.fillText("PC2", 10, 25);
}

async function drawThreeProjection() {
  setText("nmv-status", `${byId("nmv-status")?.textContent || ""} · lade Three.js`);
  try {
    const THREE = await import(THREE_URL);
    renderThree(THREE);
  } catch (error) {
    setText("nmv-status", `3D CDN nicht verfügbar · Canvas-Fallback`);
    drawThreeCanvasFallback();
  }
}

function normalizeProjected3() {
  const cols = [0,1,2].map((d) => viewerState.projected.map((row) => row[d] || 0));
  const mins = cols.map((c) => Math.min(...c)), maxs = cols.map((c) => Math.max(...c));
  return viewerState.projected.map((row) => [0,1,2].map((d) => ((row[d] || 0) - mins[d]) / Math.max(1e-12, maxs[d] - mins[d]) * 2 - 1));
}

function renderThree(THREE) {
  const canvas = byId("nmv-canvas"), mount = byId("nmv-three");
  canvas.hidden = true; mount.hidden = false; mount.innerHTML = "";
  const width = Math.max(320, mount.clientWidth || 1000), height = Math.max(320, mount.clientHeight || 520);
  const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5)); renderer.setSize(width, height); mount.appendChild(renderer.domElement);
  const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(50, width/height, .1, 100); camera.position.z = 4.2;
  const normalized = normalizeProjected3(); const [amin, amax] = activityDomain();
  const positions = new Float32Array(normalized.length*3), colors = new Float32Array(normalized.length*3), sizes = new Float32Array(normalized.length);
  normalized.forEach((row, i) => { positions.set(row, i*3); const t = amax > amin ? clamp((viewerState.points[i].activity-amin)/(amax-amin)) : 0; const color = new THREE.Color().setHSL((210-200*t)/360,.82,.5); colors.set([color.r,color.g,color.b], i*3); sizes[i] = pointRadius(viewerState.points[i])*1.35; });
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute("position", new THREE.BufferAttribute(positions,3)); geometry.setAttribute("color", new THREE.BufferAttribute(colors,3)); geometry.setAttribute("pointSize", new THREE.BufferAttribute(sizes,1));
  const material = new THREE.ShaderMaterial({ vertexColors:true, transparent:true, depthWrite:false, vertexShader:`attribute float pointSize; varying vec3 vColor; void main(){vColor=color; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_PointSize=max(2.0,pointSize*(220.0/max(1.0,-mv.z))); gl_Position=projectionMatrix*mv;}`, fragmentShader:`varying vec3 vColor; void main(){vec2 p=gl_PointCoord-vec2(.5); if(dot(p,p)>.25) discard; gl_FragColor=vec4(vColor,.92);}` });
  const cloud = new THREE.Points(geometry, material); scene.add(cloud);
  const raycaster = new THREE.Raycaster(); raycaster.params.Points.threshold = .055; const pointer = new THREE.Vector2(); let dragging=false, px=0, py=0;
  const render = () => renderer.render(scene,camera); render();
  renderer.domElement.addEventListener("pointerdown", (e) => { dragging=true; px=e.clientX; py=e.clientY; renderer.domElement.setPointerCapture(e.pointerId); });
  renderer.domElement.addEventListener("pointerup", () => { dragging=false; });
  renderer.domElement.addEventListener("pointermove", (e) => { if(dragging){cloud.rotation.y += (e.clientX-px)*.008; cloud.rotation.x += (e.clientY-py)*.008; px=e.clientX; py=e.clientY; render(); return;} const rect=renderer.domElement.getBoundingClientRect(); pointer.x=((e.clientX-rect.left)/rect.width)*2-1; pointer.y=-((e.clientY-rect.top)/rect.height)*2+1; raycaster.setFromCamera(pointer,camera); const hit=raycaster.intersectObject(cloud,false)[0]; if(hit) showTooltip(viewerState.points[hit.index], e.clientX, e.clientY); else hideTooltip(); });
  renderer.domElement.addEventListener("wheel", (e) => { e.preventDefault(); camera.position.z = clamp(camera.position.z + Math.sign(e.deltaY)*.25,2.1,8); render(); }, { passive:false });
  viewerState.three = { renderer, geometry, material, mount };
}

function destroyThree() {
  const current = viewerState.three; if (!current) return;
  current.geometry.dispose(); current.material.dispose(); current.renderer.dispose(); current.mount.innerHTML = ""; viewerState.three = null;
}

function drawThreeCanvasFallback() {
  const { canvas, ctx } = canvasContext(); const normalized = normalizeProjected3(); const [amin,amax]=activityDomain(); viewerState.screenPoints=[];
  normalized.map((row,index)=>({row,index,z:row[2]})).sort((a,b)=>a.z-b.z).forEach(({row,index})=>{ const depth=1.8+row[2]*.35; const x=canvas.width/2+row[0]*canvas.width*.34/depth+row[2]*45; const y=canvas.height/2-row[1]*canvas.height*.34/depth-row[2]*22; const point=viewerState.points[index]; const r=pointRadius(point); ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=activityColor(point.activity,amin,amax);ctx.fill(); viewerState.screenPoints.push({x,y,radius:r+5,index}); });
}

function drawCorrelation() {
  const { canvas, ctx } = canvasContext(); const matrix = correlationMatrix(viewerState.points.map((p)=>p.coords)); const size=Math.min(82,(canvas.height-90)/5); const ox=(canvas.width-size*5)/2, oy=48;
  ctx.font="13px ui-monospace,monospace"; ctx.textAlign="center";
  for(let i=0;i<5;i++){ctx.fillStyle="rgba(210,225,235,.8)";ctx.fillText(`D${i+1}`,ox+i*size+size/2,oy-14);ctx.fillText(`D${i+1}`,ox-28,oy+i*size+size/2+4);for(let j=0;j<5;j++){const v=matrix[i][j];const hue=v>=0?210:10;const alpha=.12+.72*Math.abs(v);ctx.fillStyle=`hsla(${hue},72%,52%,${alpha})`;ctx.fillRect(ox+j*size,oy+i*size,size-3,size-3);ctx.fillStyle="#f1f6f8";ctx.fillText(v.toFixed(2),ox+j*size+size/2,oy+i*size+size/2+4);}}
  ctx.textAlign="left"; ctx.fillStyle="rgba(210,225,235,.65)"; ctx.fillText("Pearson-Korrelation der fünf kanonischen Koordinaten",20,canvas.height-18);
}
function correlationMatrix(rows) {
  const means=[0,0,0,0,0]; rows.forEach(r=>r.forEach((v,i)=>means[i]+=v)); means.forEach((_,i)=>means[i]/=Math.max(1,rows.length));
  return Array.from({length:5},(_,i)=>Array.from({length:5},(_,j)=>{let num=0,di=0,dj=0;for(const r of rows){const a=r[i]-means[i],b=r[j]-means[j];num+=a*b;di+=a*a;dj+=b*b;}return di&&dj?num/Math.sqrt(di*dj):0;}));
}
function drawParallelCoordinates() {
  const { canvas, ctx } = canvasContext(); const rows=viewerState.points; const mins=[0,1,2,3,4].map(d=>Math.min(...rows.map(p=>p.coords[d]))), maxs=[0,1,2,3,4].map(d=>Math.max(...rows.map(p=>p.coords[d]))); const [amin,amax]=activityDomain(); const padX=80,padY=45,step=(canvas.width-padX*2)/4;
  ctx.strokeStyle="rgba(170,190,205,.3)";ctx.fillStyle="rgba(210,225,235,.72)";ctx.font="12px ui-monospace,monospace";for(let d=0;d<5;d++){const x=padX+d*step;ctx.beginPath();ctx.moveTo(x,padY);ctx.lineTo(x,canvas.height-padY);ctx.stroke();ctx.fillText(`D${d+1}`,x-8,24);}
  rows.forEach(point=>{ctx.beginPath();point.coords.forEach((value,d)=>{const x=padX+d*step;const y=canvas.height-padY-((value-mins[d])/Math.max(1e-12,maxs[d]-mins[d]))*(canvas.height-padY*2);if(d===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.strokeStyle=activityColor(point.activity,amin,amax).replace("hsl(","hsla(").replace("%)","%,.18)");ctx.lineWidth=.7;ctx.stroke();});
}

function handleCanvasHover(event) {
  if (!viewerState.screenPoints.length || viewerState.view !== "projection") return hideTooltip();
  const canvas = byId("nmv-canvas"), rect = canvas.getBoundingClientRect(); const x=(event.clientX-rect.left)*canvas.width/rect.width, y=(event.clientY-rect.top)*canvas.height/rect.height;
  let hit=null,best=Infinity;for(const p of viewerState.screenPoints){const d=(p.x-x)**2+(p.y-y)**2;if(d<p.radius**2&&d<best){hit=p;best=d;}}
  if(hit) showTooltip(viewerState.points[hit.index],event.clientX,event.clientY);else hideTooltip();
}
function showTooltip(point, clientX, clientY) {
  const tooltip=byId("nmv-tooltip"); if(!tooltip)return; const stage=tooltip.parentElement.getBoundingClientRect(); tooltip.innerHTML=`<strong>Neuron ${esc(point.id)}</strong><br>5D: [${point.coords.map((v)=>esc(v)).join(", ")}]<br>Aktivität: ${point.activity.toFixed(3)}<br>Verbindungsdichte: ${point.degree == null ? "—" : point.degree}${viewerState.densityComplete ? "" : " (bounded sample)"}<br>Rolle: ${point.input?"Input ":""}${point.output?"Output":"" || "intern"}`; tooltip.style.left=`${clamp(clientX-stage.left+14,8,stage.width-330)}px`;tooltip.style.top=`${clamp(clientY-stage.top+14,8,stage.height-135)}px`;tooltip.hidden=false;
}
function hideTooltip(){const tooltip=byId("nmv-tooltip");if(tooltip)tooltip.hidden=true;}
function renderEmpty(message){destroyThree();const {canvas,ctx}=canvasContext();ctx.fillStyle="rgba(210,225,235,.68)";ctx.font="15px system-ui,sans-serif";ctx.textAlign="center";ctx.fillText(message,canvas.width/2,canvas.height/2);ctx.textAlign="left";}

function init() { createViewer(); }
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once:true }); else init();

window.Brain5DNeuronModelViewer = { refresh: refreshViewer, computePca };
