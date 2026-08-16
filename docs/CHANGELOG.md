# Changelog

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
