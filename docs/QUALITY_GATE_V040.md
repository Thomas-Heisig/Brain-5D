# v0.4.0 Persistence Contract – Quality Gate

The final v0.4.0 tag is allowed only after all mandatory checks are green.

## Mandatory

- full pytest suite: 100% pass;
- deterministic restore-and-continue: exact reference equality;
- Black: no files would be reformatted;
- mypy: zero errors for the configured strict surfaces;
- Pylint: repository score >= 9.0 and no unresolved fatal/error findings;
- dashboard verification passes;
- `git diff --check` clean;
- 50k snapshot and 100k journal smoke tests pass when enabled;
- `.b5d` V1 format invariants unchanged.

## Not grounds for weakening the gate

A restore test must not be changed to approximate tolerance merely to hide
serialization precision loss.  Exact continuation uses the runtime checkpoint
sidecar instead.
