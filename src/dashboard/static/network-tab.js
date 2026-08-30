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
  refreshHeatmap,
  refreshLiveProjection,
  setHeatmapKind,
  toggleLiveSource,
  updateSourceBadge,
} from './visualizations/heatmap.js';
import { refreshIOFlow } from './visualizations/io-flow.js';
import { refreshPopulation } from './visualizations/population.js';
import {
  refreshSpikeRaster,
  refreshRateHistogram,
  refreshLayerExplorer,
} from './visualizations/dynamics.js';
import {
  refreshNetworkSummary,
  loadNeuronPage,
  loadSynapsePage,
  loadProjection,
} from './visualizations/inspector.js';

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

function bindDynamicsControls() {
  const slider = $('layer-slider');
  const dimSelect = $('layer-dim');
  const kindSelect = $('layer-kind');
  const layerVal = $('layer-value');
  if (slider) {
    slider.addEventListener('input', () => {
      if (layerVal) layerVal.textContent = slider.value;
    });
    slider.addEventListener('change', refreshLayerExplorer);
  }
  if (dimSelect) dimSelect.addEventListener('change', refreshLayerExplorer);
  if (kindSelect) kindSelect.addEventListener('change', refreshLayerExplorer);
}

function bindInspectorControls() {
  const refreshBtn = $('inspect-refresh');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshNetworkSummary();
      loadNeuronPage();
      loadSynapsePage();
      loadProjection();
    });
  }

  const neuronLoad = $('neuron-load');
  if (neuronLoad) neuronLoad.addEventListener('click', loadNeuronPage);

  const synapseLoad = $('synapse-load');
  if (synapseLoad) synapseLoad.addEventListener('click', loadSynapsePage);

  const projMode = $('projection-mode');
  if (projMode) projMode.addEventListener('change', loadProjection);
}

export function initNetworkTab() {
  if (initialized) return;
  console.log('🧠 Network tab initializing...');

  bindHeatmapControls();

  refreshHeatmap();
  refreshLiveProjection();
  refreshIOFlow();
  refreshPopulation();

  startInterval('heatmap', refreshHeatmap, 5000);
  startInterval('liveProjection', refreshLiveProjection, 500);
  startInterval('ioFlow', refreshIOFlow, 2000);
  startInterval('population', refreshPopulation, 2000);

  initDynamicsTab();
  initInspectTab();

  updateSourceBadge();
  initialized = true;
  console.log('✅ Network tab ready');
}

function initDynamicsTab() {
  console.log('📈 Dynamics tab initializing...');
  refreshSpikeRaster();
  refreshRateHistogram();
  refreshLayerExplorer();

  bindDynamicsControls();

  startInterval('spikeRaster', refreshSpikeRaster, 2000);
  startInterval('rateHistogram', refreshRateHistogram, 2000);
  startInterval('layerExplorer', refreshLayerExplorer, 3000);

  console.log('✅ Dynamics tab ready');
}

function initInspectTab() {
  console.log('🔍 Inspect tab initializing...');
  refreshNetworkSummary();
  loadNeuronPage();
  loadSynapsePage();
  loadProjection();

  bindInspectorControls();

  startInterval('networkSummary', refreshNetworkSummary, 2000);

  console.log('✅ Inspect tab ready');
}
