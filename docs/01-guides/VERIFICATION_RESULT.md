# Lokale Verifikation des ausgelieferten ZIP-Standes

Der ausgelieferte Stand wurde vor dem Verpacken in der Build-Umgebung geprüft.

## Tests

```text
11 passed
```

Ausgeführt mit:

```bash
python -m pytest -q
```

## PoC-Benchmark

Konfiguration: `configs/poc_config.yaml`, 5.000 Neuronen, 2.000 Ticks, Seed 42.

Gemessener Lauf:

```text
Neurons:                  5000
Synapses:                36031
Input cells:               468
Output cells:              501
Total spikes:                1
Secondary recruited:         0
Output reached:           false
Mean core tick:       1.934 ms
Median core tick:     1.891 ms
p95 core tick:        2.120 ms
```

Die fehlende sekundäre Rekrutierung im zufälligen PoC ist **kein Testfehler**. Bei den konservativen initialen Synapsengewichten von 0.0 bis 0.5 reicht der diagnostische Einzelzellenreiz nicht aus, Folgeneuronen sicher zum Spike zu bringen. Genau deshalb existiert zusätzlich der deterministische Golden-Chain-Test mit kontrollierter Kopplung.

Performancewerte sind maschinenabhängig und keine garantierten Zielwerte.
