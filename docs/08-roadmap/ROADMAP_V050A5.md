# Brain-5D Roadmap — v0.5.0-alpha.5 Scientific Verification Closure

**Status: CLOSED** (2026-08-31 — all Alpha.5 gates passed)

### Completed in Pre-Closure Sprint (Part 1)

1. **Gate evidence binding** — Determinism criteria now read from `research/generated/verification/determinism_infrastructure.json` instead of checking file existence. Fail-closed: missing artifact, stale digest, or failed proofs all result in PENDING/STALE, never PASSED.

2. **LearningEngine deterministic keying** — Replaced `id(synapse)` (Python memory address, non-deterministic across restarts) with stable `(pre_id, target_id)` tuples. All internal dicts (`_states`, `events`) use stable keys. All iterations use `sorted()` instead of hash-based set iteration.

3. **Production restore bundle** — New `restore_full()` function in `core_restore.py` restores network + HomeostasisEngine + LearningEngine atomically. Returns a `RestoredBundle` dataclass.

4. **Production restore test** — `tests/test_production_restore.py` verifies the full "C path": Process A creates network + engines → runs → captures checkpoint → Process B restores from snapshot → creates fresh engines → restores state → verifies full state digest identity.

5. **Determinism infrastructure artifact** — `scripts/generate_determinism_artifact.py` runs all determinism tests and produces the verification artifact with 7 proofs.

### Completed in Live Visualization Sprint (Part 2)

6. **Verification artifact generation fix** — `scripts/generate_determinism_artifact.py` now uses canonical `compute_source_tree_digest()` instead of a custom hash function. All 5 verification artifacts share the same `tested_tree_digest`.

7. **Verification semantics cleanup** — Artifacts use `test_run_head` (provenance) instead of `tested_commit` (misleading). Tree digest is the sole freshness authority.

8. **Live projection service** — `LiveProjectionService` queries the in-memory `NeuralNetwork` directly. Supports 5 kinds (activity, energy, membrane, spike, weight) with configurable aggregation and resolution. Never reads from `.b5d` snapshots.

9. **LIVE vs SNAPSHOT separation** — Dashboard now has a clear source badge (LIVE in green, SNAPSHOT in amber). `/api/live/projection` is the live endpoint; `/api/heatmap` remains snapshot-based. The user always knows what is being displayed.

10. **Live projection tests** — 12 tests covering energy accuracy, activity timing, weight projection, tick coherence, no-mutation guarantee, snapshot separation, bounded payload, and invalid parameter handling.

### Completed in Dashboard Enhancement Sprint (Part 3)

11. **IO-Fluss Visualisierung** — New `/api/live/io-flow` endpoint analyzes signal propagation from input cells through hidden layers to output cells. Frontend shows three-layer flow bars with activity rates, neuron counts, and a propagation badge (✅ Signalfluss aktiv / ⏳ Signal abgebrochen). Threshold: 0.001 spikes/tick per layer.

12. **Populationen-Übersicht** — New `/api/live/population` endpoint groups neurons by type (excitatory, inhibitory, sensory_input, motor_output) with per-population statistics (mean rate, energy, membrane potential, active fraction). E/I ratio badge with color coding. Auto-refresh every 2s.

13. **Verbesserte 5D Isometrische Projektion** — Enhanced `draw5DProjection()` with isometric floor grid, axis labels (X, Y), Z-range legend, 5D dimension info, and glow effects for high-activity regions. Better visual depth perception.

14. **CSS-Styling für neue Panels** — Dedicated styles for IO-Fluss flow bars (color-coded per layer: input=teal, hidden=blue, output=amber), population cards with active-fraction progress bars, responsive layout.

### Remaining for Alpha.5 Closure

- [x] Restore Determinism A/B/C experiment (uninterrupted vs in-process vs process restart)
- [x] EXP-DET-0001 executed
- [x] EXP-STOR-0001 executed
- [x] First DATA-* / EVID-* artifacts
- [x] Research Catalog rebuilt from real evidence

## v0.5.0-alpha.6 — Morphological Self-Regulation
> Alpha.5 closed on 2026-08-31; Alpha.6 work is unblocked.

Chronic signals, growth budgets, regional pressures, telemetry, scientific evaluation.

## v0.6 — Scaling
Event-driven dirty tracking, chunked storage, domain decomposition, 5k-1M benchmark ladder.

## v0.7 — Learning Environment
Episode lifecycle, train/evaluation split, delayed reward tasks, learning curves.

## v0.8 — Embodiment
Text/image/audio sensor adapters, actuator adapters, perception-action-reward loop.

## v0.9 — Memory and World Model
Working context, long-term associative memory, goals, multi-step state.

## v0.10 — Cognitive Evaluation
Causal tasks, compositional generalization, neuro-symbolic experiments.

## v0.11 — Controlled Action and HMI
Permissions, resource limits, audit log, safe stop, sandbox.

## v0.12 — Release Candidate
Restore/continue soak tests, benchmark freeze, seven-day stability runs.

## v1.0 — Usable Brain-5D AI
Persistent, stable, reproducible, evaluable, multimodal learning system.
