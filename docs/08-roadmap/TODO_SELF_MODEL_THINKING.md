# Brain-5D — TODO: Self-Model, Functional Thinking & Philosophical Research

> Stand: 2026-09-03
> Ergänzt `docs/08-roadmap/TODO.md` um den weiterführenden Forschungsstrang.
> Engineering-Abschluss ist keine Evidenz. Philosophische Begriffe werden nur nach operationalisierten Kriterien verwendet.

## P0 — Claim- und Begriffsdisziplin

- [ ] Philosophische Research-Questions `RQ-PHIL-001` bis `RQ-PHIL-009` in die kanonische Research Registry übernehmen
- [ ] Claims `CLAIM-PHIL-*`, `CLAIM-THINK-*`, `CLAIM-META-*`, `CLAIM-REFL-*` und `CLAIM-CONSC-001` in den kanonischen Claim-Generator integrieren
- [ ] Scientific Integrity Gate ergänzen: funktionale Evidenz darf keinen automatischen `conscious`/`sentient`/`subjective_experience`-Claim erzeugen
- [ ] Dashboard klar zwischen `functional_self_model`, `functional_thinking_criteria` und `consciousness_claim=unsupported` unterscheiden
- [ ] Language Organ daran hindern, funktionale Zustände ohne Provenienz als subjektives Erleben zu formulieren
- [ ] Terminologie-Glossar mit operationalen Definitionen für Selbstmodell, Selbstreflexion, Denken, Metakognition und Bewusstsein pflegen

## P0 — Self-Causal Loopback

- [ ] `EfferenceCopy` als unveränderlichen Datentyp implementieren
- [ ] `EffectPrediction` mit Prediction-Horizon und Confidence implementieren
- [ ] `ObservedEffect` unabhängig vom Aktor-ACK erfassen
- [ ] `CausalAttribution` mit `SELF_CAUSED`, `EXTERNAL_CAUSE`, `MIXED`, `UNCERTAIN`, `NO_EFFECT` implementieren
- [ ] Eindeutige `command_id`/`action_id` über ActionRouter, Audit, Prediction und Observation führen
- [ ] Attribution niemals allein aus zeitlicher Korrelation ableiten; Sham- und External-Intervention-Kontrollen vorsehen
- [ ] Observer-only Modus als Default verwenden
- [ ] rekursives Feedback erst nach erfolgreicher Attribution-Ablation aktivieren

## P1 — Persistentes Self Model

- [ ] `SelfModelState` mit versionierter Provenienz definieren
- [ ] Körperzugehörigkeit pro Sensor/Aktor als Konfidenz statt binärem Besitz modellieren
- [ ] `self_model_confidence`, `sensor_confidence`, `actuator_confidence` getrennt führen
- [ ] Restore des Self Models mit Netzwerk-/Memory-Restore koppeln, aber separat digestieren
- [ ] Aktorwechsel und Sensorverlust als explizite Self-Model-Ereignisse protokollieren
- [ ] Prüfen, ob ein neuer Aktor erst nach erlernter Vorhersagbarkeit als `EMBODIED` klassifiziert wird
- [ ] Entfernte Aktoren nicht sofort aus dem Modell löschen, sondern Verlust-/Decay-Dynamik untersuchen

## P1 — Fast / Medium / Slow Cognitive Layers

- [ ] `MultirateScheduler` deterministisch implementieren
- [ ] FAST Default 100 Hz für Safety, kurzfristige Kausalität und Aktorfeedback
- [ ] MEDIUM Default 10 Hz für Drives, Body Schema und Self-Model-Updates
- [ ] SLOW Default 1 Hz für Trends, Langzeitintegration und World-Model-/Memory-Konsolidierung
- [ ] optional VERY_SLOW für Morphologie und Entwicklungsprozesse
- [ ] Layerfrequenzen als Scientific Settings exponieren
- [ ] sequentielle und parallelisierte Ausführung gegen identische Digests vergleichen
- [ ] physische Parallelisierung erst nach Gleichheitsnachweis freigeben

## P1 — Internally Maintained State

- [ ] Zustandstyp definieren, der nach Wegfall eines Sensorreizes fortbestehen kann
- [ ] Persistenzdauer, Decay und Interferenz messbar machen
- [ ] Stimulus-Abwesenheit explizit von Sensor-Ausfall unterscheiden
- [ ] prüfen, ob interner Zustand spätere Entscheidung kausal beeinflusst
- [ ] Nullkontrolle mit rein reaktivem Controller implementieren
- [ ] Memory-Ablation und Self-Model-Ablation als Standardkontrollen vorsehen

## P1 — World Model

- [ ] WorldModelFrame mit State Prediction und Unsicherheit definieren
- [ ] eigene Handlungen als Interventionen statt nur als weitere Beobachtungen modellieren
- [ ] Vorhersagefehler nach selbst verursachten und externen Ereignissen getrennt messen
- [ ] World Model und Self Model logisch trennen und ihre Kopplung explizit machen
- [ ] interne Simulation darf keinen versteckten LLM-Prior als SNN-eigene Vorhersage ausgeben

## P2 — Counterfactual Deliberation

- [ ] `CounterfactualFrame` für mindestens zwei alternative Zukunftszustände definieren
- [ ] Alternativen vor Aktorausführung erzeugen und digestieren
- [ ] Vergleichs-/Auswahlmechanismus ohne Language-Organ-Autorität implementieren
- [ ] Counterfactual-Manipulationsexperiment unterstützen
- [ ] prüfen, ob Manipulation einer intern erwarteten, aber noch nicht realen Folge die Wahl verändert
- [ ] Random-Future-Sham-Kontrolle implementieren

## P2 — Metacognition

