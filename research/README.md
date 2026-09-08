## Naming update — 2026-09-08

MHRN / Multi-Scale Homeostatic Recurrence Network. Publication: Recursive Epistemics / Rekursive Epistemik. [Migration and compatibility](../NAMING.md). Historical scientific artifacts remain unchanged. Platform completion is recorded separately from requested names.

# MHRN Scientific Evidence Framework (B5D-SEF)

Ein wissenschaftliches Evidenzsystem für MHRN, das technische Implementierung, Experimentdaten, akzeptierte Evidenz und Interpretation strikt trennt.

## Aktueller technischer Stand — 2026-09-07

Die Forschungsinfrastruktur auf `main` umfasst Scientific Integrity Gate, AI-Provenienz und Causal-Taint, Shadow-/Replay-Kontrollen, deterministische Statistics Engine, epistemischen Provenienzgraph, getrennte Operator-/Experiment-/Dev-Storage-Scopes sowie protocol-driven Science Runner.

Aktueller Engineering-Snapshot:

- der aktuelle lokale Fast-Suite-Snapshot umfasst **849 bestanden, 5 uebersprungen und 3 fehlgeschlagen**; 32 Slow-Tests wurden abgewaehlt;
- die drei bekannten Fehler betreffen Windows-Zeilenenden sowie eine erwartete Fehlermeldung bei unsicheren Publikationspfaden; der lokale Snapshot ist daher nicht vollstaendig gruen;
- der letzte aufgezeichnete Browser-Snapshot umfasst **5 bestandene Chromium-Tests**;
- Research Catalog / variable-projection-dimension integration ist nach `main` gemergt;
- Merge-Commit: `85e7209509b348bf7912dde01d3d9ebb078a2e61`;
- der letzte vollständig abgeschlossene `main`-CI-Baseline-Lauf vor diesem Merge war #598 und erfolgreich;
- die nachfolgenden `main`-CI-Läufe sind die maßgebliche Verifikation für den neuen Stand und dürfen erst nach Abschluss als grün bezeichnet werden;
- Python 3.11, 3.12 und 3.13, Typprüfung, Format/Lint, Security, Scientific Integrity, Wheel und Docker bleiben verpflichtende Gates.

Diese technischen Ergebnisse sind **kein wissenschaftlicher Wirksamkeitsnachweis**.

Die aktuelle Dashboard-Oberflaeche bietet ausserdem einen gemeinsamen natuerlichen Vorlesemodus: Der File Viewer, aufgeklappte Chat-Dateikarten und die letzte Research-Chat-Antwort koennen ueber die deutsche Browser-Sprachsynthese vorgelesen, pausiert, fortgesetzt und angehalten werden. Markdown-Formatierung, Links und URLs werden fuer die Spracheingabe geglaettet; ohne Browser-Unterstuetzung bleibt der Text normal lesbar.

## Forschungsfragen- und Hypothesen-Registry

Der normale Forschungsworkflow lädt die Basiseinträge plus deterministische Registry-Fragmente:

- `research/registry/questions.yaml` und `questions.*.yaml`;
- `research/registry/hypotheses.yaml` und `hypotheses.*.yaml`.

Doppelte IDs werden fail-closed abgelehnt. MSBA-Fragen und -Hypothesen sind dadurch normale, im Experiment Workflow erreichbare Forschungsobjekte. Die UI bietet einen durchsuchbaren Research Catalog statt einer einzigen langen Pulldown-Liste und unterscheidet `OPERATIONAL` von `EXPLORATORY`.

Der Workflow-Katalog liefert die Facetten `domain`, `status`, `evidence_status` und `experiment_progress` aus dem Backend. Nach akzeptierten kanonischen Registry-Aenderungen werden die aktuellen Katalog-, Evidence- und Open-Question-Reports automatisch neu erzeugt; historische experiment-eigene Reports bleiben unveraendert.

`OPERATIONAL` bedeutet, dass ein passender eingefrorener/preregistrierter Experimentvertrag existiert. `EXPLORATORY` darf einen protokollierten Lauf erzeugen, aber **keine bestätigende Evidenz vortäuschen oder automatisch nach EVID promoten**. Noch nicht operationalisierte RQ/H bleiben in TODO und Roadmap, bis Hypothese, Kontrollen, Stopping Rule, Preregistration und Runner vollständig vorhanden sind.

Der Repository-Audit kann `RQ-*`- und `H-*`-Referenzen repo-weit gegen die kanonische Registry prüfen, ohne historische Dokumente umzuschreiben.

## Wissenschaftliche Grundhierarchie

```text
Implementierung
    ↓
registrierte Forschungsfrage
    ↓
Hypothese
    ↓
preregistriertes Experiment
    ↓
DATA
    ↓
statistische / methodische Auswertung
    ↓
Human Review
    ↓
EVID
    ↓
Claim-Status / Antwort
```

Kurzform:

```text
implementation test != experiment data != accepted evidence != interpretation
```

