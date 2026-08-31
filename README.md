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
[![Tests](https://img.shields.io/badge/tests-379%20passing-brightgreen.svg)](https://github.com/Thomas-Heisig/Brain-5D/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Brain‑5D** is an experimental **spiking‑neural simulation platform** operating in a sparse 5D coordinate space.  
It combines spiking dynamics, spike‑timing‑dependent plasticity (STDP), homeostatic regulation, structural self‑organization, deterministic persistence, and an operator‑facing dashboard.

> **Research status**  
> Brain‑5D is an engineering and research project. The current implementation does **not** claim AGI, consciousness, sentience or biological equivalence.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🧬 Spiking Core** | Izhikevich regular‑spiking neurons in a sparse 5D coordinate space |
| **📐 STDP Learning** | Spike‑timing‑dependent plasticity with signed eligibility traces |
| **⚖️ Homeostasis** | Target firing‑rate regulation, adaptive thresholds, energy homeostasis |
| **🔄 Structural Plasticity** | Controlled neuron/synapse creation, pruning, and persistent undo |
| **🧠 Self‑Organization** | Policy‑driven structural proposals with safety validation |
| **💾 Deterministic Persistence** | `.b5d` snapshots, state delta journal, structural journal, runtime checkpoints |
| **📊 Operator Dashboard** | Real‑time visualization, heatmaps, structural approval, live projection |
| **🔬 Scientific Evidence** | Built‑in evidence framework (B5D‑SEF) for reproducible experiments |

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
├── research/                 # Scientific evidence framework
├── artifacts/                # Simulation snapshots and journals
└── scripts/                  # Utility and verification scripts
```

---

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [docs/ROADMAP.md](docs/ROADMAP.md) | Development roadmap and milestones |
| [docs/changelog.md](docs/changelog.md) | Detailed changelog |
| [docs/todo.md](docs/todo.md) | Current TODO and gate status |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture documentation |
| [docs/B5D_FORMAT.md](docs/B5D_FORMAT.md) | `.b5d` snapshot format specification |
| [research/README.md](research/README.md) | Scientific evidence framework |

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

Current baseline: **379 passed, 0 failed** ✅

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
  version = {0.5.0-alpha.6},
  url = {https://huggingface.co/<your-org>/Brain-5D},
  license = {MIT}
}
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

**Current focus:** Alpha.5 closure (restore determinism experiments) → Alpha.6 (morphological self-regulation).

---

## 🔗 Links

- **GitHub:** [Thomas-Heisig/Brain-5D](https://github.com/Thomas-Heisig/Brain-5D)
- **Issues:** [GitHub Issues](https://github.com/Thomas-Heisig/Brain-5D/issues)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
