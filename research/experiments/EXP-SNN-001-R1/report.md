# EXP-SNN-001-R1: Sustained activity stability v1 replication

## Forschungszuordnung
Forschungsfrage: `RQ-SNN-001`
Hypothese: `H-SNN-001-A`
Aufgeloester Runner: `run_sustained_stability`

## Protokoll und Einstellungen
Protokoll: `sustained_activity_stability_v1`
Angeforderte Mindest-Ticks: `100000`
Seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51`
Tick-Vertrag: `{"mode": "protocol_defined_internal_trials", "requested_ticks": 100000, "status": "NOT_APPLICABLE"}`

## Bedingungen
No-input control vs tonic drive 50.0; 100000 ticks; 10000 tick burn-in; 1000 tick windows.
Runs: 20; Dauer: 12.247346 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Exact protocol replication after tick-contract registry correction. Frozen PREREG-SNN-001.
