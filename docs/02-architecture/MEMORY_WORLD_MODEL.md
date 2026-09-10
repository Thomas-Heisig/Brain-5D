# Memory, World Model and Behavior Profile

## Status

The first bounded implementation is **implemented** and its focused technical
checks are **verified**. It is not scientific evidence for memory, world-model
understanding, personality, consciousness or subjective experience.

## Ownership and data flow

`ExperienceEngine` is the only runtime integration point. Before an authorized
environment action is executed, it gives the observation-only
`TransitionWorldModel` the current `SensorFrame` and candidate action. The
model sees no hidden environment state and no target observation. After the
environment returns, the engine writes an `EpisodeRecord`, updates the model,
and stores a separate `PredictionRecord` containing the later comparison.

The SNN remains the primary learner. `MemoryStore`, `TransitionWorldModel` and
`BehaviorProfile` cannot write neurons, synapses, rewards, safety policy or
canonical snapshots. The Language Organ, dashboard and research assistant are
not granted these write paths.

| Component | Owns | Reads | Writes | Nature |
| --- | --- | --- | --- | --- |
| `MemoryStore` | bounded working/episodic/prediction records | explicit recall requests | its own JSON state | storage |
| `TransitionWorldModel` | bounded transition aggregates | frame and action before feedback | its own model state after feedback | adaptive experimental model |
| `BehaviorProfile` | initial, situational and slow disposition values | candidate actions and task outcome | its own bounded update log | algorithmic behavior controller |
| `ExperienceEngine` | ordering of the cycle | existing sensor/network/environment contracts | no canonical SNN state | integration boundary |

Memory read and write controls are independent. Disabled memory does not reset
the SNN and does not disable SNN plasticity. Retention and capacity eviction
apply only to experimental memory; research DATA, AIRR and EVID artifacts are
not deleted.

## State contracts

Memory state is schema version 1, owned by `memory.layer`, and contains run ID,
capacity configuration, controls, episodes, predictions and an integrity
digest. The coupled integration state is schema version 1, owned by
`memory.world_model.integration`, and additionally contains the world-model
state, episode ID and enabled flag. Profile state is schema version 1, owned by
`profiles.behavior`, and contains the three profile levels, update rate and an
update log. All writes use a temporary file, flush/fsync and atomic replacement.
Unknown schemas, invalid owners and digest mismatches fail closed; no
empty-memory or fresh-model fallback is used.

The coupled JSON state is logically separate from `.b5d` and checkpoint state.
An enclosing runtime snapshot integration must call both contracts at the same
simulation boundary before claiming pause/resume equivalence.

## Predictor and controls

The initial predictor is one-step and bounded. Its learned arm aggregates
observed successor fields by `(modality, sensor payload, action)`; the cold-start
reference is explicitly labelled `persistence_reference`. Numeric error is
mean absolute error and categorical error is mismatch rate. This is a
technical predictor, not a causal model. Action selection is not driven by the
world model in this stage.

`BehaviorProfile` is not an LLM role prompt. It can influence behavior only
when a decoder explicitly returns a tuple of candidate `ActionCommand` values.
Selection is deterministic from simulation tick and bounded exploration. Failed
or successful task outcomes update the slow disposition with a disclosed
bounded exponential rule and record before/after values, tick, trigger and
source. Estimated observer values are not fed back into the profile.

## Verification boundary

Focused checks cover the real ExperienceEngine path, independent memory
switches, capacity/retention, persistence integrity, target-state leakage
boundary, profile update provenance and the existing read-only dashboard
endpoint `/api/cognition/state`. They are engineering-screen checks.
Delayed-information task performance, matched no-memory controls, frozen and
adaptive world-model comparisons, held-out episodes and independent replication
remain open research work.
