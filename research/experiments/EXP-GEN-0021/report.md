# EXP-GEN-0021: Complete science suite

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
Seeds 42,43,44; alle registrierten Science-Suite-Runner ausführen; Bedingungen im DATA über Gruppenpräfixe trennen.
Runs: 57; Dauer: 237.534093 s

## Daten und Statistik
Rohdaten: `DATA/runs.json`
Deterministische deskriptive Statistik: `analysis/statistics.json`
Die Summary verbindet Rohdaten, Formeln, Einzelruns, Bedingungen, Reproduzierbarkeit und AIRR ohne KI-generierte Statistik.

## KI-generierte wissenschaftliche Interpretation

Eine ausführliche post-hoc Analyse liegt in [`AI_ANALYSIS_GPT-5.6-SOL.md`](AI_ANALYSIS_GPT-5.6-SOL.md).

Diese Datei ist ausdrücklich als **KI-generiert**, `interpretation_only` und **nicht evidenzbildend** gekennzeichnet. Sie darf Hypothesen und Folgeexperimente vorschlagen, verändert aber weder DATA noch Evidenzstatus. Human Review bleibt erforderlich.

Aus der Analyse abgeleitete, noch zu prüfende Forschungsfragen und Hypothesen liegen projektweit in:

- `research/registry/EXP_GEN_0021_FOLLOWUP_QUESTIONS.yaml`
- `research/registry/EXP_GEN_0021_FOLLOWUP_HYPOTHESES.yaml`
- `research/protocols/EXP_GEN_0021_FOLLOWUP_PROGRAM.yaml`

## Evidenzstatus
DATA, Manifest, Workflow und deterministische Statistik sind erzeugt. Wissenschaftliche EVID entsteht erst nach passender semantischer Zuordnung, Clean Freeze und Human Review.

`science_all_v1` ist als Omnibus-/Diagnostiklauf zu behandeln. Die darin enthaltenen domänenspezifischen Effekte müssen für wissenschaftliche Claims in eigenen RQ-/Hypothesen-spezifischen, preregistrierten Experimenten geprüft werden.

## Hinweise
Der Mixed-Tick-Contract umfasst protokollspezifische Timing-Subruns mit 100, 1.000, 10.000 und 100.000 Ticks. Eine globale Aussage, alle 57 Runs hätten exakt 100.000 Ticks ausgeführt, ist daher für den Omnibus-Lauf nicht angemessen.
