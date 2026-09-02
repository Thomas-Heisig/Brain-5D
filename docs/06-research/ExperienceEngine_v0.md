# Experience Engine v0

## Zweck

Brain-5D besitzt Lernmechanismen, benötigt aber einen kontrollierten
Erfahrungsstrom. `ExperienceEngine` verbindet deshalb einen autorisierten
Sensor, einen Encoder, das bestehende SNN, einen Decoder und die bestehende
Embodiment-Sicherheitsgrenze. Ein Reward wird ausschließlich aus einer
akzeptierten `EnvironmentObservation` übernommen.

## Wissenschaftliche Abgrenzung

- **Keine Evidenz:** Diese Änderung ist Infrastruktur und Testabdeckung, kein
  wissenschaftlicher Wirksamkeitsnachweis.
- **Keine externe Kausalquelle:** LLMs, Konfiguration und Decoder dürfen keinen
  Reward direkt schreiben.
- **Keine Hardwarebehauptung:** `SystemSensorAdapter` nutzt einen injizierten
  Provider. Der Standard-Provider liefert nur Uhrzeit/Tick; Kamera, Mikrofon
  und Internet bleiben unverbunden.
- **Reproduzierbarkeit:** Experimente können eine deterministische Messspur als
  Provider verwenden; Live-Systemwerte sind davon getrennt.
- **Sicherheit:** Aktionen bleiben unter `ControlledEmbodimentAgent` mit
  Autorisierung, Capability-Prüfung, Rate Limit, Audit und Emergency Stop.

## Zwischenschritte und Prüfungen

1. **Ausgangshypothese:** Sensor- und Aktorverträge sind vorhanden, aber es
   fehlt die Orchestrierung bis zum Lernsignal.
2. **Discriminating check:** Ein deterministischer Zielversuch muss drei
   Wahrnehmungs-/Aktionszyklen ausführen; nur die Zielerreichung darf Reward an
   die Lern-Schnittstelle senden.
3. **Implementierung:** `src/experience/engine.py` und
   `src/embodiment/system_sensor.py` wurden ergänzt.
4. **Sicherheitsprüfung:** Eine nicht autorisierte Aktion liefert keine
   Environment-Beobachtung und keinen Reward.
5. **Reproduzierbarkeitsprüfung:** Derselbe Sensor-Provider erzeugt identische
   `SensorFrame`-Werte.
6. **Verifiziert am 2026-09-02:**
   `python -m pytest tests/test_experience_engine.py
   tests/test_embodiment_safety.py -q` → **13 passed**.

## Offene nächste Schritte

- `ExperienceEngine` an den kanonischen Runtime-Hook anbinden, ohne den
  Diagnose-Stimulus als wissenschaftliche Eingabe umzudeuten.
- Systemmetriken wie CPU/RAM/Temperatur über explizite, plattformabhängige
  Provider ergänzen und deren Messunsicherheit dokumentieren.
- Ein registriertes, unabhängiges Experiment mit Source-Freeze durchführen,
  bevor Aussagen über synaptisches Lernen aus realen Systemdaten entstehen.
- Danach erst Kamera-, Audio- oder Knowledge-Intake-Adapter prüfen.