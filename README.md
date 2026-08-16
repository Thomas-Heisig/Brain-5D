# Brain 5D Core v0.4.0-alpha.1

Sparse 5D spiking-neural simulation with observable plasticity, optical state,
controlled structural self-organization, and experimental `.b5d` persistence.

## Current status

Brain-5D contains a deterministic sparse 5D spiking core plus optional layers
for learning, inspection/manipulation, structural adaptation, visualization,
and storage. The neural core remains the reference execution layer; newer
subsystems attach through public APIs and generic post-step hooks.

Implemented and tested before this storage overlay:

- 5D coordinate space and sparse neuron/synapse storage
- Izhikevich regular-spiking neurons with delayed spike events
- deterministic Golden Chain regression
- Observatory, telemetry and run artifacts
- nearest-neighbour STDP
- signed exponentially decaying eligibility traces
- reward-modulated three-factor plasticity
- activity, incoming-weight and energy heatmaps
- deterministic end-to-end learning experiment
- 128-byte optical neuron-state codec
- safe manipulator facade with transaction/rollback support
- optional pruning, sprouting, and neurogenesis engine

Added in v0.4.0-alpha.1:

- `.b5d` snapshot format V1
- fixed header and deterministic section layout
- 128-byte optical-only or 160-byte restart-capable neuron records
- fixed 40-byte synapse records
- memory-mapped snapshot reader
- O(log n) random neuron lookup
- explicit line-ending policy through `.gitattributes`
- frozen V1 robustness contract: strict little-endian sizes, bounded JSON metadata, structural corruption detection, sorted/unique IDs, referential topology validation, and resource-safe mmap access

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

The controlled experiment demonstrates:

`PRE spike -> POST spike -> eligibility -> reward -> weight change -> changed network response`

## Main PoC

```powershell
python -m src.main
python -m src.main --observe
python -m src.main --benchmark
```

Self-organization and storage remain disabled in the main PoC configuration by
default. The `.b5d` API is explicit in this alpha release; `src.main` does not
silently perform large snapshot writes.

## `.b5d` snapshot example

```python
from src.storage import B5DReader, B5DSnapshotWriter

writer = B5DSnapshotWriter(restart_capable=True)
writer.write(
    "artifacts/brain5d_snapshot.b5d",
    network,
    optical_states=manipulator.optical,
    metadata={"seed": 42},
)

with B5DReader("artifacts/brain5d_snapshot.b5d") as reader:
    print(reader.header)
    print(reader.get_neuron(1234))
```

See `docs/B5D_FORMAT.md` for the frozen V1 layout, invariants and corruption model.

Project progression toward a measurable, usable AI is tracked in `docs/ROADMAP_TO_USABLE_AI.md`. The roadmap defines explicit exit criteria and does not treat implementation presence as proof of intelligence.

## Quality checks

The project keeps Python 3.11 as the minimum runtime syntax target while the
current development/lint environment is Python 3.13.

```powershell
black --check src/storage/b5d.py tests/test_b5d_storage.py
mypy src/storage/b5d.py
pylint src/storage/b5d.py
```

Pylance/Pyright strict checking for the new storage boundary is configured in `pyrightconfig.json`. `src/storage/b5d.py` intentionally contains no `Any` annotations; network/core coupling is expressed through typed `Protocol` interfaces.

Storage-only verification:

```powershell
.\scripts\verify_b5d.ps1
```

## Version line

- `brain5d-core-v0.1.0` - verified observable reference core
- `brain5d-core-v0.2.0` - STDP integration and eligibility traces
- `brain5d-core-v0.3.0` - three-factor reward learning and heatmap observatory
- `brain5d-core-v0.3.1` - repository synchronization and end-to-end learning proof
- `v0.4.0-alpha.1` - `.b5d` snapshot/storage foundation; not yet a final tag

The alpha storage version should only be tagged after the full local regression,
Black, mypy, and Pylint checks pass on the repository working tree.
