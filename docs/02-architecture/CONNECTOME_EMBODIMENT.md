# Connectome-informed embodiment: integration contract

Status: experiment-only development screens, 2026-09-09. No biological data imported.

The existing MHRN core, production gateways, interfaces and scientific history remain
canonical. This extension adds a bounded joint world and six native runners to the
existing operational protocol loader, Experiment Workflow, Science Runner and DATA-v2
pipeline. It does not introduce a replacement production runtime or second file viewer.

## Implemented paths

- `src/embodiment/joint_world.py`: finite, bounded one-joint mechanics and proprioception.
- `src/research/connectome_reference.py`: opt-in local sparse reference loader and synthetic graph controls.
- `src/research/connectome_embodiment.py`: real Izhikevich SNN, declared sensory encoder and fixed spike-to-torque decoder; separate boundary-state sidecar.
- `src/research/connectome_governance.py`: launch, design-byte integrity and evidence-promotion guards.
- `research/protocols/connectome.operational.json`: six executable contracts loaded alongside existing protocols; duplicate IDs fail closed.
- `research/protocols/CONNECTOME_EMBODIMENT_V1.json`: twelve studies, including six explicitly blocked advanced designs.
- `research/protocols/connectome.design-lock.json`: versioned design SHA-256 inventory, not retrospective confirmation.

## Run and verify

```bash
python scripts/check_connectome_integrity.py
python -m pytest -q tests/test_connectome_embodiment.py tests/test_exp21_operational_protocols.py
python scripts/run_connectome_smoke.py --output /tmp/mhrn-connectome-smoke
```

On Windows use a new Windows output path instead of `/tmp`. The output directory must
not exist. The smoke command copies canonical registries, protocols, ethics state and
configuration to an isolated research workspace, then uses the normal workflow.
Existing history is never overwritten. The command has no AI backend or network access.
A non-NORMAL ethics state still blocks it. A failed smoke attempt remains on disk;
retry under a new directory. Tests are development diagnostics, not accepted EVID.

The six protocol IDs are `embodied_closed_loop_v1`, `embodied_proprioception_v1`,
`embodied_perturbation_screen_v1`, `connectome_topology_screen_v1`,
`embodied_controller_attribution_v1`, and `embodied_timing_v1`.
Each executes all registered arms over at least three distinct seeds. A fail-closed
250000-neural-tick budget covers all arms/seeds and donor runs; oversized requests
are rejected rather than silently reduced. Interrupted observations are retained
with a FAILED manifest and a VIOLATED tick contract. The neural step
is 1 ms; 1/5/15-tick physics/sensor periods are treatments. Batch sizes 1/16/128 must
leave identical completed state, including remainder steps. No UI clock is read.

## Data boundary

`DATA/gateway_state.json` owns body and decoder observations, not canonical SNN weights.
It records neural digests for association but does not claim resume support.
`DATA/runs_index.json` identifies preserved original observations; `analysis/ai_packet.json`
is a bounded review projection. New records identify SYNTHETIC data, fixed learning-disabled
controllers, donor-tape hashes/overhead, source bytecode consistency, configuration,
units and experimental limitations. Hardware energy is unknown, not replaced by zero.

The importer requires SHA-256 and explicit provenance, defaults to 8 MB, 10000 nodes
and 100000 edges, and rejects duplicate IDs/edges, invalid endpoints, nonfinite or
out-of-model weights and delays. It returns an inert graph; it does not silently
instantiate or overwrite the production neural network. A BIOLOGICAL_REFERENCE label
is a declaration to review, not independently validated ground truth.

## Visualization

Wesen remains a read-only functional projection. Null/unknown values cannot become
numeric zero; unavailable/expired requests clear previous observations; late responses
cannot overwrite newer state. Data availability is labelled. Structure, observed
activity, plasticity and causal evidence are separate concepts; no EEG/fMRI or human
neuroanatomical claims. Full reference/replay modes and a new 3D avatar are deferred,
not advertised as delivered. Add future artifact interactions through the File Viewer.

## Extension gates

Before enabling learning: native eligibility/modulator path, separately versioned
learnable gateways, frozen/random controls, training/holdout split and independent
review. Before biological replication: pinned licensed data, exact LIF source parameters,
independent expected outputs and a review of every transformation. Before 5D claims:
matched graph/neuron/synapse/activity/resource controls in the existing dimension study.
Before EVID promotion: prospectively reviewed confirmatory version and independent
replication. The present programme cannot grant itself that authority.

See [the scientific supplement](../../research/publications/2026-09-09_connectome-embodiment_supplement/README.md)
and [the programme](../../research/protocols/CONNECTOME_EMBODIMENT_V1.json).
