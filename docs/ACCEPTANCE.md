# Abnahme Stand 1 – Sprint 1C

## Pflichtprüfungen

```bash
python -m pytest -v
python -m pytest tests/test_golden_chain.py -v
python -m src.main --benchmark
python -m src.main --observe
```

## Golden Chain

Kontrolliertes Netz:

```text
A --delay 2--> B --delay 3--> C
```

Erwartung:

```text
Tick 0: A spike
Tick 1: no spike
Tick 2: B spike
Tick 3: no spike
Tick 4: no spike
Tick 5: C spike
```

Die Tatsachen müssen in `StepResult`, `SpikeHistory`, `PropagationReport`, den Run-Artefakten und der Rasterdatenaufbereitung konsistent sein.

## Stand-1-Abgrenzung

Ein PASS besagt nur, dass der nichtlernende Referenzkern deterministisch und beobachtbar arbeitet. Es ist kein Nachweis von Intelligenz, Bewusstsein oder biologischer Gleichwertigkeit.
