[Inhaltsuebersicht](README.md) | [Zurueck](section-011.md) | [Weiter](section-013.md)

<a id="b5d-hoheit-kontrolle-und-autonomierisiken"></a>

# 8. Hoheit, Kontrolle und Autonomierisiken

<a id="b5d-entscheidungshoheit-und-operatives-kontrollmodell"></a>

## Entscheidungshoheit und operatives Kontrollmodell

Kontrolle ist weder ein einzelner Schalter noch ein rein psychologisches Gefühl. Sie bezeichnet eine relationale Struktur aus Rechten, Fähigkeiten, Informationen, Zeitfenstern und technischen Eingriffspunkten. Um diese Struktur zu erfassen, werden Hoheit, Kontrollfähigkeit und Autonomierisiko getrennt modelliert. Eine Addition zu einem einzigen Gesamtscore wäre zunächst irreführend, weil ein kritischer Nullwert – etwa fehlende Interruptibilität – durch hohe Werte anderer Dimensionen verdeckt werden könnte.

*H = (G, E, B, F, M, R, A)*

Tabelle 9. Komponenten des Hoheitsvektors

| **Komponente** | **Recht**                      | **Leitfrage**                                                                    |
|:---------------|:-------------------------------|:---------------------------------------------------------------------------------|
| G              | Zielsetzungsrecht              | Wer bestimmt Zweck, Erfolgskriterien und zulässige Zieländerungen?               |
| E              | Entwurfsrecht                  | Wer erzeugt Architektur, Regeln, Code und Varianten?                             |
| B              | Bewertungsrecht                | Wer definiert und interpretiert Güte, Sicherheit und wissenschaftliche Relevanz? |
| F              | Freigaberecht                  | Wer aktiviert, publiziert oder überführt einen Entwurf in reale Nutzung?         |
| M              | Selbständerungsrecht           | Welche Komponenten dürfen sich selbst verändern?                                 |
| R              | Ressourcenrecht                | Wer verfügt über Rechenzeit, Daten, Energie, Netzwerke und Aktoren?              |
| A              | Abbruch- und Rücksetzungsrecht | Wer kann stoppen, isolieren, zurücksetzen und Zustände wiederherstellen?         |

*C = (B, O, I, V, R, P, Hc)*

Tabelle 10. Dimensionen effektiver Kontrolle

| **Dimension** | **Bezeichnung**                 | **Kriterium**                                                                                        |
|:--------------|:--------------------------------|:-----------------------------------------------------------------------------------------------------|
| B             | Begrenzbarkeit                  | Handlungs-, Raum-, Zeit- und Ressourcenraum können wirksam beschränkt werden.                        |
| O             | Beobachtbarkeit                 | relevante Zustände, Entscheidungen und Veränderungen sind erkennbar.                                 |
| I             | Interruptibilität               | das System kann rechtzeitig und unabhängig unterbrochen werden.                                      |
| V             | Reversibilität                  | Zustände und Folgen sind soweit möglich rücksetzbar oder kompensierbar.                              |
| R             | Reproduzierbarkeit              | Entwicklung und Ergebnis können mit dokumentierten Bedingungen nachgestellt werden.                  |
| P             | Provenienz                      | Herkunft von Daten, Modellen, Regeln, Prompts und Entscheidungen ist nachvollziehbar.                |
| Hc            | menschliche Entscheidungshoheit | Menschen oder legitimierte Institutionen besitzen reale, nicht nur formale Letztentscheidungsrechte. |

*U = (S, W, Q, Z, D, T)*

Tabelle 11. Autonomierisikofaktoren

| **Dimension** | **Autonomierisikofaktor**      |
|:--------------|:-------------------------------|
| S             | Selbstmodifikation             |
| W             | offener Welt- und Netzzugriff  |
| Q             | autonome Ressourcenverwendung  |
| Z             | Zielveränderung                |
| D             | dauerhafte Persistenz          |
| T             | Widerstand gegen Unterbrechung |

![Vierfelderdiagramm mit Autonomie und Selbständerungspotenzial auf der vertikalen sowie effektiver menschlicher Kontrolle auf der horizontalen Achse. Es unterscheidet Kontrollverlustrisiko, begrenzte hochautonome Systeme, schwache Kontrolle bei geringer Autonomie und gut kontrollierte Assistenzsysteme.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K3_image5.png "Kontrollierbarkeit und Autonomie")

Abbildung 2. Vierfelderdiagramm mit Autonomie und Selbständerungspotenzial auf der vertikalen sowie effektiver menschlicher Kontrolle auf der horizontalen Achse. Es unterscheidet Kontrollverlustrisiko, begrenzte hochautonome Systeme, schwache Kontrolle bei geringer Autonomie und gut kontrollierte Assistenzsysteme.

