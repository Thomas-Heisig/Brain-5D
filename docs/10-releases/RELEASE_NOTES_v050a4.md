# Brain-5D v0.5.0-alpha.4 — Controlled Structural Plasticity

This revision evolves the alpha.3 dry-run operator console into an approval-gated structural-plasticity layer.

## New

- RuntimeController supports +1 tick, finite N-tick runs, continuous loop, pause/resume/stop and snapshot requests.
- SelfOrganizationPolicy remains mutation-free and emits typed StructuralProposal objects.
- SelfOrganizationCoordinator keeps proposals and operator decisions.
- StructuralPlasticityEngine applies only explicitly approved proposals through a Manipulator protocol and keeps undo history.
- Dashboard operator fragment adds tick/loop/snapshot/undo controls.
- Cross-platform `start.cmd` avoids PowerShell execution-policy problems.
- Launcher uses concrete `subprocess.Popen` arguments instead of `dict[str, object]` + `**kwargs`.

## Safety boundary

Autonomous structural mutation is deliberately not enabled. The intended chain is:

`HomeostasisSignal -> Policy -> Proposal -> Operator approval -> PlasticityEngine -> Manipulator -> Journal`

This keeps storage and structural changes auditable and reversible.
