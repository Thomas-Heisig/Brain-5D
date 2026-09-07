[Inhaltsuebersicht](README.md) | [Zurueck](section-021.md) | [Weiter](section-023.md)

<a id="b5d-stabilität-attraktoren-emergenz-und-kausalität"></a>

# 18. Stabilität, Attraktoren, Emergenz und Kausalität

<a id="b5d-stabilität-attraktoren-metastabilität-und-bifurkation"></a>

## Stabilität, Attraktoren, Metastabilität und Bifurkation

<a id="b5d-stabilität-als-mehrdimensionales-konstrukt"></a>

### Stabilität als mehrdimensionales Konstrukt

Stabilität bedeutet in Brain-5D nicht „keine Veränderung”. Ein lernfähiges System soll auf Inputs reagieren und langfristig adaptieren. Es sind mindestens folgende Stabilitätsdimensionen zu unterscheiden:

- **numerische Stabilität:** Integration und Datenstrukturen bleiben innerhalb technischer Grenzen;

- **dynamische Stabilität:** Zustände bleiben in einem zulässigen Bereich;

- **statistische Stationarität:** ausgewählte Verteilungen verändern sich nicht unkontrolliert;

- **funktionale Stabilität:** erworbene Leistung bleibt trotz Störungen erhalten;

- **strukturelle Stabilität:** Graphwachstum und Turnover bleiben budgetiert;

- **adaptive Stabilität:** das System kann auf neue Anforderungen reagieren, ohne frühere Funktion vollständig zu verlieren.

<a id="b5d-lokale-lineare-analyse"></a>

### Lokale lineare Analyse

Für eine glatte diskrete Abbildung $x_{t + 1} = F\left( x_{t} \right)$ und einen Fixpunkt $x^{\star}$ mit $F\left( x^{\star} \right) = x^{\star}$ ist lokale asymptotische Stabilität gegeben, wenn

**\[MODEL/THEOREM-CONDITION\]**

