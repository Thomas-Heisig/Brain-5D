@echo off
:: ============================================================================
:: MHRN Stop Script (CMD)
:: ============================================================================
:: Stoppt alle MHRN-Prozesse ueber den Launcher.
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

echo [MHRN] Stopping MHRN ...

%PYTHON_CMD% scripts\mhrn_launcher.py stop
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    echo [MHRN] Successfully stopped.
) else (
    echo [MHRN] Stop finished with exit code %EXIT_CODE%.
)

endlocal
exit /b %EXIT_CODE%
