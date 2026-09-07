# EXP-BATCH-20260906200118-35: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REC-001`
- Hypothese: `H-REC-001-A`
- Protokoll: `recurrence_map_v1`
- Durchlaeufe: `300`
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
- Begründung: REC-001 erwartet eine registrierte Rekurrenz-Gewicht/Delay-Karte mit Nullkontrolle.
- Beobachtete Conditions: `w0_d1, w0_d2, w0_d4, w100_d1, w100_d2, w100_d4, w125_d1, w125_d2, w125_d4, w50_d1, w50_d2, w50_d4, w75_d1, w75_d2, w75_d4`

`DIRECT_MATCH` bezeichnet einen gezielten RQ-spezifischen Lauf. `CONTAINS_MATCH` bedeutet, dass die passende Teilstudie innerhalb einer Gesamtsuite enthalten ist; nur diese Teilstudie ist primaer fuer die registrierte RQ auszuwerten. `MISMATCH` blockiert die Nutzung als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.

## 3. Ausfuehrungsparameter

- Titel: Experiment workflow: recurrence_map_v1
- Bedingungen: Registered protocol conditions
- Notizen: Keine.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `275f3b77df6e89cc224d8542454434ff7e84d7a4`
- Git dirty: `True`
- Runtime: `0.6899207000387833` s

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
| w0_d1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 3 | 2 | 3 | 0 | 1 |
| w0_d2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 3 | 2 | 3 | 0 | 1 |
| w0_d4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 3 | 2 | 3 | 0 | 1 |
| w100_d1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 33 | 33 | 3 | 10 | 61 |
| w100_d2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 102 | 102 | 3 | 33 | 251 |
| w100_d4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 87 | 87 | 3 | 28 | 250 |
| w125_d1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 43 | 43 | 3 | 14 | 83 |
| w125_d2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 105 | 104 | 3 | 34 | 254 |
| w125_d4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 91 | 90 | 3 | 30 | 249 |
| w50_d1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 6 | 6 | 3 | 1 | 6 |
| w50_d2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 6 | 6 | 3 | 1 | 7 |
| w50_d4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 6 | 6 | 3 | 1 | 9 |
| w75_d1 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 15 | 15 | 3 | 4 | 24 |
| w75_d2 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 15 | 15 | 3 | 4 | 28 |
| w75_d4 | 20 | 101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 | 256 | 21 | 21 | 3 | 6 | 56 |

### 5.2 Inter-Spike-Intervalle

- `w0_d1`: n=40, mean=1, median=1, min=1, max=1 Ticks.
- `w0_d2`: n=40, mean=1, median=1, min=1, max=1 Ticks.
- `w0_d4`: n=40, mean=1, median=1, min=1, max=1 Ticks.
- `w100_d1`: n=640, mean=1.9375, median=2, min=1, max=4 Ticks.
- `w100_d2`: n=2020, mean=2.49505, median=2, min=1, max=4 Ticks.
- `w100_d4`: n=1720, mean=2.9186, median=2, min=1, max=5 Ticks.
- `w125_d1`: n=840, mean=2.04762, median=2, min=1, max=5 Ticks.
- `w125_d2`: n=2080, mean=2.45192, median=2, min=1, max=3 Ticks.
- `w125_d4`: n=1800, mean=2.83333, median=2, min=1, max=5 Ticks.
- `w50_d1`: n=100, mean=1.4, median=1, min=1, max=3 Ticks.
- `w50_d2`: n=100, mean=1.6, median=1, min=1, max=4 Ticks.
- `w50_d4`: n=100, mean=2, median=1, min=1, max=6 Ticks.
- `w75_d1`: n=280, mean=1.78571, median=2, min=1, max=3 Ticks.
- `w75_d2`: n=280, mean=2.07143, median=2, min=1, max=4 Ticks.
- `w75_d4`: n=400, mean=2.85, median=2, min=1, max=7 Ticks.

## 6. Einzelne Läufe

| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 101 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 101 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 101 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 101 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 101 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 101 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 101 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 101 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 101 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 101 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 101 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 101 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 102 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 102 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 102 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 102 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 102 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 102 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 102 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 102 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 102 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 102 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 102 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 102 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 102 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 103 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 103 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 103 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 103 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 103 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 103 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 103 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 103 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 103 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 103 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 103 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 103 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 103 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 104 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 104 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 104 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 104 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 104 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 104 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 104 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 104 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 104 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 104 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 104 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 104 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 104 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 105 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 105 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 105 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 105 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 105 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 105 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 105 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 105 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 105 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 105 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 105 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 105 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 105 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 106 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 106 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 106 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 106 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 106 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 106 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 106 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 106 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 106 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 106 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 106 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 106 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 106 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 107 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 107 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 107 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 107 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 107 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 107 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 107 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 107 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 107 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 107 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 107 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 107 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 107 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 108 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 108 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 108 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 108 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 108 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 108 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 108 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 108 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 108 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 108 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 108 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 108 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 108 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 109 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 109 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 109 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 109 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 109 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 109 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 109 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 109 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 109 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 109 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 109 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 109 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 109 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 110 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 110 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 110 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 110 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 110 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 110 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 110 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 110 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 110 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 110 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 110 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 110 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 110 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 111 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 111 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 111 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 111 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 111 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 111 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 111 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 111 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 111 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 111 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 111 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 111 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 111 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 112 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 112 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 112 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 112 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 112 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 112 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 112 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 112 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 112 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 112 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 112 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 112 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 112 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 113 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 113 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 113 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 113 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 113 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 113 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 113 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 113 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 113 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 113 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 113 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 113 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 113 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 114 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 114 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 114 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 114 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 114 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 114 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 114 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 114 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 114 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 114 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 114 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 114 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 114 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 115 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 115 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 115 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 115 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 115 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 115 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 115 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 115 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 115 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 115 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 115 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 115 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 115 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 116 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 116 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 116 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 116 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 116 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 116 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 116 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 116 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 116 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 116 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 116 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 116 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 116 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 117 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 117 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 117 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 117 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 117 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 117 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 117 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 117 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 117 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 117 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 117 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 117 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 117 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 118 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 118 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 118 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 118 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 118 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 118 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 118 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 118 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 118 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 118 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 118 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 118 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 118 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 119 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 119 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 119 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 119 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 119 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 119 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 119 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 119 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 119 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 119 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 119 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 119 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 119 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 120 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 120 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 120 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 120 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 120 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 120 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 120 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 120 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 120 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 120 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 120 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 120 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 120 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |

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

