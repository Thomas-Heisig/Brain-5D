# MHRN Operator & Research Dashboard

## Purpose

The dashboard is the operator and research interface for MHRN. It visualizes published state, exposes explicit operator controls and connects research workflows without becoming an alternative simulation engine.

The current UI is a responsive, full-width workspace system with one shared visual language. Presentation layers do not manufacture scientific state and do not acquire hidden runtime authority.

## Primary navigation

The user-facing frontend is intentionally reduced to **three primary areas**:

1. **Dashboard** — operator command center with runtime/health/gate/CI state, neural activity, storage, learning, structural state and fast routes to explicit controls.
2. **Wissenschaft** — Network Workbench, experiment workflow, research DATA/EVID/documentation, formula rendering, Research Chat and scientific parameter inspection.
3. **Runtime & Wesen** — adaptive machine-native body, technical body boundary, interoception, connection inventory, Neural Symbiosis/MSBA visibility and capability maturity.

The existing `Control`, `Network`, `Research`, `Settings`, `Embodiment` and `Release/Gate` workspaces remain internal routed surfaces so their lifecycle and functions are preserved. They are no longer independent top-level navigation concepts.

`Release/Gate` remains a footer utility. `Control` belongs to the Dashboard operator flow. `Network` and `Settings` belong to Wissenschaft. Technical Embodiment is embedded into Runtime & Wesen.

The three-area shell deliberately keeps the legacy route buttons in the DOM but visually hides the legacy navigation. This lets `app.js` remain the sole lifecycle owner and preserves its lazy initialization behavior.

## Operator experience

The Dashboard is the command center rather than a collection of unrelated pages. It exposes system state, runtime health, scientific gate, CI/release context, operating mode, neural activity, SNN size/spikes, storage/persistence, learning/homeostasis and structural changes.

Fast actions continue to route through the existing explicit control surfaces. Presentation never bypasses the typed control plane.

The dashboard experience layer provides unified workspace navigation, live runtime context, command palette, focus/keyboard navigation where supported, responsive desktop/tablet/mobile layouts, light/dark presentation contracts, reduced-motion support and explicit rendering of unknown/unavailable values.

## State integrity

The dashboard follows non-negotiable display rules:

- `0` means measured zero only when the source measured zero;
- missing values remain unknown/unavailable;
- stale telemetry is distinguishable from live telemetry where age is available;
- device discovery is not device authorization;
- an accepted action is not proof of an observed effect;
- UI logs are not scientific provenance;
- AI text is interpretation/proposal, not empirical measurement;
- visual connectivity is not automatically causal evidence;
- planned functionality is labelled **Not implemented yet** instead of being rendered as a functioning control.

## Runtime controls

The runtime control service supports bounded commands such as start/resume, pause, stop, single-step, exact tick runs, snapshots and configuration changes where the underlying capability exists.

Wall-clock target Hz is separate from simulation `dt`. Increasing target Hz must not silently alter neural-time semantics.

## Wissenschaft

The scientific area combines three workflows that remain technically separate:

1. **Network Workbench** — live neural dynamics, topology/inspection, raster/histogram and low-load structural visualization.
2. **Experimente & Nachweise** — canonical RQ/H catalog, experiment runner, DATA/EVID, reports, file manager, documentation and Research Chat.
3. **Parameter** — provenance-aware scientific configuration and pending-change workflow.

### Neuron Model Viewer

The old nested 5D visual projection is replaced in the scientific Network Workbench by a bounded **Neuron Model Viewer**. The legacy panel remains in the DOM for compatibility but is hidden by the viewer module.

Implemented viewer behavior:

- real neuron coordinates are obtained from the existing bounded `/api/network/projection` contract;
- deterministic sample sizes are 200, 500 or 2000 neurons, with **500 as the default**;
- **PCA is the default** and is computed client-side from the N×5 coordinate matrix via a 5×5 covariance matrix and symmetric eigendecomposition;
- PCA explained variance is displayed for the selected 2D/3D projection;
- 2D uses Canvas rather than a per-object DOM/WebGL scene;
- 3D uses one Three.js `Points`/`BufferGeometry` cloud where the CDN is available, with a Canvas fallback;
- colour uses the currently available per-neuron activity value from the inspector contract;
- point size uses synaptic degree when it can be derived from the bounded synapse response; an incomplete synapse sample is explicitly labelled bounded rather than exact;
- hover exposes neuron ID and the exact five canonical coordinates;
- alternative tabs provide a 5×5 Pearson correlation heatmap and parallel-coordinate view;
- update policy is manual by default, with opt-in 5 s or 30 s refresh.

