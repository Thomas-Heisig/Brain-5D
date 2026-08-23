@echo off
:: ============================================================================
:: Brain-5D Stop Script (CMD)
:: ============================================================================
:: Stoppt alle Brain-5D-Prozesse ueber den Launcher.
::
:: Usage:
::   stop.cmd
:: ============================================================================
setlocal enabledelayedexpansion

:: Projekt-Root ermitteln (Verzeichnis dieser Batch-Datei)
cd /d "%~dp0"

:: Python finden (bevorzugt venv)
set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

echo [Brain-5D] Stopping Brain-5D ...

%PYTHON_CMD% scripts\brain5d_launcher.py stop
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    echo [Brain-5D] Successfully stopped.
) else (
    echo [Brain-5D] Stop finished with exit code %EXIT_CODE%.
)

endlocal
exit /b %EXIT_CODE%
