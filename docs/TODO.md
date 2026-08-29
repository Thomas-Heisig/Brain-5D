# Brain-5D — Consolidated TODO

> Last updated: 2026-08-29
>
> Infrastructure: Hugging Face Repository vorbereitet (HF_README.md,
> .gitattributes LFS, .huggingface/ metadata, Space-Konfiguration,
> GitHub→HF Sync Workflow).
> Verification basis:
>   Current verification → tests/test_baseline.json (tree-digest authority)
>   All 5 verification artifacts share the same tested_tree_digest ✅
> Status: Alpha.5 — LIVE TELEMETRY FROZEN. Gate B open only for Restore A/B/C.
> Alpha.6: BLOCKED
>
> Phase 1-9 implemented (error integrity, canonical state, RNG persistence,
> iteration determinism, structural determinism, checkpoint v4,
> production restore bundle, deterministic LearningEngine).
> Phase 10-25: PENDING (restore determinism experiments, DATA/EVID artifacts).
>
> Dashboard truth sources:
>   /api/integration/status = live runtime truth
>   /api/gate/status        = release/verification truth
>   /api/live/projection    = live runtime visualization (LIVE_RUNTIME)  /api/live/io-flow       = input-output signal propagation analysis
  /api/live/population    = neuron population overview (E/I ratio, rates)>   /api/heatmap            = snapshot visualization (SNAPSHOT)
>   /api/errors             = canonical runtime-error endpoint (available/count/events)
>   /api/structural/errors  = structural runtime errors
>   B5D-SEF                 = scientific evidence truth

---

# ALPHA.5 GATE STATUS

```
Gate A — Technical Integration
Process / Runtime / Control / Dashboard       VERIFIED (CLOSED)
Snapshot / Heatmap / 5D Inspector            VERIFIED
Structural canonical composition             VERIFIED
Structural production signal->policy         VERIFIED (live loop artifact)
Real single-port ownership proof             VERIFIED (hardened test + artifact)
Structural Live Loop (full E2E path)         VERIFIED

Gate B — Verification
Recorded full test run                       379 passed / 0 failed
Structural mechanism E2E                     11/11 VERIFIED
Error Visibility (no silent exceptions)      VERIFIED
Runtime exceptions enter manifest            VERIFIED (Phase 1)
Invalid run cannot become evidence           VERIFIED (Phase 1)
Explicit iteration-order determinism         VERIFIED (Phase 6)
Full RNG state persistence                   VERIFIED (Phase 5)
Canonical full-state digest                  VERIFIED (Phase 3-4)
Structural determinism                       VERIFIED (Phase 7)
Homeostasis + learning state persistence     VERIFIED (Phase 8)
Restore-and-continue identity                OPEN (engine attach fix applied, 
                                                 B==C confirmed via subprocess,
                                                 but A still diverges from B/C —
                                                 synapse list order after file 
                                                 restore causes STDP weight 
                                                 misalignment)
Production restore bundle                    VERIFIED (Phase 9)
LearningEngine deterministic keying          VERIFIED (Phase 9)
Gate evidence binding                        VERIFIED (Phase 9)
Live visualization backend                   VERIFIED (Phase 9)

Gate C — Scientific Baseline
B5D-SEF                                      IMPLEMENTED
EXP-DET-0001                                 REGISTERED / NOT STARTED
EXP-STOR-0001                                REGISTERED / NOT STARTED
Scientific DATA-*                            NONE
Scientific EVID-*                            NONE

ALPHA.5                                      OPEN
ALPHA.6                                      BLOCKED
```

---

# Current Recorded Test Baseline

```
Current verification: tests/test_baseline.json
Python:               3.13.14

Full suite:
  Passed:             414
  Failed:             0
  Skipped:            2
  Collection errors:  0

Verification artifacts (all share the same tested_tree_digest):
  tests/test_baseline.json                    ✅
  research/generated/verification/structural_e2e.json ✅
  research/generated/verification/structural_live_loop.json ✅
  research/generated/verification/single_listener.json ✅
  research/generated/verification/determinism_infrastructure.json ✅

Determinism infrastructure artifact (7/7 proofs):
  rng_state_persistence       ✓
  explicit_iteration_order    ✓
  canonical_state_digest      ✓
  structural_determinism      ✓
  checkpoint_v4_roundtrip     ✓
  engine_state_roundtrip      ✓
  experiment_validity         ✓

Freshness authority: tested_tree_digest (SHA-256)

Digest scope:
  src/
  configs/
  research/schemas/
  pyproject.toml
  tests/

Excluded:
  tests/test_baseline.json (cannot invalidate itself)
  docs/ (documentation changes do not affect verification)
  research/generated/ (generated reports are derived, not source)
```

