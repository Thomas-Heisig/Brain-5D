# Brain 5D Core v0.1.0

**Sprint 1C – Verified Observable Core**

Dieses Repository bildet den vollständigen Stand 1 des Brain-5D-Projekts ab: einen deterministischen, sparse gespeicherten, beobachtbaren Referenzkern für ein 5-dimensionales Spiking-Neuronennetzwerk.

## Stand-1-Ziele

- 5D-Koordinatenraum mit gepackten 40-Bit-IDs
- Sparse Neuronen- und Synapsenspeicherung
- Izhikevich-Regular-Spiking-Neuronen, 1 ms Tick
- verzögerte Spike-Events über Ringpuffer
- konfigurierbare Input-/Output-Hyperflächen
- diagnostische Stimuli
- echte Spike-Historie und Developer Observatory
- Topologie-Health-Check
- Propagations-/Rekrutierungsanalyse
- reproduzierbare Run-Artefakte
- Golden-Chain-Referenztest A(0) -> B(2) -> C(5)

**Nicht Bestandteil von Stand 1:** STDP, Eligibility Traces, Reward Learning, Homöostase mit Verhaltenswirkung, Neurogenese, Pruning oder selbstmodifizierender Code.

## Installation

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

Alternativ:

```bash
pip install -r requirements.txt
```

## Tests

```bash
python -m pytest -v
```

Golden Chain separat:

```bash
python -m pytest tests/test_golden_chain.py -v
```

## Start

Headless:

```bash
python -m src.main
```

Mit Observatory:

```bash
python -m src.main --observe
```

Benchmark:

```bash
python -m src.main --benchmark
```

## Git-Referenzstand

Nach erfolgreichem Testlauf:

```bash
git init
git add .
git commit -m "feat: verified observable Brain 5D Sprint 1 core"
git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"
```

Siehe `docs/GIT_WORKFLOW.md` und `docs/ACCEPTANCE.md`.
# Brain-5D
