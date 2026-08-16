# Integration

Extract this overlay into the repository root, then run:

```powershell
cd F:\Brain-5D
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
black src tests
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_dashboard.py
git diff --check
```

Do not tag the release until the local Quality Gate is fully green.

After the final v0.4 commit/tag is present, commit this revision as:

```powershell
git add -A
git commit -m "v0.5.0-alpha.1: homeostasis and self-regulation foundation"
git tag -a brain5d-core-v0.5.0-alpha.1 -m "Homeostasis and self-regulation foundation"
git push origin main
git push origin brain5d-core-v0.5.0-alpha.1
```
