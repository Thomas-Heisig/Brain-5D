# Brain-5D Real-Body Embodiment

## Ziel

Das Embodiment soll kein vorgezeichnetes menschliches Körperschema simulieren. Das sichtbare Selbstbild wird zur Laufzeit ausschließlich aus tatsächlich erkannten Verbindungen und tatsächlich gelieferten Systemmesswerten aufgebaut.

## Grundregel

**Keine Fantasiedaten.**

- Ein erkanntes Gerät oder eine reale Ressource darf als Körperorgan erscheinen.
- Ein nicht erkanntes Gerät erscheint nicht als Organ.
- Ein vom Betriebssystem nicht gelieferter Messwert bleibt `None`/`UNKNOWN`.
- `available` bedeutet nur beobachtete Verfügbarkeit und niemals automatisch `authorized` oder `active`.
- Aktorzugriff bleibt weiterhin an die bestehenden Autorisierungs-, Safety- und Audit-Grenzen gebunden.

## Dynamische Körpergrenze

Das Dashboard erzeugt den Körper aus `/api/embodiment/connections`. Verfügbare Verbindungen werden radial um den Brain-5D-Kern angeordnet. Dadurch verändert sich die Form automatisch, wenn reale Verbindungen hinzukommen oder verschwinden.

Beispiele sind:

- Compute und Arbeitsspeicher als interne Ressourcen;
- lokales Netzwerk und Internetroute als digitale Reichweite;
- Kamera als visuelles Sinnesorgan;
- Mikrofon als akustisches Sinnesorgan;
- Display und Audioausgabe als digitale Aktoren;
- Drucker als physisch/digitaler Ausgabeaktor;
- zukünftige Robotik-, Umwelt-, Standort-, Datenbank- oder Serviceadapter.

Nicht erkannte Katalogeinträge bleiben außerhalb des aktuellen Körpers und werden lediglich als mögliche Erweiterungsgrenze angezeigt.

## Reale Interozeption

`host_system_readings()` stellt einen read-only Host-Snapshot bereit. Er enthält nur Werte, die Python, das Betriebssystem oder `psutil` tatsächlich liefern können, unter anderem:

- Plattform, Hostname, Boot-Zeit und Architektur;
- CPU-Auslastung, Auslastung je logischem Kern, Kernzahlen und Frequenzen;
- RAM und Swap;
- Datenträgerkapazität und Disk-I/O;
- Netzwerkinterfaces, Adressen, Zustand und I/O-/Fehlerzähler;
- Akku, sofern vorhanden;
- Lüfterdaten, sofern vom Betriebssystem geliefert;
- Temperatursensoren, sofern geliefert;
- Prozesszahl.

Fehlende Temperatur-, Lüfter- oder Akkudaten werden ausdrücklich nicht geschätzt.

## Dashboard-Selbstbild

`embodiment-self-model.js` ergänzt das bestehende Embodiment-Dashboard um ein zentrales Selbstbild:

1. Brain-5D bleibt der visuelle Mittelpunkt.
2. Reale verfügbare Verbindungen bilden dynamisch die äußeren Organe.
3. Host-Telemetrie bildet die inneren Zustandsanzeigen.
4. Verbindungsstatus, Beziehung, Fähigkeiten, Berechtigungen, Autorisierung und Aktivität sind interaktiv einsehbar.
5. Die bestehende detaillierte Embodiment-Ansicht bleibt als technische Detailansicht erhalten.
6. Dark- und Light-Theme besitzen eigene kontrastfeste Design-Tokens.

## Rückkopplung

Die Darstellung selbst erzeugt keine Kausalität. Sie bildet nur den aktuellen beobachteten Zustand ab. Rückkopplung entsteht weiterhin über die existierende Kette

`Environment -> Sensor -> Encoder -> SNN -> Decoder -> Actuator -> EnvironmentObservation`.

Das Selbstbild kann künftig als expliziter beobachtbarer Input für Self-Model-Experimente verwendet werden. Dafür muss die wissenschaftliche Trennung erhalten bleiben zwischen:

- real gemessenem Körperzustand,
- daraus deterministisch abgeleiteten Regulierungsgrößen,
- neuronaler Repräsentation im SNN,
- Interpretation durch Dashboard oder Language Organ.

Diese Trennung verhindert, dass das Dashboard oder ein LLM dem SNN einen inneren Zustand nur sprachlich zuschreibt.
