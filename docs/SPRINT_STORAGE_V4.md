# Brain-5D v0.4.0-alpha.4 – Persistence Finalization

## Ziel

Alpha.4 schließt den Persistenz-Contract vor v0.4.0 final. Die Simulation
bleibt vom I/O entkoppelt, Storage wird messbar, Journale können sicher
kompaktiert werden und der nicht im eingefrorenen `.b5d`-V1-Format enthaltene
Runtime-Zustand erhält einen typisierten Sidecar.

## Neue Bausteine

- `async_runtime.py`: bounded Queue, ein I/O-Worker, Backpressure oder opt-in Drop.
- `checkpoint.py`: RNG, Event Queue, Pending Currents, Input/Output-Sets, Zähler.
- `core_restore.py`: Rekonstruktion eines laufbaren `NeuralNetwork`.
- `compaction.py`: Generation-Dateien + atomar publiziertes Manifest.
- Storage-Telemetrie: Queue-Tiefe, Bytes, Deltas, Drop-Zähler und Latenzen.

## Architektur

```text
Network.step()
    -> Delta-Erkennung auf Simulationsthread
    -> immutable DeltaRecord batch
    -> bounded Queue
    -> Storage Worker
    -> DeltaJournal
```

Der Worker liest niemals mutable Neuronen oder Synapsen. Damit entstehen keine
Race Conditions zwischen Simulation und Storage.

## Backpressure

Default ist `drop_on_overflow: false`. Bei voller Queue darf die Simulation
kontrolliert warten. Drop ist nur explizit aktivierbar und wird über
`dropped_batches` sichtbar. Es gibt keinen stillen Datenverlust.

## Crash-sichere Compaction

Eine einzelne Datei-Paar-Rotation kann nicht atomar sein. Alpha.4 verwendet
stattdessen Generationen und einen atomar ersetzten Manifest-Pointer:

```text
g0 snapshot + g0 journal   [aktiv]
        |
        +-> recover -> g1 snapshot
        +-> create empty g1 journal
        +-> validate both
        +-> atomic replace manifest -> g1
```

Ein Crash vor dem Manifest-Replace lässt g0 aktiv. Ein Crash danach lässt g1
aktiv. Alte Generationen können erst nach erfolgreicher Promotion entfernt
werden.

## Restore-and-Continue

`.b5d` V1 bleibt eingefroren. Nicht darin enthaltene Runtime-Daten liegen in
einem JSON-Sidecar. Gespeichert werden insbesondere `random.Random` state,
future events und pending currents. Damit kann ein echter Core deterministisch
weiterlaufen, sofern Snapshot, Journal und Sidecar vom selben Checkpoint stammen.

## Grenzen

- Change detection ist weiterhin O(N+E); Dirty Tracking folgt in v0.5/v0.6.
- Nur ein Storage-Worker ist freigegeben. Mehrere Writer auf dasselbe Journal
  bleiben verboten.
- Compaction löscht alte Generationen nicht automatisch in diesem Alpha.
