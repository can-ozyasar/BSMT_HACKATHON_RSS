@echo off
SETLOCAL EnableDelayedExpansion

echo ==========================================
echo   BIOS Signal Radar - Tek Tikla Baslat
echo ==========================================

:: 1. Backend'i Baslat
echo [+] Backend baslatiliyor...
start "BIOS-Backend" cmd /k "cd bios-signal-radar\backend && .venv\Scripts\python.exe main.py"

:: 2. Frontend'i Baslat
echo [+] Frontend baslatiliyor...
start "BIOS-Frontend" cmd /k "cd bios-signal-radar\frontend && npm run dev"

echo.
echo ==========================================
echo   Sistemler ayri pencerelerde acildi.
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:5173
echo ==========================================
pause
