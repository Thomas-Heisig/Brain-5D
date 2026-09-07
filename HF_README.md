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
  - embodiment
  - multimodal
  - neuromorphic
  - simulation
  - 5D
  - neuroscience
  - brain-inspired
pipeline_tag: reinforcement-learning
---

# Brain-5D

**Sparse 5D spiking-neural research framework with controlled plasticity, embodiment, peripheral multi-network integration and scientific provenance.**

Brain-5D is an experimental framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network. The SNN remains the primary adaptive system; language models, research assistants and peripheral neural networks are bounded interpretation/proposal/adapter components unless explicitly registered as experimental treatments.

> Brain-5D does not claim AGI, consciousness, sentience or biological equivalence. Passing implementation tests, reachable devices or available neural pipelines are not the same as scientific evidence.

## Current baseline — 2026-09-07

- version: `0.5.0a7`
- Python: 3.11–3.13
- latest verified Python suite: **825 passed, 5 skipped**
- latest verified browser suite: **5 passed** with Chromium
- Research Catalog / variable-projection-dimension integration is merged to `main`
- merge commit: `85e7209509b348bf7912dde01d3d9ebb078a2e61`
- latest fully completed pre-merge `main` CI baseline: run #598, success
- the post-merge CI run is authoritative for the merged baseline and must complete before that baseline is described as fully green
- GitHub `main` is canonical; this file is published as the Hugging Face repository README during mirror synchronization

## Capabilities

- sparse 5D Izhikevich SNN with delayed events and deterministic RNG state;
- STDP, signed eligibility and delayed reward / three-factor learning;
- homeostasis and bounded interoception;
- structural proposals, explicit approval, mutation, journal, undo and recovery;
- `.b5d` snapshots, delta journals, checkpoints and deterministic restore/continue;
- typed embodiment, actuator authorization, audit trails and deterministic environments;
- real host telemetry/device discovery without fabricated fallback values;
- **Neural Symbiosis**: open-set peripheral neural/virtual area contracts and read-only pipeline reachability;
- **MSBA**: modality-specific pathways, energy/resource accounting and external projection dimensionality from 1–32 dimensions;
- fragmentable canonical research-question/hypothesis registries with duplicate-ID rejection;
- searchable Research Catalog with operational/exploratory distinction;
- repository-wide read-only RQ/H reference audit;
- research registries, manifests, DATA/EVID separation and AI provenance;
- responsive dashboard centered on Overview, Control, Research, Settings, Wesen and Embodiment.

## Research Catalog and dimensions

Canonical `questions.yaml` / `hypotheses.yaml` can be extended through deterministic `questions.*.yaml` / `hypotheses.*.yaml` fragments. MSBA research questions and hypotheses are normal experiment-workflow entries. A question is marked operational only when an appropriate frozen/preregistered protocol exists; otherwise it remains exploratory and cannot be silently promoted to evidence.

MSBA/external projection spaces may use 1–32 dimensions. The persisted productive SNN core remains 5D for backward compatibility until a separately versioned N-D neuron-ID, spatial-index and `.b5d` migration has been implemented and verified.

## Neural Symbiosis

The embodiment layer can represent dedicated processing stages between endpoints and the 5D-SNN:

```text
Camera → CNN / Vision Transformer → gateway → 5D-SNN
Microphone → Audio/Speech Transformer → gateway → 5D-SNN
Database / Knowledge Graph → GNN/projector → gateway → 5D-SNN
Logic engine → neuro-symbolic projector → gateway → 5D-SNN
5D-SNN → gateway → speech/control network → audio/robotics output
```

The adapter model is open-set and framework-neutral. CNN, Transformer, LSTM/GRU/RNN, GNN, Modern Hopfield, reservoir/ESN, MLP, VAE/GAN/diffusion, autoencoder, peripheral SNN, multimodal, neuro-symbolic and custom architectures can be represented without importing their runtime frameworks into the Brain-5D core.

Gateway plasticity is **disabled by default**. Pipeline reachability or area registration is not evidence that the SNN learned to use an external area. Plastic gateway experiments require explicit preregistration, persisted RNG/model/version provenance, matched controls and the normal DATA/EVID review path.

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

1. operationalize every still-unmapped canonical RQ/H with dedicated protocols and preregistrations;
2. post-repair propagation/recurrence validation across independent seeds;
3. productive learning with holdout and matched controls;
4. closed-loop embodiment versus replay/open-loop controls;
5. experiment-only Neural Symbiosis/MSBA gateway studies with frozen/random/shuffled controls;
6. preregistered N-D projection sweeps before any productive-core N-D migration;
7. simulation-time versus wall-clock pacing calibration;
8. causal ablations of the 5D organization;
9. self-regulation/sensor-loss studies;
10. later memory/world-model, multimodal grounding and AI-as-treatment studies.

## Documentation

- [Project README](README.md)
- [Architecture](docs/02-architecture/ARCHITECTURE.md)
- [Neural Symbiosis](docs/02-architecture/NEURAL_SYMBIOSIS.md)
- [MSBA](docs/02-architecture/MSBA.md)
- [Wesen](docs/02-architecture/WESEN_ADAPTIVE_BODY.md)
- [Dashboard](docs/03-dashboard/DASHBOARD.md)
- [Roadmap](docs/08-roadmap/ROADMAP.md)
- [TODO](docs/08-roadmap/TODO.md)
- [Research/evidence framework](research/README.md)

Versioned Alpha/Sprint/Release documents are historical traceability records and should not be used as the current project status unless linked by a canonical document.

## Scientific boundary

```text
implementation test != experiment data != accepted evidence != interpretation
```

Observed values remain distinct from inferred values. Missing telemetry remains unknown. Device availability is not authorization. AI output is not empirical measurement. Pipeline reachability is not learned tool use.

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
