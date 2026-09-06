# Brain-5D Documentation

This directory contains both **current canonical documentation** and **historical/versioned records**. Historical Alpha, Sprint, Release and dated change documents remain traceability artifacts and must not be read as the current repository state.

## Source of truth

When documents disagree, use this order:

1. code, configuration schemas and machine-readable contracts on `main`;
2. current CI and verification artifacts;
3. experiment `DATA/` and accepted `EVID` records;
4. the canonical documents listed below;
5. historical/versioned documents;
6. narrative or AI-generated interpretation.

Passing tests prove engineering behavior covered by those tests; they do not automatically establish a scientific claim.

## Current baseline — 2026-09-06

- canonical branch: `main`
- package version: `0.5.0a7`
- current pytest collection: **791 tests**
- Research Catalog / variable-projection-dimension merge: `85e7209509b348bf7912dde01d3d9ebb078a2e61`
- latest fully completed pre-merge `main` CI baseline: **success** (run #598)
- Python matrix: **3.11 / 3.12 / 3.13**
- Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, Security, Scientific Integrity, wheel and Docker checks remain mandatory CI gates
- post-merge CI is authoritative for the merged baseline; do not describe it as fully green until the corresponding `main` run completes
- historical experiment DATA/EVID remains unchanged by documentation or registry cleanup

Historical `EXP-GEN-0009` to `EXP-GEN-0012` artifacts remain untouched. They recorded zero observable activity under the older probe contract. Current instrumentation measures published spike IDs plus tick, neuron and synaptic-event activity and persists those fields in new experiment DATA.

## Canonical current documents

| Area | Canonical document |
| --- | --- |
| Project overview | [`../README.md`](../README.md) |
| Architecture | [`02-architecture/ARCHITECTURE.md`](02-architecture/ARCHITECTURE.md) |
| Adaptive Wesen body view | [`02-architecture/WESEN_ADAPTIVE_BODY.md`](02-architecture/WESEN_ADAPTIVE_BODY.md) |
| Neural Symbiosis / multi-network embodiment | [`02-architecture/NEURAL_SYMBIOSIS.md`](02-architecture/NEURAL_SYMBIOSIS.md) |
| MSBA / modality-specific pathways and energy homeostasis | [`02-architecture/MSBA.md`](02-architecture/MSBA.md) |
| Storage format | [`02-architecture/B5D_FORMAT.md`](02-architecture/B5D_FORMAT.md) |
| Real-body embodiment | [`02-architecture/EMBODIMENT_REAL_BODY.md`](02-architecture/EMBODIMENT_REAL_BODY.md) |
| Learning preparation | [`02-architecture/LEARNING_PREPARATION_STUDIO.md`](02-architecture/LEARNING_PREPARATION_STUDIO.md) |
| Dashboard | [`03-dashboard/DASHBOARD.md`](03-dashboard/DASHBOARD.md) |
| API reference | [`03-dashboard/API_REFERENCE.md`](03-dashboard/API_REFERENCE.md) |
| Quality gate | [`05-quality/QUALITY_GATE.md`](05-quality/QUALITY_GATE.md) |
| Research positioning & evidence program | [`06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`](06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md) |
| Development roadmap | [`08-roadmap/ROADMAP.md`](08-roadmap/ROADMAP.md) |
| Current TODO | [`08-roadmap/TODO.md`](08-roadmap/TODO.md) |
| Research roadmap | [`08-roadmap/RESEARCH_ROADMAP.md`](08-roadmap/RESEARCH_ROADMAP.md) |
| Research/evidence system | [`../research/README.md`](../research/README.md) |
| Security | [`../SECURITY.md`](../SECURITY.md) |
| Contribution workflow | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |

## Current research-registry contract

The normal research workflow loads canonical base registries plus deterministic fragments:

- `research/registry/questions.yaml`
- `research/registry/questions.*.yaml`
- `research/registry/hypotheses.yaml`
- `research/registry/hypotheses.*.yaml`

Duplicate identifiers fail closed. MSBA questions/hypotheses are first-class entries rather than side documentation. The Experiment Workflow exposes them through a searchable Research Catalog and distinguishes questions with frozen/preregistered operational protocols from exploratory-only questions. Exploratory execution must not be confused with confirmatory evidence.

The repository-wide RQ/H audit reports references that are not represented in the canonical registry without rewriting historical sources.

## Current dashboard terminology

- **Overview** — summary/runtime context;
- **Control** — explicit operator controls;
- **Research** — research/evidence workflows and searchable Research Catalog;
- **Settings** — configuration;
- **Wesen** — adaptive read-only live machine-body visualization;
- **Embodiment** — technical sensor/device/actuator/body-boundary surface;
- **Neural Symbiosis** — read-only multi-network/virtual-pipeline view inside `Wesen`;
- **MSBA** — modality-specific audio/vision/digital gateway contract plus resource/energy model inside Neural Symbiosis;
- **Release/Gate** — footer-accessed release-readiness surface;
- **Network** — no longer a primary user-facing workspace.

`Wesen`, Neural Symbiosis and MSBA must never be described as proof of consciousness, self-awareness, causal tool use or learned sensor control. Reachability, recurrence, loopback, morphology, pipeline availability, energy allocation candidates and gateway candidates are engineering/observation state until a preregistered experiment produces reviewable DATA/EVID.

## Scientific boundary for Neural Symbiosis, MSBA and dimensions

The multi-network layer is part of Embodiment, not a rewrite of the SNN core. Peripheral CNN/Transformer/RNN/GNN/memory/generative/custom networks and virtual systems such as logic or knowledge databases are connected only through explicit adapter/gateway contracts.

MSBA specializes those gateway contracts by modality:

- audio: temporal-coherence features and candidate phase-weighted t-STDP;
- vision: spatial multiplexing, fixed sparse target degree and candidate locality/information/resource structural growth;
- digital: exact immutable payload outside the SNN, deterministic population representation and candidate meta-gating only;
- resource pressure: normalized energy accounting, explicit estimate-vs-measurement provenance and deterministic NORMAL/CONSERVE/CRITICAL/SURVIVAL protection states.

Current dimension rule:

- MSBA/external projection spaces may declare **1–32 dimensions**;
- the productive persisted SNN core remains **5D** for compatibility;
- productive core >5D requires a separately versioned neuron-ID/storage representation, generalized spatial indexing, `.b5d` migration, canonical state/equivalence tests and preregistered experiments;
- increased-dimensional projection experiments must not be mislabeled as productive-core N-D evidence.

Current gateway rules:

- open-set `NetworkAreaAdapter` contract;
- framework-neutral peripheral implementations;
- pipeline templates are disabled until explicitly instantiated;
- Neural-Symbiosis and MSBA gateway learning/growth/allocation are disabled by default;
- gateway RNG belongs to an experiment runner and must be persisted;
- endpoint reachability is not evidence of learned use;
- fixed semantics are not imposed on the five Brain-5D axes;
- measured joules are never inferred from normalized units without explicit calibration/provenance;
- historical DATA/EVID is never rewritten to reflect new adapters.

See [`02-architecture/NEURAL_SYMBIOSIS.md`](02-architecture/NEURAL_SYMBIOSIS.md) and [`02-architecture/MSBA.md`](02-architecture/MSBA.md).

## Experiment-data compacting rule

Large experiment series preserve raw observations in immutable/compressed artifacts. Bounded projections such as `runs.json` and `analysis/ai_packet.json` exist for UI/review/small-model consumption and must carry provenance back to the raw record. Compact files are not replacements for scientific raw DATA.

## Directory map

- `01-guides/` — operator/developer guides;
- `02-architecture/` — architecture and subsystem contracts;
- `03-dashboard/` — dashboard contracts and UI/API documentation;
- `04-integration/` — integration notes and overlays;
- `05-quality/` — quality and release-gate definitions;
- `06-research/` — research notes and canonical research-positioning documents;
- `07-changelog/` — dated change records;
- `08-roadmap/` — current roadmap/TODO plus historical phase-specific roadmaps;
- `09-sprints/` — time-boxed sprint records;
- `10-releases/` — release checklists and notes;
- `11-readme/` — historical README blocks;
- `12-updates/` — update manifests and integration snapshots;
- `99-archive/` — explicitly archived legacy material.

## Historical-document rule

A filename containing a previous version, `ALPHA*`, `SPRINT*`, `V0*`, `UPDATE*`, `RELEASE_*`, or an entry under `99-archive/` is historical unless a canonical current document links to it as an active contract. Old test counts, commit hashes, milestones and implementation status in those files are not current project metadata.

Historical experiment DATA must not be silently rewritten when instrumentation improves. Corrections belong in code, canonical documentation and new versioned experiments.

## Documentation maintenance

Avoid copying fixed test counts or commit hashes into many current documents. Where a fixed number is useful, date it and treat it as a verified snapshot. Scientific conclusions must cite experiment/evidence artifacts, not README prose or dashboard state alone.

**Current development policy:** `main` is canonical. Short-lived branches start from current `origin/main`, are verified before merge, and should be deleted after merge when repository tooling permits. A branch with no commits ahead of `main` contains nothing to integrate and must not be merged merely to make the branch list empty.
