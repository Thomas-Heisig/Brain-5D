# Brain-5D User Guide

## Purpose

This guide covers installation, simulation startup, dashboard startup, basic
operator controls, persistence and troubleshooting for Brain-5D
`v0.5.0-alpha.5`.

Brain-5D is an experimental research and engineering platform. It does not
claim AGI, consciousness, sentience or biological equivalence.

## 1. Installation

```powershell
git clone https://github.com/Thomas-Heisig/Brain-5D.git
cd Brain-5D

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For an existing checkout:

```powershell
git pull --rebase origin main
python -m pip install -e ".[dev]"
```

## 2. Run the simulation

Default:

```powershell
.\.venv\Scripts\python.exe -m src.main
```

With a configuration:

```powershell
.\.venv\Scripts\python.exe -m src.main --config configs/poc_config.yaml
```

Optional modes supported by the current CLI include:

```powershell
.\.venv\Scripts\python.exe -m src.main --observe
.\.venv\Scripts\python.exe -m src.main --benchmark
```

## 3. Start the dashboard

Against an existing snapshot:

```powershell
.\.venv\Scripts\python.exe -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

Then open:

```text
http://127.0.0.1:8765
```

Alternative launcher:

```powershell
.\.venv\Scripts\python.exe scripts\brain5d_launcher.py --dashboard
```

If PowerShell scripts are permitted:

```powershell
.\start.ps1 -OpenBrowser
```

If execution policy blocks `.ps1`, prefer the Python launcher or `.cmd`
wrappers. Do not weaken machine-wide PowerShell policy solely to start Brain-5D.

## 4. Dashboard functions

Alpha.5 operator features include:

- status and current tick;
- neuron/synapse counts;
- spike and storage telemetry;
- activity/weight/energy heatmaps;
- homeostasis metrics and heatmaps;
- structural proposals;
- approve/reject;
- structural history;
- persistent inverse undo;
- structural heatmaps;
- exact manual ticks;
- bounded loops;
- pause/resume/stop;
- snapshot requests;
- documentation view.

Mutating operations are routed through typed operator/controller/bridge
boundaries.

## 5. Manual execution

The current operator path supports bounded actions such as:

- one tick;
- 10 ticks;
- 100 ticks;
- 1000 ticks;
- validated custom tick counts;
- run/pause/resume/stop.

Concurrent uncontrolled worker loops should not be created.

## 6. Structural self-organization

Current controlled flow:

```text
HomeostasisSignal
  -> SelfOrganizationPolicy
  -> StructuralProposal
  -> Coordinator
  -> Manual/Auto Approval
  -> StructuralPlasticityEngine
  -> Manipulator
  -> NeuralNetwork
  -> StructuralJournal
```

Safe defaults:

- self-organization disabled unless configured;
- dry-run enabled by default;
- auto-approval off by default;
- neuron pruning off by default.

## 7. Persistence

Alpha.5 persistence consists of:

```text
.b5d Snapshot
+ State Delta Journal
+ Structural Journal
+ Runtime Checkpoint
```

Restore order:

```text
1. Snapshot
2. State delta replay
3. Structural replay
4. Runtime checkpoint
5. Consistency validation
6. Continue
```

Undo does not delete journal history. It appends an inverse structural record.

## 8. Configuration

Primary configuration files live under `configs/`.

Relevant sections include:

- dimensions / topology;
- simulation;
- neuron parameters;
- learning;
- reward;
- homeostasis;
- self-organization;
- controller/runtime;
- storage.

Do not assume a configuration key exists unless it is part of the typed
configuration contract for the current version.

## 9. Verification

Recommended fast gate:

```powershell
.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
git diff --check
```

Focused release verifier:

```powershell
.\.venv\Scripts\python.exe scripts\verify_v050a5.py
```

Slow tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v -m slow
```

## 10. Troubleshooting

### PowerShell says `start.ps1` is not digitally signed

Use:

```powershell
.\.venv\Scripts\python.exe scripts\brain5d_launcher.py --dashboard
```

or the `.cmd` launcher provided by the repository.

### Dashboard has no heatmap source

Start it with a valid `.b5d` snapshot path and verify that the file exists.

### Test failures after updating

Reinstall editable dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Then run focused tests before the full suite.

### Security-sensitive issue

Do not publish exploit details in a public bug report. Read
[../../SECURITY.md](../../SECURITY.md).
