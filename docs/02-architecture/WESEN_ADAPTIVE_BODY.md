# Wesen — Adaptive Machine-Native Body View

## Status

`Wesen` is the dedicated real-time body visualization in the Brain-5D dashboard. It is a **read-only presentation surface** over observed runtime, embodiment and connection state. It does not run learning, issue language output, authorize actuators, or fabricate missing telemetry.

The current view is intentionally **body-like without claiming biological equivalence**. It uses a readable anatomy metaphor while preserving machine-native semantics.

## Separation from Embodiment

- **Embodiment** is the technical connection/configuration surface for sensors, devices, actuators, permissions and body boundaries.
- **Wesen** is the live visual projection of the body state exposed by those contracts.
- **Release** is no longer a primary workspace; its legacy gate surface is opened from the footer.
- **Network** is no longer a primary user-facing workspace. Network state remains available through domain APIs and inspector/research surfaces where needed.

## Read-only data sources

The Wesen stack reads only GET endpoints. Current sources include:

- `GET /api/status`
- `GET /api/embodiment/state`
- `GET /api/embodiment/connections`
- `GET /api/embodiment/metrics`
- `GET /api/embodiment/history?limit=24`
- `GET /api/embodiment/pipeline`
- `GET /api/live/io-flow`
- `GET /api/live/population`

The primary state loop remains 750 ms; the anatomy/empirical overlay refreshes independently at a bounded cadence. Unknown/missing values remain `—`, `unknown` or equivalent. The UI must never replace missing measurements with plausible-looking constants.

## Anatomy v3 — body-like machine-native representation

Anatomy v3 introduces a stable presentation scaffold so the organism is recognizable as a body without pretending to be human biology.

The current functional zones are:

1. **Sensory head zone** — camera, microphone, network/weather and other input endpoints cluster above the main body.
2. **Central SNN core** — the SNN is positioned in the upper torso/central control region.
3. **Torso interoception** — host/resource/regulatory observations occupy the inner body.
4. **Feedback/spine path** — recurrence and return-flow visualization runs through a central longitudinal structure.
5. **Actuator limb regions** — output endpoints extend laterally and downward into arm-/leg-like branches.
6. **Body boundary** — the outer membrane still reflects observed endpoint inventory and remains separate from the decorative anatomy scaffold.

These zones are **presentation semantics only**. They do not redefine neural topology, device authorization, anatomical homology or scientific interpretation.

### Layout ownership

Anatomy v3 is the sole owner of body-node coordinates while active. The earlier organism v2 force layout remains a fallback for environments where anatomy v3 is unavailable, but it no longer periodically overwrites anatomical positions.

This prevents visual jumping between a graph layout and the body-like layout.

## Icon-first visual contract

Dense machine inventories can contain dozens of endpoints. Rendering full device names and values inside each SVG node produces unavoidable overlap, so the body follows an **icon-first** rule:

- the body itself shows symbols and status rings rather than long text;
- device classes receive stable semantic symbols, including camera, microphone, speaker, display, GPU, network, USB, storage, printer and robotics;
- complete device names and values remain available through native SVG tooltips and the right-hand inspector;
- body metric pins are hidden by default in the dense overview rather than overlapping neighboring nodes;
- selected/hovered/focused nodes receive stronger halo and stroke emphasis;
- every body node remains keyboard-focusable and activatable with Enter/Space;
- a horizontally scrollable icon dock provides guaranteed mouse/keyboard access to every discovered endpoint even if the current pan/zoom position or viewport size makes the corresponding node difficult to reach.

The icon dock is an accessibility/navigation surface only. It does not create additional body state or duplicate devices in the model.

## Empirical overlay

The right-hand empirical panel consumes only backend-published observations. Where the endpoints expose matching fields, the view can show:

- neural active fraction;
- spike count;
- input flow;
- output flow;
- signal/observation quality;
- sensory integrity;
- resource pressure;
- continuity risk;
- recent embodiment-history count;
- current embodiment pipeline stage availability.

The overlay searches documented/typed response fields conservatively and renders `—` when a value is absent. It does not infer a missing quantity from unrelated data.

