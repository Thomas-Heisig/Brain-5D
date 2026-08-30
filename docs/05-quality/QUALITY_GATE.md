# Brain-5D Release Quality Gate

A release may be tagged only after all required gates are green:

```powershell
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_dashboard.py
git diff --check
```

Required outcome:

- pytest: 100% passing
- Black: no files would be reformatted
- mypy: zero errors for the configured strict scope
- Pylint: score >= 9.0 and no unresolved fatal/error diagnostics
- dashboard verification: pass
- deterministic restore test: exact equality, not tolerance-based equality
- git diff check: no whitespace errors

Warnings that are explicitly documented and non-functional may be accepted only
with a release-note entry. The quality gate must never be bypassed with broad
`Any` or blanket `type: ignore` additions.
