# EXP-REPL-0001-R1: Independent replication retry after run-mode fix

## Forschungszuordnung
Forschungsfrage: `RQ-REPL-001`
Hypothese: `H-REPL-001-A`
Aufgeloester Runner: `run_replication`

## Protokoll und Einstellungen
Protokoll: `independent_replication_v1`
Angeforderte Mindest-Ticks: `256`
Seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61`
Tick-Vertrag: `{"mode": "minimum_per_run", "observed_max": 256, "observed_min": 256, "requested_ticks": 256, "status": "SATISFIED"}`

## Bedingungen
Recurrence off control vs recurrence on treatment; frozen seed set 42-61.
Runs: 40; Dauer: 0.089620 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Retry after accepting REPLICATION run mode in manifest governance.
