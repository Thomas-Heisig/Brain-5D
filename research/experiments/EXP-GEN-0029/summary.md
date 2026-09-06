# EXP-GEN-0029: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-002`
- Hypothese: `H-SNN-002-A`
- Protokoll: `science_suite_v1`
- Durchlaeufe: `6`
- Seeds: `[42, 43, 44]`
- Angeforderte Ticks: `8`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `8 .. 8` ausgeführte Ticks
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
- Git Commit: `fd3835ca436c3e274058448653f4170101b3b41a`
- Git dirty: `True`
- Runtime: `0.012417900026775897` s

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
| recurrence_off | 3 | 42,43,44 | 8 | 3 | 2 | 3 | 0 | 1 |
| recurrence_on | 3 | 42,43,44 | 8 | 7 | 6 | 3 | 2 | 4 |

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

- `recurrence_off`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `recurrence_on`: n=18, mean=1.16667, median=1, min=1, max=2 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 43 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |
| 44 | recurrence_off | 8 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | recurrence_on | 8 | 7 | 6 | 3 | 2 | 4 | — |

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

Die Ergebnisse zeigen, dass die Aktivierung rekurrenten Verbindungen (recurrence_on) im Vergleich zu deren Deaktivierung (recurrence_off) zu einer Zunahme der synaptischen Ereignisse, der Ausbreitungstiefe und der Antwortlatenz führt. Insbesondere die Anzahl der übertragenen synaptischen Ereignisse (delivered_synaptic_events) und die maximale Ausbreitungstiefe (propagation_depth) sind unter 'recurrence_on' höher. Die Spike-Sequenzen sind in beiden Bedingungen zwar vorhanden, aber die rekurrenten Verbindungen scheinen die Komplexität und Dauer der Aktivität zu steigern.

KI-Konfidenz: `0.7` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert auf einer begrenzten Anzahl von Wiederholungen (n=3) für jede Bedingung, was die Verallgemeinerbarkeit der Mittelwerte einschränkt.
- Die experimentellen Bedingungen sind sehr spezifisch (Impulsstrom 100.0, Ticks=8), was die Übertragbarkeit der Ergebnisse auf andere neuronale Modelle oder physiologische Systeme einschränkt.

### Alternative Erklaerungen

- Die beobachteten Unterschiede könnten auf die spezifische Art der rekurrenten Verbindungen zurückzuführen sein, die in diesem Experiment verwendet wurden, und nicht notwendigerweise auf einen allgemeinen Effekt der Rekurrenz selbst.
- Die beobachteten Unterschiede könnten durch die Interaktion mit anderen, nicht kontrollierten Netzwerkparametern beeinflusst werden.

### Fehlende Nachweise

- Weitere Daten, die die Abhängigkeit der beobachteten Effekte von der Anzahl der Wiederholungen (n) und der Dauer der Simulation (Ticks) beleuchten.
- Vergleiche mit Experimenten, die die Rolle von spezifischen Netzwerkarchitekturen oder Verbindungsarten isolieren.

### Empfohlene Folgeexperimente

- Die Untersuchung des Einflusses der Rekurrenz auf verschiedene Arten von neuronalen Verbindungen (z.B. Exzitatorisch vs. Inhibitorisch).
- Die Variation der Stärke der rekurrenten Verbindungen, um die Dosis-Wirkungs-Beziehung zu untersuchen.
- Die Durchführung der Experimente mit unterschiedlichen Impulsstromstärken, um die Abhängigkeit der Ergebnisse von der Input-Stimulation zu prüfen.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906104933049704-2663ced1.json](analysis/AIAR-critical_reviewer-20260906104933049704-2663ced1.json)
- [analysis/AIAR-scientific_analyst-20260906104911079979-2663ced1.json](analysis/AIAR-scientific_analyst-20260906104911079979-2663ced1.json)
- [analysis/AIAR-scientific_writer-20260906104953838085-2663ced1.json](analysis/AIAR-scientific_writer-20260906104953838085-2663ced1.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-recurrence_off-seed-42.json.gz](DATA/raw/run-0000-recurrence_off-seed-42.json.gz)
- [DATA/raw/run-0001-recurrence_on-seed-42.json.gz](DATA/raw/run-0001-recurrence_on-seed-42.json.gz)
- [DATA/raw/run-0002-recurrence_off-seed-43.json.gz](DATA/raw/run-0002-recurrence_off-seed-43.json.gz)
- [DATA/raw/run-0003-recurrence_on-seed-43.json.gz](DATA/raw/run-0003-recurrence_on-seed-43.json.gz)
- [DATA/raw/run-0004-recurrence_off-seed-44.json.gz](DATA/raw/run-0004-recurrence_off-seed-44.json.gz)
- [DATA/raw/run-0005-recurrence_on-seed-44.json.gz](DATA/raw/run-0005-recurrence_on-seed-44.json.gz)
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
