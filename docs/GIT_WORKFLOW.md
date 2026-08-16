# Git-Workflow

## Branches

Empfohlen:

- `main`: nur verifizierte Referenzstände
- `develop`: integrierte Entwicklungsstände
- `feature/<name>`: einzelne Funktionen
- `fix/<name>`: Fehlerkorrekturen
- `experiment/<name>`: nicht freigegebene Versuche

## Commit-Stil

Conventional Commits:

```text
feat: add real spike history
fix: correct ring-buffer event accounting
test: add golden chain propagation test
docs: document tick semantics
perf: cache 5D neighbour offsets
refactor: separate telemetry from core
```

## Stand-1-Freeze

```bash
git checkout main
git pull
git merge --no-ff develop
git tag -a brain5d-core-v0.1.0 -m "Sprint 1C VERIFIED - observable deterministic reference core"
git push origin main --tags
```

Tags werden nie nachträglich verschoben. Sprint 2 beginnt von einem neuen Branch, z. B. `feature/sprint2-stdp`.

## Was nicht committen

- virtuelle Umgebungen
- `__pycache__`
- lokale IDE-Dateien
- Run-Artefakte unter `artifacts/runs/`
- Snapshots
- Geheimnisse/API-Keys
