# Brain-5D — TODO: Learning Preparation Studio

> Stand: 2026-09-03
> Ergänzt die kanonische Roadmap um einen eigenen Lern-Arbeitsbereich.
> Leitregel: **KI darf Lernen vorbereiten, aber keine neuronalen Muster oder Rewards schreiben.**

## P0 — Guarded Preparation Foundation

- [x] `LearningObjective` als messbares Lernziel ohne neuronale Zielrepräsentation definieren
- [x] `LearningSourceRef` mit Digest, Herkunft, Trust und Train/Validation/Holdout-Partition definieren
- [x] `LearningPreparationProposal` als digestgebundenen, nicht ausführenden Contract implementieren
- [x] AI-assisted Proposal nur mit `ai_interaction_id`-Provenienz erlauben
- [x] `PreparedLearningPlan` mit explizitem `runtime_authority = none` implementieren
- [x] `LearningPreparationGuard` gegen Gewichte, Spikepatterns, Strominjektionen, Eligibility- und Rewardwerte fail-closed implementieren
- [x] Unit-Tests für Human-/AI-Proposals und verbotene Mutation-Payloads ergänzen

## P0 — Learning Workspace

- [x] Eigenen `LEARNING`-Workspace in das bestehende Operator Dashboard integrieren
- [x] Reale `LearningMetrics` für Engine, STDP, Reward, Updates, Pending Rewards und Laufzeit anzeigen
- [x] Learning-Ziel, Erfolgskriterium, Quellen/Provenienz und Kontrollen als Vorbereitungseingaben anzeigen
- [x] Bestehenden read-only Research Assistant als KI-Vorbereitungshelfer anbinden
- [x] KI-Ausgabe sichtbar als `AI PROPOSAL · NOT APPLIED` kennzeichnen
- [x] Keine Apply-/Execute-Schaltfläche für KI-Proposals bereitstellen
- [x] Pre-/Post-Learning-Diagnostik mit Baseline, Impulse Probe, Temporal Reference und Holdout sichtbar vorbereiten
- [x] Statisches Frontend-Wiring gegen versehentliche Execute-/Apply-Pfade testen

## P1 — Persistente Lernpläne

- [ ] `PreparedLearningPlan` im Experiment-Storage persistieren
- [ ] Proposal-Digest, Approval, AI-Provenienz, Quellen-Digests und effektive Settings im Manifest registrieren
- [ ] Plan-Status `draft -> proposed -> approved -> registered -> running -> evaluated -> archived` einführen
- [ ] Änderungen an einem approved/registered Plan nur über neue Revision zulassen
- [ ] Confirmatory Runs gegen nachträgliche Planänderungen sperren

## P1 — Structured Learning Preparation API

- [ ] `/api/learning/preparation` als typisierte, nicht ausführende API ergänzen
- [ ] GET für aktuellen Draft/Plan und Status
- [ ] POST ausschließlich für Proposal-Erstellung und menschliche Approval-Metadaten
- [ ] Keine API-Funktion zum direkten Setzen von Gewichten, Spikes, Currents oder Rewards zulassen
- [ ] AI-Payload serverseitig erneut durch `LearningPreparationGuard` validieren; Frontend-Prompt allein ist keine Sicherheitsgrenze
- [ ] Scientific AI Firewall und LearningPreparationGuard gemeinsam testen

## P1 — Knowledge / Environment → Learning Preparation

- [ ] `KnowledgeItem` ausschließlich über provenance-gebundene `LearningSourceRef` in Lernpläne aufnehmen
- [ ] Sensor-/Environment-Quellen ebenfalls als digestierbare Source References abbilden
- [ ] Train/Validation/Holdout-Leakage automatisiert prüfen
- [ ] Curriculum auf Aufgaben-/Environment-Ebene definieren, nicht als gewünschte Spikefolge
- [ ] Schwierigkeitssteigerung als kontrollierten Treatment-Faktor protokollieren
- [ ] KI darf Curriculum-Vorschläge erstellen; menschliche Freigabe und Protokollregistrierung bleiben erforderlich

## P1 — Execution Boundary

