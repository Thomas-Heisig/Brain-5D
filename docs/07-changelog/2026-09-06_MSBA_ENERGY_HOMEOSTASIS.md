# 2026-09-06 — MSBA and energy homeostasis

## Scope

This change adds the **Modality-Specific Synaptic Pathway Architecture (MSBA)** as a fail-closed subarchitecture of Neural Symbiosis.

## Implemented

- `src/embodiment/msba.py`
  - audio, vision and digital modality profiles;
  - no fixed semantic assignment of Brain-5D's five axes;
  - deterministic digital `SymbolFrame` with exact payload/checksum outside the SNN;
  - phase-coherence weighting that cannot invert the sign of candidate STDP;
  - information/locality/resource-aware visual growth probability;
  - normalized energy accounting with separate measured/estimated joules;
  - deterministic resource-pressure states NORMAL, CONSERVE, CRITICAL and SURVIVAL;
  - hard fan-failure survival override;
  - utility-minus-cost allocation candidate math;
  - deterministic protection policy.
- `src/embodiment/__init__.py`
  - public exports for MSBA contracts.
- `src/dashboard/static/wesen-neural-symbiosis.js`
  - read-only MSBA pathway, energy-homeostasis and digital-integrity presentation.
- `tests/test_msba.py`
  - ten tests for fail-closed behavior, deterministic digital encoding, energy provenance, safety, allocation, temporal phase weighting and visual growth.
- `docs/02-architecture/MSBA.md`
  - canonical scientific/technical contract.
- `research/registry/msba_experiments.yaml`
  - RQ-MSBA-E01 through E05, hypotheses, controls, protocols and preregistration schema.

## Scientific boundary

This integration does not activate MSBA learning, gateway plasticity, structural growth or adaptive resource allocation. It does not mutate the canonical SNN core and it does not rewrite historical DATA/EVID. UI visibility and endpoint reachability remain non-evidentiary.

Energy units are model-normalized values. Estimated joules and measured joules are different provenance classes and must not be conflated.

Digital payload integrity remains outside the SNN. Candidate meta-learning may later alter admission/routing/gain only inside explicitly registered experiments.
