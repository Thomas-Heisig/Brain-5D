[Inhaltsuebersicht](README.md) | [Zurueck](section-017.md) | [Weiter](section-019.md)

<a id="b5d-mathematische-annahmen-und-hybrides-zustandsmodell"></a>

# 14. Mathematische Annahmen und hybrides Zustandsmodell

<a id="b5d-mathematische-annahmen-und-geltungsbedingungen"></a>

## Mathematische Annahmen und Geltungsbedingungen

<a id="b5d-funktion-der-annahmen"></a>

### Funktion der Annahmen

Mathematische Formalisierung setzt voraus, dass Modellobjekte, Zeitskalen und Beobachtungen hinreichend definiert sind. MHRN unterscheidet deshalb explizite Arbeitsannahmen von hergeleiteten Resultaten. Eine Verletzung der Annahmen macht eine Gleichung nicht technisch unbrauchbar, begrenzt aber ihre Interpretation.

<a id="b5d-annahmenkatalog"></a>

### Annahmenkatalog

Tabelle 21. Mathematische Arbeitsannahmen

| **ID**    | **Arbeitsannahme**                                                                         | **Bedeutung**                                     | **Prüfung / Sensitivität**        |
|:----------|:-------------------------------------------------------------------------------------------|:--------------------------------------------------|:----------------------------------|
| A-MATH-01 | Der materialisierte Zustand ist zu jedem Safe Point endlich.                               | Speicher, Graph und Ereignismengen sind begrenzt. | Budget- und Integritätstest       |
| A-MATH-02 | Zustandsübergänge sind bei gegebenem Zustand, Input, Parametern und RNG wohldefiniert.     | keine mehrdeutige partielle Mutation              | deterministischer Golden Run      |
| A-MATH-03 | Numerische Integration konvergiert im relevanten Parameterbereich hinreichend.             | Schrittweite erzeugt keine dominanten Artefakte.  | Schrittweiten- und Solverablation |
| A-MATH-04 | Die Metrikmatrix ist symmetrisch positiv definit oder bewusst semidefinit.                 | Distanzen sind mathematisch kontrolliert.         | Eigenwert-/Cholesky-Test          |
| A-MATH-05 | Beobachtungsfenster und Regionen sind vor Auswertung fixiert oder als explorativ markiert. | verhindert post-hoc Optimierung.                  | Registry-Prüfung                  |
| A-MATH-06 | Seeds beziehungsweise Runs sind zwischen Bedingungen austauschbar oder gepaart.            | Grundlage für Permutation und Vergleich.          | Randomisierungsprotokoll          |
| A-MATH-07 | Stationarität wird nur lokal und zeitfensterbezogen angenommen.                            | lernende Graphen sind global nichtstationär.      | Change-Point-/Driftanalyse        |
| A-MATH-08 | Decodertraining und Testdaten sind auf Episodenebene getrennt.                             | verhindert zeitliches Leakage.                    | Split-Audit                       |
| A-MATH-09 | Kausale Interventionen verändern die Zielkomponente spezifischer als gematchte Kontrollen. | Voraussetzung funktionaler Attribution.           | Manipulationscheck                |
| A-MATH-10 | Ressourcenproxies werden nicht ohne Kalibrierung als physikalische Energie bezeichnet.     | schützt vor Einheitenfehlern.                     | Hardwaremessung / Kalibration     |
| A-MATH-11 | Fehlende Daten sind explizit und nicht stillschweigend Null.                               | Null kann ein valider Sensorwert sein.            | Schema-Constraint                 |
| A-MATH-12 | Abgeleitete Metriken sind Funktionen versionierter Primärdaten.                            | Reanalyse bleibt möglich.                         | Provenienz-Trace                  |

<a id="b5d-wohldefiniertheit-und-numerische-konvergenz"></a>

### Wohldefiniertheit und numerische Konvergenz

