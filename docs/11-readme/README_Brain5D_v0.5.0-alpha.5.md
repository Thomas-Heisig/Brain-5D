Brain-5D v0.5.0-alpha.5

Brain-5D is an experimental sparse 5D spiking-neural platform for persistent,
observable and controlled neural simulation. The current development line combines
spiking dynamics, plasticity, homeostasis, structural self-organization, deterministic
persistence and an operator-facing dashboard.

Research status

Brain-5D is an engineering and research project. The current implementation does
not claim AGI, consciousness, sentience or biological equivalence.

Current status

Version: 0.5.0a5
Development stage: Persistent Structural Plasticity

The current alpha.5 integration provides the complete controlled path:

HomeostasisEngine
        │
        ▼
HomeostasisSignal
        │
        ▼
SelfOrganizationPolicy
        │
        ▼
StructuralProposal
        │
        ▼
SelfOrganizationCoordinator
        │
        ├── Reject
        │
        ├── Manual Approval
        │
        └── Auto-Approval Policy
                    │
                    ▼
        StructuralPlasticityEngine
                    │
                    ▼
               Manipulator
                    │
                    ▼
               NeuralNetwork
                    │
                    ▼
          StructuralChangeRecord
                    │
                    ▼
           StructuralJournal
              │           │
              ▼           ▼
            Undo       Recovery
              │           │
              └─────┬─────┘
                    ▼
              Operator Dashboard

Verified alpha.5 integration

Latest integration result:

148 passed

2 skipped

20 focused alpha.5 tests passed

mypy src: clean across 61 source files

alpha.5 Pyright strict scope: clean

Black: clean

git diff --check: clean

structural restore/continue integration: passing

Repository-wide strict Pyright and Pylint still contain historical/legacy findings
outside the alpha.5 implementation scope. These are tracked as quality work and are
not hidden with broad suppressions.

Implemented foundation

Neural core

sparse 5D coordinate space;

packed neuron identifiers;

Izhikevich regular-spiking neurons;

delayed event propagation;

deterministic random-state handling;

input/output cell boundaries;

topology inspection and diagnostics.

Learning

STDP;

signed eligibility traces;

reward-modulated three-factor learning;

delayed rewards;

deterministic learning experiments;

learning observability.

Homeostasis

target firing-rate regulation;

smoothed per-neuron rate state;

adaptive threshold regulation;

energy homeostasis;

HomeostasisSignal as a read-only boundary;

homeostasis heatmaps;

long-term stability test support.

Controlled self-organization

SelfOrganizationPolicy;

chronic structural proposals;

neurogenesis proposals;

pruning proposals;

synapse sprouting/pruning proposals;

coordinator with legacy alpha.3 and current alpha.4/alpha.5 APIs;

safety validation;

manual approval;

optional auto approval;

cooldown and per-tick mutation limits;

neuron pruning disabled by default.

Structural plasticity

controlled structural mutation through the Manipulator boundary;

neuron creation/removal support;

synapse creation/removal support;

persistent structural change records;

immutable inverse operations for undo;

structural activity history;

structural heatmaps.

Persistence contract

Brain-5D currently uses four coordinated persistence layers:

.b5d Snapshot
      +
State Delta Journal
      +
Structural Journal
      +
Runtime Checkpoint

Snapshot

The frozen .b5d V1 format provides:

compact binary records;

deterministic layout;

memory mapping;

random access;

sorted neuron/synapse records;

optical sidecar support.

State delta journal

The state journal provides:

append-only delta records;

CRC protection;

commit markers;

monotonic tick handling;

recovery from uncommitted tails;

crash-safe replay.

Structural journal

Alpha.5 adds a separate append-only structural journal for:

neuron additions;

neuron removals;

synapse additions;

synapse removals;

committed CRC-protected records;

monotonic sequence numbers;

deterministic replay;

persistent inverse undo.

Undo never deletes history. It appends an inverse structural record.

