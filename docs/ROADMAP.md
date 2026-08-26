# Brain-5D Roadmap

## v0.5.0-alpha.5 — Scientific Verification Closure

**Status: OPEN** (pre-closure sprint complete)

### Completed in Pre-Closure Sprint

1. **Gate evidence binding** — Determinism criteria now read from `research/generated/verification/determinism_infrastructure.json` instead of checking file existence. Fail-closed: missing artifact, stale digest, or failed proofs all result in PENDING/STALE, never PASSED.

2. **LearningEngine deterministic keying** — Replaced `id(synapse)` (Python memory address, non-deterministic across restarts) with stable `(pre_id, target_id)` tuples. All internal dicts (`_states`, `events`) use stable keys. All iterations use `sorted()` instead of hash-based set iteration.

3. **Production restore bundle** — New `restore_full()` function in `core_restore.py` restores network + HomeostasisEngine + LearningEngine atomically. Returns a `RestoredBundle` dataclass.

4. **Production restore test** — `tests/test_production_restore.py` verifies the full "C path": Process A creates network + engines → runs → captures checkpoint → Process B restores from snapshot → creates fresh engines → restores state → verifies full state digest identity.

5. **Determinism infrastructure artifact** — `scripts/generate_determinism_artifact.py` runs all determinism tests and produces the verification artifact with 7 proofs.

### Remaining for Alpha.5 Closure

- Restore Determinism A/B/C experiment (uninterrupted vs in-process vs process restart)
- EXP-DET-0001 executed
- EXP-STOR-0001 executed
- First DATA-* / EVID-* artifacts
- Research Catalog rebuilt from real evidence

## v0.5.0-alpha.6 — Morphological Self-Regulation
> BLOCKED until Alpha.5 closes.

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