## Network-Impulse-Korrektur

Die historischen `EXP-GEN-0009` bis `EXP-GEN-0012` bleiben unverändert. Sie dokumentieren korrekt, dass die damalige Output-orientierte Instrumentierung keine sichtbaren Spikes/Aktivierung aufgezeichnet hat.

Der aktuelle Probe-Vertrag erfasst zusätzlich:

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
- State-Digests vor und nach dem Lauf.

Wissenschaftlich korrekt ist ein **neues Multi-Seed-Experiment** auf der reparierten Instrumentierung, nicht das rückwirkende Umschreiben historischer DATA.

## Experimentdaten und Kompaktierung

Große Runs dürfen nicht dadurch wissenschaftlich unbrauchbar werden, dass Dashboard oder kleine lokale KI-Modelle eine sehr große `runs.json` vollständig laden müssen.

Daher gilt:

1. Rohbeobachtungen bleiben in immutable/compressed Raw-Artefakten erhalten.
2. `runs.json` darf eine bounded aktuelle Projektion enthalten.
3. `analysis/ai_packet.json` enthält eine kompakte, für KI-Review geeignete Projektion.
4. Jede Projektion muss auf Raw-Artefakt, Digest und Provenienz zurückverweisen.
5. Kompaktierung darf keine Rohdaten löschen oder Evidenz ersetzen.
6. AI-Berichte dürfen nur aus den ihnen tatsächlich bereitgestellten Daten Schlüsse ziehen.

## Neural Symbiosis und MSBA als Forschungsbehandlung

`Neural Symbiosis` erweitert den Embodiment-Rand um offene periphere neuronale und virtuelle Areale. MSBA spezialisiert diese Grenze für Audio, Vision, Digitalpfade sowie Energie-/Ressourcensteuerung. Diese Ebenen sind **keine wissenschaftliche Evidenz an sich**.

Mögliche Areale umfassen u. a. CNN, Vision Transformer, Transformer, LSTM/GRU/RNN, GNN, Modern Hopfield, Reservoir/ESN, MLP, VAE/GAN/Diffusion, Autoencoder, periphere SNNs, multimodale und neuro-symbolische Netzwerke sowie Custom Adapter. Virtuelle Systeme wie Logic Engines, Datenbanken, Knowledge Graphs oder externe Speicher können über explizite Adapter teilnehmen.

MSBA/externe Projektionsräume dürfen aktuell **1–32 Dimensionen** deklarieren. Der produktive persistierte SNN-Core bleibt jedoch 5D. Eine echte Core-N-D-Erweiterung benötigt ein separates versioniertes Neuron-ID-/Storage-Format, `.b5d`-Migration, generalisierte Spatial-Indizes und 5D-Äquivalenztests. Projektions-N-D darf daher nicht als produktives Core-N-D-Evidenzresultat bezeichnet werden.

Für wissenschaftliche Runs gelten zusätzliche Regeln:

- exakte Adapter-/Modell-/Framework-Version erfassen;
- Modellartefakt und Hash erfassen;
- Endpoint-Identität und Modalität erfassen;
- Encoding/Decoding-Vertrag erfassen;
- Gateway-Parameter und aktivierte Mechanismen erfassen;
- RNG Seed/State persistieren;
- Gateway-Zustand von Core-Synapsenzustand trennen;
- Frozen-, Random-, Timing-Shuffle- und Information-Destroyed-Kontrollen vorsehen;
- Pipeline-Erreichbarkeit niemals als gelerntes Tool Use interpretieren;
- Gateway-Plastizität außerhalb eines expliziten preregistrierten Experimentpfads deaktiviert lassen.

Der zunächst vorgeschlagene globale Homöostase-Reward

\[
R(t)=\frac{1}{N}\sum_i(\rho_{target}-\bar\rho_i)
\]

ist **keine validierte Standarddefinition**, weil gegenläufige Populationseffekte sich gegenseitig aufheben können. Künftige Experimente sollen signierte, absolute, quadratische und lokale Fehlermaße sowie getrennte Task-/Homöostase-Rewards vergleichen.

## Empfohlener Forschungsablauf

1. Forschungsfrage, Hypothesen, Bedingungen, Seeds, Metriken und Ausschlussregeln registrieren.
2. Source Freeze und sauberen Git-Baum herstellen.
3. Netzwerkmodus, AI-Exposure und periphere Modelle explizit deklarieren.
4. Experiment unter `research/experiments/EXP-*/` ausführen.
5. DATA-Artefakte mit Digest-Provenienz speichern.
6. Prüfen, ob die Instrumentierung die hypothesenrelevanten Zustände tatsächlich beobachtet.
7. Deterministische Statistik aus der Statistics Engine erzeugen.
8. Limitationen und Ausschlüsse dokumentieren.
9. EVID erst nach unabhängiger Wiederholung und Human Review registrieren.
10. Historische negative oder unvollständige DATA niemals nachträglich an verbesserte Instrumentierung anpassen.

