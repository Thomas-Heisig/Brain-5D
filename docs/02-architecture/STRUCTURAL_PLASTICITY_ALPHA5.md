# Brain-5D v0.5.0-alpha.5 --- Persistent Structural Plasticity

## Status

Alpha.5 verbindet kontrollierte strukturelle Plastizität mit
persistenter Nachvollziehbarkeit, Undo, Recovery und Operator-Kontrolle.

## Kontrollpfad

``` text
HomeostasisEngine
    -> HomeostasisSignal
    -> SelfOrganizationPolicy
    -> StructuralProposal
    -> SelfOrganizationCoordinator
       -> Reject
       -> Manual Approval
       -> Auto-Approval Policy
    -> StructuralPlasticityEngine
    -> Manipulator
    -> NeuralNetwork
    -> StructuralChangeRecord
    -> StructuralJournal
       -> Undo
       -> Recovery
       -> Structural Heatmap
    -> Operator Dashboard
```

## Architekturregeln

1.  Der Coordinator verändert das Netzwerk nicht direkt.
2.  Das Dashboard greift nicht auf private Netzwerk-/Engine-Interna zu.
3.  Mutation läuft über den Manipulator bzw. eine definierte Core-API.
4.  Undo ist ein neues inverses Ereignis und kein Löschen des Journals.
5.  Auto-Approval ist standardmäßig deaktiviert.
6.  Neuron-Pruning ist standardmäßig deaktiviert.
7.  Snapshot-Anforderungen werden an sicheren Runtime-Grenzen
    verarbeitet.
8.  Restore muss strukturelle Ereignisse deterministisch replayen.

## Operator-Funktionen

Alpha.5 umfasst die Bedienpfade für:

-   Proposal-Übersicht,
-   Approve/Reject,
-   Auto-Approval Toggle,
-   Undo Last,
-   Structural History,
-   Structural Heatmap,
-   1/10/100/1000/custom Ticks,
-   Run/Pause/Resume/Stop,
-   Snapshot.

## Qualitätsstand

Der zuletzt dokumentierte Integrationsstand umfasst:

-   148 nicht-langsame Tests bestanden,
-   2 optionale Tests übersprungen,
-   20 fokussierte Alpha.5-Verhaltenstests bestanden,
-   Mypy für 61 Source-Dateien sauber,
-   Alpha.5 Strict-Pyright-Scope sauber,
-   Black sauber,
-   `git diff --check` sauber.

Repositoryweite historische Pyright-/Pylint-Befunde außerhalb des
Alpha.5-Scopes werden nicht durch globale Suppressions verborgen.

## Nächste Stufe

v0.5.0-alpha.6: Morphological Self-Regulation.