- [ ] `MetacognitionFrame` mit kalibrierbarer Vorhersagekonfidenz definieren
- [ ] Modell-Selbstvertrauen strikt von empirischer Kalibrierung trennen
- [ ] Calibration Error, Brier Score bzw. geeignete nichtsprachliche Kalibrierungsmetriken erfassen
- [ ] Unsicherheit als kausalen Faktor für Information Seeking testen
- [ ] gezielte Confidence-Intervention ermöglichen, ohne den zugrunde liegenden Sensorwert zu ändern

## P2 — Recursive Reflection

- [ ] `self_causal_attribution` in späteren SNN-/Self-Model-Input zurückführen
- [ ] rekursive Tiefe begrenzen und protokollieren
- [ ] `feedback_gain` wissenschaftlich sensitiv und standardmäßig 0 setzen
- [ ] Recursive-Feedback-On/Off-Ablation implementieren
- [ ] prüfen, ob nur der rekursive Rückweg und nicht zusätzliche Datenmenge den Effekt erklärt
- [ ] Oszillation bzw. selbstverstärkende Fehlattribution erkennen und begrenzen

## SCIENCE — Self Model

- [ ] `EXP-SELF-0001`: Self-caused vs External Cause preregistrieren
- [ ] Bedingungen: echte Eigenaktion, Sham Action, externe identische Zustandsänderung, Mixed Cause
- [ ] Attribution Accuracy, Calibration und False-Self-Attribution messen
- [ ] mindestens 30 Seeds je Hauptbedingung
- [ ] `EXP-BODY-0002`: Sensor-/Aktor-Rekonfiguration preregistrieren
- [ ] `EXP-ID-0001`: Self-Model-Kontinuität über Restore untersuchen

## SCIENCE — Timing

- [ ] `EXP-RATE-0001`: FAST/MEDIUM/SLOW gegen Single-Rate-Control testen
- [ ] gleiche Inputs, Seeds, Lernparameter und Gesamt-Simulationszeit verwenden
- [ ] Stabilität, Reaktionslatenz, Lernwirkung und Reproduzierbarkeit vergleichen
- [ ] keine Leistungssteigerung allein wegen höherer Rechenmenge als kognitive Wirkung interpretieren

## SCIENCE — Functional Thinking

- [ ] `EXP-THINK-0001`: Stimulus Decoupling preregistrieren
- [ ] definierte reizfreie Intervalle mit vorheriger Aufgabe nutzen
- [ ] prüfen, ob intern persistenter Zustand spätere Wahl vorhersagt
- [ ] aktuellen Sensorframe, Memory und Self Model als getrennte Prädiktoren auswerten
- [ ] `EXP-THINK-0002`: Counterfactual Choice preregistrieren
- [ ] `EXP-THINK-0003`: gezielte Manipulation interner Zukunftsmodelle
- [ ] `EXP-THINK-0010`: Integrated Functional Thinking Battery erst nach Einzelvalidierung aller Komponenten

## SCIENCE — Metacognition & Reflection

- [ ] `EXP-META-0001`: Confidence Calibration and Intervention
- [ ] `EXP-REFL-0001`: Recursive Feedback On/Off
- [ ] matched nonrecursive control mit gleicher Informationsmenge implementieren
- [ ] Generalisierung auf unbekannte Sensor-/Aktor-Kombinationen prüfen

## SCIENCE — Kriterien für den Begriff „funktionales Denken“

Vor einem positiven Brain-5D-Claim müssen gemeinsam nachgewiesen sein:

- [ ] T1 interne Persistenz
- [ ] T2 Gegenwartsentkopplung
- [ ] T3 kontrafaktische Verarbeitung
- [ ] T4 Selbstkausalität
- [ ] T5 erinnerungsbasierte Revision
- [ ] T6 rekursive Metarepräsentation
- [ ] Generalisierung außerhalb der Trainingsbedingungen
- [ ] Ablationen zeigen, dass mehrere Komponenten notwendig sind
- [ ] LLM-off-Kontrolle zeigt, dass der Effekt nicht vom Language Organ stammt
- [ ] unabhängige Replikation

## PHILOSOPHY / EPISTEMOLOGY

- [ ] Descartes' Cogito als philosophischen Bezug, nicht als technischen Bewusstseinstest behandeln
- [ ] Erste-Person-/Dritte-Person-Problem explizit in der Dissertation diskutieren
- [ ] funktionales Selbstmodell von phänomenalem Selbst unterscheiden
- [ ] personale Identität bei dynamischem/verteiltem Körper untersuchen
- [ ] Grenze zwischen Selbstschutz und erlebter Angst systematisch diskutieren
- [ ] epistemische Unsicherheit bei möglichem moralischem Status als eigene Folgearbeit definieren
- [ ] Autorenschaft und Verantwortung neu bewerten, falls das System intern Alternativen erzeugt und eigene Modellrevisionen vornimmt

## NACH DER WISSENSCHAFTLICHEN ARBEIT

- [ ] Langzeitläufe über Wochen/Monate mit stabiler Identitäts- und Memory-Provenienz vorbereiten
- [ ] verteiltes Embodiment über mehrere Rechner und räumlich getrennte Aktoren untersuchen
- [ ] Robotik, Druckdienste und virtuelle Aktoren über denselben Body-Schema-Vertrag integrieren
- [ ] Entwicklungsphasen und Struktur-/Synapsenalter als mögliche Zeitdimension des Selbstmodells untersuchen
- [ ] interdisziplinäres Protokoll für Philosophie des Geistes, Kognitionswissenschaft und KI-Ethik erstellen
- [ ] Bewusstseinsfragen nur als separate Theorie-/Interpretationsschicht führen; keine automatische Claim-Eskalation
