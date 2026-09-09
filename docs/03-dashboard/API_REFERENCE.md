# Dashboard API Reference

The local dashboard exposes JSON APIs on the configured loopback or trusted-LAN
address. Read endpoints report the shared dashboard state; mutation endpoints
are explicit operator or experiment commands.

## Runtime and Health

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/healthz` | Process liveness check. |
| `GET` | `/api/state` | Current store-driven dashboard snapshot. |
| `GET` | `/api/config` | Effective configuration path, digest and runtime configuration. |
| `GET` | `/api/health` | Aggregated component health and problems. |
| `GET` | `/api/components` | Component status inventory. |
| `GET` | `/api/components/{name}` | One component status. |
| `GET` | `/api/parameters` | Public parameter schemas. |
| `GET` | `/api/parameters/{name}` | One parameter schema and current value. |

## Pending Parameters

Parameter changes are staged before application:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/parameters/pending` | List staged changes. |
| `POST` | `/api/parameters/{name}/pending` | Stage one parameter value. |
| `POST` | `/api/parameters/pending/apply` | Apply staged runtime-mutable changes. |
| `POST` | `/api/parameters/pending/save-profile` | Apply and persist a profile. |
| `POST` | `/api/parameters/pending/cancel` | Discard staged changes. |

## Experiment State

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/experiment/mode` | Current state mode and active session. |
| `POST` | `/api/experiment/mode` | Set the dashboard session mode. Current API values are `operator`, `experiment` or compatibility `debug`; the persisted runtime state axis uses `dev`. |
| `GET` | `/api/experiment/sessions` | Session history. |
| `POST` | `/api/experiment/session/start` | Start a bounded, documented session. |
| `POST` | `/api/experiment/session/stop` | Stop the active session. |
| `POST` | `/api/experiment/note` | Add a note to the active session. |
| `GET` | `/api/experiment/workflow/catalog` | List registered workflows. |
| `POST` | `/api/experiment/workflow/run` | Run a validated bounded workflow. |

Experiment execution is isolated from the persistent operator state. A
workflow cannot promote state automatically.

## Profile & Identity

Profiles are bounded technical configuration identities. They are separate from
the `.b5d` snapshot and runtime checkpoint, and do not imply psychological or
conscious identity.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/profiles` | List bounded registry metadata. |
| `GET` | `/api/profiles/current` | Current persisted technical identity. |
| `GET` | `/api/profiles/{id}` | Validate and return one profile. |
| `POST` | `/api/profiles` | Create a schema-validated profile. |
| `PUT` | `/api/profiles/{id}` | Create a revision from explicit changes. |
| `POST` | `/api/profiles/{id}/load` | Load profile-only or profile plus bound state. |
| `POST` | `/api/profiles/{id}/save-state` | Bind an existing snapshot by digest. |
| `POST` | `/api/profiles/{id}/clone` | Create a new profile with lineage. |
| `POST` | `/api/profiles/{id}/archive` | Archive a profile and clear active assignment safely. |
| `GET` | `/api/profiles/{id}/history` | Revision and parent history. |
| `GET` | `/api/profiles/{id}/snapshots` | Snapshot references, not snapshot contents. |
| `GET` | `/api/profiles/{id}/export` | Download bounded ZIP export. |
| `POST` | `/api/profiles/import` | Import a base64 ZIP after security/digest validation. |
| `DELETE` | `/api/profiles/{id}` | Hard delete only when no active/provenance guard applies; otherwise archive. |

## Embodiment Read APIs

These endpoints are read-only and publish only measured or discovered state:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/embodiment/state` | Environment status and latest metrics. |
| `GET` | `/api/embodiment/metrics` | Latest embodiment metrics. |
| `GET` | `/api/embodiment/history?limit=N` | Retained metrics history, bounded by `limit`. |
| `GET` | `/api/embodiment/connections` | Discovered connections and authorization state. |

Device discovery does not authorize or activate a connection. Writable adapter
execution requires the fail-closed embodiment safety boundary: availability,
explicit authorization, capability permission, rate limit, audit record and
emergency-stop/override checks.

## Contract Rules

- JSON errors use an HTTP error status and an `error` field.
- `GET` endpoints do not mutate runtime state.
- Experiment and operator state are separate lifecycle boundaries.
- `compute` observability may suppress rendering, but mandatory health,
  provenance and safety evidence remain available.
