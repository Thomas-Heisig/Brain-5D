# Dashboard Control Plane

## Purpose

The control plane turns the Brain-5D dashboard from a passive observatory into an
operator console while preserving deterministic core execution.

## API

### GET `/api/control`

Returns runtime and optional self-organization state.

### POST `/api/control`

Examples:

```json
{"action":"step","ticks":10}
```

```json
{"action":"run","loop_size":100}
```

```json
{"action":"pause"}
```

```json
{"action":"configure","loop_size":500,"delay_ms":0.2}
```

```json
{"action":"snapshot"}
```

```json
{"action":"self_organization","enabled":true,"dry_run":true}
```

## Concurrency model

Only the `RuntimeController` worker executes simulation ticks. The HTTP server
never steps the network from request-handler threads. This avoids overlapping
`network.step()` calls and keeps persistence, homeostasis and learning hooks in a
single execution order.

## Canonical one-tick path

`src/main.py` should expose one function that performs exactly one existing
simulation tick including all hooks and telemetry. Both batch mode and the
interactive controller must reuse that path rather than duplicate it.

## Dashboard integration

Add the contents of `static/control-panel.fragment.html` into the existing control
area of `index.html`, load `control-panel.css`, then load `control-panel.js` after
the normal dashboard script. The control panel polls state at 500 ms and sends
commands only on operator actions.

## Planned alpha.4 extension

The same control service can later expose:

- controlled stimulus injection,
- checkpoint restore selector,
- learning enable/disable gates,
- experiment presets,
- self-organization proposal approval,
- live loop-rate targets and back-pressure.
