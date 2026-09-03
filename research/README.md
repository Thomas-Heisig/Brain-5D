# Brain-5D Scientific Evidence Framework (B5D-SEF)

Ein automatisch geführtes wissenschaftliches Evidenzsystem für Brain-5D.

## Aktueller Stand

Die technische Forschungsinfrastruktur ist weitgehend implementiert und lokal
verifiziert: Scientific Integrity Gate, AI-Provenienz und Causal-Taint,
Shadow-/Replay-Kontrollen, deterministische Statistics Engine, epistemischer
Provenienzgraph sowie getrennte Operator-/Experiment-/Dev-Storage-Scope sind
vorhanden. Die lokale Regression am 2026-09-03 ergab **675 passed, 5 skipped**.

## Verifikation

```bash
python -m pytest -q
python research/generate_reports.py
```

Die Report-Generierung verändert keine wissenschaftlichen Claims automatisch.
Claims und Reviews bleiben versionierte, append-only Artefakte mit expliziter
Provenienz.
Das ist kein wissenschaftlicher Wirksamkeitsnachweis. Noch offen sind vor allem
unabhängige Clean-Freeze-Runs für `EXP-STDP-0002` und `EXP-EMB-0001`, die
Alpha.7.1-Performance-/Restore-Vergleiche und die unabhängige menschliche
Bewertung von AIRR. Implementierungstests, Dashboard-Status, AI-Konsens und
Causal-Attribution-Reports bleiben technische bzw. interpretative Artefakte und
werden nicht zu `EVID` hochgestuft.

## Empfohlener Forschungsablauf

1. Forschungsfrage, Hypothesen, Bedingungen, Seeds, Metriken und Ausschlussregeln registrieren.
2. Source Freeze und sauberen Git-Baum herstellen; Netzwerkmodus und AI-Exposure explizit festlegen.
3. Experiment unter `experiment/EXP-*/` ausführen und DATA-Artefakte mit Digest-Provenienz speichern.
4. Deterministische Statistik aus der Statistics Engine erzeugen und Limitationen dokumentieren.
5. EVID erst nach unabhängiger Wiederholung und Human Review registrieren.

Technische Reports dürfen den Status `implemented`, `integrated` oder `verified`
tragen. `evidenced` ist ausschließlich für reproduzierbare, protokollierte und
reviewte Forschungsergebnisse zulässig.

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
