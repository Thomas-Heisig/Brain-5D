# Brain 5D Core v0.3.1

Sparse 5D spiking-neural simulation with observable plasticity.

## Current status

Brain-5D contains a deterministic sparse 5D spiking core plus an optional learning
layer. The learning layer remains outside `src/core` and observes completed core
steps through a generic post-step hook.

Implemented and tested:

- 5D coordinate space and sparse neuron/synapse storage
- Izhikevich regular-spiking neurons with delayed spike events
- deterministic Golden Chain regression
- Observatory, telemetry and run artifacts
- nearest-neighbour STDP
- signed exponentially decaying eligibility traces
- reward-modulated three-factor plasticity
- activity, incoming-weight and energy heatmaps
- deterministic end-to-end learning experiment

The v0.3.1 experiment demonstrates the full chain:

`PRE spike -> POST spike -> eligibility -> reward -> weight change -> changed network response`

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Regression tests

```powershell
python -m pytest -v
python -m pytest tests/test_golden_chain.py -v
```

## Controlled learning experiment

```powershell
python -m src.experiments.learning_lab --config configs/learning_experiment.yaml
```

The checked-in experiment starts with subthreshold convergent synapses. Repeated
PRE/POST pairings create eligibility, positive reward strengthens the synapses, and
a fresh evaluation network must then produce a target spike from the trained
weights while the baseline network remains subthreshold.

## Main PoC

Headless:

```powershell
python -m src.main
```

Observatory:

```powershell
python -m src.main --observe
```

Benchmark:

```powershell
python -m src.main --benchmark
```

## Quality checks

The project keeps Python 3.11 as the minimum runtime syntax target, while the
current development/lint environment is Python 3.13.

```powershell
black --check src/learning src/experiments src/visualization/heatmap.py tests/test_learning_experiment.py tests/test_network_hooks.py
mypy src/learning src/experiments src/visualization/heatmap.py
pylint src/learning src/experiments src/visualization/heatmap.py
```

For a complete local verification on Windows:

```powershell
.\scripts\verify_v031.ps1
```

## Version line

- `brain5d-core-v0.1.0` - verified observable reference core
- `brain5d-core-v0.2.0` - STDP integration and eligibility traces
- `brain5d-core-v0.3.0` - three-factor reward learning and heatmap observatory
- `brain5d-core-v0.3.1` - repository synchronization and end-to-end learning proof

See `docs/CHANGELOG.md` and `docs/SPRINT_2D_FOUNDATION.md`.