Die Analyse der experimentellen Daten zeigt einen klaren, deskriptiven Trend: Mit steigendem Rekurrenzgewicht (w) und einem geeigneten Delay (d) nimmt die beobachtete neuronale Aktivität und die Dauer der Aktivität zu. Die Bedingungen mit niedrigen Parametern (z.B. w0_d1, w0_d2, w0_d4) zeigen durchweg geringe Aktivitätsmetriken und kurze Spike-Sequenzen, was auf ein sofortiges Abklingen hindeutet. Im Gegensatz dazu zeigen die Bedingungen mit hohen Parametern (z.B. w125_d2, w125_d4) deutlich höhere Werte für 'delivered_synaptic_events', 'propagation_depth' und 'total_spikes', was auf eine anhaltende oder persistierende Aktivität hindeutet. Die Daten legen nahe, dass die Kombination von hohem w und hohem d die Aktivität maximiert.

KI-Konfidenz: `0.9` — dies ist keine statistische Konfidenz.

### Methodische Kritik

- Die statistische Analyse basiert auf Stichproben von 20 Läufen pro Bedingung, was die Verallgemeinerbarkeit der Mittelwerte einschränkt.
- Die Interpretation von 'persistence_class' ist deskriptiv und sollte nicht als Beweis für kausale Mechanismen interpretiert werden.
- Die Analyse ignoriert die potenziellen Interaktionen zwischen w und d, indem sie die Ergebnisse nur als separate Mittelwerte präsentiert. Eine Untersuchung der Interaktionsterme wäre notwendig, um die Abhängigkeit zu präzisieren.

### Alternative Erklaerungen

- Die beobachteten Unterschiede könnten auf die spezifische Skalierung der Lernparameter (w und d) im Verhältnis zur neuronalen Basisrate oder der Systemgröße zurückzuführen sein, was die beobachteten Effekte überdimensioniert erscheinen lässt.
- Die beobachteten Muster könnten durch die spezifische Architektur des Netzwerks und die Art der Eingabe (Input) bedingt sein, anstatt primär durch die Parameter w und d. Die Rolle des Initialzustands (State Digest Before) wurde nicht systematisch variiert.
- Die beobachteten Effekte könnten durch die Art der verwendeten Simulationsumgebung (z.B. Ticks-Limit von 256) begrenzt sein, was die tatsächliche Langzeitdynamik maskiert.

### Fehlende Nachweise

- Detaillierte Informationen über die genaue Funktionsweise der 'recurrent_weight' und 'recurrent_delay' im Kontext des verwendeten neuronalen Modells sind erforderlich, um die beobachteten Effekte zu verifizieren.
- Eine Analyse, die die Abhängigkeit der Aktivität von der Anzahl der Neuronen (N) und der Anzahl der Synapsen (S) berücksichtigt, wäre hilfreich, um die beobachteten Effekte von der Komplexität des Systems zu trennen.

### Empfohlene Folgeexperimente

- Durchführung eines systematischen Grid-Search-Experiments, um die optimale Kombination von w und d zu identifizieren, die die maximale Persistenz bei minimalem Energieverbrauch gewährleistet.
- Vergleich der Ergebnisse mit einem Netzwerk, das andere Arten von Rekurrenzmechanismen (z.B. Feedback-Schleifen mit unterschiedlichen Zeitkonstanten) verwendet, um die Rolle des 'recurrent_delay' zu isolieren.
- Analyse der zeitlichen Entwicklung der Aktivität (Spike-Sequenzen) über einen noch längeren Beobachtungszeitraum hinaus, um die tatsächliche Langzeitdynamik zu erfassen.

## 9. Artefakte

