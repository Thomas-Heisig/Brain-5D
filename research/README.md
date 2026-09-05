# Brain-5D Scientific Evidence Framework (B5D-SEF)

Ein automatisch geführtes wissenschaftliches Evidenzsystem für Brain-5D.

## Aktueller Stand

Die technische Forschungsinfrastruktur ist auf dem aktuellen `main` weitgehend implementiert und verifiziert: Scientific Integrity Gate, AI-Provenienz und Causal-Taint, Shadow-/Replay-Kontrollen, deterministische Statistics Engine, epistemischer Provenienzgraph, getrennte Operator-/Experiment-/Dev-Storage-Scopes sowie protocol-driven Science Runner sind vorhanden.

**Verifizierter Stand vom 2026-09-05:**

- 735 Tests werden aktuell gesammelt;
- 733 Tests bestanden, 2 wurden in der verifizierten Repair-Vollsuite übersprungen, 0 schlugen fehl;
- der anschließend vollständig durchgelaufene GitHub-CI-Run auf `main` war erfolgreich;
- Python 3.11, 3.12 und 3.13, Mypy, Pyright, Black, Ruff, Pylint, Pre-Commit, Security und Scientific Integrity Gate sind im vollständigen CI erfolgreich gelaufen.

Diese technischen Ergebnisse sind **kein wissenschaftlicher Wirksamkeitsnachweis**.

## Aktuelle Korrektur der Network-Impulse-Beobachtung

Bei der erneuten Prüfung von `EXP-GEN-0009` bis `EXP-GEN-0012` zeigte sich ein wichtiger methodischer Befund:

- die Runs meldeten keine Runtime-Exception;
- der gespeicherte Zustand änderte sich zwischen Vorher/Nachher;
- dennoch wurden `activated_neurons = 0` und `total_spikes = 0` protokolliert;
- Ursache war die damalige Messgrenze des Network-Impulse-Probes: ausgewertet wurde im Wesentlichen nur die Output-Spike-Projektion.

Die historischen DATA-Dateien bleiben unverändert. Sie dokumentieren korrekt, was die damalige Instrumentierung beobachtet hat.

Der aktuelle Probe-Vertrag erfasst nun zusätzlich:

- ausgeführte Ticks;
- alle publizierten Spike-IDs;
- aktivierte Neuronen;
- vollständige Spike-Sequenz und Sequenz-Digest;
- ausgelieferte synaptische Events;
- Ticks mit synaptischer Aktivität;
- maximale Zahl gleichzeitig adressierter Synapsenstrom-Ziele;
- Gesamtzahl der Synapsen;
- erste/letzte Antwortlatenz;
- Propagationstiefe;
- Recurrent-/Return-Events und Return-Latenz;
- State-Digests vor und nach dem Probe-Lauf.

Zusätzlich wurde die Recurrence-Bedingung so korrigiert, dass tatsächlich ein Rückweg zum Source-Neuron existiert. Eine direkte Validierung gegen das reale `NeuralNetwork` bestätigte Tick-Ausführung, Neuronen-Spikes und synaptische Zustellung sowohl in der feed-forward- als auch in der recurrent-Bedingung. Die recurrent-Bedingung erzeugte in der Validierung zusätzliche wiederkehrende Aktivität.

Die wissenschaftlich korrekte Konsequenz ist **nicht**, `EXP-GEN-0009` bis `EXP-GEN-0012` rückwirkend umzuschreiben. Stattdessen ist ein neues registriertes, Multi-Seed-validiertes Experiment auf der reparierten Instrumentierung durchzuführen.

## Persistenz neuer Experimentdaten

Neue Science-Runner-Läufe persistieren die `NetworkResponseSignature` je Run nach:

`research/experiments/<EXP-ID>/DATA/runs.json`

Zusätzlich werden je nach Workflow u. a. Konfiguration, Workflow, Manifest, technische Reports und Review-/Evidence-Artefakte gespeichert. Dadurch sind Tick-, Spike-, Neuron-, Synapsen-, Latenz- und Recurrence-Metriken künftig Bestandteil der experimentlokalen DATA-Provenienz.

