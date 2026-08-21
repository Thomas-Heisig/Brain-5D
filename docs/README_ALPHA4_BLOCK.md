<!-- BRAIN5D:ALPHA4:START -->
## v0.5.0-alpha.4 — Operator Control & Controlled Structural Plasticity

Brain-5D now has a typed operator-control boundary for single ticks, finite tick batches, continuous loops, pause/resume/stop and snapshot requests. Self-organization stays split into observation, proposal and mutation phases: `HomeostasisSignal -> SelfOrganizationPolicy -> StructuralProposal -> operator approval -> StructuralPlasticityEngine -> Manipulator`.

The default remains conservative: proposals may be generated automatically, but structural mutations require explicit approval. This preserves the project's storage principle that state, graph, fields and time remain separately traceable and that structural changes are executed through the Manipulator boundary rather than hidden inside storage or learning code.

On Windows with restricted PowerShell execution policy, use `start.cmd` or `python scripts/brain5d_launcher.py --dashboard` instead of requiring `start.ps1`.

Quality gate: `pytest`, Black, mypy and Pyright must pass before release.
<!-- BRAIN5D:ALPHA4:END -->
