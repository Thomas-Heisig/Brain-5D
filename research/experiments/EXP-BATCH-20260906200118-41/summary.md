# EXP-BATCH-20260906200118-41: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-PERF-001`
- Hypothese: `H-PERF-001-A`
- Protokoll: `subsystem_performance_v1`
- Durchlaeufe: `10`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110]`
- Angeforderte Ticks: `10000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `10000 .. 10000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: PERF-001 erwartet subsystemaufgelöste Runtime-Messungen.
- Beobachtete Conditions: `subsystem_profile`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: subsystem_performance_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `275f3b77df6e89cc224d8542454434ff7e84d7a4`
- Git dirty: `True`
- Runtime: `0.4669908999931067` s

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
| subsystem_profile | 10 | 101,102,103,104,105,106,107,108,109,110 | 10000 | 33 | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 102 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 103 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 104 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 105 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 106 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 107 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 108 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 109 | subsystem_profile | 10000 | 33 | — | — | — | — | — |
| 110 | subsystem_profile | 10000 | 33 | — | — | — | — | — |

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

Die gemessenen Gesamtlaufzeiten (measured_total_seconds) zeigen eine deutliche Streuung über die 10 Seeds hinweg, was auf eine nicht-konstante Systemleistung oder die Dominanz eines variablen Subsystems hindeutet. Insbesondere der Lauf mit Seed 107 weist mit 0.06275080004706979 Sekunden den höchsten Wert auf, während der Lauf mit Seed 101 mit 0.04312670009676367 Sekunden den niedrigsten Wert aufweist. Der Durchschnitt der gemessenen Gesamtzeit beträgt 0.04461440001614392 Sekunden. Die Analyse der Komponenten zeigt, dass die 'core_step_seconds' (Variationsbereich: 0.04176050005480647 bis 0.062398800044320524) einen signifikanten Beitrag zur Gesamtvariabilität leisten, da der höchste Wert (Seed 107) einen überproportionalen Anteil an der Gesamtzeit ausmacht. Die 'digest_seconds' zeigen hingegen eine geringere Variabilität (Variationsbereich: 0.00019690010230988264 bis 0.00039249996189028025).

KI-Konfidenz: `0.7` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert auf einer Stichprobe von nur 10 Läufen, was die Verallgemeinerbarkeit der Ergebnisse einschränert.
- Die gemessenen Zeiten sind Wall-Time-Messungen, die externe Systemvariablen (OS-Scheduler, Hintergrundprozesse) beinhalten können, was die Isolierung der reinen Rechenleistung erschwert.
- Es wird nicht geklärt, ob die beobachtete Variabilität der 'core_step_seconds' auf einen deterministischen Algorithmusfehler oder auf nicht-deterministische Systembedingungen zurückzuführen ist.
- Die vom Modell ausgegebene confidence war schemawidrig oder ausserhalb des Bereichs 0..1. Sie wurde fuer die AIRR-Provenienz konservativ auf 0.0 gesetzt; der Originalwert bleibt als confidence_original erhalten.

### Alternative Erklaerungen

- Die beobachtete Streuung der Laufzeiten könnte durch die Interaktion des Subsystems mit dem Betriebssystem-Scheduler verursacht werden, der die CPU-Zuweisung dynamisch steuert.
- Die Variation der Taktfrequenz ('ticks_per_second') könnte auf die Last des Gesamtsystems oder die Art der zugrundeliegenden Hardware-Ressourcenbeschaffung zurückzuführen sein, die nicht konstant ist.

### Fehlende Nachweise

- Bereitstellung von Systemressourcen-Metriken (CPU/RAM/I/O) während der Ausführung der Läufe, um externe Engpässe zu identifizieren.
- Bestätigung, ob die gemessenen Zeiten die gesamte System-Wall-Time oder nur die reine Rechenzeit darstellen.

### Empfohlene Folgeexperimente

- Durchführung einer größeren Stichprobe von Läufen (z.B. 100+ Seeds), um die Verteilung der Laufzeiten und Ticks/Sekunde besser zu charakterisieren.
- Messung der Leistung unter kontrollierten, isolierten Systembedingungen (z.B. durch Deaktivierung aller Hintergrundprozesse), um externe Systemvariablen zu eliminieren.
- Isolierte Messung der Komponenten (z.B. 'core_step_seconds' vs. 'digest_seconds') über eine größere Anzahl von Seeds, um deren individuellen Beitrag zur Gesamtvariabilität zu quantifizieren.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906230021883587-f20f538a.json](analysis/AIAR-critical_reviewer-20260906230021883587-f20f538a.json)
- [analysis/AIAR-scientific_analyst-20260906225957583639-f20f538a.json](analysis/AIAR-scientific_analyst-20260906225957583639-f20f538a.json)
- [analysis/AIAR-scientific_writer-20260906230046480272-f20f538a.json](analysis/AIAR-scientific_writer-20260906230046480272-f20f538a.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-subsystem_profile-seed-101.json.gz](DATA/raw/run-0000-subsystem_profile-seed-101.json.gz)
- [DATA/raw/run-0001-subsystem_profile-seed-102.json.gz](DATA/raw/run-0001-subsystem_profile-seed-102.json.gz)
- [DATA/raw/run-0002-subsystem_profile-seed-103.json.gz](DATA/raw/run-0002-subsystem_profile-seed-103.json.gz)
- [DATA/raw/run-0003-subsystem_profile-seed-104.json.gz](DATA/raw/run-0003-subsystem_profile-seed-104.json.gz)
- [DATA/raw/run-0004-subsystem_profile-seed-105.json.gz](DATA/raw/run-0004-subsystem_profile-seed-105.json.gz)
- [DATA/raw/run-0005-subsystem_profile-seed-106.json.gz](DATA/raw/run-0005-subsystem_profile-seed-106.json.gz)
- [DATA/raw/run-0006-subsystem_profile-seed-107.json.gz](DATA/raw/run-0006-subsystem_profile-seed-107.json.gz)
- [DATA/raw/run-0007-subsystem_profile-seed-108.json.gz](DATA/raw/run-0007-subsystem_profile-seed-108.json.gz)
- [DATA/raw/run-0008-subsystem_profile-seed-109.json.gz](DATA/raw/run-0008-subsystem_profile-seed-109.json.gz)
- [DATA/raw/run-0009-subsystem_profile-seed-110.json.gz](DATA/raw/run-0009-subsystem_profile-seed-110.json.gz)
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
