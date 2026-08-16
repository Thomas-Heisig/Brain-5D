# Brain-5D v0.5.0-alpha.5 – Structural Persistence

Alpha.5 adds a persistent audit trail for structural plasticity. The intended chain is:

`HomeostasisSignal -> StructuralProposal -> Approval -> StructuralPlasticityEngine -> Manipulator -> StructuralChangeRecord -> StructuralJournal -> Undo/Recovery/Heatmap`

## Safety defaults

Auto approval is **off** by default. Dry-run is **on** by default. Neuron pruning is **off** by default. The journal is append-only; undo is represented as a new inverse record and never deletes history.

## Persistent contract

The long-running system now treats four artifacts as one logical persistence contract:

1. `.b5d` snapshot
2. state delta journal
3. runtime checkpoint
4. structural journal

Restore must apply them deterministically and validate topology after structural replay.

## Snapshot lifecycle

Manual snapshots are queued onto the runtime worker and execute only at a safe
batch boundary. `StructuralSnapshotLifecycle` durably flushes the structural
journal, writes the `.b5d` snapshot, writes the runtime checkpoint, and only then
reports completion to the dashboard.

## Restore order

`restore_network(..., structural_journal_path=...)` reconstructs the base `.b5d`
plus committed state deltas, replays committed structural records through
`Brain5DManipulator`, and then overlays the runtime checkpoint. Uncommitted
structural tails remain ignored.
