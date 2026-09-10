# Methodik, Reproduktion und Versionsbindung

Die neue Fassung uebernimmt die 57 Kapitel der Fassung 1.3 unveraendert als datierte historische Bestandsaufnahme und ergaenzt vier Aktualisierungskapitel. Damalige Testzahlen und Aussagen zum damaligen Datenstand sind keine Beschreibung des neuen Messstands. Die urspruenglichen Editionsdateien, Messdaten und eingefrorenen Plaene werden nicht ueberschrieben.

Die Ausgangskampagne versucht alle 28 damals registrierten maschinell ausfuehrbaren Protokolle plus die siebenfamilige Basissuite. 22 Vorlagen verlangen menschliche Beurteilung; 43 Registerfragen besitzen noch kein eigenes passendes operationalisiertes Protokoll. Ein generischer Tick-/PING-Lauf ersetzt dies nicht. Unabhaengige Begutachtung, institutionalisiertes Mandat und erforderliche Ethikentscheidungen bleiben reale externe Arbeit.

Die neuen Studien wurden vor ihrer Messung als EXPLORATORY im Repository versioniert. Das wird nicht als externe OSF-/AsPredicted-Praeregistrierung bezeichnet. Bereits vorhandene konfirmatorisch bezeichnete Protokolle werden hier als explorative Reausfuehrung dokumentiert. Der Eingabedigest bindet getrackten Code, Konfiguration, Protokolle und Register vor dem Lauf; ein anschliessender Vergleich kontrolliert Quellveraenderungen. Er ist nicht derselbe Digest wie eine kombinierte Code/Config/Prompt/DATA-Provenienz oder eine Test-Baseline mit anderem Umfang.

## Budgets und statistische Einheit

Geometrie: 128 Knoten in einer gemeinsamen achtkoordinatigen Zufallswolke, acht gerichtete naechste Nachbarn unter den ersten D Koordinaten, zweimalige Inputpulse, 256 Ticks. Native Assoziation: positive/negative neue Inputs mit bis zu acht ausgelassenen Quellen und Zeitjitter, 40 Episoden pro Seed/Arm, 12 Ticks pro Testepisode. Einzelzellen: fuenf Strombedingungen, 1000 Ticks, 1 ms, drei Seeds. Skalierung: 128/1024/5000/25000/100000 Neuronen, vier Kanten je Neuron, 32 Ticks, zwei Inputpulse, drei Seeds, serielle Ausfuehrung.

Gepaarte Statistik auf Seed-Ebene: 2000 Bootstrapresamples, fester Analyse-Seed 910, punktweise 95-Prozent-Perzentilintervalle; alle 2^10 Vorzeichenwechsel fuer den zweiseitigen Test. Der Test setzt entsprechende Austauschbarkeit/Symmetrie der Paardifferenzen unter der Nullhypothese voraus; diese wird nicht empirisch bewiesen. Holm-Korrektur innerhalb der fuenf Dimensions- und vier Lernkontraste. Standardisierte Effektgroesse d_z ist mittlere Paardifferenz geteilt durch ihre Stichprobenstandardabweichung; bei Nullvarianz undefiniert statt erfunden. Keine nachtraeglichen Signifikanztests fuer die Altprotokolle und keine Stichprobengroesse aus einzelnen Ticks vortaeuschen.

## Ausfuehrung

Den exakten Quellcommit aus dem jeweiligen plan.json auschecken und eine saubere Arbeitskopie benutzen. Abhaengigkeiten: Python 3.13, Projektinstallation und Brian2 2.10.1. Jeder Protokollprozess wird separat, aber seriell ausgefuehrt. Bestehende Ausgabeordner und Ordner innerhalb des Quellbaums werden abgewiesen. Der Sicherheits-Timeout ist vorab dokumentiert. Keine Wiederholung missliebiger Ausgaenge.

```bash
python -m pip install -e '.[dev,docs]' 'brian2==2.10.1'
python scripts/empirical_campaign.py --output /absolute/private/path/new-campaign
python scripts/empirical_campaign.py --output /absolute/private/path/new-campaign --analyze
python scripts/publication_empirical.py --verify
```

Ein spaeterer Reproduktionslauf ist nicht automatisch eine unabhaengige Replikation. Fuer v2 wird der in dessen eigenem Plan genannte Commit und die dort dokumentierte Protokollauswahl verwendet. Keine neue DOCX-/PDF-Erzeugung, Promotion, Publikationsannahme oder externe Begutachtung wird behauptet.

## Primaere methodische Referenzen

Izhikevich (2003), Simple Model of Spiking Neurons, DOI 10.1109/TNN.2003.820440. Brian2, offizielles Beispiel frompapers.Izhikevich_2003 und Scheduling-Dokumentation: https://brian2.readthedocs.io/en/2.10.1/examples/frompapers.Izhikevich_2003.html . SciPy, offizielle Dokumentation scipy.stats.permutation_test: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html . Diese Quellen erklaeren Methoden; sie validieren nicht die MHRN-Ergebnisse. Das vollstaendige bisherige Literaturverzeichnis bleibt in den uebernommenen Kapiteln erhalten.
