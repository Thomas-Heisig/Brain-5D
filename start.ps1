<#
.SYNOPSIS
    Startet Brain-5D mit Dashboard und Browser.
.DESCRIPTION
    Startet die Brain-5D-Simulation mit integriertem Dashboard und oeffnet
    den Browser. Der Launcher startet src.main als einzigen Prozess.
    Verwendet bevorzugt die venv-Umgebung.

    Einfachster Aufruf:  .\start.ps1
.PARAMETER Config
    Pfad zur YAML-Konfigurationsdatei (default: configs/poc_alpha5_live.yaml).
.PARAMETER NoDashboard
    Dashboard deaktivieren.
.PARAMETER Observe
    Observatory-Fenster aktivieren.
.PARAMETER Benchmark
    Benchmark-Modus aktivieren.
.PARAMETER NoLearning
    Learning-Engine deaktivieren.
.PARAMETER NoHomeostasis
    Homeostasis-Engine deaktivieren.
.PARAMETER Ticks
    Simulations-Ticks ueberschreiben.
.PARAMETER PassThru
    Nur die Launcher-Argumente ausgeben, nicht ausfuehren.
.PARAMETER Help
    Zeigt Hilfe zum Launcher an.
.EXAMPLE
    .\start.ps1
    Startet mit poc_alpha5_live.yaml, Dashboard + Browser.
.EXAMPLE
    .\start.ps1 -NoDashboard
    Startet ohne Dashboard.
.EXAMPLE
    .\start.ps1 -Config configs\stdp_on.yaml -Observe
    Startet mit STDP-Konfiguration und Observatory.
#>

param(
    [string]$Config = "configs/poc_alpha5_live.yaml",

    [switch]$NoDashboard,
    [switch]$Observe,
    [switch]$Benchmark,
    [switch]$NoLearning,
    [switch]$NoHomeostasis,
    [int]$Ticks = 0,

    [switch]$PassThru,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Python finden (bevorzugt venv)
$VenvPython = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    $PythonExe = "python"
}

# Hilfe
if ($Help) {
    & $PythonExe (Join-Path $ProjectRoot "scripts" "brain5d_launcher.py") start --help
    exit 0
}

# Launcher-Argumente bauen
$arguments = @(
    (Join-Path $ProjectRoot "scripts" "brain5d_launcher.py"),
    "start",
    "--config", (Join-Path $ProjectRoot $Config)
)

# Standard: Dashboard + Browser
if (-not $NoDashboard) {
    $arguments += "--dashboard"
    $arguments += "--open-browser"
}

# Optionale Flags
if ($Observe)       { $arguments += "--observe" }
if ($Benchmark)     { $arguments += "--benchmark" }
if ($NoLearning)    { $arguments += "--no-learning" }
if ($NoHomeostasis) { $arguments += "--no-homeostasis" }
if ($Ticks -gt 0)   { $arguments += "--ticks"; $arguments += "$Ticks" }

# Nur anzeigen?
if ($PassThru) {
    Write-Host ($arguments -join " ")
    exit 0
}

# Ausfuehren
Write-Host "Brain-5D wird gestartet ..." -ForegroundColor Cyan
Write-Host "  Config: $Config" -ForegroundColor Gray

try {
    & $PythonExe @arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "`nBrain-5D laeuft. Stoppen mit: .\stop.ps1" -ForegroundColor Green
    } else {
        Write-Host "`nStart fehlgeschlagen (Exit $exitCode)" -ForegroundColor Red
    }
    exit $exitCode
}
catch {
    Write-Host "Fehler: $_" -ForegroundColor Red
    exit 1
}
