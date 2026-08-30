# Changelog

## 2026-08-30 — Viewer Improvements: Decoupling + Missing File Types + YAML Highlighting

### Viewer als eigenständiges Overlay-Element
- **`src/dashboard/static/index.html`**: Viewer (`fm-viewer`) ist jetzt standardmäßig ausgeblendet (`fm-viewer-hidden`) und öffnet sich als Overlay-Panel über der Sidebar, wenn eine Datei angeklickt wird.
- **`src/dashboard/static/app.js`**: Close-Button (✕) im Datei-Header. Klick schließt den Viewer und die Sidebar nimmt wieder die volle Breite ein.
- **`src/dashboard/static/styles.css`**: Viewer hat jetzt `z-index: 10`, Akzent-Rahmen und eine Übergangsanimation. Sidebar expandiert auf `flex: 1` wenn Viewer verborgen ist.

### Fehlende Dateitypen ergänzt
- **`src/dashboard/static/app.js`**: Neue Code-Dateitypen: `.bib` (BibTeX), `.patch`, `.rst`, `.tex`, `.sh`, `.bat`, `.ps1`, `.dockerfile`, `.cmake`, `.makefile`, `.txt`. JSON-Erkennung jetzt über `ext.endsWith('.json')` — fängt auch `.schema.json` und `.ipynb` ab.
- **`src/dashboard/static/index.html`**: Neue Filter-Chips für BibTeX und Patch.
- `.bib`-Dateien werden jetzt als Code (Syntax-Highlighting) statt als Plain Text angezeigt.
- `.patch`-Dateien werden jetzt als Code statt als Plain Text angezeigt.
- `.schema.json`-Dateien werden jetzt als JSON (mit Formatierung) statt als Plain Text angezeigt.

### YAML Syntax-Highlighting
- **`src/dashboard/static/app.js`**: Neue `renderFMYaml()` Funktion mit Syntax-Highlighting für YAML-Dateien. Farbliche Unterscheidung von: Keys (blau), Strings (orange), Kommentare (grün), Booleans (blau), Zahlen (hellgrün), Null-Werte (grau), List-Marker (gelb), Anchor/Alias (lila), Dokument-Separatoren (grau).
- **`src/dashboard/static/styles.css`**: 12 neue CSS-Klassen für YAML-Token-Farben im VS Code Dark Theme-Stil.

### Multi-Language Code Syntax-Highlighting
- **`src/dashboard/static/app.js`**: Neue `renderFMCode()` Funktion mit Syntax-Highlighting für alle Code-Dateitypen. Unterstützt 17 Sprachen:
  - **Python** (`.py`): Keywords, Builtins, Dekorateure, f-Strings, Magic Methods
  - **JavaScript/TypeScript** (`.js`, `.ts`): Keywords, Builtins, Template Literals
  - **HTML** (`.html`): Tags, Attribute, Entities
  - **CSS** (`.css`): Selektoren, Properties, Values, !important
  - **Shell/Batch/PowerShell** (`.sh`, `.bat`, `.ps1`): Keywords, Builtins, Variablen
  - **TOML/Config** (`.toml`, `.cfg`, `.conf`, `.ini`): Sections, Keys, Booleans, Datum
  - **XML** (`.xml`): Tags, Attribute, CDATA, Entities
  - **BibTeX** (`.bib`): Entry-Typen, Felder, Querverweise
  - **Patch/Diff** (`.patch`): Diff-Marker, Hunks, Add/Delete
  - **LaTeX** (`.tex`): Commands, Math-Umgebungen, Labels
  - **reStructuredText** (`.rst`): Directives, Roles, Sections
  - **Dockerfile**: Instructions, Variablen
- **`src/dashboard/static/styles.css`**: 25 neue CSS-Klassen für Code-Token-Farben (VS Code Dark+ Palette): Kommentare (grün), Keywords (blau), Builtins (cyan), Strings (orange), Zahlen (hellgrün), Dekorateure (gelb-grün), Tags (blau), Attribute (gelb), Selektoren (gelb), Properties (hellblau), Variablen (cyan), Sections (gelb), Diff-Marker (rot/grün), Hunk-Header (lila).