Runtime checkpoint

The runtime checkpoint preserves state that is not fully represented by the frozen
snapshot alone, including:

current tick;

total spikes;

total processed events;

RNG state;

pending currents;

queued events;

input/output cells;

exact floating-point continuation state.

Restore order

The current restore lifecycle is:

1. Load .b5d snapshot
2. Apply committed state-delta journal records
3. Replay committed structural journal records
4. Restore runtime checkpoint
5. Validate consistency
6. Continue simulation

The structural replay occurs before the runtime checkpoint is overlaid, preserving the
expected network topology for deterministic continuation.

Operator dashboard

Brain-5D includes a local operator dashboard that acts as the system control and
inspection surface.

Default address:

http://127.0.0.1:8765

Current dashboard functions include:

system status;

current tick;

neuron/synapse counts;

spike activity;

storage telemetry;

homeostasis metrics;

homeostasis heatmaps;

structural proposals;

structural approval/rejection;

structural journal history;

persistent undo;

structural heatmaps;

documentation browser;

snapshot requests;

exact manual tick execution;

bounded loop control;

pause/resume/stop;

embodiment status placeholders/interfaces.

The dashboard does not directly manipulate NeuralNetwork internals. Mutating
operations are routed through the operator/controller/bridge boundaries.

Quick start

1. Clone or update the repository

git clone https://github.com/Thomas-Heisig/Brain-5D.git
cd Brain-5D

For an existing checkout:

git pull --rebase origin main

2. Create the virtual environment

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

If the environment already exists, only activation is required.

3. Install Brain-5D and development tools

pip install -e ".[dev]"

The development environment includes the quality tooling required by the project,
including pytest, Black, mypy, Pylint and Pyright.

Starting Brain-5D

There are several supported start paths.

Option A — Python launcher

Recommended on Windows when PowerShell execution policy blocks .ps1 scripts:

python scripts\brain5d_launcher.py --dashboard

The launcher starts the required Brain-5D processes and records only the PIDs it owns.

Option B — PowerShell launcher

.\start.ps1 -OpenBrowser

If PowerShell reports that the script is not digitally signed, either use the Python
launcher above or the CMD wrapper below.

Do not weaken the machine-wide PowerShell execution policy only to start Brain-5D.

Option C — CMD launcher

start.cmd

To stop:

stop.cmd

Starting components manually

Main simulation

python -m src.main

With observatory:

python -m src.main --observe

Benchmark mode:

python -m src.main --benchmark

The src.main CLI intentionally has its own argument contract. Launcher-specific
arguments are not forwarded blindly to it.

Dashboard only

With a snapshot:

python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d

Then open:

http://127.0.0.1:8765

If no usable snapshot/network source is attached, some heatmap or runtime controls may
be unavailable by design.

Operator runtime controls

The alpha.5 controller supports bounded interactive execution.

Typical controls exposed through the operator layer are:

1 Tick
10 Ticks
100 Ticks
1000 Ticks
Custom Tick Count
Run
Pause
Resume
Stop
Snapshot

Controller requests are validated. Negative tick counts and values above the configured
manual limit are rejected.

Only one controlled runtime execution path should own the simulation loop at a time.

Structural approval

Structural changes are deliberately conservative.

Default safety posture:

self_organization:
  enabled: false
  dry_run: true
  auto_approval: false
  allow_neuron_pruning: false

This means:

self-organization does not mutate the network by default;

auto approval is OFF;

neuron pruning is OFF;

structural changes require an explicitly enabled and valid mutation path.

Auto approval is only permitted when all configured confidence, cooldown and safety
limits are satisfied.

Snapshot behavior

A dashboard snapshot request does not write arbitrary state immediately in the HTTP
request thread.

The runtime controller records the request and processes it at a safe runtime boundary.

The intended persistence ordering is:

Structural Journal flush/commit
        ↓
.b5d Snapshot
        ↓
