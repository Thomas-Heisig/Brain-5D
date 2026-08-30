# Brain-5D v0.3.1 update

This overlay is based on the public `main` state observed on 2026-08-16.

## Why this update exists

The published tree contains a repository mismatch: `LearningEngine.attach()` calls
`NeuralNetwork.add_post_step_hook()`, while the published `src/core/network.py`
does not currently expose that hook. The README also still describes v0.1.0 and
the committed mypy/Pylint targets are Python 3.11 although the verified local
development environment is Python 3.13.

v0.3.1 repairs those synchronization issues and adds the first deterministic
system-level proof that reward learning changes network behaviour.

## Files replaced

- `README.md`
- `pyproject.toml`
- `src/core/network.py`
- `src/learning/eligibility.py`
- `src/learning/learning_engine.py`
- `src/visualization/heatmap.py`
- `tests/test_reward.py`
- `docs/07-changelog/CHANGELOG.md`

## Files added

- `src/experiments/__init__.py`
- `src/experiments/learning_lab.py`
- `configs/learning_experiment.yaml`
- `tests/test_learning_experiment.py`
- `tests/test_network_hooks.py`
- `docs/09-sprints/SPRINT_2D_FOUNDATION.md`
- `scripts/verify_v031.ps1`

## Validation performed in the reconstruction workspace

- 57 reconstructed tests pass.
- 7 new acceptance/regression tests pass.
- The learning experiment deterministically changes mean convergent weight from
  0.05 to approximately 0.8288.
- Baseline target response remains subthreshold.
- Fresh network with trained weights spikes the target at tick 2.
- Python `compileall` succeeds.

The user's real repository previously reported 61 tests. After applying this overlay,
run `scripts/verify_v031.ps1`; the full real-repository result is authoritative.
