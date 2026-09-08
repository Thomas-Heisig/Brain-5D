# Research and Strategy Alignment

This document connects the repository strategy documents to measurable Brain-5D
milestones. The source documents are:

- `docs/Analyse_Deepseek.md`
- `docs/Der_weg_zur_KI.md`
- `docs/Research.md`

## Accepted strategic conclusions

### Brain-5D is currently an SNN research platform, not a general intelligence

The current system has meaningful differentiators: deterministic sparse 5D
state, persistence, local plasticity, observability and controlled structural
changes. Those features justify continuing the architecture, but they do not by
themselves demonstrate understanding, reasoning or general intelligence.

### Scaling must be measured, not assumed

The research notes point to rapid progress in large SNN systems, but Brain-5D
must establish its own scaling curve. v0.6 therefore keeps explicit 50k, 500k
and 1M-neuron gates before any larger claim is accepted.

### Local and three-factor learning remain a valid experimental direction

The research survey does not identify a single dominant SNN learning algorithm.
Brain-5D therefore keeps STDP and three-factor rules as experimentally testable
components rather than treating them as a solved route to intelligence.

### Embodiment becomes a first-class roadmap item

A useful intelligent system needs an environment, perception and action. The
roadmap now requires a closed sensor-action loop after the multimodal adapter
phase instead of treating text interaction alone as sufficient.

### Continual learning must have explicit forgetting benchmarks

Long-running persistence is not equivalent to continual learning. Future
learning milestones require old-task retention and new-task acquisition to be
measured separately.

### Causal and neuro-symbolic capabilities are evaluation tracks

Causality and symbolic composition are not inserted into the core as unverified
architectural assumptions. They become benchmark tracks that can falsify or
support later cognitive extensions.

## Roadmap changes

### v0.5 - Self regulation

- homeostatic firing-rate control
- energy regulation
- structural plasticity limits
- 100k-tick stability benchmark

### v0.6 - Scaling

- dirty tracking
- chunked 5D storage
- active-region loading
- 50k -> 500k -> 1M measured scale gates

### v0.7 - Learning environment

- episodes
- train/evaluation split
- delayed reward
- continual-learning retention benchmark

### v0.8 - Perception and embodiment foundation

- typed text/image/audio adapters
- environment API
- sensor-to-spike encoding
- action output abstraction

### v0.9 - Memory, context and world modelling

- working context
- long-term semantic/episodic memory
- prediction error
- persistent goals

### v0.10 - Cognitive evaluation

- compositional tasks
- causal intervention tasks
- neuro-symbolic experiments
- explicit generalization benchmarks

### v0.11 - HMI and bounded action

- operator/API interface
- audited actions
- permissions and resource limits
- sandboxed external interaction

### v0.12 - Release candidate

- long soak tests
- restore-and-continue under real workloads
- benchmark suite freeze
- reproducible installation

### v1.0 - usable Brain-5D AI

v1.0 means a persistent, stable, trainable and observable system that improves
on held-out tasks, retains prior skills, uses at least two input modalities and
can perform bounded environment actions. It does not imply AGI or consciousness.
