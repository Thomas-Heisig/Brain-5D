# EXP-BATCH-20260909223705-28: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-EMB-001`
- Hypothese: `H-EMB-001-B`
- Protokoll: `embodied_closed_loop_v1`
- Durchlaeufe: `9`
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
- Beobachtete Conditions: `closed_loop, feedback_absent, yoked_replay`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: embodied_closed_loop_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.304554599992116` s

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
| feedback_absent | 3 | 101,102,103 | 1000 | 120 | — | — | — | — |
| yoked_replay | 3 | 101,102,103 | 1000 | 45 | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | closed_loop | 1000 | 54 | — | — | — | — | — |
| 101 | yoked_replay | 1000 | 42 | — | — | — | — | — |
| 101 | feedback_absent | 1000 | 120 | — | — | — | — | — |
| 102 | closed_loop | 1000 | 48 | — | — | — | — | — |
| 102 | yoked_replay | 1000 | 45 | — | — | — | — | — |
| 102 | feedback_absent | 1000 | 120 | — | — | — | — | — |
| 103 | closed_loop | 1000 | 51 | — | — | — | — | — |
| 103 | yoked_replay | 1000 | 48 | — | — | — | — | — |
| 103 | feedback_absent | 1000 | 120 | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `generated`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`
- AIRR Markdown: [`reports/AIRR-2026-0001.md`](reports/AIRR-2026-0001.md)
- AIRR JSON: [`reports/AIRR-2026-0001.json`](reports/AIRR-2026-0001.json)

### 8.1 KI-Einschaetzung

Die Rolle scientific_writer konnte nicht ausgeführt werden. Es liegt keine schema-konforme Modellanalyse vor.

KI-Konfidenz: `0.0` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- AI analysis unavailable; deterministic experiment artifacts remain the authoritative data basis.
- Technical reason: TimeoutError: timed out

### Alternative Erklaerungen

- Keine expliziten Angaben.

### Fehlende Nachweise

- Run the role again with a schema-conforming backend response.
- Complete mandatory human review before interpreting this report.

### Empfohlene Folgeexperimente

- Keine expliziten Folgeexperimente im AIRR angegeben.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260910011152174184-b4020ad8.json](analysis/AIAR-critical_reviewer-20260910011152174184-b4020ad8.json)
- [analysis/AIAR-scientific_analyst-20260910011052145699-b4020ad8.json](analysis/AIAR-scientific_analyst-20260910011052145699-b4020ad8.json)
- [analysis/AIAR-scientific_writer-20260910011252208116-b4020ad8.json](analysis/AIAR-scientific_writer-20260910011252208116-b4020ad8.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/gateway_state.json](DATA/gateway_state.json)
- [DATA/raw/run-0000-closed_loop-seed-101.json.gz](DATA/raw/run-0000-closed_loop-seed-101.json.gz)
- [DATA/raw/run-0001-yoked_replay-seed-101.json.gz](DATA/raw/run-0001-yoked_replay-seed-101.json.gz)
- [DATA/raw/run-0002-feedback_absent-seed-101.json.gz](DATA/raw/run-0002-feedback_absent-seed-101.json.gz)
- [DATA/raw/run-0003-closed_loop-seed-102.json.gz](DATA/raw/run-0003-closed_loop-seed-102.json.gz)
- [DATA/raw/run-0004-yoked_replay-seed-102.json.gz](DATA/raw/run-0004-yoked_replay-seed-102.json.gz)
- [DATA/raw/run-0005-feedback_absent-seed-102.json.gz](DATA/raw/run-0005-feedback_absent-seed-102.json.gz)
- [DATA/raw/run-0006-closed_loop-seed-103.json.gz](DATA/raw/run-0006-closed_loop-seed-103.json.gz)
- [DATA/raw/run-0007-yoked_replay-seed-103.json.gz](DATA/raw/run-0007-yoked_replay-seed-103.json.gz)
- [DATA/raw/run-0008-feedback_absent-seed-103.json.gz](DATA/raw/run-0008-feedback_absent-seed-103.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `NOT_AUTOMATICALLY_CLASSIFIED`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
