@echo off
setlocal
cd /d "%~dp0\.."
python scripts\verify_b5d.py
set "RC=%ERRORLEVEL%"
exit /b %RC%
