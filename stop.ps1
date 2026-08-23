<#
.SYNOPSIS
    Stoppt Brain-5D und alle verwalteten Prozesse.
.DESCRIPTION
    Ruft den Launcher mit dem stop-Befehl auf, der die PID-Datei liest
    und alle registrierten Brain-5D-Prozesse terminiert.
    Gibt 0 bei Erfolg zurück, 1 bei Fehler.
.EXAMPLE
    .\stop.ps1
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Projekt-Root ermitteln
$ProjectRoot = Split-Path -Parent $ScriptDir

# Prüfen ob venv existiert
$VenvPython = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    $PythonExe = "python"
}

Write-Host "🛑 Brain-5D wird gestoppt ..." -ForegroundColor Yellow

try {
    & $PythonExe (Join-Path $ProjectRoot "scripts" "brain5d_launcher.py") stop
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "✅ Brain-5D erfolgreich gestoppt." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Brain-5D-Stop mit Exit-Code $exitCode beendet." -ForegroundColor Red
    }
    exit $exitCode
}
catch {
    Write-Host "❌ Fehler beim Stoppen: $_" -ForegroundColor Red
    exit 1
}
