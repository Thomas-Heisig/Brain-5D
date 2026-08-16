# Operator Dashboard – Alpha.7

The dashboard stays local and read-only.

## Endpoints

- `GET /healthz`
- `GET /api/status`
- `GET /api/heatmap?kind=activity|weights|energy&snapshot=<name>`
- `GET /api/snapshots`
- `GET /api/docs`
- `GET /api/docs?name=<document.md>`

Path traversal is rejected for documentation and snapshot selection.

## UI sections

- core status;
- learning;
- storage queue and persistence telemetry;
- structural self-organization;
- v0.5 homeostasis bridge;
- embodiment bridge;
- lazy `.b5d` heatmaps;
- sibling snapshot selector;
- repository Markdown documentation modal.

The documentation viewer renders Markdown as plain preformatted text in
alpha.7.  This avoids introducing an HTML/Markdown rendering dependency and
prevents untrusted document HTML from being executed.

## Start

```powershell
python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

or use the process launcher:

```powershell
.\start.ps1 -OpenBrowser
```

If local PowerShell policy blocks scripts, use:

```cmd
start.cmd
```
