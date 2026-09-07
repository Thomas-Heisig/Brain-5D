[Inhaltsuebersicht](README.md) | [Zurueck](section-008.md) | [Weiter](section-010.md)

<a id="b5d-gegenwart-forschung-und-entwurf-durch-ki"></a>

# 5. Gegenwart: Forschung und Entwurf durch KI

<a id="b5d-forschungsstand-was-neue-systeme-zeigen-und-was-offenbleibt"></a>

## Forschungsstand: was neue Systeme zeigen und was offenbleibt

Lu et al. (2026) beschreiben in *Nature* ein System zur weitreichenden Automatisierung des KI-Forschungsprozesses. Es verbindet Ideengenerierung, experimentellen Code, Ausführung, Analyse und Manuskripterstellung. Die Publikation unterscheidet template-basierte und weiter automatisierte Verfahren. Die berichtete Begutachtung eines erzeugten Manuskripts betrifft eine erste Workshop-Reviewrunde; daraus folgt weder eine allgemeine Gleichwertigkeit mit menschlicher Forschung noch die institutionelle Verantwortungsfähigkeit des Systems. Für diese Abhandlung ist die Arbeit vor allem ein Beleg dafür, dass maschinelle Beiträge über einzelne Textvorschläge hinaus zu verketteten wissenschaftlichen Produktionsschritten verbunden werden können. \[W01\]

Ghareeb et al. (2026) untersuchen mit Robin ein Multi-Agent-System für wissenschaftliche Entdeckung. Die Verbindung von Hypothesenbildung, experimentellen Vorschlägen und Datenanalyse ist für die Frage epistemischer Agency relevant. Der Forschungsprozess ist jedoch als semi-autonom einzuordnen; die Beteiligung experimenteller Facharbeit und der konkrete Anwendungsbereich dürfen nicht aus der Beschreibung entfernt werden. Gerade die Verteilung der Beiträge macht das System für eine Analyse von Autorenschaft und Verantwortung interessant. \[W02\]

AlphaEvolve verbindet nach der technischen Darstellung von Google DeepMind Sprachmodelle, automatisierte Evaluatoren und evolutionäre Suche zur Entwicklung und Verbesserung algorithmischen Codes. Hier wird die konkrete Lösungsform teilweise maschinell erzeugt, während Aufgabenraum, Bewertung und Ressourcen institutionell gesetzt bleiben. Die Quelle ist eine Unternehmenspublikation und entsprechend zu gewichten. Sie illustriert eine begrenzte Form rekursiver technischer Gestaltung, nicht die materielle Selbstreproduktion einer unabhängigen Maschinenlinie. \[W03\]

Der Stanford AI Index 2026 bietet einen breiten Kontext zu technischer Leistung, Wirtschaft, Wissenschaft und Governance. Die offizielle Berichtsseite wurde als Quellenidentität und Gegenwartskontext geprüft. Einzelne in den Ausgangstexten angeführte Benchmark-Prozentwerte werden in dieser Synthese nicht als neu verifizierte Kennzahlen weiterverwendet. Ein benchmark-spezifischer Vergleich verlangt den jeweiligen Datensatz, Bewertungsmodus, Modellstand und die Definition der menschlichen Referenz. \[W04\]

<a id="b5d-drei-getrennte-rekursionen"></a>

## Drei getrennte Rekursionen

**Entwurfsrekursion** liegt vor, wenn ein System an einem nachfolgenden System mitarbeitet. **Bewertungsrekursion** liegt vor, wenn automatisierte Instanzen andere automatisierte Instanzen beurteilen. **Materielle Reproduktionsrekursion** würde darüber hinaus die Fortführung von Energieversorgung, Hardware, Wartung und Fertigung umfassen. Die ersten beiden Formen können in begrenzten technischen Prozessen untersucht werden, ohne die dritte vorauszusetzen. Diese Trennung wird als eigene begriffliche Synthese vorgeschlagen.

