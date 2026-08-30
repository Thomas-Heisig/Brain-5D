# Dateisystem und Verantwortlichkeiten

```text
brain5d-core-v0.1.0/
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── configs/
│   └── poc_config.yaml
├── src/
│   ├── main.py
│   ├── config/
│   │   └── loader.py
│   ├── core/
│   │   ├── spatial_index.py
│   │   ├── neuron.py
│   │   ├── synapse.py
│   │   └── network.py
│   ├── diagnostics/
│   │   ├── stimulus.py
│   │   ├── propagation.py
│   │   └── topology_health.py
│   ├── telemetry/
│   │   ├── history.py
│   │   ├── spike_history.py
│   │   └── probes.py
│   ├── visualization/
│   │   └── observatory.py
│   └── utils/
│       └── run_artifacts.py
├── tests/
│   ├── conftest.py
│   ├── test_spatial_index.py
│   ├── test_neuron.py
│   ├── test_network.py
│   ├── test_golden_chain.py
│   ├── test_artifacts.py
│   └── test_observatory_data.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FILESYSTEM.md
│   ├── DEVELOPMENT.md
│   ├── GIT_WORKFLOW.md
│   ├── ACCEPTANCE.md
│   ├── EXPERIMENTS.md
│   └── ROADMAP.md
└── artifacts/
    ├── runs/.gitkeep
    └── snapshots/.gitkeep
```

## Regeln

- `src/core`: keine UI-, Dateisystem- oder Lernabhängigkeit.
- `src/diagnostics`: definierte Testreize und Auswertung.
- `src/telemetry`: beobachtet, verändert keinen Simulationszustand.
- `src/visualization`: darf Matplotlib/NumPy für Darstellung verwenden.
- `artifacts`: Laufdaten; standardmäßig nicht in Git committen.
- `tests`: fachliche Invarianten statt bloßer Smoke-Tests.
