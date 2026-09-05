# Wesen — Adaptive Machine-Native Body View

## Status

`Wesen` is the dedicated real-time body visualization in the Brain-5D dashboard. It is a **read-only presentation surface** over observed runtime, embodiment and connection state. It does not run learning, issue language output, authorize actuators, or fabricate missing telemetry.

The page intentionally avoids biological-human body assumptions. Its morphology is derived from the currently observed machine body: sensors, host interoception, the SNN core, actuator endpoints, feedback paths and the changing body boundary.

## Separation from Embodiment

- **Embodiment** is the technical connection/configuration surface for sensors, devices, actuators, permissions and body boundaries.
- **Wesen** is the live visual projection of the body state exposed by those contracts.
- **Release** is no longer a primary workspace; its legacy gate surface is opened from the footer.
- **Network** is no longer a primary user-facing workspace. Network state remains available through domain APIs and other inspector/research surfaces where needed.

## Data sources

The current implementation reads only:

- `GET /api/status`
- `GET /api/embodiment/state`
- `GET /api/embodiment/connections`

Polling currently runs at 750 ms. Unknown/missing values remain `—`, `unknown` or equivalent. The UI must never replace missing measurements with plausible-looking constants.

## Dynamic morphology

The body map is generated from observed connections on every refresh.

Core body components are:

1. **SNN core** — neural dynamics.
2. **Interoception** — host/resource and regulatory observations.
3. **Feedback** — observed return/loopback context.
4. **Body boundary** — current discovered connection envelope.

Discovered connections are classified for visualization as:

- sensor endpoints;
- actuator endpoints;
- generic body connections when the direction/capability cannot be determined.

Examples include camera, microphone/audio, weather/network inputs, display, speaker, printer or external robotics where the embodiment API actually reports them. If no sensor or actuator is reported, the UI renders an explicitly unavailable placeholder instead of inventing a device.

The membrane/body envelope is recalculated from the current set of observed body nodes. Connecting or losing a device therefore changes the visible morphology.

## Adaptive state visualization

The presentation can react to observed state without writing back to the runtime. Current visual profiles include:

- stable observation;
- increased resource pressure;
- critical resource/thermal pressure;
- sensor loss/degradation when reported;
- actuator failure when reported;
- network isolation when reported.

The adaptive response may change membrane tension, body scale, emphasis and status styling. These visual changes are **derived display state**, not a claim that the SNN has an emotion or subjective experience.

## Interoception

Host telemetry is treated as machine-native interoception rather than merely a diagnostics sidebar. Where exposed, the view may show:

- CPU load;
- memory use/reserve;
- temperature;
- fan RPM;
- storage pressure;
- runtime target/achieved Hz;
- regulatory state.

Unsupported values remain unknown.

## Signals and causal paths

Animated signal markers indicate activity along currently rendered body paths. They are a visualization of observed availability/state and do not themselves prove a causal relationship.

The **Kausalpfade** mode highlights sensor/feedback/actuator paths that are candidates for an observed causal loop. A path may only be described as experimentally causal when backed by an intervention/outcome protocol and corresponding receipts/evidence. UI connectivity alone is not causal proof.

## Self-model / delayed mirror

The Self-Model panel renders a small copy of the **same current morphology**, rather than a generic second body. Its opacity is linked to an available recurrence measure and its caption uses the reported loopback latency when present.

This is a visualization of measured recurrence/return structure. It must not be labelled proof of consciousness, self-awareness or subjective self-recognition.

## Recurrence trend

When a recurrence metric is published, the page retains the last 100 observed samples for a session-local mini-chart. The chart shows metric evolution only. Increasing recurrence means increasing measured recurrence under that metric definition; it does not by itself mean increasing consciousness.

## Morphology history

The current browser session records changes in the observed body signature. This provides an operator-visible history of body-boundary changes such as devices appearing/disappearing. It is a UI observation history, not a persisted scientific artifact unless a research protocol stores the underlying source data separately.

## Interaction

The page supports:

- click a node to inspect its published primitive fields;
- mouse-wheel zoom of the body map;
- double-click/reset to restore the whole-body view;
- toggles for signals, connections, environment and causal-path emphasis;
- event filtering;
- reduced-motion support.

## Scientific integrity rules

1. No fabricated fallback telemetry.
2. Observed, derived, unknown and scientifically established causal claims remain distinct.
3. Availability never implies actuator authorization.
4. The view is read-only; no hidden `/api/control` or actuator write is issued.
5. Recurrence/loopback is not equated with consciousness.
6. Dashboard animation is presentation, not experimental evidence.
7. Scientific claims must continue through DATA/EVID and the research integrity gates.