## 2026-08-29 — Dynamics Tab + Collapsible Architecture

### Neuer Dynamics Tab (Spike Raster, Rate Histogram, 5D Layer Explorer)
- **`src/dashboard/static/index.html`**: New "📈 Dynamics" tab with three panels:
  - **Spike Raster**: Canvas-drawn scatter plot of recent spike times (last 100 ticks) for the most active neurons. Shows spike density and firing patterns over time.
  - **Feuerraten-Histogramm**: Bar chart showing the distribution of firing rates across all neurons. Includes mean (μ) and standard deviation (σ) overlay, plus silent/active neuron counts.
  - **5D Layer Explorer**: Interactive slice through the 5D space. User selects dimension (Z, d4, d5), layer value via slider, and display kind (activity, energy, membrane). The heatmap updates in real-time.
- **`src/dashboard/static/app.js`**: New `initDynamicsTab()`, `refreshSpikeRaster()`, `drawSpikeRaster()`, `refreshRateHistogram()`, `drawRateHistogram()`, `refreshLayerExplorer()`, `drawLayerSlice()` functions. Lazy-initialized when tab is first clicked.
- **`src/dashboard/static/styles.css`**: New styles for raster, histogram, and layer explorer panels with dark theme canvas backgrounds and slider controls.

### Backend: Rate Histogram & Spike Raster Endpoints
- **`src/dashboard/live_projection.py`**: New `RateHistogramData`/`compute_rate_histogram()` — computes firing rate distribution with 30 bins, mean/median/std statistics, and silent/active counts.
- **`src/dashboard/live_projection.py`**: New `SpikeRasterData`/`compute_spike_raster()` — extracts recent spike times from the activity accumulator window for the most active neurons.
- **`src/dashboard/server.py`**: New `GET /api/live/histogram` and `GET /api/live/raster` endpoints.

### Tab-Architektur: Lazy Loading für Performance
- Dynamics Tab wird nur initialisiert, wenn der Benutzer ihn das erste Mal anklickt. Keine Canvas-Rendering-Last im Dashboard-Tab.
- Alle Dynamics-Panels haben eigene Refresh-Intervalle (2s Raster/Histogram, 3s Layer Explorer).

### Documentation
- `docs/changelog.md`: This entry.
- `docs/todo.md`: Added new API endpoints to truth sources list.

## 2026-08-28 — Dashboard Hardening + Engine Attach Fix

### Dashboard Disconnect Hardening
- **`src/dashboard/server.py`**: `_send_json()` now wraps the entire HTTP response emission (send_response, send_header, end_headers, wfile.write) in a single try/except for BrokenPipeError, ConnectionResetError, ConnectionAbortedError. Previously only wfile.write was protected.
- **`src/dashboard/server.py`**: `_handle_exception()` immediately returns for client disconnect errors at the top of the method, preventing a second write attempt on a dead socket.
- **`tests/test_dashboard_disconnect_hardening.py`**: 6 new regression tests covering disconnect at every stage of response emission.

### Engine Attach Fix (one confirmed cause of restore divergence)
- **`src/storage/core_restore.py`**: `restore_full()` now calls `.attach()` on created homeostasis and learning engines. Without attach(), the engines were passive — they existed but were not registered as post-step hooks. This was one confirmed cause of Path C divergence in the A/B/C protocol.
- After this fix, A and C match at K (restore point), but still diverge during K→N due to synapse list order after file restore affecting learning engine iteration.
- **B/C protocol not yet fully compliant** until fresh-process proof passes (see below).

