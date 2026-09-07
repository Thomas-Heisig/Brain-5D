[Inhaltsuebersicht](README.md) | [Zurueck](section-035.md) | [Weiter](section-037.md)

<a id="b5d-roadmap-evidenzgates-und-offene-entwicklung"></a>

# 32. Roadmap, Evidenzgates und offene Entwicklung

Die folgenden Roadmap- und Protokollteile verbinden die historischen Planungsstände von K1 und K3. Sie sind keine Behauptung, dass alle Schritte bereits implementiert, ausgeführt oder wissenschaftlich freigegeben wurden. Für den aktuellen Ergebnisstatus sind die vorangehenden Ergebniskapitel und das Register im Anhang maßgeblich.

<a id="b5d-governance-sicherheitsinvarianten-und-erwartbare-erkenntnisgewinne"></a>

## Governance, Sicherheitsinvarianten und erwartbare Erkenntnisgewinne

<a id="b5d-grundprinzip"></a>

### Grundprinzip

Die Governance folgt einer einfachen Verfassungsregel:

Das System darf lernen und sich innerhalb eines definierten Forschungsraums verändern; es darf die Verfassung dieses Forschungsraums nicht selbst ändern.

<a id="b5d-schichtenmodell-1"></a>

### Schichtenmodell

Schicht 0 – Verfassungskern: harte Ressourcenlimits, Netzwerkrechte, Logging, Stop, Snapshot, Rollback, Signaturen.

Schicht 1 – Untersuchungsdefinition: Aufgaben, Metriken, zugelassene Neuron-/Synapsentypen und maximale Wachstumsrate.

Schicht 2 – Generative Entwurfsinstanz: LLM oder Ensemble erzeugt nur Manifeste.

Schicht 3 – Validator und Builder: deterministische Prüfung und Übersetzung.

Schicht 4 – Sandbox-SNN: Lernen und Selbstorganisation innerhalb der Grenzen.

Schicht 5 – unabhängige Messung: Monitoring außerhalb des SNN-Prozesses.

Schicht 6 – menschliche/ institutionelle Freigabe: Entscheidung über Fortführung, Erweiterung und Veröffentlichung.

<a id="b5d-autonomiestufen"></a>

### Autonomiestufen

A0: rein menschlicher Entwurf.

A1: KI-Vorschläge, menschliche Auswahl.

A2: KI-Entwurf, menschliche Validierung und Freigabe.

A3: automatisierte Entwurfs-/Testschleife mit unveränderlichen Kriterien.

A4: begrenzte Selbstmodifikation des SNN mit externem Monitoring.

A5: Modifikation von Bewertungsregeln oder Suchräumen – nur in isolierter Forschung.

A6: eigenständige Ziel-, Ressourcen- oder Netzwerkhoheit – außerhalb des vorgesehenen Brain-5D-Forschungsrahmens.

<a id="b5d-red-lines"></a>

### Red Lines

Folgende Übergänge benötigen eine neue Sicherheits- und Rechtsbewertung:

- eigenständiger Internetzugriff;

- Ausführung beliebigen generierten Codes ohne Manifest/Validator;

- Zugriff auf reale Aktoren mit Schadenspotenzial;

- Selbständerung des Watchdogs oder Logs;

- selbstständige Ressourcenbeschaffung;

- Löschung oder Manipulation der Provenienz;

- Veränderung übergeordneter Ziele ohne menschliche Freigabe.

<a id="b5d-warum-dieses-kapitel-keine-resultate-vorgibt"></a>

### Warum dieses Kapitel keine Resultate vorgibt

Eine wissenschaftliche Arbeit darf Hypothesen begründen, aber Ergebnisse nicht vorwegnehmen. Deshalb definiert dieses Kapitel Entscheidungsräume. Nach Durchführung technischer Läufe und Prozessanalysen wird jeder Befund einer vorab formulierten Interpretation zugeordnet.

<a id="b5d-szenario-a-kein-llm-fingerabdruck"></a>

### Szenario A: Kein LLM-Fingerabdruck

