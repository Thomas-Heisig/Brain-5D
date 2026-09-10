# EXP-BATCH-20260909223705-76: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-EMB-009`
- Hypothese: `H-EMB-009-A`
- Protokoll: `embodied_controller_attribution_v1`
- Durchlaeufe: `12`
- Seeds: `[101, 102, 103]`
- Angeforderte Ticks: `1000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `1000 .. 1000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `NOT_AUTOMATICALLY_CLASSIFIED`
- Evidence Readiness: `BLOCKED_UNCLASSIFIED_SEMANTICS`
- Begründung: Keine automatische semantische Regel fuer diese RQ-Familie registriert.
- Beobachtete Conditions: `closed_loop, controller_only, disconnected_motor, shuffled_motor`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: embodied_controller_attribution_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.2565523000084795` s

## 4. Deterministische Formeln

Die im Bericht verwendeten deskriptiven Groessen sind:

- Mittelwert: $\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i$
- Populationsstandardabweichung: $\sigma=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2}$
- Absolute Differenz: $\Delta_x=\bar{x}_B-\bar{x}_A$
- Verhältnis: $R_x=\bar{x}_B/\bar{x}_A$ fuer $\bar{x}_A\neq0$
- Inter-Spike-Intervall: $ISI_i=t_{i+1}-t_i$

Diese Formeln sind deskriptiv. Ohne registrierten Inferenztest, unabhaengige Stichprobenannahme und passende Versuchsplanung werden daraus keine Signifikanz- oder Kausalbehauptungen abgeleitet.

## 5. Ergebnisse nach Bedingung

| Condition | n | Seeds | Ticks mean | Spikes mean | Syn. events mean | Aktivierte Neuronen mean | Recurrent events mean | Propagation depth mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| closed_loop | 3 | 101,102,103 | 1000 | 51 | — | — | — | — |
| controller_only | 3 | 101,102,103 | 1000 | 69 | — | — | — | — |
| disconnected_motor | 3 | 101,102,103 | 1000 | 182 | — | — | — | — |
| shuffled_motor | 3 | 101,102,103 | 1000 | 142.333 | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | closed_loop | 1000 | 54 | — | — | — | — | — |
| 101 | disconnected_motor | 1000 | 180 | — | — | — | — | — |
| 101 | controller_only | 1000 | 69 | — | — | — | — | — |
| 101 | shuffled_motor | 1000 | 144 | — | — | — | — | — |
| 102 | closed_loop | 1000 | 48 | — | — | — | — | — |
| 102 | disconnected_motor | 1000 | 168 | — | — | — | — | — |
| 102 | controller_only | 1000 | 72 | — | — | — | — | — |
| 102 | shuffled_motor | 1000 | 147 | — | — | — | — | — |
| 103 | closed_loop | 1000 | 51 | — | — | — | — | — |
| 103 | disconnected_motor | 1000 | 198 | — | — | — | — | — |
| 103 | controller_only | 1000 | 66 | — | — | — | — | — |
| 103 | shuffled_motor | 1000 | 136 | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `failed`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

AIRR-Fehler: `Research registry entry not found: RQ-EMB-009`. Die deterministische Datenauswertung oben bleibt davon unberuehrt.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/gateway_state.json](DATA/gateway_state.json)
- [DATA/raw/run-0000-closed_loop-seed-101.json.gz](DATA/raw/run-0000-closed_loop-seed-101.json.gz)
- [DATA/raw/run-0001-disconnected_motor-seed-101.json.gz](DATA/raw/run-0001-disconnected_motor-seed-101.json.gz)
- [DATA/raw/run-0002-controller_only-seed-101.json.gz](DATA/raw/run-0002-controller_only-seed-101.json.gz)
- [DATA/raw/run-0003-shuffled_motor-seed-101.json.gz](DATA/raw/run-0003-shuffled_motor-seed-101.json.gz)
- [DATA/raw/run-0004-closed_loop-seed-102.json.gz](DATA/raw/run-0004-closed_loop-seed-102.json.gz)
- [DATA/raw/run-0005-disconnected_motor-seed-102.json.gz](DATA/raw/run-0005-disconnected_motor-seed-102.json.gz)
- [DATA/raw/run-0006-controller_only-seed-102.json.gz](DATA/raw/run-0006-controller_only-seed-102.json.gz)
- [DATA/raw/run-0007-shuffled_motor-seed-102.json.gz](DATA/raw/run-0007-shuffled_motor-seed-102.json.gz)
- [DATA/raw/run-0008-closed_loop-seed-103.json.gz](DATA/raw/run-0008-closed_loop-seed-103.json.gz)
- [DATA/raw/run-0009-disconnected_motor-seed-103.json.gz](DATA/raw/run-0009-disconnected_motor-seed-103.json.gz)
- [DATA/raw/run-0010-controller_only-seed-103.json.gz](DATA/raw/run-0010-controller_only-seed-103.json.gz)
- [DATA/raw/run-0011-shuffled_motor-seed-103.json.gz](DATA/raw/run-0011-shuffled_motor-seed-103.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `NOT_AUTOMATICALLY_CLASSIFIED`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
