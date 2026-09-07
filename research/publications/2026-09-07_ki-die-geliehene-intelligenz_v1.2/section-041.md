[Inhaltsuebersicht](README.md) | [Zurueck](section-040.md) | [Weiter](section-042.md)

<a id="b5d-anhang-a---datenverträge-skalen-und-statuskonventionen"></a>

# Anhang A - Datenverträge, Skalen und Statuskonventionen

**Status der folgenden Schemata:** illustrative Datenverträge und Vorlagen aus K1. Beispiel-IDs, Zahlen und Statuswerte stellen keine Ergebnisse dieser Abhandlung dar. Für reale Befunde gilt ausschließlich das Evidenzregister des Begleitpakets.

<a id="b5d-anhang-a-status--und-claim-konventionen"></a>

## Übernommene Vorlage: Anhang A — Status- und Claim-Konventionen

<a id="b5d-a.1-statussyntax"></a>

### A.1 Statussyntax

    [E0 | HYPOTHESIS | CLAIM-GEO-001]
    [E1 | IMPLEMENTED | CLAIM-ARCH-012 | commit=... | tests=...]
    [E2 | VALIDATED | CLAIM-MEM-004 | EXP-MEM-018 | n=30]
    [E3 | SYSTEM | CLAIM-EMB-003 | EXP-EMB-022,EXP-EMB-031]

<a id="b5d-a.2-herabstufung"></a>

### A.2 Herabstufung

Ein Claim wird herabgestuft oder eingeschränkt, wenn:

- Replikation scheitert;

- ein Confound identifiziert wird;

- Implementierung oder Datenintegrität fehlerhaft war;

- der Effekt nur in engerem Scope gilt;

- ein stärkeres Nullmodell die Erklärung übernimmt.

Historische EvidenceRecords bleiben erhalten; eine neue Version ersetzt die Entscheidung nicht rückwirkend.

<a id="b5d-a.3-claim-formulierung"></a>

### A.3 Claim-Formulierung

Gute Claims sind atomar, operationalisiert und begrenzt. Ungünstig ist: „Brain-5D versteht Sprache.” Besser:

    In benchmark SEM-REL-02, a decoder trained on frozen SignalFrames predicts
    held-out relation class Y above the preregistered permutation baseline after
    LLM and retrieval isolation, across 30 independent network seeds.

Die kognitive Interpretation kann anschließend diskutiert werden, bleibt aber vom empirischen Claim getrennt.

<a id="b5d-anhang-b-datenverträge"></a>

## Übernommene Vorlage: Anhang B — Datenverträge

<a id="b5d-b.1-stimulusplan"></a>

### B.1 StimulusPlan

    @dataclass(frozen=True, slots=True)
    class StimulusPlan:
        stimulus_id: str
        schema_version: str
        source_record_ids: tuple[str, ...]
        modality: str
        target_region: str
        start_tick: int
        duration_ticks: int
        intensity: float
        frequency_hz: float | None
        spatial_distribution: str
        temporal_pattern: str
        encoder_id: str
        random_seed: int | None
        safety_class: str
        content_hash: str

<a id="b5d-b.2-interpretation"></a>

### B.2 Interpretation

    @dataclass(frozen=True, slots=True)
    class Interpretation:
        interpretation_id: str
        signal_frame_ids: tuple[str, ...]
        decoder_id: str
        decoder_version: str
        hypothesis_text: str
        predicted_labels: tuple[str, ...]
        confidence: float
        calibration_version: str
        allowed_features_hash: str
        created_at_tick: int

<a id="b5d-b.3-rejectionrecord"></a>

### B.3 RejectionRecord

    @dataclass(frozen=True, slots=True)
    class RejectionRecord:
        proposal_id: str
        policy_version: str
        reason_codes: tuple[str, ...]
        evaluated_at_tick: int
        evaluated_limits_hash: str

<a id="b5d-anhang-c-beispiel-eines-evidencerecord"></a>

