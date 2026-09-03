# Brain-5D — Alpha.8 Recursive Loopback TODO

> Ergänzung zur konsolidierten `TODO.md` für die geplante Alpha.8-Integration.
> Verbindliche Architektur: `docs/02-architecture/RECURSIVE_CAUSAL_LOOPBACKS.md`
> Umsetzungsanweisung: `docs/09-sprints/PROMPT_ALPHA8_RECURSIVE_LOOPBACKS.md`

## P0 — Release-Freeze vor neuer Kausalarchitektur

- [ ] Bestehende Black-Fehler beheben; keine neue Feature-Implementierung auf ungeformattetem Stand beginnen
- [ ] Die aktuell sechs mypy-Fehler sauber typisieren statt pauschal zu ignorieren
- [ ] Python 3.11/3.12/3.13 Vollsuite erneut ausführen
- [ ] Black, Ruff, Pylint, mypy, Pyright und Scientific Integrity Gate vollständig grün bekommen
- [ ] Clean-Freeze mit Git SHA, Tree-Digest und Teststatus erzeugen

## P1 — Recursive Causal Loopback

- [ ] Paket `src/self_causality/` anlegen
- [ ] `EfferenceCopy` als immutable Record vor autorisierten Aktionen implementieren
- [ ] `EffectPrediction` mit Signal, Richtung, Wertebereich, Verzögerung, Toleranz und Confidence implementieren
- [ ] `ObservedEffect` ausschließlich aus realen Sensor-/Environment-Beobachtungen ableiten
- [ ] `CausalAttributionClass` mit `SELF_CAUSED`, `EXTERNAL_CAUSE`, `MIXED`, `UNCERTAIN`, `NO_EFFECT` implementieren
- [ ] `CausalAttribution` mit Match-, Temporal-, Alternative-Cause-Score und Confidence implementieren
- [ ] Deterministischen `CausalComparator` implementieren
- [ ] `SelfCausalModel` mit actuator-/sensorbezogener Causal Confidence und Replay-Support implementieren
- [ ] `SelfCausalLoopback` implementieren, der Attributionen optional wieder als typisierten Input verfügbar macht
- [ ] Observer Mode sicherstellen: `feedback_gain=0.0` erzeugt Records ohne SNN-Rückwirkung
- [ ] Rückführung nur bei `self_causal_feedback_enabled=true` und positivem `feedback_gain` zulassen
- [ ] LLM/Language Organ ausdrücklich von kausalen Schreibrechten ausschließen
- [ ] Fehlende oder veraltete Beobachtungen als `UNCERTAIN` bzw. Confidence-Abfall behandeln
- [ ] Loopback-off muss funktional und digest-seitig die Alpha.7-Baseline reproduzieren

## P1 — Multirate Scheduler

- [ ] Deterministischen `MultirateScheduler` in die bestehende Runtime integrieren
- [ ] SNN-Tick unverändert lassen; Multirate als übergeordnete Kontrollschicht implementieren
- [ ] FAST-Layer mit Default `100 Hz` einführen
- [ ] MEDIUM-Layer mit Default `10 Hz` einführen
- [ ] SLOW-Layer mit Default `1 Hz` einführen
- [ ] VERY_SLOW/ADAPTIVE-Layer optional und standardmäßig deaktiviert vorbereiten
- [ ] `logical_time` als wissenschaftlichen Default implementieren
- [ ] `wall_clock` nur explizit klassifiziert im Operator Mode zulassen
- [ ] `catch_up_policy` mit `drop`, `catch_up`, `single_latest` implementieren
- [ ] Effektive Ausführungsticks aller Layer protokollieren
- [ ] Frequenzabbildung ohne driftende Float-Zeit implementieren
- [ ] Beispiel verifizieren: `dt_ms=1.0`, FAST=100 Hz -> FAST alle 10 Ticks
- [ ] Beispiel verifizieren: `dt_ms=0.5`, FAST=100 Hz -> FAST alle 20 Ticks

## P1 — Massive Parallelität ohne Determinismusverlust

- [ ] `parallel_mode=logical` als Default einführen
- [ ] Logische Parallelität klar von physischer Thread-/GPU-Parallelität trennen
- [ ] Keine unkontrollierte physische Parallelität im wissenschaftlichen Default aktivieren
- [ ] Für spätere physische Parallelisierung Digest-Gleichheit und kanonische Output-Reihenfolge als Pflicht definieren
- [ ] Sequenziell vs. parallel nur als eigenes Performance-/Equivalence-Treatment messen

## P1 — Scientific Settings Catalog

- [ ] `recursive_loopback.enabled` explizit in `build_parameters()` aufnehmen
- [ ] `recursive_loopback.self_causal_feedback_enabled` aufnehmen
- [ ] `recursive_loopback.prediction_horizon_ticks` aufnehmen
- [ ] `recursive_loopback.causal_window_ticks` aufnehmen
- [ ] `recursive_loopback.attribution_threshold` aufnehmen
- [ ] `recursive_loopback.uncertainty_threshold` aufnehmen
- [ ] `recursive_loopback.max_pending_actions` aufnehmen
- [ ] `recursive_loopback.persist_records` aufnehmen
- [ ] `recursive_loopback.feedback_gain` aufnehmen
- [ ] `multirate.enabled` aufnehmen
- [ ] `multirate.mode` aufnehmen
- [ ] `multirate.fast_hz` mit Default 100 Hz aufnehmen
- [ ] `multirate.medium_hz` mit Default 10 Hz aufnehmen
- [ ] `multirate.slow_hz` mit Default 1 Hz aufnehmen
- [ ] `multirate.very_slow_hz` mit Default 0 Hz aufnehmen
- [ ] `multirate.catch_up_policy` aufnehmen
- [ ] `multirate.parallel_mode` aufnehmen
- [ ] Alle neuen Werte `scientific_sensitive=True` markieren
- [ ] Restart-/Runtime-Mutability-Metadaten gemäß Architekturdokument setzen
- [ ] Confirmatory Mode gegen unregistrierte Änderungen absichern
- [ ] Pending-Change-Mechanik wiederverwenden, keine zweite Settings-Infrastruktur bauen
- [ ] Settings-Parameter-/Sensitive-/Restart-Zähler testen

