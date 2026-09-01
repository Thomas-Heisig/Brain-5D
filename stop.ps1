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
$ProjectRoot = $ScriptDir

Write-Host "Brain-5D wird gestoppt ..." -ForegroundColor Yellow

try {
    $PidFile = Join-Path $ProjectRoot "artifacts" "brain5d.pid"
    if (-not (Test-Path $PidFile)) {
        Write-Host "Brain-5D ist bereits gestoppt." -ForegroundColor Green
        return
    }

    $Brain5DPid = [int](Get-Content $PidFile -Raw).Trim()
    & taskkill /PID $Brain5DPid /T /F | Out-Host
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0 -and (Get-Process -Id $Brain5DPid -ErrorAction SilentlyContinue)) {
        throw "Prozessbaum $Brain5DPid konnte nicht beendet werden."
    }

    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Brain-5D erfolgreich gestoppt." -ForegroundColor Green
    return
}
catch {
    Write-Error "Fehler beim Stoppen: $_"
    throw
}
