# Brain-5D v0.4.0-alpha.6

## Deterministic Restore + Research Alignment + v0.5 Dashboard Bridge

This overlay addresses the only failing functional test from alpha.5 and the
four remaining mypy errors reported in the Windows validation log.

### Main correction

The compact optical state in `.b5d` is quantized. Exact continuation therefore
uses runtime checkpoint v2 to store exact dynamic neuron values and overlays
those values after snapshot/journal reconstruction. The frozen `.b5d` V1 layout
is not changed.

### Dashboard

The existing dashboard already has status polling and storage telemetry. Alpha.6
does not duplicate those mechanisms. It adds a read-only homeostasis bridge card
for v0.5.

### Strategy documents

The revision integrates the conclusions of:

- `docs/06-research/Analyse_Deepseek.md`
- `docs/06-research/Der_weg_zur_KI.md`
- `docs/06-research/old/Research.md`

into a measurable research-aligned roadmap. Claims about AGI, understanding or
consciousness remain outside the v1.0 acceptance definition.

## Apply

```powershell
python scripts/apply_alpha6_quality_fixes.py
python scripts/apply_alpha6_metadata.py
black src tests
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_dashboard.py
git diff --check
```

Expected release gate before `v0.4.0` final:

- pytest: all pass
- Black: clean
- mypy: 0 errors
- Pylint: >= 9.0
- deterministic restore-and-continue: pass
