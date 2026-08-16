Brain 5D - Sprint 2B Overlay
============================

Basis:
- aktueller Sprint-1C-Core aus main
- Sprint-2A-Overlay aus der vorherigen Arbeitsrunde

Wesentliche Korrekturen gegenueber dem ersten Sprint-2B-Entwurf:
1. KEIN last_post_spike-Feld in src/core/synapse.py.
2. KEIN learning-spezifisches set_learning_engine() im Core.
3. Generischer post-step hook in NeuralNetwork.
4. Learning-Zeit wird nicht in core_step_ms eingerechnet.
5. Incoming-Synapsenindex statt O(E)-Vollscan pro Tick.
6. Lazy exponentieller Eligibility-Decay mit tau_ticks.
7. STDP-Timingzustand liegt vollstaendig in der LearningEngine.
8. src/main.py aktiviert die Engine tatsaechlich ueber die Konfiguration.

Geaendert:
- src/core/network.py
- src/main.py
- src/learning/__init__.py
- configs/poc_config.yaml
- configs/poc_config_stdp_on.yaml
- docs/STDP_LAB.md (Sprint-2A-Datei bleibt enthalten)

Neu:
- src/learning/eligibility.py
- src/learning/learning_engine.py
- tests/test_eligibility.py
- tests/test_stdp_integration.py
- docs/SPRINT_2B.md

Nicht geaendert:
- src/core/synapse.py
- src/core/neuron.py
- restlicher Sprint-1C-Core

Lokaler isolierter/rekonstruierter Testlauf dieser Arbeitsrunde:
37 passed

WICHTIG:
Der komplette Repository-Regressionslauf muss nach dem Overlay in F:\Brain-5D
erfolgen. Erst danach Sprint 2B taggen.
