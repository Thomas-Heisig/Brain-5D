# Brain-5D additive update package

This package is designed for the current public `main` branch (Sprint 2C layout).

Copy the contained `src/` and `tests/` directories into the repository, merge the
`self_organization` YAML block into `configs/poc_config.yaml`, and integrate the
few lines from `INTEGRATION_SNIPPET.py` into `src/main.py` after LearningEngine
initialization.

The update intentionally does **not** replace `src/core/neuron.py`,
`src/core/synapse.py`, `src/core/network.py` or `src/learning/*`.

Suggested verification:

```bash
python -m pytest -v
python -m pytest tests/test_optical_codec.py tests/test_manipulator.py tests/test_self_organization.py -v
python -m src.main
```

Start with `self_organization.enabled: false`. Enable one structural mechanism at
a time after the existing golden-chain and deterministic tests remain green.
