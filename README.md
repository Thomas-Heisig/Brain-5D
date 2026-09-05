# Brain-5D

**Experimental sparse 5D spiking-neural research framework with deterministic persistence, controlled plasticity, embodiment and scientific provenance.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.5.0a7-orange.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Brain-5D is a research framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network (SNN). The SNN remains the primary adaptive system. Language models and research assistants are bounded interpretation/proposal components and do not acquire implicit authority over neural, reward, memory or evidence state.

> **Scientific status:** Brain-5D is an experimental engineering and research platform. Implementation, passing tests, dashboards and generated reports are not by themselves scientific evidence. The project makes no claim of AGI, consciousness, sentience or biological equivalence.

## Current main baseline

As of **2026-09-05**, `main` is the canonical development line.

- package version: `0.5.0a7`
- current test collection after the adaptive Wesen regression additions: **723 tests**
- fast-suite coverage baseline: **72%**
- Scientific Integrity Gate is part of the required CI path
- wheel build/install and Docker verification remain part of release verification
- current dashboard navigation: **Overview, Control, Research, Settings, Wesen, Embodiment**
- `Network` is no longer a primary user-facing workspace
- Release/Gate is opened from the footer rather than the primary navigation

The dashboard uses explicit unknown-state rendering. Missing telemetry is never replaced with plausible-looking constants.

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
| Dashboard | Responsive operator/research shell plus dedicated adaptive `Wesen` body view |
| AI boundary | Research AI / Language Organ / Cognitive Advisor contracts remain read-only or proposal-only unless explicitly registered as a treatment |

## Wesen and Embodiment

Brain-5D intentionally separates the technical body interface from the live body visualization:

- **Embodiment** configures/observes real sensors, devices, actuators, permissions and body boundaries.
- **Wesen** is a read-only live projection of the observed machine body.

The `Wesen` page builds its morphology from currently published connections rather than from a fixed human-like anatomy. Sensor and actuator branches appear from observed connection data; unsupported or missing endpoints stay explicitly unavailable. Host CPU, memory, temperature, fan, disk and timing signals are treated as machine-native interoception where available.

The body membrane changes with the observed connection envelope. The UI also provides node inspection, session-local morphology history, recurrence trend, signal animation, causal-path emphasis and a delayed self-model that mirrors the same current morphology.

These visuals do **not** establish consciousness or causality. Recurrence and loopback are technical observables. Experimental causal claims still require controlled intervention/outcome evidence.

See [`docs/02-architecture/WESEN_ADAPTIVE_BODY.md`](docs/02-architecture/WESEN_ADAPTIVE_BODY.md).

## What remains scientifically open

The next scientific gains should come from evidence closure rather than feature volume. Priority areas remain:

- productive-learning evidence;
- closed-loop embodiment evidence;
- time-scale/runtime calibration;
- 5D ablations;
- self-regulation and sensor-loss studies;
- memory/world-model experiments;
- multimodal grounding;
- AI-as-treatment experiments.

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

Or on Windows:

```powershell
.\start.ps1
```

The dashboard defaults to `http://127.0.0.1:8765`.

## Testing and verification

```bash
python -m pytest -m "not slow"
python -m pytest -m "slow"
```

Large storage stress tests are intentionally opt-in. Scientific integrity, typing, lint, security and packaging checks are enforced through CI/release workflows.

## Architecture at a glance

```text
External environment
        |
        v
Sensors / network / camera / audio / device inputs
        |
        v
Embodiment adapters + authorization + quality
        |
        v
Signal / Experience boundary
        |
        v
+--------------------------------------------------+
|           Sparse 5D Spiking Neural Core          |
| dynamics | STDP/eligibility | homeostasis       |
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
                 feedback/reward

Host interoception feeds the body state.
Persistence + Research provenance surround the loop.
Wesen visualizes published state read-only.
```

Detailed architecture: [`docs/02-architecture/ARCHITECTURE.md`](docs/02-architecture/ARCHITECTURE.md).

## Repository structure

```text
src/                     runtime implementation
  core/                  sparse SNN
  learning/              STDP, eligibility, reward learning, preparation contracts
  homeostasis/           regulatory mechanisms
  self_organization/     proposal, approval, structural plasticity, morphology
  embodiment/            sensors, actuators, authorization, interoception
  experience/            closed-loop experience composition
  storage/               snapshots, journals, checkpoint and recovery
  research/              experiment/evidence machinery
  research_assistant/    bounded AI research tooling
  dashboard/             operator/research UI and APIs
research/                registries, protocols, DATA/EVID and generated research views
docs/                    canonical + historical documentation
tests/                   current regression suite
configs/                 runtime and experiment configuration
scripts/                 verification and utility scripts
releases/                machine-readable release registry
```

## Documentation policy

The authoritative current-state documents are listed in [`docs/README.md`](docs/README.md). Versioned Alpha/Sprint/Release documents are retained for traceability but do not override current `main`.

Hierarchy:

1. current code and machine-readable contracts on `main`;
2. current CI/test results;
3. experiment `DATA/`;
4. accepted `EVID` artifacts;
5. interpretation/narrative documentation.

## Security

The dashboard binds to loopback by default. It exposes operator and file-management capabilities and must not be directly port-forwarded to the public Internet. See [`docs/03-dashboard/DASHBOARD.md`](docs/03-dashboard/DASHBOARD.md) and [`SECURITY.md`](SECURITY.md).

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

## License

MIT License. See [LICENSE](LICENSE).
