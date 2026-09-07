# EXP-BATCH-20260906200118-36: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-GEN-001`
- Hypothese: `H-GEN-001-A`
- Protokoll: `learning_generalization_v1`
- Durchlaeufe: `180`
- Seeds: `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]`
- Angeforderte Ticks: `1000`
- Tickgebundene SNN-Läufe (PING/TEMP/5D): `nicht direkt messbar .. nicht direkt messbar` ausgeführte Ticks
- Tick-Vertrag: `NOT_APPLICABLE`
- TIME-Ladder: Der angeforderte Endpunkt wird je Seed separat validiert; Zwischenstufen duerfen kleiner sein.
- Trial-/Regulationsprotokolle: Interne Versuchszyklen sind nicht mit `ticks_executed` gleichzusetzen und werden nicht in die SNN-Tickspanne eingerechnet.
- Laufmodus: `CONFIRMATORY`
- Netzwerkmodus: `OFFLINE`

## 2. Semantische Konsistenz

- RQ/Condition-Pruefung: `DIRECT_MATCH`
- Evidence Readiness: `BLOCKED_DIRTY_SOURCE_TREE`
- Begründung: GEN-001 erwartet Learning-on, Learning-off und Sham-Replay über registrierte Perturbationsproben.
- Beobachtete Conditions: `learning_off_drive_0.85, learning_off_drive_1.00, learning_off_drive_1.15, learning_on_drive_0.85, learning_on_drive_1.00, learning_on_drive_1.15, sham_replay_drive_0.85, sham_replay_drive_1.00, sham_replay_drive_1.15`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: learning_generalization_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `275f3b77df6e89cc224d8542454434ff7e84d7a4`
- Git dirty: `True`
- Runtime: `1.2457530000247061` s

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
| learning_off_drive_0.85 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| learning_off_drive_1.00 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| learning_off_drive_1.15 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| learning_on_drive_0.85 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| learning_on_drive_1.00 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| learning_on_drive_1.15 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| sham_replay_drive_0.85 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| sham_replay_drive_1.00 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |
| sham_replay_drive_1.15 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | — | — | — | — | — | — |

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 101 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 101 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 101 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 101 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 101 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 101 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 101 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 101 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 102 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 102 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 102 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 102 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 102 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 102 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 102 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 102 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 102 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 103 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 103 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 103 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 103 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 103 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 103 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 103 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 103 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 103 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 104 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 104 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 104 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 104 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 104 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 104 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 104 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 104 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 104 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 105 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 105 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 105 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 105 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 105 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 105 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 105 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 105 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 105 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 106 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 106 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 106 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 106 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 106 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 106 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 106 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 106 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 106 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 107 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 107 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 107 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 107 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 107 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 107 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 107 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 107 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 107 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 108 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 108 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 108 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 108 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 108 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 108 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 108 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 108 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 108 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 109 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 109 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 109 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 109 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 109 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 109 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 109 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 109 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 109 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 110 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 110 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 110 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 110 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 110 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 110 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 110 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 110 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 110 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 111 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 111 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 111 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 111 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 111 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 111 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 111 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 111 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 111 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 112 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 112 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 112 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 112 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 112 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 112 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 112 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 112 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 112 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 113 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 113 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 113 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 113 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 113 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 113 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 113 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 113 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 113 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 114 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 114 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 114 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 114 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 114 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 114 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 114 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 114 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 114 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 115 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 115 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 115 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 115 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 115 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 115 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 115 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 115 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 115 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 116 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 116 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 116 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 116 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 116 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 116 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 116 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 116 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 116 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 117 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 117 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 117 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 117 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 117 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 117 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 117 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 117 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 117 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 118 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 118 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 118 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 118 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 118 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 118 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 118 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 118 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 118 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 119 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 119 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 119 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 119 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 119 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 119 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 119 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 119 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 119 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |
| 120 | learning_on_drive_0.85 | — | — | — | — | — | — | — |
| 120 | learning_on_drive_1.00 | — | — | — | — | — | — | — |
| 120 | learning_on_drive_1.15 | — | — | — | — | — | — | — |
| 120 | learning_off_drive_0.85 | — | — | — | — | — | — | — |
| 120 | learning_off_drive_1.00 | — | — | — | — | — | — | — |
| 120 | learning_off_drive_1.15 | — | — | — | — | — | — | — |
| 120 | sham_replay_drive_0.85 | — | — | — | — | — | — | — |
| 120 | sham_replay_drive_1.00 | — | — | — | — | — | — | — |
| 120 | sham_replay_drive_1.15 | — | — | — | — | — | — | — |

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

