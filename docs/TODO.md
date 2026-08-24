# Brain-5D — Consolidated TODO

> Last updated: 2026-08-24
> Verification basis:
>   Test-run commit: a57026d
>   Source-tree digest: 5f90946b...
> Status: Alpha.5 integration and verification closure
> Alpha.6: BLOCKED
>
> Technical structural mechanisms are implemented and E2E-tested.
> Automatic production signal->policy->coordinator wiring,
> error visibility, restore determinism and scientific baseline
> experiments remain open.
>
> Dashboard truth sources:
>   /api/integration/status = live runtime truth
>   /api/gate/status        = release/verification truth
>   B5D-SEF                 = scientific evidence truth

---

# ALPHA.5 GATE STATUS

```
Gate A — Technical Integration
Process / Runtime / Control / Dashboard       VERIFIED
Snapshot / Heatmap / 5D Inspector            VERIFIED
Structural canonical composition             VERIFIED
Structural production signal->policy         OPEN
Real single-port ownership proof             OPEN

Gate B — Verification
Recorded full test run                       274 passed / 2 skipped
Structural mechanism E2E                     11/11 VERIFIED
Error Visibility                             OPEN
Restore Determinism                          OPEN

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
Test-run commit: a57026d
Python:          3.13.14

Full suite:
  Passed:             274
  Failed:             0
  Skipped:            2
  Collection errors:  0

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
 8. Production signal -> policy -> coordinator adapter ....... 🔴
 9. Real single-listener port ownership test ................ 🔴

=== GATE B ====================================================

10. Full pytest collection 274/0/2 .......................... ✅
11. Structural mechanism E2E 11/11 .......................... ✅
12. Error Visibility / scientific integrity ................. 🔴
13. Restore-and-continue determinism ........................ 🔴

=== GATE C ====================================================

14. Research registry / B5D-SEF framework .................. ✅
15. EXP-DET-0001 (deterministic replay) .................... 🔴
16. EXP-STOR-0001 (snapshot/restore identity) .............. 🔴
17. Generate evidence from actual runs ..................... 🔴
18. Close ALPHA.5 .......................................... 🎯
19. Begin alpha.6
```

---

# Structural Safety

* [x] Proposal creation alone does NOT mutate the network (proof 5)
* [x] Reject does NOT mutate the network (proof 6)
* [x] Manual approval required for canonical StructuralProposal mutation (canonical E2E)
* [x] Dry-run mode implemented (SelfOrganizationCoordinator(dry_run=True))
* [ ] Auto-approval explicitly opt-in verified in production config
* [x] Canonical approved mutation produces StructuralChangeRecord (proof 8)
* [x] Canonical mutation linked to proposal_id (proof 8)
* [x] E2E proposals attributable to canonical HomeostasisSignal (proof 4)
* [ ] Production proposals attributable to runtime measurements (blocked by missing adapter)

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
* [x] Evidence engine
* [x] Report builder (RESEARCH_CATALOG, EVIDENCE_MATRIX, etc.)
* [x] Registry uniqueness validation (8 tests)
* [x] DATA-* object type in schema
* [x] evidence_level (E0-E4) in claim schema
* [x] experiment_status in manifest schema
* [x] ID correction: RQ-SNN-003 -> RQ-DET-001 for determinism question
* [ ] Configuration SHA-256 hash (path only, not hash)
* [ ] Runtime exceptions automatically propagated into manifest
* [ ] Eligibility / Reward configuration in manifest
* [ ] Test/environment provenance in manifest

---

# Open Items

## Gate A
* [ ] Production signal -> policy -> coordinator adapter (SelfOrganizationRuntimeAdapter)
* [ ] Real single-listener port ownership test (TCP listener assertion)

## Gate B
* [ ] Structured Runtime Error Events (RuntimeErrorEvent, error buffer, /api/errors)
* [ ] Research fail-fast mode (invalid experiment runs rejected)
* [ ] Config SHA-256 in .b5d metadata, experiment manifests, verification artifacts
* [ ] Full RNG state persistence
* [ ] Delayed event + learning/homeostasis state persistence
* [ ] Restore Determinism A/B/C (uninterrupted vs in-process vs process restart)

## Gate C
* [ ] EXP-DET-0001 executed
* [ ] EXP-STOR-0001 executed
* [ ] First DATA-* artifact produced
* [ ] First EVID-* record produced
* [ ] First reproducibly supported/refuted hypothesis
* [ ] Research Catalog rebuilt from real evidence
* [ ] Evidence Matrix rebuilt from real evidence

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
