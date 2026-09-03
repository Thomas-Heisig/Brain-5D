---
license: mit
language:
  - en
library_name: brain5d-core
tags:
  - spiking-neural-networks
  - STDP
  - structural-plasticity
  - homeostasis
  - neuromorphic
  - simulation
  - 5D
  - neuroscience
  - brain-inspired
pipeline_tag: reinforcement-learning
---

# 🧠 Brain‑5D

**Sparse 5D Spiking‑Neural Simulation with Observable Plasticity**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-618%20passing-brightgreen.svg)](https://github.com/Thomas-Heisig/Brain-5D/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Brain‑5D** is an experimental **spiking‑neural simulation platform** operating in a sparse 5D coordinate space.
It combines spiking dynamics, spike‑timing‑dependent plasticity (STDP), homeostatic regulation, structural self‑organization, deterministic persistence, and an operator‑facing dashboard.

> **Research status**
> Brain‑5D is an engineering and research project. The current implementation does **not** claim AGI, consciousness, sentience or biological equivalence.

> **Current status (2026-09-03)**
> The repository is on synchronized `main` (`0.5.0a7`). Deterministic task
> outcome verification now derives task success and reward from observed
> environment state. The local full test
> suite reports **640 passed, 3 known legacy dashboard failures, 5 skipped**.
> Scientific AI contracts,
> provenance, read-only boundaries, replay/shadow controls, deterministic
> statistics and storage-scope enforcement are implemented and tested.
> Scientific claims are still pending: productive STDP, independent
> embodiment evidence, long-horizon performance measurements and human-reviewed
> AI research reports remain open research work.

The controlled embodiment layer supports deterministic multi-actuator routing;
each actuator retains independent capabilities, safety limits, receipts and
audit records.

The science suite also provides a deterministic regulation DATA runner for
nominal, chronic-pressure and unknown telemetry conditions; EVID remains
separate from engineering execution.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🧬 Spiking Core** | Izhikevich regular‑spiking neurons in a sparse 5D coordinate space |
| **📐 STDP Learning** | Spike‑timing‑dependent plasticity with signed eligibility traces |
| **⚖️ Homeostasis** | Target firing‑rate regulation, adaptive thresholds, energy homeostasis and bounded regulatory state |
| **🔄 Structural Plasticity** | Controlled neuron/synapse creation, pruning, and persistent undo |
| **🧠 Self‑Organization** | Policy‑driven structural proposals with safety validation |
| **✅ Outcome Verification** | Deterministic task success and reward from observed environment state |
| **💾 Deterministic Persistence** | `.b5d` snapshots, state delta journal, structural journal, runtime checkpoints |
| **📊 Operator Dashboard** | Real‑time visualization, heatmaps, structural approval, live projection |
| **🔬 Scientific Evidence** | Built‑in evidence framework (B5D‑SEF) for reproducible experiments |
| **📡 Impulse Response** | Controlled single-spike probes with observable latency, propagation and recurrence metrics |
| **⏱️ Temporal Comparison** | Bounded FAST/MEDIUM/SLOW state references without rewinding runtime state |
| **🧭 Functional Regulation** | Bounded safety, activation, valence and uncertainty values derived from observable state |
| **🧱 Morphology Ledger** | Deterministic neuron/synapse ages with separate growth and pruning budgets |
| **〽️ Structural Hysteresis** | Per-mechanism release thresholds prevent proposal oscillation under changing pressure |
| **🧾 Action Receipts** | Typed execution receipts separate command acceptance from observed environment effects |
| **🔗 Durable Action Journal** | Hash-linked JSONL audit records reopen with integrity verification |

---

## 🏗️ Architecture Overview

```
                    ┌─────────────────────┐
                    │   Operator Dashboard │
                    │   (127.0.0.1:8765)   │
                    └──────────┬──────────┘
                               │ HTTP / Bridge
                    ┌──────────▼──────────┐
                    │   RuntimeController │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  NeuralNetwork  │  │ HomeostasisEng. │  │ LearningEngine  │
│  (5D sparse)    │  │ (rate/threshold)│  │ (STDP/eligibility)│
└────────┬────────┘  └─────────────────┘  └─────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│              Persistence Layer                            │
│  .b5d Snapshot + Delta Journal + Structural Journal + CP │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://huggingface.co/<your-org>/Brain-5D
cd Brain-5D
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\Activate.ps1  # Windows
pip install -e ".[dev]"
```

### Run the Simulation

```bash
# With dashboard (default)
python -m src.main --config configs/poc_config.yaml

# Headless mode
python -m src.main --config configs/poc_structural_live.yaml --no-dashboard --ticks 500
```

### Open the Dashboard

Navigate to [http://127.0.0.1:8765](http://127.0.0.1:8765)

### Intranet and Internet Access

Trusted LAN access is available with
`.\start.ps1 -DashboardHost 0.0.0.0`. Internet access must keep Brain-5D on
loopback and use the supplied Caddy TLS/authentication proxy; never forward
port `8765` directly. See
[Dashboard network access](docs/03-dashboard/DASHBOARD.md#netzwerkzugriff).

---

## 📦 Repository Structure

```
Brain-5D/
├── src/
│   ├── core/                 # Neural network and neuron/synapse core
│   ├── controller/           # Operator/runtime controller
│   ├── learning/             # STDP, eligibility and reward learning
│   ├── homeostasis/          # Firing-rate / threshold / energy regulation
│   ├── self_organization/    # Policy, coordinator, approval, plasticity
│   ├── manipulation/         # Controlled mutation boundary
│   ├── storage/              # Snapshots, journals, checkpoint, recovery
│   ├── dashboard/            # Local operator console and API
│   └── ...
├── tests/                    # Test suite (379+ tests)
├── configs/                  # YAML configuration files
├── docs/                     # Documentation and roadmap
├── research/                 # Registry, protocols, schemas and AI research artifacts
├── artifacts/                # Simulation snapshots and journals
└── scripts/                  # Utility and verification scripts
```

---

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [docs/08-roadmap/ROADMAP.md](docs/08-roadmap/ROADMAP.md) | Development roadmap and milestones |
| [docs/07-changelog/CHANGELOG.md](docs/07-changelog/CHANGELOG.md) | Detailed changelog |
| [docs/08-roadmap/TODO.md](docs/08-roadmap/TODO.md) | Current TODO and gate status |
| [docs/02-architecture/](docs/02-architecture/) | Architecture documentation |
| [docs/B5D_FORMAT.md](docs/B5D_FORMAT.md) | `.b5d` snapshot format specification |
| [research/README.md](research/README.md) | Scientific evidence framework and evidence boundary |

---

## 🧪 Testing

```bash
# Fast regression suite
pytest -v -m "not slow"

# Full suite
pytest -v

# With coverage
pytest --cov=src --cov-report=term-missing
```

Current local baseline: **618 passed, 5 skipped, 0 failed** ✅

The skipped tests are platform- or opt-in large-storage checks. Run the full
suite with `python -m pytest -q`; scientific experiments additionally require
a clean tree, a registered protocol and DATA/EVID provenance.

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

Copyright © 2025-2026 Thomas Heisig and contributors.

---

## 📖 Citation

```bibtex
@software{heisig2026brain5d,
  author = {Thomas Heisig},
  title = {Brain-5D: Sparse 5D Spiking-Neural Simulation with Observable Plasticity},
  year = {2026},
  version = {0.5.0-alpha.7},
  url = {https://huggingface.co/<your-org>/Brain-5D},
  license = {MIT}
}
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

**Current focus:** Alpha.7.1 — persistent operator storage, dirty-tracking
equivalence and runtime performance measurement.

---

## 🔗 Links

- **GitHub:** [Thomas-Heisig/Brain-5D](https://github.com/Thomas-Heisig/Brain-5D)
- **Issues:** [GitHub Issues](https://github.com/Thomas-Heisig/Brain-5D/issues)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