Die Ergebnisse zeigen, dass die Bedingungen 'learning_on_drive_X.XX' durchweg höhere Werte für 'mean_weight_delta' (Mittelwert: 0.4672804698428431) und 'reward_weight_updates' (Mittelwert: 576.0) im Vergleich zu den Kontrollbedingungen 'learning_off_drive_X.XX' und 'sham_replay_drive_X.XX' (Mittelwert: 0.0) aufweisen. Dies gilt für alle getesteten Drive-Skalen (0.85, 1.00, 1.15). Die Metriken 'p_success_after' und 'generalization_success' sind in den 'learning_on_drive'-Bedingungen durchweg 1.0 bzw. true, während sie in den Kontrollbedingungen 0.0 bzw. false sind. Die statistische Signifikanz wurde nicht getestet.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die Analyse basiert auf einer Stichprobe von 20 Seeds, was die Verallgemeinerbarkeit der Ergebnisse einschränken könnte.
- Es wird nicht angegeben, ob die 'generalization_success' oder 'success_after' Metriken auf einer ausreichenden Anzahl von unabhängigen Tests basieren.

### Alternative Erklaerungen

- Die beobachteten Unterschiede könnten auf andere, nicht gemessene Lernmechanismen zurückzuführen sein, die durch die 'learning_on_drive'-Bedingung aktiviert werden.
- Die 'sham_replay'-Bedingung könnte nicht ausreichend als Negativkontrolle dienen, um sicherzustellen, dass die beobachteten Effekte ausschließlich auf das Lernen auf dem Drive zurückzuführen sind.

### Fehlende Nachweise

- Detaillierte Protokolle der 'learning_on_drive' und 'learning_off_drive' Bedingungen, um die genauen Mechanismen des Gewichts-Updates zu verstehen.
- Bestätigung, dass die 'generalization_success' Metrik tatsächlich die Fähigkeit misst, auf völlig neue, ungesehene Daten zu generalisieren, und nicht nur eine Wiederholung bekannter Muster.

### Empfohlene Folgeexperimente

