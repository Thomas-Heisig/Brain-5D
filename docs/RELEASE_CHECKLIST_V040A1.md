# Release Checklist – Brain-5D v0.4.0-alpha.1

Do not mark the snapshot sprint complete until these checks pass on the real
`F:\Brain-5D` working tree.

## Repository state

```powershell
git fetch origin
git status --short
git diff --name-status origin/main
```

Before tagging, the intended changes should be reviewed and the working tree
should be clean after commit.

## Automated verification

```powershell
.\scripts\verify_b5d.ps1
```

This executes:

1. editable dev install;
2. storage robustness tests;
3. complete repository regression;
4. Black check;
5. strict mypy check for `b5d.py`;
6. Pylint for `b5d.py`;
7. frozen format invariant check;
8. opt-in 50k-neuron mmap/storage smoke test.

## Pylance

Open the repository in VS Code with Pylance enabled. `pyrightconfig.json`
applies strict checking to `src/storage/b5d.py`. The new storage boundary must
not introduce explicit `Any` annotations or unresolved unknown types.

## Runtime sanity

```powershell
python -m src.main
python -m src.main --benchmark
```

Storage remains explicit in alpha.1, so the normal PoC must not start writing
large `.b5d` files implicitly.

## Format freeze

Verify that:

- header = 128 bytes;
- optical neuron = 128 bytes;
- restart neuron = 160 bytes;
- synapse = 40 bytes;
- little-endian is unchanged;
- metadata limit = 65,536 bytes;
- V1 flag semantics are unchanged.

Any incompatible layout change after this point requires snapshot format V2.

## Suggested release commit/tag

After all checks pass:

```powershell
git add -A
git commit -m "storage: freeze robust .b5d snapshot format v1"
git tag -a brain5d-core-v0.4.0-alpha.1 -m "Brain-5D .b5d Snapshot V1 robustness freeze"
git push origin main
git push origin brain5d-core-v0.4.0-alpha.1
```
