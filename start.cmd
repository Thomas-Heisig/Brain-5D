@echo off
:: ============================================================================
:: MHRN Start Script (CMD)
:: ============================================================================
:: Startet die MHRN-Simulation ueber den Launcher.
:: Verwendet bevorzugt die venv-Umgebung, falls vorhanden.
::
:: Usage:
::   start.cmd                          (Start mit Dashboard + Browser, vertrauenswuerdiges LAN)
::   start.cmd --no-dashboard           (Start ohne Dashboard)
::   start.cmd --config configs\...     (Eigene Config)
::   start.cmd --host 0.0.0.0            (Dashboard im vertrauenswuerdigen LAN)
::   start.cmd --help                   (Hilfe anzeigen)
::
:: Parameter werden 1:1 an brain5d_launcher.py start weitergegeben.
:: ============================================================================
setlocal enabledelayedexpansion

:: Projekt-Root ermitteln
cd /d "%~dp0"
set "PROJECT_ROOT=%CD%"

:: Enable the local research chat when Ollama is installed. The server still
:: fails closed if no provider is configured or Ollama is unavailable.
where ollama >nul 2>nul
if not errorlevel 1 if not defined BRAIN5D_CHAT_MODEL set "BRAIN5D_CHAT_MODEL=gemma4:latest"
if not errorlevel 1 if not defined BRAIN5D_CHAT_WEB_SEARCH set "BRAIN5D_CHAT_WEB_SEARCH=true"

:: Python finden (bevorzugt venv)
set "PYTHON_CMD=python"
if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%PROJECT_ROOT%\.venv\Scripts\python.exe"
) else (
    echo [MHRN] Using system Python
)

:: Hilfe anzeigen
if "%1"=="--help" (
    %PYTHON_CMD% %PROJECT_ROOT%\scripts\mhrn_launcher.py start --help
    endlocal
    exit /b 0
)

:: Banner
echo ===========================================================================
echo   MHRN v0.5.0-alpha.7
echo   Project: %PROJECT_ROOT%
echo ===========================================================================

:: Standard: Dashboard + Browser auf allen lokalen Interfaces, es sei denn --no-dashboard wurde uebergeben.
:: Ein explizites --host in den Argumenten ueberschreibt den LAN-Standard.
set "EXTRA="
echo %* | findstr /C:"--no-dashboard" >nul
if errorlevel 1 set "EXTRA=--dashboard --open-browser --config configs\poc_alpha5_live.yaml --host 0.0.0.0"

:: Launcher starten
%PYTHON_CMD% %PROJECT_ROOT%\scripts\mhrn_launcher.py start %EXTRA% %*
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    echo.
    echo ✅ MHRN is running.
    echo    Stop with: stop.cmd
) else (
    echo.
    echo ❌ Start failed (exit code %EXIT_CODE%^)
)

endlocal
exit /b %EXIT_CODE%
