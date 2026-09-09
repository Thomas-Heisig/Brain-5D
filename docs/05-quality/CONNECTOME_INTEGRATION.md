# Connectome integration: source-bound engineering verification

Date: 2026-09-09. AI-assisted implementation and verification record; not scientific EVID.

## Verified source

- Source commit: `c325acdfac5341f2b25627b1d762eef044e149ef`.
- Published source plus genuine reports: `7a1881c441d81744f3332f6bea219c8973c37c05`.
- Canonical source digest: `ec95b6e0e763036b5bdca4621d5fc1a03da40959983fc4ea02a3fed17c17ee1c`.
- Recorded environment: Python 3.13.15, Linux GitHub runner.
- Full collection: 1085 tests; full suite: **1083 passed, 2 skipped, 0 failed, 0 errors**.
- The two skips are explicitly opt-in large-storage tests. Both were additionally executed successfully on preceding source `7c77b277f52c1854ed21318d32896cb86772753f`; this separate result does not rewrite the recorded full-suite baseline.
- Source remained unchanged during the full suite. All pre-commit hooks, connectome design/source integrity, determinism generation, documentation consistency and all four publication verification scripts passed.
- The final correction restored the permanent READ-ONLY view label in Neural Symbiosis and added missing final newlines to two profile files. It did not weaken the browser test or alter gateway authority.

See [the canonical baseline](../../tests/test_baseline.json) and
[the determinism record](../../research/generated/verification/determinism_infrastructure.json).
The complete platform CI, including Python 3.11/3.12/3.13, Playwright, security,
wheel and Docker, must be checked for the actual PR/merge commit. This record
is not a claim that downstream checks have already completed.

## What the engineering screens establish

The dedicated Connectome research integrity workflow executes six native protocols
through the existing Experiment Workflow: 78 condition/seed runs with 120 ticks each.
It retains manifests, original run observations, separate body/gateway state and
bounded review packets. Runs identify SYNTHETIC data, fixed hand-designed encoding
and decoding, and learning disabled. Observed spikes and delivered synaptic events
are measurements from the executing SNN, not dashboard animation.

A successful screen verifies execution, instrumentation and declared control paths.
It does not establish learned competence, biological replication, a 5D advantage,
human neuroanatomy or consciousness. Six advanced designs remain explicitly blocked.
Historical experiments, accepted evidence and the original frozen publication are
unchanged. Temporary integration transports are absent from the published source.

See [the architecture contract](../02-architecture/CONNECTOME_EMBODIMENT.md),
[the programme](../../research/protocols/CONNECTOME_EMBODIMENT_V1.json) and
[the scientific supplement](../../research/publications/2026-09-09_connectome-embodiment_supplement/README.md).
