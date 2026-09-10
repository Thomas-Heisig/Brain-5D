# EXP-BATCH-20260909223705-39: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REG-002`
- Hypothese: `H-REG-002-A`
- Protokoll: `closed_loop_regulation_v1`
- Durchlaeufe: `40`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]`
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

- Titel: Experiment workflow: closed_loop_regulation_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.3609339000104228` s

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
| regulation_off | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 128 | 73 | — | — | — | — |
| regulation_on | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 128 | 67 | — | — | — | — |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `regulation_off`, Vergleich `regulation_on`.
- `total_spikes`: $\Delta=-6$; $R=0.917808$; Referenz `regulation_off`, Vergleich `regulation_on`.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | regulation_off | 128 | 73 | — | — | — | — | — |
| 101 | regulation_on | 128 | 67 | — | — | — | — | — |
| 102 | regulation_off | 128 | 73 | — | — | — | — | — |
| 102 | regulation_on | 128 | 67 | — | — | — | — | — |
| 103 | regulation_off | 128 | 73 | — | — | — | — | — |
| 103 | regulation_on | 128 | 67 | — | — | — | — | — |
| 104 | regulation_off | 128 | 73 | — | — | — | — | — |
| 104 | regulation_on | 128 | 67 | — | — | — | — | — |
| 105 | regulation_off | 128 | 73 | — | — | — | — | — |
| 105 | regulation_on | 128 | 67 | — | — | — | — | — |
| 106 | regulation_off | 128 | 73 | — | — | — | — | — |
| 106 | regulation_on | 128 | 67 | — | — | — | — | — |
| 107 | regulation_off | 128 | 73 | — | — | — | — | — |
| 107 | regulation_on | 128 | 67 | — | — | — | — | — |
| 108 | regulation_off | 128 | 73 | — | — | — | — | — |
| 108 | regulation_on | 128 | 67 | — | — | — | — | — |
| 109 | regulation_off | 128 | 73 | — | — | — | — | — |
| 109 | regulation_on | 128 | 67 | — | — | — | — | — |
| 110 | regulation_off | 128 | 73 | — | — | — | — | — |
| 110 | regulation_on | 128 | 67 | — | — | — | — | — |
| 111 | regulation_off | 128 | 73 | — | — | — | — | — |
| 111 | regulation_on | 128 | 67 | — | — | — | — | — |
| 112 | regulation_off | 128 | 73 | — | — | — | — | — |
| 112 | regulation_on | 128 | 67 | — | — | — | — | — |
| 113 | regulation_off | 128 | 73 | — | — | — | — | — |
| 113 | regulation_on | 128 | 67 | — | — | — | — | — |
| 114 | regulation_off | 128 | 73 | — | — | — | — | — |
| 114 | regulation_on | 128 | 67 | — | — | — | — | — |
| 115 | regulation_off | 128 | 73 | — | — | — | — | — |
| 115 | regulation_on | 128 | 67 | — | — | — | — | — |
| 116 | regulation_off | 128 | 73 | — | — | — | — | — |
| 116 | regulation_on | 128 | 67 | — | — | — | — | — |
| 117 | regulation_off | 128 | 73 | — | — | — | — | — |
| 117 | regulation_on | 128 | 67 | — | — | — | — | — |
| 118 | regulation_off | 128 | 73 | — | — | — | — | — |
| 118 | regulation_on | 128 | 67 | — | — | — | — | — |
| 119 | regulation_off | 128 | 73 | — | — | — | — | — |
| 119 | regulation_on | 128 | 67 | — | — | — | — | — |
| 120 | regulation_off | 128 | 73 | — | — | — | — | — |
| 120 | regulation_on | 128 | 67 | — | — | — | — | — |

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
- [analysis/AIAR-critical_reviewer-20260910014255380047-15ccce08.json](analysis/AIAR-critical_reviewer-20260910014255380047-15ccce08.json)
- [analysis/AIAR-scientific_analyst-20260910014155362101-15ccce08.json](analysis/AIAR-scientific_analyst-20260910014155362101-15ccce08.json)
- [analysis/AIAR-scientific_writer-20260910014355396640-15ccce08.json](analysis/AIAR-scientific_writer-20260910014355396640-15ccce08.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-regulation_off-seed-101.json.gz](DATA/raw/run-0000-regulation_off-seed-101.json.gz)
- [DATA/raw/run-0001-regulation_on-seed-101.json.gz](DATA/raw/run-0001-regulation_on-seed-101.json.gz)
- [DATA/raw/run-0002-regulation_off-seed-102.json.gz](DATA/raw/run-0002-regulation_off-seed-102.json.gz)
- [DATA/raw/run-0003-regulation_on-seed-102.json.gz](DATA/raw/run-0003-regulation_on-seed-102.json.gz)
- [DATA/raw/run-0004-regulation_off-seed-103.json.gz](DATA/raw/run-0004-regulation_off-seed-103.json.gz)
- [DATA/raw/run-0005-regulation_on-seed-103.json.gz](DATA/raw/run-0005-regulation_on-seed-103.json.gz)
- [DATA/raw/run-0006-regulation_off-seed-104.json.gz](DATA/raw/run-0006-regulation_off-seed-104.json.gz)
- [DATA/raw/run-0007-regulation_on-seed-104.json.gz](DATA/raw/run-0007-regulation_on-seed-104.json.gz)
- [DATA/raw/run-0008-regulation_off-seed-105.json.gz](DATA/raw/run-0008-regulation_off-seed-105.json.gz)
- [DATA/raw/run-0009-regulation_on-seed-105.json.gz](DATA/raw/run-0009-regulation_on-seed-105.json.gz)
- [DATA/raw/run-0010-regulation_off-seed-106.json.gz](DATA/raw/run-0010-regulation_off-seed-106.json.gz)
- [DATA/raw/run-0011-regulation_on-seed-106.json.gz](DATA/raw/run-0011-regulation_on-seed-106.json.gz)
- [DATA/raw/run-0012-regulation_off-seed-107.json.gz](DATA/raw/run-0012-regulation_off-seed-107.json.gz)
- [DATA/raw/run-0013-regulation_on-seed-107.json.gz](DATA/raw/run-0013-regulation_on-seed-107.json.gz)
- [DATA/raw/run-0014-regulation_off-seed-108.json.gz](DATA/raw/run-0014-regulation_off-seed-108.json.gz)
- [DATA/raw/run-0015-regulation_on-seed-108.json.gz](DATA/raw/run-0015-regulation_on-seed-108.json.gz)
- [DATA/raw/run-0016-regulation_off-seed-109.json.gz](DATA/raw/run-0016-regulation_off-seed-109.json.gz)
- [DATA/raw/run-0017-regulation_on-seed-109.json.gz](DATA/raw/run-0017-regulation_on-seed-109.json.gz)
- [DATA/raw/run-0018-regulation_off-seed-110.json.gz](DATA/raw/run-0018-regulation_off-seed-110.json.gz)
- [DATA/raw/run-0019-regulation_on-seed-110.json.gz](DATA/raw/run-0019-regulation_on-seed-110.json.gz)
- [DATA/raw/run-0020-regulation_off-seed-111.json.gz](DATA/raw/run-0020-regulation_off-seed-111.json.gz)
- [DATA/raw/run-0021-regulation_on-seed-111.json.gz](DATA/raw/run-0021-regulation_on-seed-111.json.gz)
- [DATA/raw/run-0022-regulation_off-seed-112.json.gz](DATA/raw/run-0022-regulation_off-seed-112.json.gz)
- [DATA/raw/run-0023-regulation_on-seed-112.json.gz](DATA/raw/run-0023-regulation_on-seed-112.json.gz)
- [DATA/raw/run-0024-regulation_off-seed-113.json.gz](DATA/raw/run-0024-regulation_off-seed-113.json.gz)
- [DATA/raw/run-0025-regulation_on-seed-113.json.gz](DATA/raw/run-0025-regulation_on-seed-113.json.gz)
- [DATA/raw/run-0026-regulation_off-seed-114.json.gz](DATA/raw/run-0026-regulation_off-seed-114.json.gz)
- [DATA/raw/run-0027-regulation_on-seed-114.json.gz](DATA/raw/run-0027-regulation_on-seed-114.json.gz)
- [DATA/raw/run-0028-regulation_off-seed-115.json.gz](DATA/raw/run-0028-regulation_off-seed-115.json.gz)
- [DATA/raw/run-0029-regulation_on-seed-115.json.gz](DATA/raw/run-0029-regulation_on-seed-115.json.gz)
- [DATA/raw/run-0030-regulation_off-seed-116.json.gz](DATA/raw/run-0030-regulation_off-seed-116.json.gz)
- [DATA/raw/run-0031-regulation_on-seed-116.json.gz](DATA/raw/run-0031-regulation_on-seed-116.json.gz)
- [DATA/raw/run-0032-regulation_off-seed-117.json.gz](DATA/raw/run-0032-regulation_off-seed-117.json.gz)
- [DATA/raw/run-0033-regulation_on-seed-117.json.gz](DATA/raw/run-0033-regulation_on-seed-117.json.gz)
- [DATA/raw/run-0034-regulation_off-seed-118.json.gz](DATA/raw/run-0034-regulation_off-seed-118.json.gz)
- [DATA/raw/run-0035-regulation_on-seed-118.json.gz](DATA/raw/run-0035-regulation_on-seed-118.json.gz)
- [DATA/raw/run-0036-regulation_off-seed-119.json.gz](DATA/raw/run-0036-regulation_off-seed-119.json.gz)
- [DATA/raw/run-0037-regulation_on-seed-119.json.gz](DATA/raw/run-0037-regulation_on-seed-119.json.gz)
- [DATA/raw/run-0038-regulation_off-seed-120.json.gz](DATA/raw/run-0038-regulation_off-seed-120.json.gz)
- [DATA/raw/run-0039-regulation_on-seed-120.json.gz](DATA/raw/run-0039-regulation_on-seed-120.json.gz)
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
