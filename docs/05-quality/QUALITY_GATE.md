# Brain-5D Release Quality Gate

A release may be tagged only after all required engineering and scientific-integrity gates are green for the release candidate tree.

## Required CI scopes

The current gate covers at least:

- pytest collection and full configured test matrix;
- Python 3.11, 3.12 and 3.13 compatibility;
- Black formatting;
- Ruff linting;
- Pylint quality/error diagnostics;
- Mypy strict configured scope;
- Pyright main and integration scopes;
- Pre-Commit hooks;
- security checks including Bandit and dependency audit;
- Scientific Integrity Gate;
- documentation consistency/link checks;
- deterministic persistence/restore verification;
- wheel build/install verification;
- Docker verification where configured;
- opt-in large-storage validation through its dedicated workflow/job.

A representative local verification set is:

```powershell
python -m pytest -q
python -m black --check src tests scripts
python -m ruff check src tests scripts
python -m mypy src
python -m pyright
python -m pre_commit run --all-files
python scripts/verify_dashboard.py
python scripts/verify_network_activity.py
git diff --check
```

The exact GitHub Actions workflow remains authoritative for release automation.

## Current verified baseline — 2026-09-05

- test collection: **735**
- verified repair-suite result: **733 passed, 2 skipped, 0 failed**
- latest completed full GitHub CI run on the repaired main baseline: **success**
- Python 3.11 / 3.12 / 3.13: **pass**
- Black / Ruff / Pylint / Pre-Commit: **pass**
- Mypy / Pyright: **pass**
- Security: **pass**
- Scientific Integrity: **pass**

Do not substitute an older `tests/test_baseline.json` snapshot for current CI status. That file is a versioned verification artifact and may intentionally describe an earlier tested tree until it is regenerated through its proper verification workflow.

## Scientific gate rule

Engineering success is necessary but not sufficient for scientific evidence.

A release must not describe a scientific claim as established solely because:

- tests are green;
- the dashboard shows activity;
- a network produces spikes;
- a generated report is positive;
- an AI assistant assigns high confidence.

Scientific claims require registered protocol, appropriate controls, experiment-local DATA, provenance, reproducibility where required and human/evidence review.

Historical experiment DATA must not be rewritten after instrumentation changes. The repaired Network-Impulse probe therefore applies to new runs; `EXP-GEN-0009` through `EXP-GEN-0012` remain traceable historical observations.

## Required outcome

- pytest: no unexpected failures; skips must be intentional and documented;
- formatting/lint/pre-commit: clean;
- Mypy/Pyright: zero errors in required scopes;
- Pylint: no unresolved fatal/error diagnostics and configured score threshold satisfied;
- dashboard verification: pass;
- network activity diagnostic: pass for the registered diagnostic configuration;
- deterministic restore: exact contract equality, not tolerance-based substitution;
- scientific-integrity checks: pass/fail closed;
- security checks: pass or explicitly accepted documented non-functional warning under release policy;
- documentation consistency: pass;
- `git diff --check`: no whitespace errors.

The quality gate must never be bypassed with broad `Any`, blanket `type: ignore`, disabled scientific checks, fabricated telemetry or by changing expected test values without establishing that the expectation was stale.
