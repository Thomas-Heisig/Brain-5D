# Brain-5D Update: Optical Equivalent + Manipulator + Self-Organization

## Ziel

Das Update ergänzt den bestehenden deterministischen Sparse-Core ohne ihn zu ersetzen.

- **Optical codec:** fester 128-Byte-Snapshot pro Neuron als digitales optisches Äquivalent.
- **Manipulator:** einheitliche Lese-/Schreib-API für Neuronen, Synapsen und optische Sidecar-Werte.
- **Graph-Metadaten:** chemische, elektrische, Rezeptor- und Plastizitätsdaten bleiben außerhalb der schlanken Core-Synapse.
- **Transaktionen:** Änderungen können gruppiert und zurückgerollt werden.
- **SelfOrganizationEngine:** optionale strukturelle Selbstorganisation (Pruning, Sprouting, Neurogenese), standardmäßig deaktiviert.

## Warum Sidecars?

`src.core.Neuron` und `src.core.Synapse` bleiben klein und schnell. Zusätzliche optische/chemische Daten werden nur dort angelegt, wo sie gebraucht werden. Das verhindert, dass Millionen oder später hunderte Millionen Objekte durch Python-Overhead unnötig anwachsen.

## 312.500.000 Neuronen

Die Zielzahl ist im vorhandenen 5D-Raum besonders elegant:

`50 * 50 * 50 * 50 * 50 = 312.500.000`

Damit kann ein logischer Vollraum `dimensions: [50, 50, 50, 50, 50]` exakt diese Zahl an möglichen Neuronenpositionen adressieren. Die aktuelle 40-Bit-ID mit 8 Bit je Dimension kann diese Koordinaten problemlos darstellen.

Bei 128 Byte optischem Snapshot pro Neuron wären das bei Vollbelegung exakt 40.000.000.000 Byte Rohdaten (ca. 40 GB dezimal) pro vollständigem Snapshot, bevor Chunking/Delta-Kompression greift.

## Einbindung in main.py

Nach dem Erzeugen des Networks und der LearningEngine:

```python
from src.manipulation import Brain5DManipulator
from src.self_organization import SelfOrganizationEngine

manipulator = Brain5DManipulator(network)
self_org = SelfOrganizationEngine(network, manipulator, config)
if self_org.params.enabled:
    self_org.attach()
```

Die LearningEngine bleibt für STDP/Eligibility/Reward zuständig. SelfOrganizationEngine verändert bewusst nur die Struktur.

## Speicherung

Der 128-Byte-Record ist ein stabiles Austauschformat. Für große Datenmengen sollte ein späterer Backend-Layer diese Records chunkweise in Zarr/HDF5 oder einem eigenen `.b5d`-Container ablegen. Zeitreihen sollten als Basissnapshot + Delta/Journaling gespeichert werden, nicht als vollständiger Snapshot pro Tick.