## Unmittelbarer Forschungsbedarf

### 1. Registry-Operationalisierung

- alle noch nicht gemappten kanonischen RQ/H einem dedizierten Runner oder explizitem `design_pending`-Status zuordnen;
- Kontrollen, Stopping Rules, Outcomes und Preregistrations vor confirmatory execution einfrieren;
- Audit als CI-Artefakt veröffentlichen;
- aktuelle generierte Katalog-/Evidence-/Open-Question-Ansichten nach Registry-Änderungen neu erzeugen, historische Experimentberichte aber nicht umschreiben.

### 2. Post-Repair Network-Impulse-Validierung

- recurrence-off gegen recurrence-on;
- mehrere unabhängige Seeds;
- vollständige Spike-/Synapsen-/Tick-Metriken;
- Reproduzierbarkeit/Determinismus prüfen;
- Review vor möglicher EVID-Promotion.

### 3. Closed-loop Embodiment EVID

Die technische Closed-loop-Infrastruktur existiert. Erforderlich bleibt die kontrollierte Evidence-Promotion mit Replay/Open-Loop-, Sensor-Loss- und Actuator-No-Effect-Kontrollen.

### 4. Neural Symbiosis / MSBA Gateway Experiments

- experiment-only Runner Adapter;
- frozen/random/shuffled Controls;
- `RQ-MSBA-E01` bis `RQ-MSBA-E05` mit hypothesenspezifischen Protokollen durchführen;
- noisy-area suppression;
- sensor-lesion compensation;
- alternative homeostatische Reward-/Error-Formulierungen;
- Multi-Seed-Validierung vor Tool-Use-Claims.

### 5. Dimensionsforschung

- preregistrierten N-D-Projektions-Sweep implementieren;
- dimension-shuffled/reduced/increased/topology-matched Kontrollen vergleichen;
- produktives Core-N-D erst nach versionierter Storage-/ID-Migration untersuchen;
- frühere 5D-Experimente nicht als N-D-Evidenz reinterpretieren.

### 6. Runtime-/Zeitkalibrierung

Target-Hz, Achieved-Hz, Real-Time-Ratio, `dt` und Tick-Kosten systematisch benchmarken. Pacing-Änderungen dürfen bei identischem `dt` und identischen Inputs nicht unbemerkt Simulationsergebnisse verändern.

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
├── registry/           # YAML-Register und Fragmente
├── experiments/        # Manifeste, DATA, Reports und Reviews
├── literature/         # Literaturdatenbank
├── generated/          # automatisch generierte Berichte
└── schemas/            # JSON-Schemata
```

## Verifikation

```bash
python -m pytest -q
python research/generate_reports.py
python scripts/verify_network_activity.py
```

Technische Reports dürfen `implemented`, `integrated` oder `verified` tragen. `evidenced` ist ausschließlich für reproduzierbare, protokollierte und reviewte Forschungsergebnisse vorgesehen.

## Wissenschaftliche Abhandlung und Publikationsarchiv

[KI - Die geliehene Intelligenz: vollstaendige wissenschaftliche Abhandlung](publications/README.md)

Die Research-Kategorie `publications` enthaelt Word, Markdown, Literatur, Forschungsfragen, Hypothesen, Ergebnisdarstellungen, Originalmanuskripte und alle Begleitdateien. Die kapitelweise Lesefassung ist im zentralen File Viewer vollstaendig zugaenglich. Datierte Originale bleiben unveraendert und schreibgeschuetzt; kanonische Register und Evidenzfreigaben werden nicht ersetzt.

## Kognition, Bewusstseinskritik und vorsorgliche Ethik

[Programm und Messgrenzen](protocols/COGNITION_CONSCIOUSNESS.md), [22 kanonische Fragen](registry/questions.cognition.yaml), [Hypothesen](registry/hypotheses.cognition.yaml), [38 Kritikthemen](critique/CONSCIOUSNESS_CRITIQUE.md), [Ethikrichtlinie](ethics/AI_WELFARE_POLICY.md), [Quellennutzung](literature/COGNITION_SOURCES.md), [aktuelle Abhandlung](publications/README.md). Die neue Batterie hat prospektive Entwürfe und getestete Instrumente, aber keine validierten nativen Adapter. Geschützte Starts und automatische EVID-Promotion sind blockiert; alte DATA/EVID bleiben unverändert.

## Human Review Inbox

The Research dashboard exposes an explicit Human Review Inbox through `GET /api/research/reviews`. It aggregates open AIRR and explicitly review-blocked artifacts. A reviewer must provide identity, decision and comments. Decisions are persisted only through the existing append-only review writers and therefore never rewrite the reviewed artifact or automatically create scientific evidence.

The UI is intended to make review completion operationally simple without weakening epistemic controls: `accepted_as_interpretation` means the human accepts an interpretation record, not that a hypothesis or research question is confirmed. Evidence promotion remains a separate, explicit workflow.