## Verifikation

```bash
python -m pytest -q
python research/generate_reports.py
python scripts/verify_network_activity.py
```

`verify_network_activity.py` prüft gezielt, dass der reale Impuls-Pfad Ticks ausführt, Synapsen besitzt, Spikes beobachtet und synaptische Events ausliefert.

Die Report-Generierung verändert keine wissenschaftlichen Claims automatisch. Claims und Reviews bleiben versionierte, provenance-gebundene Artefakte mit expliziter Bewertung.

## Empfohlener Forschungsablauf

1. Forschungsfrage, Hypothesen, Bedingungen, Seeds, Metriken und Ausschlussregeln registrieren.
2. Source Freeze und sauberen Git-Baum herstellen; Netzwerkmodus und AI-Exposure explizit festlegen.
3. Experiment unter `research/experiments/EXP-*/` ausführen und DATA-Artefakte mit Digest-Provenienz speichern.
4. Prüfen, ob die verwendete Instrumentierung die für die Hypothese relevanten Zustände tatsächlich beobachtet.
5. Deterministische Statistik aus der Statistics Engine erzeugen und Limitationen dokumentieren.
6. EVID erst nach unabhängiger Wiederholung und Human Review registrieren.
7. Historische negative oder unvollständige DATA niemals nachträglich an eine verbesserte Instrumentierung anpassen.

Technische Reports dürfen den Status `implemented`, `integrated` oder `verified` tragen. `evidenced` ist ausschließlich für reproduzierbare, protokollierte und reviewte Forschungsergebnisse zulässig.

## Unmittelbar nächster Forschungsbedarf

### 1. Post-Repair Network-Impulse-Validierung

- neue Experiment-ID aus dem aktuellen Katalog verwenden;
- recurrence-off gegen recurrence-on vergleichen;
- mehrere unabhängige Seeds;
- vollständige Spike-/Synapsen-/Tick-Metriken persistieren;
- Determinismus und Reproduzierbarkeit prüfen;
- erst nach Review eine mögliche Propagations-/Recurrence-Aussage in EVID überführen.

### 2. Closed-loop Embodiment EVID

Die technische Closed-loop-Infrastruktur und Störbedingungen existieren. Noch erforderlich ist die saubere Evidence-Promotion nach den definierten Protokoll- und Reviewregeln.

### 3. Runtime-/Zeitkalibrierung

Target-Hz, Achieved-Hz, Real-Time-Ratio, `dt` und Tick-Kosten müssen systematisch benchmarked werden. Eine Änderung des Wall-Clock-Pacings darf bei unverändertem `dt` und identischen Inputs nicht unbemerkt wissenschaftliche Simulationsergebnisse verändern.

### 4. 5D-Ablationen

Aussagen über den funktionalen Beitrag der fünfdimensionalen Organisation bleiben offen, bis dimension-shuffled, reduced-dimensional und möglichst topology-matched non-spatial Kontrollen vorliegen.

## Kernidee

Jede wissenschaftliche Aussage in Brain-5D bekommt eine **rückverfolgbare Identität**:

```text
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

```text
research/
├── registry/           # YAML-Register (Fragen, Hypothesen, Claims, Quellen, Methoden)
├── experiments/        # Experiment-Manifeste, DATA, Reports und Reviews
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

1. **THEORY** ≠ **OBSERVATION** ≠ **INTERPRETATION** — strikt getrennt.
2. **Negative Ergebnisse** werden gespeichert und nie gelöscht oder rückwirkend umgedeutet.
3. **Claims** benötigen ausreichende Evidenz vor Statuswechsel.
4. **Automatisch erzeugte Fragen** sind zunächst `candidate` — der Mensch entscheidet.
5. **Instrumentierungsgrenzen** müssen als Teil der wissenschaftlichen Interpretation dokumentiert werden.
6. **UI-/Dashboard-Zustand** ist kein Ersatz für experimentelle DATA oder EVID.
7. **AI-Beteiligung** bleibt provenance-gebunden und muss als Treatment registriert werden, wenn sie den experimentellen Pfad beeinflusst.