### Visual coupling of empirical state

Measured resource pressure, sensory integrity and continuity risk may subtly affect body presentation through CSS variables. This is a **derived display mapping** only. It does not feed state back into the SNN, homeostasis, device layer or reward path.

## Sensor and actuator differentiation

Sensor and actuator branches are rendered as distinct functional endpoint types. Sensor branches represent available input paths; actuator branches represent available output paths. An actuator being displayed as available never implies permission to use it.

External services or sources such as network, weather, camera or audio can be represented as environment satellites outside the membrane. Satellites are icon-first and expose labels through tooltips rather than permanent text labels.

## Adaptive state visualization

The presentation can react to observed state without writing back to the runtime. Current visual profiles include:

- stable observation;
- increased resource pressure;
- critical resource/thermal pressure;
- sensor loss/degradation when reported;
- actuator failure when reported;
- network isolation when reported;
- recovery when reported;
- unknown/unavailable telemetry.

Visual state changes may alter membrane emphasis, branch opacity, environmental satellites and endpoint styling. These are **derived display states**, not claims of emotion, illness, consciousness or subjective experience.

## Interoception

Host telemetry is treated as machine-native interoception rather than merely a diagnostics sidebar. Where exposed, the view may show CPU load, memory use/reserve, temperature, fan RPM, storage pressure, runtime target/achieved Hz and regulatory state. Unsupported values remain unknown.

## Signals and causal paths

Animated signal markers indicate activity along currently rendered body paths. They are a visualization of observed availability/state and do not themselves prove a causal relationship.

The Kausalpfade mode can emphasize paths and consume event/action/decision/receipt identifiers when such identifiers are already present in displayed event data. The UI does not invent missing IDs. A path may only be described as experimentally causal when backed by an intervention/outcome protocol and corresponding receipts/evidence.

## Self-model / delayed mirror

The Self-Model panel renders a small copy of the same morphology rather than a generic second body. The organism layer maintains a bounded in-browser frame ring buffer. If a loopback latency is reported, the mirror selects the frame closest to `now - latency` instead of merely applying a visual delay to the current frame.

If no measured loopback latency exists, the mirror remains explicitly uncalibrated. Recurrence and loopback visualization must not be labelled proof of consciousness, self-awareness or subjective self-recognition.

## Morphology history and timeline

The browser records bounded morphology snapshots when the body signature changes. The current implementation stores this operator history in browser `localStorage` and exposes a scrubber that can render an earlier body snapshot in the delayed/self-model surface.

This history is **not scientific persistence**. It is local operator state only. If morphology history is needed as research evidence, the source connection/body-boundary events must be persisted by a protocol-bound backend artifact.

## Camera and focus interaction

The body stage supports a real presentation camera:

- mouse-wheel zoom around the pointer position;
- pointer drag for pan;
- double-click reset;
- selected-node focus that fades non-selected nodes;
- bounded zoom limits.

Camera state affects rendering only and has no simulation meaning.

## Rendering technology boundary

The current body view remains browser-native SVG/CSS/JavaScript. Libraries such as `PyBullet`, `vedo` or `viser` may be evaluated later for specialized 3D/operator experiments, but they are intentionally not required for the primary body view.

A future 3D renderer should consume the same read-only body-view contract and must not become an alternative source of runtime or scientific state.

## Scientific integrity rules

1. No fabricated fallback telemetry.
2. Observed, derived, unknown and scientifically established causal claims remain distinct.
3. Availability never implies actuator authorization.
4. The view is read-only; no hidden `/api/control` or actuator write is issued.
5. Recurrence/loopback is not equated with consciousness.
6. Dashboard animation is presentation, not experimental evidence.
7. Browser-local morphology history is not DATA/EVID.
8. Causal tracer labels use only identifiers already present in observed events.
9. Icon/tool-tip/dock/anatomy presentation never changes body state.
10. Empirical-overlay values come only from backend observations and remain unknown if absent.
11. Scientific claims must continue through DATA/EVID and the research integrity gates.
