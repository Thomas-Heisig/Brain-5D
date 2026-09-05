# Wesen — Adaptive Machine-Native Body View

## Status

`Wesen` is the dedicated real-time body visualization in the Brain-5D dashboard. It is a **read-only presentation surface** over observed runtime, embodiment and connection state. It does not run learning, issue language output, authorize actuators, or fabricate missing telemetry.

The page intentionally avoids biological-human body assumptions. Its morphology is derived from the currently observed machine body: sensors, host interoception, the SNN core, actuator endpoints, feedback paths and the changing body boundary.

## Separation from Embodiment

- **Embodiment** is the technical connection/configuration surface for sensors, devices, actuators, permissions and body boundaries.
- **Wesen** is the live visual projection of the body state exposed by those contracts.
- **Release** is no longer a primary workspace; its legacy gate surface is opened from the footer.
- **Network** is no longer a primary user-facing workspace. Network state remains available through domain APIs and inspector/research surfaces where needed.

## Data sources

The current implementation reads only:

- `GET /api/status`
- `GET /api/embodiment/state`
- `GET /api/embodiment/connections`

Polling currently runs at 750 ms. Unknown/missing values remain `—`, `unknown` or equivalent. The UI must never replace missing measurements with plausible-looking constants.

## Dynamic morphology

The body is generated from observed connection inventory instead of fixed coordinates.

Core body components are:

1. **SNN core** — neural dynamics.
2. **Interoception** — host/resource and regulatory observations.
3. **Feedback** — observed return/loopback context.
4. **Body boundary** — current discovered connection envelope.

Discovered connections are classified for visualization as sensor endpoints, actuator endpoints or generic body connections when direction/capability cannot be determined. Examples include camera, microphone/audio, weather/network inputs, display, speaker, printer or external robotics where the embodiment API actually reports them. If no sensor or actuator is reported, the UI renders an explicitly unavailable placeholder instead of inventing a device.

### Force-directed body layout

The adaptive organism v2 layer places body nodes with a bounded force-directed layout:

- the SNN core is attracted to the body center;
- internal/interoceptive nodes remain relatively close to the core;
- sensor endpoints are biased toward the sensory boundary;
- actuator endpoints are biased toward the motor/output boundary;
- dense sensor/actuator sets are distributed over multiple radii;
- same-class nodes use stronger repulsion so large device inventories do not collapse into one unreadable cluster.

The layout is presentation-only and does not alter neural topology or embodiment state.

### Convex-hull membrane

The visible body membrane is recalculated as a padded convex hull around current body nodes. A device appearing or disappearing can therefore change the visible body envelope. The membrane is a visualization of the currently observed connection boundary, not an authoritative authorization boundary.

## Icon-first visual contract

Dense machine inventories can contain dozens of endpoints. Rendering full device names and values inside each SVG node produces unavoidable overlap, so the body follows an **icon-first** rule:

- the body itself shows symbols and status rings rather than long text;
- device classes receive stable semantic symbols, including camera, microphone, speaker, display, GPU, network, USB, storage, printer and robotics;
- complete device names and values remain available through native SVG tooltips and the right-hand inspector;
- body metric pins are hidden by default in the dense overview rather than overlapping neighboring nodes;
- selected/hovered/focused nodes receive stronger halo and stroke emphasis;
- every body node remains keyboard-focusable and activatable with Enter/Space;
- a horizontally scrollable icon dock provides guaranteed mouse/keyboard access to every discovered endpoint even if a dense graph, current pan/zoom position or viewport size makes the corresponding body node difficult to reach.

The icon dock is an accessibility/navigation surface only. It does not create additional body state or duplicate devices in the model.

## Sensor and actuator differentiation

Sensor and actuator branches are deliberately rendered as different functional endpoint types. Sensor branches represent available input paths; actuator branches represent available output paths. An actuator being displayed as available never implies permission to use it.

External services or sources such as network, weather, camera or audio can be represented as **environment satellites** outside the membrane. Satellites are also icon-first and expose their labels through tooltips rather than permanent text labels.

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

The **Kausalpfade** mode can emphasize paths and consume event/action/decision/receipt identifiers when such identifiers are already present in displayed event data. The UI does not invent missing IDs. A path may only be described as experimentally causal when backed by an intervention/outcome protocol and corresponding receipts/evidence.

## Self-model / delayed mirror

The Self-Model panel renders a small copy of the same morphology rather than a generic second body. The adaptive organism layer maintains a bounded in-browser frame ring buffer. If a loopback latency is reported, the mirror selects the frame closest to `now - latency` instead of merely applying a visual delay to the current frame.

If no measured loopback latency exists, the mirror remains explicitly uncalibrated. Recurrence and loopback visualization must not be labelled proof of consciousness, self-awareness or subjective self-recognition.

## Recurrence trend

When a recurrence metric is published, the page retains the last 100 observed samples for a session-local mini-chart. The chart shows metric evolution only. Increasing recurrence means increasing measured recurrence under that metric definition; it does not by itself mean increasing consciousness.

## Morphology history and timeline

The browser records bounded morphology snapshots when the body signature changes. The current v2 implementation stores this operator history in browser `localStorage` and exposes a scrubber that can render an earlier body snapshot in the delayed/self-model surface.

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

The current body view remains browser-native SVG/CSS/JavaScript. Libraries such as `PyBullet`, `vedo` or `viser` may be evaluated later for specialized 3D/operator experiments, but they are intentionally not required for the primary body view:

- `PyBullet` is a physics/simulation engine and would risk coupling presentation physics to scientific/runtime semantics;
- `vedo` is useful for Python-side 3D rendering but would add a separate rendering process for a view that currently needs lightweight browser interaction;
- `viser` is suitable for interactive 3D scenes but would introduce another server/UI dependency.

A future 3D renderer should consume the same read-only body-view contract and must not become an alternative source of runtime or scientific state.

## Terminology

Technical strings are centralized in the organism layer to keep the internal semantics neutral. Preferred terms include:

- `SNN-Kern`
- `Adaptive Regelstruktur`
- `Sensor-Endpunkt`
- `Aktor-Endpunkt`
- `Interozeption`
- `Umweltquelle`
- `Rückkopplung`

The product-facing workspace may still be named `Wesen`, but internal technical language must avoid unsupported claims such as consciousness, awareness or biological equivalence.

## Scientific integrity rules

1. No fabricated fallback telemetry.
2. Observed, derived, unknown and scientifically established causal claims remain distinct.
3. Availability never implies actuator authorization.
4. The view is read-only; no hidden `/api/control` or actuator write is issued.
5. Recurrence/loopback is not equated with consciousness.
6. Dashboard animation is presentation, not experimental evidence.
7. Browser-local morphology history is not DATA/EVID.
8. Causal tracer labels use only identifiers already present in observed events.
9. Icon/tool-tip/dock presentation never changes body state.
10. Scientific claims must continue through DATA/EVID and the research integrity gates.
