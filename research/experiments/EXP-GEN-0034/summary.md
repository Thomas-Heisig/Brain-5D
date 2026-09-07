# EXP-GEN-0034: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-002`
- Hypothese: `H-SNN-002-A`
- Protokoll: `science_suite_v1`
- Durchlaeufe: `22`
- Seeds: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]`
- Angeforderte Ticks: `100`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `100 .. 100` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: RQ-SNN-002 erwartet einen kontrollierten Impulsantwort-Vergleich mit recurrence_off und recurrence_on.
- Beobachtete Conditions: `recurrence_off, recurrence_on`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Network impulse response
- Bedingungen: Seeds 42,43,44; identical initial state per seed; impulse current 100.0; recurrence as controlled treatment.
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `90f512a3d47996a97e9dcb4470bdcd7d6a496276`
- Git dirty: `True`
- Runtime: `0.032741299946792424` s

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
| recurrence_off | 11 | 1,2,3,4,5,6,7,8,9,10,11 | 100 | 3 | 2 | 3 | 0 | 1 |
| recurrence_on | 11 | 1,2,3,4,5,6,7,8,9,10,11 | 100 | 33 | 33 | 3 | 10 | 61 |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `activated_neurons`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `delivered_synaptic_events`: $\Delta=31$; $R=16.5$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `first_response_latency`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `last_response_latency`: $\Delta=60$; $R=31$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `propagation_depth`: $\Delta=60$; $R=61$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `recurrent_events`: $\Delta=10$; $R=—$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `synaptic_activity_ticks`: $\Delta=31$; $R=16.5$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `total_spikes`: $\Delta=30$; $R=11$; Referenz `recurrence_off`, Vergleich `recurrence_on`.

### 5.2 Inter-Spike-Intervalle

- `recurrence_off`: n=22, mean=1, median=1, min=1, max=1 Ticks.
- `recurrence_on`: n=352, mean=1.9375, median=2, min=1, max=4 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 1 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 2 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 2 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 3 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 3 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 4 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 4 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 5 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 5 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 6 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 6 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 7 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 7 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 8 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 8 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 9 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 9 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 10 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 10 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |
| 11 | recurrence_off | 100 | 3 | 2 | 3 | 0 | 1 | — |
| 11 | recurrence_on | 100 | 33 | 33 | 3 | 10 | 61 | — |

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

Die deskriptiven Statistiken zeigen einen sehr deutlichen Unterschied in den gemessenen Metriken zwischen der Bedingung 'recurrence_on' und 'recurrence_off'. In der Bedingung 'recurrence_on' sind die Mittelwerte für 'delivered_synaptic_events' (33.0), 'last_response_latency' (62.0), 'propagation_depth' (61.0), 'recurrent_events' (10.0) und 'total_spikes' (33.0) deutlich höher als in der Bedingung 'recurrence_off' (Mittelwerte von 2.0, 2.0, 1.0, 0.0 bzw. 3.0). Diese Unterschiede sind konsistent über alle 11 Seeds hinweg. Die beobachteten Unterschiede deuten darauf hin, dass die Aktivierung der Rekurrenzverbindungen die Netzwerkaktivität und die Komplexität der Spike-Sequenzen erhöht. Es ist jedoch zu beachten, dass die Analyse rein deskriptiv ist und keine statistische Signifikanz getestet wurde.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert ausschließlich auf deskriptiven Statistiken (Mittelwerte, Min/Max/Median) über 11 Seeds. Es wurde keine formelle statistische Hypothesentestung durchgeführt, daher können die beobachteten Unterschiede nur als deskriptive Effekte oder Unterschiede beschrieben werden, und die statistische Signifikanz wurde nicht getestet.
- Die experimentellen Bedingungen ('recurrence_on' vs. 'recurrence_off') sind in ihren beobachteten Metriken (z.B. 'delivered_synaptic_events': 33.0 vs. 2.0) extrem unterschiedlich. Dies könnte darauf hindeuten, dass die Rekurrenzverbindung nicht nur eine spezifische Rolle spielt, sondern dass die Bedingungen insgesamt sehr unterschiedliche Netzwerkzustände induzieren, was die Interpretation der kausalen Rolle erschwert.
- Die Metriken 'ticks_executed' und 'activated_neurons' sind in beiden Bedingungen konstant (100.0 bzw. 3.0), was darauf hindeuten könnte, dass die beobachteten Unterschiede in der Netzwerkaktivität primär durch die Art der Verbindungen und nicht durch die grundlegende Rechenleistung oder die Anzahl der beteiligten Neuronen bedingt sind.

### Alternative Erklaerungen

- Die beobachteten Unterschiede könnten auf die Tatsache zurückzuführen sein, dass die Rekurrenzverbindung nicht nur eine zusätzliche Verbindung, sondern auch einen erhöhten Energiefluss oder eine veränderte Dynamik des gesamten Netzwerks erzeugt, die über die reine Spike-Übertragung hinausgeht.
- Die beobachteten Unterschiede könnten durch die Art der Initialisierung oder der Art des Inputs beeinflusst werden, die in den beiden Bedingungen verwendet werden, und nicht ausschließlich durch die Rekurrenzverbindung selbst. Die Bedingungen könnten unterschiedliche Arten von Netzwerkzuständen stabilisieren.

### Fehlende Nachweise

- Bereitstellung von detaillierten Spike-Sequenzen für mehrere Runs in beiden Bedingungen, um die Muster der Spike-Übertragung und die Art der Rekurrenzereignisse zu vergleichen.
- Eine Analyse, die die Auswirkungen der Rekurrenzverbindung auf die Energiebilanz des Netzwerks oder die metabolische Rate berücksichtigt, um die beobachteten erhöhten Aktivitätswerte zu kontextualisieren.

### Empfohlene Folgeexperimente

- Durchführung eines Experiments, bei dem die Rekurrenzverbindung nur in ihrer Funktion als Feedback-Mechanismus getestet wird, ohne die Gesamtanzahl der Synapsen oder die Aktivierung der Neuronen zu verändern.
- Vergleich der 'delivered_synaptic_events' und 'total_spikes' zwischen den beiden Bedingungen, während alle anderen Parameter (z.B. 'propagation_depth', 'recurrent_events') konstant gehalten werden, um die spezifische Rolle der Rekurrenz zu isolieren.
- Analyse der zeitlichen Entwicklung der Spike-Aktivität (Spike-Sequenzen) in beiden Bedingungen, um zu bestimmen, ob die beobachteten Unterschiede auf eine erhöhte Frequenz oder eine verlängerte Dauer der Aktivität zurückzuführen sind.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260907125108578686-2056f02e.json](analysis/AIAR-critical_reviewer-20260907125108578686-2056f02e.json)
- [analysis/AIAR-scientific_analyst-20260907125038178869-2056f02e.json](analysis/AIAR-scientific_analyst-20260907125038178869-2056f02e.json)
- [analysis/AIAR-scientific_writer-20260907125140539841-2056f02e.json](analysis/AIAR-scientific_writer-20260907125140539841-2056f02e.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-recurrence_off-seed-1.json.gz](DATA/raw/run-0000-recurrence_off-seed-1.json.gz)
- [DATA/raw/run-0001-recurrence_on-seed-1.json.gz](DATA/raw/run-0001-recurrence_on-seed-1.json.gz)
- [DATA/raw/run-0002-recurrence_off-seed-2.json.gz](DATA/raw/run-0002-recurrence_off-seed-2.json.gz)
- [DATA/raw/run-0003-recurrence_on-seed-2.json.gz](DATA/raw/run-0003-recurrence_on-seed-2.json.gz)
- [DATA/raw/run-0004-recurrence_off-seed-3.json.gz](DATA/raw/run-0004-recurrence_off-seed-3.json.gz)
- [DATA/raw/run-0005-recurrence_on-seed-3.json.gz](DATA/raw/run-0005-recurrence_on-seed-3.json.gz)
- [DATA/raw/run-0006-recurrence_off-seed-4.json.gz](DATA/raw/run-0006-recurrence_off-seed-4.json.gz)
- [DATA/raw/run-0007-recurrence_on-seed-4.json.gz](DATA/raw/run-0007-recurrence_on-seed-4.json.gz)
- [DATA/raw/run-0008-recurrence_off-seed-5.json.gz](DATA/raw/run-0008-recurrence_off-seed-5.json.gz)
- [DATA/raw/run-0009-recurrence_on-seed-5.json.gz](DATA/raw/run-0009-recurrence_on-seed-5.json.gz)
- [DATA/raw/run-0010-recurrence_off-seed-6.json.gz](DATA/raw/run-0010-recurrence_off-seed-6.json.gz)
- [DATA/raw/run-0011-recurrence_on-seed-6.json.gz](DATA/raw/run-0011-recurrence_on-seed-6.json.gz)
- [DATA/raw/run-0012-recurrence_off-seed-7.json.gz](DATA/raw/run-0012-recurrence_off-seed-7.json.gz)
- [DATA/raw/run-0013-recurrence_on-seed-7.json.gz](DATA/raw/run-0013-recurrence_on-seed-7.json.gz)
- [DATA/raw/run-0014-recurrence_off-seed-8.json.gz](DATA/raw/run-0014-recurrence_off-seed-8.json.gz)
- [DATA/raw/run-0015-recurrence_on-seed-8.json.gz](DATA/raw/run-0015-recurrence_on-seed-8.json.gz)
- [DATA/raw/run-0016-recurrence_off-seed-9.json.gz](DATA/raw/run-0016-recurrence_off-seed-9.json.gz)
- [DATA/raw/run-0017-recurrence_on-seed-9.json.gz](DATA/raw/run-0017-recurrence_on-seed-9.json.gz)
- [DATA/raw/run-0018-recurrence_off-seed-10.json.gz](DATA/raw/run-0018-recurrence_off-seed-10.json.gz)
- [DATA/raw/run-0019-recurrence_on-seed-10.json.gz](DATA/raw/run-0019-recurrence_on-seed-10.json.gz)
- [DATA/raw/run-0020-recurrence_off-seed-11.json.gz](DATA/raw/run-0020-recurrence_off-seed-11.json.gz)
- [DATA/raw/run-0021-recurrence_on-seed-11.json.gz](DATA/raw/run-0021-recurrence_on-seed-11.json.gz)
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
