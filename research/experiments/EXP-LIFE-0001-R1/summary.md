# EXP-LIFE-0001-R1: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-LIFE-001`
- Hypothese: `H-LIFE-001-A`
- Protokoll: `learning_interference_screen_v1`
- Durchlaeufe: `20`
- Seeds: `[42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]`
- Angeforderte Ticks: `1`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `nicht direkt messbar .. nicht direkt messbar` ausgeführte Ticks
- Tick-Vertrag: `NOT_APPLICABLE`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: LEARN-INTERF-001 v1 ist ein explizit als Vorläufer markierter Interferenz-Screen.
- Beobachtete Conditions: `sequential_three_task_screen`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Learning interference screen retry after trial-state reset
- Bedingungen: Sequential three-task screen; frozen seed set 42-61.
- Notizen: Retry after isolating transient neuron state between independent tasks.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `48dacb9ce26e68f39d2d63f1b82c8a9192ee8185`
- Git dirty: `True`
- Runtime: `5.140379299991764` s

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
| sequential_three_task_screen | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | — | — | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 43 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 44 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 45 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 46 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 47 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 48 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 49 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 50 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 51 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 52 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 53 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 54 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 55 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 56 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 57 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 58 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 59 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 60 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 61 | sequential_three_task_screen | — | — | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `unavailable`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-sequential_three_task_screen-seed-42.json.gz](DATA/raw/run-0000-sequential_three_task_screen-seed-42.json.gz)
- [DATA/raw/run-0001-sequential_three_task_screen-seed-43.json.gz](DATA/raw/run-0001-sequential_three_task_screen-seed-43.json.gz)
- [DATA/raw/run-0002-sequential_three_task_screen-seed-44.json.gz](DATA/raw/run-0002-sequential_three_task_screen-seed-44.json.gz)
- [DATA/raw/run-0003-sequential_three_task_screen-seed-45.json.gz](DATA/raw/run-0003-sequential_three_task_screen-seed-45.json.gz)
- [DATA/raw/run-0004-sequential_three_task_screen-seed-46.json.gz](DATA/raw/run-0004-sequential_three_task_screen-seed-46.json.gz)
- [DATA/raw/run-0005-sequential_three_task_screen-seed-47.json.gz](DATA/raw/run-0005-sequential_three_task_screen-seed-47.json.gz)
- [DATA/raw/run-0006-sequential_three_task_screen-seed-48.json.gz](DATA/raw/run-0006-sequential_three_task_screen-seed-48.json.gz)
- [DATA/raw/run-0007-sequential_three_task_screen-seed-49.json.gz](DATA/raw/run-0007-sequential_three_task_screen-seed-49.json.gz)
- [DATA/raw/run-0008-sequential_three_task_screen-seed-50.json.gz](DATA/raw/run-0008-sequential_three_task_screen-seed-50.json.gz)
- [DATA/raw/run-0009-sequential_three_task_screen-seed-51.json.gz](DATA/raw/run-0009-sequential_three_task_screen-seed-51.json.gz)
- [DATA/raw/run-0010-sequential_three_task_screen-seed-52.json.gz](DATA/raw/run-0010-sequential_three_task_screen-seed-52.json.gz)
- [DATA/raw/run-0011-sequential_three_task_screen-seed-53.json.gz](DATA/raw/run-0011-sequential_three_task_screen-seed-53.json.gz)
- [DATA/raw/run-0012-sequential_three_task_screen-seed-54.json.gz](DATA/raw/run-0012-sequential_three_task_screen-seed-54.json.gz)
- [DATA/raw/run-0013-sequential_three_task_screen-seed-55.json.gz](DATA/raw/run-0013-sequential_three_task_screen-seed-55.json.gz)
- [DATA/raw/run-0014-sequential_three_task_screen-seed-56.json.gz](DATA/raw/run-0014-sequential_three_task_screen-seed-56.json.gz)
- [DATA/raw/run-0015-sequential_three_task_screen-seed-57.json.gz](DATA/raw/run-0015-sequential_three_task_screen-seed-57.json.gz)
- [DATA/raw/run-0016-sequential_three_task_screen-seed-58.json.gz](DATA/raw/run-0016-sequential_three_task_screen-seed-58.json.gz)
- [DATA/raw/run-0017-sequential_three_task_screen-seed-59.json.gz](DATA/raw/run-0017-sequential_three_task_screen-seed-59.json.gz)
- [DATA/raw/run-0018-sequential_three_task_screen-seed-60.json.gz](DATA/raw/run-0018-sequential_three_task_screen-seed-60.json.gz)
- [DATA/raw/run-0019-sequential_three_task_screen-seed-61.json.gz](DATA/raw/run-0019-sequential_three_task_screen-seed-61.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `NOT_APPLICABLE`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
