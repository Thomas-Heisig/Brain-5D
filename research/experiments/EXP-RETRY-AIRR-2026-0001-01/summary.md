# EXP-RETRY-AIRR-2026-0001-01: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REPL-001`
- Hypothese: `H-REPL-001-A`
- Protokoll: `independent_replication_v1`
- Durchlaeufe: `40`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]`
- Angeforderte Ticks: `256`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `256 .. 256` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `REPLICATION`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: REPL-001 erwartet beide Rekurrenzarme mit unabhängiger Seedstrategie.
- Beobachtete Conditions: `recurrence_off, recurrence_on`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Recovered experiment workflow: independent_replication_v1
- Bedingungen: Recovered registered protocol conditions
- Notizen: Recovery batch for failed children of EXP-BATCH-20260906200118. The historical workflow remains unchanged; this retry is a new execution lineage.
- Konfiguration: `/home/runner/work/MHRN/MHRN/configs/learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `a8b5ea31b92e263c63acd0e83d7dda2d856a6dc6`
- Git dirty: `True`
- Runtime: `0.1597151259999947` s

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
| recurrence_off | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 3 | 2 | 3 | 0 | 1 |
| recurrence_on | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 33 | 33 | 3 | 10 | 61 |

### 5.1 Deskriptive Zwei-Bedingungs-Effekte

- `activated_neurons`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `delivered_synaptic_events`: $\Delta=31$; $R=16.5$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `first_response_latency`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `last_response_latency`: $\Delta=60$; $R=31$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `propagation_depth`: $\Delta=60$; $R=61$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `recurrent_events`: $\Delta=10$; $R=—$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `synaptic_activity_ticks`: $\Delta=31$; $R=16.5$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `ticks_executed`: $\Delta=0$; $R=1$; Referenz `recurrence_off`, Vergleich `recurrence_on`.
- `total_spikes`: $\Delta=30$; $R=11$; Referenz `recurrence_off`, Vergleich `recurrence_on`.

### 5.2 Inter-Spike-Intervalle

- `recurrence_off`: n=40, mean=1, median=1, min=1, max=1 Ticks.
- `recurrence_on`: n=640, mean=1.9375, median=2, min=1, max=4 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 102 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 103 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 104 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 105 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 106 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 107 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 108 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 109 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 110 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 111 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 112 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 113 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 114 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 115 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 116 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 117 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 118 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 119 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 120 | recurrence_off | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | recurrence_on | 256 | 33 | 33 | 3 | 10 | 61 | — |

## 7. Reproduzierbarkeit und Provenienz

Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.

Deterministische Statistikdatei: [`analysis/statistics.json`](analysis/statistics.json)

## 8. AI Research Report

- AIRR Status: `unavailable`
- Wissenschaftliche Evidenz durch KI: `false`
- Human Review: `PENDING`

## 9. Artefakte

- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-recurrence_off-seed-101.json.gz](DATA/raw/run-0000-recurrence_off-seed-101.json.gz)
- [DATA/raw/run-0001-recurrence_on-seed-101.json.gz](DATA/raw/run-0001-recurrence_on-seed-101.json.gz)
- [DATA/raw/run-0002-recurrence_off-seed-102.json.gz](DATA/raw/run-0002-recurrence_off-seed-102.json.gz)
- [DATA/raw/run-0003-recurrence_on-seed-102.json.gz](DATA/raw/run-0003-recurrence_on-seed-102.json.gz)
- [DATA/raw/run-0004-recurrence_off-seed-103.json.gz](DATA/raw/run-0004-recurrence_off-seed-103.json.gz)
- [DATA/raw/run-0005-recurrence_on-seed-103.json.gz](DATA/raw/run-0005-recurrence_on-seed-103.json.gz)
- [DATA/raw/run-0006-recurrence_off-seed-104.json.gz](DATA/raw/run-0006-recurrence_off-seed-104.json.gz)
- [DATA/raw/run-0007-recurrence_on-seed-104.json.gz](DATA/raw/run-0007-recurrence_on-seed-104.json.gz)
- [DATA/raw/run-0008-recurrence_off-seed-105.json.gz](DATA/raw/run-0008-recurrence_off-seed-105.json.gz)
- [DATA/raw/run-0009-recurrence_on-seed-105.json.gz](DATA/raw/run-0009-recurrence_on-seed-105.json.gz)
- [DATA/raw/run-0010-recurrence_off-seed-106.json.gz](DATA/raw/run-0010-recurrence_off-seed-106.json.gz)
- [DATA/raw/run-0011-recurrence_on-seed-106.json.gz](DATA/raw/run-0011-recurrence_on-seed-106.json.gz)
- [DATA/raw/run-0012-recurrence_off-seed-107.json.gz](DATA/raw/run-0012-recurrence_off-seed-107.json.gz)
- [DATA/raw/run-0013-recurrence_on-seed-107.json.gz](DATA/raw/run-0013-recurrence_on-seed-107.json.gz)
- [DATA/raw/run-0014-recurrence_off-seed-108.json.gz](DATA/raw/run-0014-recurrence_off-seed-108.json.gz)
- [DATA/raw/run-0015-recurrence_on-seed-108.json.gz](DATA/raw/run-0015-recurrence_on-seed-108.json.gz)
- [DATA/raw/run-0016-recurrence_off-seed-109.json.gz](DATA/raw/run-0016-recurrence_off-seed-109.json.gz)
- [DATA/raw/run-0017-recurrence_on-seed-109.json.gz](DATA/raw/run-0017-recurrence_on-seed-109.json.gz)
- [DATA/raw/run-0018-recurrence_off-seed-110.json.gz](DATA/raw/run-0018-recurrence_off-seed-110.json.gz)
- [DATA/raw/run-0019-recurrence_on-seed-110.json.gz](DATA/raw/run-0019-recurrence_on-seed-110.json.gz)
- [DATA/raw/run-0020-recurrence_off-seed-111.json.gz](DATA/raw/run-0020-recurrence_off-seed-111.json.gz)
- [DATA/raw/run-0021-recurrence_on-seed-111.json.gz](DATA/raw/run-0021-recurrence_on-seed-111.json.gz)
- [DATA/raw/run-0022-recurrence_off-seed-112.json.gz](DATA/raw/run-0022-recurrence_off-seed-112.json.gz)
- [DATA/raw/run-0023-recurrence_on-seed-112.json.gz](DATA/raw/run-0023-recurrence_on-seed-112.json.gz)
- [DATA/raw/run-0024-recurrence_off-seed-113.json.gz](DATA/raw/run-0024-recurrence_off-seed-113.json.gz)
- [DATA/raw/run-0025-recurrence_on-seed-113.json.gz](DATA/raw/run-0025-recurrence_on-seed-113.json.gz)
- [DATA/raw/run-0026-recurrence_off-seed-114.json.gz](DATA/raw/run-0026-recurrence_off-seed-114.json.gz)
- [DATA/raw/run-0027-recurrence_on-seed-114.json.gz](DATA/raw/run-0027-recurrence_on-seed-114.json.gz)
- [DATA/raw/run-0028-recurrence_off-seed-115.json.gz](DATA/raw/run-0028-recurrence_off-seed-115.json.gz)
- [DATA/raw/run-0029-recurrence_on-seed-115.json.gz](DATA/raw/run-0029-recurrence_on-seed-115.json.gz)
- [DATA/raw/run-0030-recurrence_off-seed-116.json.gz](DATA/raw/run-0030-recurrence_off-seed-116.json.gz)
- [DATA/raw/run-0031-recurrence_on-seed-116.json.gz](DATA/raw/run-0031-recurrence_on-seed-116.json.gz)
- [DATA/raw/run-0032-recurrence_off-seed-117.json.gz](DATA/raw/run-0032-recurrence_off-seed-117.json.gz)
- [DATA/raw/run-0033-recurrence_on-seed-117.json.gz](DATA/raw/run-0033-recurrence_on-seed-117.json.gz)
- [DATA/raw/run-0034-recurrence_off-seed-118.json.gz](DATA/raw/run-0034-recurrence_off-seed-118.json.gz)
- [DATA/raw/run-0035-recurrence_on-seed-118.json.gz](DATA/raw/run-0035-recurrence_on-seed-118.json.gz)
- [DATA/raw/run-0036-recurrence_off-seed-119.json.gz](DATA/raw/run-0036-recurrence_off-seed-119.json.gz)
- [DATA/raw/run-0037-recurrence_on-seed-119.json.gz](DATA/raw/run-0037-recurrence_on-seed-119.json.gz)
- [DATA/raw/run-0038-recurrence_off-seed-120.json.gz](DATA/raw/run-0038-recurrence_off-seed-120.json.gz)
- [DATA/raw/run-0039-recurrence_on-seed-120.json.gz](DATA/raw/run-0039-recurrence_on-seed-120.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/statistics.json](analysis/statistics.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
