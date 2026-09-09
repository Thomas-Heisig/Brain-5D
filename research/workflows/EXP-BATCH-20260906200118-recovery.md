# EXP-BATCH-20260906200118: Recovery lineage

This document does not modify the historical workflow result. The original aggregate report remains the audit record that two children failed during that execution.

## Historical failures

- `independent_replication_v1` failed because `REPLICATION` was not accepted by the run-mode governance enum at that point in the execution lineage.
- `learning_interference_screen_v1` failed because transient trial dynamics were not reset before a lower-drive task, so the training drive did not spike all declared presynaptic neurons.

## Current technical state

Both failure causes are repaired in the current codebase. `ResearchRunMode.REPLICATION` is supported, and the learning laboratory can reset transient neuron/event state between independent timing episodes while preserving learned weights. Dedicated retry artifacts already show successful technical execution for `EXP-REPL-0001-R1` and `EXP-LIFE-0001-R1`.

Those earlier retry artifacts were produced from a dirty source tree and therefore remain blocked from automatic evidence use. Their successful completion is a technical regression signal, not scientific promotion.

## Clean recovery procedure

A new recovery helper creates a fresh batch containing only historically failed operational children, while copying each child's recorded tick and seed settings. It never edits this workflow or the source workflow report.

Dry run:

```text
python -m src.research.workflow_recovery EXP-BATCH-20260906200118 --research-root research --dry-run
```

Clean execution after CI/gate verification:

```text
python -m src.research.workflow_recovery EXP-BATCH-20260906200118 --research-root research
```

The new recovery batch receives a distinct `EXP-RETRY-*` identifier. DATA, manifest, statistics, workflow and any post-hoc AIRR generated for that retry belong to the new execution lineage. No artifact from recovery is automatically promoted to EVID.
