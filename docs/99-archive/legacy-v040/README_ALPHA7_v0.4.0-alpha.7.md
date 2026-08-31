# Brain-5D v0.4.0-alpha.7 – Integration Notes

Alpha.7 is the final pre-v0.4 quality/research bridge. It does not change the
frozen `.b5d` V1 binary format.

## Main changes

- runtime checkpoint V3 restores exact neuron model parameters and synapse
  floating-point state for bit-exact continuation;
- strict JSON parsing removes the remaining checkpoint mypy errors;
- embodiment becomes a first-class typed architecture boundary without enabling
  uncontrolled external actions;
- dashboard adds embodiment metrics, documentation browsing, and a safe snapshot
  selector;
- one-click launcher uses PID tracking and never kills unrelated Python
  processes;
- roadmap integrates the project research documents into measured milestones.

## Recommended verification

```powershell
pip install -e ".[dev]"
black src tests
python scripts/verify_all.py
python scripts/verify_dashboard.py
git diff --check
```

With large storage tests enabled:

```powershell
$env:BRAIN5D_RUN_LARGE_STORAGE_TEST="1"
$env:BRAIN5D_RUN_LARGE_STORAGE_TESTS="1"
python scripts/verify_b5d.py
```

## Launcher

```powershell
.\start.ps1 -OpenBrowser
.\stop.ps1
```

If PowerShell execution policy blocks local scripts:

```cmd
start.cmd
stop.cmd
```
