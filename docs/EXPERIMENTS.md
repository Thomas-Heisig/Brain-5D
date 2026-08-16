# Experimente und Run-Artefakte

Jeder Lauf erzeugt unter `artifacts/runs/<run_id>/`:

- `effective_config.yaml`
- `config_hash.txt`
- `environment.json`
- `metrics.csv`
- `spikes.jsonl`
- `stimulus.jsonl`
- `topology.json`
- `run_summary.json`

Damit können spätere Sprint-2-Läufe gegen Stand 1 verglichen werden.

## Vergleichsregeln

Vergleiche nur Runs mit dokumentierter Konfiguration. Der Config-Hash ist ein schneller Identifikator, ersetzt aber nicht die inhaltliche Prüfung. Wall-Clock-Zeiten sind nicht deterministisch; Topologie und simulierte Zustände bei gleichem Seed sollen es sein.
