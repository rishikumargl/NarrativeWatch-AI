@echo off
title NarrativeWatch AI - Development Server
color 0A

echo.
echo ========================================
echo   NarrativeWatch AI - Development Setup
echo ========================================
echo.

REM Start Backend in new window
echo [1/2] Starting Backend Server...
start cmd /k "cd backend && python run.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend in new window
echo [2/2] Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"

REM Wait for everything to start
timeout /t 5 /nobreak

echo.
echo ========================================
echo   Servers Starting...
echo ========================================
echo.
echo Backend:   http://localhost:8000
echo Frontend:  http://localhost:3000 (or 3001/3002 if in use)
echo API Docs:  http://localhost:8000/docs
echo.
echo Press any key to continue...
pause
