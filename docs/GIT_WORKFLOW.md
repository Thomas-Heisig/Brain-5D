# Brain-5D – Git-Arbeitsablauf

## Grundprinzip

Für das Projekt **Brain-5D** gilt:

* Der **lokale Arbeitsstand ist die Single Source of Truth**.
* Der maßgebliche Branch ist immer **`main`**.
* Änderungen werden grundsätzlich nach **`origin/main`** gepusht.
* `develop` wird im normalen Arbeitsablauf nicht benötigt.
* Ein automatisches `git pull` vor dem Push wird vermieden.
* Der Remote-Stand dient primär als Sicherung und Veröffentlichung des lokalen Projektstands.
* Tags werden für definierte, geprüfte Meilensteine und Releases verwendet.
* `git push --force` wird nicht verwendet.
* Falls der Remote-Stand bewusst auf den lokalen Stand zurückgesetzt werden muss, wird ausschließlich `--force-with-lease` verwendet.

Repository:

```text
https://github.com/Thomas-Heisig/Brain-5D
```

---

# 1. Normaler täglicher Arbeitsablauf

Dies ist der Standardweg für normale Änderungen.

## Schritt 1 – Auf `main` wechseln

```bash
git checkout main
```

Alternativ bei neueren Git-Versionen:

```bash
git switch main
```

## Schritt 2 – Aktuellen Zustand prüfen

```bash
git status
```

Optional:

```bash
git branch --show-current
```

Erwartete Ausgabe:

```text
main
```

## Schritt 3 – Änderungen prüfen

Kurzübersicht:

```bash
git status
```

Inhaltliche Änderungen:

```bash
git diff
```

Bereits für den Commit vorgemerkte Änderungen:

```bash
git diff --staged
```

## Schritt 4 – Änderungen übernehmen

Alle Änderungen:

```bash
git add -A
```

Danach nochmals kontrollieren:

```bash
git status
```

## Schritt 5 – Commit erstellen

Beispiel:

```bash
git commit -m "Update Brain-5D"
```

Besser sind möglichst konkrete Commit-Nachrichten.

Beispiele:

```bash
git commit -m "Add deterministic neuron state handling"
```

```bash
git commit -m "Fix core validation tests"
```

```bash
git commit -m "Refactor observable reference core"
```

## Schritt 6 – Nach `main` pushen

```bash
git push origin main
```

Damit ist der normale Arbeitsablauf abgeschlossen.

---

# 2. Kurzform für normalen Push

Wenn der aktuelle Stand bereits geprüft wurde:

```bash
git checkout main
git status
git add -A
git commit -m "Update Brain-5D - alpha 5"
git push origin main
```

---

# 3. Wenn keine Änderungen vorhanden sind

Vor einem Commit kann Git melden:

```text
nothing to commit, working tree clean
```

Dann ist kein neuer Commit erforderlich.

In diesem Fall kann einfach geprüft werden:

```bash
git status
```

und gegebenenfalls:

```bash
git push origin main
```

Wenn auch dort nichts Neues vorhanden ist, ist der lokale und bereits gepushte Stand identisch.

---

# 4. Lokaler Stand ist aktueller als GitHub

Wenn lokal neue Commits vorhanden sind:

```bash
git status
```

Git kann beispielsweise melden:

```text
Your branch is ahead of 'origin/main' by 3 commits.
```

Dann genügt:

```bash
git push origin main
```

---

# 5. GitHub enthält Änderungen, lokal bleibt aber maßgeblich

Da im Brain-5D-Projekt der lokale Stand die **Single Source of Truth** ist, wird nicht automatisch ausgeführt:

```bash
git pull
```

Ein `git pull` würde Remote-Änderungen in den lokalen Arbeitsstand integrieren.

Das ist für den definierten Brain-5D-Workflow ausdrücklich nicht der Standard.

Zunächst wird geprüft:

```bash
git fetch origin
```

Danach:

```bash
git status
```

Optional kann der Unterschied zwischen lokalem und Remote-Stand geprüft werden:

```bash
git log --oneline main..origin/main
```

