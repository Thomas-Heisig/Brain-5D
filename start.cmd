@echo off
:: ============================================================================
:: Brain-5D Start Script (CMD)
:: ============================================================================
:: Startet die Brain-5D-Simulation ueber den Launcher.
:: Verwendet bevorzugt die venv-Umgebung, falls vorhanden.
::
:: Usage:
::   start.cmd                          (Start mit Dashboard + Browser, Alpha.5 Live Config)
::   start.cmd --no-dashboard           (Start ohne Dashboard)
::   start.cmd --config configs\...     (Eigene Config)
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
) else (
    echo [Brain-5D] Using system Python
)

:: Hilfe anzeigen
if "%1"=="--help" (
    %PYTHON_CMD% %PROJECT_ROOT%\scripts\brain5d_launcher.py start --help
    endlocal
    exit /b 0
)

:: Banner
echo ===========================================================================
echo   Brain-5D v0.5.0-alpha.5
echo   Project: %PROJECT_ROOT%
echo ===========================================================================

:: Standard: Dashboard + Browser, Alpha.5 Live Config, es sei denn --no-dashboard wurde uebergeben
set "EXTRA="
echo %* | findstr /C:"--no-dashboard" >nul
if errorlevel 1 set "EXTRA=--dashboard --open-browser --config configs\poc_alpha5_live.yaml"

:: Launcher starten
%PYTHON_CMD% %PROJECT_ROOT%\scripts\brain5d_launcher.py start %EXTRA% %*
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    echo.
    echo ✅ Brain-5D is running.
    echo    Stop with: stop.cmd
) else (
    echo.
    echo ❌ Start failed (exit code %EXIT_CODE%^)
)

endlocal
exit /b %EXIT_CODE%