### Restore A/B/C Protocol Correction
- **`tests/test_restore_determinism_abc.py`**: Complete protocol rewrite:
  - Path B now uses production `restore_full()` and asserts the restored network is a **different object**.
  - Path C now uses a real **subprocess** (`tests/_restore_worker.py`) — C1 runs 0→K in-process, C2 runs via `subprocess.run()` in a fresh Python process.
  - Stimulus schedule is now **absolute ticks** 0..N-1, serialized as JSON, shared by A, B, and C2.
  - All artifact proof fields are **machine-measured**, never hardcoded.
  - Artifact includes `pid_C1`, `pid_C2`, `config_sha256`, and all proof booleans.
- **Results**: `fresh_process_is_real=True` (PID 27804 vs 30296), `production_restore_path_used=True`, B==C. But A still diverges from B/C — the restore itself produces a different final state than uninterrupted running.

---

## 2026-08-28 — Hugging Face Repository Preparation

### New Files for Hugging Face
- **`HF_README.md`**: Hugging Face-spezifische README mit YAML Frontmatter (license, tags, pipeline_tag) und angepasstem Inhalt für die Hugging Face Platform.
- **`.huggingface/metadata.yaml`**: Repository-Metadaten für huggingface_hub (library_name, tags, card-info).
- **`.huggingface/space_config.yaml`**: Konfiguration für einen optionalen Hugging Face Space (Docker-basiert, Port 8765).
- **`.huggingface/README.md`**: Dokumentation zur Nutzung des Hugging Face Repositories.
- **`.github/workflows/sync-huggingface.yml`**: GitHub Actions Workflow zur automatischen Synchronisation von GitHub → Hugging Face.

### Infrastructure
- **`.gitattributes`**: Erweitert um Git LFS-Konfiguration für große Dateien (`.b5d`, `.ckpt`, `artifacts/`, Bilder, Model Weights).

---

## 2026-08-26 — Pre-Experiment Closure Sprint (Part 1)

### Gate Evidence Binding (Breaking Change)
- **`src/dashboard/gate_status.py`**: Replaced file-existence-based determinism checks with verification artifact (`research/generated/verification/determinism_infrastructure.json`). File existence alone no longer produces VERIFIED/PASSED status.
- Added `REQUIRED_DETERMINISM_PROOFS` with 7 proof IDs.
- Added `_read_determinism_artifact()` and `_determinism_infrastructure_verified()` methods with fail-closed validation.
- Error visibility criteria (experiment validity) now also use the determinism artifact.
- **`scripts/generate_determinism_artifact.py`**: New script to run determinism tests and produce the verification artifact.

### LearningEngine Determinism (Bug Fix)
- **`src/learning/learning_engine.py`**: Changed `_states` key from `id(synapse)` (Python memory address, non-deterministic across restarts) to stable `(pre_id, target_id)` tuples.
- Changed `events` dict key from `id(synapse)` to `(pre_id, target_id)`.
- Changed `set(spike_ids)` iteration to `sorted(set(...))` for deterministic order.
- Changed `events.values()` iteration to `sorted(events)` for deterministic order.
- Updated `get_eligibility()` and `_process_synapse_event()` to use stable keys.

### Production Restore Bundle (New Feature)
- **`src/storage/core_restore.py`**: Added `RestoredBundle` dataclass and `restore_full()` function that restores network + HomeostasisEngine + LearningEngine atomically.
- Fixed `restore_learning_state()` to use stable `(pre_id, target_id)` key lookup instead of linear scan with `id(synapse)` matching.
- Fixed `restore_learning_state()` to set `EligibilityTrace.value` instead of non-existent `_trace`.

### Tests
- **`tests/test_production_restore.py`**: New test file with 3 tests covering full restore bundle, engine-less restore, and continue-determinism.
- **`tests/test_engine_restore.py`**: Updated to use stable key lookup and correct `eligibility.value` attribute.

### Documentation
- `docs/todo.md`: Updated baseline to 367 passed, added determinism artifact info, updated gate status.
- `docs/ROADMAP.md`: Created with current status and future plans.
- `docs/changelog.md`: This file.

### Baseline
- `tests/test_baseline.json`: Updated to 367 passed, tree digest `dcd2d461...`.
- `research/generated/verification/determinism_infrastructure.json`: Created with 7/7 proofs verified.

