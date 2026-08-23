@echo off
:: ============================================================================
:: Brain-5D Start Script (CMD)
:: ============================================================================
:: Startet die Brain-5D-Simulation ueber den Launcher.
:: Verwendet bevorzugt die venv-Umgebung, falls vorhanden.
::
:: Usage:
::   start.cmd                          (Start ohne Dashboard)
::   start.cmd --dashboard              (Start mit Dashboard)
::   start.cmd --dashboard --open-browser  (Start + Browser oeffnen)
::   start.cmd --config configs\stdp_on.yaml  (Eigene Config)
::   start.cmd --help                   (Hilfe anzeigen)
::
:: Parameter werden 1:1 an brain5d_launcher.py start weitergegeben.
:: ============================================================================
setlocal enabledelayedexpansion

:: Projekt-Root ermitteln
cd /d "%~dp0"
set "PROJECT_ROOT=%CD%"

:: Python finden (bevorzugt venv)
set "PYTHON_CMD=python"
if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    echo [Brain-5D] Using venv Python
) else (
    echo [Brain-5D] Using system Python
)

:: Hilfe anzeigen
if "%1"=="--help" (
    %PYTHON_CMD% %PROJECT_ROOT%\scripts\brain5d_launcher.py --help
    endlocal
    exit /b 0
)

:: Pruefen ob Konfiguration existiert
set "CONFIG=%PROJECT_ROOT%\configs\poc_config.yaml"
if not exist "%CONFIG%" (
    echo [Brain-5D] ERROR: Config not found at %CONFIG%
    endlocal
    exit /b 1
)

echo ===========================================================================
echo   Brain-5D v0.5.0-alpha.5
echo   Project: %PROJECT_ROOT%
echo ===========================================================================

:: Launcher starten
%PYTHON_CMD% %PROJECT_ROOT%\scripts\brain5d_launcher.py start %*
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    echo [Brain-5D] Successfully started.
) else (
    echo [Brain-5D] Start finished with exit code %EXIT_CODE%.
)

endlocal
exit /b %EXIT_CODE%
