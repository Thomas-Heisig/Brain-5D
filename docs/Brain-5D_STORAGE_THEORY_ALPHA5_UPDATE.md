# Brain-5D Storage Theory --- Alpha.5 Update

**Projekt:** Brain-5D\
**Stand:** v0.5.0-alpha.5\
**Status:** Ergänzung zur bestehenden Speicher-Theorie

## 1. Einordnung

Das bestehende Speicher-Leitprinzip bleibt unverändert:

**Punkt + Graph + Feld + Zeit**

Alpha.5 präzisiert insbesondere die Zeit- und Graphschicht. Strukturelle
Änderungen an Neuronen und Synapsen werden nicht mehr nur als momentaner
Netzzustand betrachtet, sondern als eigene persistente Ereignisklasse.

## 2. Persistenzvertrag ab Alpha.5

``` text
.b5d Snapshot
      +
State Delta Journal
      +
Structural Journal
      +
Runtime Checkpoint
```

Die vier Ebenen haben getrennte Verantwortlichkeiten:

-   `.b5d Snapshot`: Basistopologie und gespeicherter neuronaler
    Zustand.
-   State Delta Journal: Änderungen vorhandener Zustandswerte.
-   Structural Journal: Änderungen der Topologie.
-   Runtime Checkpoint: Fortsetzungszustand der laufenden Simulation.

Damit wird die frühere abstrakte Zeit-/Delta-Schicht in zwei semantisch
verschiedene Änderungsarten getrennt: Zustandsänderung und
Strukturänderung.

## 3. Structural Journal

Das Structural Journal ist append-only. Es protokolliert mindestens:

-   `NEURON_ADD`
-   `NEURON_REMOVE`
-   `SYNAPSE_ADD`
-   `SYNAPSE_REMOVE`

Ein persistenter Eintrag besitzt eine monotone Sequenznummer und wird
durch Commit-/CRC-Mechanismen gegen unvollständige bzw. beschädigte
Schreibvorgänge abgesichert.

Wichtig ist die Trennung:

``` text
Zustand eines vorhandenen Objekts -> Delta Journal
Existenz/Topologie eines Objekts  -> Structural Journal
```

## 4. Persistentes Undo

Undo löscht keine Historie. Stattdessen wird eine inverse strukturelle
Operation als neues Ereignis angehängt.

``` text
NEURON_ADD   -> NEURON_REMOVE
SYNAPSE_ADD  -> SYNAPSE_REMOVE
SYNAPSE_REMOVE -> SYNAPSE_ADD
```

Für die Rekonstruktion einer gelöschten Struktur müssen die zur
Wiederherstellung erforderlichen Daten im strukturellen Ereignis
erhalten bleiben.

Damit bleibt die Historie auditierbar und Replay-fähig.

## 5. Restore-Reihenfolge

Der aktuelle Restore-Vertrag lautet:

``` text
1. .b5d Snapshot laden
2. committed State-Deltas anwenden
3. committed Structural Records replayen
4. Runtime Checkpoint restaurieren
5. Konsistenz prüfen
6. Simulation fortsetzen
```

Der strukturelle Replay liegt bewusst vor dem Runtime-Checkpoint, damit
der Fortsetzungszustand auf der erwarteten Topologie aufsetzt.

## 6. Snapshot-Grenze

Ein Operator-Snapshot soll nicht mitten in einer strukturellen Mutation
entstehen. Die Laufzeit verarbeitet Snapshot-Anforderungen deshalb an
einer sicheren Batch-Grenze.

Persistenzreihenfolge:

``` text
Structural Journal flush/commit
        ↓
.b5d Snapshot
        ↓
Runtime Checkpoint
        ↓
Operator-/Dashboard-Status
```

## 7. Bezug zum theoretischen optischen Speicher

Das theoretische optische Modell bleibt ein Forschungsmodell. Alpha.5
ändert nicht die Annahme, dass ein späterer physischer Adapter die
logische Brain-5D- Semantik auf ein anderes Medium abbilden kann.

Der digitale Zwilling wird jedoch präziser:

``` text
Punkt  -> lokaler Neuronenzustand
Graph  -> Synapsen und Beziehungen
Feld   -> geteilte elektrische/chemische/modulatorische Größen
Zeit   -> State Delta + Structural Journal + Checkpoint
```

Damit ist die Software nicht von der Realisierung eines optischen
Mediums abhängig.

## 8. Selbstorganisation und Manipulator

Die bestehende Theorie, Selbstorganisation nicht im Storage selbst
auszuführen, wird durch Alpha.5 konkretisiert:

``` text
HomeostasisSignal
    -> SelfOrganizationPolicy
    -> StructuralProposal
    -> Coordinator / Approval
    -> StructuralPlasticityEngine
    -> Manipulator
    -> NeuralNetwork
    -> StructuralJournal
```

Der Manipulator bleibt die kontrollierte Mutationsgrenze. Persistenz
beobachtet und protokolliert Änderungen, entscheidet aber nicht selbst
über Wachstum oder Pruning.

## 9. Sicherheitsstatus

Standardmäßig gilt weiterhin:

``` yaml
self_organization:
  enabled: false
  dry_run: true
  auto_approval: false
  allow_neuron_pruning: false
```

Damit ist das Structural Journal kein Mechanismus zur Freigabe autonomer
Strukturänderungen, sondern deren persistente Nachvollziehbarkeit.

## 10. Übergang zu Alpha.6

Alpha.6 sollte die bereits persistierbare Struktur langfristig
stabilisieren:

-   chronische statt momentaner Strukturreize,
-   regionale 5D-Druckgrößen,
-   Struktur-/Synapsenalter,
-   Mindestlebensdauer,
-   Growth Budgets,
-   strukturelle Kosten,
-   Hysterese,
-   Anti-Oszillation,
-   regionale Neurogenese-/Pruning-Drücke.

Das Ziel ist morphologische Selbstregulation, nicht unbeschränkte
Autonomie.
