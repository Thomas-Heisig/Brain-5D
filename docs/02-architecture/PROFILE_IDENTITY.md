# Profile & Identitaet

## Status

**Holistic Wesen profile: implemented.**

Senses, learning parameters, morphology, actuators, gateway/MSBA defaults,
memory declarations, self-model configuration, resources and safety are stored
as a bounded technical profile. Profile save/load/clone/import/export,
revision history, lineage and snapshot binding are implemented. Autonomous
profile mutation remains **locked / future research**.

A profile is a persistent technical identity. It is not evidence of a
psychological identity, personality, subjective continuity or consciousness.

## Separation of state

| Layer | Contents | Storage |
| --- | --- | --- |
| Profile | configuration, declared capabilities, limits, provenance | `profiles/<id>/profile.json` |
| Snapshot | current neuron/synapse state and tick | existing `.b5d` snapshot |
| Checkpoint | RNG, queues, traces and continuation state | existing checkpoint sidecar |
| Registry | bounded profile metadata and digest | `profiles/index.json` |
| Lineage | revisions, parent and change reasons | `profiles/<id>/revisions/` |

Large spike histories, synapse lists, raw experiment data and structural
journals never enter `profile.json`.

## Schema and digest

The current schema is version `1`. A profile contains `runtime`, `neural_core`,
`learning`, `senses`, `actuators`, `morphology`, `gateway`, `memory`,
`self_model`, `resources`, `safety`, `provenance`, `snapshot_binding` and
`compatibility`. JSON is canonicalized with sorted keys and hashed with
SHA-256. The digest excludes only its own `provenance.profile_digest` field.

Gateway active weights remain outside the profile. The gateway configuration is
always experiment-only and its productive lock cannot be disabled by imported
data. Autonomous profile mutation is likewise fail-closed.

## Lifecycle and safety

Profiles can be `active`, `inactive`, `archived`, `incompatible` or
`corrupted`. Loading a profile persists the active status and deactivates the
previous identity. Loading with state requires a snapshot binding; profile-only
loading deliberately does not silently reinitialize the runtime.

Hard deletion is blocked for an active profile and for profiles with snapshot
provenance. Archive is the normal disposal path. Writes use a temporary file,
flush/fsync and atomic replacement. ZIP imports reject traversal, backslashes,
directories, oversized members, duplicate identity IDs and digest mismatches.
Imported actuator declarations never activate external devices.

## API

- `GET /api/profiles` and `GET /api/profiles/current`;
- `GET /api/profiles/{id}`;
- `POST /api/profiles`;
- `PUT /api/profiles/{id}`;
- `POST /api/profiles/{id}/load` with `with_state: true|false`;
- `POST /api/profiles/{id}/save-state`;
- `POST /api/profiles/{id}/clone`;
- `GET /api/profiles/{id}/history` and `/snapshots`;
- `GET /api/profiles/{id}/export`;
- `POST /api/profiles/import` with a bounded base64 ZIP;
- `DELETE /api/profiles/{id}` where archive/provenance rules still apply.

Runtime application is an explicit boundary. With a live RuntimeController,
profile-only loading pauses and applies the supported runtime pacing settings.
Profile-plus-state loading reports `runtime_applied: false` until the canonical
snapshot restore hook is connected; no partial neural-state mutation is claimed.

## Reproducibility

Experiment manifests should bind `profile_id`, revision, profile digest and
snapshot digest. This identifies exactly which technical configuration and
state were studied without treating the profile as scientific evidence.
