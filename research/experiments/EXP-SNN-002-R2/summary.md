# EXP-SNN-002-R2: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-002`
- Hypothese: `H-SNN-002-A`
- Protokoll: `science_suite_v1`
- Durchlaeufe: `20`
- Seeds: `[42, 43, 44, 45, 46, 47, 48, 49, 50, 51]`
- Angeforderte Ticks: `8`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `8 .. 8` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `HUMAN_REVIEW_REQUIRED`
- Begründung: RQ-SNN-002 erwartet einen kontrollierten Impulsantwort-Vergleich mit recurrence_off und recurrence_on.
- Beobachtete Conditions: `recurrence_off, recurrence_on`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: RQ-SNN-002 constant-input spike reproducibility replication
- Bedingungen: Constant impulse input; recurrence_off versus recurrence_on; 10 independent seeds
- Notizen: Clean-tree technical replication; AI post-hoc interpretation only; no evidence promotion.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `ac3474a155968a78a1f0def2c40af0225a15610d`
- Git dirty: `False`
- Runtime: `0.01839570002630353` s

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
| recurrence_off | 10 | 42,43,44,45,46,47,48,49,50,51 | 8 | 3 | 2 | 3 | 0 | 1 |
| recurrence_on | 10 | 42,43,44,45,46,47,48,49,50,51 | 8 | 7 | 6 | 3 | 2 | 4 |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `activated_neurons`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `delivered_synaptic_events`: $\Delta=4$; $R=3$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `first_response_latency`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `last_response_latency`: $\Delta=3$; $R=2.5$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `propagation_depth`: $\Delta=3$; $R=4$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `recurrent_events`: $\Delta=2$; $R=—$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `synaptic_activity_ticks`: $\Delta=4$; $R=3$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `total_spikes`: $\Delta=4$; $R=2.33333$; Referenz `recurrence_off`, Vergleich `recurrence_on`.

### 5.2 Inter-Spike-Intervalle

- `recurrence_off`: n=20, mean=1, median=1, min=1, max=1 Ticks.
- `recurrence_on`: n=60, mean=1.16667, median=1, min=1, max=2 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 43 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 44 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 45 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 45 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 46 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 46 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 47 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 47 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 48 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 48 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 49 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 49 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 50 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 50 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 51 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 51 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |

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
- [DATA/raw/run-0000-recurrence_off-seed-42.json.gz](DATA/raw/run-0000-recurrence_off-seed-42.json.gz)
- [DATA/raw/run-0001-recurrence_on-seed-42.json.gz](DATA/raw/run-0001-recurrence_on-seed-42.json.gz)
- [DATA/raw/run-0002-recurrence_off-seed-43.json.gz](DATA/raw/run-0002-recurrence_off-seed-43.json.gz)
- [DATA/raw/run-0003-recurrence_on-seed-43.json.gz](DATA/raw/run-0003-recurrence_on-seed-43.json.gz)
- [DATA/raw/run-0004-recurrence_off-seed-44.json.gz](DATA/raw/run-0004-recurrence_off-seed-44.json.gz)
- [DATA/raw/run-0005-recurrence_on-seed-44.json.gz](DATA/raw/run-0005-recurrence_on-seed-44.json.gz)
- [DATA/raw/run-0006-recurrence_off-seed-45.json.gz](DATA/raw/run-0006-recurrence_off-seed-45.json.gz)
- [DATA/raw/run-0007-recurrence_on-seed-45.json.gz](DATA/raw/run-0007-recurrence_on-seed-45.json.gz)
- [DATA/raw/run-0008-recurrence_off-seed-46.json.gz](DATA/raw/run-0008-recurrence_off-seed-46.json.gz)
- [DATA/raw/run-0009-recurrence_on-seed-46.json.gz](DATA/raw/run-0009-recurrence_on-seed-46.json.gz)
- [DATA/raw/run-0010-recurrence_off-seed-47.json.gz](DATA/raw/run-0010-recurrence_off-seed-47.json.gz)
- [DATA/raw/run-0011-recurrence_on-seed-47.json.gz](DATA/raw/run-0011-recurrence_on-seed-47.json.gz)
- [DATA/raw/run-0012-recurrence_off-seed-48.json.gz](DATA/raw/run-0012-recurrence_off-seed-48.json.gz)
- [DATA/raw/run-0013-recurrence_on-seed-48.json.gz](DATA/raw/run-0013-recurrence_on-seed-48.json.gz)
- [DATA/raw/run-0014-recurrence_off-seed-49.json.gz](DATA/raw/run-0014-recurrence_off-seed-49.json.gz)
- [DATA/raw/run-0015-recurrence_on-seed-49.json.gz](DATA/raw/run-0015-recurrence_on-seed-49.json.gz)
- [DATA/raw/run-0016-recurrence_off-seed-50.json.gz](DATA/raw/run-0016-recurrence_off-seed-50.json.gz)
- [DATA/raw/run-0017-recurrence_on-seed-50.json.gz](DATA/raw/run-0017-recurrence_on-seed-50.json.gz)
- [DATA/raw/run-0018-recurrence_off-seed-51.json.gz](DATA/raw/run-0018-recurrence_off-seed-51.json.gz)
- [DATA/raw/run-0019-recurrence_on-seed-51.json.gz](DATA/raw/run-0019-recurrence_on-seed-51.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