Runtime Checkpoint
        ↓
Dashboard completion/status update

This prevents the operator interface from capturing a topology in the middle of a
controlled structural mutation batch.

Testing

Always run tests from the project virtual environment.

Fast regression suite

.\.venv\Scripts\python.exe -m pytest -v -m "not slow"

Current confirmed alpha.5 result:

148 passed
2 skipped

Full pytest run

.\.venv\Scripts\python.exe -m pytest -v

Alpha.5 verifier

.\.venv\Scripts\python.exe scripts\verify_v050a5.py

The verifier is intended to call tools through the active Python environment instead of
silently depending on globally installed executables.

Dashboard verification

.\.venv\Scripts\python.exe scripts\verify_dashboard.py

Storage verification

.\.venv\Scripts\python.exe scripts\verify_b5d.py

Large storage smoke tests are opt-in:

$env:BRAIN5D_RUN_LARGE_STORAGE_TEST="1"
$env:BRAIN5D_RUN_LARGE_STORAGE_TESTS="1"
.\.venv\Scripts\python.exe scripts\verify_b5d.py

Static quality checks

Black

.\.venv\Scripts\python.exe -m black --check src tests scripts

To format:

.\.venv\Scripts\python.exe -m black src tests scripts

Mypy

.\.venv\Scripts\python.exe -m mypy src

Current alpha.5 source result:

61 source files clean

Pyright

.\.venv\Scripts\python.exe -m pyright src scripts tests

The alpha.5 implementation scope is strict-Pyright clean. Repository-wide strict mode can
still expose legacy findings in older modules; these should be corrected incrementally
rather than hidden with broad suppressions.

Pylint

.\.venv\Scripts\python.exe -m pylint src

Historical complexity/documentation findings are still present in parts of the codebase.
They are tracked separately from alpha.5 functional correctness.

Git whitespace check

git diff --check

Recommended pre-push sequence

.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
.\.venv\Scripts\python.exe -m pyright src scripts tests
.\.venv\Scripts\python.exe -m pylint src
git diff --check
.\.venv\Scripts\python.exe scripts\verify_v050a5.py

Slow tests can be run separately:

.\.venv\Scripts\python.exe -m pytest -v -m slow

Type-safety policy

Brain-5D treats type safety as an architectural requirement.

Current rules include:

no unparameterized dict, list, tuple, deque, etc.;

JSON/YAML data enters the system as untrusted object and is narrowed explicitly;

no dynamic runtime attributes on neuron objects;

no broad Any escape hatches;

no broad type: ignore / pyright: ignore;

subprocess arguments use explicit typed argument lists;

configuration keys must exist in the declared typed contracts;

dashboard code must not reach into private network/engine attributes;

enum handling should be exhaustive;

mutable internals stay behind typed public interfaces.

Shared contracts should live in or reuse:

src/typing_contracts.py

Windows notes

PowerShell execution policy

If:

.\start.ps1

fails with a digital-signature/execution-policy error, use:

python scripts\brain5d_launcher.py --dashboard

or:

start.cmd

This avoids requiring a machine-wide policy change.

Virtual environment matters

Run quality tools through:

.\.venv\Scripts\python.exe

rather than relying on the Windows Store Python or global PATH.

This prevents false discrepancies between VS Code/Pylance, pytest, mypy and the actual
project environment.

Project structure

Important current areas:

src/
├── core/                 neural network and neuron/synapse core
├── controller/           operator/runtime controller
├── runtime/              interactive runtime control
├── learning/             STDP, eligibility and reward learning
├── homeostasis/          firing-rate / threshold / energy regulation
├── self_organization/    policy, coordinator, approval, plasticity and undo
├── manipulation/         controlled mutation boundary
├── storage/              snapshot, journals, checkpoint, recovery
├── visualization/        observatory and heatmaps
├── dashboard/            local operator console and API
├── embodiment/           perception/action interface foundation
├── telemetry/            runtime metrics
└── typing_contracts.py   shared type contracts

