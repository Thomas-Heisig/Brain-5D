# EXP-SNN-002-R1: RQ-SNN-002 constant-input spike reproducibility

## Forschungszuordnung
Forschungsfrage: `RQ-SNN-002`
Hypothese: `H-SNN-002-A`
Aufgeloester Runner: `run_ping`

## Protokoll und Einstellungen
Protokoll: `science_suite_v1`
Angeforderte Mindest-Ticks: `8`
Seeds: `42, 43, 44, 45, 46, 47, 48, 49, 50, 51`
Tick-Vertrag: `{"mode": "minimum_per_run", "observed_max": 8, "observed_min": 8, "requested_ticks": 8, "status": "SATISFIED"}`

## Bedingungen
Constant impulse input; recurrence_off versus recurrence_on; 10 independent seeds
Runs: 20; Dauer: 0.015288 s

## Daten und Statistik
Kompakte Run-Projektion: `DATA/runs.json`
Unveränderlicher Rohdatenindex: `DATA/runs_index.json`
KI-Eingabepaket: `analysis/ai_packet.json` (hart begrenzt)
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## Epistemische Ebenen
UI-Zustand: Dashboard-Steuerung und Fortschritt; kein wissenschaftliches Ergebnis.
DATA: Rohdaten, Run-Index und deterministische Statistik.
EVID: nicht erzeugt; Clean Freeze, semantische Zuordnung und Human Review erforderlich.
Interpretation: nachgelagerte KI-/Human-Interpretation; keine Ausfuehrungseingabe.

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

## Hinweise
Technical reproducibility run; AI post-hoc interpretation only; no evidence promotion.
