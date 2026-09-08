[Inhaltsuebersicht](README.md) | [Zurueck](section-031.md) | [Weiter](section-033.md)

<a id="b5d-kompakte-daten-berichtstreue-und-epistemische-kontrolle"></a>

# 28. Kompakte Daten, Berichtstreue und epistemische Kontrolle

<a id="b5d-kompaktierung-als-epistemische-schnittstelle"></a>

## Kompaktierung als epistemische Schnittstelle

Ein kleineres Sprachmodell sollte nicht bei jedem Lauf eine ständig anwachsende Gesamtdatei mit allen historischen Run-Details verarbeiten müssen. Die Projektdokumentation sieht deshalb immutable, komprimierte Rohartefakte, eine begrenzte aktuelle `runs.json`-Projektion und ein kompaktes `analysis/ai_packet.json` vor. Das kompakte Paket ist eine Sicht auf Daten, nicht deren Ersatz. Seine Inhalte müssen auf Quelle, Schema, Zeitfenster und Digest zurückverweisen. \[R1\]

Der gelesene SNN-Pointer illustriert die Trennung: `DATA/current_run.json` enthält lediglich den Verweis auf den letzten archivierten tonic-drive-Run und dessen Metadaten. Für diese konkrete Datei werden 24.781 komprimierte und 2.102.883 unkomprimierte Bytes angegeben. Dies belegt einen berichteten Kompaktierungsumfang dieses Artefakts, nicht allgemein eine bestimmte Kompressionsrate aller MHRN-Daten. Der referenzierte Hash wurde nicht durch ein erneutes Herunterladen und Dekomprimieren der Rohdatei verifiziert. \[R14\]

<a id="b5d-was-ein-wissenschaftliches-ki-paket-enthalten-sollte"></a>

## Was ein wissenschaftliches KI-Paket enthalten sollte

Als Erweiterung des bestehenden Konzepts wird ein strukturierter Vertrag vorgeschlagen: Frage und Hypothese, Protokollversion, Conditions, Anzahl tatsächlicher unabhängiger Einheiten, Beobachtungsabdeckung, fehlende Felder, primäre Endpunkte, deterministische Kennzahlen, Provenienz, aktive Gate-Blocker, Ausschlussregeln und gezielte Rohdatenzeiger. Zusätzlich sollte das Paket sichtbar machen, **welche Informationen nicht enthalten sind**. Ein Bericht ohne Roh-Spikefolgen darf beispielsweise keine nicht bereitgestellte zeitliche Feinstruktur erfinden.

Die Auswahlregel selbst ist Teil der Methode. Ein Paket, das nur erfolgreiche Läufe enthält, kann zu systematisch zu optimistischen Reviews führen. Eines, das alle Ausreisser entfernt, kann technische Instabilität verdecken. Eines, das zu stark mittelt, kann zwei gegensätzliche Populationen als stabil darstellen. Deshalb sind Vollständigkeitsfelder, Fehlversuchszähler und ein definierter Nachladepfad keine Komfortmerkmale, sondern Bedingungen glaubwürdiger Erkenntnis.

<a id="b5d-drei-ebenen-von-berichtstreue"></a>

## Drei Ebenen von Berichtstreue

**Numerische Treue** verlangt, dass die enthaltenen Kennzahlen aus kanonischen Daten mit dokumentierter Berechnung stammen. **Semantische Treue** verlangt, dass ein Zahlenfeld dieselbe Bedeutung wie im Protokoll besitzt. **Schlussfolgerungstreue** verlangt, dass der Bericht nicht mehr behauptet, als Kennzahlen und Design gemeinsam tragen. Ein exakt übernommener Wert kann semantisch falsch eingeordnet werden; eine korrekt beschriebene Metrik kann trotzdem zu einem unzulässigen Kognitionsschluss führen.

Die vorliegenden Konflikte liefern konkrete Testfälle: fehlende generische Spikefelder trotz spezieller Stabilitätsmetriken; angeforderte Ticks ohne direkte Anwendbarkeit auf Trials; identische Seed-Outcomes ohne geprüfte Initialisierungsvariation; ein semantischer Blocker trotz passend benanntem Protokoll. Ein wissenschaftlicher Assistent soll solche Fälle nicht rhetorisch glätten, sondern als prüfbare Widersprüche ausweisen.

<a id="b5d-datenrotation-ohne-verlust-der-forschungsgeschichte"></a>

## Datenrotation ohne Verlust der Forschungsgeschichte

Die aktuelle Projektion kann nach einem festen Budget rotiert oder neu aufgebaut werden. Die Rohdaten dürfen dabei nicht ohne Archivierungs- und Aufbewahrungsentscheidung verschwinden. Eine geeignete Rotation erzeugt ein abgeschlossenes Manifest, schreibt die unveränderliche Raw-Referenz, prüft lokale Integrität und startet dann eine neue begrenzte Projektion. Historische Berichte bleiben an ihre damaligen Daten- und Softwareversionen gebunden. Eine korrigierte Auswertung erscheint als neue Version mit Verweis auf ihren Vorgänger.

Die kleinere Modellgröße ist damit kein Anlass, wissenschaftliche Detailtreue aufzugeben. Sie ist ein Anlass, die Schnittstelle zwischen Messung und Interpretation zu verbessern. Ob ein kompaktes Paket relevante methodische Fehler ebenso gut erkennen lässt wie eine umfangreichere Darstellung, muss allerdings empirisch geprüft werden. Genau hier verbindet sich die technische Speicherfrage mit `RQ-AIR-001` und der Frage nach effektiver menschlicher beziehungsweise institutioneller Kontrolle.

[Inhaltsuebersicht](README.md) | [Zurueck](section-031.md) | [Weiter](section-033.md)
