# Brain-5D v0.5.0-alpha.5 Overlay

This overlay is intentionally **non-destructive**. It adds the alpha.5 structural persistence modules, tests, config fragment and verification script. Because the live repository evolves quickly, existing `main.py`, dashboard server, controller and plasticity files are not blindly overwritten.

## Additive files

- `src/storage/structural_journal.py`
- `src/storage/structural_recovery.py`
- `src/self_organization/approval.py`
- `src/self_organization/undo.py`
- `src/visualization/structural_heatmap.py`
- `src/dashboard/structural_api.py`
- focused tests
- `scripts/verify_v050a5.py`
- alpha.5 config fragment
- architecture documentation

## Required integration points

Follow `INTEGRATION_v050a5.md` after copying the overlay. It describes the exact contracts that must be wired into the current alpha.4 implementation without removing legacy alpha.3 APIs.
