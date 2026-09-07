# EXP-REC-0001-R1: Wissenschaftliche Zusammenfassung

Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.

## 1. Identifikation und Status

- Experimentstatus: `completed`
- Forschungsfrage: `RQ-REC-001`
- Hypothese: `H-REC-001-A`
- Protokoll: `recurrence_map_v1`
- Durchlaeufe: `300`
- Seeds: `[42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]`
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

- Titel: Recurrence map v1 full registered grid
- Bedingungen: Recurrent weight x delay grid with zero-weight control; frozen seeds 42-61.
- Notizen: Full PREREG-REC-001 weight x delay x seed grid.
- Konfiguration: `F:\Brain-5D\configs\learning_experiment.yaml`
- Config SHA-256: `6f6cd457caf6216c286fee47ef03b529a0b496ed2dd53ee96b85d3b51e7b3a1c`
- Git Commit: `65d238fd739bf8a0cbf15f3a1c5ffbfa1159fbb5`
- Git dirty: `True`
- Runtime: `0.5480186999775469` s

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
| w0_d1 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 3 | 2 | 3 | 0 | 1 |
| w0_d2 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 3 | 2 | 3 | 0 | 1 |
| w0_d4 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 3 | 2 | 3 | 0 | 1 |
| w100_d1 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 33 | 33 | 3 | 10 | 61 |
| w100_d2 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 102 | 102 | 3 | 33 | 251 |
| w100_d4 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 87 | 87 | 3 | 28 | 250 |
| w125_d1 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 43 | 43 | 3 | 14 | 83 |
| w125_d2 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 105 | 104 | 3 | 34 | 254 |
| w125_d4 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 91 | 90 | 3 | 30 | 249 |
| w50_d1 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 6 | 6 | 3 | 1 | 6 |
| w50_d2 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 6 | 6 | 3 | 1 | 7 |
| w50_d4 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 6 | 6 | 3 | 1 | 9 |
| w75_d1 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 15 | 15 | 3 | 4 | 24 |
| w75_d2 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 15 | 15 | 3 | 4 | 28 |
| w75_d4 | 20 | 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61 | 256 | 21 | 21 | 3 | 6 | 56 |

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
| 42 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 42 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 42 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 42 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 42 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 42 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 42 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 42 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 42 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 42 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 42 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 42 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 42 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 43 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 43 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 43 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 43 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 43 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 43 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 43 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 43 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 43 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 43 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 43 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 43 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 43 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 44 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 44 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 44 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 44 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 44 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 44 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 44 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 44 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 44 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 44 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 44 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 44 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 44 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 45 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 45 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 45 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 45 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 45 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 45 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 45 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 45 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 45 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 45 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 45 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 45 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 45 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 45 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 45 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 46 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 46 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 46 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 46 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 46 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 46 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 46 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 46 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 46 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 46 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 46 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 46 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 46 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 46 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 46 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 47 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 47 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 47 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 47 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 47 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 47 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 47 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 47 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 47 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 47 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 47 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 47 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 47 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 47 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 47 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 48 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 48 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 48 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 48 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 48 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 48 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 48 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 48 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 48 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 48 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 48 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 48 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 48 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 48 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 48 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 49 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 49 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 49 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 49 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 49 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 49 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 49 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 49 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 49 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 49 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 49 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 49 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 49 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 49 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 49 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 50 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 50 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 50 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 50 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 50 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 50 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 50 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 50 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 50 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 50 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 50 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 50 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 50 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 50 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 50 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 51 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 51 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 51 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 51 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 51 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 51 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 51 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 51 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 51 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 51 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 51 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 51 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 51 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 51 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 51 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 52 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 52 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 52 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 52 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 52 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 52 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 52 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 52 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 52 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 52 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 52 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 52 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 52 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 52 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 52 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 53 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 53 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 53 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 53 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 53 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 53 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 53 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 53 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 53 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 53 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 53 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 53 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 53 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 53 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 53 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 54 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 54 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 54 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 54 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 54 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 54 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 54 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 54 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 54 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 54 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 54 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 54 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 54 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 54 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 54 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 55 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 55 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 55 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 55 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 55 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 55 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 55 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 55 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 55 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 55 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 55 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 55 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 55 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 55 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 55 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 56 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 56 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 56 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 56 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 56 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 56 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 56 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 56 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 56 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 56 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 56 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 56 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 56 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 56 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 56 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 57 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 57 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 57 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 57 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 57 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 57 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 57 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 57 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 57 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 57 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 57 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 57 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 57 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 57 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 57 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 58 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 58 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 58 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 58 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 58 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 58 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 58 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 58 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 58 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 58 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 58 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 58 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 58 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 58 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 58 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 59 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 59 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 59 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 59 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 59 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 59 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 59 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 59 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 59 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 59 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 59 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 59 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 59 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 59 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 59 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 60 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 60 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 60 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 60 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 60 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 60 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 60 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 60 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 60 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 60 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 60 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 60 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 60 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 60 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 60 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |
| 61 | w0_d1 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 61 | w0_d2 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 61 | w0_d4 | 256 | 3 | 2 | 3 | 0 | 1 | — |
| 61 | w50_d1 | 256 | 6 | 6 | 3 | 1 | 6 | — |
| 61 | w50_d2 | 256 | 6 | 6 | 3 | 1 | 7 | — |
| 61 | w50_d4 | 256 | 6 | 6 | 3 | 1 | 9 | — |
| 61 | w75_d1 | 256 | 15 | 15 | 3 | 4 | 24 | — |
| 61 | w75_d2 | 256 | 15 | 15 | 3 | 4 | 28 | — |
| 61 | w75_d4 | 256 | 21 | 21 | 3 | 6 | 56 | — |
| 61 | w100_d1 | 256 | 33 | 33 | 3 | 10 | 61 | — |
| 61 | w100_d2 | 256 | 102 | 102 | 3 | 33 | 251 | — |
| 61 | w100_d4 | 256 | 87 | 87 | 3 | 28 | 250 | — |
| 61 | w125_d1 | 256 | 43 | 43 | 3 | 14 | 83 | — |
| 61 | w125_d2 | 256 | 105 | 104 | 3 | 34 | 254 | — |
| 61 | w125_d4 | 256 | 91 | 90 | 3 | 30 | 249 | — |

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
- [DATA/raw/run-0000-w0_d1-seed-42.json.gz](DATA/raw/run-0000-w0_d1-seed-42.json.gz)
- [DATA/raw/run-0001-w0_d2-seed-42.json.gz](DATA/raw/run-0001-w0_d2-seed-42.json.gz)
- [DATA/raw/run-0002-w0_d4-seed-42.json.gz](DATA/raw/run-0002-w0_d4-seed-42.json.gz)
- [DATA/raw/run-0003-w50_d1-seed-42.json.gz](DATA/raw/run-0003-w50_d1-seed-42.json.gz)
- [DATA/raw/run-0004-w50_d2-seed-42.json.gz](DATA/raw/run-0004-w50_d2-seed-42.json.gz)
- [DATA/raw/run-0005-w50_d4-seed-42.json.gz](DATA/raw/run-0005-w50_d4-seed-42.json.gz)
- [DATA/raw/run-0006-w75_d1-seed-42.json.gz](DATA/raw/run-0006-w75_d1-seed-42.json.gz)
- [DATA/raw/run-0007-w75_d2-seed-42.json.gz](DATA/raw/run-0007-w75_d2-seed-42.json.gz)
- [DATA/raw/run-0008-w75_d4-seed-42.json.gz](DATA/raw/run-0008-w75_d4-seed-42.json.gz)
- [DATA/raw/run-0009-w100_d1-seed-42.json.gz](DATA/raw/run-0009-w100_d1-seed-42.json.gz)
- [DATA/raw/run-0010-w100_d2-seed-42.json.gz](DATA/raw/run-0010-w100_d2-seed-42.json.gz)
- [DATA/raw/run-0011-w100_d4-seed-42.json.gz](DATA/raw/run-0011-w100_d4-seed-42.json.gz)
- [DATA/raw/run-0012-w125_d1-seed-42.json.gz](DATA/raw/run-0012-w125_d1-seed-42.json.gz)
- [DATA/raw/run-0013-w125_d2-seed-42.json.gz](DATA/raw/run-0013-w125_d2-seed-42.json.gz)
- [DATA/raw/run-0014-w125_d4-seed-42.json.gz](DATA/raw/run-0014-w125_d4-seed-42.json.gz)
- [DATA/raw/run-0015-w0_d1-seed-43.json.gz](DATA/raw/run-0015-w0_d1-seed-43.json.gz)
- [DATA/raw/run-0016-w0_d2-seed-43.json.gz](DATA/raw/run-0016-w0_d2-seed-43.json.gz)
- [DATA/raw/run-0017-w0_d4-seed-43.json.gz](DATA/raw/run-0017-w0_d4-seed-43.json.gz)
- [DATA/raw/run-0018-w50_d1-seed-43.json.gz](DATA/raw/run-0018-w50_d1-seed-43.json.gz)
- [DATA/raw/run-0019-w50_d2-seed-43.json.gz](DATA/raw/run-0019-w50_d2-seed-43.json.gz)
- [DATA/raw/run-0020-w50_d4-seed-43.json.gz](DATA/raw/run-0020-w50_d4-seed-43.json.gz)
- [DATA/raw/run-0021-w75_d1-seed-43.json.gz](DATA/raw/run-0021-w75_d1-seed-43.json.gz)
- [DATA/raw/run-0022-w75_d2-seed-43.json.gz](DATA/raw/run-0022-w75_d2-seed-43.json.gz)
- [DATA/raw/run-0023-w75_d4-seed-43.json.gz](DATA/raw/run-0023-w75_d4-seed-43.json.gz)
- [DATA/raw/run-0024-w100_d1-seed-43.json.gz](DATA/raw/run-0024-w100_d1-seed-43.json.gz)
- [DATA/raw/run-0025-w100_d2-seed-43.json.gz](DATA/raw/run-0025-w100_d2-seed-43.json.gz)
- [DATA/raw/run-0026-w100_d4-seed-43.json.gz](DATA/raw/run-0026-w100_d4-seed-43.json.gz)
- [DATA/raw/run-0027-w125_d1-seed-43.json.gz](DATA/raw/run-0027-w125_d1-seed-43.json.gz)
- [DATA/raw/run-0028-w125_d2-seed-43.json.gz](DATA/raw/run-0028-w125_d2-seed-43.json.gz)
- [DATA/raw/run-0029-w125_d4-seed-43.json.gz](DATA/raw/run-0029-w125_d4-seed-43.json.gz)
- [DATA/raw/run-0030-w0_d1-seed-44.json.gz](DATA/raw/run-0030-w0_d1-seed-44.json.gz)
- [DATA/raw/run-0031-w0_d2-seed-44.json.gz](DATA/raw/run-0031-w0_d2-seed-44.json.gz)
- [DATA/raw/run-0032-w0_d4-seed-44.json.gz](DATA/raw/run-0032-w0_d4-seed-44.json.gz)
- [DATA/raw/run-0033-w50_d1-seed-44.json.gz](DATA/raw/run-0033-w50_d1-seed-44.json.gz)
- [DATA/raw/run-0034-w50_d2-seed-44.json.gz](DATA/raw/run-0034-w50_d2-seed-44.json.gz)
- [DATA/raw/run-0035-w50_d4-seed-44.json.gz](DATA/raw/run-0035-w50_d4-seed-44.json.gz)
- [DATA/raw/run-0036-w75_d1-seed-44.json.gz](DATA/raw/run-0036-w75_d1-seed-44.json.gz)
- [DATA/raw/run-0037-w75_d2-seed-44.json.gz](DATA/raw/run-0037-w75_d2-seed-44.json.gz)
- [DATA/raw/run-0038-w75_d4-seed-44.json.gz](DATA/raw/run-0038-w75_d4-seed-44.json.gz)
- [DATA/raw/run-0039-w100_d1-seed-44.json.gz](DATA/raw/run-0039-w100_d1-seed-44.json.gz)
- [DATA/raw/run-0040-w100_d2-seed-44.json.gz](DATA/raw/run-0040-w100_d2-seed-44.json.gz)
- [DATA/raw/run-0041-w100_d4-seed-44.json.gz](DATA/raw/run-0041-w100_d4-seed-44.json.gz)
- [DATA/raw/run-0042-w125_d1-seed-44.json.gz](DATA/raw/run-0042-w125_d1-seed-44.json.gz)
- [DATA/raw/run-0043-w125_d2-seed-44.json.gz](DATA/raw/run-0043-w125_d2-seed-44.json.gz)
- [DATA/raw/run-0044-w125_d4-seed-44.json.gz](DATA/raw/run-0044-w125_d4-seed-44.json.gz)
- [DATA/raw/run-0045-w0_d1-seed-45.json.gz](DATA/raw/run-0045-w0_d1-seed-45.json.gz)
- [DATA/raw/run-0046-w0_d2-seed-45.json.gz](DATA/raw/run-0046-w0_d2-seed-45.json.gz)
- [DATA/raw/run-0047-w0_d4-seed-45.json.gz](DATA/raw/run-0047-w0_d4-seed-45.json.gz)
- [DATA/raw/run-0048-w50_d1-seed-45.json.gz](DATA/raw/run-0048-w50_d1-seed-45.json.gz)
- [DATA/raw/run-0049-w50_d2-seed-45.json.gz](DATA/raw/run-0049-w50_d2-seed-45.json.gz)
- [DATA/raw/run-0050-w50_d4-seed-45.json.gz](DATA/raw/run-0050-w50_d4-seed-45.json.gz)
- [DATA/raw/run-0051-w75_d1-seed-45.json.gz](DATA/raw/run-0051-w75_d1-seed-45.json.gz)
- [DATA/raw/run-0052-w75_d2-seed-45.json.gz](DATA/raw/run-0052-w75_d2-seed-45.json.gz)
- [DATA/raw/run-0053-w75_d4-seed-45.json.gz](DATA/raw/run-0053-w75_d4-seed-45.json.gz)
- [DATA/raw/run-0054-w100_d1-seed-45.json.gz](DATA/raw/run-0054-w100_d1-seed-45.json.gz)
- [DATA/raw/run-0055-w100_d2-seed-45.json.gz](DATA/raw/run-0055-w100_d2-seed-45.json.gz)
- [DATA/raw/run-0056-w100_d4-seed-45.json.gz](DATA/raw/run-0056-w100_d4-seed-45.json.gz)
- [DATA/raw/run-0057-w125_d1-seed-45.json.gz](DATA/raw/run-0057-w125_d1-seed-45.json.gz)
- [DATA/raw/run-0058-w125_d2-seed-45.json.gz](DATA/raw/run-0058-w125_d2-seed-45.json.gz)
- [DATA/raw/run-0059-w125_d4-seed-45.json.gz](DATA/raw/run-0059-w125_d4-seed-45.json.gz)
- [DATA/raw/run-0060-w0_d1-seed-46.json.gz](DATA/raw/run-0060-w0_d1-seed-46.json.gz)
- [DATA/raw/run-0061-w0_d2-seed-46.json.gz](DATA/raw/run-0061-w0_d2-seed-46.json.gz)
- [DATA/raw/run-0062-w0_d4-seed-46.json.gz](DATA/raw/run-0062-w0_d4-seed-46.json.gz)
- [DATA/raw/run-0063-w50_d1-seed-46.json.gz](DATA/raw/run-0063-w50_d1-seed-46.json.gz)
- [DATA/raw/run-0064-w50_d2-seed-46.json.gz](DATA/raw/run-0064-w50_d2-seed-46.json.gz)
- [DATA/raw/run-0065-w50_d4-seed-46.json.gz](DATA/raw/run-0065-w50_d4-seed-46.json.gz)
- [DATA/raw/run-0066-w75_d1-seed-46.json.gz](DATA/raw/run-0066-w75_d1-seed-46.json.gz)
- [DATA/raw/run-0067-w75_d2-seed-46.json.gz](DATA/raw/run-0067-w75_d2-seed-46.json.gz)
- [DATA/raw/run-0068-w75_d4-seed-46.json.gz](DATA/raw/run-0068-w75_d4-seed-46.json.gz)
- [DATA/raw/run-0069-w100_d1-seed-46.json.gz](DATA/raw/run-0069-w100_d1-seed-46.json.gz)
- [DATA/raw/run-0070-w100_d2-seed-46.json.gz](DATA/raw/run-0070-w100_d2-seed-46.json.gz)
- [DATA/raw/run-0071-w100_d4-seed-46.json.gz](DATA/raw/run-0071-w100_d4-seed-46.json.gz)
- [DATA/raw/run-0072-w125_d1-seed-46.json.gz](DATA/raw/run-0072-w125_d1-seed-46.json.gz)
- [DATA/raw/run-0073-w125_d2-seed-46.json.gz](DATA/raw/run-0073-w125_d2-seed-46.json.gz)
- [DATA/raw/run-0074-w125_d4-seed-46.json.gz](DATA/raw/run-0074-w125_d4-seed-46.json.gz)
- [DATA/raw/run-0075-w0_d1-seed-47.json.gz](DATA/raw/run-0075-w0_d1-seed-47.json.gz)
- [DATA/raw/run-0076-w0_d2-seed-47.json.gz](DATA/raw/run-0076-w0_d2-seed-47.json.gz)
- [DATA/raw/run-0077-w0_d4-seed-47.json.gz](DATA/raw/run-0077-w0_d4-seed-47.json.gz)
- [DATA/raw/run-0078-w50_d1-seed-47.json.gz](DATA/raw/run-0078-w50_d1-seed-47.json.gz)
- [DATA/raw/run-0079-w50_d2-seed-47.json.gz](DATA/raw/run-0079-w50_d2-seed-47.json.gz)
- [DATA/raw/run-0080-w50_d4-seed-47.json.gz](DATA/raw/run-0080-w50_d4-seed-47.json.gz)
- [DATA/raw/run-0081-w75_d1-seed-47.json.gz](DATA/raw/run-0081-w75_d1-seed-47.json.gz)
- [DATA/raw/run-0082-w75_d2-seed-47.json.gz](DATA/raw/run-0082-w75_d2-seed-47.json.gz)
- [DATA/raw/run-0083-w75_d4-seed-47.json.gz](DATA/raw/run-0083-w75_d4-seed-47.json.gz)
- [DATA/raw/run-0084-w100_d1-seed-47.json.gz](DATA/raw/run-0084-w100_d1-seed-47.json.gz)
- [DATA/raw/run-0085-w100_d2-seed-47.json.gz](DATA/raw/run-0085-w100_d2-seed-47.json.gz)
- [DATA/raw/run-0086-w100_d4-seed-47.json.gz](DATA/raw/run-0086-w100_d4-seed-47.json.gz)
- [DATA/raw/run-0087-w125_d1-seed-47.json.gz](DATA/raw/run-0087-w125_d1-seed-47.json.gz)
- [DATA/raw/run-0088-w125_d2-seed-47.json.gz](DATA/raw/run-0088-w125_d2-seed-47.json.gz)
- [DATA/raw/run-0089-w125_d4-seed-47.json.gz](DATA/raw/run-0089-w125_d4-seed-47.json.gz)
- [DATA/raw/run-0090-w0_d1-seed-48.json.gz](DATA/raw/run-0090-w0_d1-seed-48.json.gz)
- [DATA/raw/run-0091-w0_d2-seed-48.json.gz](DATA/raw/run-0091-w0_d2-seed-48.json.gz)
- [DATA/raw/run-0092-w0_d4-seed-48.json.gz](DATA/raw/run-0092-w0_d4-seed-48.json.gz)
- [DATA/raw/run-0093-w50_d1-seed-48.json.gz](DATA/raw/run-0093-w50_d1-seed-48.json.gz)
- [DATA/raw/run-0094-w50_d2-seed-48.json.gz](DATA/raw/run-0094-w50_d2-seed-48.json.gz)
- [DATA/raw/run-0095-w50_d4-seed-48.json.gz](DATA/raw/run-0095-w50_d4-seed-48.json.gz)
- [DATA/raw/run-0096-w75_d1-seed-48.json.gz](DATA/raw/run-0096-w75_d1-seed-48.json.gz)
- [DATA/raw/run-0097-w75_d2-seed-48.json.gz](DATA/raw/run-0097-w75_d2-seed-48.json.gz)
- [DATA/raw/run-0098-w75_d4-seed-48.json.gz](DATA/raw/run-0098-w75_d4-seed-48.json.gz)
- [DATA/raw/run-0099-w100_d1-seed-48.json.gz](DATA/raw/run-0099-w100_d1-seed-48.json.gz)
- [DATA/raw/run-0100-w100_d2-seed-48.json.gz](DATA/raw/run-0100-w100_d2-seed-48.json.gz)
- [DATA/raw/run-0101-w100_d4-seed-48.json.gz](DATA/raw/run-0101-w100_d4-seed-48.json.gz)
- [DATA/raw/run-0102-w125_d1-seed-48.json.gz](DATA/raw/run-0102-w125_d1-seed-48.json.gz)
- [DATA/raw/run-0103-w125_d2-seed-48.json.gz](DATA/raw/run-0103-w125_d2-seed-48.json.gz)
- [DATA/raw/run-0104-w125_d4-seed-48.json.gz](DATA/raw/run-0104-w125_d4-seed-48.json.gz)
- [DATA/raw/run-0105-w0_d1-seed-49.json.gz](DATA/raw/run-0105-w0_d1-seed-49.json.gz)
- [DATA/raw/run-0106-w0_d2-seed-49.json.gz](DATA/raw/run-0106-w0_d2-seed-49.json.gz)
- [DATA/raw/run-0107-w0_d4-seed-49.json.gz](DATA/raw/run-0107-w0_d4-seed-49.json.gz)
- [DATA/raw/run-0108-w50_d1-seed-49.json.gz](DATA/raw/run-0108-w50_d1-seed-49.json.gz)
- [DATA/raw/run-0109-w50_d2-seed-49.json.gz](DATA/raw/run-0109-w50_d2-seed-49.json.gz)
- [DATA/raw/run-0110-w50_d4-seed-49.json.gz](DATA/raw/run-0110-w50_d4-seed-49.json.gz)
- [DATA/raw/run-0111-w75_d1-seed-49.json.gz](DATA/raw/run-0111-w75_d1-seed-49.json.gz)
- [DATA/raw/run-0112-w75_d2-seed-49.json.gz](DATA/raw/run-0112-w75_d2-seed-49.json.gz)
- [DATA/raw/run-0113-w75_d4-seed-49.json.gz](DATA/raw/run-0113-w75_d4-seed-49.json.gz)
- [DATA/raw/run-0114-w100_d1-seed-49.json.gz](DATA/raw/run-0114-w100_d1-seed-49.json.gz)
- [DATA/raw/run-0115-w100_d2-seed-49.json.gz](DATA/raw/run-0115-w100_d2-seed-49.json.gz)
- [DATA/raw/run-0116-w100_d4-seed-49.json.gz](DATA/raw/run-0116-w100_d4-seed-49.json.gz)
- [DATA/raw/run-0117-w125_d1-seed-49.json.gz](DATA/raw/run-0117-w125_d1-seed-49.json.gz)
- [DATA/raw/run-0118-w125_d2-seed-49.json.gz](DATA/raw/run-0118-w125_d2-seed-49.json.gz)
- [DATA/raw/run-0119-w125_d4-seed-49.json.gz](DATA/raw/run-0119-w125_d4-seed-49.json.gz)
- [DATA/raw/run-0120-w0_d1-seed-50.json.gz](DATA/raw/run-0120-w0_d1-seed-50.json.gz)
- [DATA/raw/run-0121-w0_d2-seed-50.json.gz](DATA/raw/run-0121-w0_d2-seed-50.json.gz)
- [DATA/raw/run-0122-w0_d4-seed-50.json.gz](DATA/raw/run-0122-w0_d4-seed-50.json.gz)
- [DATA/raw/run-0123-w50_d1-seed-50.json.gz](DATA/raw/run-0123-w50_d1-seed-50.json.gz)
- [DATA/raw/run-0124-w50_d2-seed-50.json.gz](DATA/raw/run-0124-w50_d2-seed-50.json.gz)
- [DATA/raw/run-0125-w50_d4-seed-50.json.gz](DATA/raw/run-0125-w50_d4-seed-50.json.gz)
- [DATA/raw/run-0126-w75_d1-seed-50.json.gz](DATA/raw/run-0126-w75_d1-seed-50.json.gz)
- [DATA/raw/run-0127-w75_d2-seed-50.json.gz](DATA/raw/run-0127-w75_d2-seed-50.json.gz)
- [DATA/raw/run-0128-w75_d4-seed-50.json.gz](DATA/raw/run-0128-w75_d4-seed-50.json.gz)
- [DATA/raw/run-0129-w100_d1-seed-50.json.gz](DATA/raw/run-0129-w100_d1-seed-50.json.gz)
- [DATA/raw/run-0130-w100_d2-seed-50.json.gz](DATA/raw/run-0130-w100_d2-seed-50.json.gz)
- [DATA/raw/run-0131-w100_d4-seed-50.json.gz](DATA/raw/run-0131-w100_d4-seed-50.json.gz)
- [DATA/raw/run-0132-w125_d1-seed-50.json.gz](DATA/raw/run-0132-w125_d1-seed-50.json.gz)
- [DATA/raw/run-0133-w125_d2-seed-50.json.gz](DATA/raw/run-0133-w125_d2-seed-50.json.gz)
- [DATA/raw/run-0134-w125_d4-seed-50.json.gz](DATA/raw/run-0134-w125_d4-seed-50.json.gz)
- [DATA/raw/run-0135-w0_d1-seed-51.json.gz](DATA/raw/run-0135-w0_d1-seed-51.json.gz)
- [DATA/raw/run-0136-w0_d2-seed-51.json.gz](DATA/raw/run-0136-w0_d2-seed-51.json.gz)
- [DATA/raw/run-0137-w0_d4-seed-51.json.gz](DATA/raw/run-0137-w0_d4-seed-51.json.gz)
- [DATA/raw/run-0138-w50_d1-seed-51.json.gz](DATA/raw/run-0138-w50_d1-seed-51.json.gz)
- [DATA/raw/run-0139-w50_d2-seed-51.json.gz](DATA/raw/run-0139-w50_d2-seed-51.json.gz)
- [DATA/raw/run-0140-w50_d4-seed-51.json.gz](DATA/raw/run-0140-w50_d4-seed-51.json.gz)
- [DATA/raw/run-0141-w75_d1-seed-51.json.gz](DATA/raw/run-0141-w75_d1-seed-51.json.gz)
- [DATA/raw/run-0142-w75_d2-seed-51.json.gz](DATA/raw/run-0142-w75_d2-seed-51.json.gz)
- [DATA/raw/run-0143-w75_d4-seed-51.json.gz](DATA/raw/run-0143-w75_d4-seed-51.json.gz)
- [DATA/raw/run-0144-w100_d1-seed-51.json.gz](DATA/raw/run-0144-w100_d1-seed-51.json.gz)
- [DATA/raw/run-0145-w100_d2-seed-51.json.gz](DATA/raw/run-0145-w100_d2-seed-51.json.gz)
- [DATA/raw/run-0146-w100_d4-seed-51.json.gz](DATA/raw/run-0146-w100_d4-seed-51.json.gz)
- [DATA/raw/run-0147-w125_d1-seed-51.json.gz](DATA/raw/run-0147-w125_d1-seed-51.json.gz)
- [DATA/raw/run-0148-w125_d2-seed-51.json.gz](DATA/raw/run-0148-w125_d2-seed-51.json.gz)
- [DATA/raw/run-0149-w125_d4-seed-51.json.gz](DATA/raw/run-0149-w125_d4-seed-51.json.gz)
- [DATA/raw/run-0150-w0_d1-seed-52.json.gz](DATA/raw/run-0150-w0_d1-seed-52.json.gz)
- [DATA/raw/run-0151-w0_d2-seed-52.json.gz](DATA/raw/run-0151-w0_d2-seed-52.json.gz)
- [DATA/raw/run-0152-w0_d4-seed-52.json.gz](DATA/raw/run-0152-w0_d4-seed-52.json.gz)
- [DATA/raw/run-0153-w50_d1-seed-52.json.gz](DATA/raw/run-0153-w50_d1-seed-52.json.gz)
- [DATA/raw/run-0154-w50_d2-seed-52.json.gz](DATA/raw/run-0154-w50_d2-seed-52.json.gz)
- [DATA/raw/run-0155-w50_d4-seed-52.json.gz](DATA/raw/run-0155-w50_d4-seed-52.json.gz)
- [DATA/raw/run-0156-w75_d1-seed-52.json.gz](DATA/raw/run-0156-w75_d1-seed-52.json.gz)
- [DATA/raw/run-0157-w75_d2-seed-52.json.gz](DATA/raw/run-0157-w75_d2-seed-52.json.gz)
- [DATA/raw/run-0158-w75_d4-seed-52.json.gz](DATA/raw/run-0158-w75_d4-seed-52.json.gz)
- [DATA/raw/run-0159-w100_d1-seed-52.json.gz](DATA/raw/run-0159-w100_d1-seed-52.json.gz)
- [DATA/raw/run-0160-w100_d2-seed-52.json.gz](DATA/raw/run-0160-w100_d2-seed-52.json.gz)
- [DATA/raw/run-0161-w100_d4-seed-52.json.gz](DATA/raw/run-0161-w100_d4-seed-52.json.gz)
- [DATA/raw/run-0162-w125_d1-seed-52.json.gz](DATA/raw/run-0162-w125_d1-seed-52.json.gz)
- [DATA/raw/run-0163-w125_d2-seed-52.json.gz](DATA/raw/run-0163-w125_d2-seed-52.json.gz)
- [DATA/raw/run-0164-w125_d4-seed-52.json.gz](DATA/raw/run-0164-w125_d4-seed-52.json.gz)
- [DATA/raw/run-0165-w0_d1-seed-53.json.gz](DATA/raw/run-0165-w0_d1-seed-53.json.gz)
- [DATA/raw/run-0166-w0_d2-seed-53.json.gz](DATA/raw/run-0166-w0_d2-seed-53.json.gz)
- [DATA/raw/run-0167-w0_d4-seed-53.json.gz](DATA/raw/run-0167-w0_d4-seed-53.json.gz)
- [DATA/raw/run-0168-w50_d1-seed-53.json.gz](DATA/raw/run-0168-w50_d1-seed-53.json.gz)
- [DATA/raw/run-0169-w50_d2-seed-53.json.gz](DATA/raw/run-0169-w50_d2-seed-53.json.gz)
- [DATA/raw/run-0170-w50_d4-seed-53.json.gz](DATA/raw/run-0170-w50_d4-seed-53.json.gz)
- [DATA/raw/run-0171-w75_d1-seed-53.json.gz](DATA/raw/run-0171-w75_d1-seed-53.json.gz)
- [DATA/raw/run-0172-w75_d2-seed-53.json.gz](DATA/raw/run-0172-w75_d2-seed-53.json.gz)
- [DATA/raw/run-0173-w75_d4-seed-53.json.gz](DATA/raw/run-0173-w75_d4-seed-53.json.gz)
- [DATA/raw/run-0174-w100_d1-seed-53.json.gz](DATA/raw/run-0174-w100_d1-seed-53.json.gz)
- [DATA/raw/run-0175-w100_d2-seed-53.json.gz](DATA/raw/run-0175-w100_d2-seed-53.json.gz)
- [DATA/raw/run-0176-w100_d4-seed-53.json.gz](DATA/raw/run-0176-w100_d4-seed-53.json.gz)
- [DATA/raw/run-0177-w125_d1-seed-53.json.gz](DATA/raw/run-0177-w125_d1-seed-53.json.gz)
- [DATA/raw/run-0178-w125_d2-seed-53.json.gz](DATA/raw/run-0178-w125_d2-seed-53.json.gz)
- [DATA/raw/run-0179-w125_d4-seed-53.json.gz](DATA/raw/run-0179-w125_d4-seed-53.json.gz)
- [DATA/raw/run-0180-w0_d1-seed-54.json.gz](DATA/raw/run-0180-w0_d1-seed-54.json.gz)
- [DATA/raw/run-0181-w0_d2-seed-54.json.gz](DATA/raw/run-0181-w0_d2-seed-54.json.gz)
- [DATA/raw/run-0182-w0_d4-seed-54.json.gz](DATA/raw/run-0182-w0_d4-seed-54.json.gz)
- [DATA/raw/run-0183-w50_d1-seed-54.json.gz](DATA/raw/run-0183-w50_d1-seed-54.json.gz)
- [DATA/raw/run-0184-w50_d2-seed-54.json.gz](DATA/raw/run-0184-w50_d2-seed-54.json.gz)
- [DATA/raw/run-0185-w50_d4-seed-54.json.gz](DATA/raw/run-0185-w50_d4-seed-54.json.gz)
- [DATA/raw/run-0186-w75_d1-seed-54.json.gz](DATA/raw/run-0186-w75_d1-seed-54.json.gz)
- [DATA/raw/run-0187-w75_d2-seed-54.json.gz](DATA/raw/run-0187-w75_d2-seed-54.json.gz)
- [DATA/raw/run-0188-w75_d4-seed-54.json.gz](DATA/raw/run-0188-w75_d4-seed-54.json.gz)
- [DATA/raw/run-0189-w100_d1-seed-54.json.gz](DATA/raw/run-0189-w100_d1-seed-54.json.gz)
- [DATA/raw/run-0190-w100_d2-seed-54.json.gz](DATA/raw/run-0190-w100_d2-seed-54.json.gz)
- [DATA/raw/run-0191-w100_d4-seed-54.json.gz](DATA/raw/run-0191-w100_d4-seed-54.json.gz)
- [DATA/raw/run-0192-w125_d1-seed-54.json.gz](DATA/raw/run-0192-w125_d1-seed-54.json.gz)
- [DATA/raw/run-0193-w125_d2-seed-54.json.gz](DATA/raw/run-0193-w125_d2-seed-54.json.gz)
- [DATA/raw/run-0194-w125_d4-seed-54.json.gz](DATA/raw/run-0194-w125_d4-seed-54.json.gz)
- [DATA/raw/run-0195-w0_d1-seed-55.json.gz](DATA/raw/run-0195-w0_d1-seed-55.json.gz)
- [DATA/raw/run-0196-w0_d2-seed-55.json.gz](DATA/raw/run-0196-w0_d2-seed-55.json.gz)
- [DATA/raw/run-0197-w0_d4-seed-55.json.gz](DATA/raw/run-0197-w0_d4-seed-55.json.gz)
- [DATA/raw/run-0198-w50_d1-seed-55.json.gz](DATA/raw/run-0198-w50_d1-seed-55.json.gz)
- [DATA/raw/run-0199-w50_d2-seed-55.json.gz](DATA/raw/run-0199-w50_d2-seed-55.json.gz)
- [DATA/raw/run-0200-w50_d4-seed-55.json.gz](DATA/raw/run-0200-w50_d4-seed-55.json.gz)
- [DATA/raw/run-0201-w75_d1-seed-55.json.gz](DATA/raw/run-0201-w75_d1-seed-55.json.gz)
- [DATA/raw/run-0202-w75_d2-seed-55.json.gz](DATA/raw/run-0202-w75_d2-seed-55.json.gz)
- [DATA/raw/run-0203-w75_d4-seed-55.json.gz](DATA/raw/run-0203-w75_d4-seed-55.json.gz)
- [DATA/raw/run-0204-w100_d1-seed-55.json.gz](DATA/raw/run-0204-w100_d1-seed-55.json.gz)
- [DATA/raw/run-0205-w100_d2-seed-55.json.gz](DATA/raw/run-0205-w100_d2-seed-55.json.gz)
- [DATA/raw/run-0206-w100_d4-seed-55.json.gz](DATA/raw/run-0206-w100_d4-seed-55.json.gz)
- [DATA/raw/run-0207-w125_d1-seed-55.json.gz](DATA/raw/run-0207-w125_d1-seed-55.json.gz)
- [DATA/raw/run-0208-w125_d2-seed-55.json.gz](DATA/raw/run-0208-w125_d2-seed-55.json.gz)
- [DATA/raw/run-0209-w125_d4-seed-55.json.gz](DATA/raw/run-0209-w125_d4-seed-55.json.gz)
- [DATA/raw/run-0210-w0_d1-seed-56.json.gz](DATA/raw/run-0210-w0_d1-seed-56.json.gz)
- [DATA/raw/run-0211-w0_d2-seed-56.json.gz](DATA/raw/run-0211-w0_d2-seed-56.json.gz)
- [DATA/raw/run-0212-w0_d4-seed-56.json.gz](DATA/raw/run-0212-w0_d4-seed-56.json.gz)
- [DATA/raw/run-0213-w50_d1-seed-56.json.gz](DATA/raw/run-0213-w50_d1-seed-56.json.gz)
- [DATA/raw/run-0214-w50_d2-seed-56.json.gz](DATA/raw/run-0214-w50_d2-seed-56.json.gz)
- [DATA/raw/run-0215-w50_d4-seed-56.json.gz](DATA/raw/run-0215-w50_d4-seed-56.json.gz)
- [DATA/raw/run-0216-w75_d1-seed-56.json.gz](DATA/raw/run-0216-w75_d1-seed-56.json.gz)
- [DATA/raw/run-0217-w75_d2-seed-56.json.gz](DATA/raw/run-0217-w75_d2-seed-56.json.gz)
- [DATA/raw/run-0218-w75_d4-seed-56.json.gz](DATA/raw/run-0218-w75_d4-seed-56.json.gz)
- [DATA/raw/run-0219-w100_d1-seed-56.json.gz](DATA/raw/run-0219-w100_d1-seed-56.json.gz)
- [DATA/raw/run-0220-w100_d2-seed-56.json.gz](DATA/raw/run-0220-w100_d2-seed-56.json.gz)
- [DATA/raw/run-0221-w100_d4-seed-56.json.gz](DATA/raw/run-0221-w100_d4-seed-56.json.gz)
- [DATA/raw/run-0222-w125_d1-seed-56.json.gz](DATA/raw/run-0222-w125_d1-seed-56.json.gz)
- [DATA/raw/run-0223-w125_d2-seed-56.json.gz](DATA/raw/run-0223-w125_d2-seed-56.json.gz)
- [DATA/raw/run-0224-w125_d4-seed-56.json.gz](DATA/raw/run-0224-w125_d4-seed-56.json.gz)
- [DATA/raw/run-0225-w0_d1-seed-57.json.gz](DATA/raw/run-0225-w0_d1-seed-57.json.gz)
- [DATA/raw/run-0226-w0_d2-seed-57.json.gz](DATA/raw/run-0226-w0_d2-seed-57.json.gz)
- [DATA/raw/run-0227-w0_d4-seed-57.json.gz](DATA/raw/run-0227-w0_d4-seed-57.json.gz)
- [DATA/raw/run-0228-w50_d1-seed-57.json.gz](DATA/raw/run-0228-w50_d1-seed-57.json.gz)
- [DATA/raw/run-0229-w50_d2-seed-57.json.gz](DATA/raw/run-0229-w50_d2-seed-57.json.gz)
- [DATA/raw/run-0230-w50_d4-seed-57.json.gz](DATA/raw/run-0230-w50_d4-seed-57.json.gz)
- [DATA/raw/run-0231-w75_d1-seed-57.json.gz](DATA/raw/run-0231-w75_d1-seed-57.json.gz)
- [DATA/raw/run-0232-w75_d2-seed-57.json.gz](DATA/raw/run-0232-w75_d2-seed-57.json.gz)
- [DATA/raw/run-0233-w75_d4-seed-57.json.gz](DATA/raw/run-0233-w75_d4-seed-57.json.gz)
- [DATA/raw/run-0234-w100_d1-seed-57.json.gz](DATA/raw/run-0234-w100_d1-seed-57.json.gz)
- [DATA/raw/run-0235-w100_d2-seed-57.json.gz](DATA/raw/run-0235-w100_d2-seed-57.json.gz)
- [DATA/raw/run-0236-w100_d4-seed-57.json.gz](DATA/raw/run-0236-w100_d4-seed-57.json.gz)
- [DATA/raw/run-0237-w125_d1-seed-57.json.gz](DATA/raw/run-0237-w125_d1-seed-57.json.gz)
- [DATA/raw/run-0238-w125_d2-seed-57.json.gz](DATA/raw/run-0238-w125_d2-seed-57.json.gz)
- [DATA/raw/run-0239-w125_d4-seed-57.json.gz](DATA/raw/run-0239-w125_d4-seed-57.json.gz)
- [DATA/raw/run-0240-w0_d1-seed-58.json.gz](DATA/raw/run-0240-w0_d1-seed-58.json.gz)
- [DATA/raw/run-0241-w0_d2-seed-58.json.gz](DATA/raw/run-0241-w0_d2-seed-58.json.gz)
- [DATA/raw/run-0242-w0_d4-seed-58.json.gz](DATA/raw/run-0242-w0_d4-seed-58.json.gz)
- [DATA/raw/run-0243-w50_d1-seed-58.json.gz](DATA/raw/run-0243-w50_d1-seed-58.json.gz)
- [DATA/raw/run-0244-w50_d2-seed-58.json.gz](DATA/raw/run-0244-w50_d2-seed-58.json.gz)
- [DATA/raw/run-0245-w50_d4-seed-58.json.gz](DATA/raw/run-0245-w50_d4-seed-58.json.gz)
- [DATA/raw/run-0246-w75_d1-seed-58.json.gz](DATA/raw/run-0246-w75_d1-seed-58.json.gz)
- [DATA/raw/run-0247-w75_d2-seed-58.json.gz](DATA/raw/run-0247-w75_d2-seed-58.json.gz)
- [DATA/raw/run-0248-w75_d4-seed-58.json.gz](DATA/raw/run-0248-w75_d4-seed-58.json.gz)
- [DATA/raw/run-0249-w100_d1-seed-58.json.gz](DATA/raw/run-0249-w100_d1-seed-58.json.gz)
- [DATA/raw/run-0250-w100_d2-seed-58.json.gz](DATA/raw/run-0250-w100_d2-seed-58.json.gz)
- [DATA/raw/run-0251-w100_d4-seed-58.json.gz](DATA/raw/run-0251-w100_d4-seed-58.json.gz)
- [DATA/raw/run-0252-w125_d1-seed-58.json.gz](DATA/raw/run-0252-w125_d1-seed-58.json.gz)
- [DATA/raw/run-0253-w125_d2-seed-58.json.gz](DATA/raw/run-0253-w125_d2-seed-58.json.gz)
- [DATA/raw/run-0254-w125_d4-seed-58.json.gz](DATA/raw/run-0254-w125_d4-seed-58.json.gz)
- [DATA/raw/run-0255-w0_d1-seed-59.json.gz](DATA/raw/run-0255-w0_d1-seed-59.json.gz)
- [DATA/raw/run-0256-w0_d2-seed-59.json.gz](DATA/raw/run-0256-w0_d2-seed-59.json.gz)
- [DATA/raw/run-0257-w0_d4-seed-59.json.gz](DATA/raw/run-0257-w0_d4-seed-59.json.gz)
- [DATA/raw/run-0258-w50_d1-seed-59.json.gz](DATA/raw/run-0258-w50_d1-seed-59.json.gz)
- [DATA/raw/run-0259-w50_d2-seed-59.json.gz](DATA/raw/run-0259-w50_d2-seed-59.json.gz)
- [DATA/raw/run-0260-w50_d4-seed-59.json.gz](DATA/raw/run-0260-w50_d4-seed-59.json.gz)
- [DATA/raw/run-0261-w75_d1-seed-59.json.gz](DATA/raw/run-0261-w75_d1-seed-59.json.gz)
- [DATA/raw/run-0262-w75_d2-seed-59.json.gz](DATA/raw/run-0262-w75_d2-seed-59.json.gz)
- [DATA/raw/run-0263-w75_d4-seed-59.json.gz](DATA/raw/run-0263-w75_d4-seed-59.json.gz)
- [DATA/raw/run-0264-w100_d1-seed-59.json.gz](DATA/raw/run-0264-w100_d1-seed-59.json.gz)
- [DATA/raw/run-0265-w100_d2-seed-59.json.gz](DATA/raw/run-0265-w100_d2-seed-59.json.gz)
- [DATA/raw/run-0266-w100_d4-seed-59.json.gz](DATA/raw/run-0266-w100_d4-seed-59.json.gz)
- [DATA/raw/run-0267-w125_d1-seed-59.json.gz](DATA/raw/run-0267-w125_d1-seed-59.json.gz)
- [DATA/raw/run-0268-w125_d2-seed-59.json.gz](DATA/raw/run-0268-w125_d2-seed-59.json.gz)
- [DATA/raw/run-0269-w125_d4-seed-59.json.gz](DATA/raw/run-0269-w125_d4-seed-59.json.gz)
- [DATA/raw/run-0270-w0_d1-seed-60.json.gz](DATA/raw/run-0270-w0_d1-seed-60.json.gz)
- [DATA/raw/run-0271-w0_d2-seed-60.json.gz](DATA/raw/run-0271-w0_d2-seed-60.json.gz)
- [DATA/raw/run-0272-w0_d4-seed-60.json.gz](DATA/raw/run-0272-w0_d4-seed-60.json.gz)
- [DATA/raw/run-0273-w50_d1-seed-60.json.gz](DATA/raw/run-0273-w50_d1-seed-60.json.gz)
- [DATA/raw/run-0274-w50_d2-seed-60.json.gz](DATA/raw/run-0274-w50_d2-seed-60.json.gz)
- [DATA/raw/run-0275-w50_d4-seed-60.json.gz](DATA/raw/run-0275-w50_d4-seed-60.json.gz)
- [DATA/raw/run-0276-w75_d1-seed-60.json.gz](DATA/raw/run-0276-w75_d1-seed-60.json.gz)
- [DATA/raw/run-0277-w75_d2-seed-60.json.gz](DATA/raw/run-0277-w75_d2-seed-60.json.gz)
- [DATA/raw/run-0278-w75_d4-seed-60.json.gz](DATA/raw/run-0278-w75_d4-seed-60.json.gz)
- [DATA/raw/run-0279-w100_d1-seed-60.json.gz](DATA/raw/run-0279-w100_d1-seed-60.json.gz)
- [DATA/raw/run-0280-w100_d2-seed-60.json.gz](DATA/raw/run-0280-w100_d2-seed-60.json.gz)
- [DATA/raw/run-0281-w100_d4-seed-60.json.gz](DATA/raw/run-0281-w100_d4-seed-60.json.gz)
- [DATA/raw/run-0282-w125_d1-seed-60.json.gz](DATA/raw/run-0282-w125_d1-seed-60.json.gz)
- [DATA/raw/run-0283-w125_d2-seed-60.json.gz](DATA/raw/run-0283-w125_d2-seed-60.json.gz)
- [DATA/raw/run-0284-w125_d4-seed-60.json.gz](DATA/raw/run-0284-w125_d4-seed-60.json.gz)
- [DATA/raw/run-0285-w0_d1-seed-61.json.gz](DATA/raw/run-0285-w0_d1-seed-61.json.gz)
- [DATA/raw/run-0286-w0_d2-seed-61.json.gz](DATA/raw/run-0286-w0_d2-seed-61.json.gz)
- [DATA/raw/run-0287-w0_d4-seed-61.json.gz](DATA/raw/run-0287-w0_d4-seed-61.json.gz)
- [DATA/raw/run-0288-w50_d1-seed-61.json.gz](DATA/raw/run-0288-w50_d1-seed-61.json.gz)
- [DATA/raw/run-0289-w50_d2-seed-61.json.gz](DATA/raw/run-0289-w50_d2-seed-61.json.gz)
- [DATA/raw/run-0290-w50_d4-seed-61.json.gz](DATA/raw/run-0290-w50_d4-seed-61.json.gz)
- [DATA/raw/run-0291-w75_d1-seed-61.json.gz](DATA/raw/run-0291-w75_d1-seed-61.json.gz)
- [DATA/raw/run-0292-w75_d2-seed-61.json.gz](DATA/raw/run-0292-w75_d2-seed-61.json.gz)
- [DATA/raw/run-0293-w75_d4-seed-61.json.gz](DATA/raw/run-0293-w75_d4-seed-61.json.gz)
- [DATA/raw/run-0294-w100_d1-seed-61.json.gz](DATA/raw/run-0294-w100_d1-seed-61.json.gz)
- [DATA/raw/run-0295-w100_d2-seed-61.json.gz](DATA/raw/run-0295-w100_d2-seed-61.json.gz)
- [DATA/raw/run-0296-w100_d4-seed-61.json.gz](DATA/raw/run-0296-w100_d4-seed-61.json.gz)
- [DATA/raw/run-0297-w125_d1-seed-61.json.gz](DATA/raw/run-0297-w125_d1-seed-61.json.gz)
- [DATA/raw/run-0298-w125_d2-seed-61.json.gz](DATA/raw/run-0298-w125_d2-seed-61.json.gz)
- [DATA/raw/run-0299-w125_d4-seed-61.json.gz](DATA/raw/run-0299-w125_d4-seed-61.json.gz)
- [DATA/runs.json](DATA/runs.json)
- [DATA/runs_index.json](DATA/runs_index.json)
- [manifest.json](manifest.json)
- [report.md](report.md)
- [workflow.json](workflow.json)

## 10. Wissenschaftliche Grenze und Schlussfolgerung

Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.

**Gesamtstatus:** technische Ausfuehrung `completed`, Tick-Vertrag `SATISFIED`, semantische Zuordnung `DIRECT_MATCH`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.