The following requested viewer capabilities are **Not implemented yet** because no provenance-bound backend contract currently exists:

- t-SNE backend jobs;
- UMAP backend jobs;
- cluster labels and Silhouette/Dunn scores;
- lasso/cluster export into experiment workflows;
- persisted projection/profile cache;
- a true per-neuron firing-rate-Hz field in the Network Inspector response.

These capabilities must not be simulated in the browser merely to make the UI appear complete. Backend algorithms, versions, parameters, input digest and result provenance need to be defined first.

## Wesen workspace

`Runtime & Wesen` is the primary living-system area. The existing `Wesen` implementation remains adaptive and read-only: it reads published status, embodiment state and connection inventory. It does not send learning commands, generate language output or issue actuator writes.

The body is machine-native rather than human-shaped:

- SNN core is the central neural component;
- host/system telemetry is interoception;
- discovered sensor endpoints form input branches;
- discovered actuator endpoints form output branches;
- feedback/loopback is represented separately;
- the visible membrane/body boundary follows the currently observed body nodes.

A camera, microphone, weather/network source, display, speaker, printer or external robot endpoint is shown only when published connection data supports it. Missing capabilities remain unavailable rather than appearing as demo anatomy.

### Capability maturity inside Runtime & Wesen

The frontend intentionally shows both present and planned capability classes:

- dynamic connection inventory/body morphology — **implemented, read-only**;
- host interoception/body boundary — **implemented** where telemetry exists;
- per-sense activate/deactivate control — **Not implemented yet**;
- productive Neural Symbiosis gateway activation/plasticity — **Not implemented yet** and remains experiment-only in the roadmap;
- canonical SNN snapshots/persistence — **implemented**;
- holistic Wesen profiles containing senses, SNN state, learning parameters, morphology and actuators — **Not implemented yet**;
- profile load/save/export/delete — **Not implemented yet**;
- personality profiles — **Not implemented yet**;
- Memory/World-Model layer — **Not implemented yet**.

This maturity display follows the canonical TODO/roadmap and is not evidence that a planned feature exists.

### Adaptive organism v2

The current presentation enhancement adds a bounded force-directed body layout. Core, internal, sensor, actuator and generic connection nodes are positioned according to their functional role while repelling each other to avoid a rigid circular anatomy.

The body membrane is derived from a padded convex hull around the current node set. As devices appear or disappear, the visible body envelope can grow, retract or change asymmetrically.

External sources can appear as satellites outside the membrane. Sensor and actuator paths are visually distinct; actuator availability never implies authorization.

### Camera and focus

The body stage has a presentation camera with pointer-centered wheel zoom, pointer drag to pan, bounded zoom, double-click reset and focus fading. These camera operations affect only rendering.

### Delayed self-model

The self-model uses a bounded in-browser frame ring buffer. When measured loopback latency is available, the mirror chooses the body frame closest to `now - latency`. If no measured latency exists, the view remains explicitly uncalibrated. Recurrence and loopback are not evidence of consciousness or self-awareness.

### Morphology history

Morphology signatures are stored as bounded browser-local snapshots when the observed body shape changes. A timeline scrubber can inspect earlier snapshots in the self-model surface.

This is operator history only. Browser `localStorage` is not research DATA/EVID and must not be cited as scientific evidence.

### Differentiated visual states

The presentation layer can distinguish reported/derived states such as thermal pressure, generic resource pressure, sensor loss, actuator failure, network isolation, recovery and unknown telemetry. These are visualization states, not emotion or illness claims.

### Causal tracer

The UI can surface event/decision/action/receipt identifiers already present in observed event text and use them as a visual tracer label. It never manufactures missing identifiers. A highlighted path remains a debugging/inspection aid unless a protocol and accepted evidence establish causality.

