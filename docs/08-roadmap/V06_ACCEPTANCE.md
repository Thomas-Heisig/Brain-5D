# v0.6 Scaling & Deterministic Performance — Acceptance Contract

This document closes the ambiguity between the v0.6 engineering milestone and the scientific evidence programme. Passing these checks is an engineering release condition only; it does not promote an experiment, AIRR, hypothesis or research question to EVID.

## 1. Persistence compatibility

- B5D snapshot format remains frozen at V1 (`src/storage/b5d.py`).
- Delta journal remains frozen at V1 (`src/storage/delta_journal.py`).
- `src/storage/v06_contract.py` binds v0.6 to those versions and requires restart-capable snapshots.
- v0.6 introduces no binary persisted-state schema rewrite. Migration and rollback are therefore an explicit `NOOP_FROZEN_FORMAT` / `BYTE_IDENTITY` contract. `tests/test_v06_contract.py` verifies that compatibility inspection leaves the snapshot SHA-256 unchanged.

## 2. Bounded research data

`src/research/data_v2.py` is the canonical long-run data contract:

- immutable raw runs are compressed under `DATA/raw/`;
- `DATA/runs_index.json` indexes raw runs and records SHA-256 provenance;
- `DATA/current_run.json` is bounded mutable writer state;
- the compact `DATA/runs.json` projection never has to contain unbounded nested traces;
- AI input is bounded and raw detail is only loaded by deterministic indexed extraction.

`tests/test_research_data_v2.py` exercises large nested traces, compact projection, raw preservation and deterministic detail extraction.

## 3. Scaling and performance budgets

`scripts/benchmark_ladder.py` reports, per tier:

- neuron and synapse counts;
- construction time;
- mean tick cost;
- ticks/second, neurons/second and synapses/second;
- Python peak allocation bytes and bytes/neuron via `tracemalloc`;
- Python/platform/seed configuration.

`configs/v06_performance_budgets.json` defines conservative cross-runner engineering ceilings. `src/diagnostics/performance_contract.py` validates scaling, RuntimeController latency, structural/learning/storage/dashboard phase budgets and pacing telemetry. These are regression limits, not scientific performance claims.

## 4. Runtime identity and pacing

- `tests/test_v06_pause_resume_identity.py` proves an exact pause at tick 5 and resume to tick 10 reaches the same deterministic state digest as an uninterrupted ten-tick run.
- existing restore/golden-chain tests cover restart identity and persisted engine state.
- the normal CI test matrix executes the contracts on Python 3.11, 3.12 and 3.13.
- target-Hz telemetry exposes requested target, achieved Hz and realtime ratio.
- `MAX` is the explicit unlimited-mode identity.
- finite targets must report `TARGETED` or `COMPUTE LIMITED`; the shared acceptance rule requires achieved Hz to remain at least 75% of target for a pacing acceptance sample, while realtime ratio must equal achieved Hz multiplied by simulation `dt` within the configured tolerance.

## 5. Research workspace and archive safety

The dashboard Research workspace is organized into four working views: **Planen & Ausführen**, **Läufe & Reihen**, **Reviews**, and **Dateien & Analyse**. Major Research surfaces participate in the shared minimize/standard/maximize box-state controller.

The experiment archive is a work-view filter, not a filesystem relocation mechanism. `research/archive/experiment_index.json` stores only archive metadata, reason, timestamp and manifest digest. Canonical experiment files remain under `research/experiments/<id>`. Legacy moved archives are still discoverable and can be restored once.

## 6. Release gate

The repository CI already requires the following before its aggregate `ci-status` can pass on `main`:

- Black/Ruff/Pylint/pre-commit/whitespace;
- Mypy and Pyright;
- Bandit and pip-audit;
- full tests on Python 3.11, 3.12 and 3.13;
- Chromium browser smoke and Playwright E2E;
- Scientific Integrity Gate and catalog audit;
- wheel build and clean install;
- Docker build and runtime smoke;
- documentation consistency.

A v0.6 immutable release record must only be created in the publication phase after the exact source-freeze commit has a green aggregate CI result and the release-readiness snapshot reports `ready=true`. The release-record commit may contain only publication/evidence/documentation metadata required to record that already-green source freeze; it must not silently change the verified runtime source.

## Acceptance boundary

A green v0.6 engineering gate means the software contracts above are reproducible and release-ready. It does **not** establish biological plausibility, consciousness, intelligence, superiority of a dimensional representation, or support/refutation of a registered scientific hypothesis.