Remote-Commits, die lokal fehlen.

Umgekehrt:

```bash
git log --oneline origin/main..main
```

Lokale Commits, die auf dem Remote fehlen.

Zusätzlich:

```bash
git diff main..origin/main
```

oder:

```bash
git diff origin/main..main
```

---

# 6. Remote bewusst durch lokalen Stand ersetzen

Wenn eindeutig feststeht:

> Der lokale Stand ist korrekt und `origin/main` soll exakt diesem Stand entsprechen.

Dann:

```bash
git push --force-with-lease origin main
```

Nicht verwenden:

```bash
git push --force origin main
```

`--force-with-lease` bietet einen zusätzlichen Schutz gegen das unbemerkte Überschreiben unerwarteter Remote-Änderungen.

---

# 7. Empfohlener sicherer Ablauf vor `--force-with-lease`

Vor einem erzwungenen Push:

```bash
git checkout main
git status
git fetch origin
git log --oneline --decorate --graph --all -20
```

Optional Unterschiede prüfen:

```bash
git diff origin/main..main
```

Danach erst:

```bash
git push --force-with-lease origin main
```

---

# 8. Lokalen Stand sichern, bevor Remote überschrieben wird

Vor wichtigen oder riskanten Änderungen kann ein lokaler Sicherungs-Branch erzeugt werden:

```bash
git branch backup-before-sync
```

Oder mit Datum:

```bash
git branch backup-2026-08-16
```

Danach kann der Hauptbranch weiterverwendet werden:

```bash
git checkout main
```

Damit existiert ein zusätzlicher lokaler Wiederherstellungspunkt.

---

# 9. Sicherung über Tag

Noch sinnvoller für definierte Zustände:

```bash
git tag -a backup-2026-08-16 -m "Backup before repository synchronization"
```

Tag prüfen:

```bash
git tag
```

Optional auf GitHub sichern:

```bash
git push origin backup-2026-08-16
```

---

# 10. Sprint erfolgreich abgeschlossen

Bei einem geprüften Sprint kann zunächst normal committed werden.

Beispiel:

```bash
git checkout main
git status
git add -A
git commit -m "Sprint 1C VERIFIED - observable deterministic reference core"
git push origin main
```

Danach wird der Zustand getaggt.

```bash
git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"
```

Anschließend:

```bash
git push origin brain5d-core-v0.1.0
```

---

# 11. Vollständiger Sprint-Release-Ablauf

```bash
git checkout main

git status

git add -A

git commit -m "Sprint 1C VERIFIED - observable deterministic reference core"

git push origin main

git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"

git push origin brain5d-core-v0.1.0
```

---

# 12. Alle lokalen Tags pushen

Falls mehrere neue Tags vorhanden sind:

```bash
git push origin --tags
```

Dies sollte bewusst eingesetzt werden, da damit sämtliche noch nicht übertragenen lokalen Tags veröffentlicht werden.

Für einen einzelnen Release ist daher normalerweise besser:

```bash
git push origin brain5d-core-v0.1.0
```

---

# 13. Tags anzeigen

```bash
git tag
```

Mit Details:

```bash
git show brain5d-core-v0.1.0
```

Sortiert nach Version:

```bash
git tag --sort=-version:refname
```

---

# 14. Falsch gesetzten lokalen Tag löschen

```bash
git tag -d brain5d-core-v0.1.0
```

Danach kann er neu erstellt werden.

```bash
git tag -a brain5d-core-v0.1.0 -m "Correct release description"
```

---

# 15. Bereits gepushten Tag entfernen

Lokal:

```bash
git tag -d brain5d-core-v0.1.0
```

Remote:

```bash
git push origin --delete brain5d-core-v0.1.0
```

Danach gegebenenfalls neu erstellen:

```bash
git tag -a brain5d-core-v0.1.0 -m "Correct release"
git push origin brain5d-core-v0.1.0
```

Bei bereits veröffentlichten Releases sollten Tags jedoch möglichst nicht nachträglich verändert werden.

---

# 16. Versionierung der Brain-5D-Tags

