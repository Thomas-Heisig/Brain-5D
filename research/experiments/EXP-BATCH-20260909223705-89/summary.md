# EXP-BATCH-20260909223705-89: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-MSBA-E05`
- Hypothese: `H-MSBA-E05-A`
- Protokoll: `msba_modality_compensation_v1`
- Durchlaeufe: `12`
- Seeds: `[101, 102, 103]`
- Angeforderte Ticks: `48`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `nicht direkt messbar .. nicht direkt messbar` ausgeführte Ticks
- Tick-Vertrag: `NOT_APPLICABLE`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `NOT_AUTOMATICALLY_CLASSIFIED`
- Evidence Readiness: `BLOCKED_UNCLASSIFIED_SEMANTICS`
- Begründung: Keine automatische semantische Regel fuer diese RQ-Familie registriert.
- Beobachtete Conditions: `adaptive_compensation, fixed_allocation, no_compensation, shuffled_utility`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: msba_modality_compensation_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.04224310000427067` s

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
| adaptive_compensation | 3 | 101,102,103 | — | — | — | — | — | — |
| fixed_allocation | 3 | 101,102,103 | — | — | — | — | — | — |
| no_compensation | 3 | 101,102,103 | — | — | — | — | — | — |
| shuffled_utility | 3 | 101,102,103 | — | — | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | adaptive_compensation | — | — | — | — | — | — | — |
| 101 | fixed_allocation | — | — | — | — | — | — | — |
| 101 | shuffled_utility | — | — | — | — | — | — | — |
| 101 | no_compensation | — | — | — | — | — | — | — |
| 102 | adaptive_compensation | — | — | — | — | — | — | — |
| 102 | fixed_allocation | — | — | — | — | — | — | — |
| 102 | shuffled_utility | — | — | — | — | — | — | — |
| 102 | no_compensation | — | — | — | — | — | — | — |
| 103 | adaptive_compensation | — | — | — | — | — | — | — |
| 103 | fixed_allocation | — | — | — | — | — | — | — |
| 103 | shuffled_utility | — | — | — | — | — | — | — |
| 103 | no_compensation | — | — | — | — | — | — | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `failed`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

AIRR-Fehler: `Research registry entry not found: RQ-MSBA-E05`. Die deterministische Datenauswertung oben bleibt davon unberuehrt.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/gateway_state.json](DATA/gateway_state.json)
- [DATA/raw/run-0000-adaptive_compensation-seed-101.json.gz](DATA/raw/run-0000-adaptive_compensation-seed-101.json.gz)
- [DATA/raw/run-0001-fixed_allocation-seed-101.json.gz](DATA/raw/run-0001-fixed_allocation-seed-101.json.gz)
- [DATA/raw/run-0002-shuffled_utility-seed-101.json.gz](DATA/raw/run-0002-shuffled_utility-seed-101.json.gz)
- [DATA/raw/run-0003-no_compensation-seed-101.json.gz](DATA/raw/run-0003-no_compensation-seed-101.json.gz)
- [DATA/raw/run-0004-adaptive_compensation-seed-102.json.gz](DATA/raw/run-0004-adaptive_compensation-seed-102.json.gz)
- [DATA/raw/run-0005-fixed_allocation-seed-102.json.gz](DATA/raw/run-0005-fixed_allocation-seed-102.json.gz)
- [DATA/raw/run-0006-shuffled_utility-seed-102.json.gz](DATA/raw/run-0006-shuffled_utility-seed-102.json.gz)
- [DATA/raw/run-0007-no_compensation-seed-102.json.gz](DATA/raw/run-0007-no_compensation-seed-102.json.gz)
- [DATA/raw/run-0008-adaptive_compensation-seed-103.json.gz](DATA/raw/run-0008-adaptive_compensation-seed-103.json.gz)
- [DATA/raw/run-0009-fixed_allocation-seed-103.json.gz](DATA/raw/run-0009-fixed_allocation-seed-103.json.gz)
- [DATA/raw/run-0010-shuffled_utility-seed-103.json.gz](DATA/raw/run-0010-shuffled_utility-seed-103.json.gz)
- [DATA/raw/run-0011-no_compensation-seed-103.json.gz](DATA/raw/run-0011-no_compensation-seed-103.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `NOT_APPLICABLE`, semantische Zuordnung `NOT_AUTOMATICALLY_CLASSIFIED`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
