# EXP-BATCH-20260908200906-01: Wissenschaftliche Zusammenfassung

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

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `HUMAN_REVIEW_REQUIRED`
- Begründung: RQ-SNN-001 verwendet das dedizierte Sustained-Activity-Protokoll mit Kontroll- und Tonic-Drive-Bedingung.
- Beobachtete Conditions: `no_input_control, tonic_drive`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: sustained_activity_stability_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `50eb28586c715b0e17872caf016c04c7c38a53dd`
- Git dirty: `False`
- Runtime: `12.007626099977642` s

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

Die Simulationsergebnisse zeigen, dass die neuronale Aktivität unter beiden Bedingungen (kein Input und tonischer Antrieb) über die gesamte Simulationsdauer von 100.000 Ticks hinweg stabil bleibt. Die gemessenen Metriken wie `neuron_v_max`, `neuron_v_min`, `post_burn_in_mean_spikes` und `window_mean_v` zeigen keine offensichtliche numerische Drift oder Instabilität, was die Hypothese H-SNN-001-A stützt, dass Brain-5D stabile Spike-Dynamiken erzeugen kann. Die beobachteten Unterschiede in der Spike-Aktivität zwischen den Bedingungen sind deskriptiv.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Keine expliziten Angaben.

### Alternative Erklaerungen

- Keine expliziten Angaben.

### Fehlende Nachweise

- Statistische Tests (z. B. t-Test oder ANOVA) zur Quantifizierung des Unterschieds in der Spike-Aktivität zwischen den Bedingungen.
- Eine Analyse der Spannungsverteilung (z. B. Histogramme) über die gesamte Simulationsdauer, um die Verteilung der Ruhemembranpotentiale zu bestätigen.

### Empfohlene Folgeexperimente

- Durchführung von Läufen mit variierter Stärke des tonischen Antriebs, um die Abhängigkeit der Spike-Aktivität von der Antriebsstärke zu untersuchen.
- Verlängerung der Simulationsdauer über 100.000 Ticks hinaus, um die Langzeitstabilität unter verschiedenen Belastungsbedingungen zu überprüfen.
- Vergleich der Spike-Dynamik mit anderen Arten von externer Stimulation (z. B. rhythmische oder zufällige Inputs), um die Spezifität des tonischen Antriebs zu klären.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260908201050984542-2240058d.json](analysis/AIAR-critical_reviewer-20260908201050984542-2240058d.json)
- [analysis/AIAR-scientific_analyst-20260908201011214309-2240058d.json](analysis/AIAR-scientific_analyst-20260908201011214309-2240058d.json)
- [analysis/AIAR-scientific_writer-20260908201128464289-2240058d.json](analysis/AIAR-scientific_writer-20260908201128464289-2240058d.json)
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

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
