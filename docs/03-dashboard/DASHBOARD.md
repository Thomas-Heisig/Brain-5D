# Brain-5D Operator & Research Dashboard

## Purpose

The dashboard is the operator and research interface for Brain-5D. It visualizes published state, exposes explicit operator controls and connects research workflows without becoming an alternative simulation engine.

The current UI is a responsive, full-width workspace system with a shared visual language derived from the Embodiment workspace. Presentation layers do not manufacture scientific state and do not acquire hidden runtime authority.

## Primary workspaces

Brain-5D currently exposes seven primary workspaces:

1. **Overview** — system state, runtime context, key health/telemetry and navigation into active work.
2. **Network** — neural dynamics, projections, populations, I/O flow, neuron/synapse inspection and observed topology.
3. **Control** — explicit runtime actions, pacing/tick controls and structural/operator control surfaces.
4. **Research** — experiment workflow, registries, reports, research files, AI-assisted analysis and learning preparation.
5. **Release** — scientific/engineering gate status, integration evidence and release readiness.
6. **Settings** — runtime-visible configuration and pending parameter workflow.
7. **Embodiment** — real/simulated body state, connections, interoception, sensor/actuator status and observed closed-loop context.

All workspaces use responsive full-width layouts. Dense cards, tables, canvases and inspector surfaces reflow on smaller displays rather than preserving fixed desktop widths.

## Operator experience

The dashboard experience layer provides presentation/navigation functions including:

- unified workspace navigation;
- live workspace/runtime context;
- command palette with `Ctrl/Cmd+K`;
- workspace shortcuts `1` through `7`;
- shortcut help via `?`;
- focus mode via `F` and the UI control;
- responsive desktop/tablet/mobile layouts;
- light/dark presentation contracts;
- reduced-motion support;
- explicit rendering of unknown/unavailable values.

The common shell/experience modules are **presentation-only**. Runtime actions remain in the existing typed/domain control paths.

## State integrity

The dashboard follows several non-negotiable display rules:

- `0` means a measured zero only when the source actually measured zero;
- missing values remain null/unknown/unavailable;
- stale telemetry is distinguishable from live telemetry;
- device discovery is not shown as device authorization;
- an accepted action command is not presented as proof of an observed effect;
- UI logs are not scientific provenance;
- generated AI text is labeled as interpretation/proposal, not empirical measurement.

## Runtime controls

The runtime control service supports bounded commands such as start/resume, pause, stop, single-step, exact tick runs, snapshots and configuration changes where the underlying capability exists.

Wall-clock target Hz is a runtime pacing parameter. It must remain conceptually separate from simulation `dt`; increasing target Hz should not silently alter neural-time semantics.

Control actions are explicit requests routed through control services. The dashboard shell itself does not issue hidden control writes.

## Network observation

Network views are backed by published/live projection contracts rather than demo data. Supported surfaces include real neuron/synapse counts, 5D coordinates, activity/energy/weight projections, population metrics and inspector pagination.

A projection or heatmap is an aggregation of observed model state. It must not be interpreted as proof of causality without a protocol that establishes the relevant causal relation.

## Research workspace

The Research workspace connects to the repository research system:

- questions/hypotheses/claims/sources registries;
- experiment creation and execution workflow;
- manifests, reports and `DATA` artifacts;
- evidence and integrity status;
- research file browser/editor;
- post-hoc AI analysis where an explicit backend/treatment is configured;
- Learning Preparation Studio.

Research AI remains observing/interpreting/proposal-only by default. Scientific runs must preserve AI provenance, treatment identity and data-partition boundaries.

## Embodiment workspace

Embodiment combines simulated environments and available real-host observations. The central self-model is constructed from published/observed information only.

Possible host/device signals include CPU load, memory, temperatures/fans where the operating system exposes them, and discovered camera/audio/display/printer capabilities. Missing telemetry stays unknown.

**Availability does not equal authorization.** Camera, microphone and actuator capture/use remains permission/capability gated even when a device is discovered.

## Release workspace

Release readiness separates engineering verification from scientific evidence. CI success, type checks, security checks and deterministic tests are engineering gates. Experimental claims require valid evidence artifacts and cannot be promoted merely because the implementation tests pass.

## File and documentation tools

The dashboard includes repository-scoped research/docs file viewing and editing functions for supported text and document formats. File operations are explicit server endpoints and are not part of the SNN execution loop. Path traversal and unsupported binary writes are rejected.

For the complete endpoint inventory see [`API_REFERENCE.md`](API_REFERENCE.md).

## Security

### Loopback default

The supported default is:

```text
http://127.0.0.1:8765
```

The dashboard contains runtime, structural and file-management capabilities. Do not expose port `8765` directly to the public Internet.

### Trusted LAN

Binding to `0.0.0.0` is appropriate only for a trusted, firewall-restricted private network. Restrict inbound access to the intended subnet and operator devices.

### Internet access

For remote Internet access keep Brain-5D bound to loopback and place an authenticated TLS reverse proxy in front of it. The repository includes `deploy/Caddyfile.internet.example` as a starting point. Production multi-user access should use stronger identity controls/MFA rather than treating Basic Auth as a complete authorization system.

## Start

Integrated runtime + dashboard:

```bash
python -m src.main --config configs/poc_config.yaml
```

Windows convenience launcher:

```powershell
.\start.ps1
```

Dashboard-only entry points remain available for inspection workflows, but the integrated launcher is the canonical path when live runtime state is required.

## Architecture boundary

```text
Runtime / Research / Storage / Embodiment
              |
       published contracts
              v
       DashboardStateStore
              |
      domain API services
              |
              v
        Browser workspaces

Presentation shell/experience: navigation + rendering only
Domain services: explicit reads/writes with validation
Scientific evidence: separate research/evidence contracts
```

See also:

- [`../02-architecture/ARCHITECTURE.md`](../02-architecture/ARCHITECTURE.md)
- [`API_REFERENCE.md`](API_REFERENCE.md)
- [`DASHBOARD_CONTROL_PLANE.md`](DASHBOARD_CONTROL_PLANE.md)
- [`../02-architecture/EMBODIMENT_REAL_BODY.md`](../02-architecture/EMBODIMENT_REAL_BODY.md)
- [`../../research/README.md`](../../research/README.md)