Empfohlenes Schema:

```text
brain5d-core-vMAJOR.MINOR.PATCH
```

Beispiele:

```text
brain5d-core-v0.1.0
brain5d-core-v0.1.1
brain5d-core-v0.2.0
brain5d-core-v1.0.0
```

Bedeutung:

```text
MAJOR
```

Größere Architekturänderung oder inkompatible Änderung.

```text
MINOR
```

Neue Funktion oder neuer Entwicklungsabschnitt.

```text
PATCH
```

Fehlerkorrektur oder kleine Verbesserung ohne grundlegende Architekturänderung.

---

# 17. Beispiel für einen Patch-Release

```bash
git checkout main
git status
git add -A
git commit -m "Fix deterministic core validation"
git push origin main

git tag -a brain5d-core-v0.1.1 -m "Fix deterministic core validation"
git push origin brain5d-core-v0.1.1
```

---

# 18. Beispiel für nächste Entwicklungsstufe

```bash
git checkout main
git status
git add -A
git commit -m "Complete Sprint 2 reference implementation"
git push origin main

git tag -a brain5d-core-v0.2.0 -m "Sprint 2 VERIFIED"
git push origin brain5d-core-v0.2.0
```

---

# 19. Commit-Historie kontrollieren

Kurze Darstellung:

```bash
git log --oneline
```

Mit Branches und Tags:

```bash
git log --oneline --decorate --graph --all
```

Letzte 20 Einträge:

```bash
git log --oneline --decorate --graph --all -20
```

---

# 20. Letzten Commit anzeigen

```bash
git show HEAD
```

Nur Informationen:

```bash
git log -1
```

Kurz:

```bash
git log -1 --oneline
```

---

# 21. Prüfen, welcher Commit aktuell aktiv ist

```bash
git rev-parse HEAD
```

Kurzform:

```bash
git rev-parse --short HEAD
```

Beispiel:

```text
a1b2c3d
```

---

# 22. Prüfen, ob lokaler `main` und `origin/main` identisch sind

Zunächst:

```bash
git fetch origin
```

Dann:

```bash
git rev-parse main
git rev-parse origin/main
```

Wenn beide Hashes identisch sind, zeigen lokal und GitHub auf denselben Commit.

Alternativ:

```bash
git status
```

Typische Meldung:

```text
Your branch is up to date with 'origin/main'.
```

---

# 23. Änderungen ansehen, bevor sie committed werden

Alle noch nicht vorgemerkten Änderungen:

```bash
git diff
```

Bereits mit `git add` vorgemerkte Änderungen:

```bash
git diff --staged
```

Dateiliste:

```bash
git status --short
```

---

# 24. Einzelne Datei committen

Datei hinzufügen:

```bash
git add path/to/file.py
```

Commit:

```bash
git commit -m "Update neuron processing"
```

Push:

```bash
git push origin main
```

---

# 25. Nur bestimmte Dateien committen

```bash
git add Core/file1.py Core/file2.py tests/test_core.py
git status
git commit -m "Update deterministic core"
git push origin main
```

---

# 26. Datei versehentlich mit `git add` hinzugefügt

Datei wieder aus dem Staging entfernen:

```bash
git restore --staged path/to/file.py
```

Die lokale Datei selbst bleibt dabei unverändert.

---

# 27. Lokale Änderung an einer Datei verwerfen

Achtung: Die nicht gespeicherte Git-Änderung wird verworfen.

```bash
git restore path/to/file.py
```

Vorher immer prüfen:

```bash
git diff path/to/file.py
```

---

# 28. Letzten Commit korrigieren

Wenn der Commit noch nicht gepusht wurde:

```bash
git add -A
git commit --amend
```

Nur Commit-Nachricht ändern:

```bash
git commit --amend -m "Correct commit message"
```

Wurde der Commit bereits gepusht, ist anschließend normalerweise notwendig:

```bash
git push --force-with-lease origin main
```

Dies sollte bewusst erfolgen.

---

# 29. Letzten lokalen Commit zurücknehmen, Änderungen behalten

```bash
git reset --soft HEAD~1
```

