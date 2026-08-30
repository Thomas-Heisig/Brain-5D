# Release Checklist – v0.4.0-alpha.4

## Functional

- [ ] full pytest suite passes
- [ ] 50k `.b5d` snapshot smoke test passes
- [ ] 100k journal smoke test passes
- [ ] async queue test passes with zero silent drops
- [ ] runtime checkpoint roundtrip passes
- [ ] generation compaction test passes
- [ ] restore-and-continue matches continuous reference run

## Quality

- [ ] `python scripts/prepare_alpha4.py`
- [ ] `black --check src tests`
- [ ] `mypy src`
- [ ] `pylint src` >= 9.0
- [ ] `git diff --check`
- [ ] Pyright/Pylance strict for `src/storage`

## Persistence invariants

- [ ] `.b5d` V1 byte layout unchanged
- [ ] journal V1 byte layout unchanged
- [ ] bounded queue has explicit overflow policy
- [ ] dropped batches are observable
- [ ] compaction publishes only through atomic manifest replacement
- [ ] old generation remains valid until new generation is fully prepared
- [ ] runtime checkpoint and recovered snapshot refer to the same checkpoint tick
