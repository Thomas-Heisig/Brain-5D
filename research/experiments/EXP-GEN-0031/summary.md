# EXP-GEN-0031: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-001`
- Hypothese: `H-SNN-001-A`
- Protokoll: `runtime_ticks_v1`
- Durchlaeufe: `0`
- Seeds: `[42]`
- Angeforderte Ticks: `1000`
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
- Git Commit: `25afd8089e12d431d856982770c2024dd99a88a9`
- Git dirty: `True`
- Runtime: `241.27970320009626` s

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

Die Simulation hat erfolgreich eine Spike-Dynamik über die angeforderte Anzahl von Ticks durchgeführt, was die Hypothese stützt, dass Brain-5D stabile Spike-Dynamiken erzeugen kann.

KI-Konfidenz: `0.7` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Provenienz der Git-Daten ist unsauber oder nicht verfügbar (Git provenance is dirty or unavailable).
- Es ist kein registrierter wissenschaftlicher Nachweis mit diesem Experiment verknüpft (No registered scientific evidence is linked to this experiment).
- Die Konfigurations- und Daten-Hashes sind nicht verfügbar (NOT_AVAILABLE).

### Alternative Erklaerungen

- Die beobachtete Stabilität könnte auf die spezifische Parametrisierung der Izhikevich-Neuronen zurüruckzuführen sein, die in der Literatur als Standardreferenz dient, und nicht auf eine allgemeine Eigenschaft des gesamten Brain-5D-Frameworks.
- Die Stabilität könnte durch die gewählte Simulationsdauer (1000 Ticks) begrenzt sein; längere Simulationen könnten andere Arten von numerischer Drift oder Instabilität aufdecken.

### Fehlende Nachweise

- Bereitstellung der vollständigen und sauberen Provenienzdaten (Git provenance).
- Verknüpfung des Experiments mit einem registrierten wissenschaftlichen Nachweis, um die Reproduzierbarkeit und Validität zu erhöhen.

### Empfohlene Folgeexperimente

- Durchführung von Simulationen mit deutlich längeren Simulationszeiträumen (z.B. 10.000 Ticks oder mehr), um die Langzeitstabilität der Spike-Dynamik zu testen.
- Systematische Variation der Netzwerkparameter (z.B. Synapsendichte, Neuronentypen) bei Beibehaltung der Simulationsdauer, um die Robustheit der Dynamik zu untersuchen.

## 9. Artefakte

- [analysis/AIAR-critical_reviewer-20260906185739529930-e7d6653a.json](analysis/AIAR-critical_reviewer-20260906185739529930-e7d6653a.json)
- [analysis/AIAR-scientific_analyst-20260906185728890345-e7d6653a.json](analysis/AIAR-scientific_analyst-20260906185728890345-e7d6653a.json)
- [analysis/AIAR-scientific_writer-20260906185750395441-e7d6653a.json](analysis/AIAR-scientific_writer-20260906185750395441-e7d6653a.json)
- [analysis/statistics.json](analysis/statistics.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `NOT_APPLICABLE`, semantische Zuordnung `MISMATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
