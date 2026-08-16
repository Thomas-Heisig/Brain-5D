# Contributing to Brain-5D

Thank you for your interest in Brain-5D.

Brain-5D is an experimental engineering and research platform. Contributions
should preserve the project's deterministic persistence contracts, typed
boundaries, safety limits and test coverage.

## Code of Conduct

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Reporting issues

Use the GitHub issue tracker:

https://github.com/Thomas-Heisig/Brain-5D/issues

For bugs, include:

- Brain-5D version or commit;
- operating system;
- Python version;
- exact command;
- minimal reproduction steps;
- relevant logs or traceback;
- whether the problem is deterministic.

Do not publish security-sensitive exploit details in a normal issue. See
[SECURITY.md](SECURITY.md).

## Feature requests

Use the feature-request template and explain:

- the engineering or research problem;
- the expected benefit;
- which existing architecture boundary it affects;
- how success can be measured;
- how it fits the roadmap.

## Pull requests

1. Fork the repository and branch from `main`.
2. Keep the change focused.
3. Preserve backwards-compatible APIs where practical.
4. Add or update tests.
5. Update documentation for public behavior.
6. Run the quality gates before submitting.
7. Complete the pull-request template.

## Type-safety rules

New code should follow the alpha.5 type-safety policy:

- parameterize collections;
- avoid `Any` as a shortcut;
- validate JSON/YAML before narrowing;
- do not add dynamic attributes to neuron objects;
- keep dashboard boundaries typed;
- avoid private network/engine access from HTTP handlers;
- use explicit subprocess argument lists;
- do not suppress broad Pyright/Pylance classes.

## Quality gates

From the repository root in the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
.\.venv\Scripts\python.exe -m pylint --fail-under=9.0 src
git diff --check
```

Alpha.5 introduced a strict Pyright-clean integration scope. Repository-wide
strict Pyright still contains historical findings, therefore pull requests must
at minimum keep all changed/new files free of new strict Pyright/Pylance errors.

When applicable:

```powershell
.\.venv\Scripts\python.exe scripts\verify_v050a5.py
.\.venv\Scripts\python.exe -m pytest -v -m slow
```

## Commit messages

Conventional Commit-style messages are recommended, for example:

- `feat: add structural journal`
- `fix: preserve deterministic restore ordering`
- `docs: update operator guide`
- `test: add structural recovery coverage`
- `chore: update tooling`

## Licensing

Unless explicitly stated otherwise, contributions are submitted under the
project's MIT license.