Der Commit verschwindet, die Änderungen bleiben vorgemerkt.

---

# 30. Letzten lokalen Commit zurücknehmen und Änderungen unstagen

```bash
git reset HEAD~1
```

Die Dateien bleiben geändert, sind jedoch nicht mehr staged.

---

# 31. Commit rückgängig machen, ohne Historie umzuschreiben

Für bereits veröffentlichte Commits ist `revert` oft die bessere Methode.

```bash
git revert <commit-hash>
```

Danach:

```bash
git push origin main
```

Beispiel:

```bash
git revert a1b2c3d
git push origin main
```

Dabei wird ein neuer Commit erzeugt, der die Änderungen des alten Commits rückgängig macht.

---

# 32. Auf einen bekannten Tag zurückgehen

Zunächst anzeigen:

```bash
git tag
```

Tag prüfen:

```bash
git show brain5d-core-v0.1.0
```

Temporär ansehen:

```bash
git checkout brain5d-core-v0.1.0
```

Dabei befindet sich Git im sogenannten `detached HEAD`.

Zurück:

```bash
git checkout main
```

---

# 33. `main` vollständig auf einen geprüften Tag zurücksetzen

Wenn der lokale `main` bewusst wieder exakt auf einen bekannten Release-Stand gesetzt werden soll:

```bash
git checkout main
git reset --hard brain5d-core-v0.1.0
```

Danach prüfen:

```bash
git status
git log -5 --oneline
```

Soll anschließend auch GitHub diesen Zustand erhalten:

```bash
git push --force-with-lease origin main
```

Achtung:

`git reset --hard` verwirft lokale, nicht gespeicherte Änderungen.

---

# 34. Wiederherstellungs-Branch aus einem Tag erzeugen

Sicherer als direktes Zurücksetzen:

```bash
git checkout -b restore-v0.1.0 brain5d-core-v0.1.0
```

Damit kann der alte Zustand separat untersucht werden.

---

# 35. Remote-Informationen aktualisieren, ohne den lokalen Code zu verändern

Das ist für Brain-5D der bevorzugte Weg:

```bash
git fetch origin
```

`fetch` lädt Informationen über Remote-Branches und Commits herunter, verändert aber den lokalen Arbeitsstand nicht.

Deshalb:

```bash
git fetch origin
```

ist im Brain-5D-Modell normalerweise sinnvoller als:

```bash
git pull
```

---

# 36. Warum `git pull` nicht zum Standardworkflow gehört

`git pull` entspricht vereinfacht:

```bash
git fetch
```

plus anschließendem Merge oder Rebase.

Damit können Änderungen von GitHub in den lokalen Branch gelangen.

Da für Brain-5D gilt:

```text
LOCAL = Single Source of Truth
```

wird Remote nicht automatisch in Lokal integriert.

Stattdessen:

```bash
git fetch origin
git status
```

und anschließend eine bewusste Entscheidung.

---

# 37. Wenn Remote-Änderungen doch übernommen werden sollen

Nur wenn ausdrücklich entschieden wurde, dass Remote-Änderungen sinnvoll sind.

Zunächst:

```bash
git fetch origin
```

Unterschiede ansehen:

```bash
git log --oneline main..origin/main
```

und:

```bash
git diff main..origin/main
```

Danach können einzelne Commits gezielt übernommen werden.

Beispiel:

```bash
git cherry-pick <commit-hash>
```

Dies ist häufig sauberer als ein pauschales `git pull`.

---

# 38. Einzelnen Remote-Commit übernehmen

```bash
git fetch origin
git log --oneline main..origin/main
```

Gewünschten Commit auswählen:

```bash
git cherry-pick <commit-hash>
```

Dann:

```bash
git push origin main
```

Damit bleibt die Entscheidung über die Integration beim lokalen Repository.

---

# 39. `develop`-Branch

Für den festgelegten Brain-5D-Workflow wird `develop` grundsätzlich nicht benötigt.

Der normale Ablauf lautet:

```text
lokale Arbeit
    ↓
main
    ↓
origin/main
```