Detailed contract: [`../02-architecture/WESEN_ADAPTIVE_BODY.md`](../02-architecture/WESEN_ADAPTIVE_BODY.md).

## Embodiment boundary

Technical Embodiment is intentionally simpler than Wesen and is integrated as the technical body-boundary surface inside Runtime & Wesen. It represents available real/simulated sensors, actuators, permissions, connection state and body-boundary configuration.

Possible host/device signals include CPU load, memory, temperatures/fans where exposed, storage/network values and discovered camera/audio/display/printer capabilities. Missing telemetry stays unknown.

**Availability does not equal authorization.** Discovery does not grant capture or actuation permission.

## Research documentation and AI

Research connects to questions/hypotheses/claims/sources registries, experiment creation/execution, manifests/reports/DATA, evidence/integrity status, research file browser/editor, scientific formula rendering, post-hoc AI analysis where configured and the Learning Preparation Studio.

Research AI remains observing/interpreting/proposal-only by default.

## Release access

Release readiness separates engineering verification from scientific evidence. The Release/Gate surface remains available, but is opened from the dashboard footer instead of occupying a primary navigation area.

CI success, typing, security and deterministic tests are engineering gates. Experimental claims require valid evidence artifacts.

## Network access

The integrated dashboard can be opened from another device on the same trusted network. The Windows wrappers `start.cmd` and `start.ps1` bind to `0.0.0.0:8765` by default; use the host machine's LAN address, for example `http://192.168.1.25:8765`. The direct Python entry point remains loopback-only unless `--dashboard-host 0.0.0.0` is supplied.

If Windows Firewall blocks the connection, allow inbound TCP `8765` only on the intended private network profile. This dashboard has operator and file-management endpoints and has no network authentication layer; do not expose it through public port forwarding.

### Development Timeline

Release includes a repository-derived **Entwicklungs-Timeline** alongside Gate, release history, preview, the chronological release timeline and source documents. The read-only endpoint is `GET /api/release/development-timeline`.

The backend classifier in `src/dashboard/development_timeline.py` evaluates concrete module/test paths, structured research registries, verification JSON, test-baseline state and runtime or snapshot sizes. Roadmap and TODO Markdown are context-only sources and cannot make a stage pass by text alone.

The response exposes eleven canonical stages from a single neuron to consciousness research, a continuous technical marker (`Du bist hier`) and a separate scientific marker (`Wissenschaftlich hier`). Engineering, technical verification and scientific evidence each have independent scores. Stage 10 is a research frontier only: `consciousness_claim` is always `unsupported`, and the UI states that engineering maturity does not imply consciousness.

Runtime size is read from active bridge telemetry when available. A `.b5d` snapshot is shown only as `last_observed`; missing active telemetry remains `unavailable`. Stage details expose machine-derived criteria, source evidence, relevant modules/tests/experiments, limits and open work.

## Security

The supported default is:

```text
http://127.0.0.1:8765
```

Do not expose the dashboard directly to the public Internet. For remote access use an authenticated TLS reverse proxy and appropriate identity controls.

## Start

```bash
python -m src.main --config configs/poc_config.yaml
```

Windows:

```powershell
.\start.ps1
```

## Architecture boundary

```text
Runtime / Research / Storage / Embodiment
              |
       published contracts
              v
       DashboardStateStore / APIs
              |
              v
      Three-area UI shell
       /       |       \
Dashboard  Wissenschaft  Runtime & Wesen
    |          |              |
 Control   Network/Research  adaptive body
           /Settings         + technical boundary

Presentation never substitutes for DATA/EVID.
```

See also:

- [`../02-architecture/ARCHITECTURE.md`](../02-architecture/ARCHITECTURE.md)
- [`../02-architecture/WESEN_ADAPTIVE_BODY.md`](../02-architecture/WESEN_ADAPTIVE_BODY.md)
- [`API_REFERENCE.md`](API_REFERENCE.md)
- [`DASHBOARD_CONTROL_PLANE.md`](DASHBOARD_CONTROL_PLANE.md)
- [`../02-architecture/EMBODIMENT_REAL_BODY.md`](../02-architecture/EMBODIMENT_REAL_BODY.md)
- [`../../research/README.md`](../../research/README.md)
