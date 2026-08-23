<#
.SYNOPSIS
    Startet Brain-5D mit dem Launcher.
.DESCRIPTION
    Startet die Brain-5D-Simulation mit optionalem Dashboard.
    Verwendet bevorzugt die venv-Umgebung, falls vorhanden.
    Der Launcher startet src.main als einzigen Prozess (dieser enthält
    Simulation, Controller, OperatorBridge und Dashboard-Server).
.PARAMETER Config
    Pfad zur YAML-Konfigurationsdatei (default: configs/poc_config.yaml).
.PARAMETER Observe
    Observatory-Fenster aktivieren.
.PARAMETER Benchmark
    Benchmark-Modus aktivieren.
.PARAMETER NoLearning
    Learning-Engine deaktivieren.
.PARAMETER NoHomeostasis
    Homeostasis-Engine deaktivieren.
.PARAMETER Ticks
    Simulations-Ticks überschreiben.
.PARAMETER Dashboard
    Integriertes Dashboard starten (default: true).
.PARAMETER NoDashboard
    Dashboard deaktivieren.
.PARAMETER OpenBrowser
    Dashboard im Standard-Browser öffnen.
.PARAMETER Host
    Dashboard-Host (default: 127.0.0.1).
.PARAMETER Port
    Dashboard-Port (default: 8765).
.PARAMETER Help
    Zeigt diese Hilfe an.
.EXAMPLE
    .\start.ps1
    Startet mit poc_config.yaml ohne Dashboard.
.EXAMPLE
    .\start.ps1 -Dashboard -OpenBrowser
    Startet mit Dashboard und öffnet den Browser.
.EXAMPLE
    .\start.ps1 -Config configs/stdp_on.yaml -Observe
    Startet mit STDP-Konfiguration und Observatory.
#>

param(
    [Parameter(Position = 0)]
    [string]$Config = "configs/poc_config.yaml",

    [switch]$Observe,
    [switch]$Benchmark,
    [switch]$NoLearning,
    [switch]$NoHomeostasis,
    [int]$Ticks = 0,

    [switch]$Dashboard,
    [switch]$NoDashboard,
    [switch]$OpenBrowser,

    [string]$Host_ = "127.0.0.1",
    [int]$Port = 8765,

    [switch]$Help
)

# Hilfe anzeigen
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Python finden (bevorzugt venv)
$VenvPython = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
    $PythonLabel = "venv"
} else {
    $PythonExe = "python"
    $PythonLabel = "system"
}

Write-Host "🧠 Brain-5D wird gestartet ..." -ForegroundColor Cyan
Write-Host "   Python : $PythonExe ($PythonLabel)" -ForegroundColor Gray
Write-Host "   Config : $Config" -ForegroundColor Gray

# Argumente für den Launcher bauen
$arguments = @(
    (Join-Path $ProjectRoot "scripts" "brain5d_launcher.py"),
    "start",
    "--config", (Join-Path $ProjectRoot $Config)
)

if ($Observe)       { $arguments += "--observe" }
if ($Benchmark)     { $arguments += "--benchmark" }
if ($NoLearning)    { $arguments += "--no-learning" }
if ($NoHomeostasis) { $arguments += "--no-homeostasis" }
if ($Ticks -gt 0)   { $arguments += "--ticks"; $arguments += "$Ticks" }

# Dashboard: default AUS, es sei denn -Dashboard oder -OpenBrowser
$useDashboard = $Dashboard -or $OpenBrowser
if ($NoDashboard)   { $useDashboard = $false }
if ($useDashboard)  { $arguments += "--dashboard" }
if ($OpenBrowser)   { $arguments += "--open-browser" }
if ($Host_ -ne "127.0.0.1") { $arguments += "--host"; $arguments += $Host_ }
if ($Port -ne 8765) { $arguments += "--port"; $arguments += "$Port" }

Write-Host "   Args  : $($arguments -join ' ')" -ForegroundColor Gray

try {
    & $PythonExe @arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "✅ Brain-5D erfolgreich gestartet (PID: $exitCode)." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Brain-5D mit Exit-Code $exitCode beendet." -ForegroundColor Red
    }
    exit $exitCode
}
catch {
    Write-Host "❌ Fehler beim Starten von Brain-5D: $_" -ForegroundColor Red
    exit 1
}
