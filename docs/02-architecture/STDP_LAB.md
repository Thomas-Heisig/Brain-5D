# Sprint 2A - STDP Laboratory

## Scope

Sprint 2A adds a deterministic, isolated reference implementation of
spike-timing-dependent plasticity (STDP). It is intentionally not connected to
`src.core.network`, `src.core.neuron`, or `src.core.synapse`.

The Sprint 1C simulation therefore remains behaviorally identical.

## Learning rule

For `dt = t_post - t_pre`:

- `dt > 0`: `dw = A_plus * exp(-dt / tau_plus)` (LTP)
- `dt < 0`: `dw = -A_minus * exp(dt / tau_minus)` (LTD)
- `dt == 0`: no update

The new weight is clamped to `[min_weight, max_weight]`.

`STDPSynapse.pre_spike()` and `STDPSynapse.post_spike()` return the weight
change that was actually applied after clamping.

## Pairing semantics

The laboratory implementation uses a simple nearest-neighbour/event-driven
pairing rule:

- a PRE spike can pair with the most recent earlier POST spike (LTD),
- a POST spike can pair with the most recent earlier PRE spike (LTP).

This means a continuous sequence `PRE(0), POST(10), PRE(20), POST(30)` is not
just two independent LTP pairs: the `PRE(20)` also sees `POST(10)` and therefore
causes LTD. Independent experimental pairs must either use separate synapse
instances or call `reset_timing()` between trials.

This behavior is explicit and tested to avoid hidden state contamination in
STDP experiments.

## Files

- `src/learning/__init__.py`
- `src/learning/stdp_plugin.py`
- `tests/test_stdp_isolated.py`
- `configs/poc_config.yaml` (new `stdp` section, disabled by default)
- `configs/poc_config_stdp_on.yaml` (parameter reference only)

## Run the laboratory tests

```bash
python -m pytest tests/test_stdp_isolated.py -v
```

Then run the complete repository regression suite:

```bash
python -m pytest tests/ -v
```

The expected Sprint 2A property is that every Sprint 1C test still passes,
because no production-core module imports or executes the STDP laboratory.

## Important limitation

`stdp.enabled` is configuration scaffolding only in Sprint 2A. Running
`python -m src.main --config configs/poc_config_stdp_on.yaml` must not be
interpreted as production-core STDP activation unless the main program already
supports config overlay files and later sprints explicitly connect the learning
module to the network.

## Exit criteria

Sprint 2A is complete when:

1. LTP for PRE-before-POST is numerically correct.
2. LTD for POST-before-PRE is numerically correct.
3. The update decays exponentially toward zero for large timing differences.
4. Weight clamping is correct.
5. Repeated/continuous timing behavior is deterministic and documented.
6. Invalid parameters fail fast.
7. The complete Sprint 1C regression suite remains green.

Core integration, eligibility traces, reward modulation, and homeostasis are
explicitly out of scope for Sprint 2A.
