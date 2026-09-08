## Naming update — 2026-09-08

MHRN / Multi-Scale Homeostatic Recurrence Network. Publication: Recursive Epistemics / Rekursive Epistemik. [Migration and compatibility](../../NAMING.md). Historical scientific artifacts remain unchanged.

# MHRN Current TODO

**Canonical TODO for `main`**  
**Baseline:** `brain5d-core 0.5.0a7`  
**Updated:** 2026-09-08  
**Current release-blocking backlog:** **0**

This file contains **active release-blocking work only**. Long-horizon engineering and scientific work is tracked in [ROADMAP.md](ROADMAP.md) and in the versioned research programme. Moving an item out of this file does **not** claim that the future research has already been performed.

## 2026-09-08 Review and gate closure

- [x] Record the completed AIRR interpretation reviews as append-only `*.review.json` artifacts with reviewer, timestamp, comments and report-content digest.
- [x] Close the stale `AIRR-2026-0003` review-pending TODO: its human interpretation review is recorded on 2026-09-08 as `accepted_as_interpretation`.
- [x] Preserve the epistemic boundary: `accepted_as_interpretation` does not by itself promote DATA or an AI report to scientific EVID.
- [x] Complete the review disposition for `EXP-GEN-0033`: review is complete, while the source experiment remains exploratory and `git.dirty=true`; therefore no EVID promotion is performed.
- [x] Complete the retry-experiment review disposition: `EXP-REPL-0001-R1` remains non-promotable because its recorded run is `git.dirty=true`; `EXP-LIFE-0001-R1` remains an exploratory precursor and is not promoted to EVID.
- [x] Complete the `RQ-SNN-001` review decision conservatively: `EXP-SNN-001-R5` is a valid clean run (`dirty=false`), but no EvidenceEngine `human_review.json` containing a `supports` / `refutes` / `inconclusive` decision is present. No EVID promotion is inferred from an AIRR interpretation review.
- [x] Resolve RQ/H evidence-link synchronization for this closure: no new validated EVID was promoted, so canonical RQ/H evidence links intentionally remain unchanged.
- [x] Resolve dissertation EVID synchronization for this closure: no new promotable EVID record was created, therefore no EVID-derived DOCX mutation is required.
- [x] Keep a future clean replication of dirty/exploratory experiments in the scientific roadmap rather than misrepresenting the historical run metadata.

## 2026-09-08 Quality-gate state

- [x] Resolve **Cross-platform source-freeze digest mismatch on Windows** with Git-canonical text content, explicit dirty/untracked diagnostics and byte-exact binary handling.
- [x] Scientific Integrity Gate passes on the reviewed `main` state.
- [x] Lint/format checks pass: Black, Ruff, Pylint, pre-commit and whitespace/merge-conflict checks.
- [x] Type checks pass: Mypy and both Pyright scopes.
- [x] Documentation checks pass.
- [x] Security checks pass.
- [x] Catalog audit passes.
- [x] Chromium browser smoke and Playwright E2E checks pass.
- [x] Cognition Programme workflow passes.
- [x] Keep scientific validity independent from UI/checklist colour: a green engineering gate never substitutes for experimental evidence.

## 2026-09-08 Hugging Face Space disposition

- [x] Resolve the external Space smoke item as **non-blocking/deferred**, not as a claimed public smoke pass. The local Space-specific smoke contract and Chromium browser CI are green; a future public proxy check remains an operational follow-up when Hugging Face rate limiting permits it.

## Completed platform consolidation

- [x] `main` is the canonical development line and GitHub is the source of truth; Hugging Face is a derived mirror.
- [x] File Viewer is the canonical file renderer shared by Dashboard, Research and Chat surfaces.
- [x] Research Review Inbox is available for completing open interpretation reviews without automatic evidence promotion.
- [x] Runtime, Research, File Viewer, Release/Gate and responsive dashboard integrations have automated browser/API coverage.
- [x] Review records are append-only and preserve reviewer identity, decision semantics, comments and provenance digests.
- [x] Historical experiment artifacts remain immutable; dirty, exploratory or AI-generated records are not rewritten to appear scientifically validated.

## Next development milestone — v0.6 Scaling & Deterministic Performance

The reviewed v0.5.0a7 release gate is closed. The following checklist opens the **next version milestone**; these items are development targets, not retroactive blockers for the closed v0.5 gate.

- [ ] Freeze the v0.6 compatibility contract for runtime state, snapshots and resumable runs.
- [ ] Add reproducible scaling benchmarks across increasing neuron/synapse counts with explicit memory and tick-cost budgets.
- [ ] Introduce bounded telemetry/storage compaction so long experiment histories never require an AI consumer to ingest unbounded `runs.json` files.
- [ ] Persist one compact current-run packet plus immutable raw-run indexes with SHA-verified provenance.
- [ ] Verify deterministic pause/resume/restart identity for the v0.6 runtime contract across supported Python versions.
- [ ] Add performance regression thresholds for RuntimeController, structural phases, learning, storage and dashboard telemetry.
- [ ] Make target-Hz pacing and unlimited mode observable with achieved-Hz/realtime-ratio acceptance criteria.
- [ ] Add clean migration/rollback tests for all v0.6 persisted-state schema changes.
- [ ] Require full Python 3.11/3.12/3.13, browser, type, lint, security, build and Docker gates before v0.6 release.
- [ ] Generate the v0.6 release record only after the exact source-freeze CI and release-readiness snapshot are both green.

## Future work is roadmap work, not an open release blocker

The following programmes remain intentionally **future research/engineering**, and are therefore maintained in [ROADMAP.md](ROADMAP.md) rather than as release-blocking TODO checkboxes:

- v0.6 scaling, bounded storage/telemetry, deterministic performance and resume;
- v0.7 knowledge/learning experiments, interference, retention, transfer and retrieval;
- v0.8 Embodiment / Neural Symbiosis / MSBA validation and governed peripheral adapters;
- v0.9 bounded memory, world model and operational self-model experiments;
- v1.0 stable reproducible research-platform APIs and artifact schemas;
- v1.1 independent replication, cross-hardware reproducibility and control families;
- v1.2 governed adaptive allocation, structural growth, peripheral plasticity, rollback and failure recovery;
- productive N-D core/storage migration beyond the current persisted 5D core;
- additional preregistered projection sweeps, large-scale dimensionality ablations and energy calibration;
- confirmatory follow-ups for exploratory or dirty historical runs;
- additional independent reviews before any future EVID promotion;
- branch-reference deletion when repository tooling exposes a supported delete-ref action.

These items are **not marked completed here**. Their implementation, controls, preregistration, replication and evidence requirements remain governed by the roadmap and research registry.

## Definition of done for future scientific milestones

A scientific milestone is complete only when all applicable requirements are satisfied:

- protocol is frozen/preregistered;
- implementation and controls are tested;
- runs are reproducible from manifests;
- data partitions and AI/peripheral-network treatments are explicit;
- runtime errors and provenance checks pass;
- source cleanliness requirements pass for promotion-eligible runs;
- mandatory human scientific review is recorded in the required schema;
- evidence artifacts are accepted by the evidence gate before RQ/H promotion;
- documentation distinguishes positive, negative and inconclusive outcomes;
- dashboard visualization, review completion or pipeline reachability is never substituted for empirical evidence.

## Current status

**Engineering/release TODO: CLEAN.**  
**Scientific Integrity Gate: GREEN on the reviewed main lineage.**  
**Scientific roadmap: active and intentionally not represented as completed work.**