- [analysis/ai_packet.json](analysis/ai_packet.json)
- [analysis/ai_packet_digest.json](analysis/ai_packet_digest.json)
- [analysis/AIAR-critical_reviewer-20260906225403278461-06f4d845.json](analysis/AIAR-critical_reviewer-20260906225403278461-06f4d845.json)
- [analysis/AIAR-scientific_analyst-20260906225327375427-06f4d845.json](analysis/AIAR-scientific_analyst-20260906225327375427-06f4d845.json)
- [analysis/AIAR-scientific_writer-20260906225446420587-06f4d845.json](analysis/AIAR-scientific_writer-20260906225446420587-06f4d845.json)
- [analysis/statistics.json](analysis/statistics.json)
- [DATA/current_run.json](DATA/current_run.json)
- [DATA/raw/run-0000-w0_d1-seed-101.json.gz](DATA/raw/run-0000-w0_d1-seed-101.json.gz)
- [DATA/raw/run-0001-w0_d2-seed-101.json.gz](DATA/raw/run-0001-w0_d2-seed-101.json.gz)
- [DATA/raw/run-0002-w0_d4-seed-101.json.gz](DATA/raw/run-0002-w0_d4-seed-101.json.gz)
- [DATA/raw/run-0003-w50_d1-seed-101.json.gz](DATA/raw/run-0003-w50_d1-seed-101.json.gz)
- [DATA/raw/run-0004-w50_d2-seed-101.json.gz](DATA/raw/run-0004-w50_d2-seed-101.json.gz)
- [DATA/raw/run-0005-w50_d4-seed-101.json.gz](DATA/raw/run-0005-w50_d4-seed-101.json.gz)
- [DATA/raw/run-0006-w75_d1-seed-101.json.gz](DATA/raw/run-0006-w75_d1-seed-101.json.gz)
- [DATA/raw/run-0007-w75_d2-seed-101.json.gz](DATA/raw/run-0007-w75_d2-seed-101.json.gz)
- [DATA/raw/run-0008-w75_d4-seed-101.json.gz](DATA/raw/run-0008-w75_d4-seed-101.json.gz)
- [DATA/raw/run-0009-w100_d1-seed-101.json.gz](DATA/raw/run-0009-w100_d1-seed-101.json.gz)
- [DATA/raw/run-0010-w100_d2-seed-101.json.gz](DATA/raw/run-0010-w100_d2-seed-101.json.gz)
- [DATA/raw/run-0011-w100_d4-seed-101.json.gz](DATA/raw/run-0011-w100_d4-seed-101.json.gz)
- [DATA/raw/run-0012-w125_d1-seed-101.json.gz](DATA/raw/run-0012-w125_d1-seed-101.json.gz)
- [DATA/raw/run-0013-w125_d2-seed-101.json.gz](DATA/raw/run-0013-w125_d2-seed-101.json.gz)
- [DATA/raw/run-0014-w125_d4-seed-101.json.gz](DATA/raw/run-0014-w125_d4-seed-101.json.gz)
- [DATA/raw/run-0015-w0_d1-seed-102.json.gz](DATA/raw/run-0015-w0_d1-seed-102.json.gz)
- [DATA/raw/run-0016-w0_d2-seed-102.json.gz](DATA/raw/run-0016-w0_d2-seed-102.json.gz)
- [DATA/raw/run-0017-w0_d4-seed-102.json.gz](DATA/raw/run-0017-w0_d4-seed-102.json.gz)
- [DATA/raw/run-0018-w50_d1-seed-102.json.gz](DATA/raw/run-0018-w50_d1-seed-102.json.gz)
- [DATA/raw/run-0019-w50_d2-seed-102.json.gz](DATA/raw/run-0019-w50_d2-seed-102.json.gz)
- [DATA/raw/run-0020-w50_d4-seed-102.json.gz](DATA/raw/run-0020-w50_d4-seed-102.json.gz)
- [DATA/raw/run-0021-w75_d1-seed-102.json.gz](DATA/raw/run-0021-w75_d1-seed-102.json.gz)
- [DATA/raw/run-0022-w75_d2-seed-102.json.gz](DATA/raw/run-0022-w75_d2-seed-102.json.gz)
- [DATA/raw/run-0023-w75_d4-seed-102.json.gz](DATA/raw/run-0023-w75_d4-seed-102.json.gz)
- [DATA/raw/run-0024-w100_d1-seed-102.json.gz](DATA/raw/run-0024-w100_d1-seed-102.json.gz)
- [DATA/raw/run-0025-w100_d2-seed-102.json.gz](DATA/raw/run-0025-w100_d2-seed-102.json.gz)
- [DATA/raw/run-0026-w100_d4-seed-102.json.gz](DATA/raw/run-0026-w100_d4-seed-102.json.gz)
- [DATA/raw/run-0027-w125_d1-seed-102.json.gz](DATA/raw/run-0027-w125_d1-seed-102.json.gz)
- [DATA/raw/run-0028-w125_d2-seed-102.json.gz](DATA/raw/run-0028-w125_d2-seed-102.json.gz)
- [DATA/raw/run-0029-w125_d4-seed-102.json.gz](DATA/raw/run-0029-w125_d4-seed-102.json.gz)
- [DATA/raw/run-0030-w0_d1-seed-103.json.gz](DATA/raw/run-0030-w0_d1-seed-103.json.gz)
- [DATA/raw/run-0031-w0_d2-seed-103.json.gz](DATA/raw/run-0031-w0_d2-seed-103.json.gz)
- [DATA/raw/run-0032-w0_d4-seed-103.json.gz](DATA/raw/run-0032-w0_d4-seed-103.json.gz)
- [DATA/raw/run-0033-w50_d1-seed-103.json.gz](DATA/raw/run-0033-w50_d1-seed-103.json.gz)
- [DATA/raw/run-0034-w50_d2-seed-103.json.gz](DATA/raw/run-0034-w50_d2-seed-103.json.gz)
- [DATA/raw/run-0035-w50_d4-seed-103.json.gz](DATA/raw/run-0035-w50_d4-seed-103.json.gz)
- [DATA/raw/run-0036-w75_d1-seed-103.json.gz](DATA/raw/run-0036-w75_d1-seed-103.json.gz)
- [DATA/raw/run-0037-w75_d2-seed-103.json.gz](DATA/raw/run-0037-w75_d2-seed-103.json.gz)
- [DATA/raw/run-0038-w75_d4-seed-103.json.gz](DATA/raw/run-0038-w75_d4-seed-103.json.gz)
- [DATA/raw/run-0039-w100_d1-seed-103.json.gz](DATA/raw/run-0039-w100_d1-seed-103.json.gz)
- [DATA/raw/run-0040-w100_d2-seed-103.json.gz](DATA/raw/run-0040-w100_d2-seed-103.json.gz)
- [DATA/raw/run-0041-w100_d4-seed-103.json.gz](DATA/raw/run-0041-w100_d4-seed-103.json.gz)
- [DATA/raw/run-0042-w125_d1-seed-103.json.gz](DATA/raw/run-0042-w125_d1-seed-103.json.gz)
- [DATA/raw/run-0043-w125_d2-seed-103.json.gz](DATA/raw/run-0043-w125_d2-seed-103.json.gz)
- [DATA/raw/run-0044-w125_d4-seed-103.json.gz](DATA/raw/run-0044-w125_d4-seed-103.json.gz)
- [DATA/raw/run-0045-w0_d1-seed-104.json.gz](DATA/raw/run-0045-w0_d1-seed-104.json.gz)
- [DATA/raw/run-0046-w0_d2-seed-104.json.gz](DATA/raw/run-0046-w0_d2-seed-104.json.gz)
- [DATA/raw/run-0047-w0_d4-seed-104.json.gz](DATA/raw/run-0047-w0_d4-seed-104.json.gz)
- [DATA/raw/run-0048-w50_d1-seed-104.json.gz](DATA/raw/run-0048-w50_d1-seed-104.json.gz)
- [DATA/raw/run-0049-w50_d2-seed-104.json.gz](DATA/raw/run-0049-w50_d2-seed-104.json.gz)
- [DATA/raw/run-0050-w50_d4-seed-104.json.gz](DATA/raw/run-0050-w50_d4-seed-104.json.gz)
- [DATA/raw/run-0051-w75_d1-seed-104.json.gz](DATA/raw/run-0051-w75_d1-seed-104.json.gz)
- [DATA/raw/run-0052-w75_d2-seed-104.json.gz](DATA/raw/run-0052-w75_d2-seed-104.json.gz)
- [DATA/raw/run-0053-w75_d4-seed-104.json.gz](DATA/raw/run-0053-w75_d4-seed-104.json.gz)
- [DATA/raw/run-0054-w100_d1-seed-104.json.gz](DATA/raw/run-0054-w100_d1-seed-104.json.gz)
- [DATA/raw/run-0055-w100_d2-seed-104.json.gz](DATA/raw/run-0055-w100_d2-seed-104.json.gz)
- [DATA/raw/run-0056-w100_d4-seed-104.json.gz](DATA/raw/run-0056-w100_d4-seed-104.json.gz)
- [DATA/raw/run-0057-w125_d1-seed-104.json.gz](DATA/raw/run-0057-w125_d1-seed-104.json.gz)
- [DATA/raw/run-0058-w125_d2-seed-104.json.gz](DATA/raw/run-0058-w125_d2-seed-104.json.gz)
- [DATA/raw/run-0059-w125_d4-seed-104.json.gz](DATA/raw/run-0059-w125_d4-seed-104.json.gz)
- [DATA/raw/run-0060-w0_d1-seed-105.json.gz](DATA/raw/run-0060-w0_d1-seed-105.json.gz)
- [DATA/raw/run-0061-w0_d2-seed-105.json.gz](DATA/raw/run-0061-w0_d2-seed-105.json.gz)
- [DATA/raw/run-0062-w0_d4-seed-105.json.gz](DATA/raw/run-0062-w0_d4-seed-105.json.gz)
- [DATA/raw/run-0063-w50_d1-seed-105.json.gz](DATA/raw/run-0063-w50_d1-seed-105.json.gz)
- [DATA/raw/run-0064-w50_d2-seed-105.json.gz](DATA/raw/run-0064-w50_d2-seed-105.json.gz)
- [DATA/raw/run-0065-w50_d4-seed-105.json.gz](DATA/raw/run-0065-w50_d4-seed-105.json.gz)
- [DATA/raw/run-0066-w75_d1-seed-105.json.gz](DATA/raw/run-0066-w75_d1-seed-105.json.gz)
- [DATA/raw/run-0067-w75_d2-seed-105.json.gz](DATA/raw/run-0067-w75_d2-seed-105.json.gz)
- [DATA/raw/run-0068-w75_d4-seed-105.json.gz](DATA/raw/run-0068-w75_d4-seed-105.json.gz)
- [DATA/raw/run-0069-w100_d1-seed-105.json.gz](DATA/raw/run-0069-w100_d1-seed-105.json.gz)
- [DATA/raw/run-0070-w100_d2-seed-105.json.gz](DATA/raw/run-0070-w100_d2-seed-105.json.gz)
- [DATA/raw/run-0071-w100_d4-seed-105.json.gz](DATA/raw/run-0071-w100_d4-seed-105.json.gz)
- [DATA/raw/run-0072-w125_d1-seed-105.json.gz](DATA/raw/run-0072-w125_d1-seed-105.json.gz)
- [DATA/raw/run-0073-w125_d2-seed-105.json.gz](DATA/raw/run-0073-w125_d2-seed-105.json.gz)
- [DATA/raw/run-0074-w125_d4-seed-105.json.gz](DATA/raw/run-0074-w125_d4-seed-105.json.gz)
- [DATA/raw/run-0075-w0_d1-seed-106.json.gz](DATA/raw/run-0075-w0_d1-seed-106.json.gz)
- [DATA/raw/run-0076-w0_d2-seed-106.json.gz](DATA/raw/run-0076-w0_d2-seed-106.json.gz)
- [DATA/raw/run-0077-w0_d4-seed-106.json.gz](DATA/raw/run-0077-w0_d4-seed-106.json.gz)
- [DATA/raw/run-0078-w50_d1-seed-106.json.gz](DATA/raw/run-0078-w50_d1-seed-106.json.gz)
- [DATA/raw/run-0079-w50_d2-seed-106.json.gz](DATA/raw/run-0079-w50_d2-seed-106.json.gz)
- [DATA/raw/run-0080-w50_d4-seed-106.json.gz](DATA/raw/run-0080-w50_d4-seed-106.json.gz)
- [DATA/raw/run-0081-w75_d1-seed-106.json.gz](DATA/raw/run-0081-w75_d1-seed-106.json.gz)
- [DATA/raw/run-0082-w75_d2-seed-106.json.gz](DATA/raw/run-0082-w75_d2-seed-106.json.gz)
- [DATA/raw/run-0083-w75_d4-seed-106.json.gz](DATA/raw/run-0083-w75_d4-seed-106.json.gz)
- [DATA/raw/run-0084-w100_d1-seed-106.json.gz](DATA/raw/run-0084-w100_d1-seed-106.json.gz)
- [DATA/raw/run-0085-w100_d2-seed-106.json.gz](DATA/raw/run-0085-w100_d2-seed-106.json.gz)
- [DATA/raw/run-0086-w100_d4-seed-106.json.gz](DATA/raw/run-0086-w100_d4-seed-106.json.gz)
- [DATA/raw/run-0087-w125_d1-seed-106.json.gz](DATA/raw/run-0087-w125_d1-seed-106.json.gz)
- [DATA/raw/run-0088-w125_d2-seed-106.json.gz](DATA/raw/run-0088-w125_d2-seed-106.json.gz)
- [DATA/raw/run-0089-w125_d4-seed-106.json.gz](DATA/raw/run-0089-w125_d4-seed-106.json.gz)
- [DATA/raw/run-0090-w0_d1-seed-107.json.gz](DATA/raw/run-0090-w0_d1-seed-107.json.gz)
- [DATA/raw/run-0091-w0_d2-seed-107.json.gz](DATA/raw/run-0091-w0_d2-seed-107.json.gz)
- [DATA/raw/run-0092-w0_d4-seed-107.json.gz](DATA/raw/run-0092-w0_d4-seed-107.json.gz)
- [DATA/raw/run-0093-w50_d1-seed-107.json.gz](DATA/raw/run-0093-w50_d1-seed-107.json.gz)
- [DATA/raw/run-0094-w50_d2-seed-107.json.gz](DATA/raw/run-0094-w50_d2-seed-107.json.gz)
- [DATA/raw/run-0095-w50_d4-seed-107.json.gz](DATA/raw/run-0095-w50_d4-seed-107.json.gz)
- [DATA/raw/run-0096-w75_d1-seed-107.json.gz](DATA/raw/run-0096-w75_d1-seed-107.json.gz)
- [DATA/raw/run-0097-w75_d2-seed-107.json.gz](DATA/raw/run-0097-w75_d2-seed-107.json.gz)
- [DATA/raw/run-0098-w75_d4-seed-107.json.gz](DATA/raw/run-0098-w75_d4-seed-107.json.gz)
- [DATA/raw/run-0099-w100_d1-seed-107.json.gz](DATA/raw/run-0099-w100_d1-seed-107.json.gz)
- [DATA/raw/run-0100-w100_d2-seed-107.json.gz](DATA/raw/run-0100-w100_d2-seed-107.json.gz)
- [DATA/raw/run-0101-w100_d4-seed-107.json.gz](DATA/raw/run-0101-w100_d4-seed-107.json.gz)
- [DATA/raw/run-0102-w125_d1-seed-107.json.gz](DATA/raw/run-0102-w125_d1-seed-107.json.gz)
- [DATA/raw/run-0103-w125_d2-seed-107.json.gz](DATA/raw/run-0103-w125_d2-seed-107.json.gz)
- [DATA/raw/run-0104-w125_d4-seed-107.json.gz](DATA/raw/run-0104-w125_d4-seed-107.json.gz)
- [DATA/raw/run-0105-w0_d1-seed-108.json.gz](DATA/raw/run-0105-w0_d1-seed-108.json.gz)
- [DATA/raw/run-0106-w0_d2-seed-108.json.gz](DATA/raw/run-0106-w0_d2-seed-108.json.gz)
- [DATA/raw/run-0107-w0_d4-seed-108.json.gz](DATA/raw/run-0107-w0_d4-seed-108.json.gz)
- [DATA/raw/run-0108-w50_d1-seed-108.json.gz](DATA/raw/run-0108-w50_d1-seed-108.json.gz)
- [DATA/raw/run-0109-w50_d2-seed-108.json.gz](DATA/raw/run-0109-w50_d2-seed-108.json.gz)
- [DATA/raw/run-0110-w50_d4-seed-108.json.gz](DATA/raw/run-0110-w50_d4-seed-108.json.gz)
- [DATA/raw/run-0111-w75_d1-seed-108.json.gz](DATA/raw/run-0111-w75_d1-seed-108.json.gz)
- [DATA/raw/run-0112-w75_d2-seed-108.json.gz](DATA/raw/run-0112-w75_d2-seed-108.json.gz)
- [DATA/raw/run-0113-w75_d4-seed-108.json.gz](DATA/raw/run-0113-w75_d4-seed-108.json.gz)
- [DATA/raw/run-0114-w100_d1-seed-108.json.gz](DATA/raw/run-0114-w100_d1-seed-108.json.gz)
- [DATA/raw/run-0115-w100_d2-seed-108.json.gz](DATA/raw/run-0115-w100_d2-seed-108.json.gz)
- [DATA/raw/run-0116-w100_d4-seed-108.json.gz](DATA/raw/run-0116-w100_d4-seed-108.json.gz)
- [DATA/raw/run-0117-w125_d1-seed-108.json.gz](DATA/raw/run-0117-w125_d1-seed-108.json.gz)
- [DATA/raw/run-0118-w125_d2-seed-108.json.gz](DATA/raw/run-0118-w125_d2-seed-108.json.gz)
- [DATA/raw/run-0119-w125_d4-seed-108.json.gz](DATA/raw/run-0119-w125_d4-seed-108.json.gz)
- [DATA/raw/run-0120-w0_d1-seed-109.json.gz](DATA/raw/run-0120-w0_d1-seed-109.json.gz)
- [DATA/raw/run-0121-w0_d2-seed-109.json.gz](DATA/raw/run-0121-w0_d2-seed-109.json.gz)
- [DATA/raw/run-0122-w0_d4-seed-109.json.gz](DATA/raw/run-0122-w0_d4-seed-109.json.gz)
- [DATA/raw/run-0123-w50_d1-seed-109.json.gz](DATA/raw/run-0123-w50_d1-seed-109.json.gz)
- [DATA/raw/run-0124-w50_d2-seed-109.json.gz](DATA/raw/run-0124-w50_d2-seed-109.json.gz)
- [DATA/raw/run-0125-w50_d4-seed-109.json.gz](DATA/raw/run-0125-w50_d4-seed-109.json.gz)
- [DATA/raw/run-0126-w75_d1-seed-109.json.gz](DATA/raw/run-0126-w75_d1-seed-109.json.gz)
- [DATA/raw/run-0127-w75_d2-seed-109.json.gz](DATA/raw/run-0127-w75_d2-seed-109.json.gz)
- [DATA/raw/run-0128-w75_d4-seed-109.json.gz](DATA/raw/run-0128-w75_d4-seed-109.json.gz)
- [DATA/raw/run-0129-w100_d1-seed-109.json.gz](DATA/raw/run-0129-w100_d1-seed-109.json.gz)
- [DATA/raw/run-0130-w100_d2-seed-109.json.gz](DATA/raw/run-0130-w100_d2-seed-109.json.gz)
- [DATA/raw/run-0131-w100_d4-seed-109.json.gz](DATA/raw/run-0131-w100_d4-seed-109.json.gz)
- [DATA/raw/run-0132-w125_d1-seed-109.json.gz](DATA/raw/run-0132-w125_d1-seed-109.json.gz)
- [DATA/raw/run-0133-w125_d2-seed-109.json.gz](DATA/raw/run-0133-w125_d2-seed-109.json.gz)
- [DATA/raw/run-0134-w125_d4-seed-109.json.gz](DATA/raw/run-0134-w125_d4-seed-109.json.gz)
- [DATA/raw/run-0135-w0_d1-seed-110.json.gz](DATA/raw/run-0135-w0_d1-seed-110.json.gz)
- [DATA/raw/run-0136-w0_d2-seed-110.json.gz](DATA/raw/run-0136-w0_d2-seed-110.json.gz)
- [DATA/raw/run-0137-w0_d4-seed-110.json.gz](DATA/raw/run-0137-w0_d4-seed-110.json.gz)
- [DATA/raw/run-0138-w50_d1-seed-110.json.gz](DATA/raw/run-0138-w50_d1-seed-110.json.gz)
- [DATA/raw/run-0139-w50_d2-seed-110.json.gz](DATA/raw/run-0139-w50_d2-seed-110.json.gz)
- [DATA/raw/run-0140-w50_d4-seed-110.json.gz](DATA/raw/run-0140-w50_d4-seed-110.json.gz)
- [DATA/raw/run-0141-w75_d1-seed-110.json.gz](DATA/raw/run-0141-w75_d1-seed-110.json.gz)
- [DATA/raw/run-0142-w75_d2-seed-110.json.gz](DATA/raw/run-0142-w75_d2-seed-110.json.gz)
- [DATA/raw/run-0143-w75_d4-seed-110.json.gz](DATA/raw/run-0143-w75_d4-seed-110.json.gz)
- [DATA/raw/run-0144-w100_d1-seed-110.json.gz](DATA/raw/run-0144-w100_d1-seed-110.json.gz)
- [DATA/raw/run-0145-w100_d2-seed-110.json.gz](DATA/raw/run-0145-w100_d2-seed-110.json.gz)
- [DATA/raw/run-0146-w100_d4-seed-110.json.gz](DATA/raw/run-0146-w100_d4-seed-110.json.gz)
- [DATA/raw/run-0147-w125_d1-seed-110.json.gz](DATA/raw/run-0147-w125_d1-seed-110.json.gz)
- [DATA/raw/run-0148-w125_d2-seed-110.json.gz](DATA/raw/run-0148-w125_d2-seed-110.json.gz)
- [DATA/raw/run-0149-w125_d4-seed-110.json.gz](DATA/raw/run-0149-w125_d4-seed-110.json.gz)
- [DATA/raw/run-0150-w0_d1-seed-111.json.gz](DATA/raw/run-0150-w0_d1-seed-111.json.gz)
- [DATA/raw/run-0151-w0_d2-seed-111.json.gz](DATA/raw/run-0151-w0_d2-seed-111.json.gz)
- [DATA/raw/run-0152-w0_d4-seed-111.json.gz](DATA/raw/run-0152-w0_d4-seed-111.json.gz)
- [DATA/raw/run-0153-w50_d1-seed-111.json.gz](DATA/raw/run-0153-w50_d1-seed-111.json.gz)
- [DATA/raw/run-0154-w50_d2-seed-111.json.gz](DATA/raw/run-0154-w50_d2-seed-111.json.gz)
- [DATA/raw/run-0155-w50_d4-seed-111.json.gz](DATA/raw/run-0155-w50_d4-seed-111.json.gz)
- [DATA/raw/run-0156-w75_d1-seed-111.json.gz](DATA/raw/run-0156-w75_d1-seed-111.json.gz)
- [DATA/raw/run-0157-w75_d2-seed-111.json.gz](DATA/raw/run-0157-w75_d2-seed-111.json.gz)
- [DATA/raw/run-0158-w75_d4-seed-111.json.gz](DATA/raw/run-0158-w75_d4-seed-111.json.gz)
- [DATA/raw/run-0159-w100_d1-seed-111.json.gz](DATA/raw/run-0159-w100_d1-seed-111.json.gz)
- [DATA/raw/run-0160-w100_d2-seed-111.json.gz](DATA/raw/run-0160-w100_d2-seed-111.json.gz)
- [DATA/raw/run-0161-w100_d4-seed-111.json.gz](DATA/raw/run-0161-w100_d4-seed-111.json.gz)
- [DATA/raw/run-0162-w125_d1-seed-111.json.gz](DATA/raw/run-0162-w125_d1-seed-111.json.gz)
- [DATA/raw/run-0163-w125_d2-seed-111.json.gz](DATA/raw/run-0163-w125_d2-seed-111.json.gz)
- [DATA/raw/run-0164-w125_d4-seed-111.json.gz](DATA/raw/run-0164-w125_d4-seed-111.json.gz)
- [DATA/raw/run-0165-w0_d1-seed-112.json.gz](DATA/raw/run-0165-w0_d1-seed-112.json.gz)
- [DATA/raw/run-0166-w0_d2-seed-112.json.gz](DATA/raw/run-0166-w0_d2-seed-112.json.gz)
- [DATA/raw/run-0167-w0_d4-seed-112.json.gz](DATA/raw/run-0167-w0_d4-seed-112.json.gz)
- [DATA/raw/run-0168-w50_d1-seed-112.json.gz](DATA/raw/run-0168-w50_d1-seed-112.json.gz)
- [DATA/raw/run-0169-w50_d2-seed-112.json.gz](DATA/raw/run-0169-w50_d2-seed-112.json.gz)
- [DATA/raw/run-0170-w50_d4-seed-112.json.gz](DATA/raw/run-0170-w50_d4-seed-112.json.gz)
- [DATA/raw/run-0171-w75_d1-seed-112.json.gz](DATA/raw/run-0171-w75_d1-seed-112.json.gz)
- [DATA/raw/run-0172-w75_d2-seed-112.json.gz](DATA/raw/run-0172-w75_d2-seed-112.json.gz)
- [DATA/raw/run-0173-w75_d4-seed-112.json.gz](DATA/raw/run-0173-w75_d4-seed-112.json.gz)
- [DATA/raw/run-0174-w100_d1-seed-112.json.gz](DATA/raw/run-0174-w100_d1-seed-112.json.gz)
- [DATA/raw/run-0175-w100_d2-seed-112.json.gz](DATA/raw/run-0175-w100_d2-seed-112.json.gz)
- [DATA/raw/run-0176-w100_d4-seed-112.json.gz](DATA/raw/run-0176-w100_d4-seed-112.json.gz)
- [DATA/raw/run-0177-w125_d1-seed-112.json.gz](DATA/raw/run-0177-w125_d1-seed-112.json.gz)
- [DATA/raw/run-0178-w125_d2-seed-112.json.gz](DATA/raw/run-0178-w125_d2-seed-112.json.gz)
- [DATA/raw/run-0179-w125_d4-seed-112.json.gz](DATA/raw/run-0179-w125_d4-seed-112.json.gz)
- [DATA/raw/run-0180-w0_d1-seed-113.json.gz](DATA/raw/run-0180-w0_d1-seed-113.json.gz)
- [DATA/raw/run-0181-w0_d2-seed-113.json.gz](DATA/raw/run-0181-w0_d2-seed-113.json.gz)
- [DATA/raw/run-0182-w0_d4-seed-113.json.gz](DATA/raw/run-0182-w0_d4-seed-113.json.gz)
- [DATA/raw/run-0183-w50_d1-seed-113.json.gz](DATA/raw/run-0183-w50_d1-seed-113.json.gz)
- [DATA/raw/run-0184-w50_d2-seed-113.json.gz](DATA/raw/run-0184-w50_d2-seed-113.json.gz)
- [DATA/raw/run-0185-w50_d4-seed-113.json.gz](DATA/raw/run-0185-w50_d4-seed-113.json.gz)
- [DATA/raw/run-0186-w75_d1-seed-113.json.gz](DATA/raw/run-0186-w75_d1-seed-113.json.gz)
- [DATA/raw/run-0187-w75_d2-seed-113.json.gz](DATA/raw/run-0187-w75_d2-seed-113.json.gz)
- [DATA/raw/run-0188-w75_d4-seed-113.json.gz](DATA/raw/run-0188-w75_d4-seed-113.json.gz)
- [DATA/raw/run-0189-w100_d1-seed-113.json.gz](DATA/raw/run-0189-w100_d1-seed-113.json.gz)
- [DATA/raw/run-0190-w100_d2-seed-113.json.gz](DATA/raw/run-0190-w100_d2-seed-113.json.gz)
- [DATA/raw/run-0191-w100_d4-seed-113.json.gz](DATA/raw/run-0191-w100_d4-seed-113.json.gz)
- [DATA/raw/run-0192-w125_d1-seed-113.json.gz](DATA/raw/run-0192-w125_d1-seed-113.json.gz)
- [DATA/raw/run-0193-w125_d2-seed-113.json.gz](DATA/raw/run-0193-w125_d2-seed-113.json.gz)
- [DATA/raw/run-0194-w125_d4-seed-113.json.gz](DATA/raw/run-0194-w125_d4-seed-113.json.gz)
- [DATA/raw/run-0195-w0_d1-seed-114.json.gz](DATA/raw/run-0195-w0_d1-seed-114.json.gz)
- [DATA/raw/run-0196-w0_d2-seed-114.json.gz](DATA/raw/run-0196-w0_d2-seed-114.json.gz)
- [DATA/raw/run-0197-w0_d4-seed-114.json.gz](DATA/raw/run-0197-w0_d4-seed-114.json.gz)
- [DATA/raw/run-0198-w50_d1-seed-114.json.gz](DATA/raw/run-0198-w50_d1-seed-114.json.gz)
- [DATA/raw/run-0199-w50_d2-seed-114.json.gz](DATA/raw/run-0199-w50_d2-seed-114.json.gz)
- [DATA/raw/run-0200-w50_d4-seed-114.json.gz](DATA/raw/run-0200-w50_d4-seed-114.json.gz)
- [DATA/raw/run-0201-w75_d1-seed-114.json.gz](DATA/raw/run-0201-w75_d1-seed-114.json.gz)
- [DATA/raw/run-0202-w75_d2-seed-114.json.gz](DATA/raw/run-0202-w75_d2-seed-114.json.gz)
- [DATA/raw/run-0203-w75_d4-seed-114.json.gz](DATA/raw/run-0203-w75_d4-seed-114.json.gz)
- [DATA/raw/run-0204-w100_d1-seed-114.json.gz](DATA/raw/run-0204-w100_d1-seed-114.json.gz)
- [DATA/raw/run-0205-w100_d2-seed-114.json.gz](DATA/raw/run-0205-w100_d2-seed-114.json.gz)
- [DATA/raw/run-0206-w100_d4-seed-114.json.gz](DATA/raw/run-0206-w100_d4-seed-114.json.gz)
- [DATA/raw/run-0207-w125_d1-seed-114.json.gz](DATA/raw/run-0207-w125_d1-seed-114.json.gz)
- [DATA/raw/run-0208-w125_d2-seed-114.json.gz](DATA/raw/run-0208-w125_d2-seed-114.json.gz)
- [DATA/raw/run-0209-w125_d4-seed-114.json.gz](DATA/raw/run-0209-w125_d4-seed-114.json.gz)
- [DATA/raw/run-0210-w0_d1-seed-115.json.gz](DATA/raw/run-0210-w0_d1-seed-115.json.gz)
- [DATA/raw/run-0211-w0_d2-seed-115.json.gz](DATA/raw/run-0211-w0_d2-seed-115.json.gz)
- [DATA/raw/run-0212-w0_d4-seed-115.json.gz](DATA/raw/run-0212-w0_d4-seed-115.json.gz)
- [DATA/raw/run-0213-w50_d1-seed-115.json.gz](DATA/raw/run-0213-w50_d1-seed-115.json.gz)
- [DATA/raw/run-0214-w50_d2-seed-115.json.gz](DATA/raw/run-0214-w50_d2-seed-115.json.gz)
- [DATA/raw/run-0215-w50_d4-seed-115.json.gz](DATA/raw/run-0215-w50_d4-seed-115.json.gz)
- [DATA/raw/run-0216-w75_d1-seed-115.json.gz](DATA/raw/run-0216-w75_d1-seed-115.json.gz)
- [DATA/raw/run-0217-w75_d2-seed-115.json.gz](DATA/raw/run-0217-w75_d2-seed-115.json.gz)
- [DATA/raw/run-0218-w75_d4-seed-115.json.gz](DATA/raw/run-0218-w75_d4-seed-115.json.gz)
- [DATA/raw/run-0219-w100_d1-seed-115.json.gz](DATA/raw/run-0219-w100_d1-seed-115.json.gz)
- [DATA/raw/run-0220-w100_d2-seed-115.json.gz](DATA/raw/run-0220-w100_d2-seed-115.json.gz)
- [DATA/raw/run-0221-w100_d4-seed-115.json.gz](DATA/raw/run-0221-w100_d4-seed-115.json.gz)
- [DATA/raw/run-0222-w125_d1-seed-115.json.gz](DATA/raw/run-0222-w125_d1-seed-115.json.gz)
- [DATA/raw/run-0223-w125_d2-seed-115.json.gz](DATA/raw/run-0223-w125_d2-seed-115.json.gz)
- [DATA/raw/run-0224-w125_d4-seed-115.json.gz](DATA/raw/run-0224-w125_d4-seed-115.json.gz)
- [DATA/raw/run-0225-w0_d1-seed-116.json.gz](DATA/raw/run-0225-w0_d1-seed-116.json.gz)
- [DATA/raw/run-0226-w0_d2-seed-116.json.gz](DATA/raw/run-0226-w0_d2-seed-116.json.gz)
- [DATA/raw/run-0227-w0_d4-seed-116.json.gz](DATA/raw/run-0227-w0_d4-seed-116.json.gz)
- [DATA/raw/run-0228-w50_d1-seed-116.json.gz](DATA/raw/run-0228-w50_d1-seed-116.json.gz)
- [DATA/raw/run-0229-w50_d2-seed-116.json.gz](DATA/raw/run-0229-w50_d2-seed-116.json.gz)
- [DATA/raw/run-0230-w50_d4-seed-116.json.gz](DATA/raw/run-0230-w50_d4-seed-116.json.gz)
- [DATA/raw/run-0231-w75_d1-seed-116.json.gz](DATA/raw/run-0231-w75_d1-seed-116.json.gz)
- [DATA/raw/run-0232-w75_d2-seed-116.json.gz](DATA/raw/run-0232-w75_d2-seed-116.json.gz)
- [DATA/raw/run-0233-w75_d4-seed-116.json.gz](DATA/raw/run-0233-w75_d4-seed-116.json.gz)
- [DATA/raw/run-0234-w100_d1-seed-116.json.gz](DATA/raw/run-0234-w100_d1-seed-116.json.gz)
- [DATA/raw/run-0235-w100_d2-seed-116.json.gz](DATA/raw/run-0235-w100_d2-seed-116.json.gz)
- [DATA/raw/run-0236-w100_d4-seed-116.json.gz](DATA/raw/run-0236-w100_d4-seed-116.json.gz)
- [DATA/raw/run-0237-w125_d1-seed-116.json.gz](DATA/raw/run-0237-w125_d1-seed-116.json.gz)
- [DATA/raw/run-0238-w125_d2-seed-116.json.gz](DATA/raw/run-0238-w125_d2-seed-116.json.gz)
- [DATA/raw/run-0239-w125_d4-seed-116.json.gz](DATA/raw/run-0239-w125_d4-seed-116.json.gz)
- [DATA/raw/run-0240-w0_d1-seed-117.json.gz](DATA/raw/run-0240-w0_d1-seed-117.json.gz)
- [DATA/raw/run-0241-w0_d2-seed-117.json.gz](DATA/raw/run-0241-w0_d2-seed-117.json.gz)
- [DATA/raw/run-0242-w0_d4-seed-117.json.gz](DATA/raw/run-0242-w0_d4-seed-117.json.gz)
- [DATA/raw/run-0243-w50_d1-seed-117.json.gz](DATA/raw/run-0243-w50_d1-seed-117.json.gz)
- [DATA/raw/run-0244-w50_d2-seed-117.json.gz](DATA/raw/run-0244-w50_d2-seed-117.json.gz)
- [DATA/raw/run-0245-w50_d4-seed-117.json.gz](DATA/raw/run-0245-w50_d4-seed-117.json.gz)
- [DATA/raw/run-0246-w75_d1-seed-117.json.gz](DATA/raw/run-0246-w75_d1-seed-117.json.gz)
- [DATA/raw/run-0247-w75_d2-seed-117.json.gz](DATA/raw/run-0247-w75_d2-seed-117.json.gz)
- [DATA/raw/run-0248-w75_d4-seed-117.json.gz](DATA/raw/run-0248-w75_d4-seed-117.json.gz)
- [DATA/raw/run-0249-w100_d1-seed-117.json.gz](DATA/raw/run-0249-w100_d1-seed-117.json.gz)
- [DATA/raw/run-0250-w100_d2-seed-117.json.gz](DATA/raw/run-0250-w100_d2-seed-117.json.gz)
- [DATA/raw/run-0251-w100_d4-seed-117.json.gz](DATA/raw/run-0251-w100_d4-seed-117.json.gz)
- [DATA/raw/run-0252-w125_d1-seed-117.json.gz](DATA/raw/run-0252-w125_d1-seed-117.json.gz)
- [DATA/raw/run-0253-w125_d2-seed-117.json.gz](DATA/raw/run-0253-w125_d2-seed-117.json.gz)
- [DATA/raw/run-0254-w125_d4-seed-117.json.gz](DATA/raw/run-0254-w125_d4-seed-117.json.gz)
- [DATA/raw/run-0255-w0_d1-seed-118.json.gz](DATA/raw/run-0255-w0_d1-seed-118.json.gz)
- [DATA/raw/run-0256-w0_d2-seed-118.json.gz](DATA/raw/run-0256-w0_d2-seed-118.json.gz)
- [DATA/raw/run-0257-w0_d4-seed-118.json.gz](DATA/raw/run-0257-w0_d4-seed-118.json.gz)
- [DATA/raw/run-0258-w50_d1-seed-118.json.gz](DATA/raw/run-0258-w50_d1-seed-118.json.gz)
- [DATA/raw/run-0259-w50_d2-seed-118.json.gz](DATA/raw/run-0259-w50_d2-seed-118.json.gz)
- [DATA/raw/run-0260-w50_d4-seed-118.json.gz](DATA/raw/run-0260-w50_d4-seed-118.json.gz)
- [DATA/raw/run-0261-w75_d1-seed-118.json.gz](DATA/raw/run-0261-w75_d1-seed-118.json.gz)
- [DATA/raw/run-0262-w75_d2-seed-118.json.gz](DATA/raw/run-0262-w75_d2-seed-118.json.gz)
- [DATA/raw/run-0263-w75_d4-seed-118.json.gz](DATA/raw/run-0263-w75_d4-seed-118.json.gz)
- [DATA/raw/run-0264-w100_d1-seed-118.json.gz](DATA/raw/run-0264-w100_d1-seed-118.json.gz)
- [DATA/raw/run-0265-w100_d2-seed-118.json.gz](DATA/raw/run-0265-w100_d2-seed-118.json.gz)
- [DATA/raw/run-0266-w100_d4-seed-118.json.gz](DATA/raw/run-0266-w100_d4-seed-118.json.gz)
- [DATA/raw/run-0267-w125_d1-seed-118.json.gz](DATA/raw/run-0267-w125_d1-seed-118.json.gz)
- [DATA/raw/run-0268-w125_d2-seed-118.json.gz](DATA/raw/run-0268-w125_d2-seed-118.json.gz)
- [DATA/raw/run-0269-w125_d4-seed-118.json.gz](DATA/raw/run-0269-w125_d4-seed-118.json.gz)
- [DATA/raw/run-0270-w0_d1-seed-119.json.gz](DATA/raw/run-0270-w0_d1-seed-119.json.gz)
- [DATA/raw/run-0271-w0_d2-seed-119.json.gz](DATA/raw/run-0271-w0_d2-seed-119.json.gz)
- [DATA/raw/run-0272-w0_d4-seed-119.json.gz](DATA/raw/run-0272-w0_d4-seed-119.json.gz)
- [DATA/raw/run-0273-w50_d1-seed-119.json.gz](DATA/raw/run-0273-w50_d1-seed-119.json.gz)
- [DATA/raw/run-0274-w50_d2-seed-119.json.gz](DATA/raw/run-0274-w50_d2-seed-119.json.gz)
- [DATA/raw/run-0275-w50_d4-seed-119.json.gz](DATA/raw/run-0275-w50_d4-seed-119.json.gz)
- [DATA/raw/run-0276-w75_d1-seed-119.json.gz](DATA/raw/run-0276-w75_d1-seed-119.json.gz)
- [DATA/raw/run-0277-w75_d2-seed-119.json.gz](DATA/raw/run-0277-w75_d2-seed-119.json.gz)
- [DATA/raw/run-0278-w75_d4-seed-119.json.gz](DATA/raw/run-0278-w75_d4-seed-119.json.gz)
- [DATA/raw/run-0279-w100_d1-seed-119.json.gz](DATA/raw/run-0279-w100_d1-seed-119.json.gz)
- [DATA/raw/run-0280-w100_d2-seed-119.json.gz](DATA/raw/run-0280-w100_d2-seed-119.json.gz)
- [DATA/raw/run-0281-w100_d4-seed-119.json.gz](DATA/raw/run-0281-w100_d4-seed-119.json.gz)
- [DATA/raw/run-0282-w125_d1-seed-119.json.gz](DATA/raw/run-0282-w125_d1-seed-119.json.gz)
- [DATA/raw/run-0283-w125_d2-seed-119.json.gz](DATA/raw/run-0283-w125_d2-seed-119.json.gz)
- [DATA/raw/run-0284-w125_d4-seed-119.json.gz](DATA/raw/run-0284-w125_d4-seed-119.json.gz)
- [DATA/raw/run-0285-w0_d1-seed-120.json.gz](DATA/raw/run-0285-w0_d1-seed-120.json.gz)
- [DATA/raw/run-0286-w0_d2-seed-120.json.gz](DATA/raw/run-0286-w0_d2-seed-120.json.gz)
- [DATA/raw/run-0287-w0_d4-seed-120.json.gz](DATA/raw/run-0287-w0_d4-seed-120.json.gz)
- [DATA/raw/run-0288-w50_d1-seed-120.json.gz](DATA/raw/run-0288-w50_d1-seed-120.json.gz)
- [DATA/raw/run-0289-w50_d2-seed-120.json.gz](DATA/raw/run-0289-w50_d2-seed-120.json.gz)
- [DATA/raw/run-0290-w50_d4-seed-120.json.gz](DATA/raw/run-0290-w50_d4-seed-120.json.gz)
- [DATA/raw/run-0291-w75_d1-seed-120.json.gz](DATA/raw/run-0291-w75_d1-seed-120.json.gz)
- [DATA/raw/run-0292-w75_d2-seed-120.json.gz](DATA/raw/run-0292-w75_d2-seed-120.json.gz)
- [DATA/raw/run-0293-w75_d4-seed-120.json.gz](DATA/raw/run-0293-w75_d4-seed-120.json.gz)
- [DATA/raw/run-0294-w100_d1-seed-120.json.gz](DATA/raw/run-0294-w100_d1-seed-120.json.gz)
- [DATA/raw/run-0295-w100_d2-seed-120.json.gz](DATA/raw/run-0295-w100_d2-seed-120.json.gz)
- [DATA/raw/run-0296-w100_d4-seed-120.json.gz](DATA/raw/run-0296-w100_d4-seed-120.json.gz)
- [DATA/raw/run-0297-w125_d1-seed-120.json.gz](DATA/raw/run-0297-w125_d1-seed-120.json.gz)
- [DATA/raw/run-0298-w125_d2-seed-120.json.gz](DATA/raw/run-0298-w125_d2-seed-120.json.gz)
- [DATA/raw/run-0299-w125_d4-seed-120.json.gz](DATA/raw/run-0299-w125_d4-seed-120.json.gz)
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