$$\rho\left( J_{F}\left( x^{\star} \right) \right) < 1,$$wobei $\rho$ der Spektralradius ist. Für kontinuierliche Systeme verlangt die lineare Näherung negative Realteile der Eigenwerte. Spikes, Resets, diskrete Strukturänderungen und stochastische Inputs verletzen jedoch häufig die Voraussetzungen einer einfachen glatten Analyse. Die Bedingung ist daher nur lokal und komponentenbezogen nutzbar ([Kuznetsov, 2004](section-045.md#ref-Kuznetsov2004); [Strogatz, 2015](section-045.md#ref-Strogatz2015)).

<a id="b5d-empirische-perturbationsanalyse"></a>

### Empirische Perturbationsanalyse

Für das Gesamtsystem wird eine perturbationsbasierte Stabilitätsmetrik vorgeschlagen:

**\[EMP\]**

$$D(\tau) = E\left\lbrack \parallel \Phi_{\tau}\left( X_{t} + \delta \right) - \Phi_{\tau}\left( X_{t} \right) \parallel \right\rbrack,$$wobei $\Phi_{\tau}$ die Entwicklung über $\tau$ Schritte bezeichnet. Je nach Fragestellung wird $D$ auf Zustände, Aktivitätsverteilungen, Graphstruktur oder Verhalten angewandt. Wächst $D$ exponentiell, kann dies auf sensitive Dynamik hinweisen; eine begrenzte Divergenz kann zugleich für reichhaltige Berechnung nützlich sein.

<a id="b5d-attraktoren-und-transiente-berechnung"></a>

### Attraktoren und transiente Berechnung

Klassische assoziative Speicher verwenden Attraktoren ([Hopfield, 1982](section-045.md#ref-Hopfield1982)). Reservoir- und Liquid-State-Ansätze nutzen dagegen reichhaltige transiente Zustände ohne notwendige Konvergenz auf einen Fixpunkt ([Lukoševičius & Jaeger, 2009](section-045.md#ref-Lukosevicius2009); [Maass et al., 2002](section-045.md#ref-Maass2002LSM)). Brain-5D setzt daher nicht voraus, dass Gedächtnis stets ein statischer Attraktor ist. Kandidaten sind:

- Fixpunkt- oder Grenzzyklusattraktoren;

- metastabile Zustände mit endlicher Verweilzeit;

- wiederkehrende Trajektorien;

- verteilte synaptische Konsolidierung;

- cue-induzierte Rekonstruktion ohne dauerhafte Aktivität.

<a id="b5d-bifurkations--und-phasenkarten"></a>

### Bifurkations- und Phasenkarten

Ein Parametervektor $\vartheta$ kann Lernrate, E/I-Verhältnis, Homöostasezeit, Delay, Rauschstärke, Konnektivität und Ressourcenbudgets umfassen. Brain-5D soll empirische Phasenkarten erstellen:

$$\Pi(\vartheta) \in \{\text{silent},\text{irregular},\text{metastable},\text{synchronous},\text{runaway},\text{resource-collapse}\}.$$Klassen und Schwellen werden vorab operationalisiert. Übergänge sind nicht automatisch mathematische Bifurkationen; dieser Begriff wird nur verwendet, wenn eine qualitative Änderung unter systematischer Parametervariation und geeigneter Analyse nachgewiesen ist.

<a id="b5d-kritikalität"></a>

### Kritikalität

Neuronale Kritikalität ist eine einflussreiche, aber kontrovers diskutierte Hypothese ([Beggs & Plenz, 2003](section-045.md#ref-Beggs2003); [Shew & Plenz, 2013](section-045.md#ref-Shew2013); [Wilting & Priesemann, 2019](section-045.md#ref-Wilting2019)). Brain-5D behandelt „kritisch” weder als Synonym für intelligent noch als vorgegebenes Optimierungsziel. Kandidatenmaße sind Avalanche-Verteilungen, Branching Ratio, Suszeptibilität und Korrelationslänge. Erforderlich sind Finite-Size-Analysen, Subsampling-Kontrollen, alternative Verteilungsmodelle und ein Vergleich mit nichtkritischen Systemen. Ein Potenzgesetz-Fit allein genügt nicht.

<a id="b5d-anti-oszillation-und-regelung"></a>

### Anti-Oszillation und Regelung

Technische Anti-Oszillationsregeln können Aktivität begrenzen, aber zugleich funktionale Oszillationen zerstören. Jede Regel muss deshalb eine Zielgröße, Bandbreite und Interventionsschwelle besitzen. Eine Safety-Regel darf harte Grenzwerte durchsetzen; eine lernbezogene Homöostase soll dagegen graduell und analysierbar wirken.

<a id="b5d-messbare-emergenz-und-kausalität"></a>

## Messbare Emergenz und Kausalität

<a id="b5d-emergenz-ist-keine-erklärung"></a>

### Emergenz ist keine Erklärung

Der Ausdruck „emergent” bezeichnet nicht automatisch einen unbekannten, wertvollen oder intelligenten Prozess. **\[DEF\]** Ein makroskopisches Phänomen $Y$ ist im schwachen methodischen Sinn emergent, wenn es aus lokalen Regeln und Zuständen

$$Y = f\left( X_{1},\ldots,X_{n} \right)$$hervorgeht, ohne als identische globale Zielstruktur direkt implementiert worden zu sein, und wenn seine Beschreibung auf Makroebene zusätzlichen analytischen Nutzen besitzt ([Bedau, 1997](section-045.md#ref-Bedau1997)). Dies ist eine Arbeitsdefinition, keine metaphysische Festlegung.

<a id="b5d-drei-emergenzstufen"></a>

### Drei Emergenzstufen

Tabelle 23. Ebenen messbarer Emergenz

| **Stufe**   | **Kriterium**                                                                                   | **Beispiel**                         | **Erforderlicher Test**                   |
|:------------|:------------------------------------------------------------------------------------------------|:-------------------------------------|:------------------------------------------|
| strukturell | nicht vorgegebene Cluster, Regionen oder Motive entstehen                                       | stabile Community nach Lernen        | Nullmodelle, Persistenz, Seed-Replikation |
| dynamisch   | nicht direkt programmierte Oszillation, Sequenz, Metastabilität oder Attraktorstruktur entsteht | wiederkehrende Aktivitätstrajektorie | Phasen-/Perturbationsanalyse              |
| funktional  | entstandene Struktur oder Dynamik verbessert eine Aufgabe oder beeinflusst Verhalten            | Cluster trägt spezifisch Recall      | Intervention, matched lesion, Rescue      |

Strukturelle oder dynamische Emergenz ist nicht automatisch funktional.

<a id="b5d-interventionelle-prüfung"></a>

### Interventionelle Prüfung

Für einen Kandidaten $C$ und Leistung $Q$ wird ein durchschnittlicher kausaler Effekt formalisiert als

**\[DEF/MODEL\]**

$${ACE}_{C} = E\left\lbrack Q|do(C = 1) \right\rbrack - E\left\lbrack Q|do(C = 0) \right\rbrack.$$In Simulationen kann `do(C=0)` etwa bedeuten: Cluster deaktivieren, interne Kanten entfernen, Spike-Ausgabe blockieren oder Gewichte permutieren. Die Intervention soll die Kandidatenstruktur möglichst spezifisch verändern. Eine unspezifische Läsion, die lediglich Gesamtaktivität reduziert, ist keine hinreichende Kausalanalyse ([Pearl, 2009](section-045.md#ref-Pearl2009); [Woodward, 2003](section-045.md#ref-Woodward2003)).

<a id="b5d-matched-lesions-und-rescue"></a>

### Matched Lesions und Rescue

Zu jeder gezielten Läsion werden Kontrollläsionen mit gleicher Knotenanzahl, ähnlicher Aktivität, gleichem Grad und vergleichbarer räumlicher Lage erzeugt. Ein stärkerer Effekt der gezielten Läsion stützt funktionale Spezifität. Ein anschließender Rescue-Test kann prüfen, ob Wiederherstellung der Struktur oder Ersatzstimulation die Leistung zurückbringt.

<a id="b5d-makroebenen-und-kausale-emergenz"></a>

### Makroebenen und kausale Emergenz

Theorien kausaler Emergenz untersuchen, ob eine Makrobeschreibung kausal informativer sein kann als eine mikroskopische Beschreibung ([Hoel et al., 2013](section-045.md#ref-Hoel2013)). Brain-5D kann dies explorieren, darf aber Makroüberlegenheit nicht aus besserer Kompression allein ableiten. Makrozustände, Interventionsverteilung und Effektmaß müssen explizit festgelegt werden.

<a id="b5d-kausalgraph-des-gesamtsystems"></a>

### Kausalgraph des Gesamtsystems

Ein vereinfachter Kausalgraph enthält mindestens:

$$\text{Stimulus} \rightarrow X_{t} \rightarrow \text{Action} \rightarrow \text{Environment}_{t + 1},$$sowie Plastizität, Reward, LLM-Interventionen, Retrieval und Scheduler als potenzielle Ursachen. Nicht beobachtete gemeinsame Ursachen, etwa globale Modulatoren, müssen in der Analyse berücksichtigt werden. Die hohe Beobachtbarkeit einer Simulation erleichtert, aber garantiert keine korrekte Kausalinferenz.

[Inhaltsuebersicht](README.md) | [Zurueck](section-021.md) | [Weiter](section-023.md)
