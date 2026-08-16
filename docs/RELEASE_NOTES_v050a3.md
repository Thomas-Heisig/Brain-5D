# Brain-5D v0.5.0-alpha.3

## Runtime Control & Structural Policy Boundary

Alpha.3 builds on the alpha.2 homeostasis/type-safety layer and adds an operator
control plane plus the first controlled bridge from homeostasis to structural
self-organization.

### New capabilities

- Thread-safe `RuntimeController` owns interactive stepping.
- Exact tick execution from the dashboard (`Step N`).
- Continuous loop execution with configurable batch size.
- Pause/stop controls and optional snapshot trigger.
- Adjustable delay per tick for observation and debugging.
- Read-only runtime telemetry for the dashboard.
- `SelfOrganizationPolicy` converts chronic homeostasis imbalance into typed
  `StructuralProposal` objects.
- `SelfOrganizationCoordinator` is dry-run by default and therefore does not
  mutate the network unless an explicit executor is configured and dry-run is
  disabled.
- Dashboard control panel for runtime and self-organization gates.

### Architectural rule

The mutation path is now explicitly staged:

`HomeostasisEngine -> HomeostasisSignal -> SelfOrganizationPolicy -> StructuralProposal -> SelfOrganizationCoordinator -> Manipulator/Executor -> NeuralNetwork`

The dashboard never calls `network.step()` directly. HTTP request threads only
submit typed commands to the runtime controller.

### Safety defaults

- Self-organization: enabled policy, **dry-run ON**.
- Structural proposal executor: not configured by the overlay.
- STOP is terminal for the current controller instance; PAUSE is the normal
  operational command.
- Control JSON bodies are bounded to 16 KiB.
- Exact tick requests and loop sizes are bounded.

### Version

After integration change `pyproject.toml` to:

`version = "0.5.0a3"`
