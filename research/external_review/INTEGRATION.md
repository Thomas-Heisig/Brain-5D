# Probanden, Fachpruefer und Ethik: Integration und Abschlusskriterien

Stand: 2026-09-10. KI-unterstuetzte technische und methodische Dokumentation.
Keine vorweggenommene Beurteilung oder institutionelle Freigabe.

## Was jetzt integriert ist

Das gemeinsame Basisinstrument (75 Fragen A-H) und die 60 Fach- und
Querschnittsfragen sind ueber den bestehenden [Fragenkatalog](../../review_portal/README.md)
und den Dashboard-Untertab **Probanden & Ethik** erreichbar.
[Instrumentbindung und Verfahrensstatus](integration.json) enthalten ausschliesslich
Metadaten oeffentlicher Unterlagen. Die lesende API
`GET /api/research/external-review` kontrolliert die gebundenen Instrumentdateien;
fehlende oder veraenderte Dateien ergeben `unavailable`, nicht einen positiven Status.

Der implementierte Erhebungsweg schliesst die technische Luecke eines fehlenden
standardisierten Instruments. Eine laufende oder abgeschlossene externe Bewertung
wird dadurch nicht behauptet. Antwortanzahlen bleiben hier unbekannt (`null`),
weil diese Ansicht keinen Zugang zum privaten Collector hat.

## Drei getrennte Personenkreise und Aussagebereiche

| Personenkreis | Beitrag | Keine automatische Schlussfolgerung |
| --- | --- | --- |
| Probanden | Verstaendlichkeit, Wahrnehmung, Erfahrung und dokumentierte Einschaetzung | Kein Beweis fuer Lernen, Bewusstsein, Reproduzierbarkeit oder Sicherheit |
| Fachpruefer | Pruefung von Protokollen, Daten, Alternativen, Grenzen und Statistik | Kein institutionelles Ethikvotum allein durch Fachkompetenz |
| Ethik-/Aufsichtsgremium | Beurteilung mit realem Mandat, Zustaendigkeit, Auflagen und Geltungsbereich | Keine externe Genehmigung durch Rollenwahl oder Selbstauskunft |

Mehrere Rollen derselben Person sind offenzulegen. Stichprobe, Unabhaengigkeit,
Interessenkonflikte und Qualifikation sind tatsaechlich zu dokumentieren, nicht
nur im Dashboard zu etikettieren. Weder KI noch Projektleitung duerfen eine
unabhaengige Entscheidung im Namen nicht beteiligter Personen erzeugen.

## Ablauf je Kohorte und Welle

1. Verantwortliche Administration, Einwilligungsunterlagen, Zugriff, Aufbewahrung
   und Ruecktrittsweg ausserhalb des oeffentlichen Repositorys festlegen.
2. Pruefpaket mit konkretem Commit, Publikationsfassung, DATA-Referenzen und
   Instrumentversion unveraenderlich binden. Eine neue Codefassung ist nicht
   automatisch dieselbe bewertete Fassung. Das bestehende Instrument wird durch
   diesen Merge weder umformuliert noch auf neue Unterlagen umgebunden.
3. Wortlaut unabhaengig pilotieren. Wertende Aussagen und fehlende
   psychometrische Validierung explizit offenlegen. Keine zustimmenden Antworten
   vorauswaehlen; keine neue Instrumentversion nach Beginn derselben Welle.
4. Befragung im isolierten Collector oder im dokumentierten Exportmodus
   durchfuehren. Rohdaten, Signaturen, Einladungen und Ruecktrittscodes bleiben
   privat. Sie gehoeren weder in Git noch in CI-Artefakte oder KI-Kontexte.
5. Bewertungen mit dokumentiertem Analyseplan auswerten. Fehlend, keine Angabe,
   nicht beurteilbar und ein numerischer Mittelwert sind unterschiedliche Dinge.
6. Fachurteile und gegebenenfalls institutionelle Entscheidungen mit Begruendung,
   Minderheitspositionen, Auflagen und Versionsbezug getrennt dokumentieren.
7. Erst danach einen freigegebenen, auf Reidentifikation geprueften oeffentlichen
   Verfahrensbericht mit Verweisen auf die zulassigen Nachweise erstellen.

Der reine statische Portalzugang ist keine bestaetigte Internetbereitstellung.
Ein Collector-Betrieb benoetigt die in der [Betriebsanleitung](../../review_portal/README.md)
beschriebene gesonderte Konfiguration und Abnahme.

## Kritikpunktbezogene Abschlussmatrix

| Kritik | Jetzt vorhandene Antwort | Noch erforderlicher Nachweis | Status |
| --- | --- | --- | --- |
| Kein einheitliches externes Pruefinstrument | Versionierter 135-Fragen-Katalog, Basis/Fachmodule, Export, API-/Browserpruefung | Laufende Pflege und Pilotierung | Technischer Instrumentpfad vorhanden |
| Nur selbstverfasste Kritikzuordnung | Externer Erhebungs- und Dokumentationsweg | Tatsaechliche unabhaengige Fachurteile, Interessenkonflikte, Gegenpositionen | Offen |
| Keine externe Ethikaufsicht | Verfahren und Personenkreis vorgesehen | Realer Beschluss/Mandat einer zustaendigen Stelle, soweit erforderlich | Nicht behauptet |
| Kein empirischer Beleg fuer Kognition | Komponententests und Forschungsprotokolle | Passende kontrollierte SNN-Versuche, unabhaengige Replikation und EVID-Pruefung | Offen |
| Ungepruefte 5D-Vorteile und Skalierung | Bestehende Ablations-/Benchmarkprogramme | Gematchte Vergleichsdaten und Unsicherheitsanalyse | Offen |
| Positive Bewertungen als Selbstlegitimation | Strikte Trennung von HUMAN_REVIEW_DATA_NOT_EVIDENCE und EVID | Nachweisbezogene Begruendung je Claim, kein Gesamtscore als Freigabe | Verfahrensregel |

Ein Kritikpunkt kann als **bearbeitet**, **teilweise geklaert** oder
**nachweislich abgeschlossen** dokumentiert werden. Dazu gehoeren konkrete
Belege, verantwortliche Beurteilung, Zeitpunkt, Scope und verbleibende Auflagen.
Die oeffentliche Status-API dieser Integration bietet absichtlich keine
Schreibfunktion fuer solche Entscheidungen. Eine spaetere Freigabe benoetigt
einen gesondert geprueften Nachweisweg; ein JSON-Label ist keine Signatur.

## Einordnung der parallel integrierten Cognition-Protokolle

Memory-, Ein-Schritt-Praediktions- und Verhaltensprofilversuche pruefen konkrete
Softwarekomponenten mit getrennten Seeds und Kontrollen. Ihre Leistungsquelle
wird als Komponente ausgewiesen; sie instanziieren kein SNN und belegen daher
weder neuronales Lernen noch erlernte Koerperbeherrschung.

Die 22 Methoden-/Ethikdesigns erzeugen Pruefvorlagen. `audit_template_generated`
ist nicht `audit_complete`. Ohne menschliche Beurteilung bleiben sie
`human_review_pending`. Die Fragebogenerhebung kann diesen Prozess unterstuetzen,
aber nicht durch einen automatisch erzeugten Audit-Record ersetzen.

Bei einem Modell, das waehrend der Auswertung weiterlernt, heisst der Modus
`prequential_online_update`, nicht unveraendertes Holdout. Der Frozen-Arm bleibt
getrennt auswertbar. Neue Resultate sind explorative Komponentendaten und werden
nicht automatisch zu EVID. Historische DATA/EVID und Publikationsfassungen
bleiben unveraendert.
