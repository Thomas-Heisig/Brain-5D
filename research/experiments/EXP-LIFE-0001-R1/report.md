# EXP-LIFE-0001-R1: Learning interference screen retry after trial-state reset

## Forschungszuordnung
Forschungsfrage: `RQ-LIFE-001`
Hypothese: `H-LIFE-001-A`
Aufgeloester Runner: `run_learning_interference`

## Protokoll und Einstellungen
Protokoll: `learning_interference_screen_v1`
Angeforderte Mindest-Ticks: `1`
Seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61`
Tick-Vertrag: `{"mode": "protocol_defined_internal_trials", "requested_ticks": 1, "status": "NOT_APPLICABLE"}`

## Bedingungen
Sequential three-task screen; frozen seed set 42-61.
Runs: 20; Dauer: 5.140379 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Retry after isolating transient neuron state between independent tasks.
