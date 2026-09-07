<a id="b5d-anhang-l-standardisierte-paradigmen"></a>
# Anhang L – Von etablierten Paradigmen zu überprüfbaren Softwareexperimenten

Die vorliegende Ergänzung registriert ein zusammenhängendes Programm aus 22 Fragen mit jeweils einer zugeordneten Hypothese. Die Fragestellungen sind offen, die Hypothesen ungetestet. Ihre kanonischen Texte stehen im Forschungsregister; diese Publikation ist die methodische Einordnung, keine zweite automatisch freigebende Registry.

## L.1 Was standardisiert wird

Standardisierung bezeichnet hier reproduzierbare Stimulus-/Antwortverträge, benannte Literaturvorbilder, klar getrennte Bedingungen, feste Auswertungsverfahren und offengelegte Abweichungen. Ein etablierter menschlicher Test wird nicht durch Umbenennung zu einem validierten Test künstlichen Bewusstseins. Stattdessen muss die Übertragung ihrer Einheiten, Beobachtungsmodelle und Schlussregeln selbst geprüft werden.

Der [vollständige Protokolltext](../../protocols/COGNITION_CONSCIOUSNESS.md) und der [maschinenlesbare Katalog](../../protocols/COGNITION_CONSCIOUSNESS_V1.json) enthalten Kontrollen und primäre Auswertungsgrößen. Sie sind zusammen mit den [Präregistrierungsentwürfen](../../preregistrations/cognition/) zu lesen. Die Entwürfe sind weder eingefrorene Konfirmationspläne noch durchgeführte Versuche. Stichprobengröße, kleinstes relevantes Effektmaß und tatsächlicher Daten-Holdout müssen vor dem jeweiligen nativen Lauf begründet werden.

## L.2 Kernbatterie

**Passive und aktive Oddball-Paradigmen** werden getrennt untersucht. Passiv stehen physisch gematchte Deviant-/Kontrollantworten nach Ausschluss einfacher Adaptation im Mittelpunkt. Aktiv werden diskriminative Leistung, Auslassungen, Fehlalarme und Berichtseffekte erfasst. Die Local-Global-Erweiterung prüft Regelverarbeitung auf unterschiedlichen zeitlichen Ebenen. Keine dieser Antworten allein ist ein Bewusstseinsnachweis.

**Delayed-Match-to-Sample** prüft die spätere Nutzung eines früheren Samples über eine definierte reizfreie oder abgelenkte Verzögerung. Das Protokoll verbietet den Zugriff auf Antwortschlüssel und zukünftige Reize. Reset-, Shuffle-, No-Memory- und Zero-Delay-Kontrollen trennen unmittelbare Diskrimination, gehaltene Information und tatsächliche Nutzung. Die Auswertung nach Verzögerung enthält alle geplanten Trials einschließlich fehlender Antworten.

**Metakognitive Prüfungen** trennen Konfidenzkalibrierung, Type-2-AUROC, Meta-d′ und metakognitive Effizienz. Der implementierte Deskriptivrechner ist kein Meta-d′-Fitter. Konstante und rein reizschwierigkeitsbasierte Konfidenz sowie angeglichene Erstordnungsleistung sind zwingende Vergleichsmöglichkeiten. Subjektive Selbstkenntnis folgt auch aus guter Kalibrierung nicht automatisch.

**LFP-/EEG-Vergleiche** beginnen mit dem Beobachtungsmodell, nicht mit einem ähnlichen Kurvenbild. Die Abbildung von Spikes auf Feldpotentiale und von diesen auf Kopfhaut-EEG braucht jeweils eine physikalisch begründete Beschreibung. Ein Datensatz mit Nutzungsrechten, Sampling, Montage, Filtern und held-out Personen ist vorab festzulegen. In dieser Revision wurde kein realer EEG-Datensatz neu ausgewertet.

## L.3 Ergänzende Prüfungen

Aufgenommen sind außerdem Maskierung mit Bericht/ohne Bericht, Attentional Blink, getrennte Go/No-Go-, Regelumkehr- und Stop-Signal-Aufgaben, multisensorische Cue-Integration, geschlossene Sensor-Aktor-Kopplung mit yoked Replay, Rekurrenz-/Zeitskalenablation, 2D–6D-Geometrievergleiche und ARC-inspirierter Transfer. Die Projektfragen können an etablierte Aufgabenfamilien anschließen, ohne deren klinische, psychologische oder leaderboardbezogene Validität zu erben.

PCI-inspirierte Perturbation wird ausdrücklich als nichtklinische Adaption bezeichnet. Der klinische Ursprung begründet Anforderungen an Mess- und Störmodelle, keinen importierbaren Grenzwert für empfindende Software. Turing-artige Dialogprüfungen sind für eine spätere Verhaltensstudie vorgesehen. Sie benötigen verblindete Richter, feste Kommunikationsbedingungen und Komponentenbaselines. Menschen in solchen Studien sind nicht durch eine Software-CI ethisch freigegeben. Der Ausdruck Turing-Test 2.0 wird nicht als unbestimmtes Gütesiegel verwendet.

## L.4 Was jetzt tatsächlich implementiert ist

`src/research/cognition_metrics.py` enthält Generatoren für Oddball und ausbalanciertes DMTS, DMTS-Auswertung einschließlich Auslassungen, Type-1-Signalentdeckungsmaße, Brier-/Type-2-AUROC, deskriptive gepaarte Effekte und eine vertragsgebundene EEG-Kurvenvergleichsfunktion. Diese Instrumente haben Tests mit konstruierten Daten. Sie führen keinen neuronalen Lernprozess aus und erzeugen keine Bewusstseinsentscheidung.

Der entscheidende nächste technische Schritt ist jeweils der native Adapter: Er muss Ereignisse tatsächlich zeitlich korrekt einspeisen, Antworten ohne Schlüssel-Leck abgreifen, den neuronalen Zustand nachprüfbar fortschreiben und die vollständige Herkunft der Beobachtungen speichern. Eine solche vollständige Validierung wird für diese neue Batterie noch nicht behauptet. Deshalb blockiert der neue Startschutz die geschützten Fragen auch dann, wenn eine Benutzeroberfläche generische Runtime-Ticks oder eine unpassende Suite als Ersatz anbietet.

## L.5 Was ein positiver oder negativer Befund bedeuten würde

Ein positiver Befund stützt zunächst genau den registrierten Funktionskontrast unter seinen Bedingungen. Unabhängige Replikation, neue Aufgaben, andere Größenordnungen und relevante Ablationen können seinen Geltungsbereich erweitern. Ein negativer Befund kann eine konkrete Hypothese begrenzen, muss aber bei unzureichender Präzision unentschieden bleiben. Beide Resultate sind wissenschaftlich verwertbar, sofern ihre Schlussregeln angemessen sind.

Die behauptete Gleichheit mit Menschen oder Tieren wird nicht aus einem fehlenden signifikanten Unterschied abgeleitet. Ein Äquivalenzanspruch benötigt vorab begründete Grenzen und passende Messgrößen. Selbst eine belastbare funktionale Äquivalenz beantwortet nicht allein die Frage nach gleicher subjektiver Erlebnisqualität.
