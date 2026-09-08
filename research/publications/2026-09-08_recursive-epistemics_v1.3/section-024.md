[Inhaltsuebersicht](README.md) | [Zurueck](section-023.md) | [Weiter](section-025.md)

<a id="b5d-signalinterpretation-sprache-und-wissensaufnahme"></a>

# 20. Signalinterpretation, Sprache und Wissensaufnahme

<a id="b5d-signal-interpretation-layer"></a>

## Signal Interpretation Layer

<a id="b5d-wissenschaftliche-funktion"></a>

### Wissenschaftliche Funktion

Der Signal Interpretation Layer (SIL) bildet eine deterministische beziehungsweise vollständig versionierte Messschicht zwischen neuronalen Rohereignissen und nachgelagerten Interpretationssystemen. Seine Aufgabe ist nicht, Bedeutung zu erzeugen, sondern definierte, prüfbare Merkmale aus einem Zeitfenster zu berechnen. Diese Trennung schützt vor einem zentralen Confound: Ein leistungsfähiges LLM darf keine semantische Geschichte direkt aus unstrukturierten Spike-Arrays konstruieren und anschließend so behandeln, als habe das SNN selbst diese Geschichte repräsentiert.

**\[DEF\]**

$$S_{v}:\left( \text{SpikeEvents},X_{\left\lbrack t_{0},t_{1} \right\rbrack},\text{RegionSchema} \right) \rightarrow \text{SignalFrame}_{v},$$wobei $v$ die Version der Transformation bezeichnet. Für identische Eingaben muss ein deterministischer SIL identische Frames erzeugen. Stochastische Schätzer müssen Seed und Unsicherheit mitführen.

<a id="b5d-minimaler-datenvertrag"></a>

### Minimaler Datenvertrag

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class RegionActivity:
        region_id: str
        neuron_count: int
        active_fraction: float
        firing_rate_hz: float
        spike_count: int
        burst_index: float
        synchrony: float

    @dataclass(frozen=True, slots=True)
    class SignalFrame:
        frame_id: str
        schema_version: str
        tick_from: int
        tick_to: int
        neuron_selection_hash: str
        population_rate_hz: float
        spike_count: int
        active_fraction: float
        burst_index: float
        synchrony: float
        entropy_estimate: float | None
        mean_energy_proxy: float
        active_regions: tuple[RegionActivity, ...]
        source_snapshot_id: str
        transformation_hash: str

Der `neuron_selection_hash` verhindert, dass dieselbe Metrik scheinbar vergleichbar ist, obwohl eine andere Population ausgewertet wurde. Der `source_snapshot_id` erlaubt die Rückführung auf den zugrunde liegenden Zustand. Ein `SignalFrame` enthält keine Felder wie `thought`, `meaning` oder `intent`, weil diese Interpretationen und keine Messungen wären.

<a id="b5d-metrikdefinitionen"></a>

### Metrikdefinitionen

Jede Metrik benötigt eine formale Definition. Beispielsweise kann Populationsrate berechnet werden als

**\[DEF\]**

$$r_{pop} = \frac{N_{spike}}{N_{neurons}\left( t_{1} - t_{0} \right)}.$$Synchronität kann je nach Methode Paar-Korrelation, Phasenkohärenz oder Coincidence-Maß bedeuten. Ohne Angabe der Methode ist der Wert nicht interpretierbar. Burst Index und Entropieschätzer benötigen ebenfalls Version, Fenster und Parameter.

<a id="b5d-rohdatenzugang"></a>

### Rohdatenzugang

Für wissenschaftliche Analysen müssen Rohereignisse oder verlustarm rekonstruierbare Daten erhalten bleiben. Der SIL darf keine irreversible alleinige Datenquelle sein. Aggregierte Frames sind effizient für Monitoring und Decoder, reichen aber nicht für jede spätere Hypothese.

<a id="b5d-leakage-schutz"></a>

### Leakage-Schutz

Ein Decoder darf nur Felder erhalten, die in der `ExperimentSpec` freigegeben sind. Insbesondere können `stimulus_id`, Zielklasse, Rewardlabel oder Dateiname ungewollt die Antwort verraten. MHRN soll eine automatische Feature-Allowlist und Leakage-Tests verwenden.

<a id="b5d-language-organ"></a>

## Language Organ

<a id="b5d-rolle-und-nicht-rolle"></a>

### Rolle und Nicht-Rolle

Das Language Organ ist ein optionaler Adapter zwischen symbolischen und neuronalen Darstellungen. Es kann Texte strukturieren, Stimulusvorschläge erzeugen, SignalFrames beschreiben oder Antworten formulieren. Es ist nicht Eigentümer des SNN-Zustands, der Lernregeln oder des Runtime-Loops.

