# EXP-REG-0002-R1: Closed-loop regulation recovery v1

## Forschungszuordnung
Forschungsfrage: `RQ-REG-002`
Hypothese: `H-REG-002-A`
Aufgeloester Runner: `run_regulation_recovery`

## Protokoll und Einstellungen
Protokoll: `closed_loop_regulation_v1`
Angeforderte Mindest-Ticks: `128`
Seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61`
Tick-Vertrag: `{"mode": "minimum_per_run", "observed_max": 128, "observed_min": 128, "requested_ticks": 128, "status": "SATISFIED"}`

## Bedingungen
Regulation off control vs regulation on treatment; nominal-pressure-recovery schedule; seeds 42-61.
Runs: 40; Dauer: 0.208793 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Full PREREG-REG-002 seed set.
