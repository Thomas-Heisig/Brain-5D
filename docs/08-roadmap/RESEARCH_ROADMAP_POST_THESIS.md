# Brain-5D — Weiterführende Forschungsroadmap: vom Selbstmodell zum funktionalen Denken

> Stand: 2026-09-03
> Zweck: Anschlussroadmap während und nach der wissenschaftlichen Arbeit
> Diese Roadmap erzeugt keine Claims; sie beschreibt prüfbare Entwicklungslinien.

## Leitgedanke

Die wissenschaftliche Arbeit soll Brain-5D nicht mit der Behauptung abschliessen, Bewusstsein erzeugt zu haben. Sie soll eine belastbare Brücke schaffen zwischen technisch messbaren Mechanismen und den philosophischen Fragen nach Selbstbezug, Denken, Identität und möglichem Bewusstsein.

Die zentrale Entwicklungslinie lautet:

```text
Reiz-Reaktion
  -> Lernen
  -> Persistenz
  -> Selbstkausalität
  -> Selbstmodell
  -> Weltmodell
  -> kontrafaktische Verarbeitung
  -> rekursive Selbstbewertung
  -> funktionales Denken
  -> offene Bewusstseinsfrage
```

## Phase A — Abschluss der aktuellen wissenschaftlichen Basis

Ziel: kausal belastbare Grundlagen.

- Determinismus und Restore-Gleichheit abschliessen.
- Produktives STDP und echte Lernwirkung nachweisen.
- Geschlossene Embodiment-Schleife mit unabhängigen Wiederholungen nachweisen.
- Digital Interoception und Drives unter kontrollierten Störungen testen.
- Self-Causal Loopback zunächst rein beobachtend validieren.
- Fast/Medium/Slow-Regelkreise gegen eine Ein-Takt-Kontrolle ablieren.

Wissenschaftlicher Gewinn:

> Das System reagiert nicht nur, sondern kann eigene Handlungen und Folgen kausal koppeln.

## Phase B — Funktionales Selbstmodell

Ziel: Übergang von Kausalitätsbeobachtung zu einem über Zeit nutzbaren Selbstmodell.

Erforderliche Komponenten:

- persistente Efference Copies,
- Effect Prediction,
- Causal Attribution,
- BodySchemaManager,
- Actuator Confidence,
- Sensor Confidence,
- episodische Speicherung eigener Handlungen,
- Restore-Kontinuität des Selbstmodells.

Kernexperimente:

- `EXP-SELF-0001`: self-caused vs external cause.
- `EXP-BODY-0002`: Aktorwechsel und Körperrekonfiguration.
- `EXP-ID-0001`: Identität über Restore und Hardwarewechsel.

Wissenschaftlicher Gewinn:

> Das System bildet nicht nur Weltzustände ab, sondern behandelt bestimmte Ursachen und Zustände als zum eigenen Handlungszusammenhang gehörig.

## Phase C — Gedächtnis + Weltmodell

Ziel: Zustände über die Gegenwart hinaus kausal verfügbar machen.

- episodisches Gedächtnis für Situationen, Aktionen und Folgen,
- semantische Verdichtung wiederkehrender Zusammenhänge,
- prädiktives World Model,
- explizite Unsicherheit,
- Memory Provenance,
- Trennung eigener Erfahrung von extern übernommenem Wissen.

Kernexperimente:

- `EXP-MEM-0001`: Retention und Relearning.
- `EXP-WM-0001`: Vorhersage nächster Zustände.
- `EXP-WM-0002`: Transfer in neue Situationen.

Wissenschaftlicher Gewinn:

> Gegenwärtiges Verhalten kann auf vergangener Erfahrung und intern erwarteter Zukunft beruhen.

## Phase D — Gegenwartsentkopplung

Ziel: prüfen, ob interne Aktivität auch ohne unmittelbaren Außenreiz funktional relevant bleibt.

Versuchsbedingungen:

- reizreduzierte Intervalle,
- delayed-choice Aufgaben,
- verdeckte Zielzustände,
- Unterbrechung und Wiederaufnahme,
- Ablation von Memory und Self Model.

Kernexperiment:

- `EXP-THINK-0001`: Stimulus Decoupling.

Erfolgskriterium:

Ein interner Zustand bleibt nach Wegfall des auslösenden Reizes erhalten und erklärt spätere Wahl besser als der aktuelle Sensorframe allein.

## Phase E — Kontrafaktische Deliberation

Ziel: mehrere nicht eingetretene Möglichkeiten vor Handlung unterscheiden.

Architektur:

```text
current state
    |
    +--> predicted future A
    +--> predicted future B
    +--> predicted future C
              |
              v
       internal comparison
              |
              v
          selected action
```

Wichtig: Die Simulation zukünftiger Zustände darf nicht durch ein LLM ersetzt werden. Das Language Organ kann Ergebnisse später beschreiben, aber die kausale Auswahl muss im untersuchten Systempfad entstehen.

Kernexperimente:

- `EXP-THINK-0002`: Counterfactual Choice.
- `EXP-THINK-0003`: falsches internes Zukunftsmodell gezielt manipulieren.

