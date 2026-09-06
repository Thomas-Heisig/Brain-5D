# 2026-09-06 — Neural Symbiosis merge and repository cleanup

## Scope

This record documents the repository cleanup performed after the Neural Symbiosis embodiment extension was merged into `main`.

## Merge state

- Pull request #19 (`Add embodied Neural Symbiosis network gateway layer`) was merged into `main`.
- Merge commit: `4f8f87cd302e333aa43ada74e8c91dcbc9653c81`.
- No open pull requests remained at the cleanup verification point.
- The only non-main branch visible after the merge was `feature/neural-symbiosis-embodiment`; it contained no work that was not already present in `main`.
- The available repository connector does not expose deletion of Git refs. The merged feature ref was therefore synchronized to the current `main` head rather than treated as an independent development source.

## CI verification

The full GitHub Continuous Integration run #583 on the Neural Symbiosis merge commit completed successfully.

Verified jobs included:

- Python 3.11 full and slow suites;
- Python 3.12 full and slow suites;
- Python 3.13 full and slow suites;
- Black;
- Ruff;
- Pylint;
- Pre-Commit;
- Mypy;
- Pyright;
- documentation checks;
- Scientific Integrity Gate;
- Bandit and pip-audit;
- wheel build and clean installation;
- Docker build and runtime verification;
- final `ci-status` aggregation.

The verified collection at this point was **773 tests**.

## Neural Symbiosis

The merged architecture adds an embodiment-only multi-network interface without redefining the canonical Brain-5D SNN core.

Implemented contracts include:

- open-set `NetworkAreaAdapter`;
- descriptors for common CNN, Transformer, recurrent, graph, associative-memory, reservoir, MLP, autoencoder, generative, peripheral-SNN, multimodal and neuro-symbolic families;
- virtual logic/knowledge/database/memory area support;
- camera, microphone, web/API, database, logic, memory, audio, display, printer and robotics pipeline templates;
- pure candidate gateway math for pair STDP, homeostatic scaling, sigmoid gating, reward-modulated gate updates and structural formation/pruning;
- read-only `Wesen` visualization of network families, endpoint reachability and disabled gateway state.

Scientific safeguards remain explicit:

- no implicit import/mutation of the canonical SNN core;
- gateway plasticity disabled by default;
- endpoint reachability is not evidence;
- pipeline registration is not evidence of learned use;
- gateway RNG belongs to a preregistered experiment runner;
- historical DATA/EVID is not rewritten.

## Documentation cleanup

Current-state documentation was refreshed to avoid mixing old snapshots with the present baseline:

- root `README.md`;
- `HF_README.md`;
- `docs/README.md`;
- `docs/02-architecture/ARCHITECTURE.md`;
- `docs/08-roadmap/ROADMAP.md`;
- `docs/08-roadmap/TODO.md`;
- `research/README.md`.

Historical dated changelogs, experiment reports and generated DATA retain their original test counts and statements because they describe earlier points in time.

## Experiment-data compacting rule

The repository now documents the distinction between raw scientific runs and bounded AI/UI projections:

```text
immutable/compressed raw DATA
        ↓ provenance + digest
bounded runs.json / analysis/ai_packet.json
        ↓
dashboard / small-local-AI review
```

Compact projections must never delete or replace the raw scientific record.

## Next work

The next Neural Symbiosis stage remains experiment-only:

1. runner-owned peripheral adapter instantiation;
2. exact model/version/artifact provenance;
3. gateway state persisted separately from core synapse state;
4. frozen/random/timing-shuffle/information-destroyed controls;
5. noisy-area and lesion-compensation experiments;
6. comparison of alternative homeostatic reward/error formulations;
7. independent multi-seed review before any claim of learned tool/area use.
