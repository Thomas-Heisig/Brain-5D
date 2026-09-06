# Brain-5D Development Roadmap

**Canonical roadmap for current `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-06

## 2026-09-06 Wissenschaft Network route restored

- The `Wissenschaft → Neuronales Netzwerk` context route now reveals the active Network workbench instead of being hidden by the retired-workspace CSS rule.
- Network view tabs are available again and continue to respect JavaScript-controlled `hidden` panels.

## 2026-09-06 Fixed application header and primary areas

- Header and the three primary areas `Dashboard`, `Wissenschaft` and `Runtime & Wesen` remain fixed together at the top of the viewport.
- The frontend architecture measures their actual wrapped heights and reserves the matching workspace offset for tablet and mobile layouts.
- Only the active workspace content scrolls; the fixed Footer remains independently reserved at the bottom.

## 2026-09-06 Fixed bottom Footer

- Footer is fixed to the bottom edge of the viewport across desktop, tablet and mobile layouts.
- Body and main reserve the responsive Footer height so the last workspace content remains reachable instead of being covered.
- Safe-area padding is applied for mobile browser insets.

## 2026-09-06 Footer status-bar consolidation

- Footer Runtime controls, tick, command feedback, I/O, experiment, mode and health now share one responsive semantic grid.
- Settings and Release actions are nested in the existing Health area instead of being injected as an extra grid row.
- Footer controls retain accessible click targets at desktop, tablet and mobile widths.

## 2026-09-06 Dashboard CSS consolidation pass II

- Removed the unscoped legacy white Topbar rule that overrode the coordinated shell theme.
- Reduced the Overview chrome to one workspace header, one status rail and the actual data surfaces.
- Replaced remaining fixed research/runtime workbench heights with viewport-aware guardrails and preserved local scrolling only where content requires it.
- Fixed the Embodiment renderer initialization order so unavailable connection lists no longer raise a runtime error.

## 2026-09-06 Canonical dashboard CSS and accessible views

- `src/dashboard/static/styles.css` is now the single CSS entry point and imports the component layers once; runtime stylesheet injection no longer duplicates the cascade.
- Shared tokens, fixed typography roles, surface types and green/orange/red status semantics now cover 4K, 1080p, tablet and mobile layouts.
- Tabs and `hidden` state are authoritative for dense workspaces; tables/logs retain local scrolling and dialogs use the available viewport as a full-size overlay.
- Contrast, reduced motion, larger controls and a persisted Reader view are available from the header; the Wesen morphology timeline is initialized before telemetry arrives.

## 2026-09-06 Footer 6/3 grid alignment

- Footer top row uses six equal columns for product, Runtime, I/O, experiment, mode and health.
- Footer bottom row uses three equal telemetry columns for activity, spikes and resource pressure.
- Symbols and Footer text share fixed compact sizing for consistent alignment.

## 2026-09-06 Compact Footer controls

- Footer symbols use compact 20px controls and reduced spacing.
- Footer labels, vital values and I/O text use a denser 1080p/100% scale while remaining readable.

## 2026-09-06 Fixed 1080p application shell

- Header and the primary menu band are fixed shell regions at the top of the viewport.
- `main` is the only vertically scrollable display area between the chrome regions.
- Footer remains visible at the bottom and does not shrink away at 1080p/100%.

## 2026-09-06 Responsive viewport and footer flow

- Removed the fixed active-tab viewport canvas that only fit a narrow 1080p/67% combination.
- Active workspaces now grow naturally and keep the complete Footer reachable at other resolutions and zoom levels.
- The Experience shell prevents horizontal overflow while preserving the full content area between Header and Footer.

## 2026-09-06 Frontend shell consolidation

- The visible frontend shell now has one navigation owner; legacy tab buttons remain internal routing targets only.
- Footer Runtime controls are static DOM elements with one controller and no dynamically appended duplicate panel.
- Legacy footer CSS and the MAX batch-yield note were removed; current shell styling lives in the Experience stylesheet.

## 2026-09-06 Header and footer shell stabilization

- Header sizing and responsive wrapping are centralized in the final Experience shell rules.
- Footer markup includes global Runtime controls and live I/O while remaining compatible with the flat legacy DOM.
- Footer and header no longer rely on fixed viewport positioning that can clip the document.

This roadmap separates **implemented engineering capability** from **scientific evidence still required**. A feature can be technically complete without its scientific hypothesis being confirmed.

## Current baseline

At the 2026-09-06 research-catalog integration point:

- **791 tests** are collected on current `main`;
- Research Catalog / variable-projection-dimension PR #21 is merged; merge commit `85e7209509b348bf7912dde01d3d9ebb078a2e61`;
- the latest fully completed pre-merge `main` CI baseline was #598 and successful;
- post-merge/current-head CI is the authoritative verification and must complete before the current head is described as fully green;
- Python 3.11/3.12/3.13, Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, security, Scientific Integrity, wheel and Docker remain mandatory gates;
- historical experiment DATA remains immutable evidence history.

Instrumentation repairs, registry repairs and new architecture produce new observations/experiments rather than rewriting prior DATA/EVID.

## Completed engineering foundation

Current development contains:

- sparse persisted 5D spiking core with delayed event propagation and deterministic RNG/state;
- STDP, signed eligibility and reward-modulated learning;
- homeostatic regulation;
- structural proposal/approval/mutation/journal/undo/recovery;
- `.b5d` storage, delta journaling and checkpoints;
- research registries, manifests, DATA/EVID separation and scientific integrity gates;
- bounded Language Organ / Research Assistant / Cognitive Advisor contracts;
- typed embodiment, actuator authorization, audit chain and deterministic environment loop;
- source-freeze binding across protocol code, configuration and DATA digests;
- productive-learning controls and train/validation/holdout partition enforcement;
- real host interoception and dynamic device discovery without fabricated fallback values;
- adaptive read-only `Wesen` workspace;
- protocol-driven Research Experiment Runner and Science Suite;
- network impulse response instrumentation for ticks, spikes, activated neurons, synaptic events, latency, recurrence and state digests;
- compressed immutable raw-run preservation plus bounded `runs.json` / `analysis/ai_packet.json` projections;
- Neural Symbiosis open-set peripheral network/virtual-area contracts at the embodiment boundary;
- MSBA modality-specific pathways, energy/resource accounting and fail-closed candidate allocation/plasticity;
- fragmentable canonical RQ/H registry with duplicate-ID rejection;
- canonical MSBA RQ/H integration into the normal Experiment Workflow;
- searchable Research Catalog UI that distinguishes operational from exploratory questions;
- repository-wide read-only RQ/H reference audit support;
- configurable MSBA/external projection dimensionality from 1 through 32 while preserving the productive 5D persistence contract.

## Roadmap principle

Development now prioritizes **evidence closure**, research-catalog completeness and controlled experiments over feature accumulation. Reachability in the UI is not evidence and an exploratory runtime run is not a substitute for a hypothesis-specific protocol.

---

## R0 — Research catalog closure and experiment operationalization

**Goal:** every canonical research question and hypothesis is discoverable, link-valid and explicitly classified by experiment readiness.

Implemented foundation:

1. load `questions.yaml` / `hypotheses.yaml` plus deterministic `questions.*.yaml` / `hypotheses.*.yaml` fragments;
2. fail closed on duplicate identifiers;
3. expose MSBA RQ/H entries through the existing Experiment Workflow;
4. provide searchable RQ/H selection instead of relying on a long pulldown;
5. allow exploratory runtime experiments for unmapped questions while preventing accidental EVID promotion;
6. provide a repository-wide reference audit so documentation/code references can be compared with the canonical registry.

Still required:

1. assign every still-unmapped canonical RQ/H a dedicated runner or an explicit `design_pending` state;
2. freeze controls, stopping rules, primary outcomes and preregistrations before confirmatory execution;
3. expose domain/status/evidence/progress facets through the workflow catalog API;
4. publish the registry audit as a CI artifact and maintain an explicit historical-reference allow-list where appropriate;
5. regenerate only current generated catalog/matrix documents after registry changes, never experiment-owned historical reports.

**Priority:** immediate.

---

## R1 — Post-repair propagation and recurrence validation

**Goal:** establish a clean multi-seed baseline for propagation and recurrent return using the repaired instrumentation.

Tasks:

- execute the registered recurrence/propagation protocol over independent seeds;
- persist complete spike, synapse, latency and digest metrics;
- compare recurrence-on/off using preregistered metrics;
- review before any EVID promotion;
- never rewrite `EXP-GEN-0009` to `EXP-GEN-0012`.

---

## R2 — Productive-learning evidence closure

**Goal:** demonstrate whether learning changes later behavior rather than merely internal weights.

Maintain frozen protocol/configuration, train/validation/holdout separation, pre/post behavior probes, learning-off and sham/replay controls, independent seeds and human-review-gated EVID promotion.

---

## R3 — Closed-loop embodiment evidence

**Goal:** test Sensor → SNN → Actuator → Outcome → Reward as a controlled causal loop.

Required comparisons include replay/open-loop, sensor-loss, degraded-quality and actuator-no-effect conditions. Action acceptance and measured effect must remain separate receipts.

---

## R4 — Neural Symbiosis / MSBA experimental gateway program

**Goal:** test whether the SNN can learn to select, weight or compensate across peripheral neural/virtual areas without compromising the canonical core.

The first implementation stage is **experiment-only**. Production peripheral activation remains out of scope until controls are validated.

Required work:

1. add an experiment-runner adapter that constructs explicitly declared peripheral areas;
2. persist exact adapter/model/version/artifact hashes;
3. persist gateway state independently from core synapse state;
4. keep gateway plasticity disabled outside registered experiments;
5. support matched frozen-gateway, random-gateway, timing-shuffle and information/activity controls;
6. support reduced-, native- and increased-dimensional projection treatments with explicit mappings;
7. execute `RQ-MSBA-E01` through `RQ-MSBA-E05` only after their hypothesis-specific runners and preregistrations exist;
8. evaluate noisy-area suppression and sensor-lesion compensation;
9. compare alternative homeostatic reward/error formulations rather than assuming a signed population mean is valid;
10. require independent seeds and evidence review before claims of learned tool/area use.

---

## R5 — Variable dimensionality and versioned N-D core research

**Goal:** allow dimensionality to become an explicit experimental variable without breaking existing 5D evidence or persistence.

### Implemented safe layer

- MSBA/external projection spaces accept 1–32 dimensions;
- schemas can record projection dimension count separately from productive core dimensions;
- UI exposes the projection-dimension request and states the productive 5D limitation;
- historical 5D neuron IDs and `.b5d` snapshots remain unchanged.

### Required before productive core >5D

1. design and freeze a versioned N-D neuron-ID/storage representation;
2. define backward-compatible `.b5d` readers/migration and canonical state hashing;
3. generalize spatial indexing, coordinate packing, neighbor generation, distances, topology diagnostics and structural locality;
4. add combinatorial-growth/memory guards for high dimensions;
5. prove bit-for-bit equivalence for unchanged 5D configurations;
6. create a preregistered N-D projection sweep first, then a separate productive-core N-D experiment after storage migration;
7. never reinterpret earlier 5D experiments as N-D evidence.

---

## R6 — Time-scale and runtime calibration

Benchmark target Hz, achieved Hz, realtime ratio, `dt` and per-subsystem tick cost. Prove pacing-only changes do not alter deterministic simulated outcomes when `dt` and inputs remain unchanged.

---

## R7 — Scientific test of the 5D organization

Compare full 5D organization against dimension-shuffled, reduced-dimensional, increased-dimensional projection and topology-matched non-spatial controls. Measure propagation, locality, learning efficiency, structural motifs, robustness and computational cost. Increased-dimensional *projection* results must not be mislabeled as productive-core N-D results.

---

## R8 — Self-regulation, continuity and sensor-loss studies

Test homeostasis/interoception as functional control mechanisms without anthropomorphic interpretation. Persist body-boundary/sensor availability changes when they are experimental variables.

---

## R9 — Memory and world-model layer

Only after stable behavioral baselines exist: define explicit memory-state contracts, compare memory-on/off, add prediction/recall metrics, distinguish observation history from learned internal state and external knowledge, and require predictive/behavioral utility before using the term world model.

---

## R10 — Multimodal grounding and knowledge intake

Introduce camera/audio/document/network/knowledge observations through typed provenance-rich SignalFrames and Neural Symbiosis/MSBA adapters. Scientific runs require frozen/replayable source snapshots and explicit treatment identity.

---

## R11 — AI-as-treatment research

Compare no-AI, frozen replay, sham/random proposer and model-family conditions under identical research packets. AI involvement remains provenance-bound and cannot be silently mixed into controls.

---

## R12 — Scaling and performance engineering

Scale only when evidence needs justify it. Profile network/tick cost, memory footprint, storage/journal backpressure and bounded telemetry before adding accelerator/native kernels. Any optimization requires semantic-equivalence tests.

## Release direction

Before a new major research milestone is declared:

1. `main` CI is green;
2. deterministic/recovery contracts remain intact;
3. Scientific Integrity Gate is green;
4. new causal capabilities have matched controls;
5. experiment artifacts are reproducible from recorded manifests;
6. documentation source-of-truth is current;
7. AI/peripheral-network involvement is registered as provenance/treatment where applicable;
8. dashboard/catalog visualization remains separated from scientific evidence;
9. historical DATA has not been rewritten to fit newer instrumentation;
10. any open research operationalization or N-D migration work remains explicitly listed in both TODO and this roadmap.

## Historical roadmaps

Files such as `ROADMAP_ALPHA4.md`, `ROADMAP_ALPHA5*.md`, `ROADMAP_V*.md` and sprint-specific plans are historical records and do not override this roadmap.
