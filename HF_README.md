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

# Brain-5D

**Sparse 5D spiking-neural research framework with controlled plasticity, embodiment and scientific provenance.**

Brain-5D is an experimental framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network. The SNN remains the primary adaptive system; language models and research assistants are bounded interpretation/proposal components unless explicitly registered as experimental treatments.

> Brain-5D does not claim AGI, consciousness, sentience or biological equivalence. Passing implementation tests is not the same as scientific evidence.

## Current baseline

- version: `0.5.0a7`
- Python: 3.11–3.13
- 700 tests collected; current full suite: 698 passed, 2 intentionally opt-in large-storage tests skipped
- fast-suite coverage: 72%
- Scientific Integrity, typing, security, wheel and Docker CI gates: green on the verified `main` baseline

## Capabilities

- sparse 5D Izhikevich SNN with delayed events and deterministic RNG state;
- STDP, signed eligibility and delayed reward / three-factor learning;
- homeostasis and bounded interoception;
- structural proposals, explicit approval, mutation, journal, undo and recovery;
- `.b5d` snapshots, delta journals, checkpoints and deterministic restore/continue;
- typed embodiment, actuator authorization, audit trails and deterministic environments;
- real host telemetry/device discovery without fabricated fallback values;
- research registries, manifests, DATA/EVID separation and AI provenance;
- responsive seven-workspace dashboard: Overview, Network, Control, Research, Release, Settings and Embodiment.

## Quick start

```bash
git clone https://github.com/Thomas-Heisig/Brain-5D.git
cd Brain-5D
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m src.main --config configs/poc_config.yaml
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
.\start.ps1
```

The dashboard defaults to `http://127.0.0.1:8765`.

## Current research focus

The engineering foundation is broad enough that the next priority is **evidence closure rather than feature accumulation**:

1. productive learning with holdout and matched controls;
2. closed-loop embodiment versus replay/open-loop controls;
3. simulation-time versus wall-clock pacing calibration;
4. causal ablations of the 5D organization;
5. self-regulation/sensor-loss studies;
6. later memory/world-model and multimodal grounding;
7. AI-as-treatment comparisons with frozen provenance.

## Documentation

- [Project README](README.md)
- [Architecture](docs/02-architecture/ARCHITECTURE.md)
- [Dashboard](docs/03-dashboard/DASHBOARD.md)
- [Roadmap](docs/08-roadmap/ROADMAP.md)
- [TODO](docs/08-roadmap/TODO.md)
- [Research roadmap](docs/08-roadmap/RESEARCH_ROADMAP.md)
- [Research/evidence framework](research/README.md)

Versioned Alpha/Sprint/Release documents are historical traceability records and should not be used as the current project status unless linked by a canonical document.

## Scientific boundary

```text
implementation test != experiment data != accepted evidence != interpretation
```

Observed values remain distinct from inferred values. Missing telemetry remains unknown. Device availability is not authorization. AI output is not empirical measurement.

## License and citation

MIT License — see `LICENSE`.

```bibtex
@software{heisig2026brain5d,
  author  = {Thomas Heisig},
  title   = {Brain-5D: Sparse 5D Spiking-Neural Research Framework},
  year    = {2026},
  version = {0.5.0a7},
  url     = {https://github.com/Thomas-Heisig/Brain-5D},
  license = {MIT}
}
```

GitHub: https://github.com/Thomas-Heisig/Brain-5D
