# v0.4.0-alpha.2 – Delta Journal & Crash Recovery

## Completed scope

- append-only journal independent from `.b5d` V1;
- typed binary delta codecs;
- per-entry and per-commit CRC32;
- explicit durable commit boundaries;
- incomplete-tail recovery;
- committed-corruption rejection;
- real snapshot replay for neuron, synapse and topology changes;
- atomic recovered snapshot publication;
- no `Any` annotations in the new storage modules.

## Corrections to the original draft

The original draft rewrote header counters during commit, omitted ticks from
entry headers, used a non-existent `zlib.crc32_combine` API and counted replay
entries without applying them. Those behaviours are not present in the final
implementation.

## Exit criterion

A forced-tail test must reconstruct exactly the state at the most recent valid
commit. Committed CRC damage must never be silently accepted.