---

# Immediate Execution Order

```
=== GATE A ====================================================

 1. Process Architecture / Single PID ........................ ✅
 2. Canonical RuntimeController ............................... ✅
 3. Frontend Lifecycle / Control API ......................... ✅
 4. Snapshot / Heatmap / 5D Inspector ........................ ✅
 5. Canonical structural production composition .............. ✅
 6. Approval -> mutation -> journal -> undo .................. ✅
 7. Dashboard Completion ..................................... ✅
 8. Production signal -> policy -> coordinator adapter ....... ✅
 9. Real single-listener port ownership test ................ ✅
10. Config-authoritative policy (from_config) ............... ✅
11. RuntimeAdapter error visibility ......................... ✅
12. Structural Live Loop E2E (full production path) ......... ✅

=== GATE B ====================================================

13. Full pytest collection 414/0/2 .......................... ✅
14. Structural mechanism E2E 11/11 .......................... ✅
15. Error Visibility / scientific integrity ................. ✅
16. Runtime exceptions enter manifest ....................... ✅
17. Invalid run cannot become evidence ...................... ✅
18. Iteration-order determinism ............................. ✅
19. RNG state persistence ................................... ✅
20. Canonical state digest .................................. ✅
21. Structural determinism .................................. ✅
22. Homeostasis + learning state persistence ............... ✅
23. Restore-and-continue determinism ........................ 🔴 (engine attach fixed,
                                                                   B==C via subprocess,
                                                                   A != B/C)
24. Production restore bundle (restore_full) ............... ✅
25. LearningEngine deterministic keying .................... ✅
26. Gate evidence binding (determinism artifact) ........... ✅
27. Live visualization backend (LiveProjectionService) ..... ✅
28. LIVE vs SNAPSHOT separation ............................ ✅

=== GATE C ====================================================

24. Research registry / B5D-SEF framework .................. ✅
25. EXP-DET-0001 (deterministic replay) .................... 🔴
26. EXP-STOR-0001 (snapshot/restore identity) .............. 🔴
27. Generate evidence from actual runs ..................... 🔴
28. Close ALPHA.5 .......................................... 🎯
29. Begin alpha.6
```

---

# Structural Safety

* [x] Proposal creation alone does NOT mutate the network (proof 5)
* [x] Reject does NOT mutate the network (proof 6)
* [x] Manual approval required for canonical StructuralProposal mutation (canonical E2E)
* [x] Dry-run mode implemented (SelfOrganizationCoordinator(dry_run=True))
* [x] Auto-approval explicitly opt-in verified in production config
* [x] No silent except:pass in RuntimeAdapter (structured RuntimeErrorEvent)
* [x] Config-authoritative mechanism gating (disabled mechanism never emits proposals)
* [x] Canonical approved mutation produces StructuralChangeRecord (proof 8)
* [x] Canonical mutation linked to proposal_id (proof 8)
* [x] E2E proposals attributable to canonical HomeostasisSignal (proof 4)
* [x] Production proposals attributable to runtime measurements (no longer blocked; adapter exists)

---

# Structural E2E Proofs (11/11 VERIFIED)

* [x] Proof 1: Coordinator instantiated via production factory
* [x] Proof 2: PlasticityEngine instantiated
* [x] Proof 3: Bridge instance identity
* [x] Proof 4: Real HomeostasisSignal -> policy -> proposal
* [x] Proof 5: Proposal alone does not mutate
* [x] Proof 6: Reject does not mutate
* [x] Proof 7: Approve causes exactly one mutation
* [x] Proof 8: Exactly one StructuralChangeRecord
* [x] Proof 9: Undo restores topology digest
* [x] Proof 10: Journal reopen/replay restores topology
* [x] Proof 11: Complete canonical structural E2E

Artifact: research/generated/verification/structural_e2e.json
Validation: REQUIRED_STRUCTURAL_PROOFS (11 IDs, all true, exact match)
Freshness: tested_tree_digest matches current source tree

---

# Research Registry

