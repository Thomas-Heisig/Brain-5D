# Pull Request

## Summary

Describe the change and its motivation.

Fixes # (issue, if applicable)

## Type

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Test
- [ ] Documentation
- [ ] Tooling / CI
- [ ] Breaking change

## Architecture impact

Describe affected boundaries and compatibility considerations.

## Verification

List the exact commands run and results.

- [ ] `pytest -m "not slow"`
- [ ] `mypy src`
- [ ] `black --check src tests scripts`
- [ ] `ruff check src/ tests/ scripts/`
- [ ] `pyright`
- [ ] Pyright/Pylance clean for changed/new files
- [ ] Pylint quality threshold maintained
- [ ] `git diff --check`
- [ ] Slow tests run when relevant

## Persistence / safety checklist

- [ ] Restore determinism is unchanged or explicitly tested
- [ ] Structural changes still pass through controlled mutation boundaries
- [ ] Auto-approval defaults remain conservative
- [ ] No arbitrary shell command path was added to the dashboard
- [ ] No new broad type suppressions were introduced

## Documentation

- [ ] README updated if user-visible behavior changed
- [ ] User Guide updated if operator workflow changed
- [ ] Developer Guide / architecture docs updated if contracts changed
