# EXP-GEN-0033-R1: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SUITE-001`
- Hypothese: `H-SUITE-001-A`
- Protokoll: `science_all_v1`
- Durchlaeufe: `57`
- Seeds: `[42, 43, 44]`
- Angeforderte Ticks: `100000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `100000 .. 100000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: SUITE erwartet science_all_v1 und PING, TEMP, STDP, Learning, TIME, 5D sowie Regulation unter gemeinsamer Provenienz.
- Beobachtete Conditions: `5d:1d, 5d:2d, 5d:3d, 5d:5d, 5d:random_graph, learning:learning_off, learning:learning_on, learning:sham_replay, ping:recurrence_off, ping:recurrence_on, regulation:chronic_pressure, regulation:nominal, regulation:telemetry_unknown, stdp:productive_reward_stdp, temporal:fast_medium_slow, time:100, time:1000, time:10000, time:100000`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Complete science suite diagnostic replication
- Bedingungen: Seeds 42,43,44; all registered science-suite runners; grouped conditions and common provenance.
- Notizen: Replication of EXP-GEN-0033 after report fallback repair; AI remains post-hoc only.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `0c64eb428430fcf0627715989857c875d674a74c`
- Git dirty: `True`
- Runtime: `204.51168389990926` s

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
| 5d:1d | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| 5d:2d | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| 5d:3d | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| 5d:5d | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| 5d:random_graph | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| learning:learning_off | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:learning_on | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:sham_replay | 3 | 42,43,44 | — | — | — | — | — | — |
| ping:recurrence_off | 3 | 42,43,44 | 100000 | 3 | 2 | 3 | 0 | 1 |
| ping:recurrence_on | 3 | 42,43,44 | 100000 | 33 | 33 | 3 | 10 | 61 |
| regulation:chronic_pressure | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:nominal | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:telemetry_unknown | 3 | 42,43,44 | — | — | — | — | — | — |
| stdp:productive_reward_stdp | 3 | 42,43,44 | — | — | — | — | — | — |
| temporal:fast_medium_slow | 3 | 42,43,44 | 100000 | 0 | — | — | — | — |
| time:100 | 3 | 42,43,44 | — | — | — | — | — | — |
| time:1000 | 3 | 42,43,44 | — | — | — | — | — | — |
| time:10000 | 3 | 42,43,44 | — | — | — | — | — | — |
| time:100000 | 3 | 42,43,44 | — | — | — | — | — | — |

### 5.2 Inter-Spike-Intervalle

- `5d:1d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:2d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:3d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:5d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:random_graph`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_off`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_on`: n=96, mean=1.9375, median=2, min=1, max=4 Ticks.

### 5.3 Temporal-State-Horizonte

