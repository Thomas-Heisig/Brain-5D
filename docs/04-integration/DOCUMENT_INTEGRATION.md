# Integration der strategischen Brain-5D-Dokumente

## Ziel

Die technische Roadmap soll nicht nur aus Sprintnotizen entstehen, sondern die
strategischen Analysen des Projekts als explizite Design-Inputs behandeln.

## Quellen

Folgende Dokumente sind fuer den naechsten Roadmap-Abgleich vorgesehen:

1. `docs/06-research/Analyse_Deepseek.md`
2. `docs/06-research/Der_weg_zur_KI.md`
3. `docs/08-roadmap/ROADMAP_TO_USABLE_AI.md`
4. `docs/02-architecture/Brain-5D_STORAGE_THEORY.md` bzw. die aktuelle Storage-Theorie
5. Sprint-/Release-Dokumente unter `docs/`

## Integrationsregel

Aussagen aus Analyse-Dokumenten werden nicht automatisch zu Architekturregeln.
Sie werden in vier Klassen eingeordnet:

- `accepted`: technisch plausibel, mit Projektarchitektur vereinbar
- `experiment`: pruefenswert, aber noch nicht als Produktionspfad bestaetigt
- `deferred`: sinnvoll, aber fuer eine spaetere Version
- `rejected`: widerspricht Invarianten, Tests, Skalierungszielen oder Sicherheit

Jede Uebernahme in die Roadmap soll ein messbares Exit-Kriterium erhalten.

## Aktueller Stand

Bei Erstellung von alpha.5 waren `Analyse_Deepseek.md` und `Der_weg_zur_KI.md`
weder im Remote-Repository noch in der verfuegbaren File Library sichtbar.
Daher werden sie in dieser Revision als vorgesehene Quellen registriert, aber
noch nicht inhaltlich bewertet.

Nach Verfuegbarkeit wird ein eigener Abschnitt `docs/04-integration/STRATEGY_REVIEW.md`
erzeugt, der Empfehlungen, Konflikte und Roadmap-Aenderungen nachvollziehbar
gegenueberstellt.
