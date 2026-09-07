# EXP-BATCH-20260906200118-38: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-5D-005`
- Hypothese: `H-5D-005-A`
- Protokoll: `topology_matched_5d_v1`
- Durchlaeufe: `120`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]`
- Angeforderte Ticks: `64`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `64 .. 64` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: 5D-005 erwartet topology-matched 1D/2D/3D/5D-Einbettungen.
- Beobachtete Conditions: `1d, 2d, 3d, 5d`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: topology_matched_5d_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `275f3b77df6e89cc224d8542454434ff7e84d7a4`
- Git dirty: `True`
- Runtime: `0.11743480002041906` s

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
| 1d | 30 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130 | 64 | 3 | 2 | 3 | 0 | 1 |
| 2d | 30 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130 | 64 | 3 | 2 | 3 | 0 | 1 |
| 3d | 30 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130 | 64 | 3 | 2 | 3 | 0 | 1 |
| 5d | 30 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130 | 64 | 3 | 2 | 3 | 0 | 1 |

### 5.2 Inter-Spike-Intervalle

- `1d`: n=60, mean=1, median=1, min=1, max=1 Ticks.
- `2d`: n=60, mean=1, median=1, min=1, max=1 Ticks.
- `3d`: n=60, mean=1, median=1, min=1, max=1 Ticks.
- `5d`: n=60, mean=1, median=1, min=1, max=1 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 121 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 121 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 121 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 121 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 122 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 122 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 122 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 122 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 123 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 123 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 123 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 123 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 124 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 124 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 124 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 124 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 125 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 125 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 125 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 125 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 126 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 126 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 126 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 126 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 127 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 127 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 127 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 127 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 128 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 128 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 128 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 128 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 129 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 129 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 129 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 129 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 130 | 1d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 130 | 2d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 130 | 3d | 64 | 3 | 2 | 3 | 0 | 1 | — |
| 130 | 5d | 64 | 3 | 2 | 3 | 0 | 1 | — |

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

Die statistischen Zusammenfassungen für alle getesteten Bedingungen ('1d', '2d', '3d', '5d') zeigen für die gemessenen Metriken (z. B. `activated_neurons`, `delivered_synaptic_events`, `propagation_depth`, `total_spikes`) keine beobachtbaren Unterschiede. Alle Metriken haben einen Mittelwert, Median und einen Standardfehler von 0.0, was auf eine konstante Leistung über alle getesteten Bedingungen hinweist. Die Analyse der Inter-Spike-Intervalle (ISI) zeigt ebenfalls, dass die Mittelwerte für alle Dimensionen (1d, 2d, 3d, 5d) gleich sind (Mittelwert = 1.0).

KI-Konfidenz: `1.0` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert auf einer Reihe von Einzelläufen (run_count=120), die jeweils nur zwei Synapsen und drei Spikes registrieren. Dies könnte die beobachteten Metriken künstlich begrenzen und die Fähigkeit des Systems, komplexere Dynamiken zu verarbeiten, nicht vollständig abbilden.

### Alternative Erklaerungen

- Die verwendeten experimentellen Parameter (z. B. `matched_synapse_count`: 2, `matched_weight_pattern`: [100.0, 100.0]) könnten zu einem stabilen und vorhersagbaren Systemzustand geführt haben, der die Variabilität über verschiedene Dimensionen hinweg minimiert.
- Die Testbedingungen sind möglicherweise zu restriktiv, um dimensionsspezifische Unterschiede zu provozieren. Die beobachtete Konstanz könnte ein Artefakt der verwendeten Testkonfiguration sein.

### Fehlende Nachweise

- Daten, die die Leistung des Systems unter Bedingungen mit höherer Netzwerkkomplexität (z. B. mehr als 2 Synapsen oder mehr als 3 Neuronen) liefern, um die Skalierbarkeit der beobachteten Metriken zu bewerten.
- Vergleichende Daten, die die Auswirkungen unterschiedlicher Gewichtsverteilungen oder -muster auf die gemessenen Metriken in den verschiedenen Dimensionen zeigen.

### Empfohlene Folgeexperimente

- Die Untersuchung sollte die Komplexität der Netzwerkstruktur erhöhen, indem die Anzahl der Synapsen oder die Komplexität der Gradmuster (Degree Patterns) erhöht wird.
- Es sollte eine Variation der Gewichtsverteilungen (Weight Patterns) oder der synaptischen Aktivität (Synaptic Activity Ticks) getestet werden, um zu sehen, ob die beobachtete Konstanz von den Verbindungsstärken abhängt.
- Die Untersuchung sollte die Anzahl der Neuronen und Synapsen in den verschiedenen Dimensionen (1d, 2d, 3d, 5d) variieren, um zu prüfen, ob die beobachtete Gleichheit der Metriken auch bei unterschiedlicher Skalierung gilt.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906225711862502-1f8a94f4.json](analysis/AIAR-critical_reviewer-20260906225711862502-1f8a94f4.json)
- [analysis/AIAR-scientific_analyst-20260906225647304842-1f8a94f4.json](analysis/AIAR-scientific_analyst-20260906225647304842-1f8a94f4.json)
- [analysis/AIAR-scientific_writer-20260906225736785497-1f8a94f4.json](analysis/AIAR-scientific_writer-20260906225736785497-1f8a94f4.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-1d-seed-101.json.gz](DATA/raw/run-0000-1d-seed-101.json.gz)
- [DATA/raw/run-0001-2d-seed-101.json.gz](DATA/raw/run-0001-2d-seed-101.json.gz)
- [DATA/raw/run-0002-3d-seed-101.json.gz](DATA/raw/run-0002-3d-seed-101.json.gz)
- [DATA/raw/run-0003-5d-seed-101.json.gz](DATA/raw/run-0003-5d-seed-101.json.gz)
- [DATA/raw/run-0004-1d-seed-102.json.gz](DATA/raw/run-0004-1d-seed-102.json.gz)
- [DATA/raw/run-0005-2d-seed-102.json.gz](DATA/raw/run-0005-2d-seed-102.json.gz)
- [DATA/raw/run-0006-3d-seed-102.json.gz](DATA/raw/run-0006-3d-seed-102.json.gz)
- [DATA/raw/run-0007-5d-seed-102.json.gz](DATA/raw/run-0007-5d-seed-102.json.gz)
- [DATA/raw/run-0008-1d-seed-103.json.gz](DATA/raw/run-0008-1d-seed-103.json.gz)
- [DATA/raw/run-0009-2d-seed-103.json.gz](DATA/raw/run-0009-2d-seed-103.json.gz)
- [DATA/raw/run-0010-3d-seed-103.json.gz](DATA/raw/run-0010-3d-seed-103.json.gz)
- [DATA/raw/run-0011-5d-seed-103.json.gz](DATA/raw/run-0011-5d-seed-103.json.gz)
- [DATA/raw/run-0012-1d-seed-104.json.gz](DATA/raw/run-0012-1d-seed-104.json.gz)
- [DATA/raw/run-0013-2d-seed-104.json.gz](DATA/raw/run-0013-2d-seed-104.json.gz)
- [DATA/raw/run-0014-3d-seed-104.json.gz](DATA/raw/run-0014-3d-seed-104.json.gz)
- [DATA/raw/run-0015-5d-seed-104.json.gz](DATA/raw/run-0015-5d-seed-104.json.gz)
- [DATA/raw/run-0016-1d-seed-105.json.gz](DATA/raw/run-0016-1d-seed-105.json.gz)
- [DATA/raw/run-0017-2d-seed-105.json.gz](DATA/raw/run-0017-2d-seed-105.json.gz)
- [DATA/raw/run-0018-3d-seed-105.json.gz](DATA/raw/run-0018-3d-seed-105.json.gz)
- [DATA/raw/run-0019-5d-seed-105.json.gz](DATA/raw/run-0019-5d-seed-105.json.gz)
- [DATA/raw/run-0020-1d-seed-106.json.gz](DATA/raw/run-0020-1d-seed-106.json.gz)
- [DATA/raw/run-0021-2d-seed-106.json.gz](DATA/raw/run-0021-2d-seed-106.json.gz)
- [DATA/raw/run-0022-3d-seed-106.json.gz](DATA/raw/run-0022-3d-seed-106.json.gz)
- [DATA/raw/run-0023-5d-seed-106.json.gz](DATA/raw/run-0023-5d-seed-106.json.gz)
- [DATA/raw/run-0024-1d-seed-107.json.gz](DATA/raw/run-0024-1d-seed-107.json.gz)
- [DATA/raw/run-0025-2d-seed-107.json.gz](DATA/raw/run-0025-2d-seed-107.json.gz)
- [DATA/raw/run-0026-3d-seed-107.json.gz](DATA/raw/run-0026-3d-seed-107.json.gz)
- [DATA/raw/run-0027-5d-seed-107.json.gz](DATA/raw/run-0027-5d-seed-107.json.gz)
- [DATA/raw/run-0028-1d-seed-108.json.gz](DATA/raw/run-0028-1d-seed-108.json.gz)
- [DATA/raw/run-0029-2d-seed-108.json.gz](DATA/raw/run-0029-2d-seed-108.json.gz)
- [DATA/raw/run-0030-3d-seed-108.json.gz](DATA/raw/run-0030-3d-seed-108.json.gz)
- [DATA/raw/run-0031-5d-seed-108.json.gz](DATA/raw/run-0031-5d-seed-108.json.gz)
- [DATA/raw/run-0032-1d-seed-109.json.gz](DATA/raw/run-0032-1d-seed-109.json.gz)
- [DATA/raw/run-0033-2d-seed-109.json.gz](DATA/raw/run-0033-2d-seed-109.json.gz)
- [DATA/raw/run-0034-3d-seed-109.json.gz](DATA/raw/run-0034-3d-seed-109.json.gz)
- [DATA/raw/run-0035-5d-seed-109.json.gz](DATA/raw/run-0035-5d-seed-109.json.gz)
- [DATA/raw/run-0036-1d-seed-110.json.gz](DATA/raw/run-0036-1d-seed-110.json.gz)
- [DATA/raw/run-0037-2d-seed-110.json.gz](DATA/raw/run-0037-2d-seed-110.json.gz)
- [DATA/raw/run-0038-3d-seed-110.json.gz](DATA/raw/run-0038-3d-seed-110.json.gz)
- [DATA/raw/run-0039-5d-seed-110.json.gz](DATA/raw/run-0039-5d-seed-110.json.gz)
- [DATA/raw/run-0040-1d-seed-111.json.gz](DATA/raw/run-0040-1d-seed-111.json.gz)
- [DATA/raw/run-0041-2d-seed-111.json.gz](DATA/raw/run-0041-2d-seed-111.json.gz)
- [DATA/raw/run-0042-3d-seed-111.json.gz](DATA/raw/run-0042-3d-seed-111.json.gz)
- [DATA/raw/run-0043-5d-seed-111.json.gz](DATA/raw/run-0043-5d-seed-111.json.gz)
- [DATA/raw/run-0044-1d-seed-112.json.gz](DATA/raw/run-0044-1d-seed-112.json.gz)
- [DATA/raw/run-0045-2d-seed-112.json.gz](DATA/raw/run-0045-2d-seed-112.json.gz)
- [DATA/raw/run-0046-3d-seed-112.json.gz](DATA/raw/run-0046-3d-seed-112.json.gz)
- [DATA/raw/run-0047-5d-seed-112.json.gz](DATA/raw/run-0047-5d-seed-112.json.gz)
- [DATA/raw/run-0048-1d-seed-113.json.gz](DATA/raw/run-0048-1d-seed-113.json.gz)
- [DATA/raw/run-0049-2d-seed-113.json.gz](DATA/raw/run-0049-2d-seed-113.json.gz)
- [DATA/raw/run-0050-3d-seed-113.json.gz](DATA/raw/run-0050-3d-seed-113.json.gz)
- [DATA/raw/run-0051-5d-seed-113.json.gz](DATA/raw/run-0051-5d-seed-113.json.gz)
- [DATA/raw/run-0052-1d-seed-114.json.gz](DATA/raw/run-0052-1d-seed-114.json.gz)
- [DATA/raw/run-0053-2d-seed-114.json.gz](DATA/raw/run-0053-2d-seed-114.json.gz)
- [DATA/raw/run-0054-3d-seed-114.json.gz](DATA/raw/run-0054-3d-seed-114.json.gz)
- [DATA/raw/run-0055-5d-seed-114.json.gz](DATA/raw/run-0055-5d-seed-114.json.gz)
- [DATA/raw/run-0056-1d-seed-115.json.gz](DATA/raw/run-0056-1d-seed-115.json.gz)
- [DATA/raw/run-0057-2d-seed-115.json.gz](DATA/raw/run-0057-2d-seed-115.json.gz)
- [DATA/raw/run-0058-3d-seed-115.json.gz](DATA/raw/run-0058-3d-seed-115.json.gz)
- [DATA/raw/run-0059-5d-seed-115.json.gz](DATA/raw/run-0059-5d-seed-115.json.gz)
- [DATA/raw/run-0060-1d-seed-116.json.gz](DATA/raw/run-0060-1d-seed-116.json.gz)
- [DATA/raw/run-0061-2d-seed-116.json.gz](DATA/raw/run-0061-2d-seed-116.json.gz)
- [DATA/raw/run-0062-3d-seed-116.json.gz](DATA/raw/run-0062-3d-seed-116.json.gz)
- [DATA/raw/run-0063-5d-seed-116.json.gz](DATA/raw/run-0063-5d-seed-116.json.gz)
- [DATA/raw/run-0064-1d-seed-117.json.gz](DATA/raw/run-0064-1d-seed-117.json.gz)
- [DATA/raw/run-0065-2d-seed-117.json.gz](DATA/raw/run-0065-2d-seed-117.json.gz)
- [DATA/raw/run-0066-3d-seed-117.json.gz](DATA/raw/run-0066-3d-seed-117.json.gz)
- [DATA/raw/run-0067-5d-seed-117.json.gz](DATA/raw/run-0067-5d-seed-117.json.gz)
- [DATA/raw/run-0068-1d-seed-118.json.gz](DATA/raw/run-0068-1d-seed-118.json.gz)
- [DATA/raw/run-0069-2d-seed-118.json.gz](DATA/raw/run-0069-2d-seed-118.json.gz)
- [DATA/raw/run-0070-3d-seed-118.json.gz](DATA/raw/run-0070-3d-seed-118.json.gz)
- [DATA/raw/run-0071-5d-seed-118.json.gz](DATA/raw/run-0071-5d-seed-118.json.gz)
- [DATA/raw/run-0072-1d-seed-119.json.gz](DATA/raw/run-0072-1d-seed-119.json.gz)
- [DATA/raw/run-0073-2d-seed-119.json.gz](DATA/raw/run-0073-2d-seed-119.json.gz)
- [DATA/raw/run-0074-3d-seed-119.json.gz](DATA/raw/run-0074-3d-seed-119.json.gz)
- [DATA/raw/run-0075-5d-seed-119.json.gz](DATA/raw/run-0075-5d-seed-119.json.gz)
- [DATA/raw/run-0076-1d-seed-120.json.gz](DATA/raw/run-0076-1d-seed-120.json.gz)
- [DATA/raw/run-0077-2d-seed-120.json.gz](DATA/raw/run-0077-2d-seed-120.json.gz)
- [DATA/raw/run-0078-3d-seed-120.json.gz](DATA/raw/run-0078-3d-seed-120.json.gz)
- [DATA/raw/run-0079-5d-seed-120.json.gz](DATA/raw/run-0079-5d-seed-120.json.gz)
- [DATA/raw/run-0080-1d-seed-121.json.gz](DATA/raw/run-0080-1d-seed-121.json.gz)
- [DATA/raw/run-0081-2d-seed-121.json.gz](DATA/raw/run-0081-2d-seed-121.json.gz)
- [DATA/raw/run-0082-3d-seed-121.json.gz](DATA/raw/run-0082-3d-seed-121.json.gz)
- [DATA/raw/run-0083-5d-seed-121.json.gz](DATA/raw/run-0083-5d-seed-121.json.gz)
- [DATA/raw/run-0084-1d-seed-122.json.gz](DATA/raw/run-0084-1d-seed-122.json.gz)
- [DATA/raw/run-0085-2d-seed-122.json.gz](DATA/raw/run-0085-2d-seed-122.json.gz)
- [DATA/raw/run-0086-3d-seed-122.json.gz](DATA/raw/run-0086-3d-seed-122.json.gz)
- [DATA/raw/run-0087-5d-seed-122.json.gz](DATA/raw/run-0087-5d-seed-122.json.gz)
- [DATA/raw/run-0088-1d-seed-123.json.gz](DATA/raw/run-0088-1d-seed-123.json.gz)
- [DATA/raw/run-0089-2d-seed-123.json.gz](DATA/raw/run-0089-2d-seed-123.json.gz)
- [DATA/raw/run-0090-3d-seed-123.json.gz](DATA/raw/run-0090-3d-seed-123.json.gz)
- [DATA/raw/run-0091-5d-seed-123.json.gz](DATA/raw/run-0091-5d-seed-123.json.gz)
- [DATA/raw/run-0092-1d-seed-124.json.gz](DATA/raw/run-0092-1d-seed-124.json.gz)
- [DATA/raw/run-0093-2d-seed-124.json.gz](DATA/raw/run-0093-2d-seed-124.json.gz)
- [DATA/raw/run-0094-3d-seed-124.json.gz](DATA/raw/run-0094-3d-seed-124.json.gz)
- [DATA/raw/run-0095-5d-seed-124.json.gz](DATA/raw/run-0095-5d-seed-124.json.gz)
- [DATA/raw/run-0096-1d-seed-125.json.gz](DATA/raw/run-0096-1d-seed-125.json.gz)
- [DATA/raw/run-0097-2d-seed-125.json.gz](DATA/raw/run-0097-2d-seed-125.json.gz)
- [DATA/raw/run-0098-3d-seed-125.json.gz](DATA/raw/run-0098-3d-seed-125.json.gz)
- [DATA/raw/run-0099-5d-seed-125.json.gz](DATA/raw/run-0099-5d-seed-125.json.gz)
- [DATA/raw/run-0100-1d-seed-126.json.gz](DATA/raw/run-0100-1d-seed-126.json.gz)
- [DATA/raw/run-0101-2d-seed-126.json.gz](DATA/raw/run-0101-2d-seed-126.json.gz)
- [DATA/raw/run-0102-3d-seed-126.json.gz](DATA/raw/run-0102-3d-seed-126.json.gz)
- [DATA/raw/run-0103-5d-seed-126.json.gz](DATA/raw/run-0103-5d-seed-126.json.gz)
- [DATA/raw/run-0104-1d-seed-127.json.gz](DATA/raw/run-0104-1d-seed-127.json.gz)
- [DATA/raw/run-0105-2d-seed-127.json.gz](DATA/raw/run-0105-2d-seed-127.json.gz)
- [DATA/raw/run-0106-3d-seed-127.json.gz](DATA/raw/run-0106-3d-seed-127.json.gz)
- [DATA/raw/run-0107-5d-seed-127.json.gz](DATA/raw/run-0107-5d-seed-127.json.gz)
- [DATA/raw/run-0108-1d-seed-128.json.gz](DATA/raw/run-0108-1d-seed-128.json.gz)
- [DATA/raw/run-0109-2d-seed-128.json.gz](DATA/raw/run-0109-2d-seed-128.json.gz)
- [DATA/raw/run-0110-3d-seed-128.json.gz](DATA/raw/run-0110-3d-seed-128.json.gz)
- [DATA/raw/run-0111-5d-seed-128.json.gz](DATA/raw/run-0111-5d-seed-128.json.gz)
- [DATA/raw/run-0112-1d-seed-129.json.gz](DATA/raw/run-0112-1d-seed-129.json.gz)
- [DATA/raw/run-0113-2d-seed-129.json.gz](DATA/raw/run-0113-2d-seed-129.json.gz)
- [DATA/raw/run-0114-3d-seed-129.json.gz](DATA/raw/run-0114-3d-seed-129.json.gz)
- [DATA/raw/run-0115-5d-seed-129.json.gz](DATA/raw/run-0115-5d-seed-129.json.gz)
- [DATA/raw/run-0116-1d-seed-130.json.gz](DATA/raw/run-0116-1d-seed-130.json.gz)
- [DATA/raw/run-0117-2d-seed-130.json.gz](DATA/raw/run-0117-2d-seed-130.json.gz)
- [DATA/raw/run-0118-3d-seed-130.json.gz](DATA/raw/run-0118-3d-seed-130.json.gz)
- [DATA/raw/run-0119-5d-seed-130.json.gz](DATA/raw/run-0119-5d-seed-130.json.gz)
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
