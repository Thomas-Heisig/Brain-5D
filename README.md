# Brain-5D

**Experimental sparse 5D spiking-neural research framework with deterministic persistence, controlled plasticity, embodiment and scientific provenance.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![CI](https://img.shields.io/badge/main-CI%20green-brightgreen.svg)](https://github.com/Thomas-Heisig/Brain-5D/actions)
[![Version](https://img.shields.io/badge/version-0.5.0a7-orange.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Brain-5D is a research framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network (SNN). The SNN remains the primary adaptive system. Language models and research assistants are bounded interpretation/proposal components and do not acquire implicit authority over neural, reward, memory or evidence state.

> **Scientific status:** Brain-5D is an experimental engineering and research platform. Implementation, passing tests, dashboards and generated reports are not by themselves scientific evidence. The project makes no claim of AGI, consciousness, sentience or biological equivalence.

## Current verified baseline

As of **2026-09-04**, `main` is the canonical development line.

- package version: `0.5.0a7`
- CI: green on Python 3.11, 3.12 and 3.13
- test collection: **700 tests**
- unique full-suite outcome on Python 3.13: **698 passed, 2 opt-in large-storage tests skipped**
- fast-suite coverage: **72%**
- Scientific Integrity Gate: green
- wheel build/install and Docker build/runtime verification: green

The latest dashboard work is part of `main`: seven full-width responsive workspaces, command palette, keyboard navigation, focus mode, explicit unknown-state rendering and a real-body embodiment view driven by observed host/device state.

## Implemented system layers

| Layer | Current capability |
| --- | --- |
| SNN core | Sparse 5D coordinates, Izhikevich RS neurons, delayed event propagation, deterministic RNG state |
| Learning | STDP, signed eligibility traces, delayed reward / three-factor learning, productive learning experiments |
| Homeostasis | Firing-rate, threshold and energy regulation with explicit telemetry |
| Structural plasticity | Proposal → approval/rejection → bounded mutation → journal → undo/recovery |
| Persistence | `.b5d` snapshots, delta journal, structural journal, checkpoints, deterministic restore/continue |
| Embodiment | Typed sensors/actuators, authorization gates, audit trail, host interoception, device discovery, deterministic environments |
| Experience loop | Sensor → encoding → SNN → action → observed outcome → reward path with explicit authorization |
| Research | Registries, manifests, DATA/EVID separation, scientific integrity gate, AI provenance, frozen replay and causal-taint contracts |
| Dashboard | Overview, Network, Control, Research, Release, Settings, Embodiment workspaces; responsive operator experience |
| AI boundary | Research AI / Language Organ / Cognitive Advisor contracts remain read-only or proposal-only unless explicitly registered as a treatment |

## What remains scientifically open

Brain-5D already contains infrastructure and preliminary experiment artifacts, but the central scientific questions require clean, preregistered and independently repeated evidence runs. Priority areas are productive learning, closed-loop embodiment, time-scale calibration, 5D ablations, self-regulation/sensor loss, memory/world models and later multimodal knowledge grounding.

See:

- [Development roadmap](docs/08-roadmap/ROADMAP.md)
- [Current TODO](docs/08-roadmap/TODO.md)
- [Research roadmap](docs/08-roadmap/RESEARCH_ROADMAP.md)
- [Documentation index](docs/README.md)

## Quick start

```bash
git clone https://github.com/Thomas-Heisig/Brain-5D.git
cd Brain-5D
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run with the integrated dashboard:

```bash
python -m src.main --config configs/poc_config.yaml
```

Or on Windows use the repository launcher:

```powershell
.\start.ps1
```

The dashboard defaults to `http://127.0.0.1:8765`.

## Testing and verification

```bash
# fast regression suite
python -m pytest -m "not slow"

# slow suite
python -m pytest -m "slow"

# scientific integrity checks are also enforced by CI
```

Large storage stress tests are intentionally opt-in and are not silently counted as executed when skipped.

## Architecture at a glance

```text
Sensors / Environment / Host interoception
                 |
                 v
       Signal / Experience boundary
                 |
                 v
+--------------------------------------------------+
|           Sparse 5D Spiking Neural Core          |
|  dynamics | STDP/eligibility | homeostasis       |
+---------------------+----------------------------+
                      |
          +-----------+-----------+
          v                       v
 Structural self-organization   Action proposals
          |                       |
          v                       v
 Approval / safety gates       Actuator hub
          |                       |
          +-----------+-----------+
                      |
                observed outcome
                      |
                 reward signal

Persistence + Research provenance surround the complete loop.
The dashboard observes/operates through explicit contracts; AI components
remain bounded by authority, treatment and provenance rules.
```

Detailed architecture: [docs/02-architecture/ARCHITECTURE.md](docs/02-architecture/ARCHITECTURE.md).

## Repository structure

```text
src/                     runtime implementation
  core/                  sparse SNN
  learning/              STDP, eligibility, reward learning, preparation contracts
  homeostasis/           regulatory mechanisms
  self_organization/     proposal, approval, structural plasticity, morphology
  embodiment/            sensors, actuators, authorization, interoception
  experience/             closed-loop experience composition
  storage/               snapshots, journals, checkpoint and recovery
  research/              experiment/evidence machinery
  research_assistant/    bounded AI research tooling
  dashboard/             operator/research UI and APIs
research/                registries, protocols, DATA/EVID and generated research views
docs/                    canonical + historical documentation
tests/                   700 collected tests
configs/                 runtime and experiment configuration
scripts/                 verification and utility scripts
releases/                machine-readable release registry
```

## Documentation policy

The authoritative current-state documents are listed in [docs/README.md](docs/README.md). Versioned Alpha/Sprint/Release documents are retained for traceability but must not override the current `main` state.

The hierarchy is deliberately strict:

1. current code and machine-readable contracts on `main`;
2. CI/test results for engineering verification;
3. experiment `DATA/` for measured run data;
4. accepted `EVID` artifacts for scientific evidence;
5. human/AI interpretations and narrative documentation.

## Security

The dashboard binds to loopback by default. It exposes operator and file-management capabilities and must not be directly port-forwarded to the public Internet. See [docs/03-dashboard/DASHBOARD.md](docs/03-dashboard/DASHBOARD.md) and [SECURITY.md](SECURITY.md).

## Citation

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

See also [CITATION.cff](CITATION.cff).

## License

MIT License. See [LICENSE](LICENSE).
