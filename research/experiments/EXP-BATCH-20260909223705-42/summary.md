# EXP-BATCH-20260909223705-42: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REC-002`
- Hypothese: `H-REC-002-A`
- Protokoll: `recurrence_scale_v1`
- Durchlaeufe: `80`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]`
- Angeforderte Ticks: `256`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `256 .. 256` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: REC-002 erwartet die registrierte Loop-Delay-Leiter.
- Beobachtete Conditions: `loop_delay_1, loop_delay_2, loop_delay_4, loop_delay_8`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: recurrence_scale_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `8184fc74654169e4d01552f093dd807f065c34e3`
- Git dirty: `True`
- Runtime: `0.29080570000223815` s

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
| loop_delay_1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 33 | 33 | 3 | 10 | 61 |
| loop_delay_2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 102 | 102 | 3 | 33 | 251 |
| loop_delay_4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 87 | 87 | 3 | 28 | 250 |
| loop_delay_8 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 61 | 61 | 3 | 20 | 244 |

### 5.2 Inter-Spike-Intervalle

- `loop_delay_1`: n=640, mean=1.9375, median=2, min=1, max=4 Ticks.
- `loop_delay_2`: n=2020, mean=2.49505, median=2, min=1, max=4 Ticks.
- `loop_delay_4`: n=1720, mean=2.9186, median=2, min=1, max=5 Ticks.
- `loop_delay_8`: n=1200, mean=4.23333, median=2, min=1, max=9 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 101 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 101 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 101 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 102 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 102 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 102 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 102 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 103 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 103 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 103 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 103 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 104 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 104 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 104 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 104 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 105 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 105 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 105 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 105 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 106 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 106 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 106 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 106 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 107 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 107 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 107 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 107 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 108 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 108 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 108 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 108 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 109 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 109 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 109 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 109 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 110 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 110 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 110 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 110 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 111 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 111 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 111 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 111 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 112 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 112 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 112 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 112 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 113 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 113 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 113 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 113 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 114 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 114 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 114 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 114 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 115 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 115 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 115 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 115 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 116 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 116 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 116 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 116 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 117 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 117 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 117 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 117 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 118 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 118 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 118 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 118 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 119 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 119 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 119 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 119 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |
| 120 | loop_delay_1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 120 | loop_delay_2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 120 | loop_delay_4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 120 | loop_delay_8 | 256 | 61 | 61 | 3 | 20 | 244 | — |

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
- [analysis/AIAR-critical_reviewer-20260910015159571009-14e549a1.json](analysis/AIAR-critical_reviewer-20260910015159571009-14e549a1.json)
- [analysis/AIAR-scientific_analyst-20260910015059546682-14e549a1.json](analysis/AIAR-scientific_analyst-20260910015059546682-14e549a1.json)
- [analysis/AIAR-scientific_writer-20260910015259596418-14e549a1.json](analysis/AIAR-scientific_writer-20260910015259596418-14e549a1.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-loop_delay_1-seed-101.json.gz](DATA/raw/run-0000-loop_delay_1-seed-101.json.gz)
- [DATA/raw/run-0001-loop_delay_2-seed-101.json.gz](DATA/raw/run-0001-loop_delay_2-seed-101.json.gz)
- [DATA/raw/run-0002-loop_delay_4-seed-101.json.gz](DATA/raw/run-0002-loop_delay_4-seed-101.json.gz)
- [DATA/raw/run-0003-loop_delay_8-seed-101.json.gz](DATA/raw/run-0003-loop_delay_8-seed-101.json.gz)
- [DATA/raw/run-0004-loop_delay_1-seed-102.json.gz](DATA/raw/run-0004-loop_delay_1-seed-102.json.gz)
- [DATA/raw/run-0005-loop_delay_2-seed-102.json.gz](DATA/raw/run-0005-loop_delay_2-seed-102.json.gz)
- [DATA/raw/run-0006-loop_delay_4-seed-102.json.gz](DATA/raw/run-0006-loop_delay_4-seed-102.json.gz)
- [DATA/raw/run-0007-loop_delay_8-seed-102.json.gz](DATA/raw/run-0007-loop_delay_8-seed-102.json.gz)
- [DATA/raw/run-0008-loop_delay_1-seed-103.json.gz](DATA/raw/run-0008-loop_delay_1-seed-103.json.gz)
- [DATA/raw/run-0009-loop_delay_2-seed-103.json.gz](DATA/raw/run-0009-loop_delay_2-seed-103.json.gz)
- [DATA/raw/run-0010-loop_delay_4-seed-103.json.gz](DATA/raw/run-0010-loop_delay_4-seed-103.json.gz)
- [DATA/raw/run-0011-loop_delay_8-seed-103.json.gz](DATA/raw/run-0011-loop_delay_8-seed-103.json.gz)
- [DATA/raw/run-0012-loop_delay_1-seed-104.json.gz](DATA/raw/run-0012-loop_delay_1-seed-104.json.gz)
- [DATA/raw/run-0013-loop_delay_2-seed-104.json.gz](DATA/raw/run-0013-loop_delay_2-seed-104.json.gz)
- [DATA/raw/run-0014-loop_delay_4-seed-104.json.gz](DATA/raw/run-0014-loop_delay_4-seed-104.json.gz)
- [DATA/raw/run-0015-loop_delay_8-seed-104.json.gz](DATA/raw/run-0015-loop_delay_8-seed-104.json.gz)
- [DATA/raw/run-0016-loop_delay_1-seed-105.json.gz](DATA/raw/run-0016-loop_delay_1-seed-105.json.gz)
- [DATA/raw/run-0017-loop_delay_2-seed-105.json.gz](DATA/raw/run-0017-loop_delay_2-seed-105.json.gz)
- [DATA/raw/run-0018-loop_delay_4-seed-105.json.gz](DATA/raw/run-0018-loop_delay_4-seed-105.json.gz)
- [DATA/raw/run-0019-loop_delay_8-seed-105.json.gz](DATA/raw/run-0019-loop_delay_8-seed-105.json.gz)
- [DATA/raw/run-0020-loop_delay_1-seed-106.json.gz](DATA/raw/run-0020-loop_delay_1-seed-106.json.gz)
- [DATA/raw/run-0021-loop_delay_2-seed-106.json.gz](DATA/raw/run-0021-loop_delay_2-seed-106.json.gz)
- [DATA/raw/run-0022-loop_delay_4-seed-106.json.gz](DATA/raw/run-0022-loop_delay_4-seed-106.json.gz)
- [DATA/raw/run-0023-loop_delay_8-seed-106.json.gz](DATA/raw/run-0023-loop_delay_8-seed-106.json.gz)
- [DATA/raw/run-0024-loop_delay_1-seed-107.json.gz](DATA/raw/run-0024-loop_delay_1-seed-107.json.gz)
- [DATA/raw/run-0025-loop_delay_2-seed-107.json.gz](DATA/raw/run-0025-loop_delay_2-seed-107.json.gz)
- [DATA/raw/run-0026-loop_delay_4-seed-107.json.gz](DATA/raw/run-0026-loop_delay_4-seed-107.json.gz)
- [DATA/raw/run-0027-loop_delay_8-seed-107.json.gz](DATA/raw/run-0027-loop_delay_8-seed-107.json.gz)
- [DATA/raw/run-0028-loop_delay_1-seed-108.json.gz](DATA/raw/run-0028-loop_delay_1-seed-108.json.gz)
- [DATA/raw/run-0029-loop_delay_2-seed-108.json.gz](DATA/raw/run-0029-loop_delay_2-seed-108.json.gz)
- [DATA/raw/run-0030-loop_delay_4-seed-108.json.gz](DATA/raw/run-0030-loop_delay_4-seed-108.json.gz)
- [DATA/raw/run-0031-loop_delay_8-seed-108.json.gz](DATA/raw/run-0031-loop_delay_8-seed-108.json.gz)
- [DATA/raw/run-0032-loop_delay_1-seed-109.json.gz](DATA/raw/run-0032-loop_delay_1-seed-109.json.gz)
- [DATA/raw/run-0033-loop_delay_2-seed-109.json.gz](DATA/raw/run-0033-loop_delay_2-seed-109.json.gz)
- [DATA/raw/run-0034-loop_delay_4-seed-109.json.gz](DATA/raw/run-0034-loop_delay_4-seed-109.json.gz)
- [DATA/raw/run-0035-loop_delay_8-seed-109.json.gz](DATA/raw/run-0035-loop_delay_8-seed-109.json.gz)
- [DATA/raw/run-0036-loop_delay_1-seed-110.json.gz](DATA/raw/run-0036-loop_delay_1-seed-110.json.gz)
- [DATA/raw/run-0037-loop_delay_2-seed-110.json.gz](DATA/raw/run-0037-loop_delay_2-seed-110.json.gz)
- [DATA/raw/run-0038-loop_delay_4-seed-110.json.gz](DATA/raw/run-0038-loop_delay_4-seed-110.json.gz)
- [DATA/raw/run-0039-loop_delay_8-seed-110.json.gz](DATA/raw/run-0039-loop_delay_8-seed-110.json.gz)
- [DATA/raw/run-0040-loop_delay_1-seed-111.json.gz](DATA/raw/run-0040-loop_delay_1-seed-111.json.gz)
- [DATA/raw/run-0041-loop_delay_2-seed-111.json.gz](DATA/raw/run-0041-loop_delay_2-seed-111.json.gz)
- [DATA/raw/run-0042-loop_delay_4-seed-111.json.gz](DATA/raw/run-0042-loop_delay_4-seed-111.json.gz)
- [DATA/raw/run-0043-loop_delay_8-seed-111.json.gz](DATA/raw/run-0043-loop_delay_8-seed-111.json.gz)
- [DATA/raw/run-0044-loop_delay_1-seed-112.json.gz](DATA/raw/run-0044-loop_delay_1-seed-112.json.gz)
- [DATA/raw/run-0045-loop_delay_2-seed-112.json.gz](DATA/raw/run-0045-loop_delay_2-seed-112.json.gz)
- [DATA/raw/run-0046-loop_delay_4-seed-112.json.gz](DATA/raw/run-0046-loop_delay_4-seed-112.json.gz)
- [DATA/raw/run-0047-loop_delay_8-seed-112.json.gz](DATA/raw/run-0047-loop_delay_8-seed-112.json.gz)
- [DATA/raw/run-0048-loop_delay_1-seed-113.json.gz](DATA/raw/run-0048-loop_delay_1-seed-113.json.gz)
- [DATA/raw/run-0049-loop_delay_2-seed-113.json.gz](DATA/raw/run-0049-loop_delay_2-seed-113.json.gz)
- [DATA/raw/run-0050-loop_delay_4-seed-113.json.gz](DATA/raw/run-0050-loop_delay_4-seed-113.json.gz)
- [DATA/raw/run-0051-loop_delay_8-seed-113.json.gz](DATA/raw/run-0051-loop_delay_8-seed-113.json.gz)
- [DATA/raw/run-0052-loop_delay_1-seed-114.json.gz](DATA/raw/run-0052-loop_delay_1-seed-114.json.gz)
- [DATA/raw/run-0053-loop_delay_2-seed-114.json.gz](DATA/raw/run-0053-loop_delay_2-seed-114.json.gz)
- [DATA/raw/run-0054-loop_delay_4-seed-114.json.gz](DATA/raw/run-0054-loop_delay_4-seed-114.json.gz)
- [DATA/raw/run-0055-loop_delay_8-seed-114.json.gz](DATA/raw/run-0055-loop_delay_8-seed-114.json.gz)
- [DATA/raw/run-0056-loop_delay_1-seed-115.json.gz](DATA/raw/run-0056-loop_delay_1-seed-115.json.gz)
- [DATA/raw/run-0057-loop_delay_2-seed-115.json.gz](DATA/raw/run-0057-loop_delay_2-seed-115.json.gz)
- [DATA/raw/run-0058-loop_delay_4-seed-115.json.gz](DATA/raw/run-0058-loop_delay_4-seed-115.json.gz)
- [DATA/raw/run-0059-loop_delay_8-seed-115.json.gz](DATA/raw/run-0059-loop_delay_8-seed-115.json.gz)
- [DATA/raw/run-0060-loop_delay_1-seed-116.json.gz](DATA/raw/run-0060-loop_delay_1-seed-116.json.gz)
- [DATA/raw/run-0061-loop_delay_2-seed-116.json.gz](DATA/raw/run-0061-loop_delay_2-seed-116.json.gz)
- [DATA/raw/run-0062-loop_delay_4-seed-116.json.gz](DATA/raw/run-0062-loop_delay_4-seed-116.json.gz)
- [DATA/raw/run-0063-loop_delay_8-seed-116.json.gz](DATA/raw/run-0063-loop_delay_8-seed-116.json.gz)
- [DATA/raw/run-0064-loop_delay_1-seed-117.json.gz](DATA/raw/run-0064-loop_delay_1-seed-117.json.gz)
- [DATA/raw/run-0065-loop_delay_2-seed-117.json.gz](DATA/raw/run-0065-loop_delay_2-seed-117.json.gz)
- [DATA/raw/run-0066-loop_delay_4-seed-117.json.gz](DATA/raw/run-0066-loop_delay_4-seed-117.json.gz)
- [DATA/raw/run-0067-loop_delay_8-seed-117.json.gz](DATA/raw/run-0067-loop_delay_8-seed-117.json.gz)
- [DATA/raw/run-0068-loop_delay_1-seed-118.json.gz](DATA/raw/run-0068-loop_delay_1-seed-118.json.gz)
- [DATA/raw/run-0069-loop_delay_2-seed-118.json.gz](DATA/raw/run-0069-loop_delay_2-seed-118.json.gz)
- [DATA/raw/run-0070-loop_delay_4-seed-118.json.gz](DATA/raw/run-0070-loop_delay_4-seed-118.json.gz)
- [DATA/raw/run-0071-loop_delay_8-seed-118.json.gz](DATA/raw/run-0071-loop_delay_8-seed-118.json.gz)
- [DATA/raw/run-0072-loop_delay_1-seed-119.json.gz](DATA/raw/run-0072-loop_delay_1-seed-119.json.gz)
- [DATA/raw/run-0073-loop_delay_2-seed-119.json.gz](DATA/raw/run-0073-loop_delay_2-seed-119.json.gz)
- [DATA/raw/run-0074-loop_delay_4-seed-119.json.gz](DATA/raw/run-0074-loop_delay_4-seed-119.json.gz)
- [DATA/raw/run-0075-loop_delay_8-seed-119.json.gz](DATA/raw/run-0075-loop_delay_8-seed-119.json.gz)
- [DATA/raw/run-0076-loop_delay_1-seed-120.json.gz](DATA/raw/run-0076-loop_delay_1-seed-120.json.gz)
- [DATA/raw/run-0077-loop_delay_2-seed-120.json.gz](DATA/raw/run-0077-loop_delay_2-seed-120.json.gz)
- [DATA/raw/run-0078-loop_delay_4-seed-120.json.gz](DATA/raw/run-0078-loop_delay_4-seed-120.json.gz)
- [DATA/raw/run-0079-loop_delay_8-seed-120.json.gz](DATA/raw/run-0079-loop_delay_8-seed-120.json.gz)
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
