@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" game.py
) else (
    python game.py
)

if errorlevel 1 (
    echo.
    echo Game exited with an error.
    pause
)
