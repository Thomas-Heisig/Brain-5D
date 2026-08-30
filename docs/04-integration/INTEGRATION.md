# Integration notes

This overlay is intentionally not wired into `src.main`, `RuntimeController`,
`StructuralPlasticityEngine`, or the dashboard write API.

That is deliberate. Alpha.6 should first establish stable contracts while keeping the
existing Alpha.5 behavior byte-for-byte and test-for-test unchanged.

## Suggested follow-up wiring after quality gates

1. Read-only dashboard card: expose `LanguageOrganStatus` only.
2. Add a bounded observation adapter that builds `SignalFrame` from existing telemetry or
   spike history without retaining `NeuralNetwork` references.
3. Keep `NullLanguageBackend` as default and require explicit config enablement before a
   local backend is instantiated.
4. Add an asynchronous queue before any real llama.cpp backend is introduced.
5. Add internet/Wikipedia adapters only under `src/knowledge/adapters/`; they must emit
   provenance-bearing items and may not call SNN mutation APIs.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -v tests/test_signal_processing_contracts.py tests/test_language_organ_contracts.py tests/test_knowledge_contracts.py
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests scripts
.\.venv\Scripts\python.exe -m pyright src scripts tests
.\.venv\Scripts\python.exe -m pytest -v -m "not slow"
git diff --check
```