- `fast`: Referenzvergleiche=299994; discrepancy mean=2.62576e-05, max=0.952011; nonzero=3237 (0.0107902); mean(nonzero)=0.00243346.
- `medium`: Referenzvergleiche=299988; discrepancy mean=3.78343e-05, max=1.15894; nonzero=3300 (0.0110004); mean(nonzero)=0.00343934.
- `slow`: Referenzvergleiche=299982; discrepancy mean=4.61094e-05, max=1.17842; nonzero=3336 (0.0111207); mean(nonzero)=0.00414628.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | ping:recurrence_off | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | ping:recurrence_on | 100000 | 33 | 33 | 3 | 10 | 61 | — |
| 43 | ping:recurrence_off | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | ping:recurrence_on | 100000 | 33 | 33 | 3 | 10 | 61 | — |
| 44 | ping:recurrence_off | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | ping:recurrence_on | 100000 | 33 | 33 | 3 | 10 | 61 | — |
| 42 | temporal:fast_medium_slow | 100000 | 0 | — | — | — | — | — |
| 43 | temporal:fast_medium_slow | 100000 | 0 | — | — | — | — | — |
| 44 | temporal:fast_medium_slow | 100000 | 0 | — | — | — | — | — |
| 42 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 43 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 44 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 42 | learning:learning_on | — | — | — | — | — | — | — |
| 42 | learning:learning_off | — | — | — | — | — | — | — |
| 42 | learning:sham_replay | — | — | — | — | — | — | — |
| 43 | learning:learning_on | — | — | — | — | — | — | — |
| 43 | learning:learning_off | — | — | — | — | — | — | — |
| 43 | learning:sham_replay | — | — | — | — | — | — | — |
| 44 | learning:learning_on | — | — | — | — | — | — | — |
| 44 | learning:learning_off | — | — | — | — | — | — | — |
| 44 | learning:sham_replay | — | — | — | — | — | — | — |
| 42 | time:100 | 100 | — | — | — | — | — | — |
| 42 | time:1000 | 1000 | — | — | — | — | — | — |
| 42 | time:10000 | 10000 | — | — | — | — | — | — |
| 42 | time:100000 | 100000 | — | — | — | — | — | — |
| 43 | time:100 | 100 | — | — | — | — | — | — |
| 43 | time:1000 | 1000 | — | — | — | — | — | — |
| 43 | time:10000 | 10000 | — | — | — | — | — | — |
| 43 | time:100000 | 100000 | — | — | — | — | — | — |
| 44 | time:100 | 100 | — | — | — | — | — | — |
| 44 | time:1000 | 1000 | — | — | — | — | — | — |
| 44 | time:10000 | 10000 | — | — | — | — | — | — |
| 44 | time:100000 | 100000 | — | — | — | — | — | — |
| 42 | 5d:1d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:2d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:3d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:5d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:random_graph | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:1d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:2d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:3d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:5d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:random_graph | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:1d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:2d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:3d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:5d | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:random_graph | 100000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | regulation:nominal | — | — | — | — | — | — | — |
| 42 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 42 | regulation:telemetry_unknown | — | — | — | — | — | — | — |
| 43 | regulation:nominal | — | — | — | — | — | — | — |
| 43 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 43 | regulation:telemetry_unknown | — | — | — | — | — | — | — |
| 44 | regulation:nominal | — | — | — | — | — | — | — |
| 44 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 44 | regulation:telemetry_unknown | — | — | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `review_pending`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

Die deterministische Datenauswertung bleibt vollständig erhalten. Da kein AI-Backend konfiguriert war, wurden die Analyse-Rollen als `analysis_unavailable` protokolliert; der AIRR-Bericht ist formal auswertbar, aber interpretation-only.

## 9. AIRR Artefakte

- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [analysis/AIAR-scientific_analyst-20260906193540367342-079d6ac4.json](analysis/AIAR-scientific_analyst-20260906193540367342-079d6ac4.json)
- [analysis/AIAR-critical_reviewer-20260906193540377192-079d6ac4.json](analysis/AIAR-critical_reviewer-20260906193540377192-079d6ac4.json)
- [analysis/AIAR-scientific_writer-20260906193540387636-079d6ac4.json](analysis/AIAR-scientific_writer-20260906193540387636-079d6ac4.json)

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-ping-recurrence_off-seed-42.json.gz](DATA/raw/run-0000-ping-recurrence_off-seed-42.json.gz)
- [DATA/raw/run-0001-ping-recurrence_on-seed-42.json.gz](DATA/raw/run-0001-ping-recurrence_on-seed-42.json.gz)
- [DATA/raw/run-0002-ping-recurrence_off-seed-43.json.gz](DATA/raw/run-0002-ping-recurrence_off-seed-43.json.gz)
- [DATA/raw/run-0003-ping-recurrence_on-seed-43.json.gz](DATA/raw/run-0003-ping-recurrence_on-seed-43.json.gz)
- [DATA/raw/run-0004-ping-recurrence_off-seed-44.json.gz](DATA/raw/run-0004-ping-recurrence_off-seed-44.json.gz)
- [DATA/raw/run-0005-ping-recurrence_on-seed-44.json.gz](DATA/raw/run-0005-ping-recurrence_on-seed-44.json.gz)
- [DATA/raw/run-0006-temporal-fast_medium_slow-seed-42.json.gz](DATA/raw/run-0006-temporal-fast_medium_slow-seed-42.json.gz)
- [DATA/raw/run-0007-temporal-fast_medium_slow-seed-43.json.gz](DATA/raw/run-0007-temporal-fast_medium_slow-seed-43.json.gz)
- [DATA/raw/run-0008-temporal-fast_medium_slow-seed-44.json.gz](DATA/raw/run-0008-temporal-fast_medium_slow-seed-44.json.gz)
- [DATA/raw/run-0009-stdp-productive_reward_stdp-seed-42.json.gz](DATA/raw/run-0009-stdp-productive_reward_stdp-seed-42.json.gz)
- [DATA/raw/run-0010-stdp-productive_reward_stdp-seed-43.json.gz](DATA/raw/run-0010-stdp-productive_reward_stdp-seed-43.json.gz)
- [DATA/raw/run-0011-stdp-productive_reward_stdp-seed-44.json.gz](DATA/raw/run-0011-stdp-productive_reward_stdp-seed-44.json.gz)
- [DATA/raw/run-0012-learning-learning_on-seed-42.json.gz](DATA/raw/run-0012-learning-learning_on-seed-42.json.gz)
- [DATA/raw/run-0013-learning-learning_off-seed-42.json.gz](DATA/raw/run-0013-learning-learning_off-seed-42.json.gz)
- [DATA/raw/run-0014-learning-sham_replay-seed-42.json.gz](DATA/raw/run-0014-learning-sham_replay-seed-42.json.gz)
- [DATA/raw/run-0015-learning-learning_on-seed-43.json.gz](DATA/raw/run-0015-learning-learning_on-seed-43.json.gz)
- [DATA/raw/run-0016-learning-learning_off-seed-43.json.gz](DATA/raw/run-0016-learning-learning_off-seed-43.json.gz)
- [DATA/raw/run-0017-learning-sham_replay-seed-43.json.gz](DATA/raw/run-0017-learning-sham_replay-seed-43.json.gz)
- [DATA/raw/run-0018-learning-learning_on-seed-44.json.gz](DATA/raw/run-0018-learning-learning_on-seed-44.json.gz)
- [DATA/raw/run-0019-learning-learning_off-seed-44.json.gz](DATA/raw/run-0019-learning-learning_off-seed-44.json.gz)
- [DATA/raw/run-0020-learning-sham_replay-seed-44.json.gz](DATA/raw/run-0020-learning-sham_replay-seed-44.json.gz)
- [DATA/raw/run-0021-time-100-seed-42.json.gz](DATA/raw/run-0021-time-100-seed-42.json.gz)
- [DATA/raw/run-0022-time-1000-seed-42.json.gz](DATA/raw/run-0022-time-1000-seed-42.json.gz)
- [DATA/raw/run-0023-time-10000-seed-42.json.gz](DATA/raw/run-0023-time-10000-seed-42.json.gz)
- [DATA/raw/run-0024-time-100000-seed-42.json.gz](DATA/raw/run-0024-time-100000-seed-42.json.gz)
- [DATA/raw/run-0025-time-100-seed-43.json.gz](DATA/raw/run-0025-time-100-seed-43.json.gz)
- [DATA/raw/run-0026-time-1000-seed-43.json.gz](DATA/raw/run-0026-time-1000-seed-43.json.gz)
- [DATA/raw/run-0027-time-10000-seed-43.json.gz](DATA/raw/run-0027-time-10000-seed-43.json.gz)
- [DATA/raw/run-0028-time-100000-seed-43.json.gz](DATA/raw/run-0028-time-100000-seed-43.json.gz)
- [DATA/raw/run-0029-time-100-seed-44.json.gz](DATA/raw/run-0029-time-100-seed-44.json.gz)
- [DATA/raw/run-0030-time-1000-seed-44.json.gz](DATA/raw/run-0030-time-1000-seed-44.json.gz)
- [DATA/raw/run-0031-time-10000-seed-44.json.gz](DATA/raw/run-0031-time-10000-seed-44.json.gz)
- [DATA/raw/run-0032-time-100000-seed-44.json.gz](DATA/raw/run-0032-time-100000-seed-44.json.gz)
- [DATA/raw/run-0033-5d-1d-seed-42.json.gz](DATA/raw/run-0033-5d-1d-seed-42.json.gz)
- [DATA/raw/run-0034-5d-2d-seed-42.json.gz](DATA/raw/run-0034-5d-2d-seed-42.json.gz)
- [DATA/raw/run-0035-5d-3d-seed-42.json.gz](DATA/raw/run-0035-5d-3d-seed-42.json.gz)
- [DATA/raw/run-0036-5d-5d-seed-42.json.gz](DATA/raw/run-0036-5d-5d-seed-42.json.gz)
- [DATA/raw/run-0037-5d-random_graph-seed-42.json.gz](DATA/raw/run-0037-5d-random_graph-seed-42.json.gz)
- [DATA/raw/run-0038-5d-1d-seed-43.json.gz](DATA/raw/run-0038-5d-1d-seed-43.json.gz)
- [DATA/raw/run-0039-5d-2d-seed-43.json.gz](DATA/raw/run-0039-5d-2d-seed-43.json.gz)
- [DATA/raw/run-0040-5d-3d-seed-43.json.gz](DATA/raw/run-0040-5d-3d-seed-43.json.gz)
- [DATA/raw/run-0041-5d-5d-seed-43.json.gz](DATA/raw/run-0041-5d-5d-seed-43.json.gz)
- [DATA/raw/run-0042-5d-random_graph-seed-43.json.gz](DATA/raw/run-0042-5d-random_graph-seed-43.json.gz)
- [DATA/raw/run-0043-5d-1d-seed-44.json.gz](DATA/raw/run-0043-5d-1d-seed-44.json.gz)
- [DATA/raw/run-0044-5d-2d-seed-44.json.gz](DATA/raw/run-0044-5d-2d-seed-44.json.gz)
- [DATA/raw/run-0045-5d-3d-seed-44.json.gz](DATA/raw/run-0045-5d-3d-seed-44.json.gz)
- [DATA/raw/run-0046-5d-5d-seed-44.json.gz](DATA/raw/run-0046-5d-5d-seed-44.json.gz)
- [DATA/raw/run-0047-5d-random_graph-seed-44.json.gz](DATA/raw/run-0047-5d-random_graph-seed-44.json.gz)
- [DATA/raw/run-0048-regulation-nominal-seed-42.json.gz](DATA/raw/run-0048-regulation-nominal-seed-42.json.gz)
- [DATA/raw/run-0049-regulation-chronic_pressure-seed-42.json.gz](DATA/raw/run-0049-regulation-chronic_pressure-seed-42.json.gz)
- [DATA/raw/run-0050-regulation-telemetry_unknown-seed-42.json.gz](DATA/raw/run-0050-regulation-telemetry_unknown-seed-42.json.gz)
- [DATA/raw/run-0051-regulation-nominal-seed-43.json.gz](DATA/raw/run-0051-regulation-nominal-seed-43.json.gz)
- [DATA/raw/run-0052-regulation-chronic_pressure-seed-43.json.gz](DATA/raw/run-0052-regulation-chronic_pressure-seed-43.json.gz)
- [DATA/raw/run-0053-regulation-telemetry_unknown-seed-43.json.gz](DATA/raw/run-0053-regulation-telemetry_unknown-seed-43.json.gz)
- [DATA/raw/run-0054-regulation-nominal-seed-44.json.gz](DATA/raw/run-0054-regulation-nominal-seed-44.json.gz)
- [DATA/raw/run-0055-regulation-chronic_pressure-seed-44.json.gz](DATA/raw/run-0055-regulation-chronic_pressure-seed-44.json.gz)
- [DATA/raw/run-0056-regulation-telemetry_unknown-seed-44.json.gz](DATA/raw/run-0056-regulation-telemetry_unknown-seed-44.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