Nicht mehr als Standard:

```text
develop
    ↓
merge
    ↓
main
```

Deshalb entfallen normalerweise:

```bash
git checkout develop
```

```bash
git merge develop
```

und:

```bash
git merge --no-ff develop
```

---

# 40. Falls `develop` noch existiert

Branches anzeigen:

```bash
git branch
```

Remote-Branches:

```bash
git branch -r
```

Alle:

```bash
git branch -a
```

Wenn `develop` nicht mehr benötigt wird, kann er zunächst einfach bestehen bleiben.

Eine Löschung ist nicht zwingend erforderlich.

---

# 41. Lokalen `develop` löschen

Nur wenn sicher ist, dass er nicht mehr benötigt wird:

```bash
git branch -d develop
```

Falls Git wegen nicht gemergter Änderungen warnt und die Löschung dennoch bewusst erfolgen soll:

```bash
git branch -D develop
```

---

# 42. Remote-`develop` löschen

Nur wenn bewusst gewünscht:

```bash
git push origin --delete develop
```

Danach:

```bash
git fetch --prune
```

---

# 43. Remote-Branches aufräumen

```bash
git fetch --prune
```

Damit werden lokal gespeicherte Verweise auf Remote-Branches entfernt, die auf GitHub nicht mehr existieren.

---

# 44. Prüfen, welches Remote verwendet wird

```bash
git remote -v
```

Erwartet:

```text
origin
```

mit dem Brain-5D-GitHub-Repository.

---

# 45. Remote-URL prüfen

```bash
git remote get-url origin
```

Erwartet:

```text
https://github.com/Thomas-Heisig/Brain-5D
```

oder entsprechend die konfigurierte SSH-Adresse.

---

# 46. Remote korrigieren

Falls nötig:

```bash
git remote set-url origin https://github.com/Thomas-Heisig/Brain-5D.git
```

Danach:

```bash
git remote -v
```

---

# 47. Erster Push eines neu eingerichteten lokalen `main`

Falls noch kein Upstream gesetzt wurde:

```bash
git push -u origin main
```

Danach reicht künftig:

```bash
git push
```

Für maximale Klarheit wird im Brain-5D-Projekt dennoch empfohlen:

```bash
git push origin main
```

---

# 48. Standard-Push-Befehl

Der eindeutige Standardbefehl lautet:

```bash
git push origin main
```

---

# 49. Standard-Push bei autoritativem lokalen Stand

Falls `origin/main` abweicht und bewusst ersetzt werden soll:

```bash
git push --force-with-lease origin main
```

Dies ist kein normaler täglicher Push, sondern ein bewusster Synchronisationsvorgang.

---

# 50. Empfohlener Brain-5D-Standardworkflow

## Normal

```bash
git checkout main
git status
git add -A
git commit -m "Beschreibung der Änderung"
git push origin main
```

## Mit vorheriger Remote-Kontrolle

```bash
git checkout main
git status
git fetch origin
git log --oneline --decorate --graph --all -20
git add -A
git commit -m "Beschreibung der Änderung"
git push origin main
```

## Wenn Remote bewusst überschrieben werden soll

```bash
git checkout main
git status
git fetch origin
git diff origin/main..main
git push --force-with-lease origin main
```

---

# 51. Empfohlener Release-Workflow

```bash
git checkout main

git status

git add -A

git commit -m "Release description"

git push origin main

git tag -a brain5d-core-v0.1.0 -m "Release description"

git push origin brain5d-core-v0.1.0
```

---

# 52. Empfohlener Sprint-Abschluss

Beispiel Sprint 1C:

```bash
git checkout main

git status

git add -A

git commit -m "Sprint 1C VERIFIED - observable deterministic reference core"

git push origin main

git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"

git push origin brain5d-core-v0.1.0
```

---

# 53. Prüfablauf vor wichtigem Release

```bash
git checkout main

git status

git diff

git diff --staged

git log --oneline --decorate --graph -20

git fetch origin

git log --oneline main..origin/main

git log --oneline origin/main..main
```

Danach erst Commit, Push und Tag.

