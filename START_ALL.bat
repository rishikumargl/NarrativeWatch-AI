@echo off
REM NarrativeWatch AI - Automated Startup Script for Windows
REM This script sets up and starts the entire application

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo NARRATIVEWATCH AI - AUTOMATED STARTUP
echo ================================================================================
echo.

REM Colors for output (Windows doesn't support ANSI by default, so using simple text)
echo [*] Starting NarrativeWatch AI setup and startup process...
echo.

REM Step 1: Create PostgreSQL Database
echo [1/6] Creating PostgreSQL Database...
echo.
psql -U postgres -c "CREATE DATABASE narrativewatch;" >nul 2>&1
if errorlevel 1 (
    echo [!] Database creation skipped (may already exist or PostgreSQL not running)
) else (
    echo [✓] Database created successfully
)

REM Step 2: Enable pgvector extension
echo [2/6] Enabling pgvector extension...
psql -U postgres -d narrativewatch -c "CREATE EXTENSION IF NOT EXISTS vector;" >nul 2>&1
if errorlevel 1 (
    echo [!] pgvector setup skipped
) else (
    echo [✓] pgvector extension enabled
)

REM Step 3: Verify Configuration
echo.
echo [3/6] Verifying configuration...
cd backend
python verify_config.py
if errorlevel 1 (
    echo [!] Configuration verification had issues
    pause
    exit /b 1
)
cd ..
echo.

REM Step 4: Install Python dependencies
echo [4/6] Installing Python dependencies...
cd backend
python -m venv venv >nul 2>&1
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [!] Some dependencies may have failed to install
)
echo [✓] Python dependencies installed
cd ..
echo.

REM Step 5: Start Backend in a new window
echo [5/6] Starting Backend Server (port 8000)...
start "NarrativeWatch Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn src.app:app --reload --port 8000"
echo [✓] Backend server starting...
timeout /t 3 /nobreak
echo.

REM Step 6: Start Frontend in a new window
echo [6/6] Starting Frontend Server (port 3000)...
start "NarrativeWatch Frontend" cmd /k "cd frontend && npm install && npm run dev"
echo [✓] Frontend server starting...
echo.

echo ================================================================================
echo SUCCESS! NarrativeWatch AI is starting up!
echo ================================================================================
echo.
echo Access the application at:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo.
echo The backend and frontend windows will open in separate terminals.
echo You can now use the application!
echo.
echo Press any key to close this window...
pause >nul

endlocal
