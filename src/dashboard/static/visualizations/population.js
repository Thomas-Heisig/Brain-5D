/**
 * Brain-5D Dashboard — Population Overview Visualization
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

export async function refreshPopulation() {
  try {
    const r = await fetch('/api/live/population', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    const badge = $('ei-ratio-badge');
    if (badge) {
      const ratio = data.ei_ratio;
      badge.textContent = `E/I: ${ratio.toFixed(2)}`;
      badge.className = `gate-badge ${ratio > 0.5 && ratio < 3.0 ? 'passed' : 'stale'}`;
    }

    const grid = $('population-grid');
    if (!grid) return;

    if (!data.populations || data.populations.length === 0) {
      grid.innerHTML = '<div class="population-empty">Keine Populationsdaten verfügbar.</div>';
    } else {
      grid.innerHTML = data.populations.map(p => {
        const activePct = (p.active_fraction * 100).toFixed(1);
        const barColor = p.name.includes('inhib') ? '#ff5d73'
          : p.name.includes('excit') ? '#40e0a8'
          : p.name.includes('sensory') ? '#4a7cf7'
          : p.name.includes('motor') ? '#f0a840'
          : '#8899bb';
        return `
          <div class="population-card">
            <div class="population-card-header">
              <span class="population-name">${escapeHtml(p.name)}</span>
              <span class="population-count">${formatNumber(p.count)}</span>
            </div>
            <div class="population-stats">
              <div class="population-stat"><dt>Rate</dt><dd>${formatFloat(p.mean_rate, 4)} spikes/tick</dd></div>
              <div class="population-stat"><dt>Energie</dt><dd>${formatFloat(p.mean_energy, 4)}</dd></div>
              <div class="population-stat"><dt>Membran V</dt><dd>${formatFloat(p.mean_v, 3)}</dd></div>
              <div class="population-stat"><dt>Aktiv</dt><dd>${formatNumber(p.active_count)} / ${formatNumber(p.count)} (${activePct}%)</dd></div>
            </div>
            <div class="population-bar">
              <div class="population-bar-fill" style="width:${activePct}%;background:${barColor};"></div>
            </div>
          </div>
        `;
      }).join('');
    }

    const meta = $('population-meta');
    if (meta) {
      meta.textContent = `Tick ${data.tick} · E: ${data.total_excitatory} / I: ${data.total_inhibitory} · ${data.source}`;
    }
  } catch (e) {
    const badge = $('ei-ratio-badge');
    if (badge) {
      badge.textContent = 'E/I: —';
      badge.className = 'gate-badge';
    }
    const grid = $('population-grid');
    if (grid) {
      grid.innerHTML = '<div class="population-empty">⚠️ Populationsdaten nicht verfügbar.</div>';
    }
  }
}
