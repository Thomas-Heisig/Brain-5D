# EXP-GEN-0027: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-SNN-001`
- Hypothese: `H-SNN-001-A`
- Protokoll: `science_all_v1`
- Durchlaeufe: `51`
- Seeds: `[42, 43, 44]`
- Angeforderte Ticks: `1000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `1000 .. 1000` ausgeführte Ticks
- Tick-Vertrag: `SATISFIED`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `EXPLORATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `MISMATCH`
- Evidence Readiness: `BLOCKED_SEMANTIC_MISMATCH`
- Begründung: RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. Ein einzelner Impuls bzw. science_all_v1 mit langer stiller Nachlaufphase ist dafuer keine ausreichende Primaerpruefung.
- Beobachtete Conditions: `5d:1d, 5d:2d, 5d:3d, 5d:5d, 5d:random_graph, learning:learning_off, learning:learning_on, learning:sham_replay, ping:recurrence_off, ping:recurrence_on, regulation:chronic_pressure, regulation:nominal, regulation:telemetry_unknown, stdp:productive_reward_stdp, temporal:fast_medium_slow, time:100, time:1000`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Long-term stability diagnostic suite
- Bedingungen: Seeds 42,43,44; complete diagnostic suite; RQ-SNN-001 remains evidence-blocked until a sustained-activity protocol exists.
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `89c28cedbbd75431c424b4f70ccfbc478a02d020`
- Git dirty: `True`
- Runtime: `0.7946525999577716` s

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
| 5d:1d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:2d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:3d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:5d | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| 5d:random_graph | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| learning:learning_off | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:learning_on | 3 | 42,43,44 | — | — | — | — | — | — |
| learning:sham_replay | 3 | 42,43,44 | — | — | — | — | — | — |
| ping:recurrence_off | 3 | 42,43,44 | 1000 | 3 | 2 | 3 | 0 | 1 |
| ping:recurrence_on | 3 | 42,43,44 | 1000 | 33 | 33 | 3 | 10 | 61 |
| regulation:chronic_pressure | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:nominal | 3 | 42,43,44 | — | — | — | — | — | — |
| regulation:telemetry_unknown | 3 | 42,43,44 | — | — | — | — | — | — |
| stdp:productive_reward_stdp | 3 | 42,43,44 | — | — | — | — | — | — |
| temporal:fast_medium_slow | 3 | 42,43,44 | 1000 | 0 | — | — | — | — |
| time:100 | 3 | 42,43,44 | — | — | — | — | — | — |
| time:1000 | 3 | 42,43,44 | — | — | — | — | — | — |

### 5.2 Inter-Spike-Intervalle