---

## 2026-08-26 — Live Visualization & Verification Freshness Sprint (Part 2)

### Verification Artifact Generation Fix (Bug Fix)
- **`scripts/generate_determinism_artifact.py`**: Replaced custom `compute_tree_digest()` with canonical `compute_source_tree_digest()` from `src.dashboard.verification`. The custom function had different file filtering (only `.py/.toml/.yaml/.json/.cfg/.md`) and no path-interleaving, producing a different digest than the canonical function.
- Added `sys.path.insert(0, str(REPO_ROOT))` so the script can import from `src/`.
- Added `current_git_head()` function for provenance tracking.

### Verification Semantics Cleanup
- **`tests/test_structural_e2e.py`**, **`tests/test_structural_live_loop.py`**, **`tests/test_single_listener.py`**: Changed artifact field from `tested_commit` to `test_run_head` for semantic clarity. The tree digest is the freshness authority; commit hash is provenance only.
- **`scripts/generate_determinism_artifact.py`**: Uses `test_run_head` instead of `tested_commit`.

### Live Projection Service (New Feature)
- **`src/dashboard/live_projection.py`**: New module — `LiveProjectionService` reads directly from the in-memory `NeuralNetwork`, never from `.b5d` snapshots. Supports 5 projection kinds (activity, energy, membrane, spike, weight) with configurable aggregation (mean, max, sum, spike_count, active_fraction) and resolution (bins).
- **`src/dashboard/operator_bridge.py`**: Added `live_projection` attribute with automatic `LiveProjectionService` creation from the controller's network.
- **`src/dashboard/server.py`**: Added `GET /api/live/projection` endpoint with parameters: `kind`, `dimension_x`, `dimension_y`, `resolution`, `aggregation`. Response tagged as `live_runtime`.
- **`src/dashboard/heatmap_source.py`**: Added `source: str = "snapshot"` field to `HeatmapPayload` to distinguish from live data.

### LIVE vs SNAPSHOT Separation
- **`src/dashboard/static/index.html`**: Added `#source-badge` element showing LIVE or SNAPSHOT. Added `#live-toggle` button. Added membrane and spike kind buttons. Changed subtitle to show source badge.
- **`src/dashboard/static/app.js`**: Added `liveSource` toggle variable. Added `refreshLiveProjection()` function polling `/api/live/projection` at 500ms. Added `updateSourceBadge()` function. Heatmap metadata now shows source prefix (LIVE/SNAPSHOT).
- **`src/dashboard/static/styles.css`**: Added `.badge`, `.badge-live`, `.badge-snapshot`, `.provenance-badge` styles with distinct green (LIVE) and amber (SNAPSHOT) colors.

### Tests
- **`tests/test_live_projection.py`**: 12 tests covering energy accuracy, activity timing, weight projection, tick coherence, no-mutation guarantee, snapshot separation, bounded payload, and invalid parameter handling.

---

## 2026-08-29 — Dashboard Enhancement Sprint (Part 3)

### IO-Fluss Visualisierung (New Feature)
- **`src/dashboard/live_projection.py`**: New `IOFlowData` dataclass and `compute_io_flow()` function that analyzes signal propagation from input cells through hidden layers to output cells. Returns per-layer activity rates, neuron counts, and propagation status.
- **`src/dashboard/server.py`**: New `GET /api/live/io-flow` endpoint that reads directly from the live network. Uses the TelemetryFrameStore's ActivityWindowAccumulator for rolling window rates.
- **`src/dashboard/static/index.html`**: New IO-Fluss panel with three-layer flow visualization (Input → Hidden → Output), activity bars, rate displays, and propagation status badge.
- **`src/dashboard/static/app.js`**: New `refreshIOFlow()` function polling `/api/live/io-flow` at 2s intervals. Updates flow bars, layer stats, and propagation badge.
- **`src/dashboard/static/styles.css`**: New `.io-flow-panel`, `.io-flow-grid`, `.io-flow-layer` styles with color-coded layer borders (input=teal, hidden=blue, output=amber).