- [ ] Vorbereitung und Ausführung strikt als zwei getrennte Services führen
- [ ] Execution nur aus `PreparedLearningPlan` + registriertem Workflow erlauben
- [ ] LearningEngine erhält weiterhin nur reale Spike-/Eligibility-/Reward-Ereignisse aus den vorhandenen Runtime-Grenzen
- [x] `TaskOutcomeVerifier` ist auf `origin/main` als deterministische technische Quelle für Task-Erfolg/Reward implementiert; fehlende Environment-Beobachtungen bleiben UNKNOWN
- [ ] Learning Studio explizit an den bestehenden `TaskOutcomeVerifier` anbinden, ohne einen alternativen Rewardpfad zu eröffnen
- [ ] LLM, Research Assistant und Language Organ von direkter Reward-Autorität ausschließen
- [ ] Reward-Provenienz je Episode persistieren

## P1 — Pre / Post Learning Instrumentation

- [ ] Pre-Learning Task Baseline automatisch mit Plan-Digest verknüpfen
- [ ] optionale `NetworkImpulseProbe` vor Lernen als sekundäre Diagnose speichern
- [ ] optionale `TemporalStateFrame`-Referenzen vor Lernintervall speichern
- [ ] Post-Learning Task Evaluation unter identischen Bedingungen durchführen
- [ ] Post-Learning `NetworkResponseSignature` mit Pre-Probe vergleichen
- [ ] TemporalComparator für Drift/Discrepancy verwenden
- [ ] Änderungen an Impulsantwort oder Netzwerkzustand niemals allein als Lernerfolg klassifizieren

## P2 — Adaptive Curriculum Preparation

- [ ] Curriculum-Progression aus gemessener Aufgabenleistung ableiten
- [ ] Schwierigkeitsanpassung zunächst deterministisch, später als AI proposal-only Treatment vergleichen
- [ ] `curriculum_source = deterministic | human | ai_proposal` im Manifest erfassen
- [ ] Counterfactual Twin Runs mit identischem Zustand für unterschiedliche Curricula ermöglichen
- [ ] prüfen, ob AI-vorbereitete Curricula gegenüber deterministischen/humanen Baselines messbaren Vorteil bieten

## SCIENCE — Productive Learning

- [ ] `EXP-LEARN-0001`: Baseline → Learning → identische Post-Evaluation preregistrieren
- [ ] mindestens Learning-On und Learning-Off Control verwenden
- [ ] Pre/Post-Taskleistung als primäre Metrik definieren
- [ ] Weight-/Impulse-/Temporal-Änderungen nur als sekundäre Mechanismusmetriken behandeln
- [ ] Holdout-Generalisation messen
- [ ] unabhängige Seeds und Replikation vor positivem Claim

## SCIENCE — AI-Assisted Preparation

- [ ] `EXP-CURR-0001`: Human vs deterministic vs AI-prepared curriculum vergleichen
- [ ] identische SNN-Ausgangszustände und Lernregeln verwenden
- [ ] AI darf nur Vorbereitungsplan beeinflussen, nicht Lernmechanismus oder Bewertung
- [ ] AIExposure und CausalTaint für den vorbereiteten Treatmentpfad registrieren
- [ ] prüfen, ob ein möglicher Vorteil aus besserer Aufgabenstruktur statt aus versteckter Information/Leakage stammt

## Claim-Grenze

Erlaubte technische Aussagen nach entsprechender Evidenz können beispielsweise sein:

- „Die definierte Lernbedingung verbessert die Holdout-Aufgabenleistung gegenüber Learning-Off.“
- „Ein AI-vorbereiteter Curriculum-Plan verbessert unter identischen Lernregeln die Sample Efficiency gegenüber einer preregistrierten Baseline.“
- „Die Impulsantwort verändert sich nach erfolgreichem Lernen reproduzierbar.“

Nicht zulässig allein aus diesen Ergebnissen:

- „Das System versteht die Daten.“
- „Die KI hat dem SNN das Muster beigebracht.“
- „Mehr Spikes bedeuten mehr Lernen.“
- „Rekurrenz ist Selbstreflexion.“
- „Eine bestimmte Neuronen-/Synapsenzahl ist eine kritische Masse für Denken.“

## Langfristiges Ziel

Der Learning Workspace soll schließlich den gesamten nachvollziehbaren Pfad zeigen:

```text
Lernziel
  -> Quellen / Environment
  -> Proposal
  -> menschliche Freigabe
  -> Pre-Baseline
  -> registrierter Experience Run
  -> Brain-5D LearningEngine
  -> Post-Evaluation
  -> Holdout / Generalisierung
  -> Mechanismusdiagnostik
  -> DATA / EVID
```

Die interne Repräsentation bleibt dabei Ergebnis des lernenden Systems, nicht ein von KI oder Operator vorgegebenes Zielmuster.
