# EXP-BATCH-20260909223705-43: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-LIFE-001`
- Hypothese: `H-LIFE-001-A`
- Protokoll: `learning_interference_screen_v1`
- Durchlaeufe: `20`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]`
- Angeforderte Ticks: `1000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `nicht direkt messbar .. nicht direkt messbar` ausgeführte Ticks
- Tick-Vertrag: `NOT_APPLICABLE`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: LEARN-INTERF-001 v1 ist ein explizit als Vorläufer markierter Interferenz-Screen.
- Beobachtete Conditions: `sequential_three_task_screen`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: learning_interference_screen_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `5.525580000001355` s

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
| sequential_three_task_screen | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 102 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 103 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 104 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 105 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 106 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 107 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 108 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 109 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 110 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 111 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 112 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 113 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 114 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 115 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 116 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 117 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 118 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 119 | sequential_three_task_screen | — | — | — | — | — | — | — |
| 120 | sequential_three_task_screen | — | — | — | — | — | — | — |

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

Die Rolle scientific_writer konnte nicht ausgeführt werden. Es liegt keine schema-konforme Modellanalyse vor.

KI-Konfidenz: `0.0` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- AI analysis unavailable; deterministic experiment artifacts remain the authoritative data basis.
- Technical reason: TimeoutError: timed out

### Alternative Erklaerungen

- Keine expliziten Angaben.

### Fehlende Nachweise

- Run the role again with a schema-conforming backend response.
- Complete mandatory human review before interpreting this report.

### Empfohlene Folgeexperimente

- Keine expliziten Folgeexperimente im AIRR angegeben.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260910015505726059-da576c2d.json](analysis/AIAR-critical_reviewer-20260910015505726059-da576c2d.json)
- [analysis/AIAR-scientific_analyst-20260910015405698719-da576c2d.json](analysis/AIAR-scientific_analyst-20260910015405698719-da576c2d.json)
- [analysis/AIAR-scientific_writer-20260910015605740932-da576c2d.json](analysis/AIAR-scientific_writer-20260910015605740932-da576c2d.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-sequential_three_task_screen-seed-101.json.gz](DATA/raw/run-0000-sequential_three_task_screen-seed-101.json.gz)
- [DATA/raw/run-0001-sequential_three_task_screen-seed-102.json.gz](DATA/raw/run-0001-sequential_three_task_screen-seed-102.json.gz)
- [DATA/raw/run-0002-sequential_three_task_screen-seed-103.json.gz](DATA/raw/run-0002-sequential_three_task_screen-seed-103.json.gz)
- [DATA/raw/run-0003-sequential_three_task_screen-seed-104.json.gz](DATA/raw/run-0003-sequential_three_task_screen-seed-104.json.gz)
- [DATA/raw/run-0004-sequential_three_task_screen-seed-105.json.gz](DATA/raw/run-0004-sequential_three_task_screen-seed-105.json.gz)
- [DATA/raw/run-0005-sequential_three_task_screen-seed-106.json.gz](DATA/raw/run-0005-sequential_three_task_screen-seed-106.json.gz)
- [DATA/raw/run-0006-sequential_three_task_screen-seed-107.json.gz](DATA/raw/run-0006-sequential_three_task_screen-seed-107.json.gz)
- [DATA/raw/run-0007-sequential_three_task_screen-seed-108.json.gz](DATA/raw/run-0007-sequential_three_task_screen-seed-108.json.gz)
- [DATA/raw/run-0008-sequential_three_task_screen-seed-109.json.gz](DATA/raw/run-0008-sequential_three_task_screen-seed-109.json.gz)
- [DATA/raw/run-0009-sequential_three_task_screen-seed-110.json.gz](DATA/raw/run-0009-sequential_three_task_screen-seed-110.json.gz)
- [DATA/raw/run-0010-sequential_three_task_screen-seed-111.json.gz](DATA/raw/run-0010-sequential_three_task_screen-seed-111.json.gz)
- [DATA/raw/run-0011-sequential_three_task_screen-seed-112.json.gz](DATA/raw/run-0011-sequential_three_task_screen-seed-112.json.gz)
- [DATA/raw/run-0012-sequential_three_task_screen-seed-113.json.gz](DATA/raw/run-0012-sequential_three_task_screen-seed-113.json.gz)
- [DATA/raw/run-0013-sequential_three_task_screen-seed-114.json.gz](DATA/raw/run-0013-sequential_three_task_screen-seed-114.json.gz)
- [DATA/raw/run-0014-sequential_three_task_screen-seed-115.json.gz](DATA/raw/run-0014-sequential_three_task_screen-seed-115.json.gz)
- [DATA/raw/run-0015-sequential_three_task_screen-seed-116.json.gz](DATA/raw/run-0015-sequential_three_task_screen-seed-116.json.gz)
- [DATA/raw/run-0016-sequential_three_task_screen-seed-117.json.gz](DATA/raw/run-0016-sequential_three_task_screen-seed-117.json.gz)
- [DATA/raw/run-0017-sequential_three_task_screen-seed-118.json.gz](DATA/raw/run-0017-sequential_three_task_screen-seed-118.json.gz)
- [DATA/raw/run-0018-sequential_three_task_screen-seed-119.json.gz](DATA/raw/run-0018-sequential_three_task_screen-seed-119.json.gz)
- [DATA/raw/run-0019-sequential_three_task_screen-seed-120.json.gz](DATA/raw/run-0019-sequential_three_task_screen-seed-120.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [reports/AIRR-2026-0001.json](reports/AIRR-2026-0001.json)
- [reports/AIRR-2026-0001.md](reports/AIRR-2026-0001.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `NOT_APPLICABLE`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
