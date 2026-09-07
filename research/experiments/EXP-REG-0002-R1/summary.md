# EXP-REG-0002-R1: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REG-002`
- Hypothese: `H-REG-002-A`
- Protokoll: `closed_loop_regulation_v1`
- Durchlaeufe: `40`
- Seeds: `[42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]`
- Angeforderte Ticks: `128`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `128 .. 128` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: REG-002 erwartet Regulation-off und Regulation-on unter gleichem Perturbationsplan.
- Beobachtete Conditions: `regulation_off, regulation_on`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Closed-loop regulation recovery v1
- Bedingungen: Regulation off control vs regulation on treatment; nominal-pressure-recovery schedule; seeds 42-61.
- Notizen: Full PREREG-REG-002 seed set.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `1471f1bcff9b6b3a586d57e0a9b086e483fc4d85`
- Git dirty: `True`
- Runtime: `0.20879289996810257` s

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
| regulation_off | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 128 | 73 | — | — | — | — |
| regulation_on | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 128 | 67 | — | — | — | — |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `regulation_off`, Vergleich `regulation_on`.
- `total_spikes`: $\Delta=-6$; $R=0.917808$; Referenz `regulation_off`, Vergleich `regulation_on`.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | regulation_off | 128 | 73 | — | — | — | — | — |
| 42 | regulation_on | 128 | 67 | — | — | — | — | — |
| 43 | regulation_off | 128 | 73 | — | — | — | — | — |
| 43 | regulation_on | 128 | 67 | — | — | — | — | — |
| 44 | regulation_off | 128 | 73 | — | — | — | — | — |
| 44 | regulation_on | 128 | 67 | — | — | — | — | — |
| 45 | regulation_off | 128 | 73 | — | — | — | — | — |
| 45 | regulation_on | 128 | 67 | — | — | — | — | — |
| 46 | regulation_off | 128 | 73 | — | — | — | — | — |
| 46 | regulation_on | 128 | 67 | — | — | — | — | — |
| 47 | regulation_off | 128 | 73 | — | — | — | — | — |
| 47 | regulation_on | 128 | 67 | — | — | — | — | — |
| 48 | regulation_off | 128 | 73 | — | — | — | — | — |
| 48 | regulation_on | 128 | 67 | — | — | — | — | — |
| 49 | regulation_off | 128 | 73 | — | — | — | — | — |
| 49 | regulation_on | 128 | 67 | — | — | — | — | — |
| 50 | regulation_off | 128 | 73 | — | — | — | — | — |
| 50 | regulation_on | 128 | 67 | — | — | — | — | — |
| 51 | regulation_off | 128 | 73 | — | — | — | — | — |
| 51 | regulation_on | 128 | 67 | — | — | — | — | — |
| 52 | regulation_off | 128 | 73 | — | — | — | — | — |
| 52 | regulation_on | 128 | 67 | — | — | — | — | — |
| 53 | regulation_off | 128 | 73 | — | — | — | — | — |
| 53 | regulation_on | 128 | 67 | — | — | — | — | — |
| 54 | regulation_off | 128 | 73 | — | — | — | — | — |
| 54 | regulation_on | 128 | 67 | — | — | — | — | — |
| 55 | regulation_off | 128 | 73 | — | — | — | — | — |
| 55 | regulation_on | 128 | 67 | — | — | — | — | — |
| 56 | regulation_off | 128 | 73 | — | — | — | — | — |
| 56 | regulation_on | 128 | 67 | — | — | — | — | — |
| 57 | regulation_off | 128 | 73 | — | — | — | — | — |
| 57 | regulation_on | 128 | 67 | — | — | — | — | — |
| 58 | regulation_off | 128 | 73 | — | — | — | — | — |
| 58 | regulation_on | 128 | 67 | — | — | — | — | — |
| 59 | regulation_off | 128 | 73 | — | — | — | — | — |
| 59 | regulation_on | 128 | 67 | — | — | — | — | — |
| 60 | regulation_off | 128 | 73 | — | — | — | — | — |
| 60 | regulation_on | 128 | 67 | — | — | — | — | — |
| 61 | regulation_off | 128 | 73 | — | — | — | — | — |
| 61 | regulation_on | 128 | 67 | — | — | — | — | — |

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
- [DATA/raw/run-0000-regulation_off-seed-42.json.gz](DATA/raw/run-0000-regulation_off-seed-42.json.gz)
- [DATA/raw/run-0001-regulation_on-seed-42.json.gz](DATA/raw/run-0001-regulation_on-seed-42.json.gz)
- [DATA/raw/run-0002-regulation_off-seed-43.json.gz](DATA/raw/run-0002-regulation_off-seed-43.json.gz)
- [DATA/raw/run-0003-regulation_on-seed-43.json.gz](DATA/raw/run-0003-regulation_on-seed-43.json.gz)
- [DATA/raw/run-0004-regulation_off-seed-44.json.gz](DATA/raw/run-0004-regulation_off-seed-44.json.gz)
- [DATA/raw/run-0005-regulation_on-seed-44.json.gz](DATA/raw/run-0005-regulation_on-seed-44.json.gz)
- [DATA/raw/run-0006-regulation_off-seed-45.json.gz](DATA/raw/run-0006-regulation_off-seed-45.json.gz)
- [DATA/raw/run-0007-regulation_on-seed-45.json.gz](DATA/raw/run-0007-regulation_on-seed-45.json.gz)
- [DATA/raw/run-0008-regulation_off-seed-46.json.gz](DATA/raw/run-0008-regulation_off-seed-46.json.gz)
- [DATA/raw/run-0009-regulation_on-seed-46.json.gz](DATA/raw/run-0009-regulation_on-seed-46.json.gz)
- [DATA/raw/run-0010-regulation_off-seed-47.json.gz](DATA/raw/run-0010-regulation_off-seed-47.json.gz)
- [DATA/raw/run-0011-regulation_on-seed-47.json.gz](DATA/raw/run-0011-regulation_on-seed-47.json.gz)
- [DATA/raw/run-0012-regulation_off-seed-48.json.gz](DATA/raw/run-0012-regulation_off-seed-48.json.gz)
- [DATA/raw/run-0013-regulation_on-seed-48.json.gz](DATA/raw/run-0013-regulation_on-seed-48.json.gz)
- [DATA/raw/run-0014-regulation_off-seed-49.json.gz](DATA/raw/run-0014-regulation_off-seed-49.json.gz)
- [DATA/raw/run-0015-regulation_on-seed-49.json.gz](DATA/raw/run-0015-regulation_on-seed-49.json.gz)
- [DATA/raw/run-0016-regulation_off-seed-50.json.gz](DATA/raw/run-0016-regulation_off-seed-50.json.gz)
- [DATA/raw/run-0017-regulation_on-seed-50.json.gz](DATA/raw/run-0017-regulation_on-seed-50.json.gz)
- [DATA/raw/run-0018-regulation_off-seed-51.json.gz](DATA/raw/run-0018-regulation_off-seed-51.json.gz)
- [DATA/raw/run-0019-regulation_on-seed-51.json.gz](DATA/raw/run-0019-regulation_on-seed-51.json.gz)
- [DATA/raw/run-0020-regulation_off-seed-52.json.gz](DATA/raw/run-0020-regulation_off-seed-52.json.gz)
- [DATA/raw/run-0021-regulation_on-seed-52.json.gz](DATA/raw/run-0021-regulation_on-seed-52.json.gz)
- [DATA/raw/run-0022-regulation_off-seed-53.json.gz](DATA/raw/run-0022-regulation_off-seed-53.json.gz)
- [DATA/raw/run-0023-regulation_on-seed-53.json.gz](DATA/raw/run-0023-regulation_on-seed-53.json.gz)
- [DATA/raw/run-0024-regulation_off-seed-54.json.gz](DATA/raw/run-0024-regulation_off-seed-54.json.gz)
- [DATA/raw/run-0025-regulation_on-seed-54.json.gz](DATA/raw/run-0025-regulation_on-seed-54.json.gz)
- [DATA/raw/run-0026-regulation_off-seed-55.json.gz](DATA/raw/run-0026-regulation_off-seed-55.json.gz)
- [DATA/raw/run-0027-regulation_on-seed-55.json.gz](DATA/raw/run-0027-regulation_on-seed-55.json.gz)
- [DATA/raw/run-0028-regulation_off-seed-56.json.gz](DATA/raw/run-0028-regulation_off-seed-56.json.gz)
- [DATA/raw/run-0029-regulation_on-seed-56.json.gz](DATA/raw/run-0029-regulation_on-seed-56.json.gz)
- [DATA/raw/run-0030-regulation_off-seed-57.json.gz](DATA/raw/run-0030-regulation_off-seed-57.json.gz)
- [DATA/raw/run-0031-regulation_on-seed-57.json.gz](DATA/raw/run-0031-regulation_on-seed-57.json.gz)
- [DATA/raw/run-0032-regulation_off-seed-58.json.gz](DATA/raw/run-0032-regulation_off-seed-58.json.gz)
- [DATA/raw/run-0033-regulation_on-seed-58.json.gz](DATA/raw/run-0033-regulation_on-seed-58.json.gz)
- [DATA/raw/run-0034-regulation_off-seed-59.json.gz](DATA/raw/run-0034-regulation_off-seed-59.json.gz)
- [DATA/raw/run-0035-regulation_on-seed-59.json.gz](DATA/raw/run-0035-regulation_on-seed-59.json.gz)
- [DATA/raw/run-0036-regulation_off-seed-60.json.gz](DATA/raw/run-0036-regulation_off-seed-60.json.gz)
- [DATA/raw/run-0037-regulation_on-seed-60.json.gz](DATA/raw/run-0037-regulation_on-seed-60.json.gz)
- [DATA/raw/run-0038-regulation_off-seed-61.json.gz](DATA/raw/run-0038-regulation_off-seed-61.json.gz)
- [DATA/raw/run-0039-regulation_on-seed-61.json.gz](DATA/raw/run-0039-regulation_on-seed-61.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