## Übernommene Vorlage: Anhang C — Beispiel eines EvidenceRecord

    evidence_id: EVID-2027-0041
    claim_id: CLAIM-HOME-002
    previous_status: E1
    new_status: E2
    decision: promoted
    basis:
      experiments: [EXP-HOME-007, EXP-HOME-009]
      run_count_total: 60
      preregistered_primary_endpoint: population_rate_variance
      effect_estimate: -0.31
      confidence_interval_95: [-0.42, -0.19]
      robustness_checks:
        - alternative_window_sizes
        - exclusion_sensitivity
        - matched_activity_control
    limitations:
      - validated_only_for_5000_and_20000_neuron_networks
      - no_closed_loop_validation
    reviewed_by: [researcher_a, researcher_b]
    created_at: "2027-04-18"

<a id="b5d-anhang-d-architekturprüfungen"></a>

## Übernommene Vorlage: Anhang D — Architekturprüfungen

Tabelle 36. Architektur- und Fehlergrenzenpruefungen

| **Prüfung**                   | **Erfolgsbedingung**                                                      |
|:------------------------------|:--------------------------------------------------------------------------|
| LLM-Crash                     | Runtime läuft weiter; Fehler wird protokolliert; keine Zustandskorruption |
| ungültiger StimulusPlan       | Reject ohne partielle Anwendung                                           |
| direkter Weight-Write-Versuch | Capability verweigert; Security-Event                                     |
| Snapshot-Restore              | Probe-Response innerhalb definierter Toleranz                             |
| RNG-Replay                    | identische beziehungsweise spezifizierte statistische Trajektorie         |
| Queue-Überlauf                | dokumentierte Drop-/Backpressure-Policy                                   |
| Sensorverlust                 | Missing-Data-Zustand; kein impliziter Nullwert                            |
| Aktorgrenze                   | SafetyController begrenzt oder blockiert                                  |
| Schemawechsel                 | explizite Migration; alter Run bleibt lesbar                              |
| Decoder-Leakage               | Ziel-/Stimulus-IDs nicht in Feature-Allowlist                             |

<a id="b5d-anhang-e-abkürzungen-und-symbole"></a>

## Übernommene Vorlage: Anhang E — Abkürzungen und Symbole

Tabelle 37. Abkürzungen und Symbole

| **Kürzel / Symbol** | **Bedeutung**                                |
|:--------------------|:---------------------------------------------|
| SNN                 | Spiking Neural Network                       |
| LLM                 | Large Language Model                         |
| SIL                 | Signal Interpretation Layer                  |
| KIE                 | Knowledge Intake Engine                      |
| STDP                | Spike-Timing-Dependent Plasticity            |
| LTP / LTD           | Long-Term Potentiation / Depression          |
| E/I                 | Excitation / Inhibition                      |
| SPD                 | symmetric positive definite                  |
| $$X_{t}$$           | vollständiger materialisierter Systemzustand |
| $$p_{i}$$           | 5D-Position eines Neurons                    |
| $$M$$               | Metrikmatrix                                 |
| $$G_{t}$$           | dynamischer Netzwerkgraph                    |
| $$d_{M}$$           | Umgebungsdistanz in der Metrik $M$           |
| $$d_{G}$$           | Graphgeodätische Distanz                     |
| $$e_{ij}$$          | Eligibility Trace                            |
| $$Q$$               | aufgabenspezifische Leistungsmetrik          |
| ACE                 | Average Causal Effect                        |
| BWT / FWT           | Backward / Forward Transfer                  |
| RNG                 | Random Number Generator                      |

<a id="b5d-anhang-a-forschungs--und-provenienzprotokoll"></a>

## Übernommene Vorlage: Anhang A – Forschungs- und Provenienzprotokoll

- analysis_id / run_id / Zeitstempel

- Repository, Commit und Softwareumgebung

- LLM-Anbieter, Modell, Version und Zugriffsweg

- Systemprompt, Benutzerprompt, Prompt-Hash und Kontext

- Samplingparameter und Seed, soweit verfügbar

- Manifest, Validator- und Builderversion

- Netzwerk-Startzustand und Endzustand

- Architektur-, Dynamik-, Leistungs- und Ressourcenmetriken

- Embodiment-Stufe, Sensoren, Aktoren und Umweltversion

- menschliche Eingriffe, Auswahl- und Freigabeentscheidungen

