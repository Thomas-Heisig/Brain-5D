# Integration into current Brain-5D checkout

This overlay intentionally does **not** blindly overwrite the current `src/dashboard/server.py`, `src/main.py`, or your reorganized documentation tree. Those files have changed repeatedly between alpha revisions and are the highest-risk merge points.

## 1. Copy overlay

Copy all files from this archive into the repository root.

## 2. README

Run:

```powershell
python scripts/apply_readme_alpha4.py
```

## 3. Dashboard server hooks

Add an optional `OperatorBridge` to the existing DashboardServer and route:

- `GET /api/controller/status` -> `bridge.status()`
- `POST /api/control` -> `bridge.command(command, ticks=...)`
- `POST /api/self-organization/apply` -> `bridge.apply_proposal(proposal_id, approved=True)`
- `POST /api/self-organization/undo` -> `bridge.undo()`

Use typed JSON parsing: parse to `object`, validate `dict`, then validate each key; do not pass arbitrary `dict[str, object]` onward.

## 4. Dashboard HTML

Insert `src/dashboard/static/operator_console.fragment.html` into your existing dashboard layout and load:

```html
<link rel="stylesheet" href="/operator_console.css">
<script src="/operator_console.js" defer></script>
```

If your static handler only whitelists suffixes, `.css` and `.js` are already supported in the earlier dashboard implementation.

## 5. Runtime ownership

Create the controller in the same process that owns the mutable NeuralNetwork. Do not attempt to control a separate simulation process through in-memory objects.

## 6. Windows start

Use `start.cmd` when PowerShell blocks unsigned `.ps1` scripts. This avoids changing machine execution policy.

## 7. Quality gate

```powershell
black src tests scripts
python -m pytest -v -m "not slow"
mypy src
pyright src scripts tests
python scripts/verify_v050a4.py
git diff --check
```