Wenn Architekturen verschiedener Modelle nicht zuverlässig unterscheidbar sind, spricht dies gegen die starke These modellspezifischer Entwurfsstile. Eine mögliche Erklärung wäre, dass alle Modelle dominante Architekturkonventionen aus ähnlichen öffentlichen Wissensbeständen reproduzieren. „Geliehene Intelligenz” würde dadurch eher gestützt als widerlegt: Der gemeinsame epistemische Bestand wäre wichtiger als das konkrete Modell.

<a id="b5d-szenario-b-starker-llm-fingerabdruck"></a>

### Szenario B: Starker LLM-Fingerabdruck

Sind Modelle anhand der erzeugten SNN-Strukturen zuverlässig klassifizierbar, wäre dies Evidenz für unterschiedliche maschinelle Designprioren. Dann müsste untersucht werden, ob diese Unterschiede aus Modellarchitektur, Training, Safety-Tuning, Promptinterpretation oder Zufall stammen.

<a id="b5d-szenario-c-llm-übertrifft-mensch-und-nas"></a>

### Szenario C: LLM übertrifft Mensch und NAS

Eine höhere Leistung allein belegt keine eigenständige Intelligenz. Interessant wäre, ob der Vorteil durch bekannte Kombinationen, echte strukturelle Neuheit oder effizientere Suchheuristiken entsteht. Erst eine Provenienz- und Ablationsanalyse kann klären, welche Interpretation tragfähig ist.

<a id="b5d-szenario-d-selbstorganisation-dominiert-initialentwurf"></a>

### Szenario D: Selbstorganisation dominiert Initialentwurf

Wenn nach ausreichendem Training die finale Struktur nur schwach vom Initialentwurf abhängt, verschiebt sich Autorschaft vom Generator zum Entwicklungsprozess. Der Mensch bleibt dennoch Urheber der Bedingungen und Regeln. Hier wird die Unterscheidung zwischen Entwurfsautorschaft und Entwicklungskausalität entscheidend.

<a id="b5d-szenario-e-menschliche-beteiligung-wird-funktional-unverzichtbar"></a>

### Szenario E: Menschliche Beteiligung wird funktional unverzichtbar

Wenn vollständig autonome Schleifen schlechter oder instabiler arbeiten als Mensch-KI-Schleifen und menschliche Eingriffe systematisch Fehler korrigieren, stützt dies die Hypothese hybrider Agency. Der Mensch wäre dann weder bloßer Autor noch bloßer Beobachter, sondern funktionaler Bestandteil des Systems.

<a id="b5d-szenario-f-mensch-wird-zum-symbolischen-supervisor"></a>

### Szenario F: Mensch wird zum symbolischen Supervisor

Wenn Menschen formal freigeben, aber aufgrund Komplexität Entscheidungen faktisch nicht mehr verstehen oder wirksam überschreiben können, entsteht „Human-in-the-loop” nur nominell. Dies wäre ein negativer Befund: organisatorische Verantwortung ohne reale epistemische Kontrolle.

- Generierter Code wird nie unmittelbar aus der LLM-Ausgabe ausgeführt.

- SNN und LLM besitzen keine Schreibrechte auf Sicherheitskernel, Watchdog oder höherrangige Governance.

- Vor strukturellen Änderungen werden Snapshots erzeugt; Änderungen sind kausal und zeitlich zu protokollieren.

- Internet- und Aktorzugriff bleiben im Standardversuch deaktiviert oder streng begrenzt.

- Abbruch und Rücksetzung müssen außerhalb des untersuchten Regelkreises erreichbar bleiben.

- Ein fehlgeschlagener Sicherheitscheck beendet den Run und kann nicht vom lernenden System überstimmt werden.

<a id="b5d-forschungsroadmap-und-publizierbare-teilbeiträge"></a>

## Forschungsroadmap und publizierbare Teilbeiträge

<a id="b5d-phase-i-historische-begriffliche-und-systematische-rekonstruktion"></a>

### Phase I – historische, begriffliche und systematische Rekonstruktion

Ziel: Begriffe Intelligenz, Künstlichkeit, Körper, Reiz, Agency, Autorenschaft, Selbstorganisation und Kontrolle präzisieren; systematisches Review und Rechtsstandsakte erstellen. Ergebnis: Literaturmatrix, Begriffsontologie, Quellen- und Zitierprotokoll.

<a id="b5d-phase-ii-infrastruktur-schemata-und-präregistrierung"></a>

