# Brain-5D

**Experimental sparse 5D spiking-neural research framework with deterministic persistence, controlled plasticity, embodiment and scientific provenance.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.5.0a7-orange.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Brain-5D is a research framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network (SNN). The SNN remains the primary adaptive system. Language models and research assistants are bounded interpretation/proposal components and do not acquire implicit authority over neural, reward, memory or evidence state.

> **Scientific status:** Brain-5D is an experimental engineering and research platform. Implementation, passing tests, dashboards and generated reports are not by themselves scientific evidence. The project makes no claim of AGI, consciousness, sentience or biological equivalence.

## Current main baseline

As of **2026-09-05**, `main` is the canonical development line and the latest completed full GitHub CI run is green.

- package version: `0.5.0a7`
- current collection: **735 tests**
- verified full-suite result during the repair cycle: **733 passed, 2 skipped, 0 failed**
- latest complete GitHub CI matrix: **success**
- Python verification: **3.11, 3.12 and 3.13**
- Mypy and Pyright: **green**
- Black, Ruff, Pylint and Pre-Commit: **green**
- Scientific Integrity Gate: **green**
- Security checks including Bandit and pip-audit: **green**
- fast-suite coverage baseline: **72%**
- current dashboard navigation: **Overview, Control, Research, Settings, Wesen, Embodiment**
- `Network` is no longer a primary user-facing workspace
- Release/Gate is opened from the footer rather than the primary navigation
- no open pull requests were present at the verification point
- the remaining `tmp-do-not-use` branch is obsolete, contains no commits ahead of `main`, and must not be used as a development base

The dashboard uses explicit unknown-state rendering. Missing telemetry is never replaced with plausible-looking constants.

## Runtime and experiment observability

The September 5 repair of the generated experiment path established an important distinction between **runtime execution** and **observable network activity**.

Historical `EXP-GEN-0009` through `EXP-GEN-0012` completed without runtime exceptions but recorded zero visible spikes/activated neurons because the impulse probe observed only the output-spike projection. Those historical artifacts remain unchanged for scientific traceability.

The current probe now records the complete observed network response:

- executed ticks;
- all published neuron spike IDs and the spike sequence;
- activated-neuron count;
- total spike count and peak spike rate;
- delivered synaptic events;
- ticks with synaptic activity;
- maximum synaptic-current target count;
- total synapse count;
- first/last response latency;
- recurrence/return events;
- state digest before and after the probe.

The recurrence topology used by the impulse experiment now contains an actual return path to the source neuron. A direct runtime validation demonstrated active ticks, neuron spikes and synaptic delivery in both feed-forward and recurrent conditions; recurrence increased the observed spike and synaptic-event counts in the validation run.

New Science Runner experiments persist these observables in `research/experiments/<EXP-ID>/DATA/runs.json` together with workflow, manifest, configuration/provenance and report artifacts. Historical experiments are never rewritten to make them match newer instrumentation.

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
| Experiment observability | Tick, spike, neuron, synapse, latency, recurrence and digest measurements persisted per run |
| Dashboard | Responsive operator/research shell plus dedicated adaptive `Wesen` body view |
| AI boundary | Research AI / Language Organ / Cognitive Advisor contracts remain read-only or proposal-only unless explicitly registered as a treatment |

## Wesen and Embodiment

Brain-5D intentionally separates the technical body interface from the live body visualization:

- **Embodiment** configures/observes real sensors, devices, actuators, permissions and body boundaries.
- **Wesen** is a read-only live projection of the observed machine body.

The `Wesen` page builds its morphology from currently published connections rather than from a fixed human-like anatomy. Sensor and actuator branches appear from observed connection data; unsupported or missing endpoints stay explicitly unavailable. Host CPU, memory, temperature, fan, disk and timing signals are treated as machine-native interoception where available.

Adaptive organism v2 provides semantic device icons, tooltips, camera pan/zoom, timeline, satellites and delayed self-model. Anatomy v3 adds a **body-like but machine-native scaffold**: a sensory head zone, central SNN core, torso interoception, a feedback/spine path and actuator branches that extend as arm-/leg-like output regions. The scaffold is presentation-only and does not imply biological homology.

The body visualization is icon-first. Device labels and metric strings are removed from the crowded SVG body and replaced by semantic symbols for camera, microphone, speaker, display, GPU, network, USB, storage, printer, robotics and related endpoint classes. Full labels/values remain available through SVG tooltips and the inspector. A scrollable icon dock below the body provides guaranteed mouse/keyboard access to every discovered endpoint even when the body is dense.

An empirical overlay consumes additional read-only backend sources when available: `/api/embodiment/metrics`, `/api/embodiment/history`, `/api/embodiment/pipeline`, `/api/live/io-flow` and `/api/live/population`. It can display measured active fraction, spikes, input/output flow, quality, sensory integrity, resource pressure, continuity risk and pipeline availability. Missing values remain `—` and are never replaced by invented constants.

The delayed self-model uses a bounded frame ring buffer and selects the earlier body frame matching reported loopback latency where available. Browser-local morphology snapshots can be inspected with a timeline scrubber. These snapshots are operator history only and are not scientific DATA/EVID.

The UI can also surface existing event/decision/action/receipt identifiers as causal tracer labels. It never manufactures missing IDs, and visual path highlighting remains distinct from experimentally established causality.

These visuals do **not** establish consciousness or causality. Recurrence and loopback are technical observables. Experimental causal claims still require controlled intervention/outcome evidence.

See [`docs/02-architecture/WESEN_ADAPTIVE_BODY.md`](docs/02-architecture/WESEN_ADAPTIVE_BODY.md).

## What remains scientifically open

The next scientific gains should come from evidence closure rather than feature volume. Priority areas remain:

- productive-learning evidence and independent replication;
- closed-loop embodiment evidence and EVID promotion;
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
- [Scientific evidence framework](research/README.md)

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
python -m mypy src/
python -m pyright
python -m black --check src tests scripts
python -m ruff check src tests scripts
python -m pre_commit run --all-files
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

## Documentation and evidence policy

The authoritative current-state documents are listed in [`docs/README.md`](docs/README.md). Versioned Alpha/Sprint/Release documents are retained for traceability but do not override current `main`.

Hierarchy:

1. current code and machine-readable contracts on `main`;
2. current CI/test results;
3. experiment `DATA/`;
4. accepted `EVID` artifacts;
5. interpretation/narrative documentation.

Historical DATA is immutable in meaning: instrumentation improvements create new runs rather than silently rewriting prior experimental observations.

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
