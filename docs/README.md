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

## Documentation maintenance

Current-state facts should be stated in canonical documents and linked elsewhere. Avoid copying fixed test counts or commit hashes into many files because they become stale quickly. Scientific conclusions must cite experiment/evidence artifacts, not README prose or dashboard state alone.

The 2026-09-05 adaptive Wesen redesign is recorded in [`07-changelog/2026-09-05_WESEN.md`](07-changelog/2026-09-05_WESEN.md).

**Current development policy:** `main` is the canonical branch. Short-lived branches should be merged through reviewed/verified changes and deleted after merge. New work starts from current `origin/main`.