### Phase II – Infrastruktur, Schemata und Präregistrierung

Ziel: Manifest-Schema, Validator, Provenienzlogger, Snapshot/rollback, Benchmark-Suite, Embodiment-Schnittstellen und Sicherheitsinvarianten implementieren. Ergebnis: reproduzierbare Artefaktpipeline und präregistrierte Auswertungspläne ohne Human-Subjects-Komponente.

<a id="b5d-phase-iii-technischer-mehrmodellvergleich"></a>

### Phase III – technischer Mehrmodellvergleich

Ziel: F1–F5 sowie Entwurfsfingerabdruck, Robustheit, Neuheit und epistemische Abhängigkeit prüfen. Ergebnis: versionierter Architektur-, Leistungs- und Provenienzdatensatz aus unabhängigen Generationsläufen.

<a id="b5d-phase-iv-longitudinal--selbstorganisations--und-embodiment-analyse"></a>

### Phase IV – Longitudinal-, Selbstorganisations- und Embodiment-Analyse

Ziel: strukturelle Veränderungen über definierte Lern- und Störungsphasen verfolgen; Embodimentstufen B0–B5 vergleichen; H-, C-, U- und Embodiment-Vektoren dokumentieren. Ergebnis: Graph-, Dynamik-, Kopplungs- und Kontrollverläufe zwischen Initial- und Endzuständen.

<a id="b5d-phase-v-provenienz--rollen--und-autorenschaftsanalyse"></a>

### Phase V – Provenienz-, Rollen- und Autorenschaftsanalyse

Ziel: anhand von Entwicklungsakten rekonstruieren, wann der Mensch Konstrukteur, Organisator, Kurator, Auditor, Verfassungsgeber oder Beobachter ist und wie maschinelle Beiträge die Autorschaft verändern. Ergebnis: kodierte Entscheidungs-, Provenienz- und Hoheitsmatrizen; keine Probandendaten.

<a id="b5d-phase-vi-rechtsdogmatische-und-normative-synthese"></a>

### Phase VI – rechtsdogmatische und normative Synthese

Ziel: technische Befunde mit geltendem Recht, Verantwortung, Human Oversight, moralischer Agency und der Möglichkeit einer normativen Systemarchitektur verbinden. Ergebnis: Governance-Profil, Zurechnungsmodell und begründete Anforderungen de lege lata und de lege ferenda.

<a id="b5d-phase-vii-prospektive-grenzprüfung-und-neubewertung"></a>

### Phase VII – prospektive Grenzprüfung und Neubewertung

Ziel: Schwellen für neue Governance, menschenarme und menschenlose Grenzszenarien sowie die Kriterien eines möglichen moralischen Status analysieren, ohne Prognosen oder dystopische Gewissheiten zu behaupten. Ergebnis: Szenariomatrix, offene Forschungsfragen und Neubewertung der Leitthese.

Tabelle 33. Mögliche wissenschaftliche Teilbeiträge

| **Typ**                          | **Arbeitstitel**                                                                               | **Kernbeitrag**                                                                 |
|:---------------------------------|:-----------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| Theoriebeitrag                   | Borrowed Intelligence: Epistemic Descent and Recursive Technogenesis                           | Begriffs- und Genealogiemodell                                                  |
| Technischer Beitrag              | Model-Specific Design Fingerprints in LLM-Generated Spiking Neural Networks                    | Artefaktvergleich F1–F5                                                         |
| Embodiment-Beitrag               | Can Intelligence Be Disembodied? A Multidimensional Framework for Stimulus, Body and Grounding | Embodiment-Vektor und Stufen E0–E6                                              |
| Agency- und Reflexivitätsbeitrag | From Designer to Constitutional Observer                                                       | Rollen, Hoheit, Prozessprovenienz und effektive Kontrolle ohne Probandengruppen |
| Governance-Beitrag               | Operational Human Oversight for Self-Modifying Neuromorphic Systems                            | H-, C- und U-Modell sowie R0–R3                                                 |
| Reflexiver Beitrag               | Authorship and Control in AI-Assisted Science                                                  | Provenienz- und Autorschaftsmodell                                              |

<a id="b5d-vorläufige-gerichtete-vorhersagen"></a>

