# Brain-5D v0.5.0-alpha.1 - Homeostasis & Self-Regulation

## Goal

v0.5 begins the transition from a persistent spiking simulation to a system that
can regulate its own activity over long runs. The first regulator is deliberately
small and observable: firing-rate homeostasis plus slow energy recovery.

## Architecture

`HomeostasisEngine` lives outside `src/core` and attaches through the existing
post-step hook. The only core change is that the Izhikevich spike threshold now
uses `30.0 + neuron.threshold_adaptation`. With the default value `0.0` and
`homeostasis.enabled: false`, the v0.4 behavior is unchanged.

The regulator keeps an exponentially smoothed firing-rate estimate per neuron:

`r_t = r_(t-1) + alpha * (s_t - r_(t-1))`

with `alpha = 1 - exp(-1 / tau_ticks)` and `s_t = 1000/dt_ms` for a spike,
otherwise zero.

Threshold feedback is:

`theta <- clamp(theta + eta * (r_t - r_target), theta_min, theta_max)`

Thus high activity raises the effective threshold and low activity lowers it.

Energy recovery is optional and follows:

`E <- clamp(E + k * (E_target - E), E_min, E_max)`

## Safety / stability rules

- Homeostasis is disabled by default.
- Threshold adaptation is bounded.
- Energy is bounded.
- No topology changes occur in this engine.
- No reward or STDP behavior is embedded here.
- The engine is observable through immutable stats.

## Persistence compatibility

The `.b5d` V1 format is unchanged. Runtime checkpoint V3 stores exact neuron and
synapse values required for deterministic restore, including homeostatic threshold
state. This closes the partial alpha.7 state where `core_restore.py` expected exact
runtime records but `checkpoint.py` still emitted version 1.

## Acceptance criteria

1. v0.4 regression remains unchanged with homeostasis disabled.
2. Excess firing raises threshold adaptation.
3. Low firing reduces threshold adaptation until the configured lower bound.
4. Energy converges toward the configured target without exceeding bounds.
5. Dashboard JSON exposes homeostasis metrics.
6. Deterministic restore remains exact.
7. Black, mypy and pytest remain green.