tests/
scripts/
configs/
docs/
artifacts/

Research and design documents

The project contains research/design material that informs future experiments. These
documents are inputs to engineering decisions, not automatically implemented features.

Examples include:

Analyse_Deepseek.md

Der_weg_zur_KI.md

Research.md

A research proposal becomes a project milestone only after it has a concrete experiment,
measurable acceptance criteria and a defined software boundary.

Roadmap

The active v0.5 development line is moving from controlled structural mutation toward
stable morphological self-regulation.

v0.4
Persistence foundation
    ├── .b5d Snapshot
    ├── Delta Journal
    ├── Crash Recovery
    ├── Runtime Checkpoint
    ├── Async Storage
    ├── Compaction
    └── Dashboard foundation

v0.5
Self-regulation and structural plasticity
    ├── alpha.1 Homeostasis Engine
    ├── alpha.2 Homeostasis Heatmaps + Type Safety
    ├── alpha.3 Operator Console + Structural Proposals
    ├── alpha.4 Controlled Structural Plasticity
    ├── alpha.5 Structural Journal + Persistent Undo + Recovery
    └── alpha.6 Morphological Self-Regulation

v0.6
Scaling and performance
    ├── dirty tracking
    ├── chunked storage
    ├── regional processing
    └── larger deterministic benchmarks

v0.7
Learning environments
    ├── episodes
    ├── train/eval separation
    ├── delayed reward tasks
    └── continual-learning retention

v0.8
Embodiment and multimodal adapters

v0.9
Memory, context and world model

v0.10
Cognitive evaluation

v0.11
Bounded HMI, permissions and autonomy

v0.12
Release candidate

v1.0
Usable Brain-5D system by measured engineering criteria

The detailed v0.5 roadmap is maintained in the organized roadmap documentation under
docs/Roadmap/.

Next evolution — v0.5.0-alpha.6

The recommended next stage is Morphological Self-Regulation.

Alpha.6 should not simply increase autonomous mutation. It should make structural
plasticity temporally and spatially stable.

Planned concepts:

chronic rather than single-tick structural signals;

regional 5D structural pressure;

neuron/synapse structural age;

minimum lifetime / grace periods;

growth budgets;

structural resource costs;

hysteresis between growth and pruning thresholds;

anti-oscillation rules;

region-local neurogenesis pressure;

region-local pruning pressure;

structural stability telemetry;

dashboard visualization of structural budgets and chronic pressure.

Conceptually:

alpha.3  observe structure
alpha.4  change structure under control
alpha.5  persist, audit, undo and recover structure
alpha.6  regulate structure over long time scales

Safety and scope

Brain-5D alpha.5 deliberately does not implement:

unrestricted autonomous self-organization;

autonomous deletion of large network regions;

unrestricted resource allocation;

autonomous source-code modification;

self-modifying Python code;

unrestricted shell/browser execution;

production LLM integration;

uncontrolled internet access;

multi-node distributed simulation;

chunked-storage rewrite.

These belong to later milestones and require separate safety, resource and evaluation
contracts.

License and contribution status

Brain-5D is currently developed as an experimental research/engineering project.

Before substantial external contribution or redistribution, check the repository for the
current license and contribution policy.

Current milestone summary

Brain-5D v0.5.0-alpha.5 can now:

simulate a sparse 5D spiking network;

learn through STDP and reward-modulated eligibility;

regulate rate, threshold and energy homeostasis;

generate structural proposals;

require bounded approval before structural mutation;

persist neural state;

persist structural changes separately;

recover committed topology changes;

undo structural mutations without deleting history;

expose structural activity in the operator dashboard;

execute bounded ticks interactively;

request consistent snapshots at safe runtime boundaries;

restore and continue with the structural topology reconstructed before runtime state.

The next engineering target is long-term morphological stability, not unrestricted
autonomy.