Für ein gegebenes Modell soll die Simulation eine eindeutige Ereignisordnung besitzen. Gleichzeitige Spikes, synaptische Updates und Strukturänderungen benötigen eine festgelegte Priorität oder eine mathematisch begründete simultane Update-Regel. Andernfalls können unterschiedliche Thread- oder Datenbankreihenfolgen verschiedene wissenschaftliche Resultate erzeugen.

Numerische Konvergenz wird nicht nur über Membranpotentiale geprüft. Bei veränderter Schrittweite $\Delta t$ werden auch Spikezeiten, Populationsmetriken, Gewichtsverteilungen und funktionale Outcomes verglichen. Eine geeignete Fehlerfamilie ist

**\[EMP\]**

$$E_{\Delta t}=d\!\left(O_{\Delta t},O_{\Delta t/2}\right)$$wobei $O$ die für den Claim relevante Beobachtung bezeichnet. Exakte Spikegleichheit kann bei sensitiver Dynamik unrealistisch sein; dann sind statistische oder funktionale Konvergenzkriterien erforderlich.

<a id="b5d-identifizierbarkeit"></a>

### Identifizierbarkeit

Ein Parameter ist praktisch nicht identifizierbar, wenn verschiedene Werte oder Mechanismenkombinationen dieselben beobachteten Metriken erzeugen. MHRN begegnet diesem Problem durch Mechanismenablation, multiple Beobachtungsebenen und gezielte Intervention. Gute Vorhersage allein identifiziert nicht zwingend den richtigen Mechanismus.

<a id="b5d-dimensionslose-größen"></a>

### Dimensionslose Größen

Wo möglich werden dimensionslose Kennzahlen verwendet, etwa normierte Rate, Delay relativ zur Membranzeit oder Kosten relativ zum Budget. Dies erleichtert Größenvergleiche. Eine dimensionslose Darstellung darf physikalische Einheiten nicht verbergen; beide werden im Registry-Schema gespeichert.

<a id="b5d-modellgrenzen"></a>

### Modellgrenzen

Die Arbeitsgleichungen bilden eine Familie möglicher MHRN-Instanzen. Ein Ergebnis gilt zunächst für die konkret registrierte Instanz. Generalisierung auf andere Neuronenmodelle, Zeitschritte, Metriken oder Aufgaben erfordert eigene Evidenz.

<a id="b5d-brain-5d-als-hybrides-dynamisches-system"></a>

## MHRN als hybrides dynamisches System

<a id="b5d-zustandsraum"></a>

### Zustandsraum

**\[DEF\]** Der materialisierte MHRN-Zustand zum Simulationszeitpunkt $t$ wird als

$$X_{t} = \left( X_{t}^{N},X_{t}^{S},X_{t}^{P},X_{t}^{H},X_{t}^{E},X_{t}^{A},X_{t}^{R},X_{t}^{M} \right)$$definiert. Darin bezeichnen:

- $X_{t}^{N}$ die neuronalen Zustände, Parameter, Koordinaten und Zelltypen;

- $X_{t}^{S}$ die Synapsen, Gewichte, Verzögerungen, Typen und Eligibility Traces;

- $X_{t}^{P}$ den Zustand der Plastizitätsprozesse;

- $X_{t}^{H}$ homeostatische und metaplastische Regler;

- $X_{t}^{E}$ die Eingangs- und Sensorzustände;

- $X_{t}^{A}$ die Aktor- beziehungsweise Outputzustände;

- $X_{t}^{R}$ Ressourcen-, Energie- und Budgetzustände;

- $X_{t}^{M}$ Metadaten, Scheduler-, RNG- und Persistenzzustände.

Die Trennung ist konzeptionell. Eine Implementierung kann Daten aus Effizienzgründen anders anordnen, solange die wissenschaftlich relevanten Zustandsbestandteile rekonstruierbar bleiben.

<a id="b5d-flüsse-und-sprünge"></a>

### Flüsse und Sprünge

