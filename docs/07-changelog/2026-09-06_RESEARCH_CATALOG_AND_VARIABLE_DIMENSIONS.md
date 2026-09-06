# Research Catalog and Variable Projection Dimensions — 2026-09-06

## Purpose

This change closes a repository-integration gap discovered after the MSBA merge: the MSBA research programme existed in `research/registry/msba_experiments.yaml`, but its RQ/H identifiers were not loaded by the canonical `ResearchRegistry` and therefore were not normal first-class Experiment Workflow entries.

## Integrated

- canonical registry fragments `questions.*.yaml` and `hypotheses.*.yaml`;
- duplicate-ID fail-closed loading;
- canonical `RQ-MSBA-E01`–`RQ-MSBA-E05` and matching hypotheses;
- extensible RQ/H schema patterns;
- searchable Research Catalog UI with full-text RQ/H search and operational-only filter;
- explicit `OPERATIONAL` versus `EXPLORATORY` status in the selector;
- exploratory fallback only to `runtime_ticks_v1` for unmapped questions; no unrelated science-runner fallback;
- repository-wide read-only RQ/H reference-audit library;
- MSBA external projection dimensionality configurable from 1 to 32;
- schema/documentation distinction between projection dimensionality and the persisted productive 5D core.

## Scientific boundary

Searchability and experiment reachability are not evidence. An RQ/H without a dedicated frozen/preregistered protocol can be explored and logged, but it cannot be treated as confirmatory evidence merely because the dashboard can run ticks under that label.

The productive SNN core remains 5D because neuron-ID packing, spatial indexing and `.b5d` persistence are currently 5D contracts. Increasing `MSBAGatewayConfig.projection_dimensions` changes only an external/adaptor projection-space contract and does not rewrite or reinterpret historical 5D DATA/EVID.

## Explicitly open

The following are intentionally tracked in both canonical TODO and ROADMAP:

- dedicated protocol/preregistration/runner coverage for every still-unmapped canonical RQ/H;
- CI publication/triage of the repository-wide registry audit;
- a preregistered N-D projection sweep with dimension count as a causal experiment parameter;
- versioned productive-core N-D neuron-ID and `.b5d` migration;
- generalized N-D spatial indexing, neighborhood generation, locality and visualization;
- legacy-5D equivalence and high-dimensional scaling guards.
