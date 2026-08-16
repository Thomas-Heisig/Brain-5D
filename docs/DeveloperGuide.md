# Brain-5D Developer Guide

## 1. Architecture

Brain-5D is organized around explicit boundaries:

1. `src/core/` — neural network, neurons, synapses, spatial indexing.
2. `src/learning/` — STDP, eligibility traces, reward learning.
3. `src/homeostasis/` — rate, threshold and energy regulation.
4. `src/self_organization/` — structural policy, proposals, coordination,
   approval and undo.
5. `src/manipulation/` — controlled network mutation boundary.
6. `src/storage/` — `.b5d`, delta journal, structural journal, recovery,
   checkpoints.
7. `src/dashboard/` — typed HTTP/operator-facing surface.
8. `src/controller/` and `src/runtime/` — interactive execution and safe runtime
   control.
9. `src/visualization/` — observability and structural/homeostasis projections.
10. `src/embodiment/` — typed interfaces for later sensor/actuator integration.

## 2. Alpha.5 structural path

```text
HomeostasisEngine
  -> HomeostasisSignal
  -> SelfOrganizationPolicy
  -> StructuralProposal
  -> SelfOrganizationCoordinator
  -> ApprovalDecision
  -> StructuralPlasticityEngine
  -> Manipulator
  -> NeuralNetwork
  -> StructuralChangeRecord
  -> StructuralJournal
```

The coordinator does not mutate the network directly.

The dashboard does not reach into private network or engine attributes.

## 3. Persistence contract

The active persistence layers are:

```text
Snapshot + State Delta Journal + Structural Journal + Runtime Checkpoint
```

Restore order is deliberately defined:

```text
snapshot -> state deltas -> structural replay -> runtime checkpoint -> validate
```

Do not reorder these stages without updating deterministic restore tests.

## 4. Type safety

New code must avoid the Pylance/Pyright error classes that were previously
observed in the project.

Rules:

- no bare `dict`, `list`, `set`, `tuple` containers;
- avoid `Any` as a repair mechanism;
- parse external JSON/YAML to `object`, then validate and narrow;
- do not expand `dict[str, object]` into strictly typed subprocess kwargs;
- subprocess commands should be explicit `list[str]`;
- keep config TypedDicts complete;
- do not reference undeclared TypedDict keys;
- avoid dynamic runtime attributes;
- use `assert_never` for exhaustive enums where appropriate;
- keep Protocol properties read-only when mutation is not required;
- no broad `type: ignore` / `pyright: ignore` for new code.

## 5. Testing strategy

- isolated unit tests for component behavior;
- integration tests for subsystem boundaries;
- restore/continue tests for persistence;
- opt-in slow tests for long-running behavior;
- focused alpha release verifiers.

When fixing a regression, reproduce it with the smallest failing test before
changing production code.

## 6. Quality commands

```powershell
.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
.\.venv\Scripts\python.exe -m pylint --fail-under=9.0 src
git diff --check
```

Alpha.5 strict Pyright production scope:

```powershell
.\.venv\Scripts\python.exe -m pyright `
  src/storage/structural_journal.py `
  src/storage/structural_recovery.py `
  src/storage/core_restore.py `
  src/self_organization/approval.py `
  src/self_organization/undo.py `
  src/self_organization/plasticity.py `
  src/self_organization/coordinator.py `
  src/dashboard/structural_api.py `
  src/dashboard/operator_bridge.py `
  src/dashboard/server.py `
  src/runtime/control.py `
  src/controller/runtime.py `
  src/visualization/structural_heatmap.py
```

Repository-wide strict Pyright currently includes legacy findings outside this
scope. Do not hide them with global suppressions and do not add new debt.

## 7. Dashboard development

HTTP handlers must validate request fields explicitly.

Do not add endpoints that accept arbitrary command strings or shell fragments.

Preferred direction:

```text
DashboardRequestHandler
  -> OperatorBridge
  -> Coordinator / Runtime Controller
  -> Plasticity / Manipulator
  -> Core
```

## 8. Structural journal development

Structural records are immutable events.

Undo appends a new inverse record. Never delete a previous committed record as
an undo mechanism.

Corrupted committed records must fail loudly. Recoverable uncommitted tails
must not be treated as committed data.

## 9. Adding a feature

1. Define an observable problem and exit criterion.
2. Choose the correct architectural boundary.
3. Add typed models/contracts.
4. Add focused tests.
5. Implement the smallest working slice.
6. Run focused tests.
7. Run static gates.
8. Run the full fast suite.
9. Update README/UserGuide/DeveloperGuide as required.

## 10. Release work

Update at minimum:

- `pyproject.toml`;
- `CHANGELOG.md`;
- README status;
- roadmap/release notes;
- release verifier.

Do not tag a release while deterministic restore, Black, Mypy or required test
gates are failing.
