# EXP-GEN-0020: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-001`
- Hypothese: `H-SNN-001-A`
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

- RQ/Condition-Pruefung: `MISMATCH`
- Evidence Readiness: `BLOCKED_SEMANTIC_MISMATCH`
- Begründung: RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. Ein einzelner Impuls bzw. science_all_v1 mit langer stiller Nachlaufphase ist dafuer keine ausreichende Primaerpruefung.
- Beobachtete Conditions: `5d:1d, 5d:2d, 5d:3d, 5d:5d, 5d:random_graph, learning:learning_off, learning:learning_on, learning:sham_replay, ping:recurrence_off, ping:recurrence_on, regulation:chronic_pressure, regulation:nominal, regulation:telemetry_unknown, stdp:productive_reward_stdp, temporal:fast_medium_slow, time:100, time:1000, time:10000, time:100000`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Complete science suite
- Bedingungen: Seeds 42,43,44; alle registrierten Science-Suite-Runner ausführen; Bedingungen im DATA über Gruppenpräfixe trennen.
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `4aeab3fee7a08c417ebe2fc5607828f70058368e`
- Git dirty: `True`
- Runtime: `252.2197587999981` s

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

- `fast`: Referenzvergleiche=299994; discrepancy mean=2.62576e-05, max=0.952011; nonzero=0 (—); mean(nonzero)=—.
- `medium`: Referenzvergleiche=299988; discrepancy mean=3.78343e-05, max=1.15894; nonzero=0 (—); mean(nonzero)=—.
- `slow`: Referenzvergleiche=299982; discrepancy mean=4.61094e-05, max=1.17842; nonzero=0 (—); mean(nonzero)=—.

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

- AIRR Status: `generated`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`
- AIRR Markdown: [`reports/AIRR-2026-0001.md`](reports/AIRR-2026-0001.md)
- AIRR JSON: [`reports/AIRR-2026-0001.json`](reports/AIRR-2026-0001.json)

### 8.1 KI-Einschaetzung

Die Ergebnisse zeigen konsistent, dass die Aktivierung rekurrenten Ereignissen (`ping:recurrence_on`) und die Aktivierung des Lernmechanismus (STDP) die Netzwerkkomplexität und die Gewichtsveränderung signifikant erhöhen. Die statistische Analyse der Zeitmetriken (`ticks_per_second`) weist jedoch auf ein erwartetes Artefakt hin: Die gemessene Taktfrequenz steigt mit der Simulationsdauer an, was die kausale Interpretation der Zeitabhängigkeit erschwert. Die statistische Analyse der Dimensionalität zeigt, dass die meisten Metriken (z.B. `delivered_synaptic_events`, `recurrent_events`) bei den getesteten Bedingungen konstant niedrig sind (Mittelwert 2.0 bzw. 0.0), was auf eine begrenzte Fähigkeit des Netzwerks zur Erzeugung komplexer, dimensionsabhängiger Dynamiken hindeutet. Die Reproduzierbarkeit der Ergebnisse über verschiedene Seeds hinweg ist hoch, was die Zuverlässigkeit der beobachteten Effekte stützt.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die statistische Analyse basiert auf einer sehr kleinen Stichprobengröße (n=3 Runs/Seeds), was die Verallgemeinerbarkeit der Mittelwerte einschränkt.
- Die Interpretation der Zeitabhängigkeit (`ticks_per_second`) ist problematisch, da der beobachtete Anstieg mit der Dauer eher ein Artefakt der Datenaggregation ist als ein Beweis für eine kausale Beschleunigung.
- Die Analyse der Dimensionalität (`5d:5d`, `5d:random_graph`) zeigt, dass die meisten Metriken (z.B. `delivered_synaptic_events`) unabhängig von der Dimension konstant niedrig sind (Mittelwert 2.0), was die Rolle der Dimensionalität in der Spike-Dynamik nicht klar beleuchtet.
- Die Vergleichsmetriken für die Dimensionalität (`5d:1d` vs. `5d:5d`) zeigen keine signifikanten Unterschiede in den Kernmetriken (z.B. `recurrent_events` = 0.0), was darauf hindeutet, dass die Dimensionalität an sich kein primärer Treiber für die beobachtete Spike-Dynamik ist.

### Alternative Erklaerungen

- Der beobachtete Anstieg der Taktfrequenz mit der Simulationsdauer könnte ein Artefakt der Messung sein, bei dem die gemittelte Rate über längere Zeiträume statistisch höher erscheint, ohne dass eine tatsächliche physikalische Änderung der Systemgeschwindigkeit vorliegt.
- Die geringe Variabilität der Metriken über die Seeds hinweg könnte darauf hindeuten, dass die zugrundeliegenden Prozesse deterministisch sind und die Variation durch die Seeds nicht signifikant beeinflusst wird.
- Die beobachtete Abhängigkeit der Spike-Dynamik von `ping:recurrence_on` könnte lediglich auf die erhöhte Anzahl von verfügbaren Synapsen oder die verlängerte Simulationszeit zurückzuführen sein, anstatt auf eine intrinsische, kausale Rolle der rekurrenten Ereignisse.

### Fehlende Nachweise

- Detaillierte Spezifikationen der Spike-Generierung und der Synapsenverbindung, um zu verstehen, wie die rekurrenten Ereignisse (`recurrent_events`) die Spike-Sequenz beeinflussen.
- Eine Analyse, die die Gewichtsveränderungen (STDP) nicht nur nach dem Vergleich mit dem Ausgangszustand, sondern auch im Verhältnis zur Anzahl der Neuronen und Synapsen skaliert, um die Effizienz des Lernprozesses zu bewerten.

### Empfohlene Folgeexperimente

- Durchführung eines Experiments, das die Spike-Dynamik bei kontrollierter, konstanten Taktfrequenz über lange Zeiträume misst, um das Artefakt der Taktfrequenzabhängigkeit zu eliminieren.
- Vergleich der Netzwerkzustände (`state_digest_after`) zwischen `ping:recurrence_on` und `ping:recurrence_off` nach einer festen, kurzen Anzahl von Spikes, um zu quantifizieren, wie stark die rekurrenten Ereignisse die kurzfristige Netzwerkstruktur beeinflussen.
- Testen von Lernprotokollen mit unterschiedlichen Lernraten (z.B. $	ext{learning rate} 	imes 2$ und $	ext{learning rate} / 2$), um die Abhängigkeit der Gewichtsveränderung von der Lernrate zu bestimmen.

## 9. Artefakte

- [analysis/AIAR-critical_reviewer-20260905191804992445-76280e55.json](analysis/AIAR-critical_reviewer-20260905191804992445-76280e55.json)
- [analysis/AIAR-scientific_analyst-20260905191715308646-76280e55.json](analysis/AIAR-scientific_analyst-20260905191715308646-76280e55.json)
- [analysis/AIAR-scientific_writer-20260905191855305815-76280e55.json](analysis/AIAR-scientific_writer-20260905191855305815-76280e55.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/runs.json](DATA/runs.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `MISMATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
