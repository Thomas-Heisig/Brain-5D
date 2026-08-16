# v0.4.0 Persistence Quality Gate

The persistence milestone may be tagged `v0.4.0` only when all gates below pass
on the real Windows repository checkout.

## Functional

- full `pytest` suite passes
- 50k `.b5d` smoke test passes
- 100k journal smoke test passes
- deterministic restore-and-continue test passes
- dashboard tests pass

## Static quality

- `black --check src tests` reports no changes
- `mypy src` reports zero errors
- `pylint src` score is at least 9.0
- `mypy --strict src/dashboard` reports zero errors
- `git diff --check` reports no whitespace errors

## Dashboard

- `/healthz` returns success
- `/api/status` returns valid JSON
- heatmap API works when a snapshot is configured
- dashboard remains read-only
- homeostasis metrics are present as a v0.5 bridge but do not change core state

## Persistence terminology

A `.b5d` snapshot alone is not advertised as bit-exact continuation. Exact
continuation requires snapshot + committed journal + runtime checkpoint v2.