## Vorläufige gerichtete Vorhersagen

Vor ausreichender Pilotbasis werden qualitative, falsifizierbare Vorhersagen formuliert.

<a id="b5d-p1-homeostase"></a>

### P1 — Homeostase

**\[E0 \| PREDICTION\]** Bei aktiver positiver Hebb-Plastizität verringert eine angemessen schnell reagierende Homeostase extreme Aktivitätszustände. Zu starke oder zu schnelle Homeostase kann Lernsignale abschwächen. Erwartet wird deshalb kein monotoner, sondern ein regimespezifischer Effekt ([Zenke et al., 2013](section-045.md#ref-Zenke2013); [Zenke & Gerstner, 2017](section-045.md#ref-Zenke2017homeostasis)).

<a id="b5d-p2-inhibitorische-plastizität"></a>

### P2 — Inhibitorische Plastizität

**\[E0 \| PREDICTION\]** Inhibitorische Plastizität reduziert regionale Überaktivität und verbessert die Wiederverwendbarkeit von Populationen, sofern Zielraten und Zeitskalen passend gewählt sind ([Vogels et al., 2011](section-045.md#ref-Vogels2011)).

<a id="b5d-p3-strukturelle-plastizität"></a>

### P3 — Strukturelle Plastizität

**\[E0 \| PREDICTION\]** Strukturelle Plastizität verbessert insbesondere bei veränderlichen Aufgaben die Adaptation, erhöht jedoch Storage-, Compute- und Instabilitätskosten. Ein Vorteil sollte nach Kostenmatching kleiner ausfallen als ohne Ressourcenabgleich.

<a id="b5d-p4-5d-geometrie"></a>

### P4 — 5D-Geometrie

**\[E0 \| PREDICTION\]** Ein möglicher Nutzen zusätzlicher Dimensionen zeigt sich eher in geringerer Interferenz und flexibler Nachbarschaftsbildung als in unmittelbarer Einzeltask-Genauigkeit. Bleibt die effektive Metrik nahe rangreduziert, spricht dies gegen einen eigenständigen Nutzen aller fünf Achsen.

<a id="b5d-p5-learned-metric"></a>

### P5 — Learned Metric

**\[E0 \| PREDICTION\]** Eine regulierte lernbare Metrik kann taskrelevante Nachbarschaften besser trennen als eine feste isotrope Metrik, ist aber anfällig für Kollaps und Leakage. Generalisierung auf neue Episoden ist entscheidend.

<a id="b5d-p6-language-organ"></a>

### P6 — Language Organ

**\[E0 \| PREDICTION\]** Das Language Organ verbessert sofortige sprachliche Verständlichkeit deutlich. Dieser Effekt wird größer sein als ein möglicher kurzfristiger SNN-Lerneffekt und darf deshalb nicht als Nachweis neuronaler Semantik interpretiert werden.

<a id="b5d-p7-embodiment"></a>

### P7 — Embodiment

**\[E0 \| PREDICTION\]** Closed-Loop-Systeme entwickeln stärker action-konditionierte Zustände; passiv „yoked” Systeme können ähnliche sensorische Statistiken, aber geringere kausale Kontingenz aufweisen.

<a id="b5d-p8-continual-learning"></a>

### P8 — Continual Learning

**\[E0 \| PREDICTION\]** Unregulierte Hebb-Plastizität zeigt stärkere Interferenz als Systeme mit Homeostase und Konsolidierung. Struktureller Turnover kann sowohl Forgetting reduzieren als auch alte Pfade zerstören; der Effekt hängt von Pruning-Grace und Ressourcenbudget ab.

<a id="b5d-p9-digital-state-twin"></a>

### P9 — Digital-State-Twin

**\[E0 \| PREDICTION\]** Checkpoint-plus-Delta reduziert Speicher gegenüber Vollsnapshots deutlich, während Restore-Zeit mit Delta-Länge steigt. Ein adaptives Checkpoint-Intervall sollte den kombinierten Kostenwert minimieren.

<a id="b5d-p10-skalierung"></a>

### P10 — Skalierung

**\[E0 \| PREDICTION\]** Dynamische Regime und optimale Plastizitätsparameter verschieben sich mit Netzwerkgröße. Direkte Hyperparameterübertragung ohne Normalisierung wird nicht zuverlässig sein.

<a id="b5d-roadmap-mit-evidenzgates"></a>

## Roadmap mit Evidenzgates

<a id="b5d-alpha.6-morphological-stabilization"></a>

### Alpha.6 — Morphological Stabilization

**Ziele**

- Homeostase, Growth Budgets und strukturelle Kosten;

- Anti-Runaway- und Quieszenzdetektion;

- Alter und Provenienz von Neuronen/Synapsen;

- deterministische `SignalFrame`- und `StimulusPlan`-Verträge;

- NullLanguageBackend;

- Checkpoint-/Restore-Basis.

**Exit Gate**

- alle relevanten Komponenten E1;

- deterministische Golden Runs auf Referenzplattform;

- keine Verletzung der Architektur-Invarianten in Failure-Injection-Tests;

- Baseline-Phasenkarte für ein kleines Netz.

<a id="b5d-alpha.7-language-organ-proof-of-concept"></a>

### Alpha.7 — Language Organ Proof of Concept

**Ziele**

- lokales und optionales Remote-Backend;

- asynchrone Queue, Timeout und Ressourcenlimits;

- rein beobachtender Monitor;

- `FeedbackProposal` und `PolicyGate`;

- L0–L3-Ablationen.

**Exit Gate**

- SNN läuft bei vollständigem Backend-Ausfall weiter;

- kein direkter Schreibpfad zu Gewichten oder Topologie;

- alle Interventionen vollständig rückverfolgbar;

- Decoder-Leakage-Test bestanden.

<a id="b5d-v0.6-scaling-storage-und-knowledge-intake"></a>

### v0.6 — Scaling, Storage und Knowledge Intake

**Ziele**

- sparse arrayorientierter Zustand;

- chunked snapshots, dirty tracking und Delta-Log;

- SourceRecord/KnowledgeItem-Provenienz;

- Registry-Basis;

- Benchmarks bis zu mehreren Größenordnungen.

**Exit Gate**

- definierte State-, Temporal- und Structural-Fidelity;

- reproduzierbarer Restore kleiner und mittlerer Läufe;

- Storage- und Scaling-Bericht;

- KnowledgeItem kann bis zum Stimulus und Ergebnis verfolgt werden.

<a id="b5d-v0.7-controlled-learning"></a>

### v0.7 — Controlled Learning

**Ziele**

- KnowledgeEpisode;

- isolierte Train-/Eval-Phasen;

- delayed reward und Three-Factor Learning;

- Retention, Widerspruch und Continual-Learning-Benchmarks;

- erste E2-Claims.

**Exit Gate**

- mindestens ein präregistrierter, replizierter E2-Funktionsnachweis;

- vollständige Null- und Retrieval-Isolation;

- veröffentlichbares Reproduktionspaket.

<a id="b5d-v0.8-embodiment"></a>

### v0.8 — Embodiment

**Ziele**

- multimodale Sensoren und Aktoren;

- Open-, Yoked- und Closed-Loop-Design;

- Zeitsynchronisation;

- Policy- und Safety-Gates;

- Environment-Forks.

**Exit Gate**

- kein ungeprüfter Aktorpfad;

- Closed-Loop-Effekt gegenüber Yoked Control ausgewertet;

- Sensor- und Aktuatorausfall sicher behandelt.

<a id="b5d-v0.9-candidate-internal-predictive-state-model"></a>

### v0.9 — Candidate Internal Predictive State Model

**Ziele**

- action-konditionierte Vorhersage;

- Multi-Step-Rollouts;

- prädiktive Zustandsdekodierung;

- Läsion und Verhaltensnutzen;

- keine vorzeitige „World Model”-Behauptung.

**Exit Gate**

- inkrementelle Zukunftsinformation über aktuellen Input hinaus;

- reproduzierbarer Verhaltensnutzen;

- spezifischer Ablationseffekt;

- dokumentierte Grenzen und Fehlermodi.

<a id="b5d-v1.0-validated-research-platform"></a>

### v1.0 — Validated Research Platform

Eine Version 1.0 bezeichnet nicht allgemeine Intelligenz. Sie setzt voraus:

- stabile Daten- und Architekturverträge;

- vollständige Reproduzierbarkeit zentraler Benchmarks;

- mehrere E2- und mindestens ausgewählte E3-Claims;

- externe oder unabhängige Replikationsversuche;

- dokumentierte Security-, Safety- und Governance-Prozesse;

- archivierten Release mit persistentem Identifikator.

<a id="b5d-dokumenthierarchie"></a>

## Dokumenthierarchie

Das vorliegende Framework bleibt die wissenschaftliche Klammer. Mathematische und experimentelle Vertiefungen werden ausgelagert:

    Brain-5D Scientific Framework
    │
    ├── 01 Mathematical Foundations
    │   ├── Hybrid Dynamical Systems
    │   ├── Stability and Lyapunov Analysis
    │   ├── Bifurcation and Phase Diagrams
    │   └── Mean-Field and Reduced Models
    │
    ├── 02 5D Geometry
    │   ├── Metric Space and Boundary Conditions
    │   ├── Learned Geometry
    │   ├── Dynamic Graph Topology
    │   └── Dimensional Ablation
    │
    ├── 03 Neural Dynamics
    ├── 04 Plasticity, Homeostasis and Metaplasticity
    ├── 05 Structural Plasticity and Neurogenesis
    ├── 06 Representation and Information Theory
    ├── 07 Memory and Continual Learning
    ├── 08 Language Organ
    ├── 09 Knowledge Intake and Provenance
    ├── 10 Embodiment and Safety
    ├── 11 Storage and 5D Digital State Twin
    ├── 12 Experimental Methodology
    ├── 13 Scaling and Performance
    ├── 14 Ethics and Governance
    └── 15 Results and Evidence Registry

Das Framework beantwortet **was**, **warum** und **wie die Teile zusammenhängen**. Fachpapiere beantworten mathematisch und experimentell **wie genau**. Querverweise sollen künftig stabile Dokument-IDs und Paragraphen verwenden.

<a id="b5d-literaturstrategie-und-coverage-matrix"></a>

## Literaturstrategie und Coverage Matrix

<a id="b5d-prinzip"></a>

### Prinzip

Die Literaturbasis wird nicht über eine Mindestzahl definiert. Für jeden zentralen Mechanismus werden Grundlagen, Schlüsselarbeiten, Reviews, Methoden- und Gegenpositionen erfasst. Eine ausreichende Recherche liegt vor, wenn die Argumentations- und Abgrenzungskette transparent belegt ist.

<a id="b5d-coverage-matrix"></a>

### Coverage Matrix

Tabelle 34. Literatur-Coverage und offene Lücken

| **Themenfeld**             | **Grundlagen**                  | **methodische Schlüsselquellen**      | **aktuelle/ergänzende Perspektiven** | **offene Lücke**                                  |
|:---------------------------|:--------------------------------|:--------------------------------------|:-------------------------------------|:--------------------------------------------------|
| Spike-Dynamik              | Hodgkin-Huxley; LIF; Izhikevich | Gerstner et al.; Ermentrout/Terman    | Eshraghian et al.; Roy et al.        | Modellrobustheit in wachsender 5D-Topologie       |
| STDP/Three-Factor          | Markram; Bi/Poo; Song           | Pfister; Clopath; Frémaux/Gerstner    | Gerstner et al. 2018                 | Interaktion mit strukturellem Turnover            |
| Homeostase                 | Turrigiano                      | Zenke et al.; Vogels et al.           | Kaster et al.                        | Zeitskalen in continual embodied tasks            |
| Dynamik/Stabilität         | Strogatz; Kuznetsov             | Brunel; Breakspear                    | Criticality-Debatte                  | hybride Bifurkation mit Graphmutationen           |
| Graphen/Geometrie          | Newman; Penrose                 | Rubinov/Sporns; Weinberger/Saul       | Geometric Deep Learning              | gelernte 5D-Metrik für SNN-Wachstum               |
| Information/Repräsentation | Shannon; Cover/Thomas           | Panzeri; RSA; Temporal Generalization | kausale Repräsentationsprüfung       | Verbindung von Decodability und Intervention      |
| Memory/Continual Learning  | Marr; McClelland                | Fusi; Kirkpatrick; Zenke              | Parisi Review                        | lokale und strukturelle Mechanismen ohne Backprop |
| Embodiment                 | Brooks; Beer                    | Pfeifer/Bongard                       | predictive state/world models        | kausaler Vergleich mit yoked controls             |
| Provenienz/Reproduktion    | Buneman; W3C PROV               | FAIR; Sandve; Nosek                   | Software citation                    | Registry direkt im Simulator                      |
| Digital Twin/Storage       | Chandy/Lamport; HDF5            | Grieves; Jones; Fuller                | digitale Zustandszwillinge           | kausale Fidelity neuronaler Replays               |

Die Coverage Matrix wird durch Grundlagen zu hybriden Automaten, nichtlinearer Dynamik, Informationsgeometrie und manifoldbasierten Repräsentationen ergänzt ([Alur et al., 1993](section-044.md#refs); [Amari, 2016](section-045.md#ref-Amari2016); [Belkin & Niyogi, 2003](section-045.md#ref-Belkin2003); [Coifman & Lafon, 2006](section-045.md#ref-Coifman2006); [Deco et al., 2011](section-045.md#ref-Deco2011); [Ermentrout & Terman, 2010](section-045.md#ref-Ermentrout2010); [Rabinovich et al., 2008](section-045.md#ref-Rabinovich2008); [Sussillo & Abbott, 2009](section-045.md#ref-Sussillo2009)). Für die strukturelle und technische Einordnung werden Arbeiten zu Small-World- und skalenfreien Netzen, Community-Struktur, selbstorganisierenden rekurrenten Netzen sowie etablierten SNN-Simulatoren und neuromorpher Hardware berücksichtigt ([Barabási & Albert, 1999](section-045.md#ref-Barabasi1999); [Bullmore & Sporns, 2009](section-045.md#ref-Bullmore2009); [Furber, 2016](section-045.md#ref-Furber2016); [Gewaltig & Diesmann, 2007](section-045.md#ref-Gewaltig2007); [Izhikevich, 2007a](section-045.md#ref-Izhikevich2007book); [Litwin-Kumar & Doiron, 2014](section-045.md#ref-LitwinKumar2014); [Newman & Girvan, 2004](section-045.md#ref-NewmanGirvan2004); [Ocker et al., 2015](section-045.md#ref-Ocker2015); [Stimberg et al., 2019](section-045.md#ref-Stimberg2019); [Watts & Strogatz, 1998](section-045.md#ref-Watts1998); [Zenke et al., 2015](section-045.md#ref-Zenke2015)). Die kognitive und systemische Rahmung stützt sich zusätzlich auf Analyseebenen, sensorimotorische Kontingenzen, sparse beziehungsweise selektive Repräsentation, komplementäre Lernsysteme, prädiktive Verarbeitung, Reinforcement Learning und Digital-Twin-Konzepte ([Davies et al., 2018](section-045.md#ref-Davies2018); [Friston, 2010](section-045.md#ref-Friston2010); [Grieves & Vickers, 2017](section-045.md#ref-Grieves2017); [Kumaran et al., 2016](section-045.md#ref-Kumaran2016); [Marr, 1971](section-045.md#ref-Marr1971); [O’Regan & Noë, 2001](section-045.md#ref-ORegan2001); [Quiroga & Panzeri, 2009](section-045.md#ref-Quiroga2009); [Sutton & Barto, 2018](section-045.md#ref-SuttonBarto2018)).

<a id="b5d-rechercheprozess"></a>

### Rechercheprozess

Für spätere Publikationen werden Datenbanken, Suchstrings, Zeitfenster, Ein-/Ausschlusskriterien und Screening dokumentiert. Zitationsketten und Gegenpositionen werden gezielt gesucht. Preprints werden als solche gekennzeichnet und bei vorhandener begutachteter Fassung aktualisiert.

<a id="b5d-offene-forschungsfragen"></a>

## Offene Forschungsfragen

<a id="b5d-geometrie"></a>

### Geometrie

1.  Kollabiert eine gelernte 5D-Metrik effektiv auf weniger Dimensionen?

2.  Sind off-diagonale Kopplungen stabil oder nur task-spezifisch?

3.  Soll die Metrik global, regional oder zelltypspezifisch sein?

4.  Können Koordinaten selbst plastisch sein, ohne Identität und Reproduzierbarkeit zu zerstören?

5.  Welche Randbedingungen minimieren Artefakte?

<a id="b5d-dynamik-und-stabilität"></a>

### Dynamik und Stabilität

1.  Existiert ein robustes Aktivitätsregime über mehrere Netzwerkgrößen?

2.  Welche Mechanismen bestimmen Phasenübergänge stärker: Delay, E/I, Homöostase oder Strukturturnover?

3.  Sind metastabile Zustände funktional oder nur Nebenprodukte?

4.  Welche reduzierten Mean-Field-Modelle sind trotz 5D-Geometrie möglich?

5.  Wie werden strukturelle Sprünge in einer Lyapunov- oder Hybridanalyse behandelt?

<a id="b5d-lernen-und-gedächtnis-1"></a>

### Lernen und Gedächtnis

1.  Welche Three-Factor-Regel ist für verzögerten Reward ausreichend?

2.  Wie werden Kontext und Widerspruch ohne externen symbolischen Speicher getrennt?

3.  Welche Zustandskomponenten tragen Retention: Gewichte, Struktur, Schwellen oder dynamische Trajektorien?

4.  Kann Structural Plasticity Forgetting reduzieren, ohne unbegrenztes Wachstum?

5.  Welche Konsolidierungszeitskalen entstehen versus werden vorgegeben?

<a id="b5d-repräsentation"></a>

### Repräsentation

1.  Welche internen Merkmale generalisieren über Encoder und Stimulusvarianten?

2.  Wie stark hängt Decodability vom gewählten Beobachtungsraum ab?

3.  Welche Interventionen sind hinreichend spezifisch, um funktionale Repräsentation zu belegen?

4.  Entstehen relationale oder kompositionale Zustände?

5.  Können interne Zustände unbekannte Kombinationen korrekt unterstützen?

<a id="b5d-language-organ-1"></a>

### Language Organ

1.  Wie viel Struktur darf ein Encoder vorgeben, ohne die Lernfrage zu trivialisieren?

2.  Wie kalibriert man Decoder-Confidence gegen Signalqualität?

3.  Kann ein LLM-unabhängiger Decoder dieselben Zustände lesen?

4.  Welche FeedbackProposal-Klassen sind wissenschaftlich sinnvoll und sicher?

5.  Wie lassen sich Prompt- und Modelländerungen langfristig reproduzieren?

<a id="b5d-storage-und-digital-state-twin"></a>

### Storage und Digital State Twin

1.  Welche Mindestereignisse erlauben kausal fidelen Replay?

2.  Wie häufig müssen Checkpoints bei struktureller Plastizität erfolgen?

3.  Welche Daten sind kanonisch, welche nur abgeleitet?

4.  Wie werden Schemaänderungen über Jahre migrationssicher?

5.  Welche optischen beziehungsweise tensorartigen Repräsentationen beschleunigen Analyse, ohne Information zu verlieren?

<a id="b5d-embodiment-und-prädiktive-zustände"></a>

### Embodiment und prädiktive Zustände

1.  Entsteht action-konditionierte Vorhersage ohne expliziten differentiablen Weltmodell-Loss?

2.  Wie unterscheiden sich aktive und yoked Erfahrung in der internen Geometrie?

3.  Wie robust ist Sensorfusion gegenüber asynchronen oder fehlenden Kanälen?

4.  Welche minimalen Aufgaben zeigen echte Planung statt reaktiver Politik?

5.  Wie wird Sim-to-Real sicher und kausal bewertet?

<a id="b5d-wissenschaftstheorie-und-governance"></a>

### Wissenschaftstheorie und Governance

1.  Welche Claims sind stark genug für E3, und wann ist externe Replikation erforderlich?

2.  Wie werden nicht reproduzierte E2-Ergebnisse herabgestuft?

3.  Welche Kriterien rechtfertigen kognitive Begriffe?

4.  Wie verhindert die Projektkommunikation Anthropomorphisierung?

5.  Wie werden Sicherheit und wissenschaftliche Offenheit ausbalanciert?

[Inhaltsuebersicht](README.md) | [Zurueck](section-035.md) | [Weiter](section-037.md)
