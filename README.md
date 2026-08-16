# 🧠 Brain-5D

**Persistent Structural Plasticity — v0.5.0-alpha.5**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![mypy](https://img.shields.io/badge/mypy-passing-green.svg)](https://github.com/python/mypy)
[![Pyright](https://img.shields.io/badge/pyright-strict-21BA45.svg)](https://github.com/microsoft/pyright)
[![Tests](https://img.shields.io/badge/tests-148%20passing%2C%202%20skipped-brightgreen.svg)](https://github.com/Thomas-Heisig/Brain-5D)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Brain-5D is an experimental sparse **5D spiking-neural platform** for persistent, observable and controlled neural simulation. The current development line combines spiking dynamics, plasticity, homeostasis, structural self-organization, deterministic persistence and an operator-facing dashboard.

---

## 📋 Table of Contents

- [What is Brain-5D?](#what-is-brain-5d)
- [Key Features](#key-features)
- [Current Status](#current-status)
- [Quick Start](#quick-start)
- [Starting Brain-5D](#starting-brain-5d)
- [Testing](#testing)
- [Static Quality Checks](#static-quality-checks)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Safety & Scope](#safety--scope)
- [Contributing](#contributing)
- [License](#license)

---

## 🧬 What is Brain-5D?

Brain-5D is a research platform for exploring **persistent spiking neural networks** in a **5D spatial coordinate space**. It provides:

- A **sparse neural core** with 40‑bit packed neuron identifiers
- Biologically inspired **spiking dynamics** (Izhikevich neurons)
- **STDP**, **eligibility traces** and **reward-modulated three-factor learning**
- **Homeostatic regulation** of firing rate, threshold and energy
- **Controlled structural plasticity** with operator approval
- **Crash-safe persistence** via `.b5d` snapshots + journals
- An **operator dashboard** for observation and control

> **Research status:** Brain-5D is an engineering and research project. The current implementation does **not** claim AGI, consciousness, sentience or biological equivalence.

---

## ✨ Key Features

| Area | Features |
|------|----------|
| **Neural Core** | Sparse 5D coordinate space, Izhikevich neurons, delayed events, deterministic RNG, input/output cell boundaries |
| **Learning** | STDP, eligibility traces, reward-modulated three-factor learning, delayed rewards, deterministic experiments |
| **Homeostasis** | Target firing-rate regulation, threshold adaptation, energy homeostasis, heatmaps |
| **Self-Organization** | Structural proposals (neurogenesis, pruning, synaptogenesis), coordinator, manual/auto approval, cooldown limits |
| **Structural Plasticity** | Controlled mutation, undo/redo, persistent change records, structural journal, recovery |
| **Persistence** | `.b5d` snapshot, state delta journal, structural journal, runtime checkpoint, crash-safe replay |
| **Dashboard** | Status, spike activity, heatmaps, structural approvals, undo, tick control, snapshot requests |

---

## 📊 Current Status

| Aspect | Status |
|--------|--------|
| **Version** | v0.5.0-alpha.5 |
| **Stage** | Persistent Structural Plasticity |
| **Tests** | 148 passed, 2 skipped |
| **Alpha.5 Tests** | 20 focused tests passed |
| **mypy** | 61 source files clean |
| **Pyright (strict)** | Clean |
| **Black** | Clean |
| **git diff --check** | Clean |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Thomas-Heisig/Brain-5D.git
cd Brain-5D
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
```

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Install Brain-5D and development tools

```bash
pip install -e ".[dev]"
```

---

## ▶️ Starting Brain-5D

### Option A — Python Launcher (recommended on Windows)

```bash
python scripts/brain5d_launcher.py start --open-browser
```

### Option B — PowerShell Launcher

```powershell
.\start.ps1 -OpenBrowser
```

If PowerShell blocks the script due to execution policy, use Option A or C.

### Option C — CMD Launcher

```cmd
start.cmd
```

**Stop:**
```cmd
stop.cmd
```

### Manual Component Start

**Simulation only:**
```bash
python -m src.main
```

**With observatory:**
```bash
python -m src.main --observe
```

**Dashboard only:**
```bash
python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

Then open: [http://127.0.0.1:8765](http://127.0.0.1:8765)

---

## 🧪 Testing

### Fast regression suite (recommended before commit)

```bash
python -m pytest -v -m "not slow"
```

### Full test suite

```bash
python -m pytest -v
```

### Alpha.5 verifier

```bash
python scripts/verify_v050a5.py
```

### Storage verification

```bash
python scripts/verify_b5d.py
```

**Large storage smoke tests (opt‑in):**

```powershell
# Windows
$env:BRAIN5D_RUN_LARGE_STORAGE_TEST="1"
python scripts/verify_b5d.py
```

```bash
# Linux/macOS
export BRAIN5D_RUN_LARGE_STORAGE_TEST=1
python scripts/verify_b5d.py
```

---

## 🔍 Static Quality Checks

### Formatting (Black)

```bash
python -m black --check src tests scripts
```

To format:
```bash
python -m black src tests scripts
```

### Type Checking (mypy)

```bash
python -m mypy src
```

### Type Checking (Pyright)

```bash
python -m pyright src scripts tests
```

### Linting (Pylint)

```bash
python -m pylint src
```

### Git whitespace check

```bash
git diff --check
```

### Recommended pre-push sequence

```bash
python -m pytest -v -m "not slow"
python -m mypy src
python -m black --check src tests scripts
python -m pyright src scripts tests
python -m pylint src
git diff --check
python scripts/verify_v050a5.py
```

---

## 📁 Project Structure

```
src/
├── core/                 # Neural network core (Neuron, Synapse, Network, SpatialIndex)
├── controller/           # Operator/runtime controller
├── runtime/              # Interactive runtime control
├── learning/             # STDP, eligibility, reward learning
├── homeostasis/          # Firing-rate, threshold, energy regulation
├── self_organization/    # Policy, coordinator, approval, plasticity, undo
├── manipulation/         # Controlled mutation boundary
├── storage/              # Snapshot, journals, checkpoint, recovery
├── visualization/        # Observatory and heatmaps
├── dashboard/            # Local operator console and API
├── embodiment/           # Perception/action interface foundation (placeholder)
├── telemetry/            # Runtime metrics
└── typing_contracts.py   # Shared type contracts

tests/
scripts/
configs/
docs/
artifacts/
```

---

## 🗺️ Roadmap

### v0.4 — Persistence Foundation ✓
- `.b5d` Snapshot • Delta Journal • Crash Recovery • Runtime Checkpoint • Async Storage • Compaction • Dashboard foundation

### v0.5 — Self-Regulation & Structural Plasticity
- **alpha.1** Homeostasis Engine ✓
- **alpha.2** Homeostasis Heatmaps + Type Safety ✓
- **alpha.3** Operator Console + Structural Proposals ✓
- **alpha.4** Controlled Structural Plasticity ✓
- **alpha.5** Structural Journal + Persistent Undo + Recovery ✓
- **alpha.6** Morphological Self-Regulation

### v0.6 — Scaling & Performance
- Dirty tracking • Chunked storage • Regional processing • Larger deterministic benchmarks

### v0.7 — Learning Environments
- Episodes • Train/eval separation • Delayed reward tasks • Continual-learning retention

### v0.8 — Embodiment & Multimodal Adapters
### v0.9 — Memory, Context & World Model
### v0.10 — Cognitive Evaluation
### v0.11 — Bounded HMI, Permissions & Autonomy
### v0.12 — Release Candidate
### v1.0 — Usable Brain-5D system by measured engineering criteria

The detailed v0.5 roadmap is maintained in [docs/Roadmap/](./docs/Roadmap/).

---

## 🛡️ Safety & Scope

Brain-5D v0.5.0-alpha.5 **deliberately does not implement**:

- Unrestricted autonomous self-organization
- Autonomous deletion of large network regions
- Unrestricted resource allocation
- Autonomous source-code modification
- Self-modifying Python code
- Unrestricted shell/browser execution
- Production LLM integration
- Uncontrolled internet access
- Multi-node distributed simulation
- Chunked-storage rewrite

These belong to later milestones with separate safety, resource and evaluation contracts.

---

## 🤝 Contributing

Brain-5D is currently developed as an experimental research/engineering project. Before substantial external contribution or redistribution, please check the repository for the current license and contribution policy.

---

## 📄 License

Please see the `LICENSE` file in the repository root for the current license terms.

---

**🧠 Brain-5D — persistent structural plasticity for computational neuroscience research.**

---