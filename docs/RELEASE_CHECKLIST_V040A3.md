# Release Checklist – Brain-5D v0.4.0-alpha.3

## Snapshot compatibility

- [ ] `.b5d` V1 invariants pass unchanged.
- [ ] Existing alpha.1 snapshot fixtures remain readable.
- [ ] `src/storage/b5d.py` format constants did not change.

## Journal / recovery

- [ ] CRC known-vector and round-trip tests pass.
- [ ] Journal entry/commit sizes remain fixed.
- [ ] Monotonic sequence/tick tests pass.
- [ ] Uncommitted tail is ignored/truncatable.
- [ ] Committed CRC corruption fails hard.
- [ ] Recovery applies neuron/synapse deltas.
- [ ] Recovery publishes via temporary file + `os.replace()`.

## Alpha.3 runtime/lazy layer

- [ ] `StorageSession` remains disabled by default.
- [ ] Runtime hook captures changed state and topology.
- [ ] Commit cadence is configurable.
- [ ] Lazy snapshot heatmaps do not instantiate a live network.
- [ ] Activity, weight and energy projections contain finite values.

## Clean Code

- [ ] `black --check ...`
- [ ] `mypy --strict src/storage`
- [ ] `pylint src/storage`
- [ ] `pyright src/storage` if installed
- [ ] no `Any` in new/changed storage modules
- [ ] no unexplained `type: ignore`

## Performance smoke tests

- [ ] 50k-neuron snapshot smoke test.
- [ ] 100k-entry journal smoke test.
- [ ] Storage overhead measured on the reference PoC before `src.main`
      auto-integration is enabled.

## Release rule

Do not tag v0.4.0 final from this checklist. Alpha.3 still needs bounded
asynchronous I/O/back-pressure, measured runtime overhead, safe long-journal
compaction and restore-and-continue against the real `NeuralNetwork`.

## Windows verification without PowerShell signature changes

The canonical verifier is now the cross-platform Python runner:

```powershell
python scripts/verify_b5d.py
```

Windows users can also run:

```cmd
scripts\verify_b5d.cmd
```

This avoids machine-wide PowerShell execution-policy changes. The `.ps1` file is only a convenience wrapper. If it is intentionally used in a restricted shell, a process-local policy may be selected explicitly by the operator; the repository never changes the user's policy automatically.

## Generated package metadata

`pip install -e ".[dev]"` may refresh `src/brain5d_core.egg-info/`. These files are generated build metadata, not Brain-5D source state. `.gitignore` now excludes `*.egg-info/` for new checkouts.

If the directory was already tracked by Git before this rule was added, remove it from the index once while keeping the local generated files:

```powershell
git rm -r --cached src/brain5d_core.egg-info
git add .gitignore
git commit -m "chore: stop tracking generated egg-info metadata"
```

Before the release commit, `git status --short` must not contain generated `egg-info`, `.pytest_cache`, `__pycache__`, `.mypy_cache`, build, or distribution output.
