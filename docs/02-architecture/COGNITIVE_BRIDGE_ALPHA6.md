# Cognitive Bridge Contracts — v0.5.0-alpha.6 preparation

## Scope

This document defines an additive research boundary for future language, signal
interpretation, knowledge intake, and embodiment work. It does not move ownership of the
Brain-5D runtime away from the SNN runtime/controller.

## Architectural rule

**The Language Organ never owns the Brain-5D runtime loop.**

The language organ is an optional I/O interpreter. It must not directly mutate synaptic
weights, structural plasticity, learning rules, storage, or runtime execution.

## Signal path

Raw spike/event observations are converted deterministically to `SignalFrame` values before
being exposed to any language model. The language model never receives mutable neuron or
network objects.

`SNN measurements -> SignalInterpreter -> SignalFrame -> optional Language Organ`

## Knowledge path

Internet, Wikipedia, and document retrieval are separate from the language backend.
Future retrieval adapters must create provenance-bearing `SourceRecord` and `KnowledgeItem`
objects before content can become a learning stimulus.

`Source -> validation/provenance -> KnowledgeItem -> semantic bridge -> LearningStimulus`

Direct `web content -> synapse` paths are prohibited.

## Permanent boundaries

- no direct `synapse.weight` writes from a language backend;
- no direct StructuralPlasticityEngine apply calls;
- no `network.step()` ownership;
- no execution of Python or shell text emitted by a model;
- no fact without source/provenance in the knowledge-intake path;
- no runtime failure when the language backend times out or is unavailable;
- language output is data, never an authority or command.

## Development sequence

- alpha.6: contracts and disabled-by-default adapters only;
- alpha.7: optional local model backend PoC, isolated worker/queue, auditability;
- v0.6: knowledge-intake foundation and source provenance;
- v0.7: deterministic knowledge-learning experiments;
- v0.8: production embodiment and multimodal perception/action loop.
