# Roadmap ab v0.4.0-alpha.4

## v0.4.0-alpha.4 – CURRENT

- Async bounded storage queue
- Storage telemetry
- generation-based crash-safe compaction
- runtime checkpoint sidecar
- real core restore foundation
- alpha.3 mypy fixes

## v0.4.0 – NEXT

Exit-Kriterien:

- komplette Testsuite grün
- `black --check src tests`
- `mypy src` ohne Fehler
- Pylint >= 9.0
- Restore-and-Continue Referenztest identisch über mindestens 2 Checkpoints
- Queue-Stresstest ohne stillen Datenverlust
- Compaction-Crash-Matrix bestanden

## v0.5.0

Homöostase und event-driven Dirty Tracking. Erst wenn Persistenz final ist,
werden neuronale Regelkreise erweitert.

## v0.6.0

Chunked 5D Storage, Domain Decomposition, Parallelisierung und 500k+ Neuronen.

## v0.7–v1.0

Learning Environment -> multimodale Adapter -> Memory/Context/Goals -> HMI/API
-> begrenzte Autonomie -> Release Candidate -> nutzbare Brain-5D KI.
