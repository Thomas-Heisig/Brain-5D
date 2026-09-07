# EXP-BATCH-20260906200118-01: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-001`
- Hypothese: `H-SNN-001-A`
- Protokoll: `sustained_activity_stability_v1`
- Durchlaeufe: `20`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110]`
- Angeforderte Ticks: `100000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `100000 .. 100000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `MISMATCH`
- Evidence Readiness: `BLOCKED_SEMANTIC_MISMATCH`
- Begründung: RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. science_suite_v1/science_all_v1 bleiben dafuer diagnostisch; eine Primaerpruefung erfordert weiterhin ein dediziertes Sustained-Activity-Protokoll.
- Beobachtete Conditions: `no_input_control, tonic_drive`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: sustained_activity_stability_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `275f3b77df6e89cc224d8542454434ff7e84d7a4`
- Git dirty: `True`
- Runtime: `10.872093599988148` s

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
| no_input_control | 10 | 101,102,103,104,105,106,107,108,109,110 | 100000 | — | — | — | — | — |
| tonic_drive | 10 | 101,102,103,104,105,106,107,108,109,110 | 100000 | — | — | — | — | — |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `no_input_control`, Vergleich `tonic_drive`.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | no_input_control | 100000 | — | — | — | — | — | — |
| 101 | tonic_drive | 100000 | — | — | — | — | — | — |
| 102 | no_input_control | 100000 | — | — | — | — | — | — |
| 102 | tonic_drive | 100000 | — | — | — | — | — | — |
| 103 | no_input_control | 100000 | — | — | — | — | — | — |
| 103 | tonic_drive | 100000 | — | — | — | — | — | — |
| 104 | no_input_control | 100000 | — | — | — | — | — | — |
| 104 | tonic_drive | 100000 | — | — | — | — | — | — |
| 105 | no_input_control | 100000 | — | — | — | — | — | — |
| 105 | tonic_drive | 100000 | — | — | — | — | — | — |
| 106 | no_input_control | 100000 | — | — | — | — | — | — |
| 106 | tonic_drive | 100000 | — | — | — | — | — | — |
| 107 | no_input_control | 100000 | — | — | — | — | — | — |
| 107 | tonic_drive | 100000 | — | — | — | — | — | — |
| 108 | no_input_control | 100000 | — | — | — | — | — | — |
| 108 | tonic_drive | 100000 | — | — | — | — | — | — |
| 109 | no_input_control | 100000 | — | — | — | — | — | — |
| 109 | tonic_drive | 100000 | — | — | — | — | — | — |
| 110 | no_input_control | 100000 | — | — | — | — | — | — |
| 110 | tonic_drive | 100000 | — | — | — | — | — | — |

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

Die Ergebnisse zeigen, dass die Bedingung 'tonic_drive' im Vergleich zur 'no_input_control' eine deutlich höhere und stabile Spike-Aktivität aufweist. Die gemesseten 'post_burn_in_mean_spikes' sind für 'tonic_drive' (Mittelwert: 300.0) höher als für 'no_input_control' (Mittelwert: 0.0). Darüber hinaus zeigen beide Bedingungen über die gesamte Simulationsdauer hinweg eine numerische Stabilität ('stability_pass': true) und eine konstante mittlere Spannung ('window_mean_v'), was auf eine stabile neuronale Dynamik hindeutet. Die beobachteten Unterschiede in der Spike-Aktivität sind konsistent über alle 20 Läufe hinweg.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert auf einer Stichprobe von 20 Läufen (n=20), was die Verallgemeinerbarkeit der Ergebnisse einschränkt. Obwohl die Ergebnisse konsistent sind, sollte die Variabilität der Parameter (z.B. Gewichte, Initialzustände) untersucht werden.
- Die 'window_mean_v' ist ein aggregierter Wert über 100 Ticks. Eine detailliertere Analyse der Spannungsverteilung über die gesamte Simulationsdauer könnte feine Dynamiken aufdecken, die durch die Mittelung verloren gehen.

### Alternative Erklaerungen

- Die beobachtete Spike-Aktivität unter 'tonic_drive' könnte auf eine übermäßige oder nicht-physiologische Anregung des Netzwerks zurückzuführen sein, anstatt auf eine biologisch relevante, stabile Funktion. Die konstante Spike-Rate könnte durch die spezifische Art der 'tonic_drive'-Stimulation (Konstanz der Eingabe) und nicht durch eine intrinsische, stabile Netzwerkdynamik bedingt sein.
- Die beobachteten Unterschiede in der Spike-Aktivität könnten durch die spezifische Stärke (50.0) und Art der 'tonic_drive'-Stimulation bedingt sein. Es ist unklar, ob diese Aktivität ein kausales Ergebnis der Netzwerkstruktur oder lediglich eine Reaktion auf die konstante externe Eingabe ist.

### Fehlende Nachweise

- Detaillierte Verteilungsstatistiken der Spike-Intervalle (ISI) für beide Bedingungen, um festzustellen, ob die Spike-Aktivität unter 'tonic_drive' rhythmisch oder zufällig ist.
- Eine Analyse der Korrelation zwischen der 'drive_current' und der Varianz der Spike-Aktivität, um die Empfindlichkeit des Systems zu bewerten.

### Empfohlene Folgeexperimente

- Durchführung von Experimenten mit variierenden Intensitäten und Frequenzen der 'tonic_drive'-Stimulation, um die Abhängigkeit der Spike-Aktivität von den Stimulusparametern zu untersuchen.
- Vergleich der Spike-Dynamik unter 'tonic_drive' mit einer Bedingung, die nur eine geringe, nicht-sättigende Stimulation liefert, um die spezifische Rolle der 'tonic_drive'-Intensität zu isolieren.
- Analyse der Spike-Timing-Abhängigkeiten (STDP) in Abhängigkeit von der 'tonic_drive'-Bedingung, um die kausale Rolle der Stimulation zu klären.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906200249380768-777c75e2.json](analysis/AIAR-critical_reviewer-20260906200249380768-777c75e2.json)
- [analysis/AIAR-scientific_analyst-20260906200208647936-777c75e2.json](analysis/AIAR-scientific_analyst-20260906200208647936-777c75e2.json)
- [analysis/AIAR-scientific_writer-20260906200331732324-777c75e2.json](analysis/AIAR-scientific_writer-20260906200331732324-777c75e2.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-no_input_control-seed-101.json.gz](DATA/raw/run-0000-no_input_control-seed-101.json.gz)
- [DATA/raw/run-0001-tonic_drive-seed-101.json.gz](DATA/raw/run-0001-tonic_drive-seed-101.json.gz)
- [DATA/raw/run-0002-no_input_control-seed-102.json.gz](DATA/raw/run-0002-no_input_control-seed-102.json.gz)
- [DATA/raw/run-0003-tonic_drive-seed-102.json.gz](DATA/raw/run-0003-tonic_drive-seed-102.json.gz)
- [DATA/raw/run-0004-no_input_control-seed-103.json.gz](DATA/raw/run-0004-no_input_control-seed-103.json.gz)
- [DATA/raw/run-0005-tonic_drive-seed-103.json.gz](DATA/raw/run-0005-tonic_drive-seed-103.json.gz)
- [DATA/raw/run-0006-no_input_control-seed-104.json.gz](DATA/raw/run-0006-no_input_control-seed-104.json.gz)
- [DATA/raw/run-0007-tonic_drive-seed-104.json.gz](DATA/raw/run-0007-tonic_drive-seed-104.json.gz)
- [DATA/raw/run-0008-no_input_control-seed-105.json.gz](DATA/raw/run-0008-no_input_control-seed-105.json.gz)
- [DATA/raw/run-0009-tonic_drive-seed-105.json.gz](DATA/raw/run-0009-tonic_drive-seed-105.json.gz)
- [DATA/raw/run-0010-no_input_control-seed-106.json.gz](DATA/raw/run-0010-no_input_control-seed-106.json.gz)
- [DATA/raw/run-0011-tonic_drive-seed-106.json.gz](DATA/raw/run-0011-tonic_drive-seed-106.json.gz)
- [DATA/raw/run-0012-no_input_control-seed-107.json.gz](DATA/raw/run-0012-no_input_control-seed-107.json.gz)
- [DATA/raw/run-0013-tonic_drive-seed-107.json.gz](DATA/raw/run-0013-tonic_drive-seed-107.json.gz)
- [DATA/raw/run-0014-no_input_control-seed-108.json.gz](DATA/raw/run-0014-no_input_control-seed-108.json.gz)
- [DATA/raw/run-0015-tonic_drive-seed-108.json.gz](DATA/raw/run-0015-tonic_drive-seed-108.json.gz)
- [DATA/raw/run-0016-no_input_control-seed-109.json.gz](DATA/raw/run-0016-no_input_control-seed-109.json.gz)
- [DATA/raw/run-0017-tonic_drive-seed-109.json.gz](DATA/raw/run-0017-tonic_drive-seed-109.json.gz)
- [DATA/raw/run-0018-no_input_control-seed-110.json.gz](DATA/raw/run-0018-no_input_control-seed-110.json.gz)
- [DATA/raw/run-0019-tonic_drive-seed-110.json.gz](DATA/raw/run-0019-tonic_drive-seed-110.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `MISMATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
