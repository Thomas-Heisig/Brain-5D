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

The dashboard experience layer provides unified workspace navigation, live runtime context, command palette, focus/keyboard navigation where supported, responsive desktop/tablet/mobile layouts, light/dark presentation contracts, reduced-motion support and explicit rendering of unknown/unavailable values.

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
- the visible membrane/body boundary follows the currently observed body nodes.

A camera, microphone, weather/network source, display, speaker, printer or external robot endpoint is shown only when published connection data supports it. Missing capabilities remain unavailable rather than appearing as demo anatomy.

### Adaptive organism v2

The current presentation enhancement adds a bounded force-directed body layout. Core, internal, sensor, actuator and generic connection nodes are positioned according to their functional role while repelling each other to avoid a rigid circular anatomy.

The body membrane is derived from a padded convex hull around the current node set. As devices appear or disappear, the visible body envelope can grow, retract or change asymmetrically.

External sources can appear as satellites outside the membrane. Sensor and actuator paths are visually distinct; actuator availability never implies authorization.

### Camera and focus

The body stage now has a real presentation camera:

- pointer-centered wheel zoom;
- pointer drag to pan;
- bounded zoom range;
- double-click reset;
- focus fading for non-selected body nodes.

These camera operations affect only rendering.

### Delayed self-model

The self-model uses a bounded in-browser frame ring buffer. When measured loopback latency is available, the mirror chooses the body frame closest to `now - latency`. It therefore renders an actually earlier observed morphology rather than only dimming or delaying the current frame.

If no measured latency exists, the view remains explicitly uncalibrated. Recurrence and loopback are not evidence of consciousness or self-awareness.

### Morphology history

Morphology signatures are stored as bounded browser-local snapshots when the observed body shape changes. A timeline scrubber can inspect earlier snapshots in the self-model surface.

This is operator history only. Browser `localStorage` is not research DATA/EVID and must not be cited as scientific evidence.

### Differentiated visual states

The presentation layer can distinguish reported/derived states such as:

- thermal pressure;
- generic resource pressure;
- sensor loss;
- actuator failure;
- network isolation;
- recovery;
- unknown telemetry.

These are visualization states, not emotion or illness claims.

### Causal tracer

The UI can surface event/decision/action/receipt identifiers already present in observed event text and use them as a visual tracer label. It never manufactures missing identifiers. A highlighted path remains a debugging/inspection aid unless a protocol and accepted evidence establish causality.

Detailed contract: [`../02-architecture/WESEN_ADAPTIVE_BODY.md`](../02-architecture/WESEN_ADAPTIVE_BODY.md).

## Embodiment workspace

Embodiment is intentionally simpler than Wesen. It is the technical surface for available real/simulated sensors, actuators, permissions, connection state and body-boundary configuration.

Possible host/device signals include CPU load, memory, temperatures/fans where exposed, storage/network values and discovered camera/audio/display/printer capabilities. Missing telemetry stays unknown.

**Availability does not equal authorization.** Discovery does not grant capture or actuation permission.

## Research workspace

Research connects to questions/hypotheses/claims/sources registries, experiment creation/execution, manifests/reports/DATA, evidence/integrity status, research file browser/editor, post-hoc AI analysis where configured and the Learning Preparation Studio.

Research AI remains observing/interpreting/proposal-only by default.

## Release access

Release readiness separates engineering verification from scientific evidence. The Release/Gate surface remains available, but is opened from the dashboard footer instead of occupying a primary navigation tab.

CI success, typing, security and deterministic tests are engineering gates. Experimental claims require valid evidence artifacts.

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
