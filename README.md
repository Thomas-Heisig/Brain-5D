# Multi-Scale Homeostatic Recurrence Network (MHRN)

## Mehrskaliges homöostatisches Rekurrenznetzwerk

**A Spiking Neural Architecture with Topological Plasticity**

*Eine spikende neuronale Architektur mit topologischer Plastizität*

[Scientific treatise / Wissenschaftliche Abhandlung](research/publications/README.md) · [Naming and compatibility / Benennung und Kompatibilität](NAMING.md).

MHRN is the current project name. Historical publications, scientific coordinates, evidence identifiers and compatible `.b5d` files retain their original meaning. The name does not establish consciousness or a performance advantage. The observed platform migration results are in [the status record](docs/05-quality/mhrn-platform-migration.json).


**Experimental sparse 5D spiking-neural research framework with deterministic persistence, controlled plasticity, embodiment, multi-network peripheral integration and scientific provenance.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.5.0a7-orange.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

MHRN is a research framework for studying learning, self-organization and embodied closed-loop behavior in a sparse five-dimensional spiking neural network (SNN). The SNN remains the primary adaptive system. Language models, research assistants and peripheral neural networks are bounded components and do not acquire implicit authority over canonical neural state, reward, memory, experiment DATA or accepted EVID.

> **Scientific status:** MHRN is an experimental engineering and research platform. Implementation, passing tests, dashboards, reachable devices, generated reports or available AI/network adapters are not by themselves scientific evidence. The project makes no claim of AGI, consciousness, sentience or biological equivalence.

## Current `main` baseline

Updated on **2026-09-07** after the dashboard release workflow, shared natural-language reader and repository verification updates:

