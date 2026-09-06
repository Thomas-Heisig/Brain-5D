# EXP-GEN-0028: Long-term stability diagnostic suite

## Forschungszuordnung
Forschungsfrage: `RQ-SNN-001`
Hypothese: `H-SNN-001-A`
Aufgeloester Runner: `run_all`

## Protokoll und Einstellungen
Protokoll: `science_all_v1`
Angeforderte Mindest-Ticks: `100000`
Seeds: `42, 43, 44`
Tick-Vertrag: `{"mode": "mixed_protocol_tick_contract", "requested_ticks": 100000, "status": "SATISFIED"}`

## Bedingungen
Seeds 42,43,44; complete diagnostic suite; RQ-SNN-001 remains evidence-blocked until a sustained-activity protocol exists.
Runs: 57; Dauer: 277.134535 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Verlängerung der Simulationsdauer (Ticks) auf mindestens 100.000, um die Hypothese H-SNN-001-A empirisch zu testen und die Langzeitstabilität der Spike-Dynamik zu validieren
