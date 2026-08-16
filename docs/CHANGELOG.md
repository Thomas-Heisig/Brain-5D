# Changelog

## 0.3.1 - Learning proof and repository synchronization - 2026-08-16

### Added
- Deterministic end-to-end learning experiment in `src/experiments/learning_lab.py`.
- Checked-in experiment configuration `configs/learning_experiment.yaml`.
- System acceptance tests proving reward-driven weights change network behaviour.
- Regression tests for the generic network post-step hook.
- Windows verification script `scripts/verify_v031.ps1`.

### Fixed
- Restored the generic post-step hook required by `LearningEngine.attach()` in the
  published core network file.
- Synchronized README documentation with the actual v0.3 learning feature set.
- Aligned mypy and Pylint development targets with the Python 3.13 verification
  environment while retaining Python 3.11-compatible source syntax.

### Scope
- No new plasticity rule is introduced.
- No homeostasis or intrinsic motivation is introduced yet.

## 0.3.0 - Sprint 2C - 2026-08-16

### Added
- RewardSignal with configurable delay.
- Signed three-factor plasticity (`eta * reward * eligibility`).
- Positive and negative reward handling.
- Optional trace reset after reward.
- Activity, incoming-weight and energy heatmap projections.
- Heatmap Observatory panel.
- Reward and heatmap unit tests.
- Black, Pylint and strict-mypy development configuration.

### Changed
- Package version raised to 0.3.0.
- Learning statistics distinguish STDP and reward weight updates.
- `main.py` supports optional `output_spike` reward generation while keeping
  `external` as the default reward source.

### Compatibility
- Default reward learning remains disabled in `configs/poc_config.yaml`.
- Sprint 1C core spike dynamics are not changed by Sprint 2C.
