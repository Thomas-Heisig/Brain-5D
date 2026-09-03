# Implementation Prompt — Alpha.8 Recursive Causal Loopbacks & Multirate Control

Du arbeitest ausschließlich im Repository `Thomas-Heisig/Brain-5D`.

## Ziel

Implementiere für Brain-5D eine **rekursive, kausal überprüfbare Selbstursachen-Schleife** sowie eine **konfigurierbare Multirate-Steuerung** mit schnellen und langsamen Ebenen, ohne die wissenschaftliche Auswertbarkeit, den bestehenden SNN-Core oder die Alpha.7-Kausalgrenzen zu beschädigen.

Die Funktion soll nicht „Bewusstsein“ simulieren und keine menschliche Selbstreflexion behaupten. Gemeint ist ausschließlich eine technische, messbare Fähigkeit:

```text
Ich habe Aktion A ausgelöst
-> ich erwarte Effekt E
-> ich beobachte Effekt O
-> E und O werden verglichen
-> Ergebnis = SELF_CAUSED / EXTERNAL_CAUSE / MIXED / UNCERTAIN / NO_EFFECT
-> dieses Ergebnis kann als neuer, typisierter Input in spätere Entscheidungen einfließen
```

Nutze `docs/02-architecture/RECURSIVE_CAUSAL_LOOPBACKS.md` als verbindliche Architekturspezifikation.

## Unveränderbare wissenschaftliche Grenzen

1. Der SNN-Core erhält **keine direkten Abhängigkeiten** zu Browsern, Kameras, Aktoren, LLMs oder Betriebssystemdiensten.
2. Rewards bleiben ausschließlich aus `EnvironmentObservation` bzw. einem deterministischen `TaskOutcomeVerifier` ableitbar.
3. Das Language Organ / LLM darf Kausalitätsdaten lesen und beschreiben, aber **niemals** `SELF_CAUSED`, Reward, Gewichte, Struktur oder Experimentzustand schreiben.
4. Fehlende Sensorwerte dürfen niemals als erfolgreicher Effekt interpretiert werden.
5. `recursive_loopback.enabled=false` muss das bisherige Alpha.7-Verhalten funktional unverändert lassen.
6. Scientific / Confirmatory Runs müssen deterministisch und replaybar bleiben.
7. Wall-clock-Verhalten darf Operator Mode unterstützen, aber wissenschaftliche Runs verwenden standardmäßig `logical_time`.
8. Parallelisierung darf die kanonische Reihenfolge, Digests oder Ergebnisse nicht verändern.

## Bestehende Architektur weiterverwenden

Nutze und erweitere insbesondere:

- `src/experience/engine.py`
- `src/experience/composition.py`
- `src/embodiment/models.py`
- `src/embodiment/controlled.py`
- `src/embodiment/audit.py`
- `src/embodiment/connections.py`
- `src/controller/runtime_controller.py` bzw. den vorhandenen Runtime-Hook-Mechanismus
- `src/dashboard/health_builder.py`
- `src/dashboard/models.py`
- Scientific Settings / Pending-Change-Mechanik
- Experiment Recorder / Manifest / Provenance
- Scientific Integrity Gate

Keine zweite parallele Settings-Infrastruktur bauen.

## Teil A — Self-Causal Loopback

Erzeuge ein neues Paket, vorzugsweise:

```text
src/self_causality/
    __init__.py
    models.py
    predictor.py
    comparator.py
    model.py
    loopback.py
```

### Datenmodelle

Implementiere immutable / typed Dataclasses für mindestens:

- `EfferenceCopy`
- `EffectPrediction`
- `ObservedEffect`
- `CausalAttribution`
- `CausalAttributionClass`
- optional `PredictionError`

`CausalAttributionClass`:

```text
SELF_CAUSED
EXTERNAL_CAUSE
MIXED
UNCERTAIN
NO_EFFECT
```

Alle wissenschaftlich relevanten Records müssen deterministisch serialisierbar und digestierbar sein.

### Ablauf

Vor jeder autorisierten Aktion:

1. stabile `command_id` erzeugen;
2. Efference Copy anlegen;
3. erwartete Effekte registrieren;
4. Prediction Horizon und Attribution Window registrieren.

Nach der Aktion:

1. unabhängige Sensor-/Environment-Daten erfassen;
2. erwartete und beobachtete Effekte zeitlich ausrichten;
3. Match Score und Temporal Score berechnen;
4. alternative Ursache berücksichtigen;
5. Attribution erzeugen;
6. Confidence explizit speichern;
7. Ergebnis persistieren/auditieren;
8. optional als typisierten Feedback-Frame wieder in den Inputpfad einspeisen.

### Kein verstecktes Freitextdenken

Die Klassifikation muss aus numerischen/typisierten Daten entstehen. Freitext darf ausschließlich eine nachgelagerte Erklärung sein.

