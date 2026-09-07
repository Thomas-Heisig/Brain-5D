# EXP-GEN-0034: Network impulse response

## Forschungszuordnung
Forschungsfrage: `RQ-SNN-002`
Hypothese: `H-SNN-002-A`
Aufgeloester Runner: `run_ping`

## Protokoll und Einstellungen
Protokoll: `science_suite_v1`
Angeforderte Mindest-Ticks: `100`
Seeds: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11`
Tick-Vertrag: `{"mode": "minimum_per_run", "observed_max": 100, "observed_min": 100, "requested_ticks": 100, "status": "SATISFIED"}`

## Bedingungen
Seeds 42,43,44; identical initial state per seed; impulse current 100.0; recurrence as controlled treatment.
Runs: 22; Dauer: 0.032741 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Keine.
