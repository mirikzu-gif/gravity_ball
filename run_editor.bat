@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tools\level_editor.py
) else (
    python tools\level_editor.py
)

if errorlevel 1 (
    echo.
    echo Level editor exited with an error.
    pause
)