Daraus folgt ein differenzierter Begriff maschineller Eigenleistung. Ein neuer Algorithmus kann über ein automatisiertes Suchverfahren entstehen und dennoch von einer extern gesetzten Bewertungsfunktion abhängen. Eine sprachlich innovative Hypothese kann wissenschaftlich unbrauchbar sein. Ein Experiment kann automatisiert ablaufen und dennoch nur deshalb valide sein, weil Menschen Messverfahren, Kontrollen und Ausschlussregeln fachlich geprüft haben. Die These geliehener Intelligenz ist daher nicht durch einen einzelnen Leistungsrekord erledigt oder bestätigt. Sie fragt, welche Voraussetzungen einer Leistung woher stammen und wer ihre Gültigkeit beurteilen kann.

<a id="b5d-keine-fortschrittserzählung-als-ersatz-für-vergleichsdesign"></a>

## Keine Fortschrittserzählung als Ersatz für Vergleichsdesign

Die historische Reihenfolge von Automaten, lernenden Netzen und Forschungsagenten ist keine kausale Leiter zu Bewusstsein oder Souveränität. Mehr automatisierte Arbeitsschritte können die Produktivität erhöhen und gleichzeitig neue Fehlerpfade schaffen. Ein maschineller Reviewer, der denselben Modellprior und dieselbe fehlerhafte Quelle wie der Generator nutzt, ist kein unabhängiger Kritiker. Ein KI-System, das seine Aufgabenstellung verändert, kann Schwierigkeiten lösen, aber ebenso das ursprüngliche wissenschaftliche Ziel verlassen. Für Brain-5D sind deshalb Rollen- und Datenflussgrenzen mindestens so wichtig wie Funktionsumfang.

<a id="b5d-technischer-forschungsstand-snn-nas-und-llm-gestützte-architekturgenerierung"></a>

## Technischer Forschungsstand: SNN, NAS und LLM-gestützte Architekturgenerierung

<a id="b5d-spiking-neural-networks-und-neuromorphe-systeme"></a>

### Spiking Neural Networks und neuromorphe Systeme

Spiking Neural Networks modellieren Information über diskrete Ereignisse und deren zeitliche Struktur. Gegenüber klassischen künstlichen neuronalen Netzen versprechen sie insbesondere bei geeigneter Hardware eine energieeffiziente, ereignisgetriebene Verarbeitung. Gleichzeitig erschweren Nichtdifferenzierbarkeit idealisierter Spikes, zeitliche Dynamik und ein großer kombinatorischer Architekturraum Training und Entwurf. Gerstner et al. (2014) geben einen etablierten theoretischen Rahmen neuronaler Dynamik; Maass (1997) ordnet SNNs konzeptionell als neue Generation neuronaler Modelle ein.

Für die vorliegende Arbeit ist entscheidend, dass SNN-Leistung nicht allein von Gewichten abhängt. Neuronenmodell, Schwellenwerte, Refraktärzeiten, Verzögerungen, synaptische Dynamik, Plastizität und Topologie interagieren. Eine LLM-generierte SNN-Architektur muss deshalb als multidimensionales Designobjekt behandelt werden.

<a id="b5d-neural-architecture-search"></a>

### Neural Architecture Search

NAS automatisiert Teile der Architekturentwicklung. Ren et al. (2021) zeigen, dass Suchraum, Suchstrategie und Leistungsbewertung zentrale Designentscheidungen darstellen. Klassische Suchverfahren verwenden unter anderem evolutionäre Algorithmen, Reinforcement Learning, differenzierbare Suche oder Gewichtsteilung. Das Grundproblem bleibt, dass ein Suchverfahren nur Strukturen entdecken kann, die sein Suchraum zulässt.

Bei SNNs verschärft sich dies durch zusätzliche zeitliche und dynamische Parameter. Yan et al. (2024) zeigen mit einem SNN-spezifischen NAS-Ansatz, dass automatische Architekturentwicklung leistungsrelevant ist. Che et al. (2024) übertragen Architektursuche auf Spikformer-Strukturen. Der Forschungsstand rechtfertigt somit die Annahme, dass Architekturentscheidungen auch in Brain-5D nicht als bloße Implementierungsdetails behandelt werden dürfen.

<a id="b5d-llm-gestützte-architekturgenerierung"></a>

### LLM-gestützte Architekturgenerierung