## Teil B — Recursive Feedback

Implementiere einen `SelfCausalLoopback`.

Er soll Attributionsergebnisse optional als neuen SensorFrame oder internen FeedbackFrame verfügbar machen.

Empfohlene Merkmale:

```text
self_caused_confidence
external_cause_confidence
mixed_cause_confidence
causal_uncertainty
prediction_error
actuator_model_confidence
sensor_reliability
```

`feedback_gain=0.0` bedeutet wissenschaftlich sauberer Observer Mode: Daten werden berechnet und protokolliert, aber nicht in das SNN zurückgeführt.

Erst bei `self_causal_feedback_enabled=true` und `feedback_gain>0` darf die Rückführung stattfinden.

## Teil C — Multirate Scheduler

Implementiere einen deterministischen Scheduler, vorzugsweise:

```text
src/runtime/multirate.py
```

oder in der bestehenden Runtime-Struktur, wenn dort bereits ein passender Ort existiert.

Konzept:

```text
SNN tick / event processing: bestehend, unverändert
FAST controller: default 100 Hz
MEDIUM controller: default 10 Hz
SLOW controller: default 1 Hz
VERY_SLOW: default disabled
```

100 Hz ist **keine neue globale SNN-Taktfrequenz**. Es ist die Default-Frequenz der schnellen Kontroll-/Interozeptions-/Causal-Matching-Schicht.

### Scheduler-Anforderungen

- `logical_time` und `wall_clock` unterscheiden;
- Scientific Runs standardmäßig `logical_time`;
- Layer separat aktivierbar;
- effektive Execution Ticks protokollieren;
- `catch_up_policy` implementieren: `drop`, `catch_up`, `single_latest`;
- keine driftende Float-Zeit verwenden, wenn eine tickbasierte rationale Abbildung möglich ist;
- bei inkompatiblen Frequenzen deterministische Phase-/Accumulator-Logik verwenden;
- Replay muss identische Layer-Ausführungen erzeugen.

## Teil D — Massive Parallelität

Keine unkontrollierte Thread-Parallelität als Standard einführen.

Trenne:

- `parallel_mode=logical`: kanonische logische Parallelität, Default;
- spätere optionale physische Parallelität nur bei Digest-Gleichheit.

Für Alpha.8 genügt `logical` vollständig. Zusätzliche physische Modi dürfen vorbereitet, aber nicht als wissenschaftlicher Default aktiviert werden.

## Teil E — Settings Catalog

Erweitere den bestehenden kanonischen Parameterkatalog in `src/dashboard/health_builder.py`.

Mindestens diese Parameter müssen explizite `ParameterSchema`-Einträge mit Beschreibung, Grenzen und wissenschaftlicher Sensitivität erhalten:

```yaml
recursive_loopback:
  enabled: false
  self_causal_feedback_enabled: false
  prediction_horizon_ticks: 25
  causal_window_ticks: 50
  attribution_threshold: 0.75
  uncertainty_threshold: 0.40
  max_pending_actions: 256
  persist_records: true
  feedback_gain: 0.0

multirate:
  enabled: false
  mode: logical_time
  fast_hz: 100.0
  medium_hz: 10.0
  slow_hz: 1.0
  very_slow_hz: 0.0
  catch_up_policy: single_latest
  parallel_mode: logical
```

Vorgaben:

- alle sind `scientific_sensitive=True`;
- `enabled`, `mode`, `parallel_mode`, `catch_up_policy`, `max_pending_actions`, `persist_records` benötigen Restart bzw. neuen Run;
- Hz-/Threshold-/Window-/Gain-Werte dürfen im Operator/Exploratory Mode pending geändert werden;
- Confirmatory Mode darf keine unregistrierte Laufzeitänderung zulassen;
- Settings UI muss die Parameter automatisch über den bestehenden Katalog anzeigen;
- Parameterzahl-/Sensitive-/Restart-Zähler müssen korrekt bleiben.

## Teil F — Configuration Validation

Erweitere den Config-Loader / Validator so, dass fehlerhafte Werte fail-closed abgewiesen werden.

Beispiele:

- `fast_hz <= 0` bei aktiviertem FAST-Layer -> Fehler;
- `medium_hz > fast_hz` -> standardmäßig Fehler oder explizit dokumentierte Erlaubnis;
- Thresholds außerhalb `[0,1]` -> Fehler;
- negative Window-Ticks -> Fehler;
- unbekannter `mode`, `catch_up_policy` oder `parallel_mode` -> Fehler;
- Feedback aktiviert bei `feedback_gain <= 0` -> erlaubt, aber effektiv observer-only und sichtbar melden;
- `feedback_gain > 1` nur wenn explizit begründet; Default Max = 1.0.

## Teil G — Dashboard / Telemetry

Dashboard nur mit real publizierten Werten erweitern.

Empfohlene read-only Metriken:

