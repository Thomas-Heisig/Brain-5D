# Brain-5D v0.4.0-alpha.7

Brain-5D is an experimental sparse 5D spiking-neural platform with observable
plasticity, persistent state, controlled self-organization, and a growing
perception/action architecture.

The project is an engineering and research system. Current versions do not
claim AGI, consciousness, sentience, or biological equivalence.

## Implemented foundation

- sparse 5D coordinate space with packed neuron IDs;
- Izhikevich regular-spiking neurons and delayed event propagation;
- STDP, signed eligibility traces, and reward-modulated three-factor learning;
- activity, weight, and energy observability;
- controlled structural self-organization;
- frozen `.b5d` Snapshot V1 with mmap/random access;
- append-only delta journal, CRC, crash recovery, and generation compaction;
- asynchronous storage queue and persistence telemetry;
- runtime checkpoint sidecar for deterministic continuation;
- local read-only operator dashboard;
- typed embodiment interfaces for future perception/action environments.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Quality gate

```powershell
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_dashboard.py
python scripts/verify_all.py
git diff --check
```

Large storage smoke tests are opt-in:

```powershell
$env:BRAIN5D_RUN_LARGE_STORAGE_TEST="1"
$env:BRAIN5D_RUN_LARGE_STORAGE_TESTS="1"
python scripts/verify_b5d.py
```

## Main simulation

```powershell
python -m src.main
python -m src.main --observe
python -m src.main --benchmark
```

## Operator dashboard

```powershell
python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

Open `http://127.0.0.1:8765`.

The dashboard is read-only. Alpha.7 adds safe documentation browsing, a sibling
snapshot selector, storage telemetry, homeostasis placeholders, and embodiment
status metrics.

## One-click launcher

```powershell
.\start.ps1 -OpenBrowser
.\stop.ps1
```

If PowerShell policy blocks local scripts:

```cmd
start.cmd
stop.cmd
```

The launcher records only the PIDs it starts and never terminates unrelated
Python processes.

## Persistence model

The frozen `.b5d` V1 snapshot remains compact and memory-mappable. Runtime
Checkpoint V3 layers exact Python floating-point values over it so a restored
network can continue bit-exactly at a checkpoint boundary.

See:

- `docs/B5D_FORMAT.md`
- `docs/DELTA_JOURNAL.md`
- `docs/CRASH_RECOVERY.md`
- `docs/DETERMINISTIC_RESTORE_V3.md`
- `docs/QUALITY_GATE_V040.md`

## Research and roadmap

`docs/Analyse_Deepseek.md`, `docs/Der_weg_zur_KI.md`, and `docs/Research.md` are
research/design inputs. Their proposals become implementation milestones only
when paired with an experiment and exit criterion.

The current roadmap is `docs/ROADMAP_TO_USABLE_AI.md`.

Near-term sequence:

1. finish the v0.4.0 persistence quality gate;
2. v0.5 self-regulation/homeostasis and dirty tracking;
3. v0.6 chunked scaling;
4. v0.7 deterministic learning environments;
5. v0.8 production embodiment and multimodal adapters;
6. v0.9 memory/context/world model;
7. v0.10 cognitive evaluation;
8. v0.11 bounded HMI/autonomy and permissions;
9. v0.12 release candidate;
10. v1.0 usable Brain-5D AI by measured engineering criteria.