LLM-basierte NAS-Forschung erweitert klassische Suchverfahren um sprachlich kodiertes Architekturwissen. Zhou et al. (2025) verwenden LLMs zur Ableitung und Übertragung von Designprinzipien. Rahman, Haider und Chakraborty (2025) demonstrieren mit LEMONADE, dass ein LLM gemeinsam mit einem Expertensystem neuronale Architekturen unter mehreren Zielgrößen iterativ erzeugen kann. Die Autoren berichten dabei ausdrücklich, dass Regeln nötig sind, um zufälliges Verhalten und Halluzinationen des Backend-LLM zu begrenzen. Damit liefert diese Arbeit einen direkten methodischen Bezugspunkt für Brain-5D: Generative Architektursynthese benötigt eine unabhängige formale Kontrollschicht.

Die offene Forschungslücke ist jedoch deutlich: Bestehende Arbeiten bewerten überwiegend Leistung, Suchkosten und Hardwareparameter. Weniger untersucht sind (a) modellfamilienspezifische Architektur-Fingerabdrücke, (b) die Provenienz der erzeugten Designentscheidungen, (c) die Verschiebung menschlicher Agency und (d) die normative Bedeutung eines Systems, das nach maschineller Konstruktion selbstorganisatorisch weiterwächst.

<a id="b5d-ki-ethik-und-governance-1"></a>

### KI-Ethik und Governance

Floridi und Cowls (2019) identifizieren eine Konvergenz zahlreicher KI-Ethikrahmen um Prinzipien wie Wohltun, Nichtschaden, Autonomie, Gerechtigkeit und Erklärbarkeit. Die UNESCO-Empfehlung von 2021 betont Menschenwürde, Rechte, Transparenz und menschliche Aufsicht. Die OECD AI Principles wurden 2024 aktualisiert und verfolgen einen menschenzentrierten Ansatz. NIST strukturiert das AI Risk Management Framework über Govern, Map, Measure und Manage; Stand 2026 wird AI RMF 1.0 überarbeitet.

Die Schwäche rein prinzipienorientierter Ethik liegt darin, dass abstrakte Werte nicht automatisch technische Kontrollmechanismen erzeugen. Die vorliegende Arbeit übersetzt deshalb normative Forderungen in messbare Systemanforderungen: Beobachtbarkeit, Unterbrechbarkeit, Reversibilität, Provenienz, Ressourcenbegrenzung und definierte Entscheidungshoheit.

<a id="b5d-autorschaft-und-erfinderschaft"></a>

### Autorschaft und Erfinderschaft

Rechtlich ist die Zuschreibung maschineller Autorschaft derzeit begrenzt. Das U.S. Copyright Office kam 2025 zu dem Ergebnis, dass generative KI-Ausgaben nur insoweit urheberrechtlichen Schutz erhalten können, wie hinreichende menschliche kreative Beiträge vorliegen; bloße Prompts genügen nicht automatisch. Im Patentrecht bestätigte die Beschwerdekammer des Europäischen Patentamts im DABUS-Verfahren, dass eine Maschine nicht Erfinder im Sinne des Europäischen Patentübereinkommens ist. Diese Rechtslage ist philosophisch nicht gleichbedeutend mit der Aussage, Maschinen könnten keinen kausalen oder epistemischen Beitrag leisten. Sie zeigt vielmehr, dass rechtliche Autorschaft und technische Urheberschaft auseinanderfallen können.

Die wissenschaftliche Neuheit darf nicht mit der bloßen Aussage begründet werden, ein LLM erzeuge ein SNN. Vitolo et al. (2024) haben bereits natürlichsprachlich gesteuerte Verilog-Erzeugung für ein rekurrentes SNN untersucht. Neural Architecture Search und SNN-spezifische Suchverfahren bilden etablierte, sich weiterentwickelnde Forschungsfelder (Elsken, Metzen, & Hutter, 2019; Ren et al., 2021; Shen et al., 2024). Der mögliche originäre Beitrag liegt daher im kontrollierten Vergleich modellspezifischer Entwurfsfingerabdrücke, der longitudinalen Beobachtung anschließender Selbstorganisation und der gleichzeitigen Analyse von Hoheit, Provenienz und Embodiment.

[Inhaltsuebersicht](README.md) | [Zurueck](section-008.md) | [Weiter](section-010.md)