$$\text{Language Organ} ≢ \text{MHRN Core}.$$**\[E0 \| ARCHITECTURE-SPEC\]** Jede wissenschaftliche Behauptung über SNN-Kompetenz muss mit einem NullLanguageBackend oder einer anderen geeigneten Ablation prüfbar bleiben.

<a id="b5d-reines-monitoring"></a>

### Reines Monitoring

Der reine Monitoring-Pfad lautet:

    SNN → SignalFrame → Monitor → LogRecord

Der Monitor darf Warnungen, Zusammenfassungen oder Visualisierungen erzeugen. Diese Ausgaben verändern weder den aktuellen noch einen zukünftigen SNN-Zustand. Auch ein Warnsignal ist erst dann eine Intervention, wenn es einen Controller oder Stimulus beeinflusst.

<a id="b5d-optionaler-feedbackpfad"></a>

### Optionaler Feedbackpfad

Der Interventionspfad lautet:

    SignalFrame
      → LanguageModelBackend
      → FeedbackProposal
      → deterministic PolicyGate
      → accepted StimulusPlan or RejectionRecord
      → SNN input channel

Ein `FeedbackProposal` kann enthalten:

    @dataclass(frozen=True, slots=True)
    class FeedbackProposal:
        proposal_id: str
        source_frame_ids: tuple[str, ...]
        objective: str
        rationale: str
        uncertainty: float
        target_region: str | None
        requested_modality: str
        intensity_ceiling: float
        duration_ceiling_ticks: int
        energy_budget: float
        expires_at_tick: int
        backend_id: str
        model_version: str
        prompt_hash: str

`rationale` ist eine Modelläußerung, kein Beweis. Das PolicyGate prüft erlaubte Ziele, Grenzen, Cooldowns, Konflikte, Provenienz und Experimentmodus. Es kann den Vorschlag ablehnen, begrenzen oder in Quarantäne stellen. Die endgültige Stimulus-ID verweist auf Proposal und Gate-Entscheidung.

<a id="b5d-backend-abstraktion"></a>

### Backend-Abstraktion

    LanguageModelBackend
    ├── NullLanguageBackend
    ├── RuleBasedBackend
    ├── LocalLlamaCppBackend
    ├── RemoteAPIBackend
    └── ExperimentalBackend

Die konkrete Modellwahl ist eine Deployment- und Experimentvariable. Die wissenschaftliche Theorie darf nicht an ein bestimmtes kommerzielles oder lokales Modell gebunden werden. Modellname, Version, Quantisierung, Kontext, Systemprompt und Samplingparameter sind Teil der Run-Metadaten.

<a id="b5d-asynchronität-und-latenz"></a>

### Asynchronität und Latenz

LLM-Inferenz kann um Größenordnungen langsamer sein als neuronale Ticks. Das Language Organ kommuniziert daher über begrenzte Queues und zeitgestempelte Nachrichten. Ein abgelaufener Vorschlag darf nicht verspätet in einen inzwischen anderen Netzwerkzustand eingreifen. Queue-Länge, Drop-Policy und Timeout werden protokolliert.

<a id="b5d-decoder-als-hypothesengenerator"></a>

### Decoder als Hypothesengenerator

Die Kette

$$\text{SpikeEvents} \rightarrow \text{SignalFrame} \rightarrow \text{Decoder} \rightarrow \text{Interpretation}$$liefert eine **symbolische Hypothese**. Jede `Interpretation` enthält Confidence, Decoder-Version, Trainingsdatenstatus, freigegebene Features und verknüpfte Frames. Ein sprachlich plausibler Text kann falsch, halluziniert oder stärker vom Decoder-Prior als vom Signal bestimmt sein.

<a id="b5d-encoder-und-stimulusplan"></a>

### Encoder und StimulusPlan

Text wird nicht direkt in Gewichte geschrieben:

$$\text{Text} \rightarrow \text{SemanticObject} \rightarrow \text{StimulusPlan} \rightarrow \text{InputEvents}.$$Ein minimaler `StimulusPlan` enthält:

    stimulus_id: STIM-2026-000184
    schema_version: 2.0
    source_type: language_organ
    source_record_ids: [SRC-018, KI-044]
    target_region: input.language.de
    start_tick: 820000
    duration_ticks: 400
    pattern_type: population_temporal_code
    frequency_hz: 18.0
    intensity: 0.32
    spatial_distribution: gaussian
    random_seed: 99172
    safety_class: research_low_energy
    encoder_version: semantic-encoder-0.3
    content_hash: sha256:...

<a id="b5d-language-organ-ablationen"></a>

### Language-Organ-Ablationen

Tabelle 24. Ablationsbedingungen für das Language Organ

