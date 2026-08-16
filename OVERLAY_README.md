# Brain-5D v0.5.0-alpha.3 Overlay

This overlay is designed for the alpha.2 architecture described in the current
Brain-5D development state. It deliberately avoids blindly replacing `main.py` or
`server.py`, because those files are integration hubs and may already contain
local alpha.2 fixes.

## Added files

- `src/runtime/control.py`
- `src/dashboard/control_service.py`
- `src/dashboard/control_http.py`
- `src/dashboard/static/control-panel.fragment.html`
- `src/dashboard/static/control-panel.css`
- `src/dashboard/static/control-panel.js`
- `src/self_organization/policy.py`
- `src/self_organization/coordinator.py`
- corresponding tests and alpha.3 verification script

## Integration order

1. Copy/extract the overlay into `F:\Brain-5D`.
2. Review and apply `patches/server_v050a3.patch` to the current dashboard server.
3. Insert the HTML fragment into the existing dashboard layout and load the new
   CSS/JS assets. `patches/index_v050a3.patch` shows the required includes.
4. Follow `patches/main_v050a3_integration.txt` to connect the controller to the
   existing canonical single-tick path.
5. Change `pyproject.toml` version from `0.5.0a2` to `0.5.0a3`.
6. Keep self-organization in dry-run until a typed Manipulator executor has been
   explicitly reviewed.

## Suggested PowerShell checks

```powershell
cd F:\Brain-5D
.venv\Scripts\Activate.ps1

black src tests scripts
mypy src
pyright src scripts tests
python -m pytest -m "not slow" -v
python scripts/verify_v050a3.py
pylint src
git diff --check
```

## Important integration invariant

Do not run the old foreground simulation loop at the same time as the interactive
`RuntimeController`. In dashboard/interactive mode the controller must be the only
owner of tick execution.
