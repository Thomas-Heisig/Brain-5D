# EXP-GEN-0032: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-001`
- Hypothese: `H-SNN-001-A`
- Protokoll: `runtime_ticks_v1`
- Durchlaeufe: `0`
- Seeds: `[42]`
- Angeforderte Ticks: `200`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `nicht direkt messbar .. nicht direkt messbar` ausgeführte Ticks
- Tick-Vertrag: `NOT_APPLICABLE`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `MISMATCH`
- Evidence Readiness: `BLOCKED_SEMANTIC_MISMATCH`
- Begründung: RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. science_suite_v1/science_all_v1 bleiben dafuer diagnostisch; eine Primaerpruefung erfordert weiterhin ein dediziertes Sustained-Activity-Protokoll.
- Beobachtete Conditions: `keine`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Controlled runtime run
- Bedingungen: Explicitly document seed, configuration, replicates and stopping criteria.
- Notizen: Keine.
- Konfiguration: `NOT_AVAILABLE`
- Config SHA-256: `NOT_AVAILABLE`
- Git Commit: `f71bc81fa2d5aa009deaf004fa4f7f37104454c4`
- Git dirty: `True`
- Runtime: `41.589169900049455` s

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

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |

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

Die Simulation erzeugte über die angeforderten 200 Ticks eine stabile Spike-Dynamik, was die Hypothese H-SNN-001-A nicht ausreichend stützt. Die beobachtete Stabilität ist auf einen extrem kurzen Zeitrahmen beschränkt, und die Hypothese erfordert nachweislich 100.000 Ticks.

KI-Konfidenz: `0.0` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Simulationsdauer von 200 Ticks ist extrem kurz und reicht nicht aus, um die Langzeitstabilität zu beurteilen. Die Beobachtung der Stabilität ist daher nur auf einen sehr kurzen Zeitrahmen beschränkt.
- Die 'known_limitations' weisen darauf hin, dass kein registrierter wissenschaftlicher Nachweis mit diesem Experiment verknüpft ist, was die Interpretation der Ergebnisse einschränkt.
- Die vom Modell ausgegebene confidence war schemawidrig oder ausserhalb des Bereichs 0..1. Sie wurde fuer die AIRR-Provenienz konservativ auf 0.0 gesetzt; der Originalwert bleibt als confidence_original erhalten.

### Alternative Erklaerungen

- Die beobachtete Stabilität könnte auf die spezifische Konfiguration des Netzwerks und die verwendeten Parameter zurückzuführen sein, und nicht auf eine allgemeine Eigenschaft der Software über lange Zeiträume.
- Die Stabilität könnte durch die Art der verwendeten Spike-Dynamik (z.B. Izhikevich-Neuronen) und die Initialisierung der Gewichte bedingt sein, was die Ergebnisse nicht auf die allgemeine Softwarearchitektur überträgt.

### Fehlende Nachweise

- Es ist erforderlich, die Simulation über einen Zeitraum von mindestens 100.000 Ticks durchzuführen, um die Hypothese H-SNN-001-A zu testen und die Langzeitstabilität zu bestätigen.

### Empfohlene Folgeexperimente

- Führen Sie die Simulation über einen deutlich längeren Zeitraum durch, idealerweise nahe oder über 100.000 Ticks, um die Langzeitstabilität der Spike-Dynamik zu testen.
- Variieren Sie die Netzwerkparameter (z.B. Synapsendichte, Aktivierungsfunktionen) und führen Sie die Langzeitstabilitätsprüfung wiederholt durch, um die Robustheit der Dynamik zu bewerten.

## 9. Artefakte

- [analysis/AIAR-critical_reviewer-20260906190143384401-ad4e32ba.json](analysis/AIAR-critical_reviewer-20260906190143384401-ad4e32ba.json)
- [analysis/AIAR-scientific_analyst-20260906190128087817-ad4e32ba.json](analysis/AIAR-scientific_analyst-20260906190128087817-ad4e32ba.json)
- [analysis/AIAR-scientific_writer-20260906190155416833-ad4e32ba.json](analysis/AIAR-scientific_writer-20260906190155416833-ad4e32ba.json)
- [analysis/statistics.json](analysis/statistics.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `NOT_APPLICABLE`, semantische Zuordnung `MISMATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
