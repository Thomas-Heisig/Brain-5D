# Brain-5D Embodiment Foundation

## Purpose

Brain-5D treats embodiment as a perception-action loop, not as a requirement
for one specific physical robot.  An environment may be simulated, physical,
digital, or hybrid.  The common contract is:

`observation -> Brain-5D processing -> bounded action -> environment feedback`

Alpha.7 introduces only the typed architecture boundary.  It does **not** grant
unbounded browser, operating-system, network, or physical-device control.

## Modules

- `src/embodiment/sensor.py`: sensor adapter protocol;
- `src/embodiment/actuator.py`: actuator adapter protocol;
- `src/embodiment/environment.py`: reset/step environment contract;
- `src/embodiment/registry.py`: typed adapter factory registry;
- `src/embodiment/agent.py`: explicit-action environment loop;
- `src/embodiment/models.py`: immutable observations, actions and metrics.

## Design rules

1. The neural core has no direct dependency on cameras, microphones, browsers,
   motors, or remote APIs.
2. External actions remain explicit and bounded.
3. Every future writable adapter needs permission, audit, timeout, and resource
   budgets before production use.
4. Deterministic simulated environments are implemented before uncontrolled
   physical or digital environments.
5. Dashboard embodiment metrics are read-only in alpha.7.

## Roadmap role

The interfaces are introduced in v0.4.0-alpha.7 so v0.5-v0.7 can design
self-regulation and learning environments against a stable future boundary.
Production sensor/action adapters remain a v0.8 milestone.