---

# 54. Empfohlener vollständiger Sicherheitsablauf

Für besonders wichtige Zustände:

```bash
git checkout main

git status

git fetch origin

git log --oneline --decorate --graph --all -20

git diff

git diff origin/main..main

git add -A

git status

git diff --staged

git commit -m "Beschreibung"

git push origin main
```

Optional Release:

```bash
git tag -a brain5d-core-vX.Y.Z -m "Beschreibung"
git push origin brain5d-core-vX.Y.Z
```

---

# 55. Regeln für Brain-5D

## Regel 1

Der lokale Stand ist maßgeblich.

```text
LOCAL = SOURCE OF TRUTH
```

## Regel 2

Produktiver Entwicklungsbranch:

```text
main
```

## Regel 3

Standardziel:

```text
origin/main
```

## Regel 4

Kein automatisches:

```bash
git pull
```

## Regel 5

Remote-Informationen nur prüfen:

```bash
git fetch origin
```

## Regel 6

Normaler Push:

```bash
git push origin main
```

## Regel 7

Remote bewusst auf lokalen Stand setzen:

```bash
git push --force-with-lease origin main
```

## Regel 8

Nie blind:

```bash
git push --force
```

## Regel 9

Verifizierte Entwicklungsstände erhalten Tags.

Beispiel:

```text
brain5d-core-v0.1.0
```

## Regel 10

Vor wichtigen Änderungen wird der aktuelle Zustand mit `status`, `diff` und `log` kontrolliert.

---

# 56. Nicht mehr empfohlener alter Ablauf

Der bisherige Ablauf:

```bash
git checkout main
git pull
git merge --no-ff develop
git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"
git push origin main --tags
```

wird für den neuen Brain-5D-Workflow nicht mehr als Standard verwendet.

Problematisch sind insbesondere:

```bash
git pull
```

weil dadurch Remote-Änderungen lokal integriert werden können,

und:

```bash
git merge --no-ff develop
```

weil `develop` im Single-Branch-Modell nicht mehr notwendig ist.

---

# 57. Neuer sauberer Ersatz

```bash
git checkout main

git status

git add -A

git commit -m "Sprint "

git push origin main

git tag -a brain5d-core-v0.0.0 -m "Sprint "

git push origin brain5d-core-v0.0.0
```

---

# 58. Minimaler täglicher Befehlssatz

```bash
git checkout main
git status
git add -A
git commit -m "Update"
git push origin main
```

---

# 59. Minimaler sicherer Befehlssatz

```bash
git checkout main
git status
git fetch origin
git add -A
git commit -m "Update"
git push origin main
```

---

# 60. Minimaler autoritativer Synchronisationsweg

Wenn der lokale Stand definitiv GitHub ersetzen soll:

```bash
git checkout main
git status
git fetch origin
git push --force-with-lease origin main
```

---

# 61. Grundsätzliches Brain-5D-Modell

```text
┌──────────────────────────────┐
│ Lokales Brain-5D Repository  │
│                              │
│ SINGLE SOURCE OF TRUTH       │
└──────────────┬───────────────┘
               │
               │ commit
               ▼
┌──────────────────────────────┐
│ local main                   │
└──────────────┬───────────────┘
               │
               │ git push origin main
               ▼
┌──────────────────────────────┐
│ GitHub origin/main           │
│                              │
│ Backup / Veröffentlichung    │
└──────────────────────────────┘
```

Remote-Änderungen fließen nicht automatisch zurück.

Prüfung erfolgt über:

```bash
git fetch origin
```

Eine Übernahme erfolgt nur nach bewusster Entscheidung.

---

# 62. Brain-5D Git-Leitsatz

```text
LOCAL FIRST.
MAIN ONLY.
FETCH TO INSPECT.
PUSH TO PUBLISH.
TAG VERIFIED STATES.
FORCE-WITH-LEASE ONLY WHEN LOCAL MUST WIN.
```

Damit bleibt der lokale Brain-5D-Projektstand kontrolliert, nachvollziehbar und eindeutig die maßgebliche Entwicklungsquelle.
