/**
 * Brain-5D Dashboard — Network Tab Coordinator
 *
 * Owns all scientific visualizations on the NETWORK tab.
 * Lazy-initializes when the tab is first activated and manages refresh intervals.
 *
 * @version 1.0.0
 * @license MIT
 */

"use strict";

import {
  refreshLiveProjection,
  setHeatmapKind,
  toggleLiveSource,
  updateSourceBadge,
} from './visualizations/heatmap.js';

const $ = (id) => document.getElementById(id);
const $$ = (sel) => document.querySelectorAll(sel);

let initialized = false;
let intervals = {};

function clearAllIntervals() {
  Object.values(intervals).forEach(timer => clearInterval(timer));
  intervals = {};
}

function startInterval(name, fn, ms) {
  if (intervals[name]) clearInterval(intervals[name]);
  intervals[name] = setInterval(fn, ms);
}

function bindHeatmapControls() {
  $$('button[data-kind]').forEach(button => {
    button.addEventListener('click', () => {
      setHeatmapKind(button.dataset.kind);
      $$('button[data-kind]').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      refreshLiveProjection();
    });
  });

  const liveToggle = $('live-toggle');
  if (liveToggle) {
    liveToggle.addEventListener('click', () => {
      const live = toggleLiveSource();
      updateSourceBadge();
      if (live) {
        refreshLiveProjection();
      } else {
        refreshHeatmap();
      }
    });
  }
}

export function initNetworkTab() {
  if (initialized) return;
  console.log('🧠 Network tab initializing...');

  bindHeatmapControls();

  refreshLiveProjection();
  startInterval('liveProjection', refreshLiveProjection, 2500);

  updateSourceBadge();
  initialized = true;
  console.log('✅ Network core view ready');
}
