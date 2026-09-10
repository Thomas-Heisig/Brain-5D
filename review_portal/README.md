# MHRN: externes Review-Portal

KI-unterstuetzte Implementierung, 2026-09-10. Vor einer echten Erhebung sind menschliche Abnahme, unabhaengige Administration sowie Datenschutz- und Sicherheitspruefung erforderlich. Die Seite behauptet weder institutionelle Freigabe noch psychometrische Validierung, Peer-Review oder Bewusstsein.

## Einfach oeffnen

Im bestehenden Dashboard: **Externes Review** anklicken oder **`/review/index.html`** oeffnen. Das ist eine eigenstaendige Seite ohne Runtime-Steuerung. Dafuer werden keine zusaetzlichen Dashboard-Abhaengigkeiten benoetigt.

Unabhaengige lokale Vorschau im Repository-Verzeichnis:

```powershell
py -m pip install -r review_portal/requirements.txt
py -m review_portal
```

Adresse: `http://127.0.0.1:8766/`. Ohne explizite Studienkonfiguration gilt **lokaler Ausfuell-/Exportmodus**, nicht zentrale Erhebung. Antworten bleiben im Arbeitsspeicher; Geraetespeicherung muss gesondert aktiviert werden. JSON-Entwurf, Import, abschliessender JSON-/CSV-Export und Druckansicht sind vorhanden. Geraetespeicher und Exporte sind **nicht verschluesselt**; keine gemeinsame Geraetenutzung und nur geschuetzte Weitergabe.

## Vollstaendiger Katalog

**75 identische Basisfragen A1-H5**, dazu **60 Zusatzfragen** in IT, BIO, OPS, BACK, ETH und Q (je zehn). Rollen: Proband, externe pruefende Person oder Gremiumsmitglied als Einzelstimme. Alle erhalten denselben Grundkatalog; optionale Fachmodule veraendern diesen nicht. Q ist fuer Reviewer/Gremium vorausgewaehlt, ohne Sachantworten zu erzwingen. Fuer eine komplette Bearbeitung aller Fragen alle sechs Zusatzmodule aktivieren.

`catalogue.py` ist die kanonische Definition. `python -m review_portal.build` erzeugt `src/dashboard/static/review/instrument.js`; `--check` prueft Byte-Gleichheit. Exportiert werden Instrument-ID, Version, SHA-256, Pruefunterlagen-Commit, Studie, Welle, Pseudonym, Rolle, Module, Antworten, Kommentare, Einwilligung und Zeiten. Die Online-Abgabe wird zusaetzlich an den Hash der vollstaendigen Studieninformation gebunden. Geaenderte Informationen erfordern einen neuen Kontext/eine neue Datenbank; alte Einwilligungen werden nicht still uebertragen. Client-Zeiten sind Selbstauskunft, der Server ergaenzt Eingangs-/Ablaufzeit.

Wortlaut bleibt erhalten, mit dokumentierten Anpassungen: C8 grammatisch `wuerde` statt `waere`; H4-Erlaeuterung im zugeordneten Kommentarfeld; H5-Namensbestaetigung freiwillig; zusaetzliche fehlende/nicht beurteilbare Antworten; Pilot nur ab 18. Keine Bewertung ist vorausgewaehlt. `Nicht beurteilbar`, `Keine Angabe`, ausgelassen und numerische 3 bleiben getrennt. Eine freiwillige Namensbestaetigung ist **keine qualifizierte elektronische Signatur**. Alter, Beruf, Signatur und Freitext koennen identifizieren; es wird keine garantierte Anonymitaet versprochen.

## Online-Erhebung: getrennt und geschlossen bis zur Konfiguration

Den Collector auf eigenem Host/Origin oder separat isoliertem Dienst bereitstellen. **Niemals das Operator-Dashboard, den File Manager oder die SNN-Steuerung oeffentlich freigeben.** Der Dienst importiert keine Runtime und liefert nur den Fragebogenordner aus. Keine LLM-Aufrufe, kein Schreiben in Experiment-/EVID-Register.

`study.example.json` **ausserhalb des Repositorys** kopieren, alle Platzhalter ersetzen, Angaben unabhaengig pruefen und erst dann `enabled: true` setzen. Verbindlich festzulegen: verantwortliche Stelle/Kontakt, Zweck und zulaessige Verarbeitung, Aufbewahrung samt Backups, Verguetung, Hosting/Protokolle, Rechte und Ruecktritt. Eine Einwilligungs-Checkbox ersetzt keine erforderliche rechtliche oder institutionelle Pruefung. Fuer eine Welle identische, unveraenderliche Pruefunterlagen/Commit bereitstellen.

Geheimnisse lokal erzeugen; nicht in GitHub, Issues oder Chats einfuegen:

```powershell
py -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Umgebungsvariablen (fuer Geheimnisse alternativ direkte Variablen ohne `_FILE`):

```text
MHRN_REVIEW_STUDY=/private/mhrn-review/study.json
MHRN_REVIEW_DATA_DIR=/private/mhrn-review/data
MHRN_REVIEW_KEY_FILE=/private/mhrn-review/encryption.key
MHRN_REVIEW_ADMIN_TOKEN_FILE=/private/mhrn-review/admin.token
```

Datenordner muss ausserhalb des Repositorys liegen. Der Start verweigert unvollstaendige Angaben, Platzhalter, unsichere oeffentliche Origins (lokal HTTP erlaubt), falschen Schluessel oder veraenderten bestehenden Datenbankkontext. Schluessel getrennt von Backups sichern. Verlust ist nicht durch die Anwendung reparierbar; Schluesselwechsel benoetigt eine geplante Migration.

`Dockerfile`, `compose.example.yaml` und `Caddyfile.example` sind Bereitstellungsvorlagen, kein Sicherheitsaudit. `REVIEW_PRIVATE_DIR` bezeichnet einen externen Ordner mit `study.json`, `encryption.key`, `admin.token`. Container-UID 10001 muss diese Dateien lesen koennen; Hostzugriff beschraenken. Unter Linux beispielsweise eigene Gruppe 10001, Verzeichnis 0750, Dateien 0440. Die Datenbank liegt in einem separaten Volume. Caddy laeuft in diesem Beispiel **auf dem Host**, verbindet zur loopback-gebundenen Collector-Schnittstelle und benoetigt eine kontrollierte Domain mit korrektem DNS. Zertifikate, Firewall und Updates ueberwachen. Es werden keine Domain, Kosten oder Server automatisch beauftragt.

Keine Anwendungs-Zugriffslogs; Plattform-/Proxylogs separat pruefen. Der Anfragelimiter haelt kurzlebige gesalzene Adressableitungen nur im Speicher. Hinter der Beispiel-Proxykonfiguration teilen Zugriffe dessen Limit; fuer groessere Erhebungen bewusst dimensionieren und keine beliebigen Forwarded-Header vertrauen. Ein Worker, begrenzte Parallelitaet, 2-MiB-Anfragen, Zeitlimits, Same-Origin-Pruefung, CSP und authentifizierte Administration sind vorgesehen. Produktion benoetigt eigene Sicherheitsabnahme.

## Verwaltung, Abgabe und Ruecktritt

Auf dem Collector **`/admin.html`** oeffnen und privaten Admin-Schluessel eingeben. Einmal-Einladungen einzeln erstellen/privat weitergeben; Klartext wird nur bei Erstellung angezeigt, Gueltigkeit 14 Tage. Kein Admin-Schluessel im Geraetespeicher oder URL. Antworten sind unveraenderlich: identische Wiederholung ist idempotent, gebrauchte Einladungen koennen nichts ueberschreiben und werden durch Ruecktritt nicht erneut freigeschaltet.

Vor der Uebermittlung erzeugt der Browser einen persoenlichen Ruecktrittsbeleg mit Zufallscode. Der Beleg allein beweist **keinen** Servereingang; die ausdrueckliche Serverbestaetigung abwarten. Bei unklarem Netzfehler unveraendert wiederholen, nicht zwischenzeitlich die Antwort aendern. Der verschluesselte Antwortdatensatz enthaelt keine Einladungs-/Ruecktrittsgeheimnisse. Der Ruecktrittscode berechtigt zur Loeschung: privat aufbewahren. Ohne Code kann eine Zuordnung unmoeglich sein.

Die Ruecktrittsseite funktioniert ohne Benutzerkonto. Eine falsche/nicht existierende ID bekommt dieselbe generische Rueckmeldung. Aktive Datensaetze werden geloescht; schon exportierte Kopien und Backups brauchen eigene Loeschprozesse. Verschluesselte Datentraegerreste werden nicht als physisch unwiederherstellbar versprochen. Ruecktritt bedeutet nicht automatisches Loeschen lokaler Dateien.

Authentifizierte Rohdatenexporte und private deskriptive Auswertung sind vorhanden. **Nicht automatisch anonymisiert oder publikationsfertig.** Keine echten Antworten, Signaturen, Codes, Datenbanken, Backups oder Admin-Schluessel ins Repository, GitHub-Artefakte oder Modellkontexte schreiben. CSV-Zellen mit Formel-Anfang werden entschaerft. Notizen/Belege sind inerte Texte; keine Ausfuehrung, kein automatisches Abrufen, keine Evidenzhochwertung.

SQLite speichert Antwortinhalte authentifiziert Fernet-verschluesselt. Nur technische Kennungen, Zeitpunkte und Token-Hashes liegen ausserhalb des Chiffrats. Ablaufpruefung beim Zugriff und einmal pro Minute, solange der Dienst laeuft. Ein gestoppter Dienst kann nicht zeitgesteuert loeschen; betriebliche Bereinigung vorsehen. Begrenzte Backup-Aufbewahrung und Rechte aller Empfaenger sind vor Start zu klaeren.

## Auswertung und Grenzen

Pro Skalenitem: Haeufigkeiten, Mittelwert, Median, Stichproben-SD, nutzbares N, fehlend/nicht beurteilbar/keine Angabe getrennt. B-E: Cronbach-Alpha nur fuer vollstaendige Faelle pro Abschnitt und erst ab 20 solchen Faellen als **vorsichtige Pilotregel, nicht allgemeine Fallzahlschwelle**. Alpha kann negativ sein; bei konstanter Summe kein Alpha. Heterogene, unvalidierte Aussagen bilden nicht automatisch eine sinnvolle Skala. Kein Gesamtscore, keine automatischen Ausschluesse durch H1-H4-Hinweise.

Weitere gewuenschte Analysen bleiben ein vorab zu konkretisierender **Analyseplan**, keine automatische Signifikanzmaschine: ANOVA/Kruskal-Wallis bei geeigneter Gruppenstruktur; Pearson/Spearman bei passenden Variablen/Annahmen; EFA/CFA mit begruendeter Stichprobe/Messmodell; gepaarter t-Test/Wilcoxon nur bei echt verbundenen wiederholten Personen und vergleichbaren Unterlagen. Fehlwerte, Effektstaerken, Mehrfachtests, Power und Ausschluesse vorab festlegen. Thematische Freitextanalyse braucht dokumentierten Codeplan und vorzugsweise unabhaengige Kodierung. N=5-50 aus einer Gelegenheitsstichprobe ist nicht bevoelkerungsrepraesentativ.

Wertende Begriffe wie Hybris/Spinnerei wurden bewusst nicht still umgeschrieben; unabhaengig kognitiv pilotieren. Selbsteingeschaetztes Verstaendnis ist kein objektiver Wissenstest. Wahrgenommene Reproduzierbarkeit/Sicherheit ist keine ausgefuehrte Replikation/Sicherheitspruefung. Ueberarbeiteter Wortlaut erhaelt eine neue Instrumentversion. Positive Stimmen sind kein wissenschaftlicher Beleg.

Eine Veroeffentlichung benoetigt gesonderte Anonymisierungs-/Reidentifikations- und Offenlegungspruefung, angemessene Information und ausdrueckliche Freigabe. Ein interdisziplinaeres Gremium ergaenzt, ersetzt aber weder qualifizierte Fachpruefung, Statistik, einschlaegige Rechtsberatung, Ethikaufsicht noch unabhaengige Replikation. Unabhaengigkeit muss tatsaechlich organisiert werden.

## Oeffentliche statische Bereitstellung

`.github/workflows/review-portal.yml` prueft die Seite. Der optionale Pages-Job veroeffentlicht **nur** `src/dashboard/static/review`, niemals Runtime, Studiengeheimnisse oder Antwortspeicher. Repository **Settings > Pages > Source: GitHub Actions** einrichten; Workflow **External review portal** auf `main` mit `publish_pages: true` starten. Fuer automatische Folgeaktualisierungen Repositoryvariable `MHRN_REVIEW_PAGES_ENABLED=true` setzen.

Die uebliche Projektadresse waere `https://thomas-heisig.github.io/MHRN/`; sie ist **nicht allein durch diese Dateien bereits live**. Vor Weitergabe erfolgreichen Deploy und tatsaechliche URL pruefen. Pages ist hier Ausfuell-/Exportmodus, keine zentrale Antwortsammlung. Fuer direkte Abgabe statische Seite und isolierte API zusammen unter kontrollierter HTTPS-Origin betreiben. Keine beliebige Collector-URL per Querystring und kein oeffentlicher Tunnel zur neuronalen Runtime.

## Tests

```text
python -m review_portal.build --check
python -m pytest review_portal/tests/test_portal.py -q
node --test review_portal/tests/model.test.mjs
python -m playwright install chromium
python -m review_portal.tests.browser_smoke
```

55 Python-Testfaelle und sechs JavaScript-Tests; Chromium prueft Desktop/Mobil, Einwilligung, keine Vorauswahl, Abgabe, Ruecktritt, Verwaltung, Offlineexport, Opt-in-Entwurf und Versionsfehler mit ausschliesslich synthetischen Daten. Nur synthetische Screenshots werden als CI-Artefakte abgelegt. Diese Tests ergaenzen die bestehenden Kern-CI-/wissenschaftlichen Gates; keine Gate- oder Evidenzregeln werden abgeschwaecht.

Technische Referenzen fuer Bereitstellung: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages ; https://cryptography.io/en/latest/fernet/ ; https://fastapi.tiangolo.com/deployment/concepts/ . Vor Produktivbetrieb aktuelle offizielle Dokumentation beachten.
