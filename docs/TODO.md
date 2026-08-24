# Brain-5D — Consolidated TODO

> Last updated: 2026-08-24
> Repository HEAD: 6b70554
> Status: Alpha.5 integration and verification closure
> Alpha.6: BLOCKED
>
> Technical structural mechanisms are implemented and E2E-tested.
> Automatic production signal->policy->coordinator wiring,
> error visibility, restore determinism and scientific baseline
> experiments remain open.
>
> Dashboard:
> /api/integration/status = live runtime truth
> /api/gate/status        = release/verification truth
> B5D-SEF                 = scientific evidence truth

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
Structural mechanism E2E                     11/11 passed
Structural Gate artifact validation          PASSED (11/11 proof set)
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

# Status Model

Fur alle grosseren Funktionen gelten kunftig vier Reifestufen:

```
IMPLEMENTED
    |
INTEGRATED
    |
VERIFIED
    |
EVIDENCED
```

Bedeutung:

- `IMPLEMENTED` -- Code existiert.
- `INTEGRATED` -- Code ist im realen `src.main`-Pfad angeschlossen.
- `VERIFIED` -- Tests bzw. Laufzeitprufung bestatigen die Funktion.
- `EVIDENCED` -- wissenschaftliche Experimente liefern dokumentierte Evidenz.

---

# Current Recorded Test Baseline

```
Repository HEAD:  6b70554
Test-run HEAD:    6b70554
Python:           3.13.14

Full suite:
  Passed:             274
  Failed:             0
  Skipped:            2
  Collection errors:  0

Freshness authority:
  tested_tree_digest (SHA-256)

Digest scope:
  src/
  configs/
  research/schemas/
  pyproject.toml
  tests/

Excluded:
  tests/test_baseline.json
```

---

# Immediate Execution Order

```
=== GATE A ====================================================

 1. Verify current real HTTP Bridge state .................... ✅
 2. Fix frontend double initialization ....................... ✅
 3. Select canonical RuntimeController ....................... ✅
 4. Remove SimpleController .................................. ✅
 5. Make RuntimeController sole simulation-clock owner ....... ✅
 6. Remove automatic startup 1000-tick execution ............. ✅
 7. Unify /api/control contract ............................. ✅
 8. Connect snapshot pipeline to RuntimeController .......... ✅
 9. Verify .b5d -> Heatmap live chain ....................... ✅
10. Canonical structural production composition ............. ✅
11. Approval -> mutation -> journal -> undo ................. ✅
12. Dashboard Completion .................................... ✅
13. Production signal -> policy -> coordinator adapter ...... 🔴
14. Real single-listener port ownership test ............... 🔴

=== GATE B ====================================================

15. Full pytest collection 274/0/2 ......................... ✅
16. Structural mechanism E2E 11/11 ......................... ✅*
17. Error Visibility / scientific integrity ................ 🔴
18. Restore-and-continue determinism ....................... 🔴

* Verification authoritative when required-proof-set
  and tree-digest freshness pass.

=== GATE C ====================================================

19. Correct research registry ID collisions ................ ✅
20. Add DATA-* object type ................................ ✅
21. Harden experiment manifests ........................... ✅
22. Run EXP-DET-0001 (deterministic replay) ............... 🔴
23. Run EXP-STOR-0001 (snapshot/restore identity) ......... 🔴
24. Generate evidence from actual runs .................... 🔴
25. Close ALPHA.5 ......................................... 🎯
26. Begin alpha.6
```

---

# Structural Safety

```
[x] Proposal creation alone does not mutate the network
    Verified by structural E2E proof 5

[x] Reject does not mutate the network
    Verified by proof 6

[x] Manual approval required for canonical StructuralProposal mutation
    Verified by canonical E2E

[x] Dry-run mode implemented
    SelfOrganizationCoordinator(dry_run=True)

[ ] Auto-approval explicitly opt-in verified in production config

[x] Canonical approved mutation produces StructuralChangeRecord
    Verified by proof 8

[x] Canonical mutation linked to proposal_id
    Verified by proof 8

[x] Every production proposal attributable to runtime measurement
    E2E verified, production adapter still missing
```

---

# Bereits implementiert laut Changelog

- CRC-protected Structural Journal
- Commit markers
- Recovery uncommitted journal tails
- Deterministic structural replay
- Persistent inverse-record undo
- Manual proposal approval
- Optional policy-based approval
- Journal-backed structural history
- Structural heatmaps
- Typed dashboard structural routes
- Bounded tick execution routes
- Worker-boundary manual snapshot mechanism
- Ordered structural flush before snapshot
- .b5d snapshot writing capability
- Runtime checkpoint writing
- Snapshot completion notification
- Optional Structural Journal replay during restore
- Runtime checkpoint overlay after structural replay
- Single-instance Dashboard regression suite
- Bridge identity regression tests
- JSON-404 API isolation regression tests


* [x] Proof 5: Proposal alone does not mutate
* [x] Proof 6: Reject does not mutate
* [x] Proof 7: Approve causes exactly one mutation
* [x] Proof 8: Exactly one StructuralChangeRecord
* [x] Proof 9: Undo restores topology digest
* [x] Proof 10: Journal reopen/replay restores topology
* [x] Proof 11: Complete canonical structural E2E

---

# Homeostasis — Runtime Status

* [x] Canonical `HomeostasisSignal` added
* [x] Engine builder added
* [x] Dashboard bridge added historically
* [ ] Runtime-active path verified
* [ ] Convergence experiment
* [ ] Settling time / Overshoot / Steady-state error
* [ ] STDP interaction
* [ ] Structural interaction
* [ ] Evidence status

---

# Scientific Claim Ledger

* [x] Create `claims.yaml` (5 Claims)
* [x] Associate claims with Research Questions
* [x] Associate claims with literature
* [ ] Associate claims with experiments
* [ ] Associate claims with evidence
* [ ] Record contradicting evidence
* [ ] Record limitations

---

# Automatic Research Catalog

* [x] Build generator (`src/research/report_builder.py`)
* [x] Generate on demand (`research/generate_reports.py`)
* [ ] Generate on release
* [ ] Optionally generate through CI
* [x] Keep generated documents reproducible

---

# Automatic Evidence Matrix

* [x] Build evidence aggregation
* [ ] Separate positive and negative evidence
* [ ] Track replication count / independent seeds / contradictory evidence
* [x] Track confidence level

---

# v0.5.0-alpha.6 — Morphological Self-Regulation

> **BLOCKED until Alpha.5 Integration Gate passes.**

Chronic signals, growth budgets, regional pressures, telemetry, scientific evaluation.

---

# v0.6 — Scaling

Event-driven dirty tracking, chunked storage, domain decomposition, benchmark ladder 5k-1M.

---

# v0.7 — Learning Environment

Episode lifecycle, train/evaluation split, delayed reward tasks, learning curves, statistical replication.

---

# v0.8 — Embodiment

Text/image/audio sensor adapters, actuator adapters, perception-action-reward loop.

---

# v0.9 — Memory and World Model

Working context, long-term associative memory, goals, multi-step state.

---

# v0.10 — Cognitive Evaluation

Causal tasks, compositional generalization, neuro-symbolic experiments.

---

# v0.11 — Controlled Action and HMI

Permissions, resource limits, audit log, safe stop, sandbox.

---

# v0.12 — Release Candidate

Restore/continue soak tests, benchmark freeze, seven-day stability runs.

---

# v1.0 — Usable Brain-5D AI

Persistent, stable, reproducible, evaluable, multimodal learning system.
