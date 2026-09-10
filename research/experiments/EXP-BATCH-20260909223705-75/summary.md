# EXP-BATCH-20260909223705-75: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-CONN-002`
- Hypothese: `H-CONN-002-A`
- Protokoll: `connectome_topology_screen_v1`
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
- Beobachtete Conditions: `degree_preserving, random_edges, structured, weight_shuffle`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: connectome_topology_screen_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `1.1778044999955455` s

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
| degree_preserving | 3 | 101,102,103 | 1000 | 155.667 | — | — | — | — |
| random_edges | 3 | 101,102,103 | 1000 | 182.333 | — | — | — | — |
| structured | 3 | 101,102,103 | 1000 | 51 | — | — | — | — |
| weight_shuffle | 3 | 101,102,103 | 1000 | 63.6667 | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | structured | 1000 | 54 | — | — | — | — | — |
| 101 | degree_preserving | 1000 | 182 | — | — | — | — | — |
| 101 | weight_shuffle | 1000 | 106 | — | — | — | — | — |
| 101 | random_edges | 1000 | 168 | — | — | — | — | — |
| 102 | structured | 1000 | 48 | — | — | — | — | — |
| 102 | degree_preserving | 1000 | 44 | — | — | — | — | — |
| 102 | weight_shuffle | 1000 | 45 | — | — | — | — | — |
| 102 | random_edges | 1000 | 302 | — | — | — | — | — |
| 103 | structured | 1000 | 51 | — | — | — | — | — |
| 103 | degree_preserving | 1000 | 241 | — | — | — | — | — |
| 103 | weight_shuffle | 1000 | 40 | — | — | — | — | — |
| 103 | random_edges | 1000 | 77 | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `failed`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

AIRR-Fehler: `Research registry entry not found: RQ-CONN-002`. Die deterministische Datenauswertung oben bleibt davon unberuehrt.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/gateway_state.json](DATA/gateway_state.json)
- [DATA/raw/run-0000-structured-seed-101.json.gz](DATA/raw/run-0000-structured-seed-101.json.gz)
- [DATA/raw/run-0001-degree_preserving-seed-101.json.gz](DATA/raw/run-0001-degree_preserving-seed-101.json.gz)
- [DATA/raw/run-0002-weight_shuffle-seed-101.json.gz](DATA/raw/run-0002-weight_shuffle-seed-101.json.gz)
- [DATA/raw/run-0003-random_edges-seed-101.json.gz](DATA/raw/run-0003-random_edges-seed-101.json.gz)
- [DATA/raw/run-0004-structured-seed-102.json.gz](DATA/raw/run-0004-structured-seed-102.json.gz)
- [DATA/raw/run-0005-degree_preserving-seed-102.json.gz](DATA/raw/run-0005-degree_preserving-seed-102.json.gz)
- [DATA/raw/run-0006-weight_shuffle-seed-102.json.gz](DATA/raw/run-0006-weight_shuffle-seed-102.json.gz)
- [DATA/raw/run-0007-random_edges-seed-102.json.gz](DATA/raw/run-0007-random_edges-seed-102.json.gz)
- [DATA/raw/run-0008-structured-seed-103.json.gz](DATA/raw/run-0008-structured-seed-103.json.gz)
- [DATA/raw/run-0009-degree_preserving-seed-103.json.gz](DATA/raw/run-0009-degree_preserving-seed-103.json.gz)
- [DATA/raw/run-0010-weight_shuffle-seed-103.json.gz](DATA/raw/run-0010-weight_shuffle-seed-103.json.gz)
- [DATA/raw/run-0011-random_edges-seed-103.json.gz](DATA/raw/run-0011-random_edges-seed-103.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `NOT_AUTOMATICALLY_CLASSIFIED`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
