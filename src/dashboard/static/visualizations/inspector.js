/**
 * Brain-5D Dashboard — Network Inspector (5D coordinates, tables, projection)
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

const $ = (id) => document.getElementById(id);

function formatNumber(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString();
}

function formatFloat(value, decimals = 3) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(decimals);
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = String(value);
}

export async function refreshNetworkSummary() {
  try {
    const r = await fetch('/api/network/summary', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    setText('inspect-dimensions', (d.dimensions || []).join(' × '));
    setText('inspect-neuron-count', formatNumber(d.neuron_count));
    setText('inspect-synapse-count', formatNumber(d.synapse_count));
    setText('inspect-input-count', formatNumber(d.input_count));
    setText('inspect-output-count', formatNumber(d.output_count));
    setText('inspect-active-neurons', formatNumber(d.active_neurons));
    setText('inspect-silent-neurons', formatNumber(d.silent_neurons));
    setText('inspect-queue-depth', formatNumber(d.queue_depth));
    setText('inspect-tick', formatNumber(d.current_tick));
    setText('inspect-total-spikes', formatNumber(d.total_spikes));
    setText('inspect-mean-energy', formatFloat(d.mean_energy, 4));
    setText('inspect-mean-v', formatFloat(d.mean_v, 4));
  } catch {
    ['inspect-dimensions','inspect-neuron-count','inspect-synapse-count','inspect-input-count',
     'inspect-output-count','inspect-active-neurons','inspect-silent-neurons','inspect-queue-depth',
     'inspect-tick','inspect-total-spikes','inspect-mean-energy','inspect-mean-v']
      .forEach(id => setText(id, '—'));
  }
}

export async function loadNeuronPage() {
  const limit = parseInt($('neuron-limit')?.value || '200', 10);
  const offset = parseInt($('neuron-offset')?.value || '0', 10);
  const activeOnly = $('neuron-active-only')?.checked || false;
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (activeOnly) params.set('active_only', 'true');
    const r = await fetch(`/api/network/neurons?${params}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    const body = $('neuron-table-body');
    if (!body) return;
    const rows = d.neurons || [];
    body.innerHTML = rows.map(n => `
      <tr>
        <td>${n.neuron_id}</td>
        <td>${n.x1}</td><td>${n.x2}</td><td>${n.x3}</td><td>${n.x4}</td><td>${n.x5}</td>
        <td>${formatFloat(n.v, 3)}</td>
        <td>${formatFloat(n.u, 3)}</td>
        <td>${formatFloat(n.energy, 4)}</td>
        <td>${n.last_spike < 0 ? '—' : n.last_spike}</td>
        <td>${n.spike_count}</td>
        <td>${n.is_input ? 'I' : (n.is_output ? 'O' : '')}</td>
      </tr>`).join('');
    setText('neuron-page-meta',
      `${d.returned}/${d.total} (offset ${d.offset}, limit ${d.limit}) · source: ${d.source}`);
  } catch (e) {
    const body = $('neuron-table-body');
    if (body) body.innerHTML = `<tr><td colspan="12">⚠️ ${escapeHtml(e.message)}</td></tr>`;
    setText('neuron-page-meta', '—');
  }
}

export async function loadSynapsePage() {
  const limit = parseInt($('synapse-limit')?.value || '200', 10);
  const offset = parseInt($('synapse-offset')?.value || '0', 10);
  const sourceRaw = $('synapse-source')?.value;
  const minWeightRaw = $('synapse-min-weight')?.value;
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (sourceRaw) params.set('source', sourceRaw);
    if (minWeightRaw) params.set('min_weight', minWeightRaw);
    const r = await fetch(`/api/network/synapses?${params}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    const body = $('synapse-table-body');
    if (!body) return;
    const rows = d.synapses || [];
    body.innerHTML = rows.map(s => `
      <tr>
        <td>${s.source_id}</td>
        <td>${s.target_id ?? '—'}</td>
        <td>${formatFloat(s.weight, 4)}</td>
        <td>${s.delay ?? '—'}</td>
        <td>${formatFloat(s.eligibility, 4)}</td>
      </tr>`).join('');
    setText('synapse-page-meta',
      `${d.returned}/${d.total} (offset ${d.offset}, limit ${d.limit}) · source: ${d.source}`);
  } catch (e) {
    const body = $('synapse-table-body');
    if (body) body.innerHTML = `<tr><td colspan="5">⚠️ ${escapeHtml(e.message)}</td></tr>`;
    setText('synapse-page-meta', '—');
  }
}

export async function loadProjection() {
  const canvas = $('inspect-projection');
  if (!canvas) return;
  const mode = $('projection-mode')?.value || 'activity';
  try {
    const r = await fetch(`/api/network/projection?limit=2000&mode=${encodeURIComponent(mode)}`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    drawInspectProjection(canvas, d);
    setText('projection-meta',
      `${d.label} · ${d.sample_count}/${d.total_count} samples · ${d.sampling_method} · source: ${d.source}`);
  } catch (e) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setText('projection-meta', `⚠️ ${e.message}`);
  }
}

function drawInspectProjection(canvas, payload) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const points = payload.points || [];
  if (!points.length) {
    setText('projection-meta', 'No projection data.');
    return;
  }

  const vals = points.map(p => p.value);
  const vMin = Math.min(...vals);
  const vMax = Math.max(...vals);
  const range = vMax - vMin || 1;

  const xs = points.map(p => p.x);
  const ys = points.map(p => p.y);
  const zs = points.map(p => p.z);
  const xMin = Math.min(...xs), xMax = Math.max(...xs);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const zMin = Math.min(...zs), zMax = Math.max(...zs);

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const scale = Math.min(canvas.width, canvas.height) * 0.35 / Math.max(xMax - xMin, yMax - yMin, zMax - zMin, 1);

  for (const p of points) {
    const nx = (p.x - xMin) / Math.max(xMax - xMin, 1);
    const ny = (p.y - yMin) / Math.max(yMax - yMin, 1);
    const nz = (p.z - zMin) / Math.max(zMax - zMin, 1);
    const valN = (p.value - vMin) / range;

    const px = cx + (nx - 0.5) * canvas.width * 0.8;
    const py = cy + (ny - 0.5) * canvas.height * 0.7 - nz * scale * 1.5;

    const size = 1.5 + valN * 4 + (p.is_input || p.is_output ? 2 : 0);
    const hue = 210 - valN * 195;
    const light = 20 + valN * 50;

    ctx.beginPath();
    ctx.arc(px, py, size, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
    ctx.fill();

    if (p.is_input || p.is_output) {
      ctx.strokeStyle = p.is_input ? '#40e0a8' : '#f0a840';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(px, py, size + 2, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  ctx.fillStyle = '#8899bb';
  ctx.font = '11px monospace';
  ctx.fillText('X,Y visible · Z=depth · D4/D5 in point data (filter TBD)', 10, canvas.height - 10);
}