- Durchführung eines Experiments, das die Interaktion zwischen der Drive-Skala und der Art des Lernens (on vs. off) untersucht, um die Abhängigkeit zu quantifizieren.
- Vergleich der Leistung mit einer weiteren Kontrollgruppe, die nur die Wiederholung von Daten ohne spezifische Modifikation des Lernprozesses durchführt, um die Spezifität des 'learning_on_drive' zu erhöhen.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906225555320016-ee0af4bd.json](analysis/AIAR-critical_reviewer-20260906225555320016-ee0af4bd.json)
- [analysis/AIAR-scientific_analyst-20260906225518218821-ee0af4bd.json](analysis/AIAR-scientific_analyst-20260906225518218821-ee0af4bd.json)
- [analysis/AIAR-scientific_writer-20260906225622334643-ee0af4bd.json](analysis/AIAR-scientific_writer-20260906225622334643-ee0af4bd.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-learning_on_drive_0.85-seed-101.json.gz](DATA/raw/run-0000-learning_on_drive_0.85-seed-101.json.gz)
- [DATA/raw/run-0001-learning_on_drive_1.00-seed-101.json.gz](DATA/raw/run-0001-learning_on_drive_1.00-seed-101.json.gz)
- [DATA/raw/run-0002-learning_on_drive_1.15-seed-101.json.gz](DATA/raw/run-0002-learning_on_drive_1.15-seed-101.json.gz)
- [DATA/raw/run-0003-learning_off_drive_0.85-seed-101.json.gz](DATA/raw/run-0003-learning_off_drive_0.85-seed-101.json.gz)
- [DATA/raw/run-0004-learning_off_drive_1.00-seed-101.json.gz](DATA/raw/run-0004-learning_off_drive_1.00-seed-101.json.gz)
- [DATA/raw/run-0005-learning_off_drive_1.15-seed-101.json.gz](DATA/raw/run-0005-learning_off_drive_1.15-seed-101.json.gz)
- [DATA/raw/run-0006-sham_replay_drive_0.85-seed-101.json.gz](DATA/raw/run-0006-sham_replay_drive_0.85-seed-101.json.gz)
- [DATA/raw/run-0007-sham_replay_drive_1.00-seed-101.json.gz](DATA/raw/run-0007-sham_replay_drive_1.00-seed-101.json.gz)
- [DATA/raw/run-0008-sham_replay_drive_1.15-seed-101.json.gz](DATA/raw/run-0008-sham_replay_drive_1.15-seed-101.json.gz)
- [DATA/raw/run-0009-learning_on_drive_0.85-seed-102.json.gz](DATA/raw/run-0009-learning_on_drive_0.85-seed-102.json.gz)
- [DATA/raw/run-0010-learning_on_drive_1.00-seed-102.json.gz](DATA/raw/run-0010-learning_on_drive_1.00-seed-102.json.gz)
- [DATA/raw/run-0011-learning_on_drive_1.15-seed-102.json.gz](DATA/raw/run-0011-learning_on_drive_1.15-seed-102.json.gz)
- [DATA/raw/run-0012-learning_off_drive_0.85-seed-102.json.gz](DATA/raw/run-0012-learning_off_drive_0.85-seed-102.json.gz)
- [DATA/raw/run-0013-learning_off_drive_1.00-seed-102.json.gz](DATA/raw/run-0013-learning_off_drive_1.00-seed-102.json.gz)
- [DATA/raw/run-0014-learning_off_drive_1.15-seed-102.json.gz](DATA/raw/run-0014-learning_off_drive_1.15-seed-102.json.gz)
- [DATA/raw/run-0015-sham_replay_drive_0.85-seed-102.json.gz](DATA/raw/run-0015-sham_replay_drive_0.85-seed-102.json.gz)
- [DATA/raw/run-0016-sham_replay_drive_1.00-seed-102.json.gz](DATA/raw/run-0016-sham_replay_drive_1.00-seed-102.json.gz)
- [DATA/raw/run-0017-sham_replay_drive_1.15-seed-102.json.gz](DATA/raw/run-0017-sham_replay_drive_1.15-seed-102.json.gz)
- [DATA/raw/run-0018-learning_on_drive_0.85-seed-103.json.gz](DATA/raw/run-0018-learning_on_drive_0.85-seed-103.json.gz)
- [DATA/raw/run-0019-learning_on_drive_1.00-seed-103.json.gz](DATA/raw/run-0019-learning_on_drive_1.00-seed-103.json.gz)
- [DATA/raw/run-0020-learning_on_drive_1.15-seed-103.json.gz](DATA/raw/run-0020-learning_on_drive_1.15-seed-103.json.gz)
- [DATA/raw/run-0021-learning_off_drive_0.85-seed-103.json.gz](DATA/raw/run-0021-learning_off_drive_0.85-seed-103.json.gz)
- [DATA/raw/run-0022-learning_off_drive_1.00-seed-103.json.gz](DATA/raw/run-0022-learning_off_drive_1.00-seed-103.json.gz)
- [DATA/raw/run-0023-learning_off_drive_1.15-seed-103.json.gz](DATA/raw/run-0023-learning_off_drive_1.15-seed-103.json.gz)
- [DATA/raw/run-0024-sham_replay_drive_0.85-seed-103.json.gz](DATA/raw/run-0024-sham_replay_drive_0.85-seed-103.json.gz)
- [DATA/raw/run-0025-sham_replay_drive_1.00-seed-103.json.gz](DATA/raw/run-0025-sham_replay_drive_1.00-seed-103.json.gz)
- [DATA/raw/run-0026-sham_replay_drive_1.15-seed-103.json.gz](DATA/raw/run-0026-sham_replay_drive_1.15-seed-103.json.gz)
- [DATA/raw/run-0027-learning_on_drive_0.85-seed-104.json.gz](DATA/raw/run-0027-learning_on_drive_0.85-seed-104.json.gz)
- [DATA/raw/run-0028-learning_on_drive_1.00-seed-104.json.gz](DATA/raw/run-0028-learning_on_drive_1.00-seed-104.json.gz)
- [DATA/raw/run-0029-learning_on_drive_1.15-seed-104.json.gz](DATA/raw/run-0029-learning_on_drive_1.15-seed-104.json.gz)
- [DATA/raw/run-0030-learning_off_drive_0.85-seed-104.json.gz](DATA/raw/run-0030-learning_off_drive_0.85-seed-104.json.gz)
- [DATA/raw/run-0031-learning_off_drive_1.00-seed-104.json.gz](DATA/raw/run-0031-learning_off_drive_1.00-seed-104.json.gz)
- [DATA/raw/run-0032-learning_off_drive_1.15-seed-104.json.gz](DATA/raw/run-0032-learning_off_drive_1.15-seed-104.json.gz)
- [DATA/raw/run-0033-sham_replay_drive_0.85-seed-104.json.gz](DATA/raw/run-0033-sham_replay_drive_0.85-seed-104.json.gz)
- [DATA/raw/run-0034-sham_replay_drive_1.00-seed-104.json.gz](DATA/raw/run-0034-sham_replay_drive_1.00-seed-104.json.gz)
- [DATA/raw/run-0035-sham_replay_drive_1.15-seed-104.json.gz](DATA/raw/run-0035-sham_replay_drive_1.15-seed-104.json.gz)
- [DATA/raw/run-0036-learning_on_drive_0.85-seed-105.json.gz](DATA/raw/run-0036-learning_on_drive_0.85-seed-105.json.gz)
- [DATA/raw/run-0037-learning_on_drive_1.00-seed-105.json.gz](DATA/raw/run-0037-learning_on_drive_1.00-seed-105.json.gz)
- [DATA/raw/run-0038-learning_on_drive_1.15-seed-105.json.gz](DATA/raw/run-0038-learning_on_drive_1.15-seed-105.json.gz)
- [DATA/raw/run-0039-learning_off_drive_0.85-seed-105.json.gz](DATA/raw/run-0039-learning_off_drive_0.85-seed-105.json.gz)
- [DATA/raw/run-0040-learning_off_drive_1.00-seed-105.json.gz](DATA/raw/run-0040-learning_off_drive_1.00-seed-105.json.gz)
- [DATA/raw/run-0041-learning_off_drive_1.15-seed-105.json.gz](DATA/raw/run-0041-learning_off_drive_1.15-seed-105.json.gz)
- [DATA/raw/run-0042-sham_replay_drive_0.85-seed-105.json.gz](DATA/raw/run-0042-sham_replay_drive_0.85-seed-105.json.gz)
- [DATA/raw/run-0043-sham_replay_drive_1.00-seed-105.json.gz](DATA/raw/run-0043-sham_replay_drive_1.00-seed-105.json.gz)
- [DATA/raw/run-0044-sham_replay_drive_1.15-seed-105.json.gz](DATA/raw/run-0044-sham_replay_drive_1.15-seed-105.json.gz)
- [DATA/raw/run-0045-learning_on_drive_0.85-seed-106.json.gz](DATA/raw/run-0045-learning_on_drive_0.85-seed-106.json.gz)
- [DATA/raw/run-0046-learning_on_drive_1.00-seed-106.json.gz](DATA/raw/run-0046-learning_on_drive_1.00-seed-106.json.gz)
- [DATA/raw/run-0047-learning_on_drive_1.15-seed-106.json.gz](DATA/raw/run-0047-learning_on_drive_1.15-seed-106.json.gz)
- [DATA/raw/run-0048-learning_off_drive_0.85-seed-106.json.gz](DATA/raw/run-0048-learning_off_drive_0.85-seed-106.json.gz)
- [DATA/raw/run-0049-learning_off_drive_1.00-seed-106.json.gz](DATA/raw/run-0049-learning_off_drive_1.00-seed-106.json.gz)
- [DATA/raw/run-0050-learning_off_drive_1.15-seed-106.json.gz](DATA/raw/run-0050-learning_off_drive_1.15-seed-106.json.gz)
- [DATA/raw/run-0051-sham_replay_drive_0.85-seed-106.json.gz](DATA/raw/run-0051-sham_replay_drive_0.85-seed-106.json.gz)
- [DATA/raw/run-0052-sham_replay_drive_1.00-seed-106.json.gz](DATA/raw/run-0052-sham_replay_drive_1.00-seed-106.json.gz)
- [DATA/raw/run-0053-sham_replay_drive_1.15-seed-106.json.gz](DATA/raw/run-0053-sham_replay_drive_1.15-seed-106.json.gz)
- [DATA/raw/run-0054-learning_on_drive_0.85-seed-107.json.gz](DATA/raw/run-0054-learning_on_drive_0.85-seed-107.json.gz)
- [DATA/raw/run-0055-learning_on_drive_1.00-seed-107.json.gz](DATA/raw/run-0055-learning_on_drive_1.00-seed-107.json.gz)
- [DATA/raw/run-0056-learning_on_drive_1.15-seed-107.json.gz](DATA/raw/run-0056-learning_on_drive_1.15-seed-107.json.gz)
- [DATA/raw/run-0057-learning_off_drive_0.85-seed-107.json.gz](DATA/raw/run-0057-learning_off_drive_0.85-seed-107.json.gz)
- [DATA/raw/run-0058-learning_off_drive_1.00-seed-107.json.gz](DATA/raw/run-0058-learning_off_drive_1.00-seed-107.json.gz)
- [DATA/raw/run-0059-learning_off_drive_1.15-seed-107.json.gz](DATA/raw/run-0059-learning_off_drive_1.15-seed-107.json.gz)
- [DATA/raw/run-0060-sham_replay_drive_0.85-seed-107.json.gz](DATA/raw/run-0060-sham_replay_drive_0.85-seed-107.json.gz)
- [DATA/raw/run-0061-sham_replay_drive_1.00-seed-107.json.gz](DATA/raw/run-0061-sham_replay_drive_1.00-seed-107.json.gz)
- [DATA/raw/run-0062-sham_replay_drive_1.15-seed-107.json.gz](DATA/raw/run-0062-sham_replay_drive_1.15-seed-107.json.gz)
- [DATA/raw/run-0063-learning_on_drive_0.85-seed-108.json.gz](DATA/raw/run-0063-learning_on_drive_0.85-seed-108.json.gz)
- [DATA/raw/run-0064-learning_on_drive_1.00-seed-108.json.gz](DATA/raw/run-0064-learning_on_drive_1.00-seed-108.json.gz)
- [DATA/raw/run-0065-learning_on_drive_1.15-seed-108.json.gz](DATA/raw/run-0065-learning_on_drive_1.15-seed-108.json.gz)
- [DATA/raw/run-0066-learning_off_drive_0.85-seed-108.json.gz](DATA/raw/run-0066-learning_off_drive_0.85-seed-108.json.gz)
- [DATA/raw/run-0067-learning_off_drive_1.00-seed-108.json.gz](DATA/raw/run-0067-learning_off_drive_1.00-seed-108.json.gz)
- [DATA/raw/run-0068-learning_off_drive_1.15-seed-108.json.gz](DATA/raw/run-0068-learning_off_drive_1.15-seed-108.json.gz)
- [DATA/raw/run-0069-sham_replay_drive_0.85-seed-108.json.gz](DATA/raw/run-0069-sham_replay_drive_0.85-seed-108.json.gz)
- [DATA/raw/run-0070-sham_replay_drive_1.00-seed-108.json.gz](DATA/raw/run-0070-sham_replay_drive_1.00-seed-108.json.gz)
- [DATA/raw/run-0071-sham_replay_drive_1.15-seed-108.json.gz](DATA/raw/run-0071-sham_replay_drive_1.15-seed-108.json.gz)
- [DATA/raw/run-0072-learning_on_drive_0.85-seed-109.json.gz](DATA/raw/run-0072-learning_on_drive_0.85-seed-109.json.gz)
- [DATA/raw/run-0073-learning_on_drive_1.00-seed-109.json.gz](DATA/raw/run-0073-learning_on_drive_1.00-seed-109.json.gz)
- [DATA/raw/run-0074-learning_on_drive_1.15-seed-109.json.gz](DATA/raw/run-0074-learning_on_drive_1.15-seed-109.json.gz)
- [DATA/raw/run-0075-learning_off_drive_0.85-seed-109.json.gz](DATA/raw/run-0075-learning_off_drive_0.85-seed-109.json.gz)
- [DATA/raw/run-0076-learning_off_drive_1.00-seed-109.json.gz](DATA/raw/run-0076-learning_off_drive_1.00-seed-109.json.gz)
- [DATA/raw/run-0077-learning_off_drive_1.15-seed-109.json.gz](DATA/raw/run-0077-learning_off_drive_1.15-seed-109.json.gz)
- [DATA/raw/run-0078-sham_replay_drive_0.85-seed-109.json.gz](DATA/raw/run-0078-sham_replay_drive_0.85-seed-109.json.gz)
- [DATA/raw/run-0079-sham_replay_drive_1.00-seed-109.json.gz](DATA/raw/run-0079-sham_replay_drive_1.00-seed-109.json.gz)
- [DATA/raw/run-0080-sham_replay_drive_1.15-seed-109.json.gz](DATA/raw/run-0080-sham_replay_drive_1.15-seed-109.json.gz)
- [DATA/raw/run-0081-learning_on_drive_0.85-seed-110.json.gz](DATA/raw/run-0081-learning_on_drive_0.85-seed-110.json.gz)
- [DATA/raw/run-0082-learning_on_drive_1.00-seed-110.json.gz](DATA/raw/run-0082-learning_on_drive_1.00-seed-110.json.gz)
- [DATA/raw/run-0083-learning_on_drive_1.15-seed-110.json.gz](DATA/raw/run-0083-learning_on_drive_1.15-seed-110.json.gz)
- [DATA/raw/run-0084-learning_off_drive_0.85-seed-110.json.gz](DATA/raw/run-0084-learning_off_drive_0.85-seed-110.json.gz)
- [DATA/raw/run-0085-learning_off_drive_1.00-seed-110.json.gz](DATA/raw/run-0085-learning_off_drive_1.00-seed-110.json.gz)
- [DATA/raw/run-0086-learning_off_drive_1.15-seed-110.json.gz](DATA/raw/run-0086-learning_off_drive_1.15-seed-110.json.gz)
- [DATA/raw/run-0087-sham_replay_drive_0.85-seed-110.json.gz](DATA/raw/run-0087-sham_replay_drive_0.85-seed-110.json.gz)
- [DATA/raw/run-0088-sham_replay_drive_1.00-seed-110.json.gz](DATA/raw/run-0088-sham_replay_drive_1.00-seed-110.json.gz)
- [DATA/raw/run-0089-sham_replay_drive_1.15-seed-110.json.gz](DATA/raw/run-0089-sham_replay_drive_1.15-seed-110.json.gz)
- [DATA/raw/run-0090-learning_on_drive_0.85-seed-111.json.gz](DATA/raw/run-0090-learning_on_drive_0.85-seed-111.json.gz)
- [DATA/raw/run-0091-learning_on_drive_1.00-seed-111.json.gz](DATA/raw/run-0091-learning_on_drive_1.00-seed-111.json.gz)
- [DATA/raw/run-0092-learning_on_drive_1.15-seed-111.json.gz](DATA/raw/run-0092-learning_on_drive_1.15-seed-111.json.gz)
- [DATA/raw/run-0093-learning_off_drive_0.85-seed-111.json.gz](DATA/raw/run-0093-learning_off_drive_0.85-seed-111.json.gz)
- [DATA/raw/run-0094-learning_off_drive_1.00-seed-111.json.gz](DATA/raw/run-0094-learning_off_drive_1.00-seed-111.json.gz)
- [DATA/raw/run-0095-learning_off_drive_1.15-seed-111.json.gz](DATA/raw/run-0095-learning_off_drive_1.15-seed-111.json.gz)
- [DATA/raw/run-0096-sham_replay_drive_0.85-seed-111.json.gz](DATA/raw/run-0096-sham_replay_drive_0.85-seed-111.json.gz)
- [DATA/raw/run-0097-sham_replay_drive_1.00-seed-111.json.gz](DATA/raw/run-0097-sham_replay_drive_1.00-seed-111.json.gz)
- [DATA/raw/run-0098-sham_replay_drive_1.15-seed-111.json.gz](DATA/raw/run-0098-sham_replay_drive_1.15-seed-111.json.gz)
- [DATA/raw/run-0099-learning_on_drive_0.85-seed-112.json.gz](DATA/raw/run-0099-learning_on_drive_0.85-seed-112.json.gz)
- [DATA/raw/run-0100-learning_on_drive_1.00-seed-112.json.gz](DATA/raw/run-0100-learning_on_drive_1.00-seed-112.json.gz)
- [DATA/raw/run-0101-learning_on_drive_1.15-seed-112.json.gz](DATA/raw/run-0101-learning_on_drive_1.15-seed-112.json.gz)
- [DATA/raw/run-0102-learning_off_drive_0.85-seed-112.json.gz](DATA/raw/run-0102-learning_off_drive_0.85-seed-112.json.gz)
- [DATA/raw/run-0103-learning_off_drive_1.00-seed-112.json.gz](DATA/raw/run-0103-learning_off_drive_1.00-seed-112.json.gz)
- [DATA/raw/run-0104-learning_off_drive_1.15-seed-112.json.gz](DATA/raw/run-0104-learning_off_drive_1.15-seed-112.json.gz)
- [DATA/raw/run-0105-sham_replay_drive_0.85-seed-112.json.gz](DATA/raw/run-0105-sham_replay_drive_0.85-seed-112.json.gz)
- [DATA/raw/run-0106-sham_replay_drive_1.00-seed-112.json.gz](DATA/raw/run-0106-sham_replay_drive_1.00-seed-112.json.gz)
- [DATA/raw/run-0107-sham_replay_drive_1.15-seed-112.json.gz](DATA/raw/run-0107-sham_replay_drive_1.15-seed-112.json.gz)
- [DATA/raw/run-0108-learning_on_drive_0.85-seed-113.json.gz](DATA/raw/run-0108-learning_on_drive_0.85-seed-113.json.gz)
- [DATA/raw/run-0109-learning_on_drive_1.00-seed-113.json.gz](DATA/raw/run-0109-learning_on_drive_1.00-seed-113.json.gz)
- [DATA/raw/run-0110-learning_on_drive_1.15-seed-113.json.gz](DATA/raw/run-0110-learning_on_drive_1.15-seed-113.json.gz)
- [DATA/raw/run-0111-learning_off_drive_0.85-seed-113.json.gz](DATA/raw/run-0111-learning_off_drive_0.85-seed-113.json.gz)
- [DATA/raw/run-0112-learning_off_drive_1.00-seed-113.json.gz](DATA/raw/run-0112-learning_off_drive_1.00-seed-113.json.gz)
- [DATA/raw/run-0113-learning_off_drive_1.15-seed-113.json.gz](DATA/raw/run-0113-learning_off_drive_1.15-seed-113.json.gz)
- [DATA/raw/run-0114-sham_replay_drive_0.85-seed-113.json.gz](DATA/raw/run-0114-sham_replay_drive_0.85-seed-113.json.gz)
- [DATA/raw/run-0115-sham_replay_drive_1.00-seed-113.json.gz](DATA/raw/run-0115-sham_replay_drive_1.00-seed-113.json.gz)
- [DATA/raw/run-0116-sham_replay_drive_1.15-seed-113.json.gz](DATA/raw/run-0116-sham_replay_drive_1.15-seed-113.json.gz)
- [DATA/raw/run-0117-learning_on_drive_0.85-seed-114.json.gz](DATA/raw/run-0117-learning_on_drive_0.85-seed-114.json.gz)
- [DATA/raw/run-0118-learning_on_drive_1.00-seed-114.json.gz](DATA/raw/run-0118-learning_on_drive_1.00-seed-114.json.gz)
- [DATA/raw/run-0119-learning_on_drive_1.15-seed-114.json.gz](DATA/raw/run-0119-learning_on_drive_1.15-seed-114.json.gz)
- [DATA/raw/run-0120-learning_off_drive_0.85-seed-114.json.gz](DATA/raw/run-0120-learning_off_drive_0.85-seed-114.json.gz)
- [DATA/raw/run-0121-learning_off_drive_1.00-seed-114.json.gz](DATA/raw/run-0121-learning_off_drive_1.00-seed-114.json.gz)
- [DATA/raw/run-0122-learning_off_drive_1.15-seed-114.json.gz](DATA/raw/run-0122-learning_off_drive_1.15-seed-114.json.gz)
- [DATA/raw/run-0123-sham_replay_drive_0.85-seed-114.json.gz](DATA/raw/run-0123-sham_replay_drive_0.85-seed-114.json.gz)
- [DATA/raw/run-0124-sham_replay_drive_1.00-seed-114.json.gz](DATA/raw/run-0124-sham_replay_drive_1.00-seed-114.json.gz)
- [DATA/raw/run-0125-sham_replay_drive_1.15-seed-114.json.gz](DATA/raw/run-0125-sham_replay_drive_1.15-seed-114.json.gz)
- [DATA/raw/run-0126-learning_on_drive_0.85-seed-115.json.gz](DATA/raw/run-0126-learning_on_drive_0.85-seed-115.json.gz)
- [DATA/raw/run-0127-learning_on_drive_1.00-seed-115.json.gz](DATA/raw/run-0127-learning_on_drive_1.00-seed-115.json.gz)
- [DATA/raw/run-0128-learning_on_drive_1.15-seed-115.json.gz](DATA/raw/run-0128-learning_on_drive_1.15-seed-115.json.gz)
- [DATA/raw/run-0129-learning_off_drive_0.85-seed-115.json.gz](DATA/raw/run-0129-learning_off_drive_0.85-seed-115.json.gz)
- [DATA/raw/run-0130-learning_off_drive_1.00-seed-115.json.gz](DATA/raw/run-0130-learning_off_drive_1.00-seed-115.json.gz)
- [DATA/raw/run-0131-learning_off_drive_1.15-seed-115.json.gz](DATA/raw/run-0131-learning_off_drive_1.15-seed-115.json.gz)
- [DATA/raw/run-0132-sham_replay_drive_0.85-seed-115.json.gz](DATA/raw/run-0132-sham_replay_drive_0.85-seed-115.json.gz)
- [DATA/raw/run-0133-sham_replay_drive_1.00-seed-115.json.gz](DATA/raw/run-0133-sham_replay_drive_1.00-seed-115.json.gz)
- [DATA/raw/run-0134-sham_replay_drive_1.15-seed-115.json.gz](DATA/raw/run-0134-sham_replay_drive_1.15-seed-115.json.gz)
- [DATA/raw/run-0135-learning_on_drive_0.85-seed-116.json.gz](DATA/raw/run-0135-learning_on_drive_0.85-seed-116.json.gz)
- [DATA/raw/run-0136-learning_on_drive_1.00-seed-116.json.gz](DATA/raw/run-0136-learning_on_drive_1.00-seed-116.json.gz)
- [DATA/raw/run-0137-learning_on_drive_1.15-seed-116.json.gz](DATA/raw/run-0137-learning_on_drive_1.15-seed-116.json.gz)
- [DATA/raw/run-0138-learning_off_drive_0.85-seed-116.json.gz](DATA/raw/run-0138-learning_off_drive_0.85-seed-116.json.gz)
- [DATA/raw/run-0139-learning_off_drive_1.00-seed-116.json.gz](DATA/raw/run-0139-learning_off_drive_1.00-seed-116.json.gz)
- [DATA/raw/run-0140-learning_off_drive_1.15-seed-116.json.gz](DATA/raw/run-0140-learning_off_drive_1.15-seed-116.json.gz)
- [DATA/raw/run-0141-sham_replay_drive_0.85-seed-116.json.gz](DATA/raw/run-0141-sham_replay_drive_0.85-seed-116.json.gz)
- [DATA/raw/run-0142-sham_replay_drive_1.00-seed-116.json.gz](DATA/raw/run-0142-sham_replay_drive_1.00-seed-116.json.gz)
- [DATA/raw/run-0143-sham_replay_drive_1.15-seed-116.json.gz](DATA/raw/run-0143-sham_replay_drive_1.15-seed-116.json.gz)
- [DATA/raw/run-0144-learning_on_drive_0.85-seed-117.json.gz](DATA/raw/run-0144-learning_on_drive_0.85-seed-117.json.gz)
- [DATA/raw/run-0145-learning_on_drive_1.00-seed-117.json.gz](DATA/raw/run-0145-learning_on_drive_1.00-seed-117.json.gz)
- [DATA/raw/run-0146-learning_on_drive_1.15-seed-117.json.gz](DATA/raw/run-0146-learning_on_drive_1.15-seed-117.json.gz)
- [DATA/raw/run-0147-learning_off_drive_0.85-seed-117.json.gz](DATA/raw/run-0147-learning_off_drive_0.85-seed-117.json.gz)
- [DATA/raw/run-0148-learning_off_drive_1.00-seed-117.json.gz](DATA/raw/run-0148-learning_off_drive_1.00-seed-117.json.gz)
- [DATA/raw/run-0149-learning_off_drive_1.15-seed-117.json.gz](DATA/raw/run-0149-learning_off_drive_1.15-seed-117.json.gz)
- [DATA/raw/run-0150-sham_replay_drive_0.85-seed-117.json.gz](DATA/raw/run-0150-sham_replay_drive_0.85-seed-117.json.gz)
- [DATA/raw/run-0151-sham_replay_drive_1.00-seed-117.json.gz](DATA/raw/run-0151-sham_replay_drive_1.00-seed-117.json.gz)
- [DATA/raw/run-0152-sham_replay_drive_1.15-seed-117.json.gz](DATA/raw/run-0152-sham_replay_drive_1.15-seed-117.json.gz)
- [DATA/raw/run-0153-learning_on_drive_0.85-seed-118.json.gz](DATA/raw/run-0153-learning_on_drive_0.85-seed-118.json.gz)
- [DATA/raw/run-0154-learning_on_drive_1.00-seed-118.json.gz](DATA/raw/run-0154-learning_on_drive_1.00-seed-118.json.gz)
- [DATA/raw/run-0155-learning_on_drive_1.15-seed-118.json.gz](DATA/raw/run-0155-learning_on_drive_1.15-seed-118.json.gz)
- [DATA/raw/run-0156-learning_off_drive_0.85-seed-118.json.gz](DATA/raw/run-0156-learning_off_drive_0.85-seed-118.json.gz)
- [DATA/raw/run-0157-learning_off_drive_1.00-seed-118.json.gz](DATA/raw/run-0157-learning_off_drive_1.00-seed-118.json.gz)
- [DATA/raw/run-0158-learning_off_drive_1.15-seed-118.json.gz](DATA/raw/run-0158-learning_off_drive_1.15-seed-118.json.gz)
- [DATA/raw/run-0159-sham_replay_drive_0.85-seed-118.json.gz](DATA/raw/run-0159-sham_replay_drive_0.85-seed-118.json.gz)
- [DATA/raw/run-0160-sham_replay_drive_1.00-seed-118.json.gz](DATA/raw/run-0160-sham_replay_drive_1.00-seed-118.json.gz)
- [DATA/raw/run-0161-sham_replay_drive_1.15-seed-118.json.gz](DATA/raw/run-0161-sham_replay_drive_1.15-seed-118.json.gz)
- [DATA/raw/run-0162-learning_on_drive_0.85-seed-119.json.gz](DATA/raw/run-0162-learning_on_drive_0.85-seed-119.json.gz)
- [DATA/raw/run-0163-learning_on_drive_1.00-seed-119.json.gz](DATA/raw/run-0163-learning_on_drive_1.00-seed-119.json.gz)
- [DATA/raw/run-0164-learning_on_drive_1.15-seed-119.json.gz](DATA/raw/run-0164-learning_on_drive_1.15-seed-119.json.gz)
- [DATA/raw/run-0165-learning_off_drive_0.85-seed-119.json.gz](DATA/raw/run-0165-learning_off_drive_0.85-seed-119.json.gz)
- [DATA/raw/run-0166-learning_off_drive_1.00-seed-119.json.gz](DATA/raw/run-0166-learning_off_drive_1.00-seed-119.json.gz)
- [DATA/raw/run-0167-learning_off_drive_1.15-seed-119.json.gz](DATA/raw/run-0167-learning_off_drive_1.15-seed-119.json.gz)
- [DATA/raw/run-0168-sham_replay_drive_0.85-seed-119.json.gz](DATA/raw/run-0168-sham_replay_drive_0.85-seed-119.json.gz)
- [DATA/raw/run-0169-sham_replay_drive_1.00-seed-119.json.gz](DATA/raw/run-0169-sham_replay_drive_1.00-seed-119.json.gz)
- [DATA/raw/run-0170-sham_replay_drive_1.15-seed-119.json.gz](DATA/raw/run-0170-sham_replay_drive_1.15-seed-119.json.gz)
- [DATA/raw/run-0171-learning_on_drive_0.85-seed-120.json.gz](DATA/raw/run-0171-learning_on_drive_0.85-seed-120.json.gz)
- [DATA/raw/run-0172-learning_on_drive_1.00-seed-120.json.gz](DATA/raw/run-0172-learning_on_drive_1.00-seed-120.json.gz)
- [DATA/raw/run-0173-learning_on_drive_1.15-seed-120.json.gz](DATA/raw/run-0173-learning_on_drive_1.15-seed-120.json.gz)
- [DATA/raw/run-0174-learning_off_drive_0.85-seed-120.json.gz](DATA/raw/run-0174-learning_off_drive_0.85-seed-120.json.gz)
- [DATA/raw/run-0175-learning_off_drive_1.00-seed-120.json.gz](DATA/raw/run-0175-learning_off_drive_1.00-seed-120.json.gz)
- [DATA/raw/run-0176-learning_off_drive_1.15-seed-120.json.gz](DATA/raw/run-0176-learning_off_drive_1.15-seed-120.json.gz)
- [DATA/raw/run-0177-sham_replay_drive_0.85-seed-120.json.gz](DATA/raw/run-0177-sham_replay_drive_0.85-seed-120.json.gz)
- [DATA/raw/run-0178-sham_replay_drive_1.00-seed-120.json.gz](DATA/raw/run-0178-sham_replay_drive_1.00-seed-120.json.gz)
- [DATA/raw/run-0179-sham_replay_drive_1.15-seed-120.json.gz](DATA/raw/run-0179-sham_replay_drive_1.15-seed-120.json.gz)
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
