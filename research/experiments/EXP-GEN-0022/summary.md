# EXP-GEN-0022: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-002`
- Hypothese: `H-SNN-002-A`
- Protokoll: `science_all_v1`
- Durchlaeufe: `51`
- Seeds: `[42, 43, 44]`
- Angeforderte Ticks: `1000`
- Tatsächlich ausgeführte Ticks je Lauf: `1000 .. 1000`
- Tick-Vertrag: `SATISFIED`
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `NOT_AUTOMATICALLY_CLASSIFIED`
- Begründung: Keine automatische semantische Regel fuer diese RQ-Familie registriert.
- Beobachtete Conditions: `5d:1d, 5d:2d, 5d:3d, 5d:5d, 5d:random_graph, learning:learning_off, learning:learning_on, learning:sham_replay, ping:recurrence_off, ping:recurrence_on, regulation:chronic_pressure, regulation:nominal, regulation:telemetry_unknown, stdp:productive_reward_stdp, temporal:fast_medium_slow, time:100, time:1000`

Ein semantischer Mismatch blockiert die Nutzung des Laufs als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Complete science suite
- Bedingungen: Seeds 42,43,44; alle registrierten Science-Suite-Runner ausführen; Bedingungen im DATA über Gruppenpräfixe trennen.
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `1d9572c72d9bd6e9b0495db4ed20a00c05789d92`
- Git dirty: `True`
- Runtime: `0.8960387000115588` s

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
| 5d:1d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:2d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:3d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:5d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:random_graph | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| learning:learning_off | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:learning_on | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:sham_replay | 3 | 42,43,44 | — | — | — | — | — | — |
| ping:recurrence_off | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| ping:recurrence_on | 3 | 42,43,44 | 1000 | 33 | 33 | 3 | 10 | 61 |
| regulation:chronic_pressure | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:nominal | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:telemetry_unknown | 3 | 42,43,44 | — | — | — | — | — | — |
| stdp:productive_reward_stdp | 3 | 42,43,44 | — | — | — | — | — | — |
| temporal:fast_medium_slow | 3 | 42,43,44 | 1000 | 0 | — | — | — | — |
| time:100 | 3 | 42,43,44 | — | — | — | — | — | — |
| time:1000 | 3 | 42,43,44 | — | — | — | — | — | — |

### 5.2 Inter-Spike-Intervalle

- `5d:1d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:2d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:3d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:5d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:random_graph`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_off`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_on`: n=96, mean=1.9375, median=2, min=1, max=4 Ticks.

### 5.3 Temporal-State-Horizonte

- `fast`: Referenzvergleiche=2994; discrepancy mean=0.00263097, max=0.952011.
- `medium`: Referenzvergleiche=2988; discrepancy mean=0.00379847, max=1.15894.
- `slow`: Referenzvergleiche=2982; discrepancy mean=0.00463849, max=1.17842.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 43 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 44 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 42 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
| 43 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
| 44 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
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
| 43 | time:100 | 100 | — | — | — | — | — | — |
| 43 | time:1000 | 1000 | — | — | — | — | — | — |
| 44 | time:100 | 100 | — | — | — | — | — | — |
| 44 | time:1000 | 1000 | — | — | — | — | — | — |
| 42 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
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

- AIRR Status: `failed`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

AIRR-Fehler: `timed out`. Die deterministische Datenauswertung oben bleibt davon unberuehrt.

## 9. Artefakte

- [analysis/statistics.json](analysis/statistics.json)
- [DATA/runs.json](DATA/runs.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `NOT_AUTOMATICALLY_CLASSIFIED`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