- package version: `0.5.0a7`
- latest local fast-suite snapshot: **849 passed, 5 skipped, 3 failed**; 32 slow tests deselected
- the three known failures are Windows line-ending and publication-path contract expectations; this local snapshot is not fully green
- last recorded browser suite: **5 passed** with Chromium
- current `main` HEAD: `a5cdfa7b4fcce97eea8b68c9b81fe2fea1757c56`
- Research Catalog / variable-dimension merge commit: `85e7209509b348bf7912dde01d3d9ebb078a2e61`
- latest fully completed pre-merge `main` CI baseline: **success** (run #598)
- the merge-triggered `main` CI is the authoritative verification for the new baseline; do not infer success until that run completes
- GitHub `main` is the canonical source; the configured Hugging Face mirror is updated from this branch after repository changes
- Live dashboard Space: https://huggingface.co/spaces/superdigger/Brain-5D-Space
- Python verification matrix: **3.11, 3.12 and 3.13**
- Black, Ruff, Pylint, Pre-Commit, Mypy, Pyright, Scientific Integrity, security, wheel and Docker are mandatory CI gates
- PR #21 is merged; no scientific DATA/EVID was rewritten by the integration

The dashboard uses explicit unknown-state rendering. Missing telemetry is never replaced with plausible-looking constants.

## Implemented system layers

| Layer | Current capability |
| --- | --- |
| SNN core | Sparse 5D coordinates, Izhikevich RS neurons, delayed event propagation, deterministic RNG state |
| Learning | STDP, signed eligibility traces, delayed reward / three-factor learning, productive-learning protocols |
| Homeostasis | Firing-rate, threshold and energy regulation with explicit telemetry |
| Structural plasticity | Proposal → approval/rejection → bounded mutation → journal → undo/recovery |
| Persistence | `.b5d` snapshots, delta journal, structural journal, checkpoints, deterministic restore/continue |
| Embodiment | Typed sensors/actuators, authorization gates, audit trail, host interoception, device discovery, deterministic environments |
| Neural Symbiosis | Open-set peripheral neural/virtual areas, disabled pipeline templates and inert plastic-gateway candidate math at the embodiment boundary |
| MSBA | Modality-specific audio/vision/digital gateway contracts, energy/resource accounting and configurable external projection spaces from 1–32 dimensions |
| Experience loop | Sensor → encoding → SNN → action → observed outcome → reward path with explicit authorization |
| Research | Fragmentable RQ/H registries, searchable Research Catalog, manifests, DATA/EVID separation, scientific integrity gate, AI provenance, frozen replay and causal-taint contracts |
| Experiment observability | Tick, spike, neuron, synapse, latency, recurrence and digest measurements persisted per run |
| Dashboard | Responsive operator/research shell plus dedicated adaptive `Wesen` body view |
| Accessibility | Shared German read-aloud controls for the File Viewer, chat file cards and Research Chat answers |
| AI boundary | Research AI / Language Organ / Cognitive Advisor contracts remain read-only or proposal-only unless explicitly registered as a treatment |

## Research Catalog and variable dimensions

The research workflow now loads canonical base registries plus deterministic fragments such as `questions.*.yaml` and `hypotheses.*.yaml`. Duplicate IDs fail closed. `RQ-MSBA-E01` through `RQ-MSBA-E05` and their matching hypotheses are first-class registry entries and visible through the normal Experiment Workflow.

The frontend uses a searchable Research Catalog rather than relying on a single long pulldown. Questions are marked `OPERATIONAL` when a matching frozen/preregistered protocol exists and `EXPLORATORY` otherwise. Exploratory questions may run through the bounded runtime path but must not be promoted as confirmatory EVID.

The workflow catalog API publishes backend-owned `domain`, `status`, `evidence_status` and `experiment_progress` facets. Current generated catalog, evidence and open-question reports are regenerated after accepted canonical registry changes; historical experiment-owned reports remain untouched.

MSBA/external projection spaces can declare **1–32 dimensions**. This does **not** yet change the persisted productive SNN core: neuron IDs, `.b5d` persistence and the canonical spatial core remain 5D until a separately versioned N-D storage/ID migration is designed, tested and preregistered. The remaining work is explicitly tracked in both [`TODO`](docs/08-roadmap/TODO.md) and [`ROADMAP`](docs/08-roadmap/ROADMAP.md).

## Neural Symbiosis — embodied multi-network interface

`Neural Symbiosis` is the international-facing name for the peripheral multi-network layer inside Embodiment/Wesen. It allows dedicated neural or virtual processing stages to be placed between physical/digital endpoints and the 5D-SNN without redefining the scientific core.

Examples:

```text
Camera → CNN / Vision Transformer → afferent gateway → 5D-SNN
Microphone → Audio/Speech Transformer → gateway → 5D-SNN
Database → Knowledge adapter / GNN → gateway → 5D-SNN
Logic engine → neuro-symbolic projector → gateway → 5D-SNN
5D-SNN → gateway → Speech/Language network → audio output
5D-SNN → gateway → GRU / control MLP → robotics adapter
```

The adapter contract is deliberately open-set and framework-neutral. CNNs, Transformers, LSTM/GRU/RNN, GNN, Modern Hopfield, reservoir/ESN, MLP, VAE/GAN/diffusion, autoencoders, peripheral SNNs, multimodal/neuro-symbolic networks and future custom architectures can be represented through `NetworkAreaAdapter` without importing their implementation framework into the MHRN core.

Virtual cognitive systems such as logic engines, databases, knowledge graphs, retrieval systems or external memory stores can participate through explicit virtual-area adapters.

**Scientific boundary:** all gateway learning is disabled by default. Endpoint reachability, area registration or a visible pipeline is not evidence that the SNN learned to use that area. Synaptic/structural/efferent gateway plasticity must first be enabled only inside an explicit preregistered experiment with its own RNG, model/version hashes, controls, DATA and EVID path.

See [`docs/02-architecture/NEURAL_SYMBIOSIS.md`](docs/02-architecture/NEURAL_SYMBIOSIS.md).

## Read-aloud support

The shared File Viewer and Research Chat provide natural-language German read-aloud controls through the browser Speech Synthesis API. Markdown links, formatting markers and URLs are simplified before speech. The controls support start, pause, resume and stop for file previews, expanded chat file cards and the latest assistant answer. Browsers without speech synthesis keep the text usable and disable the unsupported control gracefully.

## Runtime and experiment observability

The generated experiment path distinguishes **runtime execution** from **observable network activity**.

Historical `EXP-GEN-0009` through `EXP-GEN-0012` completed without runtime exceptions but recorded zero visible spikes/activated neurons because the older impulse probe observed only the output-spike projection. Those historical artifacts remain unchanged for scientific traceability.

The current probe records the complete observed network response:

- executed ticks;
- all published neuron spike IDs and spike sequence;
- activated-neuron count;
- total spike count and peak spike rate;
- delivered synaptic events;
- ticks with synaptic activity;
- maximum synaptic-current target count;
- total synapse count;
- first/last response latency;
- recurrence/return events;
- state digest before and after the probe.

New Science Runner experiments persist these observables in `research/experiments/<EXP-ID>/DATA/` together with workflow, manifest, configuration/provenance and report artifacts. Historical experiments are never rewritten to match newer instrumentation.

Large raw run series are preserved as immutable/compressed artifacts while bounded projections such as `runs.json` and `analysis/ai_packet.json` can be used for dashboards and small/local AI review. Compact projections never replace the raw scientific record.

## Wesen and Embodiment

MHRN intentionally separates the technical body interface from the live body visualization:

- **Embodiment** configures/observes sensors, devices, actuators, permissions, connection quality and body boundaries.
- **Wesen** is a read-only live projection of the observed machine body.
- **Neural Symbiosis** is shown inside `Wesen` as a read-only view of possible peripheral network/virtual pipelines and endpoint reachability.

The `Wesen` page builds its morphology from published connections rather than from a fixed human-like anatomy. Sensor and actuator branches appear from observed connection data; unsupported or missing endpoints stay explicitly unavailable. Host CPU, memory, temperature, fan, disk and timing signals are treated as machine-native interoception where available.

Adaptive organism/anatomy layers provide semantic device icons, tooltips, camera pan/zoom, timeline, delayed self-model, body-like machine-native scaffold, empirical overlays and causal-tracer presentation. These are operator/research views only and do **not** establish consciousness or causality.

See:

- [`docs/02-architecture/WESEN_ADAPTIVE_BODY.md`](docs/02-architecture/WESEN_ADAPTIVE_BODY.md)
- [`docs/02-architecture/NEURAL_SYMBIOSIS.md`](docs/02-architecture/NEURAL_SYMBIOSIS.md)
- [`docs/02-architecture/EMBODIMENT_REAL_BODY.md`](docs/02-architecture/EMBODIMENT_REAL_BODY.md)

## What remains scientifically open

The next gains should come from evidence closure rather than feature volume:

- dedicated protocols/preregistrations for every still-unmapped canonical RQ/H;
- post-repair multi-seed propagation/recurrence validation;
- productive-learning evidence and independent replication;
- closed-loop embodiment evidence and EVID promotion;
- experiment-only Neural Symbiosis/MSBA gateway studies with frozen/random/shuffled controls;
- preregistered N-D projection sweeps and later versioned productive-core N-D migration;
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
git clone https://github.com/Thomas-Heisig/Brain-5D.git MHRN
cd MHRN
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

Large storage stress tests are intentionally opt-in/scheduled. Scientific integrity, typing, lint, security, packaging and Docker checks are enforced through CI/release workflows.

## Architecture at a glance

```text
External / simulated / virtual environment
        |
        v
Sensors / network / camera / audio / database / logic / devices
        |
        v
Embodiment adapters + authorization + provenance
        |
        +---- optional dedicated neural/virtual areas
        |        CNN / Transformer / RNN / GNN / memory / logic / custom
        |                       |
        |                 explicit gateway
        v                       v
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
 Approval / safety gates       explicit gateway
                                  |
                           optional decoder/control area
                                  |
                              Actuator hub
                                  |
                           observed outcome
                                  |
                             feedback/reward

Persistence + research provenance surround the loop.
Wesen visualizes published state and Neural Symbiosis reachability read-only.
```

Detailed architecture: [`docs/02-architecture/ARCHITECTURE.md`](docs/02-architecture/ARCHITECTURE.md).

## Repository structure

```text
src/                     runtime implementation
  core/                  sparse SNN
  learning/              STDP, eligibility, reward learning, preparation contracts
  homeostasis/           regulatory mechanisms
  self_organization/     proposal, approval, structural plasticity, morphology
  embodiment/            sensors, actuators, authorization, interoception, Neural Symbiosis/MSBA contracts
  experience/            closed-loop experience composition
  storage/               snapshots, journals, checkpoint and recovery
  research/              experiment/evidence machinery and registry audit
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
@software{heisig2026mhrn,
  author  = {Thomas Heisig},
  title   = {Multi-Scale Homeostatic Recurrence Network (MHRN)},
  year    = {2026},
  version = {0.5.0a7},
  url     = {https://github.com/Thomas-Heisig/Brain-5D},
  license = {MIT}
}
```

## License

MIT License. See [LICENSE](LICENSE).

## Wissenschaftliche Abhandlung und Publikationsarchiv

[KI - Die geliehene Intelligenz: vollstaendige wissenschaftliche Abhandlung](research/publications/README.md)

Die Research-Kategorie `publications` enthaelt Word, Markdown, Literatur, Forschungsfragen, Hypothesen, Ergebnisdarstellungen, Originalmanuskripte und alle Begleitdateien. Die kapitelweise Lesefassung ist im zentralen File Viewer vollstaendig zugaenglich. Datierte Originale bleiben unveraendert und schreibgeschuetzt; kanonische Register und Evidenzfreigaben werden nicht ersetzt.

Main integration decisions and verification scope are recorded in
[the consolidation record](docs/08-roadmap/MAIN_CONSOLIDATION_2026-09-07.md).

## Consciousness critique and research safeguards

The [current treatise](research/publications/README.md) integrates a [38-topic critique audit](research/critique/CONSCIOUSNESS_CRITIQUE.md), [22 registered research questions and protocol contracts](research/protocols/COGNITION_CONSCIOUSNESS.md), and a [precautionary ethics policy](research/ethics/AI_WELFARE_POLICY.md). Cognitive-task success is not a consciousness verdict. The new battery has tested stimulus/scoring instruments; unvalidated native adapters cannot silently fall back to generic experiments. No empirical consciousness findings or external ethics approval are claimed.

## Full-stack File Viewer completion — 2026-09-08

The repository File Viewer is the canonical renderer for Dashboard, Research and Chat file cards. It now includes bounded media metadata, bounded PDF metadata/text when local tools are available, optional local Graphviz/PlantUML-to-SVG conversion, DOCX page/section markers, RIS export with selectable citation styles, and a responsive split editor with live preview and optimistic-lock conflict diff. Scientific artifacts remain read-only and local converters never upload source material.