### Populationen-Übersicht (New Feature)
- **`src/dashboard/live_projection.py`**: New `PopulationData`/`_PopulationEntry` dataclasses and `compute_population_data()` function that groups neurons by type (excitatory, inhibitory, sensory_input, motor_output) with per-population statistics.
- **`src/dashboard/server.py`**: New `GET /api/live/population` endpoint returning population metrics including E/I ratio.
- **`src/dashboard/static/index.html`**: New Population panel with dynamic card grid showing per-type stats and active-fraction progress bars.
- **`src/dashboard/static/app.js`**: New `refreshPopulation()` function polling `/api/live/population` at 2s intervals. Renders population cards with rate, energy, membrane V, and activity bars.
- **`src/dashboard/static/styles.css`**: New `.population-panel`, `.population-card`, `.population-bar` styles with color-coded progress bars per population type.

### Verbesserte 5D Isometrische Projektion
- **`src/dashboard/static/app.js`**: Enhanced `draw5DProjection()` with isometric floor grid, axis labels (X, Y), Z-range legend, and 5D dimension info overlay. Better visual depth perception with grid dots and glow effects.

### Documentation
- `docs/ROADMAP.md`: Added Dashboard Enhancement Sprint section with 4 completed items.
- `docs/changelog.md`: This entry.
- `docs/todo.md`: Added new dashboard API endpoints to truth sources list.

### Verification Freshness Restored
- All 5 verification artifacts now share the same `tested_tree_digest`.
- `tests/test_baseline.json`: 379 passed, 0 failed, 2 skipped.

### Baseline
- `tests/test_baseline.json`: 379 passed, canonical tree digest.
- All structural and determinism artifacts regenerated with matching digests.

---

## 2026-08-26 — Live Visualization Correctness Sprint (Part 3)

### Critical Bug Fixes

1. **`unpack_coords` correction** — `LiveProjectionService` now uses `src.core.spatial_index.unpack_coords()` (the canonical packed-5D decoder) instead of a custom `_unpack_coord()` that treated neuron IDs as linear row-major indices. This was the root cause of neurons appearing in wrong spatial bins.

2. **Activity is now a real firing-rate estimate** — Replaced `1.0 / max(1, age)` (recency of last spike) with `1.0 / window` (firing rate over the activity window). The old implementation gave identical activity to neurons with very different spike counts if their last spike was equally recent.

3. **Empty bins = null, not 0** — Bins with no neurons now return `None` in the `values` array, with a corresponding `mask` boolean array. The range (min/max/mean) is computed only over non-empty bins. This prevents empty regions from distorting the color scale.

4. **Aggregation semantics are now correct** — `_final_value()` dispatches correctly:
   - `mean`: sum/count
   - `sum` / `spike_count`: raw sum (no division)
   - `max`: stored max value (separate accumulator)
   - `active_fraction`: active_count / total_count

5. **MAX works with negative values** — Changed MAX accumulator initialization from `0.0` to `float("-inf")`. Membrane potentials (-70mV to -50mV) now correctly resolve their maximum.

6. **Dimension validation** — `dim_x` and `dim_y` must differ and be in 0..4. Raises `ValueError` otherwise.

7. **TelemetryFrame** — Introduced `capture_frame()` that atomically captures all neuron/synapse state from a single tick into an immutable `TelemetryFrame`. The `LiveProjectionService.project()` reads from the frame, not directly from the live network, preventing incoherent reads across a concurrently stepping simulation.

### Tests
- **`tests/test_live_projection.py`**: Expanded from 12 to 24 tests. New tests cover:
  - Known 5D coordinate lands in expected bin (H)
  - Empty bin is null, not 0 (I)
  - Mask matches null values (I)
  - MAX with negative membrane potentials (J)
  - Spiking vs silent neuron activity difference (K)
  - TelemetryFrame tick/neuron/synapse coherence (L)
  - Invalid dimension axes and values (M)


