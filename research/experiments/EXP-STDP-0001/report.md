# EXP-STDP-0001: Pair-Timing STDP

## Klassifikation
Pilot- und Methodenvalidierung. Dieser Lauf ist nicht evidenzfaehig und wird weder fuer `CLAIM-STDP-001` noch fuer `RQ-STDP-001` gezaehlt.

## Forschungsfrage und Hypothese
- Forschungsfrage: `RQ-STDP-001`
- Hypothese: `H-STDP-001-A`
- Ziel: die mathematische Timing-Signatur der isolierten `STDPSynapse` pruefen.

## Protokoll und Bedingungen
- Protokoll: `stdp_pair_timing_v1`
- Timing-Bedingungen: -50, -20, -10, -5, -1, 0, +1, +5, +10, +20, +50 ms
- Startgewicht: 0.5
- STDP-Parameter: `a_plus=0.1`, `a_minus=0.12`, `tau_plus=20`, `tau_minus=20`
- Wiederholte Auswertungen: 10 je Bedingung, insgesamt 110
- Unabhaengige stochastische Runs: 0

## Messung und Ergebnis
Messgroesse: `Delta w = w_after - w_before`.

Alle positiven Delta-t-Werte erzeugten LTP, alle negativen Delta-t-Werte LTD und Delta t = 0 keine Gewichtsveraenderung. Die wiederholten Auswertungen waren innerhalb jeder Bedingung bit-identisch.

- LTP-Mittelwert: `0.05573051`
- LTD-Mittelwert: `-0.06687661`
- Delta t = 0: `0.00000000`
- Laufzeit: `0.000131 s`

## Reproduzierbarkeit
Der Git-Commit, Python, Betriebssystem, Version und der Protokoll-Snapshot sind im Manifest festgehalten. Der Tree war beim Lauf jedoch dirty. Der Seed `42` ist dokumentiert, wird von diesem voll deterministischen Laborprotokoll aber nicht als Zufallsquelle verwendet.

## Evidenzstatus und Grenzen
Es wurde bewusst keine `EVID-*`-Datei erzeugt. Die fruehere `EVID-2026-17` wurde entfernt, weil ein Dirty Tree keine wissenschaftliche Evidenz erzeugen darf.

Der Lauf verifiziert nur die isolierte Pair-STDP-Implementierung. Ein evidenzfaehiger Nachfolger muss auf einem sauberen, CI-gruenen Commit den produktiven Pfad `NeuralNetwork -> LearningEngine -> reale Synapse -> Delta w` mit unabhaengigen Runs messen.
