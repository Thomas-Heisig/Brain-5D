# Brain-5D Crash Recovery

## Recovery contract

A restart-capable `.b5d` snapshot is immutable input. Recovery reads the base
snapshot, replays only committed journal entries into a typed in-memory
reconstruction, writes a temporary snapshot, validates it, fsyncs it and then
uses `os.replace()` to publish the recovered file.

The original snapshot is never modified in place while replay is running.

## Crash cases

| Crash/corruption | Result |
|---|---|
| before first commit | base snapshot only |
| partial entry header | ignore/truncate tail |
| partial payload | ignore/truncate tail |
| complete entries without commit | ignore/truncate tail |
| partial commit marker | use previous complete commit |
| valid commit | replay through marker |
| CRC error in committed entry | hard corruption error |
| sequence/tick regression | hard corruption error |

## Replayed state

Alpha.3 recovery applies:

- neuron dynamic state;
- synapse weight/eligibility state;
- neuron add/remove;
- synapse add/remove.

Spike-event records are diagnostic and do not mutate the recovered snapshot.
`PARAMETER` is reserved and rejected until the v0.5 homeostasis state contract
is defined.

## Platform note

`os.replace()` provides atomic replacement semantics for the target path on
supported local filesystems. Directory-level durability differs between
platforms; Windows does not expose the same directory-fsync pattern as POSIX.
The release documentation therefore distinguishes **file atomicity** from a
formal power-loss guarantee for every filesystem/controller combination.
