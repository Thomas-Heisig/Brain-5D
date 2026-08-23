# Brain-5D Scientific Evidence Framework (B5D-SEF)

Ein automatisch geführtes wissenschaftliches Evidenzsystem für Brain-5D.

## Kernidee

Jede wissenschaftliche Aussage in Brain-5D bekommt eine **rückverfolgbare Identität**:

```
Codeänderung → Wissenschaftliche Frage → Hypothese → Experiment → Messdaten → Auswertung → Evidenz → Antwort → Neue Fragen
```

## Sechs feste Objekttypen

| Typ | Beispiel | Bedeutung |
|-----|----------|-----------|
| `RQ` | `RQ-SNN-001` | Research Question |
| `H` | `H-SNN-001-A` | Hypothese |
| `EXP` | `EXP-2026-0001` | Experiment |
| `EVID` | `EVID-2026-01` | Evidenz |
| `SRC` | `SRC-IZHIKEVICH-2003` | Literaturquelle |
| `CLAIM` | `CLAIM-SNN-001` | Wissenschaftliche Aussage |

## Verzeichnisstruktur

```
research/
├── registry/           # YAML-Register (Fragen, Hypothesen, Claims, Quellen, Methoden)
├── experiments/        # Experiment-Manifeste mit Metadaten
├── literature/         # BibTeX-Literaturdatenbank
├── generated/          # Automatisch generierte Berichte (NICHT manuell bearbeiten)
└── schemas/            # JSON-Schemata zur Validierung
```

## Automatisch generierte Berichte

- **RESEARCH_CATALOG.md** — Vollständiger Forschungskatalog
- **EVIDENCE_MATRIX.md** — Evidenzstatus pro Forschungsfrage
- **OPEN_QUESTIONS.md** — Alle offenen Fragen
- **CLAIM_REGISTER.md** — Alle Claims mit Status
- **DISSERTATION_MAP.md** — Dissertationsstruktur
- **LITERATURE_MATRIX.md** — Literaturrelevanz für Brain-5D

## Generierung

```bash
python research/generate_reports.py
```

## Wichtige Grundsätze

1. **THEORY** ≠ **OBSERVATION** ≠ **INTERPRETATION** — strikt getrennt
2. **Negative Ergebnisse** werden gespeichert und nie gelöscht
3. **Claims** benötigen ausreichende Evidenz (min. Runs) vor Statuswechsel
4. **Automatisch erzeugte Fragen** sind zunächst `candidate` — der Mensch entscheidet
