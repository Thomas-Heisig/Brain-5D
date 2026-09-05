# Research DATA v2

Status: canonical research-data handling for new Science Runner experiments.

## Purpose

Large scientific traces must remain auditable without forcing a small local language model to parse hundreds of megabytes of JSON. Research DATA v2 therefore separates raw observations, deterministic statistics and bounded AI inputs.

## Artifact layout

For a new experiment `<EXP-ID>`:

```text
research/experiments/<EXP-ID>/
├── DATA/
│   ├── runs.json                 # compact projection of this experiment only
│   ├── runs_index.json           # immutable raw-run index + SHA-256
│   ├── current_run.json          # bounded writer state; reset to idle after archive
│   └── raw/
│       └── run-*.json.gz         # complete immutable run observations
├── analysis/
│   ├── statistics.json           # deterministic statistics from complete observations
│   ├── ai_packet.json            # bounded default LLM input
│   ├── ai_packet_digest.json     # packet/index integrity metadata
│   └── detail/                   # optional deterministic condition extracts
├── manifest.json
├── workflow.json
└── summary.md
```

## Write order

1. Execute the registered runner.
2. Compute `analysis/statistics.json` from the complete in-memory observations.
3. Archive every complete run independently as compressed JSON under `DATA/raw/`.
4. Record path, seed, condition, SHA-256 and byte sizes in `DATA/runs_index.json`.
5. Replace long sequences in the review projection with deterministic head/tail/count representations.
6. Write the compact experiment-local `DATA/runs.json`.
7. Build `analysis/ai_packet.json` from deterministic statistics and bounded run previews.
8. Write the packet digest and manifest references.
9. The Research Assistant reads `ai_packet.json` by default and does not open raw run archives.

`DATA/current_run.json` is a bounded state marker rather than an accumulating history file. During archival it identifies the current run; after each archive it returns to `status: idle` and contains only the last archive reference.

## Hard limits

Current implementation fails closed when:

- `analysis/ai_packet.json` would exceed **1 MB**;
- compact `DATA/runs.json` would exceed **5 MB**;
- a requested AI detail packet would exceed **1 MB**.

A limit violation must be solved by stronger deterministic aggregation or a narrower detail request, never by silently feeding raw data to the model.

## Detail extraction

When an interpretation needs more information than the default packet contains, `build_detail_packet()` / `write_detail_packet()` in `src/research/data_v2.py` can select a single indexed condition and a requested metric set. The extractor verifies the raw archive SHA-256 before reading it and returns another bounded packet.

This keeps the AI read-only: it requests or receives a deterministic projection; it never chooses which raw records to delete, rewrite or promote to evidence.

## Scientific integrity

Raw observations are **not deleted** by compaction. Compression changes storage representation, not the measured content. The manifest/data digest includes the compact projection, raw index, AI packet metadata and compressed raw-run artifacts.

Historical experiments are not rewritten to conform to DATA v2. The Research Assistant retains a bounded legacy fallback for experiments created before `analysis/ai_packet.json` existed.

## Relationship to evidence

DATA v2 changes storage and review mechanics only. It does not turn DATA into EVID. Evidence still requires the registered RQ/H pair, compatible frozen protocol, valid preregistration, clean provenance, semantic match and human scientific review.
