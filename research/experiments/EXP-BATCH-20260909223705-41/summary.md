# EXP-BATCH-20260909223705-41: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-PERF-001`
- Hypothese: `H-PERF-001-A`
- Protokoll: `subsystem_performance_v1`
- Durchlaeufe: `10`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110]`
- Angeforderte Ticks: `10000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `10000 .. 10000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: PERF-001 erwartet subsystemaufgelöste Runtime-Messungen.
- Beobachtete Conditions: `subsystem_profile`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: subsystem_performance_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.7142192000028444` s

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
| subsystem_profile | 10 | 101,102,103,104,105,106,107,108,109,110 | 10000 | 33 | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 102 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 103 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 104 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 105 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 106 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 107 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 108 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 109 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 110 | subsystem_profile | 10000 | 33 | — | — | — | — | — |

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
- [analysis/AIAR-critical_reviewer-20260910014857838410-ea022f16.json](analysis/AIAR-critical_reviewer-20260910014857838410-ea022f16.json)
- [analysis/AIAR-scientific_analyst-20260910014757823525-ea022f16.json](analysis/AIAR-scientific_analyst-20260910014757823525-ea022f16.json)
- [analysis/AIAR-scientific_writer-20260910014957861033-ea022f16.json](analysis/AIAR-scientific_writer-20260910014957861033-ea022f16.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-subsystem_profile-seed-101.json.gz](DATA/raw/run-0000-subsystem_profile-seed-101.json.gz)
- [DATA/raw/run-0001-subsystem_profile-seed-102.json.gz](DATA/raw/run-0001-subsystem_profile-seed-102.json.gz)
- [DATA/raw/run-0002-subsystem_profile-seed-103.json.gz](DATA/raw/run-0002-subsystem_profile-seed-103.json.gz)
- [DATA/raw/run-0003-subsystem_profile-seed-104.json.gz](DATA/raw/run-0003-subsystem_profile-seed-104.json.gz)
- [DATA/raw/run-0004-subsystem_profile-seed-105.json.gz](DATA/raw/run-0004-subsystem_profile-seed-105.json.gz)
- [DATA/raw/run-0005-subsystem_profile-seed-106.json.gz](DATA/raw/run-0005-subsystem_profile-seed-106.json.gz)
- [DATA/raw/run-0006-subsystem_profile-seed-107.json.gz](DATA/raw/run-0006-subsystem_profile-seed-107.json.gz)
- [DATA/raw/run-0007-subsystem_profile-seed-108.json.gz](DATA/raw/run-0007-subsystem_profile-seed-108.json.gz)
- [DATA/raw/run-0008-subsystem_profile-seed-109.json.gz](DATA/raw/run-0008-subsystem_profile-seed-109.json.gz)
- [DATA/raw/run-0009-subsystem_profile-seed-110.json.gz](DATA/raw/run-0009-subsystem_profile-seed-110.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