## P1 — Config Validation

- [ ] Frequenzen <= 0 für aktive Layer fail-closed ablehnen
- [ ] Thresholds außerhalb `[0,1]` ablehnen
- [ ] Negative Horizon-/Window-Werte ablehnen
- [ ] Unbekannte `mode`, `catch_up_policy` und `parallel_mode` ablehnen
- [ ] `feedback_gain` auf dokumentierten Bereich begrenzen
- [ ] Effektiven Observer-Mode sichtbar melden, wenn Feedback deaktiviert oder Gain 0 ist

## P1 — Persistence, Provenance und Dashboard

- [ ] Efference Copies, Predictions, Observed Effects und Attributions persistent im korrekten Scope speichern
- [ ] Action-/Loopback-Records mit Experiment-ID, Git SHA, Tick und Digests verknüpfen
- [ ] Layer Execution Timeline im Experimentmanifest bzw. DATA-Artefakt speichern
- [ ] Effektive Loopback-/Multirate-Konfiguration vollständig in Run-Metadaten persistieren
- [ ] Read-only Dashboard-Metriken für Loopback-Status, Pending Actions, letzte Attribution, Confidence und Prediction Error ergänzen
- [ ] Effektive FAST/MEDIUM/SLOW-Frequenzen und letzte Ausführungsticks anzeigen
- [ ] Keine synthetischen Dashboardwerte erzeugen, wenn Runtime nichts publiziert

## P2 — Tests

- [ ] Eigene Aktion + erwarteter Effekt -> `SELF_CAUSED`
- [ ] Identischer Effekt ohne eigene Aktion -> `EXTERNAL_CAUSE`
- [ ] Eigene Aktion ohne Wirkung -> klar definierte `NO_EFFECT`/`UNCERTAIN`-Regel
- [ ] Eigene Aktion + externe Ursache -> `MIXED`
- [ ] Verzögerter Effekt innerhalb Window korrekt attribuieren
- [ ] Effekt außerhalb Window nicht selbst attribuieren
- [ ] Fehlende Beobachtung -> `UNCERTAIN`
- [ ] Loopback disabled -> Alpha.7-Baseline identisch
- [ ] Feedback Gain 0 -> keine Rückwirkung auf SNN-State
- [ ] Replay -> identische Attribution-Digests
- [ ] FAST=100 Hz deterministisch testen
- [ ] Alle neuen Settings im Scientific Settings Catalog testen
- [ ] Confirmatory Pending-Change-Regeln testen
- [ ] Ungültige Config fail-closed testen

## SCIENCE — neue Preregistrierungen

### EXP-SELF-0001 — Self vs External Causation

- [ ] Forschungsfrage und Hypothesen preregistrieren
- [ ] Own-action / expected-effect Bedingung definieren
- [ ] External-identical-effect Bedingung definieren
- [ ] Blocked-own-effect Bedingung definieren
- [ ] Mixed-cause Bedingung definieren
- [ ] Delayed-observation Bedingung definieren
- [ ] Missing-observation Bedingung definieren
- [ ] Attribution Accuracy als primäre Metrik definieren
- [ ] False Self-Attribution und False External-Attribution definieren
- [ ] Uncertainty Calibration und Attribution Latency definieren
- [ ] Keine EVID erzeugen, bevor Clean Freeze, unabhängige Runs und Review abgeschlossen sind

### EXP-RATE-0001 — Multirate Ablation

- [ ] Single-rate Baseline definieren
- [ ] FAST 10 Hz Treatment definieren
- [ ] FAST 50 Hz Treatment definieren
- [ ] FAST 100 Hz Treatment definieren
- [ ] FAST 200 Hz Treatment definieren
- [ ] FAST 100 Hz ohne MEDIUM/SLOW definieren
- [ ] Default Multirate Stack definieren
- [ ] Attribution Latency, Task Success und Stability messen
- [ ] CPU/RAM/Storage-Kosten messen
- [ ] Deterministic Digest vergleichen
- [ ] Missed/Late Safety Signals messen
- [ ] Keine Frequenz vor experimenteller Evidenz als wissenschaftlich optimal bezeichnen

## Definition of Done

- [ ] Loopback-off reproduziert Alpha.7
- [ ] Neue Settings erscheinen im bestehenden Scientific Settings Workspace
- [ ] Keine neue parallele Settings-Infrastruktur
- [ ] Alle wissenschaftlichen Parameter sind provenance-gebunden
- [ ] Keine LLM-Schreibrechte auf kausale Klassifikation
- [ ] Alle Qualitätsgates grün
- [ ] `EXP-SELF-0001` und `EXP-RATE-0001` preregistriert
- [ ] Noch keine Aussage über Bewusstsein, subjektive Selbstreflexion oder biologische Gleichwertigkeit
