# Brain-5D v0.5.0-alpha.2 - Dashboard Compatibility and Stability Bridge

## Purpose

v0.5.0-alpha.1 introduced active homeostatic regulation. During that overlay the
older alpha.6 homeostasis dashboard contract and the alpha.7 embodiment field
were accidentally shadowed. alpha.2 restores those public contracts without
rolling back the v0.5 regulator.

## Compatibility contract

The dashboard now publishes both naming generations:

- `actual_rate_hz` and `rate_error_hz` (alpha.6 compatibility)
- `mean_rate_hz` and `mean_rate_error_hz` (v0.5 canonical regulator metrics)

Both pairs resolve to the same values. New code should use the `mean_*` names;
legacy API consumers can continue to use the alpha.6 names during the v0.5
series.

`DashboardSnapshot` again carries `EmbodimentMetrics`, preserving the alpha.7
embodiment foundation.

## Protocol quality fix

The embodiment `Protocol` methods now use explicit `...` bodies. This keeps
runtime behavior unchanged while preventing Pylint from interpreting protocol
methods as functions returning `None`.

## Release checks

```powershell
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_v050a1.py
git diff --check
```

Expected critical result: all dashboard alpha.6, alpha.7 and v0.5 tests pass.

## Next target

v0.5.0-alpha.3 will concentrate on long-run self-regulation: a 100,000-tick
stability experiment, homeostasis heatmaps, and explicit coordination rules
between threshold regulation and structural neurogenesis/pruning.
