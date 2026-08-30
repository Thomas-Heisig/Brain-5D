/**
 * Brain-5D Dashboard — Dynamics Visualizations (Raster, Histogram, Layer Explorer)
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

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = String(value);
}

export async function refreshSpikeRaster() {
  try {
    const r = await fetch('/api/live/raster', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawSpikeRaster(data);
    const badge = $('raster-badge');
    if (badge) {
      badge.textContent = `${data.sample_count}/${data.total_neurons} Neuronen`;
      badge.className = 'gate-badge passed';
    }
    const meta = $('raster-meta');
    if (meta) meta.textContent = `Tick ${data.tick} · Fenster: ${data.window_ticks} Ticks · ${data.sample_count} aktive Neuronen von ${data.total_neurons}`;
  } catch {
    const badge = $('raster-badge');
    if (badge) { badge.textContent = 'offline'; badge.className = 'gate-badge failed'; }
  }
}

function drawSpikeRaster(data) {
  const canvas = $('spike-raster');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const nids = data.neuron_ids || [];
  const ticks = data.spike_ticks || [];
  if (!nids.length || !ticks.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Spike-Daten im aktuellen Fenster', canvas.width/2, canvas.height/2);
    return;
  }

  const windowTicks = data.window_ticks || 100;
  const tick = data.tick || 0;
  const tickMin = tick - windowTicks;
  const tickMax = tick;

  const neuronCount = nids.length;
  const idToRow = {};
  nids.forEach((id, i) => { idToRow[id] = i; });

  const margin = { top: 20, right: 20, bottom: 30, left: 50 };
  const plotW = canvas.width - margin.left - margin.right;
  const plotH = canvas.height - margin.top - margin.bottom;

  ctx.fillStyle = '#050d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = 'rgba(142, 178, 193, 0.06)';
  ctx.lineWidth = 0.5;
  for (let i = 0; i < 10; i++) {
    const y = margin.top + (plotH / 10) * i;
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(margin.left + plotW, y);
    ctx.stroke();
  }

  ctx.fillStyle = 'rgba(64, 224, 208, 0.6)';
  for (let i = 0; i < ticks.length; i++) {
    const t = ticks[i];
    const nid = nids[i % nids.length];
    const row = idToRow[nid];
    if (row === undefined) continue;
    const x = margin.left + ((t - tickMin) / Math.max(1, tickMax - tickMin)) * plotW;
    const y = margin.top + (row / Math.max(1, neuronCount)) * plotH;
    ctx.fillRect(x - 0.5, y - 1, 2, 2);
  }

  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('Tick →', margin.left + plotW/2, canvas.height - 5);
  ctx.textAlign = 'right';
  ctx.fillText('Neuron ↑', margin.left - 5, margin.top + 12);
  ctx.textAlign = 'left';
  ctx.fillStyle = 'rgba(142, 178, 193, 0.3)';
  ctx.font = '9px monospace';
  ctx.fillText(tickMin, margin.left, canvas.height - 8);
  ctx.textAlign = 'right';
  ctx.fillText(tickMax, margin.left + plotW, canvas.height - 8);
}

export async function refreshRateHistogram() {
  try {
    const r = await fetch('/api/live/histogram?bins=30', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawRateHistogram(data);
    const stats = $('histogram-stats');
    if (stats) {
      stats.textContent = `μ=${data.mean_rate.toFixed(4)} σ=${data.std_rate.toFixed(4)}`;
      stats.className = 'gate-badge passed';
    }
    const meta = $('histogram-meta');
    if (meta) meta.textContent = `Tick ${data.tick} · ${data.active_count} aktiv / ${data.silent_count} stumm · Median ${data.median_rate.toFixed(4)}`;
  } catch {
    const stats = $('histogram-stats');
    if (stats) { stats.textContent = 'offline'; stats.className = 'gate-badge failed'; }
  }
}

function drawRateHistogram(data) {
  const canvas = $('rate-histogram');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const bins = data.bins || [];
  const counts = data.counts || [];
  if (!counts.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Histogramm-Daten', canvas.width/2, canvas.height/2);
    return;
  }

  const margin = { top: 20, right: 20, bottom: 35, left: 60 };
  const plotW = canvas.width - margin.left - margin.right;
  const plotH = canvas.height - margin.top - margin.bottom;

  ctx.fillStyle = '#050d14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const maxCount = Math.max(...counts, 1);
  const barW = plotW / counts.length;

  for (let i = 0; i < counts.length; i++) {
    const x = margin.left + i * barW;
    const h = (counts[i] / maxCount) * plotH;
    const y = margin.top + plotH - h;
    const normalized = counts[i] / maxCount;
    const hue = 210 - normalized * 195;
    ctx.fillStyle = `hsl(${hue}, 85%, ${30 + normalized * 40}%)`;
    ctx.fillRect(x + 1, y, barW - 2, h);
  }

  if (data.mean_rate > 0 && bins.length > 1) {
    const maxRate = bins[bins.length - 1];
    const meanX = margin.left + (data.mean_rate / maxRate) * plotW;
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.7)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(meanX, margin.top);
    ctx.lineTo(meanX, margin.top + plotH);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255, 159, 28, 0.7)';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('μ=' + data.mean_rate.toFixed(3), meanX, margin.top - 4);
  }

  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('Feuerrate (spikes/tick) →', margin.left + plotW/2, canvas.height - 5);
  ctx.textAlign = 'right';
  ctx.fillText('Anzahl ↑', margin.left - 5, margin.top + 12);
}

export async function refreshLayerExplorer() {
  const dimSelect = $('layer-dim');
  const slider = $('layer-slider');
  const kindSelect = $('layer-kind');
  if (!dimSelect || !slider) return;

  const dim = dimSelect.value;
  const layerVal = parseInt(slider.value, 10);
  const kind = kindSelect ? kindSelect.value : 'activity';

  try {
    const r = await fetch(`/api/live/projection?kind=${encodeURIComponent(kind)}&resolution=40`, { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawLayerSlice(data, dim, layerVal);

    const badge = $('layer-badge');
    if (badge) badge.textContent = dim.toUpperCase();

    const meta = $('layer-meta');
    if (meta) meta.textContent = `Tick ${data.tick} · ${dim.toUpperCase()}=${layerVal} · ${data.kind || kind} · ${data.source}`;
  } catch {
    const meta = $('layer-meta');
    if (meta) meta.textContent = '⚠️ Layer-Daten nicht verfügbar';
  }
}

function drawLayerSlice(payload, dim, layerValue) {
  const canvas = $('layer-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const values = payload.values || [];
  if (!values.length) return;

  const rows = values.length;
  const cols = values[0]?.length || 1;
  const flat = values.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  if (!flat.length) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Daten', canvas.width/2, canvas.height/2);
    return;
  }
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  const cellW = canvas.width / cols;
  const cellH = canvas.height / rows;

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const val = values[y]?.[x];
      if (val === null || val === undefined) {
        ctx.fillStyle = 'rgba(40, 50, 65, 0.4)';
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      } else {
        const normalized = (val - min) / range;
        const hue = 210 - normalized * 195;
        const light = 16 + normalized * 50;
        ctx.fillStyle = `hsl(${hue}, 88%, ${light}%)`;
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      }
    }
  }

  ctx.fillStyle = 'rgba(142, 178, 193, 0.4)';
  ctx.font = '10px monospace';
  ctx.textAlign = 'left';
  ctx.fillText(`${dim.toUpperCase()}=${layerValue}`, 8, 16);
  ctx.textAlign = 'right';
  ctx.fillText(`${min.toFixed(2)} … ${max.toFixed(2)}`, canvas.width - 8, 16);
}