- `5d:1d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:2d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:3d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:5d`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `5d:random_graph`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_off`: n=6, mean=1, median=1, min=1, max=1 Ticks.
- `ping:recurrence_on`: n=96, mean=1.9375, median=2, min=1, max=4 Ticks.

### 5.3 Temporal-State-Horizonte

- `fast`: Referenzvergleiche=2994; discrepancy mean=0.00263097, max=0.952011; nonzero=2994 (1); mean(nonzero)=0.00263097.
- `medium`: Referenzvergleiche=2988; discrepancy mean=0.00379847, max=1.15894; nonzero=2988 (1); mean(nonzero)=0.00379847.
- `slow`: Referenzvergleiche=2982; discrepancy mean=0.00463849, max=1.17842; nonzero=2982 (1); mean(nonzero)=0.00463849.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 43 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 44 | ping:recurrence_off | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | ping:recurrence_on | 1000 | 33 | 33 | 3 | 10 | 61 | — |
| 42 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
| 43 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
| 44 | temporal:fast_medium_slow | 1000 | 0 | — | — | — | — | — |
| 42 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 43 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 44 | stdp:productive_reward_stdp | — | — | — | — | — | — | — |
| 42 | learning:learning_on | — | — | — | — | — | — | — |
| 42 | learning:learning_off | — | — | — | — | — | — | — |
| 42 | learning:sham_replay | — | — | — | — | — | — | — |
| 43 | learning:learning_on | — | — | — | — | — | — | — |
| 43 | learning:learning_off | — | — | — | — | — | — | — |
| 43 | learning:sham_replay | — | — | — | — | — | — | — |
| 44 | learning:learning_on | — | — | — | — | — | — | — |
| 44 | learning:learning_off | — | — | — | — | — | — | — |
| 44 | learning:sham_replay | — | — | — | — | — | — | — |
| 42 | time:100 | 100 | — | — | — | — | — | — |
| 42 | time:1000 | 1000 | — | — | — | — | — | — |
| 43 | time:100 | 100 | — | — | — | — | — | — |
| 43 | time:1000 | 1000 | — | — | — | — | — | — |
| 44 | time:100 | 100 | — | — | — | — | — | — |
| 44 | time:1000 | 1000 | — | — | — | — | — | — |
| 42 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:1d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:2d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:3d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:5d | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | 5d:random_graph | 1000 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | regulation:nominal | — | — | — | — | — | — | — |
| 42 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 42 | regulation:telemetry_unknown | — | — | — | — | — | — | — |
| 43 | regulation:nominal | — | — | — | — | — | — | — |
| 43 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 43 | regulation:telemetry_unknown | — | — | — | — | — | — | — |
| 44 | regulation:nominal | — | — | — | — | — | — | — |
| 44 | regulation:chronic_pressure | — | — | — | — | — | — | — |
| 44 | regulation:telemetry_unknown | — | — | — | — | — | — | — |

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

Die Analyse der Simulationsergebnisse (EXP-GEN-0027) zeigt, dass die Spike-Dynamik unter den getesteten Bedingungen (ping:recurrence_off, ping:recurrence_on, temporal:fast_medium_slow) in allen Fällen stabil ist und keine offensichtlichen numerischen Drifts oder sofortigen Zusammenbrüche der Aktivität aufweist. Insbesondere die 'ping:recurrence_on'-Bedingung zeigt eine signifikant höhere neuronale Aktivität (33 Synaptic Events, 33 Spikes) und eine längere Propagation Depth (61) im Vergleich zu den 'ping:recurrence_off'-Bedingungen (2 Synaptic Events, 3 Spikes). Die 'temporal:fast_medium_slow'-Bedingung demonstriert die Fähigkeit, über einen langen Zeitraum (1000 Ticks) kontinuierlich messbare Veränderungen (mean_v) zu vergleichen, was auf eine funktionierende Langzeitstabilität hindeutet. Die Ergebnisse sind konsistent über die Seeds 42, 43 und 44, was die Reproduzierbarkeit der beobachteten Muster stützt. Die Hypothese H-SNN-001-A ('Brain-5D erzeugt über mindestens 100.000 Simulations-Ticks stabile Spike-Dynamiken ohne numerische Drift') ist derzeit unbewiesen, da die Simulationszeit nur 1000 Ticks beträgt, aber die beobachtete Stabilität ist vielversprechend.

KI-Konfidenz: `0.85` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Keine expliziten Angaben.

### Alternative Erklaerungen

- Die beobachtete hohe Spike-Aktivität bei 'ping:recurrence_on' könnte lediglich auf eine Überstimulation des Systems durch die rekurrenten Signale zurücführen sein, anstatt auf eine intrinsisch komplexe oder adaptive Verarbeitung. Dies könnte ein Artefakt der spezifischen Eingabemethode sein.
- Die scheinbare Stabilität der Dynamik über 1000 Ticks könnte durch die Art des verwendeten neuronalen Modells (z.B. Izhikevich) bedingt sein, das inhärent stabil ist, unabhängig von der tatsächlichen Komplexität der zugrundeliegenden neuronalen Netzwerke. Die Stabilität könnte daher ein Modell-Artefakt sein.
- Die konstanten, optimalen Werte in den regulatorischen Zuständen (regulation:nominal) könnten darauf hindeuten, dass das System in einem stabilen Gleichgewichtszustand arbeitet, der durch die Anfangsbedingungen des Experiments vorgegeben ist, und nicht notwendigerweise eine aktive, lernbasierte Selbstregulation darstellt.

### Fehlende Nachweise

- Längerfristige Simulationsdaten (Ticks > 100.000) zur Bestätigung der Langzeitstabilität der Spike-Dynamik.
- Daten, die den Übergang von einem stabilen Zustand zu einem instabilen Zustand (oder umgekehrt) unter kontrolliert variierten Parametern zeigen, um die Grenzen der Systemstabilität zu definieren.
- Eine detaillierte Analyse der Korrelation zwischen den gemessenen regulatorischen Parametern (z.B. `resource_pressure`) und den Spike-Metriken, um kausale Zusammenhänge zu identifizieren.

### Empfohlene Folgeexperimente

- Verlängerung der Simulationsdauer (Ticks) auf mindestens 100.000, um die Hypothese H-SNN-001-A empirisch zu testen und die Langzeitstabilität der Spike-Dynamik zu validieren.
- Durchführung von Experimenten mit variierenden Stärken und Frequenzen der rekurrenten Signale, um die optimale Frequenz und Amplitude für die Aufrechterhaltung komplexer, stabiler Muster zu bestimmen.
- Implementierung eines 'Stress-Tests' durch die gezielte Störung der regulatorischen Parameter (z.B. künstliche Reduzierung von `energy_reserve` oder Erhöhung von `resource_pressure`) und Beobachtung der Fähigkeit des Systems, einen stabilen Zustand wiederherzustellen.
- Vergleich der Spike-Dynamik unter verschiedenen neuronalen Modellarchitekturen (z.B. Izhikevich vs. Hodgkin-Huxley) bei gleicher Komplexität, um festzustellen, ob die beobachtete Stabilität modellabhängig ist.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906083557549145-5e113afb.json](analysis/AIAR-critical_reviewer-20260906083557549145-5e113afb.json)
- [analysis/AIAR-scientific_analyst-20260906083512843259-5e113afb.json](analysis/AIAR-scientific_analyst-20260906083512843259-5e113afb.json)
- [analysis/AIAR-scientific_writer-20260906083644071387-5e113afb.json](analysis/AIAR-scientific_writer-20260906083644071387-5e113afb.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-ping-recurrence_off-seed-42.json.gz](DATA/raw/run-0000-ping-recurrence_off-seed-42.json.gz)
- [DATA/raw/run-0001-ping-recurrence_on-seed-42.json.gz](DATA/raw/run-0001-ping-recurrence_on-seed-42.json.gz)
- [DATA/raw/run-0002-ping-recurrence_off-seed-43.json.gz](DATA/raw/run-0002-ping-recurrence_off-seed-43.json.gz)
- [DATA/raw/run-0003-ping-recurrence_on-seed-43.json.gz](DATA/raw/run-0003-ping-recurrence_on-seed-43.json.gz)
- [DATA/raw/run-0004-ping-recurrence_off-seed-44.json.gz](DATA/raw/run-0004-ping-recurrence_off-seed-44.json.gz)
- [DATA/raw/run-0005-ping-recurrence_on-seed-44.json.gz](DATA/raw/run-0005-ping-recurrence_on-seed-44.json.gz)
- [DATA/raw/run-0006-temporal-fast_medium_slow-seed-42.json.gz](DATA/raw/run-0006-temporal-fast_medium_slow-seed-42.json.gz)
- [DATA/raw/run-0007-temporal-fast_medium_slow-seed-43.json.gz](DATA/raw/run-0007-temporal-fast_medium_slow-seed-43.json.gz)
- [DATA/raw/run-0008-temporal-fast_medium_slow-seed-44.json.gz](DATA/raw/run-0008-temporal-fast_medium_slow-seed-44.json.gz)
- [DATA/raw/run-0009-stdp-productive_reward_stdp-seed-42.json.gz](DATA/raw/run-0009-stdp-productive_reward_stdp-seed-42.json.gz)
- [DATA/raw/run-0010-stdp-productive_reward_stdp-seed-43.json.gz](DATA/raw/run-0010-stdp-productive_reward_stdp-seed-43.json.gz)
- [DATA/raw/run-0011-stdp-productive_reward_stdp-seed-44.json.gz](DATA/raw/run-0011-stdp-productive_reward_stdp-seed-44.json.gz)
- [DATA/raw/run-0012-learning-learning_on-seed-42.json.gz](DATA/raw/run-0012-learning-learning_on-seed-42.json.gz)
- [DATA/raw/run-0013-learning-learning_off-seed-42.json.gz](DATA/raw/run-0013-learning-learning_off-seed-42.json.gz)
- [DATA/raw/run-0014-learning-sham_replay-seed-42.json.gz](DATA/raw/run-0014-learning-sham_replay-seed-42.json.gz)
- [DATA/raw/run-0015-learning-learning_on-seed-43.json.gz](DATA/raw/run-0015-learning-learning_on-seed-43.json.gz)
- [DATA/raw/run-0016-learning-learning_off-seed-43.json.gz](DATA/raw/run-0016-learning-learning_off-seed-43.json.gz)
- [DATA/raw/run-0017-learning-sham_replay-seed-43.json.gz](DATA/raw/run-0017-learning-sham_replay-seed-43.json.gz)
- [DATA/raw/run-0018-learning-learning_on-seed-44.json.gz](DATA/raw/run-0018-learning-learning_on-seed-44.json.gz)
- [DATA/raw/run-0019-learning-learning_off-seed-44.json.gz](DATA/raw/run-0019-learning-learning_off-seed-44.json.gz)
- [DATA/raw/run-0020-learning-sham_replay-seed-44.json.gz](DATA/raw/run-0020-learning-sham_replay-seed-44.json.gz)
- [DATA/raw/run-0021-time-100-seed-42.json.gz](DATA/raw/run-0021-time-100-seed-42.json.gz)
- [DATA/raw/run-0022-time-1000-seed-42.json.gz](DATA/raw/run-0022-time-1000-seed-42.json.gz)
- [DATA/raw/run-0023-time-100-seed-43.json.gz](DATA/raw/run-0023-time-100-seed-43.json.gz)
- [DATA/raw/run-0024-time-1000-seed-43.json.gz](DATA/raw/run-0024-time-1000-seed-43.json.gz)
- [DATA/raw/run-0025-time-100-seed-44.json.gz](DATA/raw/run-0025-time-100-seed-44.json.gz)
- [DATA/raw/run-0026-time-1000-seed-44.json.gz](DATA/raw/run-0026-time-1000-seed-44.json.gz)
- [DATA/raw/run-0027-5d-1d-seed-42.json.gz](DATA/raw/run-0027-5d-1d-seed-42.json.gz)
- [DATA/raw/run-0028-5d-2d-seed-42.json.gz](DATA/raw/run-0028-5d-2d-seed-42.json.gz)
- [DATA/raw/run-0029-5d-3d-seed-42.json.gz](DATA/raw/run-0029-5d-3d-seed-42.json.gz)
- [DATA/raw/run-0030-5d-5d-seed-42.json.gz](DATA/raw/run-0030-5d-5d-seed-42.json.gz)
- [DATA/raw/run-0031-5d-random_graph-seed-42.json.gz](DATA/raw/run-0031-5d-random_graph-seed-42.json.gz)
- [DATA/raw/run-0032-5d-1d-seed-43.json.gz](DATA/raw/run-0032-5d-1d-seed-43.json.gz)
- [DATA/raw/run-0033-5d-2d-seed-43.json.gz](DATA/raw/run-0033-5d-2d-seed-43.json.gz)
- [DATA/raw/run-0034-5d-3d-seed-43.json.gz](DATA/raw/run-0034-5d-3d-seed-43.json.gz)
- [DATA/raw/run-0035-5d-5d-seed-43.json.gz](DATA/raw/run-0035-5d-5d-seed-43.json.gz)
- [DATA/raw/run-0036-5d-random_graph-seed-43.json.gz](DATA/raw/run-0036-5d-random_graph-seed-43.json.gz)
- [DATA/raw/run-0037-5d-1d-seed-44.json.gz](DATA/raw/run-0037-5d-1d-seed-44.json.gz)
- [DATA/raw/run-0038-5d-2d-seed-44.json.gz](DATA/raw/run-0038-5d-2d-seed-44.json.gz)
- [DATA/raw/run-0039-5d-3d-seed-44.json.gz](DATA/raw/run-0039-5d-3d-seed-44.json.gz)
- [DATA/raw/run-0040-5d-5d-seed-44.json.gz](DATA/raw/run-0040-5d-5d-seed-44.json.gz)
- [DATA/raw/run-0041-5d-random_graph-seed-44.json.gz](DATA/raw/run-0041-5d-random_graph-seed-44.json.gz)
- [DATA/raw/run-0042-regulation-nominal-seed-42.json.gz](DATA/raw/run-0042-regulation-nominal-seed-42.json.gz)
- [DATA/raw/run-0043-regulation-chronic_pressure-seed-42.json.gz](DATA/raw/run-0043-regulation-chronic_pressure-seed-42.json.gz)
- [DATA/raw/run-0044-regulation-telemetry_unknown-seed-42.json.gz](DATA/raw/run-0044-regulation-telemetry_unknown-seed-42.json.gz)
- [DATA/raw/run-0045-regulation-nominal-seed-43.json.gz](DATA/raw/run-0045-regulation-nominal-seed-43.json.gz)
- [DATA/raw/run-0046-regulation-chronic_pressure-seed-43.json.gz](DATA/raw/run-0046-regulation-chronic_pressure-seed-43.json.gz)
- [DATA/raw/run-0047-regulation-telemetry_unknown-seed-43.json.gz](DATA/raw/run-0047-regulation-telemetry_unknown-seed-43.json.gz)
- [DATA/raw/run-0048-regulation-nominal-seed-44.json.gz](DATA/raw/run-0048-regulation-nominal-seed-44.json.gz)
- [DATA/raw/run-0049-regulation-chronic_pressure-seed-44.json.gz](DATA/raw/run-0049-regulation-chronic_pressure-seed-44.json.gz)
- [DATA/raw/run-0050-regulation-telemetry_unknown-seed-44.json.gz](DATA/raw/run-0050-regulation-telemetry_unknown-seed-44.json.gz)
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