- Selbstmodifikationen, Stopps, Snapshots und Rollbacks

- Quellen, Unsicherheiten, Ausschlüsse und Interpretationsnotizen

<a id="b5d-anhang-b-skalen-für-hoheit-kontrolle-autonomierisiko-und-embodiment"></a>

## Übernommene Vorlage: Anhang B – Skalen für Hoheit, Kontrolle, Autonomierisiko und Embodiment

Tabelle 38. Ordinalskalen für Hoheit und Kontrolle

| **Wert** | **Interpretation**                                              |
|:---------|:----------------------------------------------------------------|
| 0        | nicht vorhanden / nicht dokumentiert                            |
| 1        | minimal, indirekt oder praktisch unwirksam                      |
| 2        | begrenzt und nur in Teilbereichen wirksam                       |
| 3        | substanziell, aber mit relevanten Lücken                        |
| 4        | hoch und weitgehend nachgewiesen                                |
| 5        | vollständig, unabhängig geprüft und reproduzierbar dokumentiert |

Die Skala ist kein validiertes Messinstrument. Sie ist ein strukturiertes Dokumentationsschema. Gewichtungen und aggregierte Scores dürfen erst nach Validierungs- und Sensitivitätsanalyse verwendet werden.

<a id="b5d-anhang-c-minimalanforderungen-an-sichere-reflexive-begleitforschung"></a>

## Übernommene Vorlage: Anhang C – Minimalanforderungen an sichere reflexive Begleitforschung

1.  Generierter Code wird nicht unmittelbar ausgeführt.

2.  Sicherheitskernel, Watchdog und Protokollierung liegen außerhalb der Schreibrechte untersuchter Systeme.

3.  Ressourcen, Laufzeit, Netzwerk und Aktorik sind standardmäßig begrenzt.

4.  Vor jeder strukturellen Selbstmodifikation wird ein Snapshot erzeugt.

5.  Jede Veränderung wird mit Ursache, Zeitpunkt und verantwortlicher Instanz protokolliert.

6.  Stop und Rollback bleiben unabhängig vom untersuchten Regelkreis erreichbar.

7.  Ein fehlgeschlagener Sicherheitscheck beendet den Lauf.

8.  Menschliche Freigabe setzt fachliche Prüfbarkeit und reale Ablehnungsmöglichkeit voraus.

9.  Embodiment wird stufenweise von virtueller zu physischer Kopplung erweitert.

10. Aus Systemverhalten werden keine Aussagen über Bewusstsein oder Empfindungsfähigkeit ohne separate Theorie und Evidenz abgeleitet.

<a id="b5d-anhang-e-offenes-forschungsprogramm"></a>

## Übernommene Vorlage: Anhang E – Offenes Forschungsprogramm

- Wie verändert sich semantische Grounding-Leistung zwischen E1, E3 und E5?

- Welche Architekturmerkmale bilden modellspezifische LLM-Entwurfsfingerabdrücke?

- Kann ein SNN ohne externe Reize stabile, funktional relevante interne Dynamik entwickeln?

- Welche Rolle spielen Homeostase und Energiezustände für langfristige Präferenzbildung?

- Wie lässt sich nominale von effektiver menschlicher Aufsicht empirisch unterscheiden?

- Ab welchem G-Level muss ein unabhängiger institutioneller Validator zwingend werden?

- Wie verändert virtuelle Verkörperung die Generalisierung gegenüber reinem Texttraining?

- Kann eine normative Regelhierarchie technisch gegen Selbstmodifikation geschützt werden?

- Welche Formen verteilten Verstehens genügen für wissenschaftliche Verantwortung?

- Wann wird ein KI-gestützter Forscher funktional Teil eines hybriden Erkenntnissystems?

- Welche Kriterien rechtfertigen vorsorgliche moralische Berücksichtigung bei Unsicherheit über Empfindungsfähigkeit?

- Welche Rechtsrollen müssen an Hoheitsrechte statt an traditionelle Herstellerbegriffe gekoppelt werden?

[Inhaltsuebersicht](README.md) | [Zurueck](section-040.md) | [Weiter](section-042.md)