```text
loopback.enabled
loopback.pending_actions
loopback.last_classification
loopback.last_confidence
loopback.prediction_error
loopback.self_attribution_rate
loopback.uncertainty_rate
multirate.fast_hz_effective
multirate.medium_hz_effective
multirate.slow_hz_effective
multirate.last_fast_tick
multirate.last_medium_tick
multirate.last_slow_tick
```

Keine erfundenen Dashboard-Werte.

## Teil H — Persistence & Provenance

Speichere wissenschaftlich relevante Loopback-Daten in Experiment-Scopes.

Mindestens:

- effektive Config;
- Efference Copies;
- Effect Predictions;
- Observed Effects;
- Causal Attributions;
- Layer Execution Timeline;
- Digests;
- Source / Sensor provenance;
- Experiment-ID;
- Git SHA;
- Replay-Modus.

Operator- und Experiment-Storage bleiben getrennt.

## Teil I — Tests

Ergänze Unit-, Integration- und Regressionstests.

Pflichtfälle:

1. eigene Aktion + erwarteter Effekt -> `SELF_CAUSED`;
2. Effekt ohne eigene Aktion -> `EXTERNAL_CAUSE`;
3. eigene Aktion ohne Effekt -> `NO_EFFECT` oder `UNCERTAIN` gemäß klarer Regel;
4. eigene + externe Ursache -> `MIXED`;
5. verspäteter Effekt innerhalb Window -> korrekt attribuiert;
6. Effekt außerhalb Window -> nicht selbst attribuieren;
7. fehlender Sensor -> `UNCERTAIN`;
8. Loopback disabled -> Alpha.7-Baseline identisch;
9. Feedback gain 0 -> keine SNN-Rückwirkung;
10. Replay -> identische Attribution-Digests;
11. FAST=100 Hz Scheduling deterministisch;
12. 1-ms-SNN-Tick + 100-Hz-FAST-Layer -> FAST alle 10 logischen ms;
13. 0.5-ms-SNN-Tick + 100-Hz-FAST-Layer -> FAST alle 20 Ticks;
14. Settings-Katalog enthält alle neuen Parameter;
15. scientific-sensitive Flags stimmen;
16. Confirmatory Pending-Change-Regeln greifen;
17. ungültige Frequenzen/Thresholds werden abgewiesen.

## Teil J — Experimente vorbereiten, aber keine Evidenz behaupten

Preregistriere:

### `EXP-SELF-0001`

Self vs External Causation.

Bedingungen:

- own action / expected effect;
- external identical effect;
- blocked own effect;
- mixed cause;
- delayed observation;
- missing observation.

Metriken:

- attribution accuracy;
- false self-attribution;
- false external-attribution;
- uncertainty calibration;
- latency;
- adaptation over trials.

### `EXP-RATE-0001`

Multirate Ablation.

Bedingungen mindestens:

- single-rate baseline;
- FAST 10 Hz;
- FAST 50 Hz;
- FAST 100 Hz;
- FAST 200 Hz;
- FAST 100 Hz ohne Medium/Slow;
- vollständiger Default Multirate Stack.

Metriken:

- attribution latency;
- task success;
- stability;
- CPU/RAM/storage cost;
- deterministic digest;
- missed/late safety signals.

Keine EVID-Ausgabe oder wissenschaftliche Behauptung erzeugen, bevor Clean Freeze, unabhängige Runs und Review erfüllt sind.

## Teil K — Qualitätsreihenfolge

Vor neuer Feature-Implementierung zuerst den bestehenden roten CI-Stand reparieren:

1. Black auf die aktuell gemeldeten Dateien anwenden;
2. sechs mypy-Fehler beheben;
3. komplette Testsuite lokal;
4. Black/Ruff/Pylint/mypy/Pyright;
5. Scientific Integrity Gate;
6. dann Recursive Loopback implementieren;
7. erneut vollständige Suite;
8. Dokumentation, TODO, Roadmap und Changelog synchronisieren.

Nicht einfach Typchecks mit `ignore` unterdrücken, sofern eine saubere Typmodellierung möglich ist.

## Definition of Done

Die Integration ist abgeschlossen, wenn:

- bestehende Alpha.7-Tests unverändert bestehen;
- alle neuen Unit-/Integrationstests grün sind;
- Python 3.11/3.12/3.13 grün sind;
- Black, Ruff, Pylint, mypy, Pyright grün sind;
- Scientific Integrity Gate grün ist;
- Loopback-off den Baseline-Digest reproduziert;
- neue Settings im Scientific Settings Workspace sichtbar sind;
- Experimente Loopback-/Multirate-Konfiguration vollständig protokollieren;
- kein LLM kausale Schreibrechte besitzt;
- `EXP-SELF-0001` und `EXP-RATE-0001` preregistriert, aber noch nicht als Evidenz ausgegeben sind.
