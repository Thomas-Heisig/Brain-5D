# Brain-5D Embodiment Foundation

## Purpose

Brain-5D treats embodiment as a perception-action loop, not as a requirement
for one specific physical robot.  An environment may be simulated, physical,
digital, or hybrid.  The common contract is:

`observation -> Brain-5D processing -> bounded action -> environment feedback`

Alpha.7 introduces only the typed architecture boundary.  It does **not** grant
unbounded browser, operating-system, network, or physical-device control.

## Modules

- `src/embodiment/sensor.py`: sensor adapter protocol;
- `src/embodiment/actuator.py`: actuator adapter protocol;
- `src/embodiment/environment.py`: reset/step environment contract;
- `src/embodiment/registry.py`: typed adapter factory registry;
- `src/embodiment/agent.py`: explicit-action environment loop;
- `src/embodiment/models.py`: immutable observations, actions and metrics.

## Design rules

1. The neural core has no direct dependency on cameras, microphones, browsers,
   motors, or remote APIs.
2. External actions remain explicit and bounded.
3. Every future writable adapter needs permission, audit, timeout, and resource
   budgets before production use.
4. Deterministic simulated environments are implemented before uncontrolled
   physical or digital environments.
5. Dashboard embodiment metrics are read-only in alpha.7.

## Dynamic body boundary

Brain-5D does not equate network reachability with body ownership. Its body is
the changing graph of resources whose state can be perceived, whose use is
authorized, whose effects can be observed, and whose causal model has been
integrated. `src/embodiment/connections.py` represents this boundary.

Every `ConnectionDescriptor` records:

- stable identity, kind, modalities and capabilities;
- relationship class: `perceivable`, `reachable`, `usable`, `controllable`,
  `integrated`, or `embodied`;
- observed status independently from `authorized` and `active`;
- explicit permissions, latency, energy demand and hazard level;
- provenance and a human-readable discovery or adapter message.

The default catalog contains compute, storage, LAN, internet route, camera,
microphone, location/environment sensing, Web/API and database data sources,
messaging, display, audio output, printing and robotics. It is open-ended:
configured adapters can register additional descriptors without changing the
neural core.

Read-only system discovery currently detects local compute/filesystem, local
network addresses, an outbound IP route, and platform camera, microphone,
audio-output and printer devices. Detection never opens a media stream, sends
data, prints, or moves hardware. Discovered entries are `reachable`, but remain
`authorized=false` and `active=false` until a permission-bounded adapter is
explicitly composed.

## Dashboard contract

The dashboard exposes the published state without creating an environment or
inventing sensor, actuator, latency, gain, or history values:

- `GET /api/embodiment/state`: current metrics, configuration status and the
   six closed-loop phases Environment → Sensor → Encoder → SNN → Decoder →
   Actuator;
- `GET /api/embodiment/metrics`: the latest measured `EmbodimentMetrics`;
- `GET /api/embodiment/history?limit=N`: snapshots already retained by the
   thread-safe `DashboardStateStore`.
- `GET /api/embodiment/connections`: discovered and configured body
   connections, capabilities, relationship class, health and authorization.

When no adapter is configured, `available` is false, the loop reports
`unconfigured` / `unavailable` / `not_reported`, history is empty, and detail
payloads are null. This is a scientific boundary, not a visual fallback.

The Embodiment workspace visualizes the causal loop and current episode,
reward, action, text-input and history state. Its central living-system map
uses the Brain-5D creature asset to place every currently published dashboard
source into one body:

- neural body: `system`, `network`, `spikes`;
- regulation and metabolism: `homeostasis`;
- plasticity and reward processing: `learning` and `embodiment`;
- perception and action boundaries: `embodiment` state/details/history;
- signal transformation, language and intake: `signal_metrics`,
  `language_organ`, `knowledge_intake`;
- growth and persistence: `structural`, `storage`;
- vital state: runtime status and component integration state.

Breathing, signal particles, synchrony rings and glow intensity are visual
encodings driven by published activity, energy and synchrony values. They are
not additional measurements. Missing values remain `unavailable`,
`not published`, or `—`; the image never supplies telemetry. Animation stops
under `prefers-reduced-motion`.

Manual actions remain disabled until a concrete, permission-bounded
`EnvironmentAdapter` is composed into the runtime.

## Roadmap role

The interfaces were introduced in v0.5.0-alpha.7 so later alpha releases can design
self-regulation and learning environments against a stable future boundary.
Production sensor/action adapters remain a v0.8 milestone.
