@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] No existe el entorno .venv. Ejecuta: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
".venv\Scripts\python.exe" desktop_launcher.py
