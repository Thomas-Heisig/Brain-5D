# Brain-5D Operator & Research Dashboard

## Purpose

The dashboard is the operator and research interface for Brain-5D. It visualizes published state, exposes explicit operator controls and connects research workflows without becoming an alternative simulation engine.

The current UI is a responsive, full-width workspace system with one shared visual language. Presentation layers do not manufacture scientific state and do not acquire hidden runtime authority.

## Primary navigation

The current user-facing primary workspaces are:

1. **Overview** — system state, runtime context and key health/telemetry.
2. **Control** — explicit runtime actions, pacing/tick controls and bounded operator control surfaces.
3. **Research** — experiments, registries, reports, research files and bounded AI-assisted analysis/preparation.
4. **Settings** — runtime-visible configuration and pending parameter workflow.
5. **Wesen** — adaptive, read-only live body visualization derived from observed runtime/embodiment/connection state.
6. **Embodiment** — technical sensor/device/actuator/body-boundary configuration and observation.

`Network` is no longer a primary user-facing workspace. Network state remains available through published domain contracts and relevant research/inspection surfaces.

The legacy Release/Gate surface is no longer in the primary navigation. It is opened from the footer button.

## Operator experience

The dashboard experience layer provides:

- unified workspace navigation;
- live runtime context;
- command palette;
- focus/keyboard navigation where supported;
- responsive desktop/tablet/mobile layouts;
- light/dark presentation contracts;
- reduced-motion support;
- explicit rendering of unknown/unavailable values.

The common shell is presentation-only. Runtime actions remain in typed/domain control paths.

## State integrity

The dashboard follows non-negotiable display rules:

- `0` means measured zero only when the source measured zero;
- missing values remain unknown/unavailable;
- stale telemetry is distinguishable from live telemetry where age is available;
- device discovery is not device authorization;
- an accepted action is not proof of an observed effect;
- UI logs are not scientific provenance;
- AI text is interpretation/proposal, not empirical measurement;
- visual connectivity is not automatically causal evidence.

## Runtime controls

The runtime control service supports bounded commands such as start/resume, pause, stop, single-step, exact tick runs, snapshots and configuration changes where the underlying capability exists.

Wall-clock target Hz is separate from simulation `dt`. Increasing target Hz must not silently alter neural-time semantics.

## Wesen workspace

`Wesen` is the dedicated live body view. It reads the published status, embodiment state and connection inventory. It does not send control commands, run learning, generate language output or issue actuator writes.

The body is machine-native rather than human-shaped:

- SNN core is the central neural component;
- host/system telemetry is interoception;
- discovered sensor endpoints form input branches;
- discovered actuator endpoints form output branches;
- feedback/loopback is represented separately;
- the visible membrane/body boundary is recalculated from observed body nodes.

A camera, microphone, weather/network source, display, speaker, printer or external robot endpoint is shown only when the published connection data actually supports it. Missing capabilities remain unavailable rather than appearing as demo anatomy.

The view supports:

- dynamic sensor/actuator morphology;
- node inspection;
- live data pins;
- session-local morphology history;
- recurrence trend for up to 100 observed samples;
- event filtering;
- wheel zoom and whole-body reset;
- signal animation;
- causal-path emphasis;
- delayed self-model using the same current morphology.

The delayed mirror visualizes recurrence/loopback structure only. It is not evidence of consciousness, self-awareness or subjective self-recognition.

Detailed contract: [`../02-architecture/WESEN_ADAPTIVE_BODY.md`](../02-architecture/WESEN_ADAPTIVE_BODY.md).

## Embodiment workspace

Embodiment is intentionally simpler than Wesen. It is the technical surface for available real/simulated sensors, actuators, permissions, connection state and body-boundary configuration.

Possible host/device signals include CPU load, memory, temperatures/fans where exposed, storage/network values and discovered camera/audio/display/printer capabilities. Missing telemetry stays unknown.

**Availability does not equal authorization.** Discovery does not grant capture or actuation permission.

## Causal-path display

The Wesen UI can emphasize candidate sensor → SNN → actuator → feedback paths. This is a visualization aid for debugging and experiment inspection.

A highlighted path is not automatically a scientifically established causal path. Causal claims require an intervention/outcome protocol, receipts and accepted evidence.

## Self-model display

The Self-Model panel renders a scaled copy of the current body topology and uses reported loopback latency/recurrence when available. Its purpose is to make measured return structure inspectable.

The dashboard must not translate rising recurrence into claims that the system is becoming "more conscious".

## Research workspace

Research connects to:

- questions/hypotheses/claims/sources registries;
- experiment creation/execution;
- manifests, reports and DATA;
- evidence/integrity status;
- research file browser/editor;
- post-hoc AI analysis where explicitly configured;
- Learning Preparation Studio.

Research AI remains observing/interpreting/proposal-only by default.

## Release access

Release readiness separates engineering verification from scientific evidence. The Release/Gate surface remains available, but is opened from the dashboard footer instead of occupying a primary navigation tab.

CI success, typing, security and deterministic tests are engineering gates. Experimental claims require valid evidence artifacts.

## File and documentation tools

Repository-scoped research/docs file operations use explicit server endpoints and are not part of the SNN execution loop. Unsupported paths/writes fail closed.

For endpoint inventory see [`API_REFERENCE.md`](API_REFERENCE.md).

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
        Browser workspaces
              |
      +-------+--------+
      |                |
 technical        adaptive live
 Embodiment          Wesen

Presentation never substitutes for DATA/EVID.
```

See also:

- [`../02-architecture/ARCHITECTURE.md`](../02-architecture/ARCHITECTURE.md)
- [`../02-architecture/WESEN_ADAPTIVE_BODY.md`](../02-architecture/WESEN_ADAPTIVE_BODY.md)
- [`API_REFERENCE.md`](API_REFERENCE.md)
- [`DASHBOARD_CONTROL_PLANE.md`](DASHBOARD_CONTROL_PLANE.md)
- [`../02-architecture/EMBODIMENT_REAL_BODY.md`](../02-architecture/EMBODIMENT_REAL_BODY.md)
- [`../../research/README.md`](../../research/README.md)
