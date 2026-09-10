[Inhaltsuebersicht](README.md) | [Zurueck](section-024.md) | [Weiter](section-026.md)

<a id="b5d-persistenz-digital-state-twin-und-reproduzierbarkeit"></a>

# 21. Persistenz, Digital State Twin und Reproduzierbarkeit

<a id="b5d-storage-und-5d-digital-state-twin"></a>

## Storage und 5D Digital State Twin

<a id="b5d-begriffliche-präzisierung"></a>

### Begriffliche Präzisierung

Ein Digital Twin wird häufig als gekoppelte digitale Repräsentation eines physischen oder technischen Gegenstands verstanden; Literatur unterscheidet zudem Digital Model, Digital Shadow und Digital Twin nach Kopplungsrichtung und Automatisierungsgrad ([Fuller et al., 2020](section-045.md#ref-Fuller2020); [Jones et al., 2020](section-045.md#ref-Jones2020); [Kritzinger et al., 2018](section-045.md#ref-Kritzinger2018)). Solange MHRN primär eine digitale Simulation ohne synchrones physisches Gegenstück ist, ist **Digital State Twin** beziehungsweise **reproduzierbarer digitaler Zustandszwilling** präziser. Wird später ein physisches neuronales Substrat gekoppelt, muss die Twin-Beziehung separat definiert werden.

<a id="b5d-schichtenmodell"></a>

### Schichtenmodell

![Schichten des MHRN Storage- und Digital-State-Twin-Konzepts.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K1_image3.png)

Abbildung 7. Schichten des MHRN Storage- und Digital-State-Twin-Konzepts.

Die Speicherarchitektur trennt:

1.  den potenziellen 5D-Adressraum;

2.  den materialisierten Simulationszustand;

3.  Checkpoints und Delta-/Event-Logs;

4.  abgeleitete Sichten und Indizes;

5.  Experiment- und Evidenzregister.

Abgeleitete Graphmetriken oder Heatmaps dürfen gelöscht und neu berechnet werden. Primärzustand und Ereignisse müssen dagegen für den behaupteten Reproduktionsgrad ausreichend sein.

<a id="b5d-speichergrößen"></a>

### Speichergrößen

Für $N = 50^{5} = 312.500.000$ und $b_{N}$ Byte je Neuron gilt

**\[DEF\]**

$$S_{N} = Nb_{N}.$$Bei $b_{N} = 128$ Byte ergibt dies $40,0$ GB dezimal beziehungsweise ungefähr $37,25$ GiB, noch ohne Synapsen, Indizes und Historie.

Bei mittlerem Out-Degree $k$ gilt

$$S_{edges} = Nk.$$Für $k = 100$ entstehen $31,25$ Milliarden gerichtete Synapsen. Der Rohbedarf beträgt:

Tabelle 25. Illustrative Rohspeicherbedarfe

| **Bytes je Synapse** | **Dezimaler Rohbedarf** | **Binärer Näherungswert** |
|:---------------------|:------------------------|:--------------------------|
| 16 B                 | 500 GB                  | ca. 465,7 GiB             |
| 24 B                 | 750 GB                  | ca. 698,5 GiB             |
| 32 B                 | 1,0 TB                  | ca. 931,3 GiB             |

Diese Werte enthalten weder Datenbank-Overhead noch Replikation, Checkpoints, Event-Historie oder temporäre Analyseobjekte. Eine naive Vollmaterialisierung ist daher nicht die Zielarchitektur.

<a id="b5d-struktur-of-arrays-und-chunking"></a>

### Struktur-of-Arrays und Chunking

Millionen Python-Objekte verursachen hohen Overhead. Für skalierende Implementierungen sind spalten- beziehungsweise arrayorientierte Strukturen zweckmäßig:

    neuron_id[]
    coord_x[] ... coord_b[]
    membrane_v[]
    recovery_u[]
    threshold[]
    energy[]
    cell_type[]
    created_tick[]

Synapsen können als CSR/CSC-nahe Strukturen, Edge-Chunks oder regional partitionierte Adjazenzlisten gespeichert werden. HDF5-artige Chunk- und Dataset-Konzepte sind für große wissenschaftliche Arrays etabliert ([Folk et al., 2011](section-045.md#ref-Folk2011)); MHRN bleibt backend-agnostisch und kann Zarr-, HDF5-, Parquet- oder spezialisierte Graphspeicher kombinieren.

<a id="b5d-checkpoint-plus-delta"></a>

### Checkpoint plus Delta

Ein Vollsnapshot jedes Ticks wäre untragbar. Stattdessen:

**\[MODEL\]**

$$X_{t} = Replay\left( C_{t_{0}},\{\Delta_{t_{0} + 1},\ldots,\Delta_{t}\} \right),$$mit Checkpoint $C_{t_{0}}$ und geordneten Deltas. Deltas umfassen Spike-Ereignisse, Gewichtsänderungen, strukturelle Mutationen, externe Inputs, Rewards und relevante Scheduler-/RNG-Übergänge.

Die mittlere Speicherlast über Zeitraum $T$ kann angenähert werden durch

$$S(T) = n_{C}S_{C} + \sum_{e \in E_{T}}^{}S_{e} + S_{index} + S_{provenance}.$$Checkpoint-Intervall, Delta-Kompression und Rekonstruktionszeit bilden einen Trade-off.

<a id="b5d-snapshot-konsistenz"></a>

### Snapshot-Konsistenz

Ein Snapshot muss einen logisch konsistenten Zustand abbilden. In parallelen oder verteilten Simulationen können Schreibvorgänge zeitlich überlappen. Konzepte verteilter Snapshots und Ereignisordnung sind daher relevant ([Chandy & Lamport, 1985](section-045.md#ref-Chandy1985); [Lamport, 1978](section-045.md#ref-Lamport1978)). MHRN benötigt entweder eine definierte Safe Point-Barriere oder ein konsistentes Snapshot-Protokoll.

<a id="b5d-fidelity-dimensionen"></a>

### Fidelity-Dimensionen

Der Digital State Twin wird anhand von vier Fidelity-Dimensionen bewertet:

1.  **State Fidelity:** rekonstruiertes ${\hat{X}}_{t}$ entspricht $X_{t}$ innerhalb definierter Toleranz;

2.  **Temporal Fidelity:** Ereignisreihenfolge und Verzögerungen bleiben erhalten;

3.  **Structural Fidelity:** Knoten, Kanten, Typen und Attribute stimmen;

4.  **Causal Fidelity:** Replay reproduziert relevante Antworten auf identische Interventionen.

**\[EMP\]** Ein Rekonstruktionsfehler kann als

$$E_{state} = \frac{\parallel X_{t} - {\hat{X}}_{t} \parallel_{W}}{\parallel X_{t} \parallel_{W} + \epsilon}$$geschätzt werden. Für diskrete Struktur werden Hashes, Set-Differenzen und typisierte Edge-Vergleiche verwendet.

<a id="b5d-digital-twin-api"></a>

### Digital-Twin-API

Die API soll mindestens ermöglichen:

- `snapshot(tick)` und `restore(snapshot_id)`;

- `query_neurons(region, time)`;

- `query_edges(source, target, type, time)`;

- `stream_events(t0, t1, filters)`;

- `diff_state(snapshot_a, snapshot_b)`;

- `trace_provenance(entity_id)`;

- `fork_experiment(snapshot_id, intervention)`;

- `verify_integrity(artifact_id)`.

Das Forking aus einem identischen Zustand ist besonders wertvoll für kontrafaktische und kausale Ablationen.

<a id="b5d-optisches-beziehungsweise-bildartiges-speicheräquivalent"></a>

### Optisches beziehungsweise bildartiges Speicheräquivalent

Die Idee einer 3D–5D-Bildrepräsentation kann als **kodierte Sicht** des Zustands nützlich sein. Ein Voxel oder Texel kann mehrere Kanäle tragen, etwa Potential, Zelltyp, Energie, Aktivität und lokale Strukturdichte. Eine Bilddatei ist jedoch nicht automatisch ein geeigneter Primärspeicher für variable Graphkanten und Ereignishistorien. MHRN unterscheidet daher:

- **state raster:** dichte oder sparse Rasterkanäle pro Koordinate;

- **edge layer:** separate Graph-/Kantenstruktur;

- **event layer:** zeitgeordnete Änderungen;

- **metadata layer:** Schema, Einheiten, Provenienz und Kompression.

Die optische Darstellung wird als analysierbare, manipulierbare und gegebenenfalls GPU-nahe Projektion behandelt, nicht als vollständiger Ersatz für alle relationalen Daten.

<a id="b5d-manipulation-und-auslesen"></a>

### Manipulation und Auslesen

Jede Manipulation am Twin erfolgt transaktional:

    ReadSnapshot → ConstructIntervention → Validate → Fork → Apply → Simulate → Compare

Direktes Editieren eines Produktionssnapshots ist unzulässig. Interventionen erhalten ID, Autorität, Ziel, Bereich, Vorher-/Nachher-Hash und Rollback-Information. Dadurch können Forschungsmanipulationen von natürlicher Plastizität unterschieden werden.

<a id="b5d-reproduzierbarkeit-und-forschungssoftware"></a>

## Reproduzierbarkeit und Forschungssoftware

<a id="b5d-minimalmetadaten-eines-wissenschaftlichen-laufs"></a>

### Minimalmetadaten eines wissenschaftlichen Laufs

Jeder wissenschaftlich relevante Lauf enthält mindestens:

    experiment_id: EXP-...
    run_id: RUN-...
    claim_ids: [CLAIM-...]
    git_repository: Thomas-Heisig/MHRN
    git_commit: "..."
    brain5d_version: "..."
    working_tree_clean: true
    configuration_hash: sha256:...
    configuration_artifact: ART-...
    random_seed: 12345
    rng_algorithm: PCG64
    rng_state_artifact: ART-...
    dataset_ids: [DATA-...]
    stimulus_schema: "2.0"
    network_schema: "3.1"
    plasticity_schema: "2.4"
    metric_schema: "1.2"
    decoder_id: DEC-...
    language_backend: null-language-1.0
    hardware:
      cpu: "..."
      gpu: "..."
      ram_gib: 64
    software:
      os: "..."
      python: "..."
      dependencies_lock_hash: sha256:...
    start_tick: 0
    end_tick: 2000000
    wall_clock_start: "..."
    termination_reason: completed

<a id="b5d-reproduzierbare-umgebungen"></a>

### Reproduzierbare Umgebungen

Abhängigkeiten werden über Lockfiles und archivierte Build-Artefakte erfasst. Container oder virtuelle Umgebungen unterstützen Reproduzierbarkeit, ersetzen aber keine Dokumentation von Hardware, Treibern und numerischen Bibliotheken. Wissenschaftliche Software soll zitierbar versioniert und mit persistenten Releases archiviert werden ([Smith et al., 2016](section-045.md#ref-Smith2016); [Wilson et al., 2017](section-045.md#ref-Wilson2017)).

<a id="b5d-tests-und-wissenschaftliche-validation"></a>

### Tests und wissenschaftliche Validation

Die Testpyramide umfasst:

1.  **Unit Tests:** Formeln, Grenzen, Serialisierung, RNG;

2.  **Property Tests:** Invarianten über viele zufällige Eingaben;

3.  **Integration Tests:** Datenverträge und Komponentenfehler;

4.  **Golden Runs:** kleine deterministische Referenzläufe;

5.  **Scientific Regression Tests:** erwartete Verteilungen und Metrikbereiche;

6.  **Benchmark Tests:** Leistung und Ressourcen;

7.  **Experiment Reproduction:** vollständige registrierte Studien.

Golden Runs dürfen nicht als wissenschaftliche Replikation gelten; sie prüfen technische Drift.

<a id="b5d-datenintegrität"></a>

### Datenintegrität

Artefakte erhalten kryptografische Hashes, Schema-ID, Bytegröße, Erzeugerprozess und Elternartefakte. FAIR-Prinzipien motivieren Auffindbarkeit, Zugänglichkeit, Interoperabilität und Wiederverwendbarkeit ([Wilkinson et al., 2016](section-045.md#ref-Wilkinson2016)). Datenschutz, Lizenzen und Speichergrenzen können offene Veröffentlichung einschränken; in diesem Fall werden Metadaten, synthetische Reproduktionsdaten oder kontrollierte Zugänge dokumentiert.

<a id="b5d-reproduktionspaket"></a>

### Reproduktionspaket

Eine veröffentlichungsfähige Studie enthält:

    paper/
    protocol/
    configs/
    source_commit.txt
    environment.lock
    run_manifest.csv
    raw_or_pointer_data/
    derived_data/
    analysis/
    figures/
    checksums.txt
    README_REPRODUCE.md

Die Analyse beginnt aus Raw- oder kanonischen Primärartefakten. Manuell veränderte Tabellen ohne Herkunft sind unzulässig.

[Inhaltsuebersicht](README.md) | [Zurueck](section-024.md) | [Weiter](section-026.md)