| **Bedingung** | **Encoder** | **Decoder** | **Feedback** | **Retrieval** | **Zweck**                      |
|:--------------|:------------|:------------|:-------------|:--------------|:-------------------------------|
| L0            | nein        | nein        | nein         | nein          | autonomer SNN-Kern             |
| L1            | nein        | ja          | nein         | nein          | reine Output-Interpretation    |
| L2            | ja          | ja          | nein         | nein          | symbolische I/O-Brücke         |
| L3            | ja          | ja          | PolicyGate   | nein          | kontrollierte Rückkopplung     |
| L4            | ja          | ja          | PolicyGate   | ja            | vollständige hybride Bedingung |

Nach Training in L4 erfolgt die entscheidende Isolation: LLM aus, Retrieval aus, Cache gelöscht, Decoder wahlweise durch festes Baseline-Modell ersetzt. Nur so lässt sich prüfen, ob im SNN persistente Information verbleibt.

<a id="b5d-knowledge-intake-engine"></a>

## Knowledge Intake Engine

<a id="b5d-trennung-von-sprache-und-wissensaufnahme"></a>

### Trennung von Sprache und Wissensaufnahme

Die Knowledge Intake Engine (KIE) ist nicht Teil des LLM. Sie verwaltet Herkunft, Abruf, Parsing, Lizenz, Vertrauensstatus, Widersprüche und Versionierung. Ein LLM kann Inhalte extrahieren oder klassifizieren, besitzt aber nicht die Autorität, eine Aussage allein dadurch zum Fakt zu erklären.

<a id="b5d-provenienzmodell"></a>

### Provenienzmodell

Provenienz ist Information über Entitäten, Aktivitäten und Akteure, die an der Erzeugung oder Transformation eines Artefakts beteiligt sind ([Buneman et al., 2001](section-045.md#ref-Buneman2001); [Moreau et al., 2013](section-045.md#ref-Moreau2013)). MHRN verwendet mindestens:

    SourceRecord
      └── RetrievalActivity
           └── RawArtifact
                └── ParseActivity
                     └── KnowledgeItem
                          └── EncodingActivity
                               └── StimulusPlan
                                    └── Episode

<a id="b5d-sourcerecord"></a>

### SourceRecord

    source_id: SRC-2026-0012
    canonical_uri: "..."
    source_type: journal_article
    retrieved_at: 2026-08-16T20:10:00+02:00
    content_hash: sha256:...
    media_type: application/pdf
    license_status: verified_open_access
    publisher: "..."
    publication_date: "..."
    retrieval_tool: intake-http-0.4

URLs sind nicht ausreichend, weil Inhalte sich ändern können. Content Hash, Abrufdatum und nach Möglichkeit archivierte Kopie oder DOI gehören zum Nachweis.

<a id="b5d-knowledgeitem"></a>

### KnowledgeItem

    knowledge_id: KI-2026-0044
    content: "..."
    language: de
    source_ids: [SRC-2026-0012]
    extraction_method: human_reviewed_llm_extract
    parser_version: 0.8
    trust_state: source_verified
    validation_state: proposition_unverified
    contradiction_set: [KI-2026-0021]
    content_hash: sha256:...

`trust_state` bewertet Quelle oder Prozess; `validation_state` bewertet die konkrete Proposition. Eine renommierte Quelle kann irren, und eine korrekte Aussage aus einer unbekannten Quelle kann unzureichend validiert sein. Widersprüche werden nicht überschrieben, sondern als Beziehung gespeichert.

<a id="b5d-lernstimulus-und-semantische-dosis"></a>

### Lernstimulus und semantische Dosis

Ein KnowledgeItem wird nicht vollständig und einmalig als „Wissen” in das SNN geschrieben. Es wird in einen Lernstimulus mit kontrollierter Dosis, Wiederholung, Variation und Kontext überführt. Die Kodierung ist Teil des Experiments. Ein zu deterministischer Encoder kann das Zielmerkmal direkt in leicht dekodierbare Kanäle einprägen und damit die eigentliche Repräsentationsfrage trivialisieren.

<a id="b5d-datenschutz-lizenz-und-datenminimierung"></a>

### Datenschutz, Lizenz und Datenminimierung

Personenbezogene oder lizenzbeschränkte Inhalte benötigen Filter, Zweckbindung und Löschkonzept. Provenienz darf nicht zum unbegrenzten Kopieren geschützter Volltexte führen. Für wissenschaftliche Läufe werden nach Möglichkeit Hashes, Metadaten, erlaubte Extrakte und reproduzierbare Abrufanweisungen gespeichert.

[Inhaltsuebersicht](README.md) | [Zurueck](section-023.md) | [Weiter](section-025.md)
