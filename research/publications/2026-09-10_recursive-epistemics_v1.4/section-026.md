[Inhaltsuebersicht](README.md) | [Zurueck](section-025.md) | [Weiter](section-027.md)

<a id="b5d-vorhandene-technische-evidenz-restore-und-speicherung"></a>

# 22. Vorhandene technische Evidenz: Restore und Speicherung

<a id="b5d-registrierte-unterstützung-für-determinismus-und-speicherung"></a>

## Registrierte Unterstützung für Determinismus und Speicherung

Im gelesenen Hypothesenregister besitzen `H-SNN-003-A` und `H-STOR-001-A` den Status `supported`. Die zugehörigen Forschungsfragen `RQ-DET-001` und `RQ-STORAGE-001` stehen im Fragenregister weiterhin auf `open`. Diese Differenz wird hier nicht stillschweigend geglättet: Sie zeigt, dass Frage-, Hypothesen- und Evidenzregister nicht notwendig denselben Bearbeitungsstand ausdrücken. Die beiden Aussagen dürfen insbesondere nicht gemeinsam mit allen übrigen Hypothesen pauschal als ungetestet bezeichnet werden. \[R2; R6\]

`EVID-2026-15` verweist auf `EXP-DET-0001`, `CLAIM-DET-001` und `H-SNN-003-A`. Der Record beschreibt identische strukturelle und dynamische Zustände nach einem A/B/C-Restore einschließlich Prozessneustart. Das zugehörige `DATA-2026-15.json` dokumentiert einen erfolgreichen Aufruf von `tests/test_restore_determinism_abc.py`: **7 Tests bestanden**, Rückgabecode 0. Die technische Durchführung stammt aus dem Projektartefakt vom 1. September 2026, nicht aus einer neuen Ausführung für diese Abhandlung. \[R7; R8\]

`EVID-2026-16` verweist auf `EXP-STOR-0001`, `CLAIM-STOR-001` und `H-STOR-001-A`. Das zugehörige DATA-Artefakt dokumentiert **15 bestandene Tests und einen übersprungenen Test** in `tests/test_b5d_storage.py`. Uebersprungen wurde der optionale **50.000-Neuronen-Speicher-Smoke-Test**, für den eine gesonderte Umgebungsvariable erforderlich war. Dies begrenzt die aus genau diesem Testlauf ableitbare Skalenaussage. Eine erfolgreiche Serialisierung kleinerer Testkonfigurationen ist kein Beleg für Tests bei 50.000, 50 Millionen oder mehr Neuronen. \[R9; R10\]

Tabelle 26. Vorhandene technische Nachweise und Geltungsgrenzen

| Aussage                | Im Artefakt dokumentiert                               | Zulässige Einordnung                             |
|:-----------------------|:-------------------------------------------------------|:-------------------------------------------------|
| Restore-Determinismus  | 7 bestandene spezialisierte Tests                      | Technischer Nachweis für die erfassten Testfälle |
| Speicher-Roundtrip     | 15 bestanden, 1 übersprungen                           | Technischer Nachweis mit expliziter Skalengrenze |
| Allgemeines Gedächtnis | Nicht Gegenstand dieser Tests                          | Nicht aus Serialisierung ableitbar               |
| Systemische Robustheit | Keine unabhängige Aufgaben-/Größensuite in diesen DATA | Keine automatische E3-Einstufung                 |

<a id="b5d-warum-ein-evid-name-die-evidenzstufe-nicht-ersetzt"></a>

## Warum ein EVID-Name die Evidenzstufe nicht ersetzt

Die beiden EvidenceRecords enthalten leere Felder für Effektgröße und statistische Signifikanz. Für deterministische Funktionstests ist das nicht automatisch ein Mangel: Gleichheit und erfolgreicher Roundtrip können durch technische Assertions geprüft werden. Es wäre jedoch ein Kategorienfehler, daraus einen statistisch abgesicherten kognitiven Effekt abzuleiten. Für die E0-E3-Systematik der Abhandlung werden diese Nachweise als **E1-nahe technische Verifikation im dokumentierten Testumfang** behandelt; der bereits gesetzte Registry-Status bleibt daneben sichtbar.

Die Hypothesen verweisen jeweils auf mehrere EVID-IDs. Deren Anzahl wird nicht als Zahl unabhängiger Replikationen verwendet. Ohne Prüfung von Run-Identität, Codebasis, Eingangszuständen und Reproduktionsbedingungen können wiederholte Records dieselbe technische Prüfung oder aufeinanderfolgende Regressionstests bezeichnen. Die hier im Detail geprüften jüngeren Einträge 15 und 16 reichen aus, um eine pauschale Aussage fehlender technischer Evidenz zu korrigieren; sie rechtfertigen keine Behauptung, alle historischen Nachweise seien umfassend neu auditiert worden.

<a id="b5d-bedeutung-für-die-philosophische-frage"></a>

## Bedeutung für die philosophische Frage

Ein rekonstruierbarer Systemzustand ermöglicht einen klareren Begriff technischer Identität: Zwei gespeicherte Instanzen können hinsichtlich definierter Zustandsbestandteile identisch sein. Daraus folgt keine numerische Identität eines erlebenden Subjekts. Ebenso ist die Fortsetzung einer Zustandsdynamik nach Neustart nicht gleichbedeutend mit autobiographischer Kontinuität. Die Speicherbefunde liefern eine Voraussetzung für kontrollierte Kausalexperimente und eine dokumentierbare Entwicklungsgenealogie. Sie lösen die ontologischen Fragen gerade nicht vorab.

[Inhaltsuebersicht](README.md) | [Zurueck](section-025.md) | [Weiter](section-027.md)


<a id="cognition-context-026"></a>
## Ergänzung der Fassung 1.2: Evidenzkandidaten und externe Replikation

Die neue Prüfung ist Bestandteil dieses Kapitels: [Evidenzkandidaten und externe Replikation](section-055.md). Dabei bleiben funktionaler Nachweis, theoriebedingte Interpretation, phänomenales Erleben und normative Bewertung getrennt. Die neuen kanonischen Fragen, Protokollentwürfe, Ethikregeln und technischen Grenzen werden im verknüpften Anhang konkretisiert; ältere Befunde erhalten dadurch keine weiter reichende Evidenzfreigabe.