<a id="b5d-kontrollstufen-der-ki-gestützten-erzeugung-weiterer-ki"></a>

## Kontrollstufen der KI-gestützten Erzeugung weiterer KI

![Treppenförmiges Stufenmodell G0 bis G8 von menschlicher Konstruktion und KI-Assistenz über maschinellen Entwurf, Bewertung, rekursive Optimierung und adaptive Regeländerung bis zu Ziel- und Governanceänderung sowie existenzautonomer Technogenese.](../2026-09-07_ki-die-geliehene-intelligenz/abbildungen/K3_image6.png "Kontrollstufen KI-generierter KI")

Abbildung 3. Treppenförmiges Stufenmodell G0 bis G8 von menschlicher Konstruktion und KI-Assistenz über maschinellen Entwurf, Bewertung, rekursive Optimierung und adaptive Regeländerung bis zu Ziel- und Governanceänderung sowie existenzautonomer Technogenese.

Tabelle 12. Stufen KI-gestützter Systemerzeugung

| **Stufe** | **Bezeichnung**                                        | **Abgrenzung**                                                                                           |
|:----------|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|
| G0        | Menschliche Konstruktion                               | Mensch entwirft interne Struktur unmittelbar.                                                            |
| G1        | Maschinelle Assistenz                                  | KI unterstützt Recherche, Dokumentation, Codeergänzung oder Fehleranalyse.                               |
| G2        | Maschineller Teilentwurf                               | KI schlägt Komponenten, Parameter, Lernregeln oder Module vor.                                           |
| G3        | Maschineller Gesamtentwurf unter menschlicher Freigabe | vollständiger Entwurf, unabhängige menschliche Prüfung und Aktivierung.                                  |
| G4        | Maschineller Entwurf und maschinelle Bewertung         | Generator und Evaluator sind maschinell; menschliche Freigabe bleibt.                                    |
| G5        | Rekursive Optimierung                                  | System erzeugt, testet und verändert Nachfolgesysteme über mehrere Zyklen.                               |
| G6        | Adaptive Regelveränderung                              | untergeordnete Lern-, Bewertungs- oder Selektionsregeln werden verändert.                                |
| G7        | Ziel- und Governanceveränderung                        | System verändert Regeln, die Ziele, Ressourcen oder Freigaben bestimmen.                                 |
| G8        | Existenzautonome rekursive Technogenese                | materielle und informationelle Fortexistenz sowie Reproduktion ohne fortlaufende menschliche Mitwirkung. |

<a id="b5d-übernimmt-die-ki-zerlegung-einer-unpräzisen-frage"></a>

## „Übernimmt die KI?” – Zerlegung einer unpräzisen Frage

Die Formulierung „Übernimmt die KI?” verdichtet unterschiedliche Vorgänge zu einer politischen oder dystopischen Chiffre. Wissenschaftlich ist sie nur brauchbar, wenn präzisiert wird, welche Hoheit übertragen wurde. Entwurfshoheit liegt vor, wenn ein System die Struktur bestimmt; Bewertungshoheit, wenn es die Gütekriterien oder deren Interpretation kontrolliert; Freigabehoheit, wenn es seine Ergebnisse selbst aktiviert; Ressourcenhoheit, wenn es Rechenleistung, Daten, Netzwerke oder Aktoren eigenständig erschließt; Zielhoheit, wenn es übergeordnete Zwecke verändert.

Eine bedeutsame Übernahme beginnt daher nicht schon mit der Erzeugung von Code. Sie entsteht, wenn ein nichtmenschlicher Regelkreis gleichzeitig wesentliche Teile von Zielsetzung, Bewertung, Freigabe, Selbständerung und Ressourcenverwendung kontrolliert und der Mensch keine wirksame materielle oder epistemische Eingriffsmöglichkeit mehr besitzt. Die rein formale Existenz einer Freigabetaste genügt nicht, wenn ihre Bediener die Optionen nicht prüfen können oder der organisatorische Prozess faktisch keine Ablehnung zulässt.

- Formale Kontrolle: Zuständigkeit oder Unterschrift ist rechtlich zugeordnet.

- Technische Kontrolle: Eingriff, Isolation, Begrenzung und Rücksetzung sind tatsächlich möglich.

- Epistemische Kontrolle: Entscheidungsträger verstehen Evidenz, Grenzen und Folgen hinreichend.

- Institutionelle Kontrolle: Organisation, Anreize und Zeit erlauben unabhängige Prüfung.

- Effektive Kontrolle: alle erforderlichen Bedingungen wirken im konkreten Entscheidungszeitpunkt zusammen.

[Inhaltsuebersicht](README.md) | [Zurueck](section-011.md) | [Weiter](section-013.md)
