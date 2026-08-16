# Brain-5D v0.5.0-alpha.6 Cognitive Bridge Overlay

This overlay is intentionally additive. It does not replace `src.core`, the runtime loop,
learning, homeostasis, self-organization, storage, or the existing dashboard.

## Purpose

Prepare the next Brain-5D evolution step with three isolated contracts:

1. deterministic SNN signal interpretation (`SignalFrame`),
2. an optional, replaceable language organ (`LanguageModelBackend`),
3. a separate knowledge-intake boundary with provenance (`KnowledgeItem`).

The LLM path is disabled by default and the included `NullLanguageBackend` performs no
inference. No network weights, synapses, structural proposals, shell commands, or runtime
steps can be changed by these modules.

## Safe integration order

1. Copy the overlay into the repository root.
2. Run `python scripts/apply_alpha6_docs.py` to append roadmap/TODO markers where supported.
3. Run the focused tests: `python -m pytest -v tests/test_signal_processing_contracts.py tests/test_language_organ_contracts.py tests/test_knowledge_contracts.py`.
4. Run the existing full quality gates before wiring any runtime or dashboard adapter.

## Deliberately not implemented

- no llama.cpp dependency,
- no model download,
- no internet access,
- no Wikipedia fetcher,
- no direct SNN mutation,
- no autonomous structural plasticity,
- no dashboard write route,
- no runtime-loop ownership.

These are future integration stages after the contracts are proven stable.
