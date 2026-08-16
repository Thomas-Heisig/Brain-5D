@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe scripts\brain5d_launcher.py --dashboard %*
) else (
  python scripts\brain5d_launcher.py --dashboard %*
)
endlocal