Spiking-Netze kombinieren kontinuierliche oder diskret integrierte Zustandsentwicklung mit diskreten Ereignissen wie Schwellenüberschreitungen, Resets und Strukturänderungen. MHRN wird daher als hybrides System modelliert ([Goebel et al., 2012](section-045.md#ref-Goebel2012Hybrid)):

**\[MODEL\]** Für kontinuierliche Phasen gilt abstrakt

$$\dot{x} = f_{q}(x,u,\xi;\theta),x \in C_{q},$$und bei einem Ereignis beziehungsweise einer Guard-Bedingung

**\[MODEL \| redaktionelle Ergänzung\]** Die angekündigte Sprunggleichung ist in K1 leer. Als allgemeine, hier ergänzte Reset-Spezifikation wird vorgeschlagen:

$$(x_{\mathrm{post}},q_{\mathrm{post}})=g_q(x,u,\xi;\theta),\quad x\in D_q$$Dabei gibt g_q den Zustands- und Moduswechsel an. Dies ist eine explizite Modellergänzung, kein rekonstruierter Originalwortlaut und kein Nachweis eines implementierten Codepfads.

$q$ beschreibt den diskreten Modus, $C_{q}$ die Flussmenge, $D_{q}$ die Sprungmenge, $u$ externe Eingaben, $\xi$ stochastische Einflüsse und $\theta$ Modellparameter. In einer vollständig diskretisierten Simulation kann dies als

$$X_{t + 1} = F_{q_{t}}\left( X_{t},U_{t},\Xi_{t};\Theta \right),q_{t + 1} = G\left( q_{t},X_{t},E_{t} \right)$$geschrieben werden. Diese Gleichungen sind Rahmenmodelle, keine Behauptung, dass alle Komponenten glatt, linear oder analytisch lösbar sind.

<a id="b5d-zeitbegriffe"></a>

### Zeitbegriffe

MHRN unterscheidet mindestens fünf Zeitdomänen:

Tabelle 22. Zeitdomänen und ihre Funktionen

| **Zeitdomäne**                 | **Symbol** | **Funktion**                                                  |
|:-------------------------------|:-----------|:--------------------------------------------------------------|
| neuronale Simulationszeit      | $$t_{n}$$  | Membranintegration, Spike-Ereignisse, synaptische Verzögerung |
| Plastizitätszeit               | $$t_{p}$$  | Eligibility, STDP, Homeostase, Gewichtsregulation             |
| Strukturzeit                   | $$t_{s}$$  | Pruning, Synapsenwachstum, Neurogenese, Reorganisation        |
| Agenten-/Episodenzeit          | $$t_{e}$$  | Wahrnehmung, Aktion, Reward, Umweltübergang                   |
| Wall-Clock- und Provenienzzeit | $$t_{w}$$  | reale Ausführung, I/O, LLM-Latenz, Logging                    |

Typischerweise gilt $t_{n} \ll t_{p} \lesssim t_{s}$, doch die Größenordnung ist eine konfigurierbare Modellannahme. $t_{w}$ darf nicht mit $t_{n}$ gleichgesetzt werden. Ein LLM-Aufruf von fünf Sekunden realer Dauer muss die neuronale Simulationszeit nicht um fünf Sekunden voranschreiten lassen.

<a id="b5d-determinismus-und-stochastik"></a>

### Determinismus und Stochastik

MHRN kann stochastische Initialisierung, probabilistische Konnektivität, Rauschen und zufällige Umweltübergänge verwenden. Reproduzierbarkeit bedeutet daher nicht zwangsläufig Bitidentität auf jeder Hardware. Es sind drei Modi zu unterscheiden:

1.  **bitnaher Replay:** gleiche Plattform, deterministische Kernel und vollständig gespeicherte RNG-Zustände;

2.  **numerischer Replay:** Abweichungen innerhalb definierter Toleranzen;

3.  **statistischer Replay:** gleiche Verteilungen und Effekte über unabhängige Seeds.

Der Reproduktionsmodus und die zulässige Toleranz gehören in die `ExperimentSpec`.

[Inhaltsuebersicht](README.md) | [Zurueck](section-017.md) | [Weiter](section-019.md)
