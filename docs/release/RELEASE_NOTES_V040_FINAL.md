# Brain-5D v0.4.0 final - Release Notes

v0.4 establishes the persistence contract required for all later learning and
self-regulation work.

Delivered capabilities:

- `.b5d` snapshot format with optical and restart-capable modes.
- Delta journal, CRC validation, commit markers and crash recovery.
- Runtime storage capture, async queue, storage telemetry and compaction.
- Deterministic restore-and-continue through Runtime Checkpoint V3.
- Lazy snapshot heatmaps and local read-only operator dashboard.
- Embodiment interfaces as a future-facing architectural boundary.
- Strict JSON API contracts for dashboard endpoints.

The frozen `.b5d` V1 format is not modified by v0.5. Exact floating-point runtime
state lives in the checkpoint sidecar so snapshot compactness and deterministic
continuation remain separate concerns.