> Canonical source: research/registry/*.yaml
> Generated reports: research/generated/RESEARCH_CATALOG.md

* [x] Research Questions: 28 registered
* [x] Hypotheses: 27 registered
* [x] Claims: 5 registered
* [x] Literature Sources: 8 registered
* [x] Experiment Methods: 13 defined

Registered experiments:
* EXP-2026-0001   template (example)
* EXP-DET-0001    not_started (deterministic replay)
* EXP-STOR-0001   not_started (snapshot/restore identity)

---

# B5D-SEF Infrastructure

* [x] Research registry YAML files (questions, hypotheses, claims, sources, methods)
* [x] JSON schemas for validation
* [x] Experiment recorder with manifest generation
* [x] Evidence engine (with validity rejection)
* [x] Report builder (RESEARCH_CATALOG, EVIDENCE_MATRIX, etc.)
* [x] Registry uniqueness validation (8 tests)
* [x] DATA-* object type in schema
* [x] evidence_level (E0-E4) in claim schema
* [x] experiment_status in manifest schema (template, not_started, running, completed, failed, invalid)
* [x] ID correction: RQ-SNN-003 -> RQ-DET-001 for determinism question
* [x] Configuration SHA-256 hash (path and sha256 in .b5d metadata, experiment manifests)
* [x] Runtime exceptions automatically propagated into manifest (record_runtime_error)
* [x] Experiment validity semantics (validity.valid, validity.reason, validity.runtime_error_count)
* [x] Fail-fast mode (ExperimentRecorder(fail_fast=True))
* [ ] Eligibility / Reward configuration in manifest
* [ ] Test/environment provenance in manifest

---

# Open Items

## Gate A
* [x] Production signal -> policy -> coordinator adapter (SelfOrganizationRuntimeAdapter)
* [x] Real single-listener port ownership test (TCP listener assertion)

## Gate B
* [x] Structured Runtime Error Events (RuntimeErrorEvent, error buffer, /api/errors)
* [x] Research fail-fast mode (implemented in ExperimentRecorder, fail_fast parameter)
* [x] Runtime exceptions automatically propagated into manifest (record_runtime_error)
* [x] Invalid run evidence rejection (EvidenceEngine rejects template/not_started/running/failed/invalid)
* [x] Config SHA-256 in .b5d metadata, experiment manifests, verification artifacts
* [x] Full RNG state persistence (checkpoint v3+ via getstate/setstate)
* [x] Delayed event + learning/homeostasis state persistence (checkpoint v4)
* [x] Canonical state digest (canonical_state_digest -> SHA-256)
* [x] Iteration-order determinism (verified by tests)
* [x] Structural determinism (verified by tests)
* [x] Gate evidence binding — determinism criteria use verification artifact, not file existence
* [x] LearningEngine deterministic keying — stable (pre_id, target_id) instead of id(synapse)
* [x] LearningEngine deterministic iteration — sorted() instead of set iteration
* [x] Production restore bundle (restore_full) — network + homeostasis + learning in one call
* [x] Live projection service (LiveProjectionService) — read-only live runtime visualization
* [x] LIVE vs SNAPSHOT separation — source badge in UI, /api/live/projection vs /api/heatmap
* [x] Verification artifact generation uses canonical compute_source_tree_digest() everywhere
* [x] Verification artifacts use test_run_head (provenance) instead of tested_commit (misleading)
* [ ] Restore Determinism A/B/C (uninterrupted vs in-process vs process restart)
  * [x] Engine attach fix — restored engines were passive
  * [x] Path B uses restore_full() + asserts different object
  * [x] Path C uses real subprocess (pid_C1 != pid_C2)
  * [x] Absolute tick schedule (serialized, shared by A/B/C2)
  * [x] All proofs machine-measured, never hardcoded
  * [ ] A == B == C still fails — synapse list order after file restore

## Gate C
* [ ] EXP-DET-0001 executed
* [ ] EXP-STOR-0001 executed
* [ ] First DATA-* artifact produced
* [ ] First EVID-* record produced
* [ ] First reproducibly supported/refuted hypothesis
* [ ] Research Catalog rebuilt from real evidence
* [ ] Evidence Matrix rebuilt from real evidence

## Documentation
* [x] Version consistency (main.py now prints alpha.5)
* [x] /api/errors documented as canonical runtime-error endpoint
* [x] TODO updated to reflect current state
* [ ] Rebuild research reports after experiments

---

# Future Versions

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
