# Brain-5D Scientific Evidence Framework (B5D-SEF)

Ein wissenschaftliches Evidenzsystem für Brain-5D, das technische Implementierung, Experimentdaten, akzeptierte Evidenz und Interpretation strikt trennt.

## Aktueller technischer Stand — 2026-09-06

Die Forschungsinfrastruktur auf `main` umfasst Scientific Integrity Gate, AI-Provenienz und Causal-Taint, Shadow-/Replay-Kontrollen, deterministische Statistics Engine, epistemischen Provenienzgraph, getrennte Operator-/Experiment-/Dev-Storage-Scopes sowie protocol-driven Science Runner.

Verifizierter Engineering-Snapshot:

- 773 Tests werden gesammelt;
- Python 3.11, 3.12 und 3.13 Full-/Slow-Suites laufen grün;
- Mypy, Pyright, Black, Ruff, Pylint und Pre-Commit laufen grün;
- Security und Scientific Integrity Gate laufen grün;
- Wheel Build/Install sowie Docker Build/Runtime Verify laufen grün;
- der vollständige GitHub-CI-Run #583 auf dem Neural-Symbiosis-Merge-Commit war erfolgreich.

Diese technischen Ergebnisse sind **kein wissenschaftlicher Wirksamkeitsnachweis**.

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

## Neural Symbiosis als Forschungsbehandlung

`Neural Symbiosis` erweitert den Embodiment-Rand um offene periphere neuronale und virtuelle Areale. Diese Ebene ist **keine wissenschaftliche Evidenz an sich**.

Mögliche Areale umfassen u. a. CNN, Vision Transformer, Transformer, LSTM/GRU/RNN, GNN, Modern Hopfield, Reservoir/ESN, MLP, VAE/GAN/Diffusion, Autoencoder, periphere SNNs, multimodale und neuro-symbolische Netzwerke sowie Custom Adapter. Virtuelle Systeme wie Logic Engines, Datenbanken, Knowledge Graphs oder externe Speicher können über explizite Adapter teilnehmen.

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

### 1. Post-Repair Network-Impulse-Validierung

- recurrence-off gegen recurrence-on;
- mehrere unabhängige Seeds;
- vollständige Spike-/Synapsen-/Tick-Metriken;
- Reproduzierbarkeit/Determinismus prüfen;
- Review vor möglicher EVID-Promotion.

### 2. Closed-loop Embodiment EVID

Die technische Closed-loop-Infrastruktur existiert. Erforderlich bleibt die kontrollierte Evidence-Promotion mit Replay/Open-Loop-, Sensor-Loss- und Actuator-No-Effect-Kontrollen.

### 3. Neural Symbiosis Gateway Experiments

- experiment-only Runner Adapter;
- frozen/random/shuffled Controls;
- noisy-area suppression;
- sensor-lesion compensation;
- alternative homeostatische Reward-/Error-Formulierungen;
- Multi-Seed-Validierung vor Tool-Use-Claims.

### 4. Runtime-/Zeitkalibrierung

Target-Hz, Achieved-Hz, Real-Time-Ratio, `dt` und Tick-Kosten systematisch benchmarken. Pacing-Änderungen dürfen bei identischem `dt` und identischen Inputs nicht unbemerkt Simulationsergebnisse verändern.

### 5. 5D-Ablationen

Funktionale Aussagen über die fünfdimensionale Organisation bleiben offen, bis dimension-shuffled, reduced-dimensional und topology-matched Kontrollen vorliegen.

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
├── registry/           # YAML-Register
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
