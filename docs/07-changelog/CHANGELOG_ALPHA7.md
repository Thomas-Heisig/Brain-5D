# Experience Engine v0 (2026-09-02)

- Added `ExperienceEngine` for controlled sensor -> SNN -> action ->
  environment-feedback -> reward orchestration.
- Added `SystemSensorAdapter` with an injected provider so live system data is
  opt-in and deterministic research traces remain possible.
- Added focused tests for reproducibility, reward provenance, and fail-closed
  action authorization, including runtime-hook single-tick behavior.
- Added opt-in `host_system_readings` for CPU, RAM, temperature when available,
  network state, process count and time; deterministic providers remain the
  research path.
- Preregistered `EXP-EMB-0001`; no evidence is claimed or generated.
- No camera, microphone, internet, or scientific learning claim is enabled by
  this change.

# Brain-5D v0.4.0-alpha.7

## Fixed

- deterministic restore now overlays exact double-precision neuron parameters;
- exact synapse weight/eligibility state is preserved in runtime checkpoint V3;
- JSON checkpoint parsing is strict-typing safe without `Any` or `type: ignore`;
- v1/v2 runtime checkpoint files remain readable.

## Added

- typed embodiment interfaces for sensors, actuators, environments and episodes;
- read-only embodiment metrics in the operator dashboard;
- safe Markdown documentation API and popup viewer;
- safe sibling `.b5d` snapshot selector;
- cross-platform PID-tracked launcher plus PowerShell/CMD wrappers;
- consolidated `scripts/verify_all.py` quality gate;
- updated roadmap aligned with `Analyse_Deepseek.md`, `Der_weg_zur_KI.md`, and
  `Research.md`.

## Compatibility

- `.b5d` V1 binary layout is unchanged;
- journal layout is unchanged;
- Runtime Checkpoint JSON advances to version 3;
- checkpoint versions 1 and 2 remain readable but cannot guarantee exact restore
  for values that were never stored losslessly.
