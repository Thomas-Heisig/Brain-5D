/**
 * Brain-5D Dashboard — Heatmap & 5D Projection Visualization
 *
 * Polls scientific endpoints directly; large data remains lazy-loaded.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

const $ = (id) => document.getElementById(id);

export let heatmapKind = 'activity';
export let liveSource = true;

function formatFloat(value, decimals = 3) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(decimals);
}

function formatNumber(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString();
}

function heatmapColor(value, min, max) {
  const scale = max > min ? (value - min) / (max - min) : 0;
  const t = Math.max(0, Math.min(1, scale));
  const hue = 210 - (195 * t);
  const light = 16 + (46 * t);
  return `hsl(${hue}, 88%, ${light}%)`;
}

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = String(value);
}

export function setHeatmapKind(kind) {
  heatmapKind = kind;
}

export function toggleLiveSource() {
  liveSource = !liveSource;
  return liveSource;
}

export function updateSourceBadge(telemetryStatus) {
  const badge = $('source-badge');
  if (!badge) return;

  if (!liveSource) {
    badge.textContent = 'SNAPSHOT';
    badge.className = 'badge badge-snapshot';
    return;
  }

  const status = telemetryStatus || (document.getElementById('heatmap-meta')?.dataset?.telemetryStatus);
  if (status === 'stale') {
    badge.textContent = 'STALE';
    badge.className = 'badge badge-stale';
    return;
  }
  if (status === 'unavailable') {
    badge.textContent = 'UNAVAILABLE';
    badge.className = 'badge badge-unavailable';
    return;
  }

  badge.textContent = 'LIVE';
  badge.className = 'badge badge-live';
}

export function drawHeatmap(payload) {
  const canvas = $('heatmap');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const rows = payload.values || [];
  if (!rows.length || !rows[0]?.length) {
    setText('heatmap-meta', payload.error || 'Keine Heatmap-Daten verfügbar.');
    return;
  }

  const valid = rows.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  const min = valid.length > 0 ? Math.min(...valid) : 0;
  const max = valid.length > 0 ? Math.max(...valid) : 0;
  const width = rows[0].length;
  const height = rows.length;
  const cellW = canvas.width / width;
  const cellH = canvas.height / height;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const val = rows[y][x];
      if (val === null || val === undefined) {
        ctx.fillStyle = 'rgba(40, 50, 65, 0.4)';
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
        ctx.strokeStyle = 'rgba(60, 70, 85, 0.3)';
        ctx.lineWidth = 0.5;
        const cx = x * cellW;
        const cy = y * cellH;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + cellW, cy + cellH);
        ctx.moveTo(cx + cellW, cy);
        ctx.lineTo(cx, cy + cellH);
        ctx.stroke();
      } else {
        ctx.fillStyle = heatmapColor(val, min, max);
        ctx.fillRect(x * cellW, y * cellH, Math.ceil(cellW), Math.ceil(cellH));
      }
    }
  }

  setText(
    'heatmap-meta',
    `${payload.source === 'live_runtime' ? 'LIVE' : 'SNAPSHOT'} · ${payload.kind || heatmapKind} · Tick ${payload.tick || 0} · ${payload.sample_count || 0} Samples · ${formatFloat(min, 4)}…${formatFloat(max, 4)}`
  );

  const metaEl = $('heatmap-meta');
  if (metaEl && payload.telemetry && payload.telemetry.status) {
    metaEl.dataset.telemetryStatus = payload.telemetry.status;
  }

  draw5DProjection(payload);
}

export async function refreshHeatmap() {
  const canvas = $('heatmap');
  if (!canvas) return;

  try {
    const response = await fetch(
      `/api/heatmap?kind=${encodeURIComponent(heatmapKind)}`,
      { cache: 'no-store' }
    );
    if (!response.ok) {
      const data = await response.json();
      setText('heatmap-meta', data.error || `Heatmap HTTP ${response.status}`);
      return;
    }
    drawHeatmap(await response.json());
  } catch (error) {
    setText('heatmap-meta', '⚠️ Heatmap nicht erreichbar.');
  }
}

export async function refreshLiveProjection() {
  const canvas = $('heatmap');
  if (!canvas) return;
  if (!liveSource) return;

  try {
    const response = await fetch(
      `/api/live/projection?kind=${encodeURIComponent(heatmapKind)}&resolution=50`,
      { cache: 'no-store' }
    );
    if (!response.ok) {
      if (liveSource) {
        liveSource = false;
        updateSourceBadge();
      }
      return;
    }
    const data = await response.json();
    drawHeatmap(data);
    updateSourceBadge(data.telemetry?.status);
  } catch {
    // Silently fall back — snapshot will be used on next interval
  }
}

function draw5DProjection(payload) {
  const canvas = $('projection-5d');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const values = payload.values || [];
  if (!values.length) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const rows = values.length;
  const cols = values[0]?.length || 1;

  const cx = canvas.width / 2;
  const cy = canvas.height / 2 + 20;
  const scale = Math.min(canvas.width, canvas.height) * 0.35 / Math.max(rows, cols);

  const flat = values.flat().filter(v => v !== null && v !== undefined && Number.isFinite(v));
  if (flat.length === 0) {
    ctx.fillStyle = '#4a6a8a';
    ctx.font = '14px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Keine Daten', cx, cy);
    return;
  }
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const range = max - min || 1;

  ctx.strokeStyle = 'rgba(64, 224, 208, 0.06)';
  ctx.lineWidth = 0.5;
  const gridStep = 4;
  for (let y = 0; y < rows; y += gridStep) {
    for (let x = 0; x < cols; x += gridStep) {
      const gx1 = cx + (x - y) * scale * 0.7;
      const gy1 = cy + (x + y) * scale * 0.35;
      ctx.beginPath();
      ctx.arc(gx1, gy1, 1.5, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(64, 224, 208, 0.15)';
      ctx.fill();
    }
  }

  for (let y = 0; y < rows; y += 2) {
    for (let x = 0; x < cols; x += 2) {
      const val = values[y]?.[x];
      if (val === null || val === undefined) continue;
      const normalized = (val - min) / range;

      const isoX = (x - y) * scale * 0.7;
      const isoY = (x + y) * scale * 0.35 - normalized * scale * 2;

      const size = 2 + normalized * 5;
      const hue = 210 - normalized * 195;
      const light = 20 + normalized * 55;

      ctx.beginPath();
      ctx.arc(cx + isoX, cy + isoY, size, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
      ctx.fill();

      if (normalized > 0.6) {
        ctx.beginPath();
        ctx.arc(cx + isoX, cy + isoY, size * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${hue}, 85%, ${light}%, 0.15)`;
        ctx.fill();
      }
    }
  }

  ctx.strokeStyle = 'rgba(64, 224, 208, 0.08)';
  ctx.lineWidth = 0.5;
  for (let y = 0; y < rows - 2; y += 3) {
    for (let x = 0; x < cols - 2; x += 3) {
      const v1 = values[y]?.[x];
      const v2 = values[y]?.[x + 2];
      const v3 = values[y + 2]?.[x];
      if (v1 === null || v1 === undefined || v2 === null || v2 === undefined || v3 === null || v3 === undefined) continue;

      const n1 = (v1 - min) / range;
      const n2 = (v2 - min) / range;
      const n3 = (v3 - min) / range;

      const x1 = cx + (x - y) * scale * 0.7;
      const y1 = cy + (x + y) * scale * 0.35 - n1 * scale * 2;
      const x2 = cx + ((x + 2) - y) * scale * 0.7;
      const y2 = cy + ((x + 2) + y) * scale * 0.35 - n2 * scale * 2;
      const x3 = cx + (x - (y + 2)) * scale * 0.7;
      const y3 = cy + (x + (y + 2)) * scale * 0.35 - n3 * scale * 2;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x3, y3);
      ctx.stroke();
    }
  }

  ctx.fillStyle = 'rgba(142, 178, 193, 0.5)';
  ctx.font = '10px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('X →', cx + cols * scale * 0.35, cy + cols * scale * 0.17 + 12);
  ctx.fillText('Y →', cx - rows * scale * 0.35, cy + rows * scale * 0.17 + 12);
  ctx.fillText(`Z: ${min.toFixed(2)} … ${max.toFixed(2)}`, cx, 14);

  const dims = payload.dimensions || [];
  if (dims.length >= 5) {
    ctx.fillStyle = 'rgba(142, 178, 193, 0.35)';
    ctx.font = '9px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`5D: ${dims.join('×')}`, 8, canvas.height - 8);
  }
}
