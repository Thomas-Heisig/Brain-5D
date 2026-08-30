/**
 * Brain-5D Dashboard — IO Flow Visualization
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

export async function refreshIOFlow() {
  try {
    const r = await fetch('/api/live/io-flow', { cache: 'no-store' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();

    setText('io-input-count', formatNumber(data.input_count));
    setText('io-input-rate', formatFloat(data.input_mean_rate, 4));
    const inputFill = $('io-input-fill');
    if (inputFill) inputFill.style.width = Math.min(100, data.input_mean_rate * 200) + '%';

    setText('io-hidden-count', formatNumber(data.hidden_count));
    setText('io-hidden-rate', formatFloat(data.hidden_mean_rate, 4));
    const hiddenFill = $('io-hidden-fill');
    if (hiddenFill) hiddenFill.style.width = Math.min(100, data.hidden_mean_rate * 200) + '%';

    setText('io-output-count', formatNumber(data.output_count));
    setText('io-output-rate', formatFloat(data.output_mean_rate, 4));
    const outputFill = $('io-output-fill');
    if (outputFill) outputFill.style.width = Math.min(100, data.output_mean_rate * 200) + '%';

    const badge = $('io-flow-badge');
    if (badge) {
      if (data.propagation_active) {
        badge.textContent = '✅ Signalfluss aktiv';
        badge.className = 'gate-badge passed';
      } else {
        badge.textContent = '⏳ Signal abgebrochen';
        badge.className = 'gate-badge pending';
      }
    }

    const meta = $('io-flow-meta');
    if (meta) {
      meta.textContent = `Tick ${data.tick} · Input ${data.input_mean_rate.toFixed(4)} → Hidden ${data.hidden_mean_rate.toFixed(4)} → Output ${data.output_mean_rate.toFixed(4)} · ${data.source}`;
    }
  } catch (e) {
    const badge = $('io-flow-badge');
    if (badge) {
      badge.textContent = '⚠️ offline';
      badge.className = 'gate-badge failed';
    }
    const meta = $('io-flow-meta');
    if (meta) meta.textContent = '⚠️ IO-Fluss nicht verfügbar';
  }
}