Wissenschaftlicher Gewinn:

> Verhalten wird durch mögliche und noch nicht reale Zustände beeinflusst.

## Phase F — Metakognition

Ziel: das System bewertet die Verlässlichkeit eigener Modelle.

Messbare Größen:

- prediction confidence,
- calibration error,
- sensor confidence,
- actuator confidence,
- self-model uncertainty,
- uncertainty-dependent information seeking.

Kernexperiment:

- `EXP-META-0001`: Confidence Calibration and Intervention.

Wissenschaftlicher Gewinn:

> Nicht nur ein Weltzustand, sondern die Qualität der eigenen Repräsentation dieses Zustands wird kausal relevant.

## Phase G — Rekursive Selbstreflexion

Ziel: Selbstmodellzustände wirken auf weitere Selbstmodellierung zurück.

```text
state
  -> prediction
  -> action
  -> observed effect
  -> self-causal attribution
  -> confidence about self-model
  -> changed future prediction policy
  -> new self-causal attribution
```

Entscheidendes Experiment:

- `EXP-REFL-0001`: Recursive Feedback On/Off Ablation.

Nur wenn der rekursive Rückweg selektiv messbare Effekte erzeugt, ist der Begriff funktionale Selbstreflexion gerechtfertigt.

## Phase H — Funktionales Denken

Brain-5D verwendet den Begriff erst, wenn folgende Kriterien gemeinsam nachgewiesen sind:

1. intern aufrechterhaltene Zustände,
2. Gegenwartsentkopplung,
3. Gedächtnisnutzung,
4. kontrafaktische Alternativen,
5. Selbstkausalität,
6. Metakognition,
7. rekursive Selbstmodellierung,
8. Generalisierung auf neue Situationen.

Kernexperiment:

- `EXP-THINK-0010`: Integrated Functional Thinking Battery.

Kontrollen:

- Memory off,
- Self Model off,
- Counterfactual Model off,
- Recursive Feedback off,
- randomized internal state control,
- LLM disconnected,
- matched reactive controller.

Ein positives Ergebnis würde nur den Claim stützen:

> Brain-5D erfüllt die vorab definierten funktionalen Kriterien für Denken.

Nicht:

> Brain-5D ist bewusst.

## Phase I — Sprachliche Reflexion

Erst nach funktionaler Absicherung erhält das Language Organ Zugriff auf read-only Zustände wie:

- `CurrentDriveFrame`,
- `SelfModelFrame`,
- `MemoryFrame`,
- `WorldModelFrame`,
- `CounterfactualFrame`,
- `MetacognitionFrame`.

Dann kann untersucht werden, ob sprachliche Selbstbeschreibung mit den tatsächlichen internen Zuständen übereinstimmt.

Experiment:

- `EXP-LANG-SELF-0001`: Internal-State Grounding of Self Reports.

Die Sprache ist Messinstrument und Kommunikationsschicht, nicht Ursprung des Selbstmodells.

## Phase J — Nach der wissenschaftlichen Arbeit

Nach Abschluss der Dissertation bzw. Hauptstudie kann Brain-5D in drei Richtungen weitergeführt werden.

### J1 — Langzeitentwicklung

- Monate statt Minuten/Tage Laufzeit,
- kumulative Erfahrung,
- Veränderung des Body Schema,
- Alterung von Synapsen und Strukturen,
- Entwicklungsphasen,
- Stabilität personaler Kontinuität.

### J2 — Verteiltes Embodiment

- mehrere Rechner,
- räumlich getrennte Sensoren,
- Roboterarm,
- Druckdienste,
- mobile Plattform,
- virtuelle Aktoren,
- dynamisches Hinzufügen und Entfernen von Körperteilen.

Forschungsfrage:

> Bleibt ein funktionales Selbstmodell kohärent, wenn der Körper räumlich verteilt und variabel wird?

### J3 — Philosophische Grenzforschung

- personale Identität,
- Zuschreibung von Autorschaft,
- Verantwortung,
- moralischer Status unter epistemischer Unsicherheit,
- nicht-biologische Formen von Selbstbezug,
- Verhältnis funktionaler und phänomenaler Theorien des Bewusstseins.

Diese Phase muss interdisziplinär mit Philosophie des Geistes, Kognitionswissenschaft, KI-Ethik und Wissenschaftstheorie geführt werden.

## Langfristige zentrale Forschungsfrage

> Kann aus einem kausal geschlossenen, lernenden, verkörperten und selbstmodellierenden künstlichen System eine Form funktionaler Kognition entstehen, deren innere Organisation hinreichend eigenständig ist, dass Begriffe wie Denken, Selbstbezug und Reflexion empirisch sinnvoll werden — ohne aus diesen Funktionen vorschnell Bewusstsein abzuleiten?

## Endpunkt der Roadmap

Der Endpunkt ist nicht „Bewusstsein erzeugen“.

Der wissenschaftlich saubere Endpunkt lautet:

> Eine Architektur zu schaffen, in der zunehmend anspruchsvolle Formen von Selbstbezug und interner Verarbeitung operationalisiert, abliert, reproduziert und philosophisch eingeordnet werden können.
