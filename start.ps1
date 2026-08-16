param(
    [switch]$NoDashboard,
    [switch]$NoSimulation,
    [switch]$OpenBrowser,
    [string]$Config = "configs/poc_config.yaml",
    [string]$SnapshotPath = "artifacts/brain5d_snapshot.b5d",
    [int]$Port = 8765
)

$arguments = @(
    "scripts/brain5d_launcher.py", "start",
    "--config", $Config,
    "--snapshot", $SnapshotPath,
    "--port", $Port
)
if ($NoDashboard) { $arguments += "--no-dashboard" }
if ($NoSimulation) { $arguments += "--no-simulation" }
if ($OpenBrowser) { $arguments += "--open-browser" }

& python @arguments
exit $LASTEXITCODE
