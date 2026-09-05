# Brain-5D Documentation

This directory contains both **current canonical documentation** and **historical versioned records**. Historical Alpha, Sprint, Release and Update documents remain useful for traceability, but they must not be read as the current repository state.

## Source of truth

When documents disagree, use this order:

1. code, configuration schemas and machine-readable contracts on `main`;
2. current CI and verification artifacts;
3. experiment `DATA/` and accepted `EVID` records;
4. the canonical documents listed below;
5. historical/versioned documents;
6. narrative or AI-generated interpretation.

Passing tests prove engineering behavior covered by those tests; they do not automatically establish a scientific claim.

## Verified current baseline — 2026-09-05

- canonical branch: `main`
- package version: `0.5.0a7`
- current collection: **735 tests**
- latest complete GitHub CI run: **success**
- verified repair-suite result: **733 passed, 2 skipped, 0 failed**
- Python matrix: **3.11 / 3.12 / 3.13**
- Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, security and Scientific Integrity checks: **green**
- open pull requests at verification point: **none**
- `tmp-do-not-use`: obsolete branch, zero commits ahead of `main`; not a development source

The historical `EXP-GEN-0009` to `EXP-GEN-0012` artifacts remain untouched. They recorded zero observable activity under the older probe contract. Current instrumentation measures all published spike IDs plus tick, neuron and synaptic-event activity and persists those fields in new experiment DATA.

## Canonical current documents

| Area | Canonical document |
| --- | --- |
| Project overview | [`../README.md`](../README.md) |
| Architecture | [`02-architecture/ARCHITECTURE.md`](02-architecture/ARCHITECTURE.md) |
| Adaptive Wesen body view | [`02-architecture/WESEN_ADAPTIVE_BODY.md`](02-architecture/WESEN_ADAPTIVE_BODY.md) |
| Storage format | [`02-architecture/B5D_FORMAT.md`](02-architecture/B5D_FORMAT.md) |
| Real-body embodiment | [`02-architecture/EMBODIMENT_REAL_BODY.md`](02-architecture/EMBODIMENT_REAL_BODY.md) |
| Learning preparation | [`02-architecture/LEARNING_PREPARATION_STUDIO.md`](02-architecture/LEARNING_PREPARATION_STUDIO.md) |
| Dashboard | [`03-dashboard/DASHBOARD.md`](03-dashboard/DASHBOARD.md) |
| API reference | [`03-dashboard/API_REFERENCE.md`](03-dashboard/API_REFERENCE.md) |
| Quality gate | [`05-quality/QUALITY_GATE.md`](05-quality/QUALITY_GATE.md) |
| Development roadmap | [`08-roadmap/ROADMAP.md`](08-roadmap/ROADMAP.md) |
| Current TODO | [`08-roadmap/TODO.md`](08-roadmap/TODO.md) |
| Research roadmap | [`08-roadmap/RESEARCH_ROADMAP.md`](08-roadmap/RESEARCH_ROADMAP.md) |
| Research/evidence system | [`../research/README.md`](../research/README.md) |
| Network observability/CI repair | [`07-changelog/2026-09-05_NETWORK_OBSERVABILITY_AND_CI.md`](07-changelog/2026-09-05_NETWORK_OBSERVABILITY_AND_CI.md) |
| Security | [`../SECURITY.md`](../SECURITY.md) |
| Contribution workflow | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |

## Current dashboard terminology

The canonical frontend terminology is:

- **Overview** — summary/runtime context;
- **Control** — explicit operator controls;
- **Research** — research/evidence workflows;
- **Settings** — configuration;
- **Wesen** — adaptive read-only live machine-body visualization;
- **Embodiment** — technical sensor/device/actuator/body-boundary surface;
- **Release/Gate** — footer-accessed legacy release-readiness surface;
- **Network** — no longer a primary user-facing workspace.

`Wesen` must never be described as proof of consciousness or self-awareness. Its recurrence, loopback, morphology and body-state visuals are technical observations/derived presentation state only.

## Current experiment-observability contract

New Science Runner impulse experiments persist network observables rather than only the output-neuron projection. The current response signature covers:

- `ticks_executed`;
- activated neurons and total spikes;
- complete observed spike sequence and deterministic digest;
- delivered synaptic events;
- ticks with synaptic activity;
- maximum current-target count;
- total synapse count;
- first/last response latency;
- propagation depth;
- recurrent/return events and return latency where present;
- before/after state digests.

This instrumentation makes runtime activity inspectable, but a nonzero spike count is still an observation, not a scientific causal conclusion.

## Directory map

- `01-guides/` — operator/developer guides. Version-specific installation/hotfix guides may be historical.
- `02-architecture/` — architecture and subsystem contracts.
- `03-dashboard/` — dashboard contracts and UI/API documentation.
- `04-integration/` — integration notes, overlays and legacy patches.
- `05-quality/` — quality and release-gate definitions.
- `06-research/` — research notes, dissertations and conceptual documents; not automatically empirical evidence.
- `07-changelog/` — changelog history, including dated current-change records.
- `08-roadmap/` — current roadmap/TODO plus historical phase-specific roadmaps.
- `09-sprints/` — time-boxed sprint records; historical unless explicitly referenced by current roadmap.
- `10-releases/` — release checklists and release notes.
- `11-readme/` — historical README blocks retained for traceability.
- `12-updates/` — update manifests and integration snapshots.
- `99-archive/` — explicitly archived legacy material.

## Historical-document rule

A filename containing a previous version, `ALPHA*`, `SPRINT*`, `V0*`, `UPDATE*`, `RELEASE_*`, or an entry under `99-archive/` is a historical record unless a canonical current document links to it as an active contract. Old test counts, commit hashes, milestones and implementation status inside those files are not current project metadata.

Historical experiment DATA must not be silently rewritten when instrumentation improves. Corrections belong in code, documentation and new versioned experiments so that negative and incomplete observations remain traceable.

## Documentation maintenance

Current-state facts should be stated in canonical documents and linked elsewhere. Avoid copying fixed test counts or commit hashes into many files because they become stale quickly. Scientific conclusions must cite experiment/evidence artifacts, not README prose or dashboard state alone.

The 2026-09-05 adaptive Wesen redesign is recorded in [`07-changelog/2026-09-05_WESEN.md`](07-changelog/2026-09-05_WESEN.md). The network-observability and CI-repair pass is recorded in [`07-changelog/2026-09-05_NETWORK_OBSERVABILITY_AND_CI.md`](07-changelog/2026-09-05_NETWORK_OBSERVABILITY_AND_CI.md).

**Current development policy:** `main` is the canonical branch. Short-lived branches should be merged through reviewed/verified changes and deleted after merge. New work starts from current `origin/main`. Obsolete branches must not be merged merely to make the branch list empty; a branch with no commits ahead of `main` contains nothing to integrate.
